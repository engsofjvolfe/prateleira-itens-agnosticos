"""Testes do extrator (extrator.py e os leitores).

Os documentos sao inventados aqui: PDFs montados pelo proprio teste, um HTML em ISO-8859-1,
um XML com etiquetas de outros nomes e um JSON com partes. O texto deles e sorteado entre
todos os caracteres que um texto pode ter, com uma semente fixa (o sorteio e o mesmo em
toda rodada), mais linhas que comecam e terminam com cada caractere que os padroes tratam
de um jeito proprio e com o hifen. Tres padroes de transcricao, com marcas que nao sao as
de nenhum projeto, passam pelos mesmos testes: nada do padrao fica no codigo.

Os testes conferem regras que valem para qualquer texto, nunca uma frase pronta:
  - lida de volta pela definicao do padrao (a funcao le, aqui), cada linha escrita tem o
    texto do documento, com os espacos juntados; texto_simples le o mesmo texto;
  - nenhum caractere que se escapa fica sem escape, e cada marca fecha na mesma linha,
    colada ao texto destacado;
  - cada caractere sai com o destaque que tem no documento, e o espaco, so com o destaque
    que os dois vizinhos tem;
  - os titulos seguem o modelo, e o numero impresso, lido de volta, e o da numeracao;
  - as trocas e as correcoes dao o que a regra delas diz e sao contadas no resumo;
  - todo erro para tudo, sem gravar nada, e a mensagem diz o dado que o causou;
  - duas rodadas dao a mesma saida;
  - no extrator_comum, campo da o valor no caminho com o tipo pedido e da erro, dizendo o
    caminho, quando ele falta ou e de outro tipo; expressao compila o campo ou da erro.
Precisa do Poppler e do Tesseract com o idioma "eng". Uso:
    python3 -I teste_extrator.py <pasta do extrator> <pasta de trabalho nova>
"""
import html
import json
import random
import re
import string
import subprocess
import sys
import unicodedata
from pathlib import Path

PECA, TRABALHO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
FALHAS = []
sys.path.insert(0, str(PECA))
sys.path.insert(1, str(Path(__file__).resolve().parent))
import extrator  # noqa: E402
import extrator_comum  # noqa: E402
import leitor_pdf  # noqa: E402
from pdf_inventado import FONTES, pagina_de_linhas, pdf_inventado  # noqa: E402  -- nesta pasta

SORTEIO = random.Random(1)
ALFABETO = string.ascii_letters + string.digits + string.punctuation + "áâãçéêíóôõúüÁÉÇÕºª§°"
PONTUACAO = [c for c in ALFABETO if unicodedata.category(c).startswith("P")]


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


# ---------- padroes e leitores inventados ----------

PADRAO_A = {"titulo_pagina": "=== {rotulo} / folha {arquivo} ===", "rotulo_numerada": "pg {numero}",
            "rotulo_sem_numero": "pg ?", "rotulo_sem_paginas": "inteiro", "sem_texto": "(vazio)", "escape": "~",
            "escapar": ["*", "~", "<", ">", "(", ")", "{", "}", "[", "]"], "escapar_no_comeco": ["="],
            "destaques": {"forte": {"abre": "<<", "fecha": ">>"}, "inclinado": {"abre": "((", "fecha": "))"},
                          "cortado": {"abre": "{{", "fecha": "}}"}},
            "tabela": {"inicio": "[", "meio": "][", "fim": "]", "separador": "--"}}
PADRAO_B = dict(PADRAO_A, titulo_pagina="### {rotulo} <{arquivo}>", rotulo_numerada="n.{numero}",
                sem_texto="--nada--", escapar_no_comeco=["#"])
PADRAO_C = {"titulo_pagina": "@ {arquivo}: {rotulo}", "rotulo_numerada": "{numero}", "rotulo_sem_numero": "?",
            "rotulo_sem_paginas": "unico", "sem_texto": "(nada)", "escape": "!", "escapar": ["!", "+", "%", "|"],
            "escapar_no_comeco": ["@"],
            "destaques": {"forte": {"abre": "++", "fecha": "++"}, "inclinado": {"abre": "+", "fecha": "+"},
                          "cortado": {"abre": "%%", "fecha": "%%"}},
            "tabela": {"inicio": "| ", "meio": " | ", "fim": " |", "separador": "-"}}
PADROES = {"A": PADRAO_A, "B": PADRAO_B, "C": PADRAO_C}

DESTAQUES_HTML = {"S": "cortado", "b": "forte", "em": "inclinado"}  # uma etiqueta em maiusculas na opcao
DESTAQUES_XML = {"enfase": "inclinado"}
DESTAQUES_PDF = {"b": "forte", "i": "inclinado"}  # as etiquetas do pdftohtml
LEITORES = {
    "pdf": {"extensoes": [".pdf"], "opcoes": {"ocr": [], "idioma_ocr": "eng", "modo_ocr": "3", "resolucao_ocr": 300,
                                              "destaques": {}}},
    "marcacao": {"extensoes": [".HTML"], "opcoes": {
        "codificacao": "declarada", "blocos": ["p", "h1", "li", "caption"], "quebras": ["br"],
        "vazios": ["br", "meta", "img", "link", "hr", "input"], "ignorar": ["head", "script", "style"],
        "conteudo": None, "tabela": {"tabela": "table", "linha": "tr", "celulas": ["td", "th"]},
        "destaques": DESTAQUES_HTML}},
    "xml_inventado": {"modulo": "marcacao", "extensoes": [".xml"], "opcoes": {
        "codificacao": "declarada", "blocos": ["titulo-artigo", "par", "legenda"], "quebras": ["quebra"],
        "vazios": ["quebra"], "ignorar": ["nota-oculta"], "conteudo": None,
        "tabela": {"tabela": "tab", "linha": "lin", "celulas": ["cel"]}, "destaques": DESTAQUES_XML}},
    "json": {"extensoes": [".json"], "opcoes": {"codificacao": "utf-8", "lista": [], "antes": [], "campos": [],
                                                "leitor_do_texto": "marcacao"}},
}
NOMES_HTML = {"blocos": ["h1", "p"], "quebra": "<br>", "ignorada": "script", "legenda": "caption", "tabela": "table",
              "linha": "tr", "celulas": ["th", "td"], "destaques": DESTAQUES_HTML}
NOMES_XML = {"blocos": ["titulo-artigo", "par"], "quebra": "<quebra/>", "ignorada": "nota-oculta",
             "legenda": "legenda", "tabela": "tab", "linha": "lin", "celulas": ["cel"], "destaques": DESTAQUES_XML}


def caracteres(valor):
    """Os caracteres que nao sao letra, numero nem espaco de todos os textos de um valor."""
    if isinstance(valor, dict):
        return set().union(set(), *(caracteres(v) for v in valor.values()))
    if isinstance(valor, list):
        return set().union(set(), *(caracteres(v) for v in valor))
    return {c for c in str(valor) if not c.isalnum() and not c.isspace()}


ESPECIAIS = sorted(set().union(*(caracteres(p) for p in PADROES.values())) | {"-"})


# ---------- texto sorteado ----------

