"""Testes do que o extrator_comum.py da para as pecas lerem os proprios dados: o leitor de
molde (fora_do_molde, confere_molde, conferido e le_conferido), le_texto, campo e expressao.
Nao precisa de PDF.

Os nomes dos campos e os valores sao sorteados, com semente fixa (o sorteio e o mesmo em toda
rodada; outra semente vem com --semente), e cada molde e inventado aqui. Os testes conferem
regras, nunca uma frase pronta:
  - cada palavra do molde que o leitor confere aceita o valor que a segue e acusa o que nao
    a segue, no caminho do valor, e so nele: type (um ou uma lista; o booleano nao e numero,
    e o numero com ponto nao e inteiro), const e enum (o booleano nao e igual ao numero, e o
    numero e igual ao de mesmo valor), minLength e maxLength (em letras, tambem com acento),
    pattern (buscada no texto), minimum e maximum (com o proprio limite aceito), minItems,
    maxItems, uniqueItems (tambem com objetos), items, required, properties,
    additionalProperties (falso ou um molde), minProperties, maxProperties, allOf, if, then e
    else, o molde falso e o $ref (para $defs, para a raiz, com escape no nome, ao lado de
    outra palavra, e um molde que se repete dentro dos dados); as anotacoes nao conferem
    nada;
  - cada palavra do molde dos moldes tem um caso aqui, e cada molde do extrator, o proprio
    molde dos moldes tambem, segue o molde dos moldes;
  - todos os erros saem, nao so o primeiro; o valor do tipo errado da um erro so;
  - o molde fora do molde dos moldes (uma palavra que o leitor nao conhece, outro dialeto,
    um valor que nao e da forma que a palavra pede, uma referencia que nao vai a raiz nem a
    $defs) e erro, que diz o lugar no molde; o tipo desconhecido, tambem depois de um tipo
    certo, a referencia para o que o molde nao tem ou que volta a ela mesma e a forma que
    nao compila sao erro, que diz o que;
  - le_conferido da os dados do arquivo que segue o molde e, senao, erro com o arquivo, o
    molde e o caminho de cada valor fora; o arquivo que falta ou que nao e JSON e erro; o
    molde fora do molde dos moldes e erro, com o arquivo dele e o lugar; conferido faz o
    mesmo com dados ja lidos, e o erro diz o nome dado a eles;
  - le_texto da o texto do arquivo em UTF-8, como ele e, e o arquivo que falta ou que nao se
    le em UTF-8 e erro, que diz o arquivo;
  - campo da o valor no caminho com o tipo pedido e da erro, dizendo o caminho, quando ele
    falta ou e de outro tipo; expressao compila o campo ou da erro, dizendo o caminho;
  - duas conferencias dao o mesmo.
Uso:
    python3 -I teste_extrator_comum.py <pasta do extrator> <pasta de trabalho nova> [--semente N]
"""
import argparse
import json
import random
import re
import string
import sys
from pathlib import Path

LEITOR = argparse.ArgumentParser(description="Testes do leitor de molde, de campo e de expressao.")
LEITOR.add_argument("peca", type=Path, help="a pasta do extrator")
LEITOR.add_argument("trabalho", type=Path, help="uma pasta de trabalho nova")
LEITOR.add_argument("--semente", type=int, default=7, help="a semente do sorteio")
ARGS = LEITOR.parse_args()
PECA, TRABALHO = ARGS.peca.resolve(), ARGS.trabalho.resolve()
sys.path.insert(0, str(PECA))
import extrator_comum  # noqa: E402

SORTE = random.Random(ARGS.semente)
LETRAS = string.ascii_lowercase + "áçõü"
FALHAS = []
USADOS = set()
DOS_MOLDES = extrator_comum.le_json(extrator_comum.MOLDE_DOS_MOLDES)


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


def nome():
    """Um nome sorteado que nao saiu antes."""
    while True:
        sorteado = "".join(SORTE.choice(LETRAS) for _ in range(SORTE.randint(3, 8)))
        if sorteado not in USADOS:
            USADOS.add(sorteado)
            return sorteado


def erro_de(funcao, *argumentos):
    """A mensagem do ErroDeDados da chamada; None quando ela nao da erro."""
    try:
        funcao(*argumentos)
    except extrator_comum.ErroDeDados as e:
        return str(e)
    return None


