"""Testes do divergencias.py, com listas, cabecalhos e rotulos inventados aqui, sorteados e
com letras de fora do ASCII. Conferem regras, nunca uma frase pronta: o documento e o
cabecalho, sem os espacos e as quebras do fim, e, para cada divergencia, na ordem da lista,
o titulo de segundo nivel com o fato e, para cada forma, a ensinada primeiro e as outras na
ordem delas, o rotulo dela com o que ela diz e a fonte, sem os espacos e as quebras das
pontas, com uma linha em branco entre os blocos e uma quebra de linha no fim; sem
divergencia, o documento e so o cabecalho; com --conferir, nada e gravado, o documento em
dia sai com 0 e o mudado ou o que falta, com 1; o fato repetido (com outras maiusculas,
outra forma Unicode ou outros espacos) e a forma que diz o mesmo que outra do mesmo fato
(com outra forma Unicode ou outros espacos) saem com 1, com o caminho dos dois no ERRO e nada
gravado, mas o que difere so em maiusculas no que a forma diz, e o que fatos diferentes
dizem igual, passam; a lista fora do molde, que nao e JSON ou nao se le em UTF-8, o
cabecalho que falta, que nao se le em UTF-8 ou que esta vazio, o rotulo que falta ou que nao
e uma linha so com alguma letra e o documento que e um dos arquivos de entrada ou uma pasta
saem com 2, sem nada gravado; duas rodadas dao o mesmo. Uso:
    python3 -I teste_divergencias.py <pasta do divergencias.py> <pasta de trabalho nova>
Precisa do extrator_comum.py, do texto_comum.py, do grava_ou_confere.py e do
documento_gerado.py, nas pastas irmas da peca.
"""
import copy
import json
import random
import string
import subprocess
import sys
import unicodedata
from pathlib import Path

PECA, TRABALHO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
FALHAS = []
SORTEIO = random.Random(1)
ACENTUADAS = "áçõüéñ"  # letras que a forma NFD escreve com o acento separado
LETRAS = string.ascii_letters + ACENTUADAS + "€✓"


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


def palavra():
    return "".join(SORTEIO.choice(LETRAS) for _ in range(SORTEIO.randint(3, 8)))


def linha():
    """Uma linha sorteada, de palavras, sempre com uma letra acentuada e uma do ASCII."""
    return " ".join(palavra() for _ in range(SORTEIO.randint(2, 5))) + f" {SORTEIO.choice(ACENTUADAS)}x"


def forma(pontas=False):
    """Uma forma sorteada; a fonte e um bloco de uma a tres linhas, com espacos e quebras nas pontas quando pedido."""
    fonte = "\n".join(f"> {linha()}" for _ in range(SORTEIO.randint(1, 3)))
    return {"diz": linha(), "fonte": f"\n \n{fonte}  \n\n" if pontas else fonte}


def divergencia(pontas=False, outras=None):
    quantas = SORTEIO.randint(1, 3) if outras is None else outras
    return {"fato": linha(), "ensinada": forma(pontas), "outras": [forma(pontas) for _ in range(quantas)]}


def grava_lista(caminho, divergencias, **outros):
    caminho.write_text(json.dumps({"versao_schema": 1, "divergencias": divergencias, **outros},
                                  ensure_ascii=False, indent=1), encoding="utf-8")
    return caminho


