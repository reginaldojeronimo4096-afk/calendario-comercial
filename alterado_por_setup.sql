-- Migração: coluna de auditoria "Alterado por" (quem mexeu por último em cada ação)
-- Necessária a partir de 2026-07-25 (app.py salvar() manda a chave 'alterado_por').
-- Sem esta coluna, SALVAR o calendário quebra (Supabase rejeita coluna inexistente).
-- A tabela 'acoes' é compartilhada por Natura e Avon (separadas pela coluna 'marca'),
-- então esta ÚNICA coluna cobre as duas marcas. Rodar UMA vez no Supabase (SQL Editor).

ALTER TABLE acoes ADD COLUMN IF NOT EXISTS alterado_por text DEFAULT '';
