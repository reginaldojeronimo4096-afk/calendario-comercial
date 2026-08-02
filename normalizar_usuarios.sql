-- Normaliza os e-mails de login já cadastrados para minúsculas (sem espaços).
-- Necessário junto com o fix de 2026-08-02 em db.buscar_usuario (que passou a buscar
-- por IGUALDADE EXATA em minúsculas, no lugar do 'ilike' com coringa). Se algum e-mail
-- tiver ficado gravado com maiúscula, sem isto o login dele deixaria de casar.
-- Rodar UMA vez no SQL Editor do Supabase. É idempotente (inofensivo se já minúsculo).
--
-- CUIDADO (raro): se existirem DUAS contas que só diferem por maiúscula/minúscula
-- (ex.: 'Maria@natura.net' e 'maria@natura.net'), e a coluna 'usuario' tiver UNIQUE,
-- este UPDATE falha por conflito — nesse caso apague/mescle a duplicada antes.

UPDATE usuarios SET usuario = lower(trim(usuario))
WHERE usuario <> lower(trim(usuario));