def roda(lista, cabecalho, documento, *extra, ensinada=None, outra=None):
    rotulos = {"--ensinada": ENSINADA if ensinada is None else ensinada, "--outra": OUTRA if outra is None else outra}
    comando = [sys.executable, "-I", str(PECA / "divergencias.py"), str(lista), str(cabecalho), str(documento)]
    comando += [parte for opcao, valor in rotulos.items() if valor is not False for parte in (opcao, valor)]
    r = subprocess.run(comando + list(extra), capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def esperado(cabecalho, divergencias):
    """O documento pela regra: o cabecalho e, de cada divergencia, o titulo e cada forma, com o rotulo e a fonte."""
    blocos = [cabecalho.rstrip()]
    for d in divergencias:
        blocos.append(f"## {d['fato']}")
        for rotulo, f in [(ENSINADA, d["ensinada"])] + [(OUTRA, o) for o in d["outras"]]:
            blocos += [f"{rotulo} {f['diz']}", f["fonte"].strip()]
    return "\n\n".join(blocos) + "\n"


def le(caminho):
    return caminho.read_text(encoding="utf-8")


TRABALHO.mkdir(parents=True)
ENSINADA, OUTRA = f"**{palavra()}:**", f"{palavra()} {palavra()}:"
CABECALHO = TRABALHO / "cabecalho.md"
CABECALHO.write_text(f"# {linha()}\n\n{linha()}\n{linha()}  \n\n \n\n", encoding="utf-8")
DIVERGENCIAS = [divergencia(pontas=True, outras=3)] + [divergencia() for _ in range(SORTEIO.randint(2, 5))]
LISTA = grava_lista(TRABALHO / "lista.json", DIVERGENCIAS)
DOCUMENTO = TRABALHO / "saida" / "dentro" / "documento.md"

cod, out = roda(LISTA, CABECALHO, DOCUMENTO)
confere(cod == 0 and DOCUMENTO.is_file(), f"a lista certa sai com 0 e grava o documento, criando as pastas: {out}")
if DOCUMENTO.is_file():
    confere(le(DOCUMENTO) == esperado(le(CABECALHO), DIVERGENCIAS),
            "o documento é o cabeçalho e cada divergência, na ordem, com o título, os rótulos, o que cada forma diz "
            "e a fonte")
    primeira = DOCUMENTO.read_bytes()
    roda(LISTA, CABECALHO, DOCUMENTO)
    confere(DOCUMENTO.read_bytes() == primeira, "duas rodadas dão o mesmo")

    cod, out = roda(LISTA, CABECALHO, DOCUMENTO, "--conferir")
    confere(cod == 0 and DOCUMENTO.read_bytes() == primeira, f"o documento em dia passa no --conferir: {out}")
    DOCUMENTO.write_text(le(DOCUMENTO) + palavra(), encoding="utf-8")
    mudado = DOCUMENTO.read_bytes()
    cod, out = roda(LISTA, CABECALHO, DOCUMENTO, "--conferir")
    confere(cod == 1 and DOCUMENTO.read_bytes() == mudado,
            f"o documento mudado sai com 1 no --conferir, sem gravar: {out}")
SUMIDO = TRABALHO / "sumido" / "documento.md"
cod, out = roda(LISTA, CABECALHO, SUMIDO, "--conferir")
confere(cod == 1 and not SUMIDO.parent.exists(),
        f"o documento que falta sai com 1 no --conferir, sem criar nada: {out}")

VAZIO = TRABALHO / "vazio.md"
cod, out = roda(grava_lista(TRABALHO / "lista-vazia.json", []), CABECALHO, VAZIO)
confere(cod == 0 and VAZIO.is_file() and le(VAZIO) == le(CABECALHO).rstrip() + "\n",
        f"sem divergência, o documento é só o cabeçalho: {out}")

VARIANTES = {"outras maiúsculas": str.swapcase, "a forma NFD": lambda t: unicodedata.normalize("NFD", t),
             "outros espaços": lambda t: f"  {t.replace(' ', ' ' + chr(9) + '  ')} "}
ANTES = TRABALHO / "antes.md"
roda(LISTA, CABECALHO, ANTES)
GUARDADO = ANTES.read_bytes() if ANTES.is_file() else b""
for numero, (nome, muda) in enumerate(VARIANTES.items()):
    j = SORTEIO.randrange(len(DIVERGENCIAS))
    repetida = copy.deepcopy(DIVERGENCIAS[SORTEIO.randrange(len(DIVERGENCIAS))])
    repetida["fato"] = muda(DIVERGENCIAS[j]["fato"])
    lista = grava_lista(TRABALHO / f"fato-repetido-{numero}.json", DIVERGENCIAS + [repetida])
    cod, out = roda(lista, CABECALHO, ANTES)
    k = len(DIVERGENCIAS)
    confere(cod == 1 and any(l.startswith("ERRO") and f"/divergencias/{k}/fato" in l and f"/divergencias/{j}/fato" in l
                             for l in out.split("\n")),
            f"o fato repetido, com {nome}, sai com 1 e o ERRO diz os dois: {out}")
    confere(ANTES.read_bytes() == GUARDADO, f"com o fato repetido, com {nome}, nada é gravado")

for numero, (nome, muda) in enumerate(list(VARIANTES.items())[1:]):
    divergencias = copy.deepcopy(DIVERGENCIAS)
    k = SORTEIO.randrange(len(divergencias))
    m = SORTEIO.randrange(len(divergencias[k]["outras"]))
    divergencias[k]["outras"][m]["diz"] = muda(divergencias[k]["ensinada"]["diz"])
    lista = grava_lista(TRABALHO / f"forma-repetida-{numero}.json", divergencias)
    cod, out = roda(lista, CABECALHO, ANTES)
    confere(cod == 1 and any(l.startswith("ERRO") and f"/divergencias/{k}/outras/{m}/diz" in l
                             and f"/divergencias/{k}/ensinada/diz" in l for l in out.split("\n")),
            f"a forma que diz o mesmo que outra do fato, com {nome}, sai com 1 e o ERRO diz as duas: {out}")
    confere(ANTES.read_bytes() == GUARDADO, f"com a forma repetida, com {nome}, nada é gravado")

PASSAM = TRABALHO / "passam"
PASSAM.mkdir()
so_maiusculas = copy.deepcopy(DIVERGENCIAS)
so_maiusculas[0]["outras"][0]["diz"] = so_maiusculas[0]["ensinada"]["diz"].swapcase()
mesma_em_outro = copy.deepcopy(DIVERGENCIAS)
mesma_em_outro[1]["ensinada"]["diz"] = mesma_em_outro[0]["ensinada"]["diz"]
for numero, (nome, divergencias) in enumerate((("o que a forma diz com outras maiúsculas", so_maiusculas),
                                               ("o mesmo dito em fatos diferentes", mesma_em_outro))):
    saida = PASSAM / f"{numero}.md"
    cod, out = roda(grava_lista(PASSAM / f"{numero}.json", divergencias), CABECALHO, saida)
    confere(cod == 0 and saida.is_file() and le(saida) == esperado(le(CABECALHO), divergencias),
            f"{nome} não é problema: {out}")


def com(mudanca):
    """Uma copia das divergencias com a mudanca feita na primeira."""
    divergencias = copy.deepcopy(DIVERGENCIAS)
    mudanca(divergencias[0])
    return divergencias


NAO_SERVEM = TRABALHO / "nao-servem"
NAO_SERVEM.mkdir()
NAO_UTF8 = "{\"versao_schema\": 1, \"divergencias\": [], \"x\": \"é\"}".encode("latin-1")
LISTAS_RUINS = {
    "campo que o molde não conhece": com(lambda d: d.update({palavra(): linha()})),
    "divergência sem as outras formas": com(lambda d: d.pop("outras")),
    "outras formas vazias": com(lambda d: d.update(outras=[])),
    "fato com quebra de linha no meio": com(lambda d: d.update(fato=f"{linha()}\n{linha()}")),
    "fato com quebra de linha no fim": com(lambda d: d.update(fato=f"{linha()}\n")),
    "o que a forma diz só com espaços": com(lambda d: d["ensinada"].update(diz=" " + chr(9) + " ")),
    "fonte só com espaços": com(lambda d: d["outras"][0].update(fonte=" \n \n")),
    "forma sem a fonte": com(lambda d: d["ensinada"].pop("fonte")),
}
for numero, (nome, divergencias) in enumerate(LISTAS_RUINS.items()):
    saida = NAO_SERVEM / f"lista-{numero}.md"
    cod, out = roda(grava_lista(NAO_SERVEM / f"lista-{numero}.json", divergencias), CABECALHO, saida)
    confere(cod == 2 and out.startswith("ERRO") and not saida.exists(), f"{nome}: sai com 2, sem gravar nada: {out}")
OUTROS = {"versao_schema que não é a 1": lambda c: c.write_text(json.dumps({"versao_schema": 2, "divergencias": []}),
                                                                 encoding="utf-8"),
          "campo da lista que o molde não conhece": lambda c: grava_lista(c, [], **{palavra(): 1}),
          "lista que não é JSON": lambda c: c.write_text("{" + linha(), encoding="utf-8"),
          "lista que não se lê em UTF-8": lambda c: c.write_bytes(NAO_UTF8)}
for numero, (nome, grava) in enumerate(OUTROS.items()):
    lista, saida = NAO_SERVEM / f"outro-{numero}.json", NAO_SERVEM / f"outro-{numero}.md"
    grava(lista)
    cod, out = roda(lista, CABECALHO, saida)
    confere(cod == 2 and out.startswith("ERRO") and not saida.exists(), f"{nome}: sai com 2, sem gravar nada: {out}")

CABECALHOS = {"cabeçalho vazio": lambda c: c.write_text(" \n\n" + chr(9) + "\n", encoding="utf-8"),
              "cabeçalho que não se lê em UTF-8": lambda c: c.write_bytes(f"# {linha()}".encode("latin-1", "replace")
                                                                          + "ç".encode("latin-1")),
              "cabeçalho que falta": lambda c: None}
for numero, (nome, grava) in enumerate(CABECALHOS.items()):
    cabecalho, saida = NAO_SERVEM / f"cabecalho-{numero}.md", NAO_SERVEM / f"cabecalho-{numero}-saida.md"
    grava(cabecalho)
    cod, out = roda(LISTA, cabecalho, saida)
    confere(cod == 2 and out.startswith("ERRO") and not saida.exists(), f"{nome}: sai com 2, sem gravar nada: {out}")

ROTULOS = {"rótulo vazio": "", "rótulo só com espaços": " " + chr(9) + " ", "rótulo com quebra de linha no meio":
           f"{palavra()}\n{palavra()}", "rótulo com quebra de linha no fim": f"{palavra()}\n"}
for numero, (nome, rotulo) in enumerate(ROTULOS.items()):
    for opcao in ("ensinada", "outra"):
        saida = NAO_SERVEM / f"rotulo-{numero}-{opcao}.md"
        cod, out = roda(LISTA, CABECALHO, saida, **{opcao: rotulo})
        confere(cod == 2 and out.startswith("ERRO") and not saida.exists(),
                f"{nome}, em --{opcao}: sai com 2, sem gravar nada: {out}")
for opcao in ("ensinada", "outra"):
    saida = NAO_SERVEM / f"sem-{opcao}.md"
    cod, out = roda(LISTA, CABECALHO, saida, **{opcao: False})
    confere(cod == 2 and not saida.exists(), f"sem --{opcao}: sai com 2, sem gravar nada: {out}")

for nome, entrada in (("a lista", LISTA), ("o cabeçalho", CABECALHO)):
    antes = entrada.read_bytes()
    cod, out = roda(LISTA, CABECALHO, entrada)
    confere(cod == 2 and out.startswith("ERRO") and entrada.read_bytes() == antes,
            f"o documento que é {nome}: sai com 2, sem gravar nada: {out}")
PASTA_NO_LUGAR = NAO_SERVEM / "pasta.md"
PASTA_NO_LUGAR.mkdir()
cod, out = roda(LISTA, CABECALHO, PASTA_NO_LUGAR)
confere(cod == 2 and out.startswith("ERRO") and not any(PASTA_NO_LUGAR.iterdir()),
        f"o documento que é uma pasta: sai com 2, sem gravar nada: {out}")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
