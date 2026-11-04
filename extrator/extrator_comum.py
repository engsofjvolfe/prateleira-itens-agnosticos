"""
O que o extrator, os leitores dele e as outras pecas da prateleira fazem do mesmo jeito,
num lugar so: ler um texto em UTF-8, com as quebras de linha trocadas por "\\n" ou como estao
no arquivo, ler os dados de um arquivo ou de um texto JSON e conferir os dados contra
o molde deles (JSON Schema), que antes e conferido contra o molde dos moldes (o que o leitor
de molde entende), pegar um campo dos dados com o tipo pedido, achar os valores repetidos de
uma lista, compilar a expressao regular de um campo, conferir que a codificacao de um campo
existe, ler a configuracao do extrator contra o molde dela, conferir o padrao, preencher um
modelo do padrao, reconhecer o titulo de pagina que o modelo faz, dividir uma transcricao em
paginas, juntar os pedacos de uma linha com destaques, tirar de uma linha as marcas de
destaque e os escapes e expandir faixas de paginas.
"""

import codecs
import json
import re
from collections import Counter, namedtuple
from pathlib import Path

CAMPO = re.compile(r"\{(\w+)\}")
MOLDES = Path(__file__).resolve().parent / "esquemas"  # o molde de cada entrada do extrator, e os moldes comuns
MOLDE_DOS_MOLDES = MOLDES / "molde.schema.json"  # as palavras do JSON Schema que o leitor entende, e o valor de cada
QUEBRAS_COMO_ESTAO = ""  # o newline do open que le cada quebra de linha como ela esta no arquivo

# o molde de onde partem as referencias de "#", o arquivo dele (None quando ele nao vem de um molde comum) e a pasta
# em que se acha, antes da pasta dos moldes, o molde comum que uma referencia nomeia
Raiz = namedtuple("Raiz", "molde arquivo pasta")

# O tipo do Python de cada tipo do JSON Schema.
TIPOS = {"object": dict, "array": list, "string": str, "integer": int, "number": (int, float), "boolean": bool,
         "null": type(None)}


class ErroDeDados(Exception):
    """O que impede o trabalho; a mensagem diz o que e onde."""


def le_texto(caminho, exato=False):
    """O texto de um arquivo em UTF-8; erro (ErroDeDados) que diz o arquivo quando ele nao
    existe ou nao se le. Cada quebra de linha "\\r\\n" ou "\\r" vem como "\\n", como o Python le
    um texto; com exato, as quebras vem como estao no arquivo, para o texto que se grava de
    volta nele igual."""
    try:
        with open(caminho, encoding="utf-8", newline=QUEBRAS_COMO_ESTAO if exato else None) as arquivo:
            return arquivo.read()
    except (OSError, UnicodeDecodeError) as e:
        raise ErroDeDados(f"{caminho}: não se lê como texto em UTF-8 ({e})")


def le_json(caminho):
    """Os dados de um arquivo JSON em UTF-8; erro (ErroDeDados) que diz o arquivo quando ele
    nao se le."""
    return de_json(le_texto(caminho), caminho)


def de_json(texto, origem):
    """Os dados de um texto JSON; erro (ErroDeDados) que diz a origem dele, como o arquivo,
    quando ele nao se le como JSON."""
    try:
        return json.loads(texto)
    except json.JSONDecodeError as e:
        raise ErroDeDados(f"{origem}: não se lê como JSON ({e})")


def mostra(valor):
    """O valor JSON escrito como no JSON, para a mensagem de erro."""
    return json.dumps(valor, ensure_ascii=False)


def do_tipo(valor, tipo):
    """Se o valor JSON e do tipo do molde. O booleano nao e numero, e o inteiro e o numero
    escrito sem ponto, como o Python o le."""
    if tipo not in TIPOS:
        raise ErroDeDados(f"o molde usa um tipo que o leitor não conhece: {tipo!r}")
    return isinstance(valor, TIPOS[tipo]) and (tipo == "boolean" or not isinstance(valor, bool))


