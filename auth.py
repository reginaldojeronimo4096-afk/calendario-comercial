# -*- coding: utf-8 -*-
"""
Login, sessão e gestão de usuários do Calendário.

Papéis:
  • admin  -> faz tudo + gerencia usuários (Hudson e Reginaldo)
  • editor -> edita o calendário (adicionar/editar/excluir), sem mexer em usuários
  • leitor -> só vê o calendário e baixa o Excel

Fluxo de cadastro: a pessoa clica em "Criar conta" no login -> a conta entra como
'pendente' -> um admin aprova em "Gerenciar Usuários" (definindo o papel).

Senhas ficam guardadas com bcrypt (embaralhadas), nunca em texto puro.
"""
import base64
import os
import secrets as _secrets

import bcrypt
import streamlit as st

import db

PAPEIS = ["admin", "editor", "leitor"]

# E-mail da empresa: quem se cadastra com um e-mail deste domínio entra NA HORA
# como leitor (sem esperar aprovação). Qualquer outro e-mail cai como 'pendente'
# e um admin precisa aprovar — mantém gente de fora bloqueada por padrão.
DOMINIO_CORP = "@natura.net"

# ---------------------------------------------------------------------------
# Empresas (marcas) — Natura e Avon. MESMO app e MESMOS usuários (uma conta só,
# pois há gente que cuida das duas, ex.: mídia); o que muda é a MARCA dos dados
# (calendário/promoções separados) e a CARA (logo/cor) da tela de escolha e login.
# 'logo' é o arquivo PNG na pasta do projeto; 'cor' é o tom principal da marca.
# ---------------------------------------------------------------------------
EMPRESAS = {
    "natura": {
        "nome": "Natura", "emoji": "🌸", "logo": "natura_logo.png",
        "cor": "#EE7B30", "cor_hover": "#D96C22",     # laranja Natura
    },
    "avon": {
        "nome": "Avon", "emoji": "💄", "logo": "avon_logo.png",
        "cor": "#E4007C", "cor_hover": "#B4004E",      # rosa/magenta Avon
    },
}


def empresa_cfg(empresa: str) -> dict:
    """Config visual da empresa (cai na Natura se vier algo inesperado)."""
    return EMPRESAS.get(empresa, EMPRESAS["natura"])


# ---------------------------------------------------------------------------
# Senhas (bcrypt)
# ---------------------------------------------------------------------------
def _hash(senha: str) -> str:
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _confere(senha: str, senha_hash: str) -> bool:
    try:
        return bcrypt.checkpw(senha.encode("utf-8"), (senha_hash or "").encode("utf-8"))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Bootstrap: cria os admins iniciais a partir dos secrets (só se não existirem)
# ---------------------------------------------------------------------------
def inicializar() -> None:
    """Na 1ª vez, cria as contas de admin definidas nos secrets ([[admin_inicial]]).
    Se a conta já existe, NÃO mexe (para não sobrescrever senha trocada depois)."""
    if st.session_state.get("_admins_ok"):
        return
    try:
        admins = st.secrets.get("admin_inicial", [])
    except Exception:
        admins = []
    for a in admins:
        try:
            if not db.buscar_usuario(a["usuario"]):
                db.criar_usuario(
                    a["usuario"], a.get("nome", ""), _hash(a["senha"]),
                    papel="admin", status="ativo",
                )
        except Exception:
            pass  # se o banco estiver indisponível, segue (a tela de erro aparece no login)
    st.session_state["_admins_ok"] = True


# ---------------------------------------------------------------------------
# Sessão
# ---------------------------------------------------------------------------
def esta_logado() -> bool:
    return bool(st.session_state.get("auth_user"))


def usuario_atual():
    return st.session_state.get("auth_user")


def sair() -> None:
    st.session_state.pop("auth_user", None)
    st.rerun()


