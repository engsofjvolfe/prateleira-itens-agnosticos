"""
Leitor de marcacao: HTML, XHTML e XML. Capta o texto do documento, bloco por bloco: cada
bloco vira uma linha, com os espacos juntados, na ordem do documento. Um documento de
marcacao nao tem paginas: sai uma pagina so.

O que e bloco, o que nao entra e a parte do documento que conta vem das opcoes, todas
obrigatorias (as padrao vem da configuracao):
  - "codificacao": a do arquivo ("utf-8", "iso-8859-1"...) ou "declarada", que usa a que
    o proprio documento declara (charset= ou encoding=); sem declaracao, e erro;
  - "blocos": as etiquetas que abrem e fecham um bloco (p, h1, li...);
  - "quebras": as etiquetas vazias que fecham o bloco (br);
  - "vazios": as etiquetas que nunca tem fim (br, img, meta...);
  - "ignorar": as etiquetas cujo conteudo nao entra (script, style...);
  - "conteudo": null, para o documento inteiro, ou {"etiqueta", "atributo", "valor"}: so
    conta o que esta dentro do primeiro elemento com essa etiqueta (e, se dado, com o valor
    entre os valores do atributo, como uma das classes); se ele nao existe, e erro;
  - "tabela": {"tabela", "linha", "celulas"}: as etiquetas da tabela, da linha e das
    celulas. A tabela sai como bloco de tabela, uma lista de linhas de celulas; o texto da
    tabela fora das celulas (a legenda) sai como bloco de texto antes dela;
  - "destaques": {etiqueta: destaque}: o texto dentro dessas etiquetas sai com o destaque
    (o nome dele nas marcas de destaque do padrao da transcricao), como o texto riscado
    (strike) de uma lei; {} para nenhum. A linha com destaque sai como uma lista de
    pedacos, cada um com os destaques dele, e o programa principal escreve as marcas.

As etiquetas valem sem diferenca de maiusculas. Uma etiqueta de fim sem inicio e ignorada;
uma de fim que fecha outra deixada aberta fecha as duas, como no HTML.
"""

import re
from html.parser import HTMLParser
from pathlib import Path

from extrator_comum import pedacos
from texto_comum import espacos_juntos

OPCOES = ("codificacao", "blocos", "quebras", "vazios", "ignorar", "conteudo", "tabela", "destaques")

DECLARACAO = re.compile(rb"""(?:charset|encoding)\s*=\s*["']?([A-Za-z0-9._:-]+)""", re.I)


def decodifica(dados, codificacao):
    if codificacao == "declarada":
        m = DECLARACAO.search(dados)
        if not m:
            raise ValueError("o documento não declara a codificação: ela tem de vir em \"codificacao\"")
        codificacao = m.group(1).decode("ascii")
    return dados.decode(codificacao)


def _junta(partes):
    """O texto das partes (texto, destaques), com os espacos juntados: a linha escrita,
    quando nada tem destaque, ou a lista de pedacos."""
    if not any(d for _, d in partes):
        return espacos_juntos("".join(s for s, _ in partes))
    return pedacos(partes)


