"""Teste do fluxo completo com Playwright e leituras simuladas da IA.
Uso: SHOTS=/tmp/shots FOTOS=/caminho/fotos python3 tests/ui_test.py
Precisa de: pip playwright, Chrome em /usr/bin/google-chrome, xlsx e jszip em /tmp/node_modules."""
import asyncio, glob, json, os, sys, threading, http.server, functools, zipfile, io
from playwright.async_api import async_playwright

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.environ.get('SHOTS', '/tmp/shots'); os.makedirs(SHOTS, exist_ok=True)
FOTOS = sorted(glob.glob(os.path.join(os.environ.get('FOTOS', '/mnt/user-data/uploads'), '*.jpg')))[:12]
LIBS = {'xlsx.full.min.js': '/tmp/node_modules/xlsx/dist/xlsx.full.min.js', 'jszip.min.js': '/tmp/node_modules/jszip/dist/jszip.min.js'}
falhas = []
def check(ok, msg):
    print(('OK   ' if ok else 'FALHA ') + msg)
    if not ok: falhas.append(msg)

def servir():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=RAIZ)
    h.log_message = lambda *a: None
    s = http.server.ThreadingHTTPServer(('127.0.0.1', 8765), h)
    threading.Thread(target=s.serve_forever, daemon=True).start()

def resposta_falsa(n):
    # fotos 1 a 6: João; 7 a 12: Guilherme
    primeira = n in (1, 7)
    nome = 'João Pedro' if n == 1 else ('Guilherme Souza' if n == 7 else None)
    q = [((n - 1) % 6) * 2 + 1, ((n - 1) % 6) * 2 + 2]
    resp = {str(x): 'ABCD'[(x + n) % 4] for x in q if x != 5}
    ab = {'5': {'transcricao': 'a chuva vem das [?nuvem?] quando fica [ilegível]', 'pontos': 0.5, 'justificativa': 'Explicou a causa, sem exemplo.', 'confianca': 'media'}} if 5 in q else {}
    return {'primeira_pagina': primeira, 'nome': nome, 'questoes': q, 'respostas': resp, 'abertas': ab}

async def rota(route):
    url = route.request.url
    for k, p in LIBS.items():
        if url.endswith(k): return await route.fulfill(path=p, content_type='application/javascript')
    if '/api/ler' in url:
        body = json.loads(route.request.post_data)
        n = int(body['imagem'].split('#')[1])
        return await route.fulfill(json=resposta_falsa(n))
    if url.startswith('http://127.0.0.1'): return await route.continue_()
    return await route.abort()