def palavra(alfabeto=ALFABETO):
    return "".join(SORTEIO.choice(alfabeto) for _ in range(SORTEIO.randint(1, 6)))


def frase(alfabeto=ALFABETO):
    return " ".join(palavra(alfabeto) for _ in range(SORTEIO.randint(1, 6)))


def sem_destaque(texto):
    return [(c, ()) for c in texto]


def trecho(destaques, alfabeto=ALFABETO, pontas=True):
    """(marcacao, letras) de um texto sorteado: palavras com espacos variados (ou coladas),
    umas dentro de etiquetas de destaque ou de uma neutra, aninhadas em ordem sorteada;
    letras e [(caractere, destaques)]. Sem pontas, o texto nao comeca nem termina com
    espaco."""
    marcacao, letras = [], []
    nomes, quantas = sorted(destaques) + ["span"], SORTEIO.randint(1, 6)
    for k in range(quantas):
        if k:
            sep = SORTEIO.choice([" ", "  ", "\n", "\t ", ""])
            marcacao.append(sep)
            letras += sem_destaque(sep)
        abertas = SORTEIO.sample(nomes, SORTEIO.randint(0, min(2, len(nomes))))
        texto = (SORTEIO.choice(["", " "]) if pontas or k > 0 else "") + palavra(alfabeto) \
            + (SORTEIO.choice(["", " "]) if pontas or k < quantas - 1 else "")
        d = sorted({destaques[t] for t in abertas if t in destaques})
        marcacao.append("".join(f"<{t.lower()}>" for t in abertas) + html.escape(texto)
                        + "".join(f"</{t.lower()}>" for t in reversed(abertas)))
        letras += [(c, d) for c in texto]
    return "".join(marcacao), letras


def marcacao_inventada(nomes, alfabeto=ALFABETO):
    """(marcacao do conteudo, esperado) de um conteudo sorteado com as etiquetas dadas:
    blocos, um com quebra, um vazio e um com um trecho ignorado no meio, uma tabela com
    legenda, uma linha com uma celula com um bloco dentro, uma com uma quebra dentro e uma
    vazia, linhas mais curtas e uma linha vazia. esperado e a lista do que deve sair, em
    ordem: ("texto", letras) ou ("tabela", [[letras de cada celula]], largura)."""
    destaques, partes, esperado = nomes["destaques"], [], []
    for tag in nomes["blocos"]:
        m, l = trecho(destaques, alfabeto)
        partes.append(f"<{tag}>{m}</{tag}>")
        esperado.append(("texto", l))
    bloco = nomes["blocos"][-1]
    (m1, l1), (m2, l2) = trecho(destaques, alfabeto), trecho(destaques, alfabeto)
    partes.append(f"<{bloco}>{m1}{nomes['quebra']}{m2}</{bloco}>")
    esperado += [("texto", l1), ("texto", l2)]
    partes.append(f"<{bloco}> \n\t </{bloco}>")
    (m1, l1), (m2, l2) = trecho(destaques, alfabeto), trecho(destaques, alfabeto)
    partes.append(f"<{bloco}>{m1}<{nomes['ignorada']}>{html.escape(frase())}</{nomes['ignorada']}>{m2}</{bloco}>")
    esperado.append(("texto", l1 + l2))
    m, l = trecho(destaques, alfabeto)
    tabela = [f"<{nomes['tabela']}><{nomes['legenda']}>{m}</{nomes['legenda']}>"]
    esperado.append(("texto", l))
    largura, linhas = SORTEIO.randint(3, 4), []

    def celula(jeito):
        """(marcacao, letras) de uma celula: comum, com um bloco ou uma quebra entre dois
        textos sem espaco nas pontas (o bloco e a quebra viram o espaco), ou vazia."""
        if jeito == "vazia":
            return "", []
        if jeito == "comum":
            return trecho(destaques, alfabeto)
        (m1, a), (m2, b) = trecho(destaques, alfabeto, False), trecho(destaques, alfabeto, False)
        meio = f"<{bloco}>{m2}</{bloco}>" if jeito == "bloco" else f"{nomes['quebra']}{m2}"
        return m1 + meio, a + sem_destaque(" ") + b
    for r in range(SORTEIO.randint(3, 5)):
        tag = nomes["celulas"][0] if r == 0 else nomes["celulas"][-1]
        jeitos = (["comum"] * largura if r == 0 else ["bloco", "quebra", "vazia"] if r == 1
                  else ["comum"] * SORTEIO.randint(1, largura))
        celulas, linha = [], [f"<{nomes['linha']}>"]
        for jeito in jeitos:
            m1, l1 = celula(jeito)
            linha.append(f"<{tag}>{m1}</{tag}>")
            celulas.append(l1)
        tabela.append("".join(linha) + f"</{nomes['linha']}>")
        linhas.append(celulas + [[]] * (largura - len(celulas)))
    tabela.append(f"<{nomes['linha']}></{nomes['linha']}></{nomes['tabela']}>")
    partes.append("".join(tabela))
    esperado.append(("tabela", linhas, largura))
    m, l = trecho(destaques, alfabeto)
    partes.append(f"<{bloco}>{m}</{bloco}>")
    esperado.append(("texto", l))
    return "".join(partes), esperado


# ---------- a leitura de volta, pela definicao do padrao ----------

def le(linha, padrao, comeco=True):
    """([(caractere, destaques)], [problemas]) de uma linha escrita no padrao: o escape
    seguido de um caractere que se escapa e esse caractere; uma marca de destaque abre o
    destaque que esta fechado e fecha o que esta aberto (a mais longa primeiro). Problemas:
    caractere que se escapa sem escape, linha que comeca sem escape com um caractere do
    comeco (com comeco), marca que abre ou fecha encostada num espaco ou na ponta, marca
    sem fechar no fim."""
    esc, escapar = padrao["escape"], set(padrao["escapar"])
    marcas = sorted(((d[lado], nome, lado) for nome, d in padrao["destaques"].items() for lado in ("abre", "fecha")),
                    key=lambda t: -len(t[0]))
    letras, problemas, ativos, i = [], [], set(), 0
    if comeco and linha[:1] in padrao["escapar_no_comeco"]:
        problemas.append(f"começa com {linha[0]!r} sem escape")
    if comeco and any(linha.startswith(esc + c) for c in padrao["escapar_no_comeco"]):
        letras.append((linha[1], frozenset()))
        i = 2
    while i < len(linha):
        if linha[i] == esc and linha[i + 1:i + 2] and linha[i + 1] in escapar:
            letras.append((linha[i + 1], frozenset(ativos)))
            i += 2
            continue
        marca = next((t for t in marcas if linha.startswith(t[0], i) and (t[2] == "fecha") == (t[1] in ativos)), None)
        if marca is not None:
            m, nome, lado = marca
            vizinho = linha[i + len(m):i + len(m) + 1] if lado == "abre" else linha[i - 1:i]
            if not vizinho.strip():
                problemas.append(f"{m!r} na posição {i} {lado} encostada num espaço ou na ponta")
            (ativos.add if lado == "abre" else ativos.discard)(nome)
            i += len(m)
            continue
        if linha[i] in escapar:
            problemas.append(f"{linha[i]!r} sem escape na posição {i}")
        letras.append((linha[i], frozenset(ativos)))
        i += 1
    if ativos:
        problemas.append(f"marca(s) sem fechar: {sorted(ativos)}")
    return letras, problemas


