-- ============================================================
-- Calendario Comercial - criacao das tabelas + dados atuais
-- ============================================================

create table if not exists acoes (
  id bigint generated always as identity primary key,
  acao text not null default '',
  categoria text not null default '',
  inicio date,
  fim date,
  cor text default '',
  detalhes text default '',
  criado_em timestamptz default now()
);

create table if not exists ciclos (
  id bigint generated always as identity primary key,
  ciclo text not null default '',
  inicio date,
  fim date,
  criado_em timestamptz default now()
);

create table if not exists usuarios (
  id bigint generated always as identity primary key,
  usuario text unique not null,
  nome text default '',
  senha_hash text not null,
  papel text not null default 'leitor',
  status text not null default 'pendente',
  criado_em timestamptz default now()
);

-- Limpa qualquer dado anterior destas duas tabelas antes de recarregar
truncate table acoes;
truncate table ciclos;


insert into acoes (acao, categoria, inicio, fim, cor, detalhes) values
('LIQUIDA', 'DESTAQUE DA COMUNICAÇÃO', '2026-07-01', '2026-07-19', '#FFC000', ''),
('DIA DOS PAIS', 'DESTAQUE DA COMUNICAÇÃO', '2026-07-20', '2026-07-31', '#0000FF', ''),
('ESTRATÉGIA DE PAIS (presente empilhado ciclo 10 e 11)', 'PRESENTES', '2026-07-01', '2026-07-31', '#7F7F7F', ''),
('Geral (exceto tododia) 2 itens com 20% | 3 com 30%', 'PROGRESSIVO', '2026-07-01', '2026-07-31', '#990000', ''),
('Tododia -  Exceto sabonetes (2 = 10% // 3 = 20% // 4 = 30%)', 'MONTE SEU RITUAL', '2026-07-01', '2026-07-31', '#CC33FF', ''),
('Ekos - (2 = 20% // 3 = 30%)', 'MONTE SEU RITUAL', '2026-07-13', '2026-07-31', '#6AA84F', ''),
('Chronos - (2 = 20% // 3 = 30%)', 'MONTE SEU RITUAL', '2026-07-13', '2026-07-31', '#BFBFBF', ''),
('Lumina - (2 = 20% // 3 = 30%)', 'MONTE SEU RITUAL', '2026-07-13', '2026-07-31', '#E46C0A', ''),
('KITS com até 30% OFF  (kits com 2 itens com 20% | 3 ou + com 30%)  | COMUNICAÇÃO ATÉ 50% OFF', 'KITS', '2026-07-01', '2026-07-31', '#61CBF3', ''),
('10% OFF no site ou  APP com cupom PRIMEIRACOMPRA', 'PRIMEIRA COMPRA', '2026-07-01', '2026-07-31', '#A9D18E', ''),
('Frete ', 'FRETE', '2026-07-01', '2026-07-02', '#E06666', 'Frete grátis acima de R$149 no site'),
('esquenta 7.7 frete grátis', 'FRETE', '2026-07-03', '2026-07-06', '#BFBFBF', ''),
('Frete grátis acima de R$149 no site', 'FRETE', '2026-07-07', '2026-07-31', '#E06666', ''),
('DE/POR CICLO 11 | COMOUNICAÇÃO ATÉ 50% OFF', 'DE/POR CICLO', '2026-07-01', '2026-07-20', '#ffffff', ''),
('DE/POR CICLO 12 | COMOUNICAÇÃO ATÉ 50% OFF', 'DE/POR CICLO', '2026-07-21', '2026-07-31', '#F9E49C', ''),
('Festival de Refis', 'FLASHSALE / EFEMÉRIDES / DE-POR EXCLUSIVO', '2026-07-01', '2026-07-05', '#000000', 'DE/POR: até 20% refis do site'),
('7.7', 'FLASHSALE / EFEMÉRIDES / DE-POR EXCLUSIVO', '2026-07-07', '2026-07-07', '#000000', 'Compor LP:
- Lista da RI
- Exclusivos que estavam em progressivo/VNP (EXTRA)
- Lista multi até 20% (EXTRA)
- DE/POR vigentes acima de 35%
- Lista de sobras'),
('15/07: Dia Internacional do Homem ', 'FLASHSALE / EFEMÉRIDES / DE-POR EXCLUSIVO', '2026-07-10', '2026-07-15', '#38761D', 'DE/POR produtos masc até 20%'),
('20/07: Dia do Amigo', 'FLASHSALE / EFEMÉRIDES / DE-POR EXCLUSIVO', '2026-07-16', '2026-07-20', '#CC33FF', 'Na compra de 2 itens selecionados, o 2º sai com 50% OFF (lista multicategoria)'),
('26/07: Dia dos Avós', 'FLASHSALE / EFEMÉRIDES / DE-POR EXCLUSIVO', '2026-07-21', '2026-07-27', '#FFC000', 'média de 100 skus
desconsiderar o que tem promo, kvi, o que esta no progressivo de tododia e o que estiver no progressivo geral. foco em outras marcas sem ser ekos e tododia'),
('Liquida: Lista Multi 20% (SEMANAL)', 'FLASHSALE / EFEMÉRIDES / DE-POR EXCLUSIVO', '2026-07-01', '2026-07-20', '#FFC000', 'média de 150 skus
desconsiderar o que tem promo, o que esta no progressivo de tododia e o que estiver no progressivo geral'),
('Oferta Relampago Ecomm: Lista Multi 20% (SEMANAL)', 'FLASHSALE / EFEMÉRIDES / DE-POR EXCLUSIVO', '2026-07-21', '2026-07-31', '#CC33FF', 'Incluir na LP de oferta relâmpago::

média 100 skus / semana
Tirar itens com promo do ciclo anterior, atual e seguinte
Tirar KVIs
Desconsiderar itens do progressivo geral e de tododia
Garantir mix de categoria'),
('LIVE  PAIS', 'FLASHSALE / EFEMÉRIDES / DE-POR EXCLUSIVO', '2026-07-22', '2026-07-24', '#000000', ''),
('29/07: Dia do Batom Lista de batons até 20% + Frete Grátis', 'FLASHSALE / EFEMÉRIDES / DE-POR EXCLUSIVO', '2026-07-27', '2026-07-31', '#FF0000', 'sem numero de skus
desconsiderar o que tem promo, o que esta, e o que estiver no progressivo geral'),
('OFERTA RELÂMPAGO', 'OFERTA RELÂMPAGO', '2026-07-01', '2026-07-05', '#F9CB9C', ''),
('OFERTA RELÂMPAGO', 'OFERTA RELÂMPAGO', '2026-07-06', '2026-07-12', '#E46C0A', ''),
('OFERTA RELÂMPAGO', 'OFERTA RELÂMPAGO', '2026-07-13', '2026-07-19', '#F9CB9C', ''),
('OFERTA RELÂMPAGO', 'OFERTA RELÂMPAGO', '2026-07-20', '2026-07-26', '#E46C0A', ''),
('OFERTA RELÂMPAGO', 'OFERTA RELÂMPAGO', '2026-07-27', '2026-07-31', '#F9CB9C', ''),
('Férias de Beleza e Bem-Estar 20%Off em make, rosto, cabelo, corpo (BEMESTAR)', 'CUPOM SITE', '2026-07-01', '2026-07-12', '#E06666', ''),
('Revele Sua Beleza no Inverno  20%OFF em lista multicategoria (INVERNO20)', 'CUPOM SITE', '2026-07-13', '2026-07-19', '#FF4343', ''),
('24/07: Dia do Autocuidado 20%Off make, rosto, cabelo, corpo (MEUMOMENTO)', 'CUPOM SITE', '2026-07-20', '2026-07-26', '#00FFFF', ''),
('RF 20%', 'CUPOM SITE', '2026-07-27', '2026-07-27', '#0000FF', ''),
('RF 20%', 'CUPOM SITE', '2026-07-06', '2026-07-06', '#0000FF', ''),
('RF 20%', 'CUPOM SITE', '2026-07-13', '2026-07-13', '#0000FF', ''),
('RF 20%', 'CUPOM SITE', '2026-07-20', '2026-07-20', '#0000FF', ''),
('DIA DO PAGAMENTO NATURA', 'CUPOM SITE', '2026-07-08', '2026-07-12', '#93D050', 'compras acima de 99 - R$ 15 OFF
compras acima de 149 - R$ 25 OFF
compras acima de 249 - R$ 50 OFF
CUPOM: PAGAMENTO'),
('Especial dia das pais  20% perfumaria masc + extensões para montar seu presente  Cupom: PAIS20', 'CUPOM SITE', '2026-07-21', '2026-07-31', '#38761D', ''),
('(150340) - Cupom: EKOSCABELOS', 'BRINDE', '2026-07-01', '2026-07-06', '#F4CCCC', 'Compras acima de R$ 99 em Cabelos ganha um Cond Ekos Pataua'),
('(140759) - Cupom: BRINDETODODIA', 'BRINDE', '2026-07-01', '2026-07-06', '#F4CCCC', 'Compras acima de R$ 140 em Corpo ganha um Esfoliante Tododia Macadamia'),
('7.7', 'BRINDE', '2026-07-07', '2026-07-07', '#000000', ''),
('7.7', 'BRINDE', '2026-07-07', '2026-07-07', '#000000', ''),
('7.7', 'BRINDE', '2026-07-07', '2026-07-07', '#000000', ''),
('(164508) - Cupom: MIMOCABELOS', 'BRINDE', '2026-07-08', '2026-07-14', '#F4CCCC', 'Compras acima de R$ 215 em Cabelos ganha um Serum Lumina Força'),
('(189554) - Cupom: MIMOEKOS', 'BRINDE', '2026-07-08', '2026-07-14', '#F4CCCC', 'Compras acima de R$ 110 em Corpo ganha um hid Tukuma 100ml'),
('(3379) - Cupom: MIMOMAKE', 'BRINDE', '2026-07-08', '2026-07-14', '#F4CCCC', 'Compras acima de R$ 99 em Maquiagem ganha um Batom Faces'),
('(6386) - Cupom: BRINDECORPO', 'BRINDE', '2026-07-15', '2026-07-21', '#ffffff', 'Compras acima de R$ 99 em Corpo ganha um Hid Mãos Tododia Tamara'),
('(194223) - Cupom: BRINDEPERF', 'BRINDE', '2026-07-15', '2026-07-21', '#ffffff', 'Compras acima de R$ 180 em Perfumaria ganha um mini Kaiak Oceano Fem'),
('(147460) - Cupom: BRINDEROSTO', 'BRINDE', '2026-07-15', '2026-07-21', '#ffffff', 'Compras acima de R$ 120 em Rosto ganha uma mini Água Micelar'),
('(148455) - Cupom: QUEROLUMINA', 'BRINDE', '2026-07-22', '2026-07-28', '#F4CCCC', 'Compras acima de R$ 220 em Cabelos ganha um Texturizador Lumina'),
('(203389) - Cupom: QUEROEKOS', 'BRINDE', '2026-07-22', '2026-07-28', '#F4CCCC', 'Compras acima de R$ 190 em Corpo ganha um Hid Ekos Açaí 200ml'),
('(151544) - Cupom: QUEROPERF', 'BRINDE', '2026-07-22', '2026-07-28', '#F4CCCC', 'Compras acima de R$ 310 em Perfumaria ganha um mini Essencial Ato Masc'),
('(175105) - Cupom: MAISMAKE', 'BRINDE', '2026-07-29', '2026-07-31', '#ffffff', 'Compras acima de R$ 99 em Maquiagem ganha um Gloss Faces'),
('(2820) - Cupom: QUEROHIDRA', 'BRINDE', '2026-07-29', '2026-07-31', '#ffffff', 'Compras acima de R$ 220 em Corpo ganha Hid Tododia Noz Peca 400ml'),
('(194225) - Cupom: MAISPERF', 'BRINDE', '2026-07-29', '2026-07-31', '#ffffff', 'Compras acima de R$ 299 em Perfumaria ganha um mini Ilia Secreto'),
('OFERTA DA MADRUGADA', 'CALENDÁRIO CRM', '2026-07-02', '2026-07-03', '#E06666', ''),
('OFERTA DA MADRUGADA', 'CALENDÁRIO CRM', '2026-07-09', '2026-07-10', '#E06666', ''),
('OFERTA DA MADRUGADA', 'CALENDÁRIO CRM', '2026-07-16', '2026-07-17', '#E06666', ''),
('OFERTA DA MADRUGADA', 'CALENDÁRIO CRM', '2026-07-23', '2026-07-24', '#E06666', ''),
('OFERTA DA MADRUGADA', 'CALENDÁRIO CRM', '2026-07-30', '2026-07-31', '#E06666', ''),
('PAIS', 'DESTAQUE DA COMUNICAÇÃO', '2026-08-01', '2026-08-09', '#0000FF', ''),
('NATURA WEEK', 'DESTAQUE DA COMUNICAÇÃO', '2026-08-10', '2026-08-23', '#FFC000', ''),
('ESQUENTA MÊS DO CLIENTE', 'DESTAQUE DA COMUNICAÇÃO', '2026-08-24', '2026-08-31', '#38761D', ''),
('ESTRATÉGIA DE PAIS (presente empilhado ciclo 10 e 11)', 'PRESENTES', '2026-08-01', '2026-08-09', '#7F7F7F', ''),
('manter presentes que tiverem estoque', 'PRESENTES', '2026-08-10', '2026-08-31', '#FFFFFF', ''),
('Geral (exceto tododia) 2 itens com 20% | 3 com 30%', 'PROGRESSIVO', '2026-08-01', '2026-08-31', '#741B47', ''),
('Tododia -  Exceto sabonetes (2 = 10% // 3 = 20% // 4 = 30%)', 'MONTE SEU RITUAL', '2026-08-01', '2026-08-31', '#CC33FF', ''),
('Ekos - (2 = 20% // 3 = 30%)', 'MONTE SEU RITUAL', '2026-08-01', '2026-08-31', '#6AA84F', ''),
('Chronos - (2 = 20% // 3 = 30%)', 'MONTE SEU RITUAL', '2026-08-01', '2026-08-31', '#BFBFBF', ''),
('Lumina - (2 = 20% // 3 = 30%)', 'MONTE SEU RITUAL', '2026-08-01', '2026-08-31', '#FFC000', ''),
('KITS com até 30% OFF  (kits com 2 itens com 20% | 3 ou + com 30%)  | COMUNICAÇÃO ATÉ 50% OFF', 'KITS', '2026-08-01', '2026-08-31', '#0000FF', ''),
('10% OFF no site ou  APP com cupom PRIMEIRACOMPRA', 'PRIMEIRA COMPRA', '2026-08-01', '2026-08-31', '#A9D18E', ''),
('Frete grátis acima de R$149 no site', 'FRETE', '2026-08-01', '2026-08-31', '#E06666', ''),
('DE/POR CICLO 12 | CMOUNICAÇÃO ATÉ XX% OFF CONFIRMAR', 'DE/POR CICLO', '2026-08-01', '2026-08-10', '#FFFFFF', ''),
('DE/POR CICLO 13 | CMOUNICAÇÃO ATÉ XX% OFF CONFIRMAR', 'DE/POR CICLO', '2026-08-11', '2026-08-31', '#F4CCCC', ''),
('Esquenta 8.8 Lista Multi 20%', 'FLASHSALE / EFEMÉRIDES / DE-POR EXCLUSIVO', '2026-08-03', '2026-08-06', '#BFBFBF', ''),
('8.8', 'FLASHSALE / EFEMÉRIDES / DE-POR EXCLUSIVO', '2026-08-07', '2026-08-09', '#000000', ''),
('NATURA WEEK Lista Multi 20% (SEMANAL)', 'FLASHSALE / EFEMÉRIDES / DE-POR EXCLUSIVO', '2026-08-10', '2026-08-23', '#FFC000', 'média de 150 skus
desconsiderar o que tem promo, o que esta no progressivo de tododia e o que estiver no progressivo geral'),
('LIVE', 'FLASHSALE / EFEMÉRIDES / DE-POR EXCLUSIVO', '2026-08-25', '2026-08-30', '#000000', ''),
('OFERTA RELÂMPAGO', 'OFERTA RELÂMPAGO', '2026-08-01', '2026-08-02', '#F4CCCC', ''),
('OFERTA RELÂMPAGO', 'OFERTA RELÂMPAGO', '2026-08-03', '2026-08-09', '#F9CB9C', ''),
('OFERTA RELÂMPAGO', 'OFERTA RELÂMPAGO', '2026-08-10', '2026-08-16', '#F4CCCC', ''),
('OFERTA RELÂMPAGO', 'OFERTA RELÂMPAGO', '2026-08-17', '2026-08-23', '#F9CB9C', ''),
('OFERTA RELÂMPAGO', 'OFERTA RELÂMPAGO', '2026-08-24', '2026-08-30', '#F4CCCC', ''),
('Especial dia das pais  20% perfumaria masc + extensões para montar seu presente', 'CUPOM SITE', '2026-08-01', '2026-08-09', '#0000FF', ''),
('HAPPY WEEKEND', 'CUPOM SITE', '2026-08-14', '2026-08-16', '#93D050', '20% OFF + Frete Grátis
multicategoria
Cupom: HAPPY20
CUPOM ML:'),
('HAPPY WEEKEND', 'CUPOM SITE', '2026-08-21', '2026-08-23', '#93D050', '20% OFF + Frete Grátis
multicategoria
Cupom: HAPPY20
CUPOM ML:'),
('HAPPY WEEKEND', 'CUPOM SITE', '2026-08-28', '2026-08-30', '#93D050', '20% OFF + Frete Grátis
multicategoria
Cupom: HAPPY20
CUPOM ML:'),
('RF 20%', 'CUPOM SITE', '2026-08-03', '2026-08-03', '#CC33FF', ''),
('RF 20%', 'CUPOM SITE', '2026-08-10', '2026-08-10', '#CC33FF', ''),
('RF 20%', 'CUPOM SITE', '2026-08-24', '2026-08-24', '#CC33FF', ''),
('RF 20%', 'PRESENTES', '2026-08-17', '2026-08-17', '#CC33FF', ''),
('RF 20%', 'CUPOM SITE', '2026-08-31', '2026-08-31', '#CC33FF', ''),
('MECÂNICA: Esquenta 8.8 Desbloqueie até R$88 OFF no 8.8', 'CUPOM SITE', '2026-08-03', '2026-08-09', '#7F7F7F', 'R$8 OFF em R$80
🔓 R$18 OFF em R$160
🔓 R$38 OFF em R$240
🔓 R$58 OFF em R$320
🔓 R$88 OFF em R$400'),
('NATURA WEEK', 'CUPOM SITE', '2026-08-10', '2026-08-16', '#61CBF3', 'CUPOM 15% OFF perfumaria, deos, corpo, proteção
CUPOM: 
CUPOM ML:'),
('NATURA WEEK', 'CUPOM SITE', '2026-08-17', '2026-08-23', '#83CCEB', 'CUPOM 15% OFF cabelos, sab, rosto e make
CUPOM: 
CUPOM ML:'),
('ESQUENTA MÊS DO CLIENTE:  CUPOM 15% OFF MULTICATEGORIAS:  CUPOM:  CUPOM ML:', 'CUPOM SITE', '2026-08-24', '2026-08-31', '#6AA84F', '');

insert into ciclos (ciclo, inicio, fim) values
('CICLOS - C10 e C11', '2026-06-01', '2026-06-20'),
('CICLOS - C11 e C12', '2026-06-21', '2026-06-30'),
('PREÇO 11  ::  Portifólio C10 e C11', '2026-07-01', '2026-07-20'),
('PREÇO 12  ::  Portifólio C11 e C12', '2026-07-21', '2026-07-31'),
('PREÇO 12  ::  Portifólio C11 e C12', '2026-08-01', '2026-08-10'),
('PREÇO 13  ::  Portifólio C12 e C13', '2026-08-11', '2026-08-31');