class _Blocos(HTMLParser):
    def __init__(self, opcoes):
        super().__init__(convert_charrefs=True)
        self.op = opcoes
        self.blocos, self.atual, self.pilha = [], [], []
        self.alvo, self.inicio, self.achou = opcoes["conteudo"], None, False
        self.linhas, self.celula = None, None  # a tabela aberta e a celula aberta

    # ---- o que conta ----
    def _captando(self):
        dentro = self.alvo is None or self.inicio is not None
        return dentro and not any(t in self.op["ignorar"] for t in self.pilha)

    def _e_o_alvo(self, tag, attrs):
        if self.achou or self.alvo is None or tag != self.alvo["etiqueta"].lower():
            return False
        atributo = self.alvo.get("atributo")
        if atributo is None:
            return True
        valores = (dict(attrs).get(atributo.lower()) or "").split()
        return self.alvo["valor"] in valores

    def _destaques(self):
        return frozenset(self.op["destaques"][t] for t in self.pilha if t in self.op["destaques"])

    # ---- blocos ----
    def _fecha_bloco(self):
        texto = _junta(self.atual)
        if texto:
            self.blocos.append(("texto", texto))
        self.atual = []

    def _fecha_tabela(self):
        self._fecha_bloco()
        linhas = [l for l in self.linhas if l]
        if linhas:
            self.blocos.append(("tabela", linhas))
        self.linhas, self.celula = None, None

    def _fecha_celula(self):
        if self.celula is not None:
            if not self.linhas:
                self.linhas.append([])
            self.linhas[-1].append(_junta(self.celula))
            self.celula = None

    def _marca(self, tag, abrindo):
        """O efeito de uma etiqueta de inicio ou de fim no texto captado."""
        t = self.op["tabela"]
        if tag == t["tabela"].lower():
            if abrindo and self.linhas is None:
                self._fecha_bloco()
                self.linhas = []
            elif not abrindo and self.linhas is not None:
                self._fecha_celula()
                self._fecha_tabela()
        elif self.linhas is not None and tag == t["linha"].lower():
            self._fecha_celula()
            if abrindo:
                self.linhas.append([])
        elif self.linhas is not None and tag in [c.lower() for c in t["celulas"]]:
            self._fecha_celula()
            if abrindo:
                self.celula = []
        elif tag in self.op["blocos"]:
            if self.celula is not None:
                self.celula.append((" ", frozenset()))
            elif self.linhas is None:
                self._fecha_bloco()

    # ---- o leitor de HTML ----
    def handle_starttag(self, tag, attrs):
        if tag in self.op["vazios"]:
            self.handle_startendtag(tag, attrs)
            return
        if self._captando():
            self._marca(tag, True)
        self.pilha.append(tag)
        if self._e_o_alvo(tag, attrs):
            self.inicio, self.achou = len(self.pilha) - 1, True

    def handle_startendtag(self, tag, attrs):
        if self._captando() and tag in self.op["quebras"]:
            if self.celula is not None:
                self.celula.append((" ", frozenset()))
            else:
                self._fecha_bloco()

    def handle_endtag(self, tag):
        if tag not in self.pilha:
            return
        while self.pilha:
            aberta = self.pilha[-1]
            if self._captando():
                self._marca(aberta, False)
            self.pilha.pop()
            if self.inicio is not None and len(self.pilha) <= self.inicio:
                self.inicio = None
            if aberta == tag:
                break

    def handle_data(self, data):
        if self._captando():
            (self.celula if self.celula is not None else self.atual).append((data, self._destaques()))

    def close(self):
        super().close()
        if self.linhas is not None:
            self._fecha_celula()
            self._fecha_tabela()
        self._fecha_bloco()
        if self.alvo is not None and not self.achou:
            raise ValueError(f"a parte pedida em \"conteudo\" não existe no documento: {self.alvo}")


def _minusculas(opcoes):
    out = dict(opcoes)
    for chave in ("blocos", "quebras", "vazios", "ignorar"):
        out[chave] = {t.lower() for t in opcoes[chave]}
    out["destaques"] = {}
    for etiqueta, destaque in sorted(opcoes["destaques"].items()):
        if out["destaques"].setdefault(etiqueta.lower(), destaque) != destaque:
            raise ValueError(f"a etiqueta {etiqueta.lower()!r} aparece em \"destaques\" com dois destaques")
    return out


def blocos_do_texto(texto, opcoes):
    """Os blocos de um texto de marcacao, pelas opcoes deste leitor."""
    leitor = _Blocos(_minusculas(opcoes))
    leitor.feed(texto)
    leitor.close()
    return leitor.blocos


def ler(arquivo, opcoes, contexto):
    texto = decodifica(Path(arquivo).read_bytes(), opcoes["codificacao"])
    return {"paginado": False, "paginas": [{"arquivo": 1, "ocr": False, "blocos": blocos_do_texto(texto, opcoes)}]}
