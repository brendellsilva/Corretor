# Corretor de Provas

Ferramenta web para professores corrigirem provas pelo celular: múltipla escolha e questões abertas, com leitura por IA, separação automática por aluno, relatórios para imprimir e planilha de notas.

Funciona no navegador do celular (Android ou iPhone) e do computador. Para salvar direto numa pasta do computador, use Chrome ou Edge.

## Como a professora usa (4 etapas)

1. **Gabarito:** nome da prova, número de questões e a resposta certa de cada uma (toque na letra ou em "Aberta"). Pontuação com o mesmo valor para todas, ou valor por questão. Fica salvo no navegador.
2. **Fotos:** "Tirar foto" para cada página, em sequência, aluno por aluno, começando pela página com o nome. Também dá para escolher da galeria ou de uma pasta do computador.
3. **Conferir:** o sistema lê as respostas, separa os alunos e marca em laranja o que precisa de atenção. Se errar a separação, use os três pontinhos da foto ("Esta foto é de outro aluno") ou "Juntar com o aluno de cima". As correções feitas à mão são mantidas.
4. **Entregar:** imprimir os relatórios (folha completa ou fichas para grampear, 4 por folha) e baixar um ZIP com uma pasta por aluno, a planilha de notas e os relatórios.

A correção fica guardada no aparelho: se a página recarregar, continua de onde parou. "Começar uma correção nova", nos Ajustes (⚙️), apaga as fotos e as notas, mas mantém o gabarito.

## Questões abertas

A IA transcreve a resposta tal como foi escrita (palavras duvidosas em amarelo), sugere a nota com uma justificativa e indica a confiança da leitura. A professora confirma ou ajusta. Notas não conferidas saem nos relatórios como "nota provisória".

Para letra difícil, pode usar um modelo mais forte definindo `MODELO` na Vercel (por exemplo `claude-opus-5-5`).

## Estrutura

- `index.html`: a ferramenta inteira.
- `api/ler.js`: função da Vercel que recebe uma foto e chama a API da Anthropic. A chave nunca chega ao navegador.
- `tests/ui_test.py`: teste do fluxo completo com Playwright e leituras simuladas, em 360, 390, 768 e 1360 px. Uso: `SHOTS=/tmp/shots FOTOS=pasta_com_fotos python3 tests/ui_test.py` (`UX=1` gera capturas em todas as larguras). Tem de terminar com 0 falhas.

## Deploy na Vercel

1. Em vercel.com, **Add New → Project** e importe este repositório.
2. Em **Environment Variables**, crie:
   - `ANTHROPIC_API_KEY` (ou `CLAUDE_API_KEY`): a chave criada na Claude Console.
   - `CODIGO_ACESSO`: o código que a professora digita na primeira vez.
   - `MODELO` (opcional): por omissão `claude-sonnet-5-5`.
3. **Deploy**. Partilhe o link e o código.

Para testar com o gabarito de exemplo (prova M0504), abra o link com `#teste` no fim: aparece "Carregar gabarito de exemplo" nos Ajustes.

## Segurança

- Use uma chave dedicada e um limite de gasto na Claude Console.
- Se o código de acesso se espalhar, troque-o na Vercel e faça Redeploy.
- As fotos são enviadas para a API da Anthropic para leitura. Confirme as regras da escola sobre dados de alunos (LGPD).
