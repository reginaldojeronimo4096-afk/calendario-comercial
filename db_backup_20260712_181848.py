# -*- coding: utf-8 -*-
"""
Camada de dados no Supabase (banco online).

Guarda três tabelas: 'acoes', 'ciclos' e 'usuarios'. O app fala com o banco
usando a chave *service_role* (guardada em st.secrets, NUNCA no código) — essa
chave tem acesso total e ignora o RLS (a trava de segurança do banco).

Se um dia quiser trocar o banco de lugar, é só mexer AQUI: o resto do app chama
só estas funções.
"""
from datetime import datetime, timezone

import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def _cliente() -> Client:
    """Conexão única com o Supabase (reaproveitada entre as telas)."""
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["service_key"]
    return create_client(url, key)


# ---------------------------------------------------------------------------
# Ações do calendário
# ---------------------------------------------------------------------------
def listar_acoes() -> list:
    r = _cliente().table("acoes").select("*").order("id").execute()
    return r.data or []


def substituir_acoes(registros: list) -> None:
    """Regrava TODAS as ações (apaga tudo e insere de novo) — espelha o antigo
    'salvar CSV inteiro'. Volume é pequeno, então é simples e seguro."""
    c = _cliente()
    c.table("acoes").delete().gte("id", 0).execute()
    if registros:
        c.table("acoes").insert(registros).execute()


# ---------------------------------------------------------------------------
# Ciclos (Portfólio do Ciclo)
# ---------------------------------------------------------------------------
def listar_ciclos() -> list:
    r = _cliente().table("ciclos").select("*").order("id").execute()
    return r.data or []


def substituir_ciclos(registros: list) -> None:
    c = _cliente()
    c.table("ciclos").delete().gte("id", 0).execute()
    if registros:
        c.table("ciclos").insert(registros).execute()


# ---------------------------------------------------------------------------
# Usuários (login)
# ---------------------------------------------------------------------------
def buscar_usuario(usuario: str):
    """Retorna o dict do usuário (ou None). Busca sem diferenciar maiúsculas."""
    r = (
        _cliente()
        .table("usuarios")
        .select("*")
        .ilike("usuario", (usuario or "").strip())
        .limit(1)
        .execute()
    )
    return r.data[0] if r.data else None


def listar_usuarios() -> list:
    r = _cliente().table("usuarios").select("*").order("id").execute()
    return r.data or []


def criar_usuario(usuario, nome, senha_hash, papel="leitor", status="pendente") -> None:
    _cliente().table("usuarios").insert(
        {
            "usuario": usuario,
            "nome": nome,
            "senha_hash": senha_hash,
            "papel": papel,
            "status": status,
        }
    ).execute()


def atualizar_usuario(usuario_id, campos: dict) -> None:
    _cliente().table("usuarios").update(campos).eq("id", usuario_id).execute()


def remover_usuario(usuario_id) -> None:
    """Apaga o usuário DE VEZ (diferente de 'revogar', que só desativa e mantém
    a linha na lista). Usado pela tela Gerenciar Usuários p/ limpar cadastros."""
    _cliente().table("usuarios").delete().eq("id", usuario_id).execute()


# ---------------------------------------------------------------------------
# Grade de Ativação (promoções + produtos)
# ---------------------------------------------------------------------------
def grade_listar_listas() -> list:
    r = _cliente().table("grade_listas").select("*").order("tipo").execute()
    return r.data or []


def grade_upsert_lista(lista: dict) -> None:
    """Cria/atualiza a promoção pela chave 'lista_nome' (substitui ao subir grade
    nova). Listas que não vierem no arquivo NÃO são tocadas (viram histórico)."""
    dados = dict(lista)
    dados["atualizado_em"] = datetime.now(timezone.utc).isoformat()
    _cliente().table("grade_listas").upsert(dados, on_conflict="lista_nome").execute()


def grade_substituir_produtos(lista_nome: str, produtos: list) -> None:
    """Troca TODOS os produtos daquela promoção pelos novos (apaga e reinsere)."""
    c = _cliente()
    c.table("grade_produtos").delete().eq("lista_nome", lista_nome).execute()
    for i in range(0, len(produtos), 500):        # insere em lotes de 500
        lote = produtos[i:i + 500]
        if lote:
            c.table("grade_produtos").insert(lote).execute()


def grade_listar_produtos(lista_nome: str) -> list:
    r = (
        _cliente()
        .table("grade_produtos")
        .select("*")
        .eq("lista_nome", lista_nome)
        .order("id")
        .execute()
    )
    return r.data or []


def grade_apagar_lista(lista_nome: str) -> None:
    """Apaga UMA promoção (a lista + os produtos dela)."""
    c = _cliente()
    c.table("grade_produtos").delete().eq("lista_nome", lista_nome).execute()
    c.table("grade_listas").delete().eq("lista_nome", lista_nome).execute()


def grade_apagar_todas() -> None:
    """Apaga TODAS as promoções (todas as listas + todos os produtos)."""
    c = _cliente()
    c.table("grade_produtos").delete().gte("id", 0).execute()
    c.table("grade_listas").delete().gte("id", 0).execute()