def caminhos(dados, molde):
    """Os caminhos dos valores fora do molde, em ordem, um por erro."""
    return sorted(onde for onde, _ in extrator_comum.fora_do_molde(dados, molde))


A, B, C, D = nome(), nome(), nome(), nome()
TEXTO, OUTRO = nome(), nome()
LETRA = next(c for c in LETRAS if c != TEXTO[0])  # um texto so dela nunca tem TEXTO
N = SORTE.randint(2, 5)

# (descricao, molde, [(dados, caminhos dos erros)])
CASOS = [
    ("type de um tipo", {"type": "string"}, [(TEXTO, []), (N, [""]), (None, [""]), ([TEXTO], [""])]),
    ("type inteiro", {"type": "integer"}, [(N, []), (-N, []), (True, [""]), (N + 0.5, [""]), (float(N), [""]),
                                           (str(N), [""])]),
    ("type número", {"type": "number"}, [(N, []), (N + 0.5, []), (False, [""]), ({}, [""])]),
    ("type booleano", {"type": "boolean"}, [(True, []), (False, []), (0, [""]), ("", [""])]),
    ("type nulo", {"type": "null"}, [(None, []), ("", [""]), (0, [""]), (False, [""])]),
    ("type objeto", {"type": "object"}, [({}, []), ({A: N}, []), ([], [""])]),
    ("type lista", {"type": "array"}, [([], []), ([TEXTO, N], []), ({}, [""]), (TEXTO, [""])]),
    ("type de dois tipos", {"type": ["string", "null"]}, [(TEXTO, []), (None, []), (N, [""])]),
    ("const", {"const": N}, [(N, []), (float(N), []), (N + 1, [""]), (str(N), [""])]),
    ("const booleano", {"const": True}, [(True, []), (1, [""]), (False, [""])]),
    ("const objeto", {"const": {A: [N, TEXTO]}}, [({A: [N, TEXTO]}, []), ({A: [TEXTO, N]}, [""]),
                                                  ({A: [N, TEXTO], B: 1}, [""])]),
    ("enum", {"enum": [TEXTO, N, None]}, [(TEXTO, []), (N, []), (None, []), (OUTRO, [""]), (True, [""])]),
    ("minLength", {"minLength": N}, [("á" * N, []), ("ç" * (N - 1), [""]), (N, [])]),
    ("maxLength", {"maxLength": N}, [("õ" * N, []), ("ü" * (N + 1), [""])]),
    ("pattern", {"pattern": TEXTO}, [(TEXTO, []), (LETRA + TEXTO + OUTRO, []), (LETRA * 9, [""]), (N, [])]),
    ("minimum e maximum", {"minimum": -N, "maximum": N}, [(-N, []), (N, []), (0.5, []), (-N - 1, [""]),
                                                          (N + 0.5, [""]), (TEXTO, [])]),
    ("minItems e maxItems", {"minItems": 1, "maxItems": N}, [([TEXTO], []), ([N] * N, []), ([], [""]),
                                                             ([N] * (N + 1), [""])]),
    ("uniqueItems", {"uniqueItems": True}, [([N, str(N), True], []), ([N, TEXTO, N], ["/2"]),
                                            ([{A: N}, {A: N}], ["/1"]), ([N, float(N)], ["/1"]),
                                            ([1, True], [])]),
    ("items", {"items": {"type": "string"}}, [([TEXTO, OUTRO], []), ([TEXTO, N, None], ["/1", "/2"])]),
    ("required", {"required": [A, B]}, [({A: N, B: N}, []), ({A: N}, [f"/{B}"]), ({}, [f"/{A}", f"/{B}"]),
                                        ([A], [])]),
    ("properties", {"properties": {A: {"type": "string"}, B: {"type": "integer"}}},
     [({A: TEXTO, B: N, C: None}, []), ({A: N, B: TEXTO}, [f"/{A}", f"/{B}"])]),
    ("additionalProperties falso", {"properties": {A: True}, "additionalProperties": False},
     [({A: N}, []), ({A: N, C: N, D: N}, [f"/{C}", f"/{D}"])]),
    ("additionalProperties molde", {"properties": {A: True}, "additionalProperties": {"type": "integer"}},
     [({A: TEXTO, C: N}, []), ({A: TEXTO, C: TEXTO}, [f"/{C}"])]),
    ("minProperties e maxProperties", {"minProperties": 1, "maxProperties": 2},
     [({A: N}, []), ({A: N, B: N}, []), ({}, [""]), ({A: N, B: N, C: N}, [""])]),
    ("allOf", {"allOf": [{"minLength": N}, {"pattern": TEXTO}]},
     [(TEXTO * N, []), (LETRA * N, [""]), (TEXTO[:1], ["", ""])]),
    ("if, then e else", {"if": {"properties": {A: {"const": TEXTO}}}, "then": {"required": [B]},
                         "else": {"required": [C]}},
     [({A: TEXTO, B: N}, []), ({A: TEXTO}, [f"/{B}"]), ({A: OUTRO, C: N}, []), ({A: OUTRO}, [f"/{C}"])]),
    ("if e then, sem else", {"if": {"required": [A]}, "then": {"required": [B]}},
     [({A: N, B: N}, []), ({A: N}, [f"/{B}"]), ({C: N}, [])]),
    ("molde falso", {"properties": {A: False}}, [({B: N}, []), ({A: N}, [f"/{A}"])]),
    ("$ref para $defs", {"$defs": {D: {"type": "string"}}, "properties": {A: {"$ref": f"#/$defs/{D}"}}},
     [({A: TEXTO}, []), ({A: N}, [f"/{A}"])]),
    ("$ref com escape", {"$defs": {f"{D}/{C}": {"type": "integer"}, f"{D}~{C}": {"type": "string"}},
                         "properties": {A: {"$ref": f"#/$defs/{D}~1{C}"}, B: {"$ref": f"#/$defs/{D}~0{C}"}}},
     [({A: N, B: TEXTO}, []), ({A: TEXTO, B: N}, [f"/{A}", f"/{B}"])]),
    ("$ref ao lado de outra palavra", {"$defs": {D: {"type": "integer"}}, "$ref": f"#/$defs/{D}", "minimum": 0},
     [(N, []), (-N, [""]), (TEXTO, [""])]),
    ("$ref que se repete nos dados", {"type": "object", "additionalProperties": False,
                                      "properties": {A: {"type": "array", "items": {"$ref": "#"}}}},
     [({A: [{A: []}, {}]}, []), ({A: [{A: [{B: N}]}]}, [f"/{A}/0/{A}/0/{B}"])]),
    ("todos os erros", {"items": {"properties": {A: {"type": "string"}}, "required": [B]}},
     [([{A: N}, {B: N}, {A: TEXTO}], [f"/0/{A}", f"/0/{B}", f"/2/{B}"])]),
    ("o tipo errado dá um erro só", {"type": "string", "minLength": N + 1, "pattern": TEXTO, "enum": [TEXTO]},
     [(N, [""]), (TEXTO[:1], ["", "", ""])]),
    ("anotações, que não conferem", {"$schema": DOS_MOLDES["$schema"], "$id": TEXTO, "$comment": OUTRO,
                                     "title": TEXTO, "description": OUTRO, "default": N, "examples": [None]},
     [(N, []), (TEXTO, []), (None, []), ([{}], [])]),
]

