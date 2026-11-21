# Corretor de Provas

Ferramenta web para professores: escolhe uma pasta de origem com as fotos das provas (uma subpasta por aluno) e uma pasta de destino. A IA lê as alternativas marcadas, o professor revê, e a ferramenta copia as fotos renomeadas e gera um Excel com as notas e os detalhes de cada aluno.

Funciona no Chrome ou Edge de computador.

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
