-- ============================================================
-- Multi-empresa (Natura + Avon) — adiciona a coluna "marca" e ajusta a grade.
-- Rode UMA VEZ no Supabase: painel do projeto -> SQL Editor -> cole tudo -> Run.
-- É SEGURO: tudo que já existe vira 'natura' automaticamente; a Avon nasce vazia.
-- ============================================================

-- 1) Coluna "marca" nas tabelas de dados. Default 'natura' => todos os dados
--    atuais passam a ser da Natura; a Avon começa sem nada.
alter table acoes          add column if not exists marca text not null default 'natura';
alter table ciclos         add column if not exists marca text not null default 'natura';
alter table grade_listas   add column if not exists marca text not null default 'natura';
alter table grade_produtos add column if not exists marca text not null default 'natura';

-- 2) grade_listas: a "chave única" deixa de ser só lista_nome e passa a ser
--    (marca, lista_nome) — assim Natura e Avon podem ter a MESMA "LISTA_20",
--    cada uma com a sua, sem uma sobrescrever a outra.
alter table grade_listas drop constraint if exists grade_listas_lista_nome_key;
alter table grade_listas add constraint grade_listas_marca_lista_key unique (marca, lista_nome);

-- 3) Índices por empresa (deixa os filtros por marca mais rápidos). Opcional.
create index if not exists idx_acoes_marca          on acoes (marca);
create index if not exists idx_ciclos_marca         on ciclos (marca);
create index if not exists idx_grade_listas_marca   on grade_listas (marca);
create index if not exists idx_grade_produtos_marca on grade_produtos (marca);

-- Pronto! O app já vai separar Natura e Avon usando esta coluna "marca".
