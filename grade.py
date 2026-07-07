# -*- coding: utf-8 -*-
"""
Grade de Ativação: lê o Excel (.xlsm) da grade e mostra as promoções.

- Só considera as abas cujo nome começa com 'LISTA_' e que estão VISÍVEIS
  (abas ocultas são ignoradas de propósito).
- De cada aba pega os dados da promoção (período, link, %) e os produtos.
- Ao subir uma grade nova, SUBSTITUI as listas que vierem no arquivo; as que não
  vierem ficam como histórico (não são apagadas). Ver db.py.
"""
import io
import re

import openpyxl
import pandas as pd
import streamlit as st

import db

# Colunas dos produtos, por posição (1-based) na aba LISTA_:
#   H=SKU, I=DESCRIÇÃO, J=CATEGORIA PLANEJAMENTO, M=LINHA, N=KVIs, T=MECÂNICA,
#   U=SELO, Y=DE, Z=POR, AA=DESCONTO, AF=CICLO PROMO, AG=TIPO
_COLS = {
    "sku": 8, "descricao": 9, "categoria": 10, "linha": 13, "kvis": 14,
    "mecanica": 20, "selo": 21, "preco_de": 25, "preco_por": 26,
    "desconto": 27, "ciclo_promo": 32, "tipo": 33,
}

# Como mostrar cada coluna na tela (ordem e rótulo).
_ROTULOS = {
    "sku": "SKU", "descricao": "Descrição", "categoria": "Categoria",
    "linha": "Linha", "kvis": "KVIs", "mecanica": "Mecânica", "selo": "Selo",
    "preco_de": "DE", "preco_por": "POR", "desconto": "Desconto",
    "ciclo_promo": "Ciclo Promo", "tipo": "Tipo",
}


# ---------------------------------------------------------------------------
# Leitura da planilha
# ---------------------------------------------------------------------------
def _tipo_amigavel(nome: str) -> str:
    """'LISTA_20.5_MEIO_AMBIENTE' -> 'Meio Ambiente'."""
    s = re.sub(r"^LISTA_\d+(\.\d+)?_?", "", nome).replace("_", " ").strip()
    return s.title() if s else nome


def _ciclo_periodo(nome_arq: str):
    """Extrai o ciclo (CL_09_2026) e o período (26.05 a 31.05) do nome do arquivo."""
    per = re.search(r"\(([\d.]+ a [\d.]+)\)", nome_arq or "")
    cic = re.search(r"(CL[_ ]?\d+[_ ]?\d{4})", nome_arq or "")
    return (cic.group(1) if cic else "", per.group(1) if per else "")


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _txt(v) -> str:
    if v is None:
        return ""
    if isinstance(v, float) and v != v:   # NaN
        return ""
    return str(v).strip()


def ler_grade(file_bytes: bytes, nome_arquivo: str) -> list:
    """Lê o arquivo e devolve [(meta, produtos), ...] das abas LISTA_ visíveis."""
    wb = openpyxl.load_workbook(io.BytesIO(file_bytes), read_only=True, data_only=True)
    ciclo, periodo = _ciclo_periodo(nome_arquivo)
    resultado = []
    for nome in wb.sheetnames:
        if not nome.startswith("LISTA_"):
            continue
        ws = wb[nome]
        if ws.sheet_state != "visible":     # ignora abas ocultas
            continue
        linhas = list(ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=42))

        def celula(lin, col):               # col 1-based
            if len(linhas) > lin and len(linhas[lin]) >= col:
                return linhas[lin][col - 1].value
            return None

        meta = {
            "lista_nome": nome,
            "tipo": _tipo_amigavel(nome),
            "ciclo": ciclo,
            "periodo": periodo,
            "link_lp": _txt(celula(1, 2)),        # B2
            "comissao": _num(celula(2, 40)),      # AN3
            "cupom": _num(celula(2, 41)),         # AO3
            "depor": _num(celula(2, 42)),         # AP3
        }
        produtos = []
        for row in linhas[4:]:                    # produtos a partir da linha 5
            if not row[0].value:                  # coluna A (INSERIR SKU) vazia -> ignora
                continue
            p = {"lista_nome": nome}
            for chave, col in _COLS.items():
                v = row[col - 1].value if len(row) >= col else None
                p[chave] = _num(v) if chave in ("preco_de", "preco_por", "desconto") else _txt(v)
            produtos.append(p)
        meta["total_skus"] = len(produtos)
        resultado.append((meta, produtos))
    wb.close()
    return resultado


def salvar_grade(file_bytes: bytes, nome_arquivo: str) -> list:
    """Lê o arquivo e grava no Supabase. Retorna [(tipo, n_produtos), ...]."""
    resumo = []
    for meta, produtos in ler_grade(file_bytes, nome_arquivo):
        db.grade_upsert_lista(meta)
        db.grade_substituir_produtos(meta["lista_nome"], produtos)
        resumo.append((meta["tipo"], meta["total_skus"]))
    return resumo


# ---------------------------------------------------------------------------
# Tela de promoções (página inteira)
# ---------------------------------------------------------------------------
def _pct(v):
    return f"{round(v * 100)}%" if isinstance(v, (int, float)) else "—"


