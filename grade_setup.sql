-- ============================================================
-- Promocoes (Grade de Ativacao) - criacao das 2 tabelas
-- ============================================================

-- Promocoes (uma por aba LISTA_ visivel). Chave = lista_nome, para SUBSTITUIR ao
-- subir grade nova; listas que somem ficam como historico (nao sao apagadas).
create table if not exists grade_listas (
  id bigint generated always as identity primary key,
  lista_nome text unique not null,
  tipo text default '',
  ciclo text default '',
  periodo text default '',
  periodo_acao text default '',   -- período da AÇÃO (B1/C1 da aba, ou "Todo o ciclo")
  link_lp text default '',
  total_skus int default 0,
  comissao numeric,
  cupom numeric,
  depor numeric,
  atualizado_em timestamptz default now()
);
alter table grade_listas enable row level security;

-- Produtos de cada promocao.
create table if not exists grade_produtos (
  id bigint generated always as identity primary key,
  lista_nome text not null,
  sku text default '',
  descricao text default '',
  categoria text default '',
  linha text default '',
  kvis text default '',
  mecanica text default '',
  selo text default '',
  preco_de numeric,
  preco_por numeric,
  desconto numeric,
  ciclo_promo text default '',
  tipo text default ''
);
create index if not exists idx_grade_produtos_lista on grade_produtos (lista_nome);
alter table grade_produtos enable row level security;
