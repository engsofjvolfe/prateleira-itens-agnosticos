"""
Leitor de PDF. Le o arquivo pagina por pagina, palavra por palavra, cada palavra com a
posicao dela: da propria camada de texto do PDF (pdftotext -bbox-layout) ou, nas paginas
das faixas de "ocr", do que o Tesseract le na imagem da pagina (pdftoppm e a tabela de
palavras do Tesseract). As linhas saem como estao na pagina, na ordem de leitura, com as
palavras separadas por um espaco e uma linha vazia entre dois blocos de texto; a palavra
partida no fim da linha fica como esta, com o hifen, porque o programa nao sabe se o hifen
e da palavra ("situacoes-problema") ou so da quebra.

Com "destaques", o negrito e o italico vem dos trechos que o proprio PDF marca assim
(pdftohtml -xml, que diz a posicao de cada trecho e marca a fonte dele com uma etiqueta: b
para negrito, i para italico). Um trecho destacado conta para uma palavra quando cobre a
linha dela e, na largura, mais que a precisao da posicao ou a palavra inteira (a palavra
mais estreita que a precisao, como um ponto que o OCR leu como letra). A parte da palavra que e uma
palavra do texto desse trecho fica com o destaque dele, e a pontuacao das pontas que sobra
fica sem destaque (o ponto depois de um titulo em negrito). Vale a parte cuja posicao bate
com a do trecho: a ponta da palavra que sobra fica fora do trecho na pagina, e a que nao
sobra, dentro. Sem parte assim, a palavra inteira, quando o trecho a cobre inteira (a
leitura deu um texto um pouco diferente do texto do trecho, como o OCR que junta a palavra
aos pontos que vem depois dela); senao, a parte mais longa que e palavra do texto do
trecho. Quando nenhuma parte bate com o texto do trecho, a palavra inteira fica com o
destaque dos trechos em que cai o centro dela. A troca de destaque no meio de uma
palavra, fora da pontuacao das pontas, nao se ve. A linha sai como uma lista de pedacos,
cada um com os destaques dele, e o programa principal escreve as marcas. Um trecho do
pdftohtml que mistura partes com destaques diferentes e erro: a posicao de cada parte
dentro dele nao se sabe. Sem "destaques", o texto e o mesmo, sem as marcas.

Opcoes, todas obrigatorias (as padrao vem da configuracao):
  - "ocr": as faixas de paginas lidas pelo OCR (lista vazia: nenhuma);
  - "idioma_ocr", "modo_ocr" e "resolucao_ocr": o idioma (codigo do Tesseract, varios com
    "+"), o modo de segmentacao (--psm) e a resolucao da imagem, em pontos por polegada;
  - "destaques": {etiqueta do pdftohtml: destaque}, como {"b": "negrito", "i": "italico"},
    com o nome de cada destaque nas marcas de destaque do padrao da transcricao; {} para
    nenhum.

Precisa do Poppler (pdfinfo, pdftotext, pdftoppm e, com destaques, pdftohtml) e, se houver
pagina pelo OCR, do Tesseract com os dados do idioma. Com "pular_ocr" no contexto, as
paginas de OCR nao sao lidas: vem com "blocos" None.
"""

import re
import subprocess
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

from extrator_comum import paginas_das_faixas, pedacos

OPCOES = ("ocr", "idioma_ocr", "modo_ocr", "resolucao_ocr", "destaques")

TOTAL = re.compile(r"^Pages:\s+(\d+)\s*$", re.M)
FORA_DO_XML = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
PONTOS_POR_POLEGADA = 72  # a unidade de medida do PDF
ZOOM = 1  # o pdftohtml da a posicao dos trechos em pontos (zoom 1), em numeros inteiros:
PRECISAO = 1 / ZOOM  # a posicao de um trecho pode errar ate isso


def _roda(args):
    return subprocess.run([str(a) for a in args], capture_output=True, text=True, check=True).stdout


def total_de_paginas(arquivo):
    m = TOTAL.search(_roda(["pdfinfo", arquivo]))
    if not m:
        raise ValueError(f"o pdfinfo não diz quantas páginas {arquivo} tem")
    return int(m.group(1))


