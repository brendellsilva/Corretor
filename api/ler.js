// Função da Vercel: recebe UMA foto de prova e devolve as questões e as alternativas marcadas.
// Variáveis de ambiente: ANTHROPIC_API_KEY (ou CLAUDE_API_KEY), CODIGO_ACESSO e, opcional, MODELO.

const PROMPT = `Esta imagem é UMA página da prova de múltipla escolha de um aluno.
Identifique os números das questões que aparecem nesta página e, para cada questão, a alternativa que o aluno marcou (letra circulada, riscada ou com X sobre a letra).
Se a questão não tiver marca clara, ou tiver mais de uma marca, use "-".
Se o nome do aluno estiver escrito nesta página, devolva-o; caso contrário use null.
Responda APENAS com JSON válido, sem texto extra, neste formato:
{"nome": null, "questoes": [2], "respostas": {"2": "C"}}`;

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ erro: 'Método não permitido' });

  const { codigo, imagem } = req.body || {};
  if (!process.env.CODIGO_ACESSO || codigo !== process.env.CODIGO_ACESSO) {
    return res.status(401).json({ erro: 'Código de acesso inválido.' });
  }
  if (typeof imagem !== 'string' || imagem.length < 100) {
    return res.status(400).json({ erro: 'Imagem em falta.' });
  }

  try {
    const r = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': process.env.ANTHROPIC_API_KEY || process.env.CLAUDE_API_KEY,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json',
      },
      body: JSON.stringify({
        model: process.env.MODELO || 'claude-sonnet-5-5',
        max_tokens: 1000,
        messages: [{
          role: 'user',
          content: [
            { type: 'image', source: { type: 'base64', media_type: 'image/jpeg', data: imagem } },
            { type: 'text', text: PROMPT },
          ],
        }],
      }),
    });
    const data = await r.json();
    if (!r.ok) return res.status(502).json({ erro: data?.error?.message || 'Falha na API' });

    const txt = (data.content || []).filter(b => b.type === 'text').map(b => b.text).join('');
    const json = JSON.parse(txt.slice(txt.indexOf('{'), txt.lastIndexOf('}') + 1));
    return res.status(200).json({
      nome: json.nome ?? null,
      questoes: Array.isArray(json.questoes) ? json.questoes : [],
      respostas: json.respostas || {},
    });
  } catch (e) {
    return res.status(500).json({ erro: 'Não foi possível ler a foto.' });
  }
}
