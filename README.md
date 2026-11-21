# Corretor de Provas

Ferramenta web para professores, para provas de múltipla escolha e questões abertas: escolhe uma pasta de origem com as fotos das provas (uma subpasta por aluno) e uma pasta de destino. A IA lê as alternativas marcadas, o professor revê, e a ferramenta copia as fotos renomeadas e gera um Excel com as notas e os detalhes de cada aluno.

Funciona no Chrome ou Edge de computador.

## Fotos em sequência (telemóvel)

Toque em **Tirar foto** para cada página, prova a prova: primeira página do João, páginas seguintes, primeira página do Guilherme, e assim por diante. Em **Ler e separar por aluno**, a IA reconhece a primeira página de cada aluno, lê o nome e as respostas e separa as fotos. Se errar, use **Novo aluno daqui** numa foto ou **Juntar ao aluno anterior** num aluno.

Sem pasta de destino (sempre no telemóvel), o resultado é descarregado num ZIP com uma pasta por aluno e o Excel.

## Questões abertas

No gabarito, escolha "Aberta" na questão e escreva a resposta esperada e os critérios com pontos. A IA transcreve a resposta do aluno tal como foi escrita (palavras duvidosas ficam destacadas), sugere a nota com uma justificação e um nível de confiança. A professora confirma ou ajusta cada nota. O Excel guarda a transcrição, a sugestão da IA, a nota final e se foi revista.

Para letra difícil, pode usar um modelo mais forte definindo `MODELO` na Vercel (por exemplo `claude-opus-5-5`).

## Estrutura

- `index.html`: a ferramenta (gabarito, pontos por questão, pastas, revisão, Excel).
- `api/ler.js`: função da Vercel que recebe uma foto e chama a API da Anthropic. A chave nunca chega ao navegador.

## Deploy na Vercel

1. Em vercel.com, **Add New → Project** e importe este repositório.
2. Em **Environment Variables**, crie:
   - `ANTHROPIC_API_KEY` (ou `CLAUDE_API_KEY`): a chave criada na Claude Console.
   - `CODIGO_ACESSO`: um código à sua escolha, que vai dar aos professores.
   - `MODELO` (opcional): por omissão `claude-sonnet-5-5`.
3. Clique em **Deploy**. Partilhe o link e o código de acesso com o professor.

Para mudar a chave ou o código, altere a variável em **Settings → Environment Variables** e faça **Redeploy**.

## Segurança

- Use uma chave dedicada e um limite de gasto na Claude Console.
- Se o código de acesso for partilhado com quem não deve, troque-o na Vercel.
- As fotos são enviadas para a API da Anthropic para leitura. Confirme as regras da escola sobre dados de alunos.
