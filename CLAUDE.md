# Calendário da Grade Comercial

App **Streamlit** (Python) que desenha um calendário mensal de ações/promoções comerciais
como uma linha do tempo (gráfico Plotly), com um formulário para adicionar ações e ciclos,
uma tabela para editar/excluir, e exportação para Excel formatado.

O usuário (Hudson) **não é programador** — trabalha de forma visual e iterativa, validando
com **prints anotados** (setas/quadrados). Fala português. Entregar mudanças pequenas e
explicar em linguagem simples o que mudou e o que conferir na tela.

## Como rodar
- Windows: dar duplo-clique em `iniciar.bat` (cria o venv na 1ª vez e roda `streamlit run app.py`).
- O venv é do **Windows** (`.venv/Scripts/`). No WSL **não há navegador headless nem as libs
  no `python3`** — então **não dá para tirar screenshot** para medir layout, nem rodar o app aqui.
- Verificação de sanidade após editar: `python3 -m py_compile app.py` (só checa sintaxe, não nomes).

## Arquivos
- `app.py` — a interface do calendário (formulário, gráfico, tabela, Excel).
- `db.py` — camada de dados no **Supabase** (ações, ciclos, usuários). Usa a chave
  `service_role` (em `st.secrets`) que ignora o RLS.
- `auth.py` — login, papéis e a tela "Gerenciar Usuários" (bcrypt nas senhas).
- `acoes.csv` / `ciclos.csv` — **histórico** (fonte da migração inicial). O app **não usa
  mais** esses arquivos: os dados vivem no Supabase (tabelas `acoes`, `ciclos`, `usuarios`).
- `supabase_setup.sql` — script que criou as tabelas + carregou os dados iniciais.
- `requirements.txt` — streamlit, plotly, pandas, openpyxl, supabase, bcrypt.
- `.streamlit/secrets.toml.example` — modelo dos segredos (valores reais vão na hospedagem).
- `app_backup_AAAAMMDD_HHMMSS.py` — backups locais com data/hora.
  **Convenção: ao terminar um bloco de mudanças, o usuário costuma pedir para atualizar o backup**
  → `cp -p app.py "app_backup_$(date +%Y%m%d_%H%M%S).py"`.

## Multiusuário / online (Supabase + login)
- Hospedagem alvo: **Streamlit Community Cloud** (deploy a partir do GitHub). Ver
  [[calendario-multiusuario]] na memória.
- **Papéis**: `admin` (tudo + gerenciar usuários), `editor` (edita calendário), `leitor`
  (só vê + baixa Excel). No `app.py`: `PAPEL`, `PODE_EDITAR`, `EH_ADMIN` (definidos logo
  após o portão de login) controlam o que aparece.
- **Login/cadastro**: `auth.tela_login()` (cara Natura). O **login é o e-mail**. Cadastro
  automático por domínio (`auth.DOMINIO_CORP`, hoje `@natura.net`): e-mail do domínio →
  nasce `leitor`/`ativo` (entra na hora, sem aprovação); qualquer outro e-mail → `pendente`
  → admin aprova em `auth.dialog_gerenciar_usuarios()` (que também tem **Revogar** e o
  **Remover** = apaga a linha de vez, via `db.remover_usuario`). Admins iniciais nascem dos
  secrets `[[admin_inicial]]` via `auth.inicializar()` (só cria se não existir; se remover um
  admin pela tela mas ele continuar nos secrets, renasce no próximo carregamento).
- **Esqueci a senha** (`auth._form_reset`, modo `_modo_reset`): auto-redefinição SÓ para
  **leitores** do domínio (`DOMINIO_CORP`) — digita e-mail + senha nova, sem confirmação por
  e-mail (mesma confiança do cadastro). **admin/editor são barrados** aqui de propósito (protege
  as contas de mais poder — usam o "🔑 Resetar senha" da tela de gestão). Sucesso volta ao login
  com aviso via `_login_flash`.
- **Segredos** (`st.secrets`): `[supabase] url/service_key` e os `[[admin_inicial]]`.
  Nunca commitar `.streamlit/secrets.toml` (está no `.gitignore`).
