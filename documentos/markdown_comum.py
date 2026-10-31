"""
O que as pecas da prateleira fazem do mesmo jeito com um texto Markdown, lido como o GitHub
o le: as linhas fora dos blocos de codigo, o texto sem os blocos e sem o codigo na linha, a
ancora de um titulo, os titulos fora dos blocos de codigo, cada um com a linha, o nivel, o
texto e a ancora (o titulo repetido ganha -1, -2... no fim dela), e os marcadores, o id e o
name de cada tag HTML fora de codigo e de comentario.

Nao se roda: as pecas o importam da pasta irma "documentos" ou da propria pasta. So
biblioteca padrao.
"""

import collections
import re

QUEBRA = "\n"  # o que separa as linhas do texto corrido
CERCA = re.compile(r"^ {0,3}(`{3,}|~{3,})")
CODIGO_NA_LINHA = re.compile(r"(`+)(?:(?!\1).)+?\1")
TITULO = re.compile(r"^ {0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
TAG_HTML = re.compile(r"<[^>]+>")
LINK_NO_TITULO = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
COMENTARIO_HTML = re.compile(r"<!--.*?-->", re.DOTALL)
# um atributo de uma tag HTML como o CommonMark o le: o nome e o valor, sem aspas, entre simples ou entre duplas
ATRIBUTO_HTML = re.compile(r"""\s+([A-Za-z_:][A-Za-z0-9_.:-]*)(?:\s*=\s*(?:([^\s"'=<>`]+)|'([^']*)'|"([^"]*)"))?""")
TAG_DE_ABERTURA = re.compile(rf"<[A-Za-z][A-Za-z0-9-]*(?:{ATRIBUTO_HTML.pattern})*\s*/?>")
ATRIBUTOS_DE_MARCADOR = ("id", "name")  # os atributos de uma tag HTML que um link alcanca pela ancora

Titulo = collections.namedtuple("Titulo", "linha nivel texto ancora")


def linhas_fora_de_codigo(texto):
    """(numero, linha) de cada linha fora de bloco de codigo."""
    cerca = None
    for n, linha in enumerate(texto.splitlines(), 1):
        m = CERCA.match(linha)
        if cerca:
            if m and m.group(1)[0] == cerca[0] and len(m.group(1)) >= len(cerca) \
                    and not linha.strip()[len(m.group(1)):].strip():
                cerca = None
            continue
        if m:
            cerca = m.group(1)
            continue
        yield n, linha


def texto_fora_de_codigo(texto):
    """O texto com as linhas dos blocos de codigo vazias e sem o codigo na linha; cada linha
    fica no numero dela."""
    linhas = texto.splitlines()
    fora = dict(linhas_fora_de_codigo(texto))
    return QUEBRA.join(CODIGO_NA_LINHA.sub("", fora.get(n, "")) for n in range(1, len(linhas) + 1))


def ancora(titulo):
    """A ancora que o GitHub da a um titulo: o texto como aparece, em minusculas, sem
    pontuacao, com hifen no lugar de cada espaco."""
    texto = LINK_NO_TITULO.sub(r"\1", titulo)
    texto = TAG_HTML.sub("", texto)
    texto = texto.replace("`", "").lower()
    return re.sub(r"[^\w\- ]", "", texto).replace(" ", "-")


def titulos(texto):
    """[Titulo] de cada titulo fora de bloco de codigo, na ordem: o numero da linha, o nivel
    (quantos #), o texto, sem os # e os espacos das pontas, e a ancora que o GitHub da a ele;
    o titulo repetido ganha -1, -2... no fim da ancora."""
    saida, vistas = [], {}
    for n, linha in linhas_fora_de_codigo(texto):
        m = TITULO.match(linha)
        if not m:
            continue
        base = ancora(m.group(2))
        k = vistas.get(base, 0)
        vistas[base] = k + 1
        saida.append(Titulo(n, len(m.group(1)), m.group(2), base if k == 0 else f"{base}-{k}"))
    return saida


def marcadores(texto):
    """O valor do id e do name de cada tag HTML fora de codigo e de comentario."""
    sem_comentario = COMENTARIO_HTML.sub("", texto_fora_de_codigo(texto))
    return {"".join(valor) for tag in TAG_DE_ABERTURA.finditer(sem_comentario)
            for nome, *valor in ATRIBUTO_HTML.findall(tag.group()) if nome.lower() in ATRIBUTOS_DE_MARCADOR}