for descricao, molde, exemplos in CASOS:
    for dados, esperados in exemplos:
        achados = caminhos(dados, molde)
        confere(achados == sorted(esperados), f"{descricao}: {dados!r}: os erros em {achados}, e não em {esperados}")
        confere(caminhos(dados, molde) == achados, f"{descricao}: {dados!r}: duas conferências dão o mesmo")
FALTAM = sorted(set(DOS_MOLDES["properties"]) - {palavra for _, molde, _ in CASOS for palavra in molde})
confere(not FALTAM, f"cada palavra do molde dos moldes tem um caso aqui; faltam {FALTAM}")
for arquivo in sorted(extrator_comum.MOLDES.glob("*.schema.json")):
    mensagem = erro_de(extrator_comum.confere_molde, extrator_comum.le_json(arquivo))
    confere(mensagem is None, f"{arquivo.name} segue o molde dos moldes: {mensagem}")

MOLDES_ERRADOS = [  # (descricao, molde, o que o erro diz: fora do molde dos moldes, o lugar no molde)
    ("uma palavra que o leitor não conhece", {"properties": {A: {"oneOf": [True]}}}, f"/properties/{A}/oneOf"),
    ("outro dialeto do JSON Schema", {"$schema": TEXTO}, "/$schema"),
    ("um molde que não é objeto nem booleano", {"items": N}, "/items"),
    ("uma contagem que não é inteiro", {"minLength": TEXTO}, "/minLength"),
    ("uma contagem negativa", {"maxItems": -N}, "/maxItems"),
    ("um tipo que não é texto", {"type": [N]}, "/type/0"),
    ("uma lista de tipos vazia", {"type": []}, "/type"),
    ("um enum vazio", {"enum": []}, "/enum"),
    ("um campo obrigatório repetido", {"required": [A, A]}, "/required/1"),
    ("um campo cujo molde não é molde", {"properties": {A: TEXTO}}, f"/properties/{A}"),
    ("um allOf vazio", {"allOf": []}, "/allOf"),
    ("um molde de $defs que não é molde", {"$defs": {A: N}}, f"/$defs/{A}"),
    ("uma forma que não é texto", {"pattern": N}, "/pattern"),
    ("um limite que não é número", {"minimum": TEXTO}, "/minimum"),
    ("uma referência para fora dele", {"$defs": {A: True}, "$ref": f"{TEXTO}.json#/$defs/{A}"}, "/$ref"),
    ("uma referência que não é caminho", {"$ref": f"#{TEXTO}"}, "/$ref"),
    ("uma referência que não vai a $defs", {"properties": {A: True}, "$ref": f"#/properties/{A}"}, "/$ref"),
    ("um tipo desconhecido", {"type": TEXTO}, TEXTO),
    ("um tipo desconhecido depois de um certo", {"type": ["array", TEXTO]}, TEXTO),
    ("uma referência para o que ele não tem", {"$defs": {}, "$ref": f"#/$defs/{TEXTO}"}, TEXTO),
    ("uma referência que volta a ela mesma", {"$defs": {A: {"$ref": f"#/$defs/{B}"}, B: {"$ref": f"#/$defs/{A}"}},
                                              "$ref": f"#/$defs/{A}"}, A),
    ("uma referência à raiz no mesmo valor", {"allOf": [{"$ref": "#"}]}, "#"),
    ("uma forma que não compila", {"items": {"additionalProperties": {"pattern": f"({TEXTO}"}}}, f"({TEXTO}"),
]
for descricao, molde, diz in MOLDES_ERRADOS:
    mensagem = erro_de(extrator_comum.fora_do_molde, [{A: TEXTO}], molde)
    confere(mensagem is not None and diz in mensagem, f"o molde com {descricao} é erro, que diz {diz!r}: {mensagem}")