- `carregar/salvar/carregar_ciclos/salvar_ciclos` mantêm a MESMA assinatura de antes, mas
  por dentro falam com o Supabase (mapas `_MAPA_ACOES`/`_MAPA_CICLOS` traduzem as colunas
  com acento do app ↔ sem acento do banco). Salvar = apaga tudo e reinsere (volume pequeno).

## Estrutura do app.py (mapa mental)
1. **Constantes**: `CATEGORIAS_PADRAO` (faixas), `CORES_CICLO`, `PALETA_CORES` (22 cores da paleta),
   `COLUNAS`, helper `_contraste_texto(hex)` (preto/branco conforme luminância).
2. **Seletor de Mês/Ano** no topo (`mes_num`, `ano`) → o app é focado em **um mês por vez**.
3. **Expander "Adicionar nova ação"** (recolhido por padrão; reabre após cadastrar via
   `st.session_state._add_aberto`):
   - Campos usam chave com sufixo `_{_n}` (nonce `form_nonce`); ao salvar, incrementa o nonce
     → campos viram widgets novos (limpos). É o método de "limpar formulário".
   - **Datas únicas** `data_inicio`/`data_fim` valem para o Ciclo **e/ou** para a Ação (não há
     datas separadas). Ficam **limitadas ao mês selecionado** (`min_value`/`max_value`) e a chave
     inclui `{ano}{mes}` para resetar ao trocar de mês (o popup já abre no mês correto).
   - **Paleta de cores**: botões `st.button` coloridos via CSS `.st-key-cor_btn_<i>`. **Precisa ficar
     FORA de `st.form`** (por isso o form virou `st.container()` + `st.button` comum). A paleta é
     renderizada ANTES do color_picker "Ajustar tom" no código (os botões setam `cor_tom`, que não
     pode ser modificado depois do widget existir). Posição visual vem da ORDEM das colunas.
4. **Gráfico Plotly (`px.timeline`)** — o calendário. São **TRÊS** figuras alinhadas
   (mesma margem `l=120/r=10` e mesmo intervalo de datas), dentro do envelope rolável
   `cal_scroll`: **`fig_head`** (Portfólio do Ciclo + SEMANAS + datas) e **`fig_destaque`**
   (a faixa `FAIXA_FIXA_TOPO` = "DESTAQUE DA COMUNICAÇÃO") ficam no quadro FIXO `cal_head_box`
   (não rola); **`fig`** (as demais faixas = `FAIXAS_CORPO`) fica no quadro rolável `cal_box`.
   `plot_df` é dividido em `topo_df` (faixa fixa, 1 sub-linha — nunca empilha) e o corpo.
   `_linha_vazia(cat)` gera placeholder transparente p/ faixa aparecer vazia sem dados.
   - Texto das barras: negrito + cor de contraste por barra; nomes compridos quebram em **até 2
     linhas** só quando **não cabem** na largura da barra (`CHARS_LARGURA_CHEIA`, hoje 75).
   - Fins de semana em **vermelho** nos rótulos; faixa amarela/azul do "Portfólio do Ciclo" no topo.
   - Linha sutil entre ações empilhadas (sub-linhas) da mesma faixa.
5. **Expander "Editar ou excluir ações"** (recolhido): `st.data_editor`. Coluna **Categoria é um
   `SelectboxColumn`** (opções = CATEGORIAS_PADRAO + já usadas). Botões Salvar / Baixar Excel /
   **Limpar calendário** (com confirmação + backup) na mesma linha.
   - **Gotcha**: colunas de texto viram `float` quando o mês está vazio e quebram o `data_editor`
     → sempre `fillna("").astype(str)` antes.
6. **Exportar Excel** (openpyxl): cabeçalho verde/negrito, bordas, largura automática, datas
   **dd/mm/aaaa**, cabeçalho fixo. NÃO exporta a coluna "Cor" (hex).

## Preferências do usuário / como iterar
- Confie na **imagem anotada**, não no termo — ele às vezes troca "largura" e "comprimento".
- Ajustes de layout em pixels (ex.: `height`) costumam levar 1–2 rodadas; ofereça afinar o número.
- Limitação do Streamlit relevante: **colunas aninhadas só até 1 nível** (por isso a paleta não
  cabe ao lado da Descrição — fica em largura total abaixo).
- Regra de negócio: **cada mês é fechado em si**. Datas só dentro do mês; ação que passa para o
  mês seguinte é cadastrada entrando naquele mês.