def confere_linha(linha, esperado, padrao, onde, comeco=True):
    """Confere uma linha (ou celula) escrita contra as letras [(caractere, destaques)] do
    documento."""
    letras, problemas = le(linha, padrao, comeco)
    texto = "".join(c for c, _ in letras)
    confere(not problemas, f"{onde}: escapes e marcas certos: {problemas} em {linha!r}")
    if not confere(texto == " ".join("".join(c for c, _ in esperado).split()),
                   f"{onde}: o texto é o do documento: {linha!r}, esperado {''.join(c for c, _ in esperado)!r}"):
        return
    confere([x for x in letras if not x[0].isspace()]
            == [(c, frozenset(d)) for c, d in esperado if not c.isspace()],
            f"{onde}: cada caractere com o destaque que tem no documento: {linha!r}")
    confere(all(d == letras[k - 1][1] & letras[k + 1][1] for k, (c, d) in enumerate(letras) if c.isspace()),
            f"{onde}: o espaço leva só o destaque dos dois vizinhos: {linha!r}")
    confere(extrator_comum.texto_simples(linha, padrao) == texto, f"{onde}: texto_simples lê o mesmo texto: {linha!r}")


def celulas(linha, padrao):
    t = padrao["tabela"]
    if not (linha.startswith(t["inicio"]) and linha.endswith(t["fim"])):
        return None
    return linha[len(t["inicio"]):len(linha) - len(t["fim"])].split(t["meio"])


def confere_conteudo(linhas, esperado, padrao, onde):
    """Confere as linhas nao vazias de uma pagina contra o esperado de marcacao_inventada."""
    i = 0
    for k, item in enumerate(esperado):
        if item[0] == "texto":
            if confere(i < len(linhas), f"{onde}: falta a linha do bloco {k}"):
                confere_linha(linhas[i], item[1], padrao, f"{onde}, bloco {k}")
            i += 1
            continue
        _, tab, largura = item
        separador = celulas(linhas[i + 1], padrao) if i + 1 < len(linhas) else None
        confere(separador == [padrao["tabela"]["separador"]] * largura,
                f"{onde}: a segunda linha da tabela é a de separação, com uma marca por coluna: {separador}")
        for r, (linha, celulas_esperadas) in enumerate(zip(linhas[i:i + 1] + linhas[i + 2:], tab)):
            achadas = celulas(linha, padrao)
            if confere(achadas is not None and len(achadas) == largura,
                       f"{onde}: a linha {r} da tabela tem a forma e as {largura} células: {linha!r}"):
                for c, (cel, esp) in enumerate(zip(achadas, celulas_esperadas)):
                    confere_linha(cel, esp, padrao, f"{onde}, tabela, linha {r}, célula {c}", comeco=False)
        i += len(tab) + 1
    confere(i == len(linhas), f"{onde}: nenhuma linha a mais: {linhas[i:]}")


# ---------- documentos inventados ----------

def em_paginas(linhas, por_pagina):
    return [linhas[k:k + por_pagina] for k in range(0, len(linhas), por_pagina)]


# o PDF principal: paginas de linhas sorteadas, uma pagina vazia e uma pagina para o OCR
LINHAS_PDF = ([frase() for _ in range(30)] + ESPECIAIS + [a + b + frase() for a in ESPECIAIS for b in ESPECIAIS]
              + [frase() + c for c in ESPECIAIS])
PAGINAS_PDF = em_paginas(LINHAS_PDF, 40)
VISIVEIS, ESCONDIDA = ["LARANJA", "JANELA"], "ESCONDIDO"
PDF = pdf_inventado([pagina_de_linhas(p, 11, 17) for p in PAGINAS_PDF]
                    + [[], [(48, 72, 600, " ".join(VISIVEIS), False), (12, 72, 300, ESCONDIDA, True)]])
TOTAL_PDF = len(PAGINAS_PDF) + 2


def palavra_destacada():
    """[(fonte, pedaco)] de uma palavra sorteada numa fonte sorteada; a destacada pode ter
    pontuacao sem destaque numa ponta ou nas duas. O miolo tem um caractere que nao e
    pontuacao: o destaque vale para a palavra, e so a pontuacao da ponta fica fora dele."""
    fonte = SORTEIO.choice(["F1", "F2", "F3", "F5"])
    miolo = palavra()
    while all(c in PONTUACAO for c in miolo):
        miolo = palavra()
    antes = SORTEIO.choice(PONTUACAO) if FONTES[fonte][1] and SORTEIO.random() < 0.3 else ""
    depois = SORTEIO.choice(PONTUACAO) if FONTES[fonte][1] and SORTEIO.random() < 0.3 else ""
    return [p for p in (("F1", antes), (fonte, miolo), ("F1", depois)) if p[1]]


def linha_destacada():
    pedacos = []
    for k in range(SORTEIO.randint(1, 5)):
        pedacos += ([("F1", " ")] if k else []) + palavra_destacada()
    return pedacos


def letras_do_pdf(pedacos):
    return [(c, FONTES[f][1]) for f, s in pedacos for c in s]


def linha_repetida():
    """[(fonte, pedaco)] de uma palavra destacada que aparece duas vezes no mesmo trecho (o
    espaco entre elas e da mesma fonte): uma vez com uma pontuacao na ponta, destacada, e
    outra com a mesma pontuacao fora do destaque. So a posicao do trecho diz qual e qual."""
    fonte, ponta = SORTEIO.choice(["F2", "F3", "F5"]), SORTEIO.choice(PONTUACAO)
    miolo = palavra()
    while all(c in PONTUACAO for c in miolo):
        miolo = palavra()
    if SORTEIO.random() < 0.5:
        return [(fonte, miolo + ponta), (fonte, " "), (fonte, miolo), ("F1", ponta)]
    return [("F1", ponta), (fonte, miolo), (fonte, " "), (fonte, ponta + miolo)]


LINHAS_DESTACADAS = [linha_destacada() for _ in range(30)] + [linha_repetida() for _ in range(8)]
PDF_DESTAQUES = pdf_inventado([pagina_de_linhas(p, 12, 18) for p in em_paginas(LINHAS_DESTACADAS, 35)])
LINHA_DO_OCR = [("F1", "Autor. "), ("F2", "TITULO FORTE"), ("F1", ". meio "), ("F3", "termo inclinado"),
                ("F1", ", fim "), ("F2", "ROTULO:"), ("F1", " valor")]
PDF_DESTAQUES_OCR = pdf_inventado([[(18, 40, 600, LINHA_DO_OCR, False)]])
PDF_MISTO = pdf_inventado([[(28, 40, 600, [("F1", "Comum "), ("F4", "FORTE"), ("F1", " comum")], False)]])