# ---------------------------------------------------------------------------
# Tela de login (visual parecido com a tela Natura)
# ---------------------------------------------------------------------------
def _css_login(cor: str = "#EE7B30", cor_hover: str = "#D96C22") -> None:
    # A cor principal (__COR__/__COR_HOVER__) vem da empresa escolhida: laranja p/
    # Natura, rosa p/ Avon. Uso .replace em vez de f-string p/ não precisar escapar
    # todas as chaves { } do CSS.
    _css = """
        <style>
          /* Cartão central do login */
          .st-key-login_card {
            background: #FFFFFF;
            border: 1px solid #ECECEC;
            border-radius: 16px;
            padding: 1.6rem 1.8rem 1.2rem;
            box-shadow: 0 18px 40px rgba(0,0,0,0.10);
            max-width: 440px;          /* largura do cartão (um pouco mais largo) */
            margin: 6vh auto 0;        /* e centraliza na tela */
          }
          /* Esconde o aviso "Press Enter to submit form" que aparece DENTRO do
             campo — o botão "Entrar" já deixa claro o que fazer. */
          .st-key-login_card [data-testid="InputInstructions"] { display: none !important; }
          /* Fonte um pouco maior dentro dos campos (e-mail e senha). */
          .st-key-login_card input { font-size: 1.05rem !important; }
          /* Some com o "olho" NATIVO do navegador (Edge) no campo de senha — o app
             já tem o próprio botão de mostrar/ocultar, então apareciam DOIS olhos. */
          .st-key-login_card input::-ms-reveal,
          .st-key-login_card input::-ms-clear { display: none !important; }
          .login-logo   { text-align:center; font-size:1.7rem; font-weight:800;
                           color:__COR__; margin: 0 0 .2rem; letter-spacing:.5px; }
          .login-titulo { text-align:center; font-size:1.35rem; font-weight:800;
                          color:#1A1A2E; margin:.1rem 0 .1rem; }
          .login-sub    { text-align:center; color:#7A7A85; margin:0 0 1rem; }
          /* Rótulos "Usuário"/"Senha" legíveis no cartão branco (mesmo no tema
             escuro, onde por padrão ficariam cinza-claro e sumiam). */
          .st-key-login_card label,
          .st-key-login_card [data-testid="stWidgetLabel"] * {
            color:#3A3A3A !important; font-weight:600 !important;
          }
          /* Botão principal (Entrar / Solicitar acesso) na cor da empresa */
          .st-key-login_card [data-testid="stFormSubmitButton"] button {
            background:__COR__ !important; border:0 !important; color:#fff !important;
            font-weight:700 !important;
          }
          .st-key-login_card [data-testid="stFormSubmitButton"] button:hover {
            background:__COR_HOVER__ !important;
          }
        </style>
        """
    st.markdown(
        _css.replace("__COR__", cor).replace("__COR_HOVER__", cor_hover),
        unsafe_allow_html=True,
    )