def tipo_de(valor):
    """O tipo do JSON Schema de um valor JSON, o mais estreito."""
    return next(t for t in TIPOS if do_tipo(valor, t))


def igual(a, b):
    """Se dois valores JSON sao o mesmo: o booleano so e igual a booleano, o numero a numero
    de mesmo valor, e listas e objetos, item por item."""
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(igual(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(igual(a[k], b[k]) for k in a)
    numeros = [do_tipo(v, "number") for v in (a, b)]
    if all(numeros):
        return a == b
    return not any(numeros) and type(a) is type(b) and a == b


def junta(erros):
    """Os erros [(caminho, motivo)] numa linha so, cada um com o caminho ("/" e a raiz)."""
    return "; ".join(f"{onde or '/'}: {motivo}" for onde, motivo in erros)


def compila(texto, onde):
    """A expressao regular do texto, compilada; erro (ErroDeDados) que diz onde ela esta
    quando nao compila."""
    try:
        return re.compile(texto)
    except re.error as e:
        raise ErroDeDados(f"{onde} não compila como expressão regular: {e}")


def referido(referencia, raiz):
    """(molde, raiz dele) para que a referencia aponta, na forma que o molde dos moldes ja conferiu: na raiz dada, a
    propria raiz ("#") ou um molde de $defs ("#/$defs/nome", com "~1" no lugar de "/" e "~0" no de "~" no nome); com
    o nome de um molde comum antes do "#" ("comum.schema.json#/$defs/nome"), o desse arquivo, achado na pasta da raiz
    ou, senao, na pasta dos moldes, e conferido contra o molde dos moldes; ele passa a ser a raiz das referencias de
    dentro dele."""
    arquivo, _, fragmento = referencia.partition("#")
    if arquivo:
        pastas = [p for p in (raiz.pasta, MOLDES) if p is not None]
        caminho = next((p / arquivo for p in pastas if (p / arquivo).is_file()), pastas[-1] / arquivo)
        comum = le_json(caminho)
        confere_molde(comum)
        raiz = Raiz(comum, caminho.resolve(), caminho.parent)
    alvo = raiz.molde
    for parte in fragmento.split("/")[1:]:
        parte = parte.replace("~1", "/").replace("~0", "~")
        if parte not in alvo:
            raise ErroDeDados(f"o molde aponta para o que ele não tem: {referencia!r}")
        alvo = alvo[parte]
    return alvo, raiz


def fora_do_texto(dados, molde, onde):
    erros = []
    if len(dados) < molde.get("minLength", 0):
        erros.append((onde, f"{mostra(dados)} tem menos de {molde['minLength']} caractere(s)"))
    if "maxLength" in molde and len(dados) > molde["maxLength"]:
        erros.append((onde, f"{mostra(dados)} tem mais de {molde['maxLength']} caractere(s)"))
    if "pattern" in molde:
        forma = compila(molde["pattern"], f"a forma {mostra(molde['pattern'])} do molde")
        if not forma.search(dados):
            erros.append((onde, f"{mostra(dados)} não segue a forma {molde['pattern']}"))
    return erros


def fora_do_numero(dados, molde, onde):
    erros = []
    if "minimum" in molde and dados < molde["minimum"]:
        erros.append((onde, f"{mostra(dados)} é menor que {molde['minimum']}"))
    if "maximum" in molde and dados > molde["maximum"]:
        erros.append((onde, f"{mostra(dados)} é maior que {molde['maximum']}"))
    return erros


def fora_da_lista(dados, molde, raiz, onde):
    erros = []
    if len(dados) < molde.get("minItems", 0):
        erros.append((onde, f"tem menos de {molde['minItems']} item(ns)"))
    if "maxItems" in molde and len(dados) > molde["maxItems"]:
        erros.append((onde, f"tem mais de {molde['maxItems']} item(ns)"))
    if molde.get("uniqueItems"):
        erros += [(f"{onde}/{k}", f"{mostra(v)} repete um item de antes") for k, v in enumerate(dados)
                  if any(igual(v, w) for w in dados[:k])]
    for k, valor in enumerate(dados):
        erros += fora_do_molde(valor, molde.get("items", True), raiz, f"{onde}/{k}")
    return erros


def fora_do_objeto(dados, molde, raiz, onde):
    erros = [(f"{onde}/{c}", "falta") for c in molde.get("required", []) if c not in dados]
    if len(dados) < molde.get("minProperties", 0):
        erros.append((onde, f"tem menos de {molde['minProperties']} campo(s)"))
    if "maxProperties" in molde and len(dados) > molde["maxProperties"]:
        erros.append((onde, f"tem mais de {molde['maxProperties']} campo(s)"))
    campos, outros = molde.get("properties", {}), molde.get("additionalProperties", True)
    for chave, valor in dados.items():
        if chave in campos:
            erros += fora_do_molde(valor, campos[chave], raiz, f"{onde}/{chave}")
        elif outros is False:
            erros.append((f"{onde}/{chave}", "campo que o molde não conhece"))
        else:
            erros += fora_do_molde(valor, outros, raiz, f"{onde}/{chave}")
    return erros


def confere_molde(molde):
    """Erro (ErroDeDados) que diz cada lugar do molde fora do molde dos moldes: uma palavra
    que o leitor nao entende, ou o valor dela que nao e da forma que ela pede."""
    dos_moldes = le_json(MOLDE_DOS_MOLDES)
    erros = fora_do_molde(molde, dos_moldes, Raiz(dos_moldes, MOLDE_DOS_MOLDES, MOLDES))
    if erros:
        raise ErroDeDados(f"o molde sai do que o leitor entende ({MOLDE_DOS_MOLDES.name}): {junta(erros)}")


def fora_do_molde(dados, molde, raiz=None, onde="", seguidas=frozenset(), pasta=None):
    """[(caminho, motivo)] de cada valor dos dados fora do molde (JSON Schema), com o caminho
    dentro dos dados ("/a/0/b"; "" e a raiz). Antes, o molde e conferido contra o molde dos
    moldes, que diz as palavras que o leitor confere e as que nao conferem: o que o leitor
    nao confere nunca passa calado. O pattern e a expressao regular do Python, buscada no
    texto; o $ref vai a raiz ("#"), a um molde de $defs ou, com o nome de um molde comum antes
    do "#", a um molde de $defs dele (referido), achado na pasta dada ou na pasta dos moldes.
    O tipo que o leitor nao conhece, a referencia para o que o molde nao tem ou que volta a
    ela mesma sem passar a um valor de dentro, o molde comum que falta ou que sai do molde dos
    moldes e a forma que nao compila sao erro (ErroDeDados). raiz e seguidas sao da
    conferencia de dentro: a raiz das referencias (Raiz), ja conferida, e as referencias ja
    seguidas no mesmo valor, cada uma com o arquivo da raiz dela."""
    if raiz is None:
        confere_molde(molde)
        raiz = Raiz(molde, None, pasta)
    if isinstance(molde, bool):
        return [] if molde else [(onde, "o molde não aceita valor aqui")]
    erros = []
    if "$ref" in molde:
        alvo, outra = referido(molde["$ref"], raiz)
        chave = (outra.arquivo, molde["$ref"].partition("#")[2])
        if chave in seguidas:
            raise ErroDeDados(f"a referência do molde volta a ela mesma: {molde['$ref']!r}")
        erros += fora_do_molde(dados, alvo, outra, onde, seguidas | {chave})
    tipos = molde.get("type", list(TIPOS))
    tipos = tipos if isinstance(tipos, list) else [tipos]
    if not any([do_tipo(dados, t) for t in tipos]):  # todos, para que o tipo desconhecido nunca passe
        return erros + [(onde, f"é {tipo_de(dados)}, e não {' ou '.join(tipos)}")]
    if "const" in molde and not igual(dados, molde["const"]):
        erros.append((onde, f"{mostra(dados)} não é {mostra(molde['const'])}"))
    if "enum" in molde and not any(igual(dados, v) for v in molde["enum"]):
        erros.append((onde, f"{mostra(dados)} não é um destes: {mostra(molde['enum'])}"))
    if isinstance(dados, str):
        erros += fora_do_texto(dados, molde, onde)
    elif do_tipo(dados, "number"):
        erros += fora_do_numero(dados, molde, onde)
    elif isinstance(dados, list):
        erros += fora_da_lista(dados, molde, raiz, onde)
    elif isinstance(dados, dict):
        erros += fora_do_objeto(dados, molde, raiz, onde)
    for parte in molde.get("allOf", []):
        erros += fora_do_molde(dados, parte, raiz, onde, seguidas)
    if "if" in molde:
        ramo = "else" if fora_do_molde(dados, molde["if"], raiz, onde, seguidas) else "then"
        erros += fora_do_molde(dados, molde.get(ramo, True), raiz, onde, seguidas)
    return erros


def conferido(dados, molde, nome):
    """Os dados, conferidos contra o molde (o arquivo do JSON Schema) pelo fora_do_molde:
    erro (ErroDeDados) que diz o nome dos dados e cada valor fora do molde, com o caminho
    dentro deles -- um nome escrito errado, um campo que falta ou um valor de outro tipo nao
    passam em silencio. O molde comum que ele nomeia se acha na pasta dele ou na pasta dos
    moldes. O erro do proprio molde diz o arquivo dele."""
    regras = le_json(molde)
    try:
        erros = fora_do_molde(dados, regras, pasta=Path(molde).parent)
    except ErroDeDados as e:
        raise ErroDeDados(f"{molde}: {e}")
    if erros:
        raise ErroDeDados(f"{nome}: fora do molde {Path(molde).name}: {junta(erros)}")
    return dados


def le_conferido(caminho, molde):
    """Os dados de um arquivo JSON, conferidos contra o molde (conferido), com o arquivo no
    erro."""
    return conferido(le_json(caminho), molde, caminho)


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
    return compila(campo(dados, caminho, str), f"o campo {caminho}")


def codificacao(dados, caminho):
    """A codificacao do campo de texto, quando o Python a conhece; erro claro, que diz o caminho e a codificacao,
    quando nao conhece."""
    nome = campo(dados, caminho, str)
    try:
        codecs.lookup(nome)
    except LookupError:
        raise ErroDeDados(f"o campo {caminho}: a codificação {nome!r} não existe") from None
    return nome


def repetidos(valores):
    """Os valores que aparecem mais de uma vez na lista, cada um uma vez, em ordem; nenhum
    quando nada se repete."""
    return sorted(valor for valor, vezes in Counter(valores).items() if vezes > 1)


def le_configuracao(caminho):
    """A configuracao do extrator, conferida contra o molde dela, para o extrator e para toda
    peca que a usa."""
    return le_conferido(caminho, MOLDES / "extrator.schema.json")


def confere_padrao(padrao):
    """Erro quando uma marca do padrao, ja conferido pelo molde (o escape e cada item de
    "escapar" sao um caractere so), pode se confundir com o texto. O proprio escape esta
    entre os que se escapam (assim uma barra do texto nao vira escape), e cada caractere das
    marcas de destaque tambem (assim um asterisco do texto nao vira marca); o escape nao esta
    nas marcas de destaque (senao o escape seguido do caractere da marca seria as duas
    coisas); cada marca de destaque e de um destaque so; e a marca entre duas celulas de
    tabela tem um caractere que se escapa (assim o texto de uma celula nao a divide em
    duas)."""
    escape, escapar = padrao["escape"], padrao["escapar"]
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
    repetidas = repetidos(paginas)
    if repetidas:
        raise ValueError(f"página(s) em mais de uma faixa: {repetidas}")
    return sorted(paginas)