def _excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Produtos")
    return buffer.getvalue()


def pagina_promocoes(eh_admin: bool = False) -> None:
    st.title("📑 Promoções da Grade")
    if st.button("← Voltar ao calendário", key="voltar_calendario"):
        st.session_state.pop("_view", None)
        st.session_state.pop("_grade_sel", None)
        st.rerun()

    # --- Admin: subir uma grade nova ---------------------------------------
    if eh_admin:
        with st.expander("⬆️ Atualizar Grade (subir o Excel)", expanded=False):
            st.caption(
                "Suba o arquivo **.xlsm** da Grade de Ativação. O sistema lê as abas "
                "**LISTA_ visíveis** e substitui essas promoções (as que não vierem "
                "no arquivo ficam como histórico)."
            )
            arq = st.file_uploader("Arquivo da Grade", type=["xlsm", "xlsx"], key="up_grade")
            if arq is not None and st.button("Processar e salvar", type="primary", key="btn_proc"):
                try:
                    with st.spinner("Lendo a planilha e salvando no banco..."):
                        resumo = salvar_grade(arq.getvalue(), arq.name)
                    if resumo:
                        st.success(f"✅ {len(resumo)} promoção(ões) atualizada(s)!")
                        for tipo, n in resumo:
                            st.caption(f"• {tipo}: {n} produtos")
                        st.session_state.pop("_grade_sel", None)
                    else:
                        st.warning("Nenhuma aba 'LISTA_' visível foi encontrada no arquivo.")
                except Exception as e:
                    _msg = str(e).lower()
                    if "zip" in _msg or "badzip" in _msg:
                        st.error(
                            "⚠️ Este arquivo parece **corrompido ou incompleto** — "
                            "geralmente é um **download que não terminou**, ou um arquivo "
                            "que está **só na nuvem** (OneDrive) e não baixou inteiro.\n\n"
                            "**O que fazer:** abra a pasta, confirme que o arquivo baixou "
                            "100% (ícone sem a nuvenzinha) ou **baixe de novo**, e tente "
                            "subir mais uma vez. 🙂"
                        )
                    else:
                        st.error(f"Não consegui ler o arquivo. Detalhe: {e}")

    st.divider()

    sel = st.session_state.get("_grade_sel")
    if sel:
        _mostra_produtos(sel)
    else:
        _mostra_lista_promocoes()


def _mostra_lista_promocoes() -> None:
    listas = db.grade_listar_listas()
    if not listas:
        st.info("Nenhuma promoção cadastrada ainda. "
                + ("Suba uma Grade acima. ☝️" if True else ""))
        return

    busca = st.text_input("🔎 Buscar promoção", key="busca_lista").strip().lower()
    st.caption(f"{len(listas)} promoção(ões) disponível(is):")
    for L in listas:
        alvo = (str(L.get("tipo", "")) + " " + str(L.get("lista_nome", ""))).lower()
        if busca and busca not in alvo:
            continue
        c1, c2, c3 = st.columns([5, 2, 1.4])
        with c1:
            st.markdown(f"**{L.get('tipo') or L.get('lista_nome')}**")
            st.caption(
                f"Ciclo {L.get('ciclo') or '—'} · {L.get('periodo') or 'período —'}"
                + (f" · {L.get('link_lp')}" if L.get("link_lp") else "")
            )
        c2.markdown(f"**{L.get('total_skus', 0)}** SKUs")
        if c3.button("ver ▸", key=f"ver_{L['id']}", use_container_width=True):
            st.session_state._grade_sel = L["lista_nome"]
            st.rerun()
        st.divider()


def _mostra_produtos(lista_nome: str) -> None:
    if st.button("← Voltar às promoções", key="voltar_prom"):
        st.session_state.pop("_grade_sel", None)
        st.rerun()

    L = next((x for x in db.grade_listar_listas() if x["lista_nome"] == lista_nome), None)
    if L:
        st.subheader(L.get("tipo") or lista_nome)
        st.caption(
            f"**{L.get('total_skus', 0)} produtos** · Ciclo {L.get('ciclo') or '—'} · "
            f"{L.get('periodo') or 'período —'} · Cupom {_pct(L.get('cupom'))} · "
            f"Depor {_pct(L.get('depor'))}"
            + (f" · Página: {L.get('link_lp')}" if L.get("link_lp") else "")
        )

    produtos = db.grade_listar_produtos(lista_nome)
    if not produtos:
        st.info("Esta promoção está sem produtos.")
        return

    df = pd.DataFrame(produtos)
    # Só as colunas escolhidas, na ordem certa, com rótulos amigáveis.
    df = df[[c for c in _COLS if c in df.columns]].rename(columns=_ROTULOS)

    busca = st.text_input("🔎 Buscar produto (SKU ou descrição)", key="busca_prod").strip().lower()
    if busca:
        m = df["SKU"].astype(str).str.lower().str.contains(busca, na=False) | \
            df["Descrição"].astype(str).str.lower().str.contains(busca, na=False)
        df = df[m]

    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Baixar Excel",
        data=_excel_bytes(df),
        file_name=f"{(L.get('tipo') if L else lista_nome) or 'promocao'}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