@st.cache_data
def _logo_uri(arquivo: str = "natura_logo.png"):
    """Lê um PNG (na pasta do projeto) e devolve embutido como data-URI, para o
    logo viajar dentro da própria página (sem depender de arquivo externo).
    Recebe o nome do arquivo p/ servir tanto o logo da Natura quanto o da Avon."""
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), arquivo)
    try:
        with open(caminho, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")
    except Exception:
        return None


def tela_escolha_empresa() -> None:
    """1ª tela: escolher qual calendário abrir (Natura ou Avon). Depois de escolher,
    o app leva ao login com a CARA daquela empresa. Uma conta só serve às duas —
    quem já está logado troca de empresa aqui SEM novo login (o app.py mantém o
    auth_user; só zera '_empresa' p/ cair nesta tela)."""
    # CSS base + cor de cada empresa (borda do cartão e cor do botão).
    _btn_css = "".join(
        f".st-key-esc_card_{k}{{border-top:5px solid {v['cor']} !important;}}"
        f".st-key-esc_btn_{k} button{{background:{v['cor']} !important;border:0 !important;"
        f"color:#fff !important;font-weight:700 !important;border-radius:10px !important;}}"
        f".st-key-esc_btn_{k} button:hover{{background:{v['cor_hover']} !important;}}"
        for k, v in EMPRESAS.items()
    )
    st.markdown(
        "<style>"
        ".st-key-escolha_wrap{max-width:640px;margin:5vh auto 0;}"
        ".esc-titulo{text-align:center;font-size:1.6rem;font-weight:800;"
        "color:#1A1A2E;margin:0 0 .1rem;}"
        ".esc-sub{text-align:center;color:#7A7A85;font-size:1.05rem;margin:0 0 1.4rem;}"
        ".st-key-esc_card_natura,.st-key-esc_card_avon{background:#fff;"
        "border:1px solid #ECECEC;border-radius:16px;padding:1.3rem 1.1rem 1.1rem;"
        "box-shadow:0 14px 34px rgba(0,0,0,.08);text-align:center;}"
        ".esc-logo{display:flex;align-items:center;justify-content:center;"
        "height:92px;margin-bottom:1rem;}"
        ".esc-logo img{max-width:80%;max-height:80px;height:auto;}"
        ".esc-logo-txt{height:92px;display:flex;align-items:center;"
        "justify-content:center;font-size:1.6rem;font-weight:800;}"
        + _btn_css +
        "</style>",
        unsafe_allow_html=True,
    )
    with st.container(key="escolha_wrap"):
        st.markdown(
            "<div class='esc-titulo' style='margin:0 0 1.3rem;'>"
            "📅 Calendário de Ações</div>",
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        for col, chave in ((c1, "natura"), (c2, "avon")):
            cfg = EMPRESAS[chave]
            with col:
                with st.container(key=f"esc_card_{chave}"):
                    _logo = _logo_uri(cfg["logo"])
                    if _logo:
                        st.markdown(
                            f"<div class='esc-logo'><img src='{_logo}' "
                            f"alt='{cfg['nome']}'></div>",
                            unsafe_allow_html=True,
                        )
                    else:  # se faltar o arquivo, cai no emoji + nome
                        st.markdown(
                            f"<div class='esc-logo-txt'>{cfg['emoji']} {cfg['nome']}</div>",
                            unsafe_allow_html=True,
                        )
                    if st.button(f"Abrir calendário da {cfg['nome']}",
                                 key=f"esc_btn_{chave}", width="stretch"):
                        st.session_state["_empresa"] = chave
                        st.rerun()


def tela_login(empresa: str = "natura") -> None:
    cfg = empresa_cfg(empresa)
    _css_login(cfg["cor"], cfg["cor_hover"])
    with st.container(key="login_card"):
        _logo = _logo_uri(cfg["logo"])
        if _logo:
            st.markdown(
                f"<div style='text-align:center;margin:.2rem 0 .6rem;'>"
                f"<img src='{_logo}' alt='{cfg['nome']}' "
                f"style='width:60%;max-width:210px;height:auto;'></div>",
                unsafe_allow_html=True,
            )
        else:  # se o arquivo faltar, cai no emoji (nunca quebra a tela)
            st.markdown(
                f"<div class='login-logo'>{cfg['emoji']} {cfg['nome']}</div>",
                unsafe_allow_html=True,
            )
        st.markdown(
            "<div class='login-titulo'>Calendário da Grade Comercial</div>",
            unsafe_allow_html=True,
        )
        if st.session_state.get("_modo_cadastro"):
            _form_cadastro()
        elif st.session_state.get("_modo_reset"):
            _form_reset()
        else:
            _form_login()
        # Voltar à tela de escolha da empresa (antes de logar).
        if st.button(f"↩︎ Trocar empresa (agora: {cfg['nome']})",
                     key="trocar_emp_login", width="stretch"):
            for _m in ("_empresa", "_modo_cadastro", "_modo_reset"):
                st.session_state.pop(_m, None)
            st.rerun()


def _form_login() -> None:
    # Aviso de sucesso vindo do "Redefinir senha" (sobrevive ao recarregamento).
    _flash = st.session_state.pop("_login_flash", None)
    if _flash:
        st.success(_flash)
    st.markdown("<div class='login-sub'>Entre na sua conta</div>", unsafe_allow_html=True)
    with st.form("login_form"):
        usuario = st.text_input("E-mail / Usuário")
        senha = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar", width="stretch")

    if entrar:
        u = db.buscar_usuario(usuario)
        if not u or not _confere(senha, u.get("senha_hash", "")):
            st.error("Usuário ou senha incorretos.")
        elif u.get("status") == "pendente":
            st.warning("Seu cadastro ainda não foi aprovado por um administrador. ⏳")
        elif u.get("status") == "revogado":
            st.error("Seu acesso foi revogado. Fale com um administrador.")
        else:
            st.session_state.auth_user = {
                "id": u["id"], "usuario": u["usuario"],
                "nome": u.get("nome", ""), "papel": u.get("papel", "leitor"),
            }
            st.rerun()

    _c1, _c2 = st.columns(2)
    if _c1.button("Criar conta", key="ir_cadastro", width="stretch"):
        st.session_state._modo_cadastro = True
        st.rerun()
    if _c2.button("Esqueci a senha", key="ir_reset", width="stretch"):
        st.session_state._modo_reset = True
        st.rerun()
    st.caption(
        f"Leitores {DOMINIO_CORP} redefinem a senha sozinhos. "
        "Administradores/editores: peça a um administrador. 🙂"
    )


def _form_cadastro() -> None:
    st.markdown(
        "<div class='login-sub'>Criar uma conta nova</div>", unsafe_allow_html=True
    )
    # Mensagem de sucesso que sobrevive ao recarregamento (aparece após limpar).
    if st.session_state.get("_cad_flash"):
        st.success(st.session_state.pop("_cad_flash"))

    # Nonce nas chaves dos campos: ao cadastrar com SUCESSO, incrementamos o nonce
    # -> na próxima renderização os campos são widgets NOVOS (vazios). Em caso de
    # erro, o nonce não muda e os campos mantêm o que foi digitado (sem reescrever).
    st.session_state.setdefault("_cad_nonce", 0)
    _n = st.session_state._cad_nonce

    st.caption(
        f"Use seu e-mail **{DOMINIO_CORP}** para entrar na hora. Outro e-mail "
        "precisa da aprovação de um administrador."
    )
    with st.form("cadastro_form"):
        nome = st.text_input("Nome completo", key=f"cad_nome_{_n}")
        usuario = st.text_input(
            "E-mail (login)", key=f"cad_user_{_n}",
            placeholder=f"seunome{DOMINIO_CORP}",
        )
        senha = st.text_input("Senha", type="password", key=f"cad_senha_{_n}")
        senha2 = st.text_input("Repita a senha", type="password", key=f"cad_senha2_{_n}")
        enviar = st.form_submit_button("Solicitar acesso", width="stretch")

    if enviar:
        email = usuario.strip().lower()  # guarda em minúsculas p/ evitar duplicar
        eh_corporativo = email.endswith(DOMINIO_CORP)
        # Validação leve de e-mail (tem @ e um ponto depois do @) só p/ o campo
        # fazer sentido — a prova do domínio é o endswith acima.
        email_valido = "@" in email and "." in email.split("@")[-1]
        if not (nome.strip() and email and senha):
            st.error("Preencha todos os campos.")
        elif not email_valido:
            st.error(f"Digite um e-mail válido (ex.: seunome{DOMINIO_CORP}).")
        elif len(senha) < 4:
            st.error("A senha precisa ter pelo menos 4 caracteres.")
        elif senha != senha2:
            st.error("As duas senhas não são iguais.")
        elif db.buscar_usuario(email):
            st.error("Já existe uma conta com esse e-mail. Tente entrar. 🙂")
        else:
            # @natura.net -> ativo (entra na hora). Outro e-mail -> pendente.
            status = "ativo" if eh_corporativo else "pendente"
            db.criar_usuario(email, nome.strip(), _hash(senha),
                             papel="leitor", status=status)
            st.session_state._cad_nonce += 1   # limpa os campos na próxima tela
            if eh_corporativo:
                st.session_state._cad_flash = (
                    "Conta criada! ✅ Já pode entrar com seu e-mail e senha."
                )
            else:
                st.session_state._cad_flash = (
                    f"Cadastro enviado! Como o e-mail não é {DOMINIO_CORP}, um "
                    "administrador precisa aprovar antes de você entrar. ⏳"
                )
            st.rerun()

    if st.button("← Voltar ao login", key="voltar_login"):
        st.session_state._modo_cadastro = False
        st.rerun()


def _form_reset() -> None:
    """Auto-redefinição de senha para LEITORES com e-mail do domínio corporativo.
    Mesma confiança do cadastro (domínio = empresa, sem confirmação por e-mail).
    Admin/editor NÃO redefinem por aqui (protege as contas de mais poder)."""
    st.markdown(
        "<div class='login-sub'>Redefinir senha</div>", unsafe_allow_html=True
    )
    st.caption(
        f"Para leitores com e-mail **{DOMINIO_CORP}**: digite seu e-mail e escolha "
        "uma senha nova. Contas de administrador/editor não redefinem por aqui — "
        "peça a um administrador."
    )
    # Nonce nas chaves: ao redefinir com SUCESSO, limpa os campos (widgets novos).
    st.session_state.setdefault("_reset_nonce", 0)
    _n = st.session_state._reset_nonce

    with st.form("reset_form"):
        email_in = st.text_input(
            "E-mail", key=f"rst_email_{_n}", placeholder=f"seunome{DOMINIO_CORP}"
        )
        senha = st.text_input("Nova senha", type="password", key=f"rst_senha_{_n}")
        senha2 = st.text_input(
            "Repita a nova senha", type="password", key=f"rst_senha2_{_n}"
        )
        enviar = st.form_submit_button("Redefinir senha", width="stretch")

    if enviar:
        email = email_in.strip().lower()
        if not (email and senha):
            st.error("Preencha o e-mail e a nova senha.")
        elif not email.endswith(DOMINIO_CORP):
            st.error(
                f"A redefinição automática é só para e-mails {DOMINIO_CORP}. "
                "Para outros e-mails, peça a um administrador."
            )
        elif len(senha) < 4:
            st.error("A senha precisa ter pelo menos 4 caracteres.")
        elif senha != senha2:
            st.error("As duas senhas não são iguais.")
        else:
            u = db.buscar_usuario(email)
            if not u:
                st.error(
                    "Não encontramos uma conta com esse e-mail. Confira o e-mail "
                    "ou clique em “Criar conta”."
                )
            elif u.get("papel") in ("admin", "editor"):
                st.error(
                    "Contas de administrador/editor não redefinem por aqui, por "
                    "segurança. Peça a um administrador. 🙂"
                )
            elif u.get("status") == "revogado":
                st.error("Seu acesso foi revogado. Fale com um administrador.")
            else:
                db.atualizar_usuario(u["id"], {"senha_hash": _hash(senha)})
                st.session_state._reset_nonce += 1     # limpa os campos
                st.session_state._modo_reset = False   # volta para o login
                st.session_state["_login_flash"] = (
                    "Senha redefinida! ✅ Entre com a nova senha."
                )
                st.rerun()

    if st.button("← Voltar ao login", key="voltar_login_reset"):
        st.session_state._modo_reset = False
        st.rerun()


# ---------------------------------------------------------------------------
# Tela "Gerenciar Usuários" (só admin)
# ---------------------------------------------------------------------------
@st.dialog("👥 Gerenciar Usuários", width="large")
def dialog_gerenciar_usuarios() -> None:
    st.caption("Aprove cadastros, defina papéis, revogue acessos e resete senhas.")

    eu = usuario_atual() or {}
    usuarios = db.listar_usuarios()
    # Pendentes primeiro (para o admin ver quem está esperando aprovação).
    ordem_status = {"pendente": 0, "ativo": 1, "revogado": 2}
    usuarios.sort(key=lambda u: (ordem_status.get(u.get("status"), 9), u.get("id", 0)))

    if not usuarios:
        st.info("Ainda não há usuários cadastrados.")
        return

    # Senha temporária recém-gerada (mostrada uma vez após "Resetar senha").
    _nova = st.session_state.pop("_senha_temp", None)
    if _nova:
        st.success(
            f"Senha redefinida para **{_nova[0]}**. Anote e repasse: `{_nova[1]}`"
        )

    _BADGE = {
        "pendente": "🟡 PENDENTE", "ativo": "🟢 ATIVO", "revogado": "🔴 REVOGADO",
    }

    # Busca por nome OU e-mail — prático quando há muitos usuários. Filtra ao vivo
    # (o st.dialog re-executa a cada tecla e continua ABERTO). Pendentes seguem no
    # topo por causa da ordenação acima; a busca só recorta a lista mostrada.
    _busca = st.text_input(
        "🔎 Pesquisar usuário",
        key="busca_usuarios",
        placeholder="Digite parte do nome ou do e-mail…",
    ).strip().lower()
    if _busca:
        usuarios = [
            u for u in usuarios
            if _busca in (u.get("nome") or "").lower()
            or _busca in (u.get("usuario") or "").lower()
        ]
        st.caption(f"{len(usuarios)} resultado(s) para “{_busca}”.")
        if not usuarios:
            st.info("Nenhum usuário encontrado. Tente outro nome ou e-mail. 🙂")
            return

    for u in usuarios:
        uid, status = u["id"], u.get("status", "")
        sou_eu = uid == eu.get("id")
        st.divider()
        c_info, c_papel, c_status, c_acoes = st.columns([2.5, 2, 1.6, 3])
        with c_info:
            st.markdown(f"**{u.get('usuario','')}**")
            st.caption(u.get("nome", "") or "—")
        with c_papel:
            papel_sel = st.selectbox(
                "Papel", PAPEIS,
                index=PAPEIS.index(u["papel"]) if u.get("papel") in PAPEIS else 2,
                key=f"papel_{uid}", label_visibility="collapsed",
            )
        with c_status:
            st.write(_BADGE.get(status, status))
        with c_acoes:
            b1, b2 = st.columns(2)
            # Aprovar (pendente) / Salvar papel (ativo) / Reativar (revogado)
            if status == "pendente":
                if b1.button("✅ Aprovar", key=f"aprovar_{uid}", width="stretch"):
                    db.atualizar_usuario(uid, {"status": "ativo", "papel": papel_sel})
                    st.rerun()
            elif status == "ativo":
                if b1.button("💾 Papel", key=f"papel_btn_{uid}", width="stretch"):
                    db.atualizar_usuario(uid, {"papel": papel_sel})
                    st.rerun()
            elif status == "revogado":
                if b1.button("♻️ Reativar", key=f"reativar_{uid}", width="stretch"):
                    db.atualizar_usuario(uid, {"status": "ativo", "papel": papel_sel})
                    st.rerun()

            # Revogar (não deixa revogar a própria conta, p/ não se trancar de fora)
            if status != "revogado" and not sou_eu:
                if b2.button("🚫 Revogar", key=f"revogar_{uid}", width="stretch"):
                    db.atualizar_usuario(uid, {"status": "revogado"})
                    st.rerun()

            # Resetar senha: gera uma temporária e mostra uma vez.
            if st.button("🔑 Resetar senha", key=f"reset_{uid}", width="stretch"):
                temp = _secrets.token_urlsafe(6)
                db.atualizar_usuario(uid, {"senha_hash": _hash(temp)})
                st.session_state["_senha_temp"] = (u.get("usuario", ""), temp)
                st.rerun()

            # Remover DE VEZ (diferente de 'revogar': apaga a linha da lista).
            # Pede confirmação e nunca deixa apagar a própria conta (p/ o admin
            # não se trancar de fora). Se a conta for um admin dos secrets iniciais,
            # ela renasce no próximo carregamento — tem de sair também dos secrets.
            if not sou_eu:
                if st.session_state.get(f"_conf_rm_{uid}"):
                    st.caption("Remover mesmo?")
                    r1, r2 = st.columns(2)
                    if r1.button("Sim", key=f"rm_sim_{uid}", width="stretch"):
                        db.remover_usuario(uid)
                        st.session_state.pop(f"_conf_rm_{uid}", None)
                        st.rerun()
                    if r2.button("Não", key=f"rm_nao_{uid}", width="stretch"):
                        st.session_state.pop(f"_conf_rm_{uid}", None)
                        st.rerun()
                elif st.button("🗑️ Remover", key=f"rm_{uid}", width="stretch"):
                    st.session_state[f"_conf_rm_{uid}"] = True
                    st.rerun()