# ---- le_conferido ----

TRABALHO.mkdir(parents=True)


def grava(nome_do_arquivo, valor):
    caminho = TRABALHO / nome_do_arquivo
    caminho.write_text(json.dumps(valor, ensure_ascii=False), encoding="utf-8")
    return caminho


MOLDE = grava(f"{nome()}.schema.json", {"type": "object", "required": [A], "additionalProperties": False,
                                        "properties": {A: {"type": "integer"}, B: {"type": "string"}}})
CERTOS = {A: N, B: TEXTO}
confere(extrator_comum.le_conferido(grava("certos.json", CERTOS), MOLDE) == CERTOS,
        "le_conferido dá os dados do arquivo que segue o molde")
ERRADOS = grava(f"{nome()}.json", {A: TEXTO, C: N})
mensagem = erro_de(extrator_comum.le_conferido, ERRADOS, MOLDE)
confere(mensagem is not None and all(p in mensagem for p in (ERRADOS.name, MOLDE.name, f"/{A}", f"/{C}")),
        f"le_conferido: erro que diz o arquivo, o molde e o caminho de cada valor fora: {mensagem}")
mensagem = erro_de(extrator_comum.le_conferido, grava("sem-a.json", {B: TEXTO}), MOLDE)
confere(mensagem is not None and f"/{A}" in mensagem, f"le_conferido: o campo que falta é erro: {mensagem}")
FALTA, QUEBRADO = TRABALHO / f"{nome()}.json", TRABALHO / f"{nome()}.json"
QUEBRADO.write_text("{" + TEXTO, encoding="utf-8")
for arquivo, descricao in ((FALTA, "que falta"), (QUEBRADO, "que não é JSON")):
    mensagem = erro_de(extrator_comum.le_conferido, arquivo, MOLDE)
    confere(mensagem is not None and arquivo.name in mensagem, f"o arquivo {descricao} é erro, que o diz: {mensagem}")