def _imagem(arquivo, n, opcoes, pasta):
    base = Path(pasta) / f"p{n}"
    _roda(["pdftoppm", "-q", "-f", n, "-l", n, "-r", opcoes["resolucao_ocr"], "-gray", "-png", "-singlefile",
           arquivo, base])
    return f"{base}.png"


def _sem_espaco_de_nomes(raiz):
    for el in raiz.iter():
        el.tag = el.tag.split("}")[-1]
    return raiz


def _trechos_destacados(arquivo, n, pasta, marcas):
    """[(destaques, esquerda, topo, direita, base, texto)] dos trechos que o pdftohtml marca
    com uma das etiquetas de marcas ({etiqueta: destaque}), em pontos."""
    base = Path(pasta) / f"d{n}"
    _roda(["pdftohtml", "-q", "-xml", "-i", "-zoom", ZOOM, "-f", n, "-l", n, arquivo, base])
    raiz = ET.fromstring(FORA_DO_XML.sub("", Path(f"{base}.xml").read_text(encoding="utf-8", errors="replace")))
    out = []
    for t in raiz.iter("text"):
        partes = ([(frozenset(), t.text)] if (t.text or "").strip() else []) + [
            p for el in t for p in ((frozenset(marcas[x.tag] for x in el.iter() if x.tag in marcas),
                                     "".join(el.itertext())), (frozenset(), el.tail or "")) if p[1].strip()]
        tipos = {d for d, _ in partes}
        if len(tipos) > 1:
            raise ValueError(f"página {n}: um trecho mistura partes com destaques diferentes "
                             f"({[s for _, s in partes]}): a posição de cada parte não se sabe")
        if tipos and next(iter(tipos)):
            x, y, w, h = (float(t.get(a)) for a in ("left", "top", "width", "height"))
            out.append((next(iter(tipos)), x, y, x + w, y + h, "".join(s for _, s in partes)))
    return out


def _cobre(trecho, caixa):
    """Se o trecho cobre a palavra: o centro da altura dela e, na largura, mais que a
    precisao ou a palavra inteira."""
    _, x0, y0, x1, y1, _ = trecho
    inteira = x0 <= caixa[0] and caixa[2] <= x1
    return y0 <= (caixa[1] + caixa[3]) / 2 <= y1 and (min(x1, caixa[2]) - max(x0, caixa[0]) > PRECISAO or inteira)


def _pontuacao(c):
    return unicodedata.category(c).startswith("P")


def _cabe(trecho, caixa, ini, fim, tamanho):
    """Se o corte [ini:fim] da palavra bate com a posicao do trecho: cada ponta que sobra
    fica fora do trecho, e cada ponta que nao sobra, dentro dele."""
    _, x0, _, x1, _, _ = trecho
    return (ini > 0) == (x0 - caixa[0] > PRECISAO) and (fim < tamanho) == (caixa[2] - x1 > PRECISAO)


def _partes_da_palavra(palavra, caixa, trechos):
    """[(pedaco, destaques)] da palavra, pelos trechos destacados que a cobrem: a parte que
    e uma palavra do texto de um deles, com a pontuacao das pontas que sobra sem destaque,
    e que bate com a posicao do trecho; sem ela, a palavra inteira com os trechos que a
    cobrem inteira, e, sem eles, a parte mais longa que e palavra do texto de um trecho;
    sem parte que bata com o texto, a palavra inteira, com os trechos em que cai o centro
    dela."""
    sem, cobrem = frozenset(), [t for t in trechos if _cobre(t, caixa)]
    if not cobrem:
        return [(palavra, sem)]
    ini_max = next((k for k, c in enumerate(palavra) if not _pontuacao(c)), len(palavra))
    fim_min = len(palavra) - next((k for k, c in enumerate(reversed(palavra)) if not _pontuacao(c)), len(palavra))
    cortes = sorted(((i, f) for i in range(ini_max + 1) for f in range(max(fim_min, i + 1), len(palavra) + 1)),
                    key=lambda c: (c[0] - c[1], c[0]))
    for pela_posicao in (True, False):
        inteiros = [t for t in cobrem if _cabe(t, caixa, 0, len(palavra), len(palavra))]
        if not pela_posicao and inteiros:
            return [(palavra, frozenset(d for t in inteiros for d in t[0]))]
        for ini, fim in cortes:
            donos = [t for t in cobrem if palavra[ini:fim] in t[5].split()
                     and (not pela_posicao or _cabe(t, caixa, ini, fim, len(palavra)))]
            if donos:
                partes = [(palavra[:ini], sem), (palavra[ini:fim], frozenset(d for t in donos for d in t[0])),
                          (palavra[fim:], sem)]
                return [(s, d) for s, d in partes if s]
    x = (caixa[0] + caixa[2]) / 2
    return [(palavra, frozenset(d for t in cobrem if t[1] <= x <= t[3] for d in t[0]))]