async def fluxo(b, largura, capturas):
    ctx = await b.new_context(viewport={'width': largura, 'height': 844 if largura < 700 else 900}, device_scale_factor=2 if capturas else 1, accept_downloads=True)
    pg = await ctx.new_page()
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))
    await pg.route('**/*', rota)
    await pg.goto('http://127.0.0.1:8765/index.html')
    # a imagem enviada leva o número da foto, para a resposta simulada saber qual é
    await pg.evaluate("""()=>{ toB64 = async f => { const i=S.lote.findIndex(x=>x.file===f)+1 || (S.alunos.flatMap(a=>a.imgs).findIndex(x=>x.file===f)+1); return '#'+i+'#'+'x'.repeat(200); }; }""")
    async def sem_overflow(etapa):
        sw = await pg.evaluate('document.documentElement.scrollWidth'); iw = await pg.evaluate('innerWidth')
        check(sw <= iw, f'{largura}px {etapa}: sem deslizar para o lado ({sw} <= {iw})')
    async def foto(nome):
        if capturas: await pg.screenshot(path=f'{SHOTS}/{largura}_{nome}.png', full_page=False)

    # 1. Código de acesso aparece na primeira visita
    await pg.wait_for_timeout(500)
    check(await pg.is_visible('#shCodigo'), f'{largura}px pede o código na primeira visita')
    await foto('0_codigo')
    await pg.fill('#codigo', 'teste'); await pg.click('#cdSalvar'); await pg.wait_for_timeout(300)
    # 2. Gabarito
    check((await pg.text_content('#titulo')) == 'Gabarito', f'{largura}px título é a etapa (Gabarito)')
    check(await pg.is_disabled('#principal'), f'{largura}px não avança sem gabarito')
    await pg.fill('#prova', 'Matemática 5º ano')
    for _ in range(2): await pg.click('#nMais')
    for q, l in [(1,'B'),(2,'C'),(3,'D'),(4,'A'),(5,'AB'),(6,'A'),(7,'C'),(8,'B'),(9,'A'),(10,'B'),(11,'D'),(12,'A')]:
        await pg.click(f'#k{q} .chip[data-l="{l}"]')
    await pg.fill('#k5 textarea', 'Explica a causa (0,5). Dá um exemplo (0,5).')
    await sem_overflow('gabarito')
    await foto('1_gabarito')
    # P1: reduzir e voltar a aumentar o nº de questões não perde o gabarito
    await pg.fill('#nq', ''); await pg.dispatch_event('#nq', 'change'); await pg.wait_for_timeout(100)
    await pg.fill('#nq', '12'); await pg.dispatch_event('#nq', 'change'); await pg.wait_for_timeout(100)
    check(await pg.evaluate('chaves().length') == 12, f'{largura}px gabarito sobrevive a apagar o nº de questões')
    note = await pg.text_content('#barNote')
    check('12 de 12' in note, f'{largura}px contagem do gabarito ({note})')
    await pg.click('#principal'); await pg.wait_for_timeout(300)
    # 3. Fotos
    check((await pg.text_content('#titulo')) == 'Fotos', f'{largura}px avança para Fotos')
    await sem_overflow('fotos vazio'); await foto('2_fotos_vazio')
    for f in FOTOS: await pg.set_input_files('#cam', f)
    await pg.wait_for_timeout(300)
    check((await pg.text_content('#fotosTit')).startswith(str(len(FOTOS))), f'{largura}px {len(FOTOS)} fotos na fila')
    await sem_overflow('fotos'); await foto('3_fotos')
    lbl = await pg.text_content('#principal')
    check('Ler e separar 12' in lbl, f'{largura}px botão principal claro ({lbl})')
    await pg.click('#principal')
    await pg.wait_for_function("document.querySelector('#titulo').textContent==='Conferir'", timeout=20000)
    # 4. Conferir
    n = await pg.evaluate('S.alunos.length')
    check(n == 2, f'{largura}px separou 2 alunos (deu {n})')
    nomes = await pg.evaluate('S.alunos.map(a=>a.nome)')
    check(nomes == ['João Pedro', 'Guilherme Souza'], f'{largura}px nomes lidos {nomes}')
    await sem_overflow('conferir'); await foto('4_conferir')
    await pg.click('#al1 .al-hd'); await pg.wait_for_timeout(300)
    await sem_overflow('aluno aberto'); await foto('5_aluno')
    if capturas: await pg.screenshot(path=f'{SHOTS}/{largura}_5_aluno_inteiro.png', full_page=True)
    # corrigir uma letra à mão
    await pg.click('#al1 .qrow:first-child .chip:nth-of-type(2)')
    # confirmar a aberta
    await pg.click('#al1 .abq .btn.ok'); await pg.wait_for_timeout(200)
    corrigida = await pg.evaluate('S.alunos[0].resp[1]')
    check(await pg.evaluate('S.alunos[0].ab[5].revisado') is True, f'{largura}px confirmou a nota da aberta')
    # separar: foto 4 do João é de outro aluno
    await pg.click('#al1 .strip .ft:nth-child(4) .mais'); await pg.wait_for_timeout(200)
    await foto('6_menu_foto')
    await pg.click('#sfLista button:nth-child(2)'); await pg.wait_for_timeout(300)
    check(await pg.evaluate('S.alunos.length') == 3, f'{largura}px separou um aluno pela foto')
    await pg.click('.al.open .juntar'); await pg.wait_for_timeout(300)
    check(await pg.evaluate('S.alunos.length') == 2 and await pg.evaluate('S.alunos[0].imgs.length') == 6, f'{largura}px juntou de volta')
    check(await pg.evaluate('S.alunos[0].resp[1]') == corrigida and await pg.evaluate('S.alunos[0].ab[5].revisado') is True, f'{largura}px correções à mão sobrevivem a separar e juntar')
    # P1: recarregar a página não perde a correção
    await pg.wait_for_timeout(800)
    await pg.reload(); await pg.wait_for_timeout(1200)
    check(await pg.evaluate('S.alunos.length') == 2 and await pg.evaluate('S.alunos[0].nome') == 'João Pedro' and await pg.evaluate('S.alunos[0].imgs.length') == 6, f'{largura}px recarregar mantém alunos e fotos')
    check(await pg.evaluate('S.alunos[0].resp[1]') == corrigida, f'{largura}px recarregar mantém as correções')
    check((await pg.text_content('#titulo')) == 'Conferir', f'{largura}px volta à etapa Conferir')
    await pg.evaluate("""()=>{ toB64 = async f => '#1#'+'x'.repeat(200); }""")
    # Esc fecha folhas
    await pg.click('#abrirAjustes'); await pg.wait_for_timeout(200); await foto('7_ajustes')
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(200)
    check(not await pg.is_visible('#shAjustes'), f'{largura}px Esc fecha os Ajustes')
    await pg.click('#principal'); await pg.wait_for_timeout(300)
    # 5. Entregar
    check((await pg.text_content('#titulo')) == 'Entregar', f'{largura}px chega a Entregar')
    await sem_overflow('entregar'); await foto('8_entregar')
    async with pg.expect_download() as d:
        await pg.click('#guardar')
    dl = await d.value; p = await dl.path()
    z = zipfile.ZipFile(p); nomes_zip = z.namelist()
    check(any(x.startswith('João_Pedro/') for x in nomes_zip) and any(x.endswith('.xlsx') for x in nomes_zip) and any(x.endswith('.html') for x in nomes_zip), f'{largura}px ZIP com pastas, planilha e relatórios ({len(nomes_zip)} itens)')
    check(not erros, f'{largura}px sem erros de JavaScript {erros[:2]}')
    if capturas:
        html = await pg.evaluate("relatorioHTML('completo')"); rp = await ctx.new_page(); await rp.set_content(html); await rp.screenshot(path=f'{SHOTS}/{largura}_9_relatorio.png'); 
    await ctx.close()

async def main():
    servir()
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        for w in (360, 390, 768, 1360):
            await fluxo(b, w, capturas=(w in (390, 1360) or os.environ.get('UX') == '1'))
        await b.close()
    print(f'\n{len(falhas)} falha(s)')
    sys.exit(1 if falhas else 0)
asyncio.run(main())