MAL_FEITO = grava(f"{nome()}.schema.json", {"properties": {A: {"minLength": TEXTO}}})
mensagem = erro_de(extrator_comum.le_conferido, grava(f"{nome()}.json", CERTOS), MAL_FEITO)
confere(mensagem is not None and all(p in mensagem for p in (MAL_FEITO.name, f"/properties/{A}/minLength")),
        f"le_conferido: o molde fora do molde dos moldes é erro, com o arquivo dele e o lugar: {mensagem}")
DOS_DADOS = nome()
confere(extrator_comum.conferido(CERTOS, MOLDE, DOS_DADOS) == CERTOS, "conferido dá os dados que seguem o molde")
mensagem = erro_de(extrator_comum.conferido, {A: TEXTO, C: N}, MOLDE, DOS_DADOS)
confere(mensagem is not None and all(p in mensagem for p in (DOS_DADOS, MOLDE.name, f"/{A}", f"/{C}")),
        f"conferido: erro que diz o nome dos dados, o molde e o caminho de cada valor fora: {mensagem}")

# ---- le_texto ----

ESCRITO = f"{TEXTO}\n{OUTRO} çãõü\n\n"
LIDO, SEM_UTF8 = TRABALHO / f"{nome()}.txt", TRABALHO / f"{nome()}.txt"
LIDO.write_bytes(ESCRITO.encode("utf-8"))
SEM_UTF8.write_bytes(f"{TEXTO} ç".encode("latin-1"))
confere(extrator_comum.le_texto(LIDO) == ESCRITO, "le_texto dá o texto do arquivo em UTF-8, como ele é")
for arquivo, descricao in ((TRABALHO / f"{nome()}.txt", "que falta"), (SEM_UTF8, "que não se lê em UTF-8")):
    mensagem = erro_de(extrator_comum.le_texto, arquivo)
    confere(mensagem is not None and arquivo.name in mensagem, f"le_texto: o arquivo {descricao} é erro, que o diz: "
                                                               f"{mensagem}")

# ---- campo e expressao ----

GRUPO, VALOR = nome(), f"{TEXTO} {OUTRO}"
FORA, DENTRO, NUMERO, SIM, LISTA, RUIM = (nome() for _ in range(6))
DADOS = {FORA: {DENTRO: {TEXTO: VALOR, NUMERO: SORTE.randint(-9, 9), SIM: True, LISTA: [VALOR]}},
         TEXTO: f"(?P<{GRUPO}>{re.escape(VALOR)})", RUIM: f"(?P<{GRUPO}"}
BASE = f"{FORA}/{DENTRO}"
confere(extrator_comum.campo(DADOS, f"{BASE}/{TEXTO}", str) == VALOR, "campo dá o valor no caminho")
confere(extrator_comum.campo(DADOS, f"{BASE}/{LISTA}", (list, str)) == [VALOR], "campo aceita uma tupla de tipos")
confere(type(extrator_comum.campo(DADOS, f"{BASE}/{NUMERO}", int)) is int, "campo dá o número")
confere(extrator_comum.campo(DADOS, f"{BASE}/{SIM}", bool) is True, "o booleano vale quando o tipo pedido é bool")
for caminho, tipo, descricao in ((f"{BASE}/{RUIM}", str, "campo que falta"),
                                 (f"{BASE}/{TEXTO}/{RUIM}", str, "caminho que passa por um texto"),
                                 (f"{BASE}/{NUMERO}", str, "campo de outro tipo"),
                                 (f"{BASE}/{SIM}", int, "booleano no lugar de número")):
    mensagem = erro_de(extrator_comum.campo, DADOS, caminho, tipo)
    confere(mensagem is not None and caminho in mensagem, f"{descricao} é erro, e a mensagem diz o caminho: {mensagem}")
confere(extrator_comum.expressao(DADOS, TEXTO).search(f"{OUTRO} {VALOR}").group(GRUPO) == VALOR,
        "expressao compila o texto do campo")
for caminho, descricao in ((RUIM, "expressão que não compila"), (f"{BASE}/{NUMERO}", "expressão que não é texto")):
    mensagem = erro_de(extrator_comum.expressao, DADOS, caminho)
    confere(mensagem is not None and caminho in mensagem, f"{descricao} é erro, e a mensagem diz o caminho: {mensagem}")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s) (semente {ARGS.semente})")
sys.exit(1 if FALHAS else 0)