CONTEUDO_HTML, ESPERADO_HTML = marcacao_inventada(NOMES_HTML)
TITULO_HTML, MENU_HTML, RODAPE_HTML = (trecho(DESTAQUES_HTML) for _ in range(3))
HTML = (f'<html><head><meta charset="iso-8859-1"><title>{TITULO_HTML[0]}</title><style>.x {{ color: red }}</style>'
        f'<script>var nada = "{html.escape(frase())}";</script></head><body><nav><p>{MENU_HTML[0]}</p></nav>'
        f'<main class="conteudo principal">{CONTEUDO_HTML}</main><footer><p>{RODAPE_HTML[0]}</p></footer></body>'
        f'</html>').encode("iso-8859-1")

CONTEUDO_XML, ESPERADO_XML = marcacao_inventada(NOMES_XML)
XML = f'<?xml version="1.0" encoding="UTF-8"?>\n<doc>{CONTEUDO_XML}</doc>\n'.encode("utf-8")

NOME_JSON = palavra()
PARTES_JSON = [trecho(DESTAQUES_HTML) for _ in range(4)]
JSON_OK = {"nome": html.escape(NOME_JSON), "resposta": {"partes": [
    {"html": f"<p>{PARTES_JSON[0][0]}</p><p>{PARTES_JSON[1][0]}</p>"}, {"puro": PARTES_JSON[2][0]},
    {"html": PARTES_JSON[3][0], "puro": html.escape(frase())}]}}
ESPERADO_JSON = [sem_destaque(NOME_JSON)] + [l for _, l in PARTES_JSON]
JSON_RUIM = {"nome": "x", "resposta": {"partes": [{"html": "<p>x</p>"}, {"outro": "y"}]}}

# trocas: o texto tem os caracteres que se trocam, e uma troca leva a outro que se troca
TROCAS_GERAIS = {"¤": "o", "¶": "µ", "¢¢": "c", "¢": "C"}
TROCAS_DO_DOC = {"µ": "u"}
ALFABETO_TROCAS = ALFABETO + "¤¶µ¢" * 5
CONTEUDO_TROCAS, ESPERADO_TROCAS = marcacao_inventada(dict(NOMES_HTML, destaques={}), ALFABETO_TROCAS)
HTML_TROCAS = (f'<html><head><meta charset="iso-8859-1"></head><body><p>µ</p>{CONTEUDO_TROCAS}</body>'
               f'</html>').encode("iso-8859-1")


def trocado(texto, trocas):
    """(texto, quantas trocas) pela regra das trocas: da esquerda para a direita, a chave
    mais longa que comeca ali, uma passada so."""
    chaves, out, n, i = sorted(trocas, key=len, reverse=True), [], 0, 0
    while i < len(texto):
        k = next((k for k in chaves if texto.startswith(k, i)), None)
        out.append(trocas[k] if k else texto[i])
        i, n = i + (len(k) if k else 1), n + bool(k)
    return "".join(out), n


def com_as_trocas(esperado, trocas):
    """O esperado de marcacao_inventada (sem destaques) com as trocas feitas, e quantas."""
    total = 0

    def troca(letras):
        nonlocal total
        texto, n = trocado(" ".join("".join(c for c, _ in letras).split()), trocas)
        total += n
        return sem_destaque(texto)
    out = [(i[0], troca(i[1])) if i[0] == "texto" else (i[0], [[troca(c) for c in l] for l in i[1]], i[2])
           for i in esperado]
    return out, total


def grava(pasta, nome, conteudo):
    caminho = pasta / nome
    caminho.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(conteudo, bytes):
        caminho.write_bytes(conteudo)
    else:
        caminho.write_text(json.dumps(conteudo, ensure_ascii=False), encoding="utf-8")
    return caminho


FONTES_DOS_TESTES = {"manual.pdf": PDF, "destaques.pdf": PDF_DESTAQUES, "destaques-ocr.pdf": PDF_DESTAQUES_OCR,
                     "misto.pdf": PDF_MISTO, "pagina.html": HTML, "artigo.xml": XML, "ato.json": JSON_OK,
                     "ato-ruim.json": JSON_RUIM, "trocas.html": HTML_TROCAS}


def pasta_com_fontes(nome):
    pasta = TRABALHO / nome
    for arquivo, conteudo in FONTES_DOS_TESTES.items():
        grava(pasta, f"fontes/{arquivo}", conteudo)
    return pasta


