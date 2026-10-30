"""
O que o extrator, os leitores dele e as pecas que leem as transcricoes dele fazem do
mesmo jeito, num lugar so: ler um arquivo de dados JSON, achar nele o campo que o molde
nao conhece, pegar um campo dos dados com o tipo pedido, compilar a expressao regular de
um campo, ler a configuracao do extrator contra o molde dela, conferir o padrao,
preencher um modelo do padrao, reconhecer o titulo de pagina que o modelo faz, dividir uma transcricao
em paginas, juntar os pedacos de uma linha com destaques, tirar de uma linha as marcas de
destaque e os escapes e expandir faixas de paginas.
"""

import json
import re
from pathlib import Path

CAMPO = re.compile(r"\{(\w+)\}")
MOLDES = Path(__file__).resolve().parent / "esquemas"  # o molde de cada entrada do extrator, com o nome dela


class ErroDeDados(Exception):
    """O que impede o trabalho; a mensagem diz o que e onde."""


def le_json(caminho):
    try:
        return json.loads(Path(caminho).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ErroDeDados(f"{caminho}: não se lê como JSON em UTF-8 ({e})")


def campos_desconhecidos(dados, molde, raiz=None, onde=""):
    """[caminho de cada campo dos dados que o molde nao conhece]: em todo objeto em que o
    molde diz os campos ("properties") e nao aceita outros ("additionalProperties": false).
    Segue o "$ref" dentro do proprio molde, o "items" das listas e o "additionalProperties"
    que e um molde."""
    raiz = molde if raiz is None else raiz
    while "$ref" in molde:
        alvo = raiz
        for parte in molde["$ref"][2:].split("/"):
            alvo = alvo[parte]
        molde = alvo
    out = []
    if isinstance(dados, dict):
        campos, outros = molde.get("properties", {}), molde.get("additionalProperties", True)
        for chave, valor in dados.items():
            if chave in campos:
                out += campos_desconhecidos(valor, campos[chave], raiz, f"{onde}/{chave}")
            elif outros is False:
                out.append(f"{onde}/{chave}")
            elif isinstance(outros, dict):
                out += campos_desconhecidos(valor, outros, raiz, f"{onde}/{chave}")
    elif isinstance(dados, list) and isinstance(molde.get("items"), dict):
        for k, valor in enumerate(dados):
            out += campos_desconhecidos(valor, molde["items"], raiz, f"{onde}/{k}")
    return out


def le_conferido(caminho, molde):
    """Os dados de um arquivo JSON, com erro quando ele tem campo que o molde (o arquivo do
    JSON Schema) nao conhece -- um nome escrito errado nao passa em silencio."""
    dados = le_json(caminho)
    desconhecidos = campos_desconhecidos(dados, le_json(molde))
    if desconhecidos:
        raise ErroDeDados(f"{caminho}: campo(s) que o molde {Path(molde).name} não conhece: {desconhecidos}")
    return dados


def campo(dados, caminho, tipo):
    """O valor no caminho ("a/b") dos dados, do tipo pedido (um tipo ou uma tupla deles):
    erro claro quando falta ou e de outro tipo, e nao um KeyError no meio do trabalho. Um
    booleano so vale quando o tipo pedido e bool (no Python, ele tambem e um int)."""
    valor = dados
    for parte in caminho.split("/"):
        if not isinstance(valor, dict) or parte not in valor:
            raise ErroDeDados(f"falta o campo {caminho}")
        valor = valor[parte]
    tipos = tipo if isinstance(tipo, tuple) else (tipo,)
    if not isinstance(valor, tipos) or (isinstance(valor, bool) and bool not in tipos):
        raise ErroDeDados(f"o campo {caminho} não é do tipo {' ou '.join(t.__name__ for t in tipos)}")
    return valor


def expressao(dados, caminho):
    """A expressao regular do campo de texto, compilada; erro claro quando nao compila."""
    texto = campo(dados, caminho, str)
    try:
        return re.compile(texto)
    except re.error as e:
        raise ErroDeDados(f"o campo {caminho} não compila como expressão regular: {e}")


def le_configuracao(caminho):
    """A configuracao do extrator, conferida contra o molde dela, para o extrator e para toda
    peca que a usa."""
    return le_conferido(caminho, MOLDES / "extrator.schema.json")


def confere_padrao(padrao):
    """Erro quando uma marca do padrao pode se confundir com o texto. O escape e cada item
    de "escapar" sao um caractere so; o proprio escape esta entre os que se escapam (assim
    uma barra do texto nao vira escape), e cada caractere das marcas de destaque tambem
    (assim um asterisco do texto nao vira marca); o escape nao esta nas marcas de destaque
    (senao o escape seguido do caractere da marca seria as duas coisas); cada marca de
    destaque e de um destaque so; e a marca entre duas celulas de tabela tem um caractere
    que se escapa (assim o texto de uma celula nao a divide em duas)."""
    escape, escapar = padrao["escape"], padrao["escapar"]
    if len(escape) != 1 or any(len(c) != 1 for c in escapar):
        raise ErroDeDados(f"o escape e cada item de \"escapar\" têm de ser um caractere só: {escape!r}, {escapar}")
    nas_marcas = {c for d in padrao.get("destaques", {}).values() for m in (d["abre"], d["fecha"]) for c in m}
    faltam = sorted((nas_marcas | {escape}) - set(escapar))
    if faltam:
        raise ErroDeDados(f"caractere(s) que o padrão não escapa e que, no texto, se confundiriam com um escape "
                          f"ou uma marca de destaque: {faltam}; eles têm de estar em \"escapar\"")
    if escape in nas_marcas:
        raise ErroDeDados(f"o escape {escape!r} está numa marca de destaque")
    donos = {}
    for nome, d in padrao.get("destaques", {}).items():
        for m in {d["abre"], d["fecha"]}:
            donos.setdefault(m, []).append(nome)
    repetidas = {m: n for m, n in donos.items() if len(n) > 1}
    if repetidas:
        raise ErroDeDados(f"marca de destaque usada por mais de um destaque: {repetidas}")
    meio = padrao["tabela"]["meio"]
    if not set(meio) & set(escapar):
        raise ErroDeDados(f"a marca entre células {meio!r} não tem nenhum caractere que o padrão escapa: o texto de "
                          f"uma célula a repetiria; um deles tem de estar em \"escapar\"")


def preenche(modelo, **valores):
    """O modelo com cada {campo} trocado pelo valor; campo sem valor e erro."""
    def troca(m):
        if m.group(1) not in valores:
            raise ErroDeDados(f"o modelo {modelo!r} tem o campo {{{m.group(1)}}}, que não existe aqui")
        return str(valores[m.group(1)])
    return CAMPO.sub(troca, modelo)


def como_padrao(modelo):
    """A expressao que reconhece uma linha feita pelo modelo do titulo de pagina: o grupo
    "rotulo" e o grupo "arquivo" (a posicao da pagina no arquivo)."""
    partes = CAMPO.split(modelo)
    rx = "".join(re.escape(p) if i % 2 == 0 else
                 (r"(?P<arquivo>\d+)" if p == "arquivo" else f"(?P<{p}>.+?)")
                 for i, p in enumerate(partes))
    return re.compile(f"^{rx}\\s*$")


def paginas_da_transcricao(texto, modelo):
    """[(rotulo, posicao no arquivo, [(numero da linha, linha)])] de uma transcricao, pelo
    modelo do titulo de pagina; as linhas sao numeradas a partir de 1, como num editor.
    O que vem antes do primeiro titulo nao e de pagina nenhuma."""
    titulo, paginas = como_padrao(modelo), []
    for n, linha in enumerate(texto.split("\n"), start=1):
        m = titulo.match(linha)
        if m:
            paginas.append((m.group("rotulo"), int(m.group("arquivo")), []))
        elif paginas:
            paginas[-1][2].append((n, linha))
    return paginas


def _poe(pedacos, texto, destaques):
    if pedacos and pedacos[-1][1] == destaques:
        pedacos[-1][0] += texto
    else:
        pedacos.append([texto, destaques])


def pedacos(partes):
    """[(texto, destaques)] das partes (texto, destaques) de uma linha, juntas: cada trecho
    de espacos vira um espaco so, sem destaque (a escrita das marcas da a ele o destaque
    dos vizinhos), sem espaco nas pontas; pedacos seguidos com os mesmos destaques viram um."""
    out, espaco = [], False
    for c, d in ((c, frozenset(d)) for s, d in partes for c in s):
        if c.isspace():
            espaco = bool(out)
            continue
        if espaco:
            _poe(out, " ", frozenset())
            espaco = False
        _poe(out, c, d)
    return [(s, sorted(d)) for s, d in out]


def texto_simples(linha, padrao):
    """O texto de uma linha escrita no padrao, sem as marcas: o caractere escapado fica,
    sem o escape, e as marcas de destaque saem (as mais longas primeiro, para que "**" nao
    seja lido como dois "*")."""
    escape, escapar = padrao["escape"], set(padrao["escapar"])
    marcas = sorted({m for d in padrao.get("destaques", {}).values() for m in (d["abre"], d["fecha"])},
                    key=lambda m: (-len(m), m))
    out, i = [], 0
    comeco = next((c for c in padrao["escapar_no_comeco"] if linha.startswith(escape + c)), None)
    if comeco is not None:
        out.append(comeco)
        i = len(escape) + len(comeco)
    while i < len(linha):
        if linha[i] == escape and i + 1 < len(linha) and linha[i + 1] in escapar:
            out.append(linha[i + 1])
            i += 2
            continue
        marca = next((m for m in marcas if linha.startswith(m, i)), None)
        if marca is not None:
            i += len(marca)
            continue
        out.append(linha[i])
        i += 1
    return "".join(out)


def paginas_das_faixas(faixas, total):
    """As paginas do arquivo que as faixas cobrem, em ordem: cada faixa e {"de": primeira
    pagina, "ate": ultima}, as duas incluidas. Faixa que nao cabe nas paginas 1 a total,
    faixa ao contrario e pagina em duas faixas sao erro."""
    paginas = []
    for faixa in faixas:
        de, ate = faixa["de"], faixa["ate"]
        if not 1 <= de <= ate <= total:
            raise ValueError(f"a faixa {de}-{ate} não cabe nas páginas 1 a {total} do arquivo")
        paginas += range(de, ate + 1)
    repetidas = sorted({n for n in paginas if paginas.count(n) > 1})
    if repetidas:
        raise ValueError(f"página(s) em mais de uma faixa: {repetidas}")
    return sorted(paginas)