def _palavras_da_camada(arquivo, n):
    """[[ [(palavra, caixa)] por linha ] por bloco] da camada de texto, em pontos."""
    xml = _roda(["pdftotext", "-q", "-enc", "UTF-8", "-bbox-layout", "-f", n, "-l", n, arquivo, "-"])
    raiz = _sem_espaco_de_nomes(ET.fromstring(FORA_DO_XML.sub("", xml)))
    return [[[(w.text or "", tuple(float(w.get(a)) for a in ("xMin", "yMin", "xMax", "yMax"))) for w in l.iter("word")]
             for l in b.iter("line")] for b in raiz.iter("block")]


def _palavras_do_ocr(arquivo, n, opcoes, pasta):
    """O mesmo de _palavras_da_camada, do OCR: blocos pelos paragrafos do Tesseract."""
    escala = PONTOS_POR_POLEGADA / float(opcoes["resolucao_ocr"])
    linhas = _roda(["tesseract", _imagem(arquivo, n, opcoes, pasta), "stdout", "-l", opcoes["idioma_ocr"],
                    "--psm", opcoes["modo_ocr"], "tsv"]).split("\n")
    nomes = linhas[0].split("\t")
    blocos = {}
    for linha in linhas[1:]:
        campos = dict(zip(nomes, linha.split("\t")))
        if campos.get("level") != "5" or not campos.get("text", "").strip():
            continue
        x, y, w, h = (float(campos[k]) * escala for k in ("left", "top", "width", "height"))
        bloco = (int(campos["block_num"]), int(campos["par_num"]))
        blocos.setdefault(bloco, {}).setdefault(int(campos["line_num"]), []).append(
            (campos["text"], (x, y, x + w, y + h)))
    return [[ls[k] for k in sorted(ls)] for _, ls in sorted(blocos.items())]


def _pedacos(linha, trechos):
    """[(pedaco, destaques)] de uma linha de palavras: cada palavra com os destaques dela."""
    partes = []
    for palavra, caixa in linha:
        partes += [(" ", ())] + _partes_da_palavra(palavra, caixa, trechos)
    return pedacos(partes)


def _blocos(palavras, trechos):
    """Os blocos de texto da pagina: uma linha por linha de palavras e uma linha vazia entre
    dois blocos. Sem trechos destacados (trechos None), a linha e o texto das palavras; com
    eles, a lista de pedacos com os destaques."""
    out = []
    for bloco in palavras:
        if out:
            out.append(("texto", ""))
        for linha in bloco:
            out.append(("texto", " ".join(p for p, _ in linha) if trechos is None else _pedacos(linha, trechos)))
    return out


# ---------- leitura ----------

def ler(arquivo, opcoes, contexto):
    total = total_de_paginas(arquivo)
    pelo_ocr = set(paginas_das_faixas(opcoes["ocr"], total))
    paginas = []
    with tempfile.TemporaryDirectory() as pasta:
        for n in range(1, total + 1):
            ocr = n in pelo_ocr
            if ocr and contexto.get("pular_ocr"):
                paginas.append({"arquivo": n, "ocr": ocr, "blocos": None})
                continue
            palavras = _palavras_do_ocr(arquivo, n, opcoes, pasta) if ocr else _palavras_da_camada(arquivo, n)
            trechos = _trechos_destacados(arquivo, n, pasta, opcoes["destaques"]) if opcoes["destaques"] else None
            paginas.append({"arquivo": n, "ocr": ocr, "blocos": _blocos(palavras, trechos)})
    return {"paginado": True, "paginas": paginas}