def roda(pasta, documentos, padrao=PADRAO_A, leitores=LEITORES, extra=(), trocas=None):
    dados = {"versao_schema": 1, "padrao": padrao, "leitores": leitores}
    if trocas is not None:
        dados["trocas"] = trocas
    config = grava(pasta, "config.json", dados)
    docs = grava(pasta, "docs.json", {"versao_schema": 1, "documentos": documentos})
    r = subprocess.run([sys.executable, "-I", str(PECA / "extrator.py"), str(config), str(docs), "--raiz", str(pasta),
                        *extra], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def lida(pasta, saida, cod):
    return (pasta / saida).read_text(encoding="utf-8") if cod == 0 else ""


def paginas(texto, padrao):
    """[(titulo casado com o modelo, [linhas nao vazias do corpo])] da transcricao."""
    titulo, out = extrator_comum.como_padrao(padrao["titulo_pagina"]), []
    for linha in texto.split("\n"):
        m = titulo.match(linha)
        if m:
            out.append((m, []))
        elif out and linha:
            out[-1][1].append(linha)
    return out


def resumo(out, oque):
    """O numero que o resumo da para oque ("sem texto", "pelo OCR", "troca", "correç")."""
    m = re.search(rf"(\d+) {oque}", out)
    return int(m.group(1)) if m else None


ROMANO = re.compile(r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$")  # a forma de um numero romano


def de_romano(s):
    valores = [{"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}[c] for c in s.upper()]
    return sum(-v if k + 1 < len(valores) and v < valores[k + 1] else v for k, v in enumerate(valores))


def numero_certo(s, estilo, n):
    """Se s e o numero n escrito no estilo: arabico sem zero na frente, ou romano na forma
    certa e na caixa do estilo."""
    if estilo == "arabico":
        return s.isdigit() and not s.startswith("0") and int(s) == n
    caixa = str.lower if estilo == "romano_minusculo" else str.upper
    return s == caixa(s) and ROMANO.match(s.upper()) is not None and de_romano(s) == n


def confere_rotulos(pags, numeracao, padrao, total, onde):
    """Uma pagina por pagina do arquivo, em ordem, e o rotulo de cada uma pela numeracao."""
    confere([int(m.group("arquivo")) for m, _ in pags] == list(range(1, total + 1)),
            f"{onde}: um título por página do arquivo, em ordem: {[m.group(0) for m, _ in pags]}")
    numero = extrator_comum.como_padrao(padrao["rotulo_numerada"])
    for m, _ in pags:
        n, rotulo = int(m.group("arquivo")), m.group("rotulo")
        faixa = next((f for f in numeracao if f["de"] <= n <= f["ate"]), None)
        if faixa is None:
            confere(rotulo == padrao["rotulo_sem_numero"], f"{onde}: página {n} fora da numeração: {rotulo!r}")
            continue
        esperado, achado = faixa["primeiro"] + n - faixa["de"], numero.match(rotulo)
        if not confere(achado is not None, f"{onde}: página {n}: o rótulo segue o modelo: {rotulo!r}"):
            continue
        s = achado.group("numero")
        confere(numero_certo(s, faixa["estilo"], esperado),
                f"{onde}: página {n}: o número {s!r}, lido de volta, é {esperado} ({faixa['estilo']})")


DOC_PDF = {"arquivo": "fontes/manual.pdf", "saida": "saida/manual.md",
           "opcoes": {"ocr": [{"de": TOTAL_PDF, "ate": TOTAL_PDF}]}}
DOC_HTML = {"arquivo": "fontes/pagina.html", "saida": "saida/pagina.md",
            "opcoes": {"conteudo": {"etiqueta": "main", "atributo": "class", "valor": "principal"}}}
DOC_XML = {"arquivo": "fontes/artigo.xml", "saida": "saida/artigo.md"}
DOC_JSON = {"arquivo": "fontes/ato.json", "saida": "saida/ato.md",
            "opcoes": {"lista": ["resposta", "partes"], "antes": [["nome"]], "campos": ["html", "puro"]}}


def numeracao(estilo):
    return [{"de": 2, "ate": TOTAL_PDF - 2, "estilo": estilo, "primeiro": SORTEIO.randint(1, 3000)},
            {"de": TOTAL_PDF - 1, "ate": TOTAL_PDF, "estilo": "arabico", "primeiro": SORTEIO.randint(1, 9999)}]


# ---------- os estilos de numeracao, em todo numero que o romano escreve ----------
ESTILOS = ("arabico", "romano_minusculo", "romano_maiusculo")
for estilo in ESTILOS:
    errados = [n for n in range(1, 4000) if not numero_certo(extrator.ESTILOS[estilo](n), estilo, n)]
    confere(not errados, f"{estilo}: o número escrito, lido de volta, é o número: erra em {errados[:5]}")

# ---------- a regra da palavra destacada no PDF, com caixas e trechos sorteados, sem PDF ----------
CAIXA, FORTE, INCLINADO = (0, 0, 100, 10), frozenset({"forte"}), frozenset({"inclinado"})


def partes(palavra_, trechos):
    return [(s, frozenset(d)) for s, d in leitor_pdf._partes_da_palavra(palavra_, CAIXA, trechos)]


for _ in range(40):
    # sem corte que bata com a posicao do trecho (ele comeca depois da palavra e nao ha
    # pontuacao no comeco dela), vale a parte mais longa que e palavra do texto do trecho
    miolo = palavra(string.ascii_letters)
    ponta = "".join(SORTEIO.choice(PONTUACAO) for _ in range(SORTEIO.randint(1, 2)))
    cortes = [miolo + ponta[:j] for j in range(len(ponta) + 1)]
    no_trecho = SORTEIO.sample(cortes, SORTEIO.randint(1, len(cortes))) + [frase(string.ascii_letters)]
    SORTEIO.shuffle(no_trecho)
    maior = max((c for c in no_trecho if c in cortes), key=len)
    achado = partes(miolo + ponta, [(FORTE, 30, 0, 60, 10, " ".join(no_trecho))])
    confere(achado == [p for p in ((maior, FORTE), ((miolo + ponta)[len(maior):], frozenset())) if p[0]],
            f"PDF, sem posição que bata: a parte mais longa que é palavra do trecho: {miolo + ponta!r}, "
            f"{no_trecho}: {achado}")
    # sem parte que bata com o texto, a palavra inteira, com o trecho em que cai o centro dela
    outra = palavra(string.digits)
    achado = partes(miolo, [(INCLINADO, 0, 0, 30, 10, outra), (FORTE, 40, 0, 60, 10, outra)])
    confere(achado == [(miolo, FORTE)], f"PDF, sem parte que bata com o texto: a palavra inteira, com o trecho do "
                                        f"centro: {achado}")
    # sem parte que bata com a posicao, o trecho que cobre a palavra inteira da o destaque a
    # ela inteira, mesmo com o texto um pouco diferente (a palavra junto da pontuacao)
    achado = partes(miolo + ponta, [(FORTE, -5, 0, 105, 10, f"{miolo} {ponta * 3} {frase(string.digits)}")])
    confere(achado == [(miolo + ponta, FORTE)], f"PDF: o trecho que cobre a palavra inteira dá o destaque a ela "
                                               f"inteira: {miolo + ponta!r}: {achado}")
    # a palavra mais estreita que a precisao, inteira dentro do trecho, fica com o destaque dele
    estreita = (50, 0, 50 + leitor_pdf.PRECISAO / 2, 10)
    achado = [(s, frozenset(d)) for s, d in leitor_pdf._partes_da_palavra(
        miolo, estreita, [(FORTE, 0, 0, 100, 10, frase(string.digits))])]
    confere(achado == [(miolo, FORTE)], f"PDF: a palavra estreita dentro do trecho fica com o destaque: {achado}")
    # o trecho que cobre a palavra so ate a precisao da posicao nao conta
    achado = partes(miolo, [(FORTE, 100 - leitor_pdf.PRECISAO / 2, 0, 200, 10, miolo)])
    confere(achado == [(miolo, frozenset())], f"PDF: o trecho que só encosta na palavra não conta: {achado}")


# ---------- os mesmos testes em cada padrao ----------
for (nome, padrao), estilo in zip(PADROES.items(), ESTILOS[::-1]):
    num = numeracao(estilo)
    # PDF
    p = pasta_com_fontes(f"pdf-{nome}")
    cod, out = roda(p, [dict(DOC_PDF, numeracao=num)], padrao=padrao)
    confere(cod == 0, f"PDF ({nome}): o extrator falhou: {out}")
    pags = paginas(lida(p, "saida/manual.md", cod), padrao)
    confere_rotulos(pags, num, padrao, TOTAL_PDF if cod == 0 else 0, f"PDF ({nome})")
    for k, (_, linhas) in enumerate(pags[:len(PAGINAS_PDF)]):
        esperadas = PAGINAS_PDF[k]
        if confere(len(linhas) == len(esperadas), f"PDF ({nome}), página {k + 1}: uma linha por linha da página: "
                                                  f"{len(linhas)} != {len(esperadas)}"):
            for linha, original in zip(linhas, esperadas):
                confere_linha(linha, sem_destaque(original), padrao, f"PDF ({nome}), página {k + 1}")
    if len(pags) == TOTAL_PDF:
        confere(pags[-2][1] == [padrao["sem_texto"]], f"PDF ({nome}): página sem texto leva a marca")
        ocr = " ".join(pags[-1][1]).upper()
        confere(all(v in ocr for v in VISIVEIS), f"PDF ({nome}): a página pelo OCR traz o que a imagem mostra: {ocr!r}")
        confere(ESCONDIDA not in ocr, f"PDF ({nome}): a página pelo OCR não usa a camada de texto")
    confere(resumo(out, "sem texto") == 1 and resumo(out, "pelo OCR") == 1,
            f"PDF ({nome}): o resumo conta OCR e páginas sem texto: {out}")

    # destaques do PDF, pela camada de texto, com e sem a opcao
    q = pasta_com_fontes(f"destaques-{nome}")
    docs = [{"arquivo": "fontes/destaques.pdf", "saida": f"saida/{d}.md",
             "opcoes": {"destaques": DESTAQUES_PDF if d else {}}} for d in (True, False)]
    cod, out = roda(q, docs, padrao=padrao)
    confere(cod == 0, f"destaques ({nome}): o extrator falhou: {out}")
    for d in (True, False):
        linhas = [l for _, ls in paginas(lida(q, f"saida/{d}.md", cod), padrao) for l in ls]
        if confere(len(linhas) == len(LINHAS_DESTACADAS), f"destaques ({nome}, {d}): uma linha por linha"):
            for linha, pedacos in zip(linhas, LINHAS_DESTACADAS):
                letras = letras_do_pdf(pedacos) if d else sem_destaque("".join(s for _, s in pedacos))
                confere_linha(linha, letras, padrao, f"destaques ({nome}, opção {d})")

    # destaques do PDF, pelo OCR
    q = pasta_com_fontes(f"destaques-ocr-{nome}")
    cod, out = roda(q, [{"arquivo": "fontes/destaques-ocr.pdf", "saida": "saida/d.md",
                         "opcoes": {"destaques": DESTAQUES_PDF, "ocr": [{"de": 1, "ate": 1}]}}], padrao=padrao)
    confere(cod == 0, f"destaques pelo OCR ({nome}): o extrator falhou: {out}")
    linhas = [l for _, ls in paginas(lida(q, "saida/d.md", cod), padrao) for l in ls]
    if confere(len(linhas) == 1, f"destaques pelo OCR ({nome}): uma linha: {linhas}"):
        confere_linha(linhas[0], letras_do_pdf(LINHA_DO_OCR), padrao, f"destaques pelo OCR ({nome})")

    # HTML, XML e JSON
    h = pasta_com_fontes(f"marcacao-{nome}")
    cod, out = roda(h, [DOC_HTML, DOC_XML, DOC_JSON], padrao=padrao)
    confere(cod == 0, f"marcação ({nome}): o extrator falhou: {out}")
    for saida, esperado in (("pagina", ESPERADO_HTML), ("artigo", ESPERADO_XML)):
        pags = paginas(lida(h, f"saida/{saida}.md", cod), padrao)
        if confere(len(pags) == 1, f"{saida} ({nome}): o documento sem páginas sai numa página só"):
            confere(pags[0][0].group("rotulo") == padrao["rotulo_sem_paginas"],
                    f"{saida} ({nome}): com o rótulo de sem páginas")
            confere_conteudo(pags[0][1], esperado, padrao, f"{saida} ({nome})")
    pags = paginas(lida(h, "saida/ato.md", cod), padrao)
    if confere(len(pags) == 1, f"JSON ({nome}): uma página só"):
        confere_conteudo(pags[0][1], [("texto", l) for l in ESPERADO_JSON], padrao, f"JSON ({nome})")

    # trocas
    t = pasta_com_fontes(f"trocas-{nome}")
    doc = {"arquivo": "fontes/trocas.html", "saida": "saida/t.md", "trocas": TROCAS_DO_DOC}
    cod, out = roda(t, [doc], padrao=padrao, trocas=TROCAS_GERAIS)
    confere(cod == 0, f"trocas ({nome}): o extrator falhou: {out}")
    esperado, total = com_as_trocas([("texto", sem_destaque("µ"))] + ESPERADO_TROCAS, {**TROCAS_GERAIS,
                                                                                       **TROCAS_DO_DOC})
    pags = paginas(lida(t, "saida/t.md", cod), padrao)
    if confere(len(pags) == 1, f"trocas ({nome}): uma página só"):
        confere_conteudo(pags[0][1], esperado, padrao, f"trocas ({nome})")
    confere(resumo(out, "troca") == total, f"trocas ({nome}): o resumo conta {total} trocas: {out}")

# ---------- sem refazer o OCR: as outras paginas, como na transcricao ----------
CONFIG = {"versao_schema": 1, "padrao": PADRAO_A, "leitores": LEITORES}
q = pasta_com_fontes("pular-ocr")
DOC_NUM = dict(DOC_PDF, numeracao=numeracao("arabico"))
inteiras, _ = extrator.paginas_escritas(extrator.le_documento(DOC_NUM, CONFIG, q), DOC_NUM, CONFIG)
puladas, _ = extrator.paginas_escritas(extrator.le_documento(DOC_NUM, CONFIG, q, pular_ocr=True), DOC_NUM, CONFIG)
confere([(n, t) for n, t, _ in puladas] == [(n, t) for n, t, _ in inteiras]
        and [c for n, _, c in puladas if n != TOTAL_PDF] == [c for n, _, c in inteiras if n != TOTAL_PDF]
        and [c for n, _, c in puladas if n == TOTAL_PDF] == [None] and None not in [c for _, _, c in inteiras],
        "sem refazer o OCR, a página de OCR vem sem texto e as outras como na extração inteira")

# ---------- duas rodadas: a mesma saida ----------
saidas = []
for k in (1, 2):
    d = pasta_com_fontes(f"de-novo-{k}")
    roda(d, [DOC_PDF, DOC_HTML, DOC_XML, DOC_JSON, {"arquivo": "fontes/destaques.pdf", "saida": "saida/d.md",
                                                    "opcoes": {"destaques": DESTAQUES_PDF}}])
    saidas.append({n: (d / f"saida/{n}.md").read_bytes() if (d / f"saida/{n}.md").exists() else None
                   for n in ("manual", "pagina", "artigo", "ato", "d")})
confere(None not in saidas[0].values() and saidas[0] == saidas[1], "duas rodadas dão a mesma saída")

# ---------- o que nao conta ----------
q = pasta_com_fontes("pdf-sem-ocr")
cod, out = roda(q, [dict(DOC_PDF, opcoes={})])
confere(cod == 0 and ESCONDIDA in lida(q, "saida/manual.md", cod), "PDF: sem OCR, a página vem da camada de texto")
s = pasta_com_fontes("html-todo")
cod, out = roda(s, [dict(DOC_HTML, opcoes={})])
confere(cod == 0, f"HTML inteiro: o extrator falhou: {out}")
todo = [l for _, ls in paginas(lida(s, "saida/pagina.md", cod), PADRAO_A) for l in ls]
confere_conteudo(todo, [("texto", MENU_HTML[1])] + ESPERADO_HTML + [("texto", RODAPE_HTML[1])], PADRAO_A,
                 "HTML sem 'conteudo': o documento inteiro conta, sem as etiquetas ignoradas")

# ---------- erros: param tudo, sem gravar nada, e dizem o dado que os causou ----------


def erro(pasta, documentos, dado, descricao, **kw):
    cod, out = roda(pasta, documentos, **kw)
    confere(cod == 1 and out.startswith("ERRO") and dado in out and not (pasta / "saida").exists(),
            f"{descricao} é erro, sem gravar nada, e a mensagem diz {dado!r}: {out}")


def caso(nome):
    return pasta_com_fontes(f"erro-{nome}")


erro(caso("misto"), [{"arquivo": "fontes/misto.pdf", "saida": "saida/m.md", "opcoes": {"destaques": DESTAQUES_PDF}}],
     "FORTE", "trecho do PDF que mistura destaques")
erro(caso("json"), [DOC_HTML, dict(DOC_JSON, arquivo="fontes/ato-ruim.json")], "outro",
     "parte do JSON sem campo de texto (com erro num documento, nenhum é gravado)")
erro(caso("alvo"), [dict(DOC_HTML, opcoes={"conteudo": {"etiqueta": "article"}})], "article",
     "parte pedida em 'conteudo' que não existe")
grava(TRABALHO / "erro-extensao", "fontes/coisa.xyz", b"qualquer")
erro(TRABALHO / "erro-extensao", [{"arquivo": "fontes/coisa.xyz", "saida": "saida/coisa.md"}], ".xyz",
     "extensão sem leitor")
erro(caso("leitor"), [dict(DOC_PDF, leitor="../fora")], "../fora", "leitor que a configuração não tem")
erro(caso("modulo"), [DOC_XML], "../fora", "módulo de leitor com nome fora da forma",
     leitores=dict(LEITORES, xml_inventado=dict(LEITORES["xml_inventado"], modulo="../fora")))
erro(caso("faixa"), [dict(DOC_PDF, numeracao=[{"de": 3, "ate": TOTAL_PDF + 5, "estilo": "arabico", "primeiro": 1}])],
     str(TOTAL_PDF + 5), "numeração fora das páginas")
erro(caso("duas-faixas"), [dict(DOC_PDF, numeracao=[{"de": 1, "ate": 2, "estilo": "arabico", "primeiro": 1},
                                                    {"de": 2, "ate": 3, "estilo": "arabico", "primeiro": 5}])],
     "[2]", "página em duas faixas")
erro(caso("estilo"), [dict(DOC_PDF, numeracao=[{"de": 1, "ate": 1, "estilo": "grego", "primeiro": 1}])], "grego",
     "estilo de numeração desconhecido")
erro(caso("sem-paginas"), [dict(DOC_HTML, numeracao=[{"de": 1, "ate": 1, "estilo": "arabico", "primeiro": 1}])],
     "pagina.html", "documento sem páginas com numeração")
erro(caso("campo"), [DOC_PDF], "desconhecido", "modelo com campo que não existe",
     padrao=dict(PADRAO_A, titulo_pagina="{rotulo} {desconhecido} {arquivo}"))
erro(caso("sem-marca"), [DOC_HTML], "cortado", "destaque do leitor que o padrão não tem",
     padrao=dict(PADRAO_A, destaques={k: v for k, v in PADRAO_A["destaques"].items() if k != "cortado"}))
erro(caso("campo-no-documento"), [dict(DOC_PDF, correcao=[])], "correcao", "campo do documento que o molde não conhece")
erro(caso("campo-no-padrao"), [DOC_PDF], "troca", "campo do padrão que o molde não conhece",
     padrao=dict(PADRAO_A, troca={}))
erro(caso("opcao-desconhecida"), [dict(DOC_PDF, opcoes={"destaque": DESTAQUES_PDF})], "destaque",
     "opção que o leitor não conhece")
erro(caso("opcao-que-falta"), [dict(DOC_PDF, opcoes={})], "idioma_ocr",
     "opção padrão que falta na configuração, mesmo sem página que a use",
     leitores=dict(LEITORES, pdf=dict(LEITORES["pdf"], opcoes={k: v for k, v in LEITORES["pdf"]["opcoes"].items()
                                                              if k != "idioma_ocr"})))
erro(caso("etiqueta-dupla"), [DOC_HTML], "'b'", "etiqueta com dois destaques na opção",
     leitores=dict(LEITORES, marcacao=dict(LEITORES["marcacao"], opcoes=dict(
         LEITORES["marcacao"]["opcoes"], destaques={"B": "forte", "b": "inclinado"}))))

# o padrao em que marca e texto se confundiriam
ruins = {
    "marca-sem-escape": (dict(PADRAO_A, escapar=[c for c in PADRAO_A["escapar"] if c != "<"]), "'<'"),
    "escape-sem-escape": (dict(PADRAO_A, escapar=[c for c in PADRAO_A["escapar"] if c != "~"]), "'~'"),
    "item-longo": (dict(PADRAO_A, escapar=PADRAO_A["escapar"] + ["ab"]), "'ab'"),
    "escape-na-marca": (dict(PADRAO_A, escapar=PADRAO_A["escapar"] + ["|"],
                             destaques=dict(PADRAO_A["destaques"], cortado={"abre": "~|", "fecha": "|~"})), "'~'"),
    "marca-de-dois": (dict(PADRAO_A, destaques=dict(PADRAO_A["destaques"], cortado=PADRAO_A["destaques"]["forte"])),
                      "'<<'"),
    "celula-sem-escape": (dict(PADRAO_A, tabela=dict(PADRAO_A["tabela"], meio="|")), "'|'"),
}
for nome, (padrao, dado) in ruins.items():
    erro(caso(nome), [DOC_HTML], dado, f"padrão com {nome}", padrao=padrao)

# a linha que se confundiria com uma marca do padrao
LINHA_TITULO = "folha {arquivo}: {rotulo}".format(arquivo=1, rotulo=palavra(string.ascii_letters))
grava(TRABALHO / "erro-titulo", "fontes/t.html", f'<html><meta charset="utf-8"><p>{LINHA_TITULO}</p></html>'.encode())
erro(TRABALHO / "erro-titulo", [{"arquivo": "fontes/t.html", "saida": "saida/t.md"}], LINHA_TITULO,
     "linha do texto que se lê como título de página", padrao=dict(PADRAO_A, titulo_pagina="folha {arquivo}: {rotulo}"))
grava(TRABALHO / "erro-sem-texto", "fontes/v.html",
      f'<html><meta charset="utf-8"><p>{PADRAO_B["sem_texto"]}</p></html>'.encode())
erro(TRABALHO / "erro-sem-texto", [{"arquivo": "fontes/v.html", "saida": "saida/v.md"}], "página 1",
     "página cujo texto é a marca de página sem texto", padrao=PADRAO_B)

# trocas que nao valem
DOC_TROCAS = {"arquivo": "fontes/trocas.html", "saida": "saida/t.md"}
erro(caso("troca-nos-dois"), [dict(DOC_TROCAS, trocas={"¤": "o"})], "¤", "a mesma troca na configuração e no documento",
     trocas={"¤": "o"})
erro(caso("troca-sem-uso"), [dict(DOC_TROCAS, trocas={"æ": "ae"})], "æ", "troca do documento que não acha nada")
erro(caso("troca-vazia"), [dict(DOC_TROCAS, trocas={"": "x"})], "vazio", "troca de um texto vazio")
q = caso("troca-geral-sem-uso")
cod, out = roda(q, [DOC_TROCAS], trocas={"æ": "ae"})
confere(cod == 0, f"troca da configuração que não acha nada num documento não é erro: {out}")

# ---------- correcoes ----------
c = pasta_com_fontes("correcoes")
cod, out = roda(c, [DOC_PDF])
base = paginas(lida(c, "saida/manual.md", cod), PADRAO_A)
if confere(cod == 0 and len(base) == TOTAL_PDF, f"correções: o extrator falhou: {out}"):
    TUDO = lida(c, "saida/manual.md", cod)
    CORR = [{"pagina": n, "de": next(l for l in base[n - 1][1] if TUDO.count(l) == 1),
             "para": palavra(string.ascii_letters)} for n in (1, 2)]
    cod, out = roda(c, [dict(DOC_PDF, correcoes=CORR)], extra=["--substituir"])
    corrigida = lida(c, "saida/manual.md", cod)
    esperado = []
    for n, (_, ls) in enumerate(base, start=1):
        texto = "\n".join(ls)
        for x in CORR:
            texto = texto.replace(x["de"], x["para"]) if x["pagina"] == n else texto
        esperado.append(texto.split("\n"))
    confere(cod == 0 and [ls for _, ls in paginas(corrigida, PADRAO_A)] == esperado,
            "a correção troca o texto na página dela, e só lá")
    confere(resumo(out, "correç") == len(CORR), f"o resumo conta as correções: {out}")
    for corr, dado, descricao in (
            ({"pagina": 1, "de": CORR[0]["de"] + "æ", "para": "x"}, "0 vez", "correção cujo texto não aparece"),
            ({"pagina": 2, "de": CORR[0]["de"], "para": "x"}, "página 2", "correção numa página onde o texto não está"),
            ({"pagina": TOTAL_PDF + 4, "de": "a", "para": "b"}, str(TOTAL_PDF + 4), "correção para página que não há"),
            ({"pagina": 1, "de": CORR[0]["de"], "para": "b", "vezes": 99}, "99", "correção com outro número de vezes")):
        cod, out = roda(c, [dict(DOC_PDF, correcoes=[corr])], extra=["--substituir"])
        confere(cod == 1 and dado in out and lida(c, "saida/manual.md", 0) == corrigida,
                f"{descricao} é erro, sem gravar nada, e a mensagem diz {dado!r}: {out}")
    cod, out = roda(c, [dict(DOC_PDF, correcoes=CORR)], extra=["--substituir"])
    confere(cod == 0 and lida(c, "saida/manual.md", cod) == corrigida,
            "extrair de novo aplica as mesmas correções e dá o mesmo texto")

# ---------- gravar por cima ----------
g = pasta_com_fontes("por-cima")
nova = pasta_com_fontes("por-cima-nova")
roda(nova, [DOC_PDF])
cabeca = f"---\n{frase()}\n---\n\n".encode("utf-8")
velha = PADRAO_A["titulo_pagina"].format(rotulo=palavra(string.ascii_letters), arquivo=1) + f"\n\n{frase()}\n"
existente = grava(g, "saida/manual.md", cabeca + velha.encode("utf-8"))
antes = existente.read_bytes()
cod, out = roda(g, [DOC_PDF])
confere(cod == 1 and existente.read_bytes() == antes, "transcrição que existe não é gravada por cima sem pedir")
cod, out = roda(g, [DOC_PDF], extra=["--substituir"])
confere(cod == 0 and existente.read_bytes() == cabeca + (nova / "saida/manual.md").read_bytes(),
        "com --substituir, o que vem antes do primeiro título fica e o resto é o que sai numa transcrição nova")
grava(g, "saida/sem-titulo.md", frase().encode("utf-8"))
cod, out = roda(g, [dict(DOC_HTML, saida="saida/sem-titulo.md")], extra=["--substituir"])
confere(cod == 1, "transcrição sem título de página não é gravada por cima")
cod, out = roda(g, [DOC_PDF, DOC_HTML], extra=["--substituir", "--so", "fontes/pagina.html"])
confere(cod == 0 and "pagina.md" in out and "manual.md" not in out, "--so escolhe o documento")
cod, out = roda(g, [DOC_PDF], extra=["--so", "fontes/nao-esta.pdf"])
confere(cod == 1 and "nao-esta.pdf" in out, "--so com documento fora da lista é erro")


# ---------- campo e expressao, que as pecas usam para ler os proprios dados ----------
def da_erro(funcao, *args):
    """A mensagem do ErroDeDados que a chamada levanta; None quando nao levanta."""
    try:
        funcao(*args)
    except extrator_comum.ErroDeDados as e:
        return str(e)
    return None


CAMPO_NOMES = []
while len(CAMPO_NOMES) < 7:
    nome_ = palavra(string.ascii_lowercase) + palavra(string.ascii_lowercase)
    if nome_ not in CAMPO_NOMES:
        CAMPO_NOMES.append(nome_)
C_FORA, C_DENTRO, C_TEXTO, C_NUMERO, C_SIM, C_LISTA, C_RUIM = CAMPO_NOMES
C_VALOR, C_GRUPO = frase(), palavra(string.ascii_lowercase)
C_DADOS = {C_FORA: {C_DENTRO: {C_TEXTO: C_VALOR, C_NUMERO: SORTEIO.randint(-9, 9), C_SIM: True, C_LISTA: [C_VALOR]}},
           C_TEXTO: f"(?P<{C_GRUPO}>{re.escape(C_VALOR)})", C_RUIM: f"(?P<{C_GRUPO}"}
C_BASE = f"{C_FORA}/{C_DENTRO}"
confere(extrator_comum.campo(C_DADOS, f"{C_BASE}/{C_TEXTO}", str) == C_VALOR, "campo dá o valor no caminho")
confere(extrator_comum.campo(C_DADOS, f"{C_BASE}/{C_LISTA}", (list, str)) == [C_VALOR],
        "campo aceita uma tupla de tipos")
confere(type(extrator_comum.campo(C_DADOS, f"{C_BASE}/{C_NUMERO}", int)) is int, "campo dá o número")
confere(extrator_comum.campo(C_DADOS, f"{C_BASE}/{C_SIM}", bool) is True, "o booleano vale quando o tipo pedido é bool")
for caminho_, tipo_, descricao_ in ((f"{C_BASE}/{C_RUIM}", str, "campo que falta"),
                                    (f"{C_BASE}/{C_TEXTO}/{C_RUIM}", str, "caminho que passa por um texto"),
                                    (f"{C_BASE}/{C_NUMERO}", str, "campo de outro tipo"),
                                    (f"{C_BASE}/{C_SIM}", int, "booleano no lugar de número")):
    msg_ = da_erro(extrator_comum.campo, C_DADOS, caminho_, tipo_)
    confere(msg_ is not None and caminho_ in msg_, f"{descricao_} é erro, e a mensagem diz o caminho: {msg_}")
confere(extrator_comum.expressao(C_DADOS, C_TEXTO).search(f"{frase()} {C_VALOR}").group(C_GRUPO) == C_VALOR,
        "expressao compila o texto do campo")
for caminho_, descricao_ in ((C_RUIM, "expressão que não compila"),
                             (f"{C_BASE}/{C_NUMERO}", "expressão que não é texto")):
    msg_ = da_erro(extrator_comum.expressao, C_DADOS, caminho_)
    confere(msg_ is not None and caminho_ in msg_, f"{descricao_} é erro, e a mensagem diz o caminho: {msg_}")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
