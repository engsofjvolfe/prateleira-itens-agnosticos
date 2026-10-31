"""Testes do confere_dicionario.py, com configuracoes e dicionarios inventados aqui, sorteados e
com letras de fora do ASCII: o comeco do titulo, as marcas do codigo, a marca entre dois
codigos, o separador das partes, as formas e os tamanhos. A primeira forma e larga (aceita
ate o vazio e as marcas), para que so a regra das marcas barre o codigo vazio ou com uma
marca dentro; as outras sao estreitas. Conferem regras, nunca uma frase pronta: o
dicionario certo, com titulos de um a tres codigos em ordem natural (9 antes de 10), um
bloco de codigo com titulos fora da regra e linhas que nao comecam pelo titulo, passa com 0;
cada titulo fora da regra (texto que nao e codigo, codigo sem uma das marcas, vazio ou com
uma marca dentro, titulo vazio, codigos separados por outra coisa, codigo com partes demais
ou com um tamanho que nao vale, parte que so tem a forma no comeco, codigo que e o comeco de
outro, codigo repetido, codigos fora da ordem natural) sai com 1 e um ERRO na linha dele, e
o codigo mais longo antes do comeco dele, com dois; o resumo diz, nessa ordem, os
dicionarios, os titulos e os erros; com mais de um dicionario, o ERRO diz o de cada um; a
configuracao fora do molde, a forma que nao compila, o tamanho que passa do numero de
formas e o dicionario que falta ou que nao se le em UTF-8 saem com 2, sem nada conferido;
duas rodadas dao o mesmo. Uso:
    python3 -I teste_confere_dicionario.py <pasta do confere_dicionario.py> <pasta de trabalho nova>
Precisa do extrator_comum.py e do markdown_comum.py, nas pastas irmas da peca.
"""
import copy
import json
import random
import re
import string
import subprocess
import sys
from pathlib import Path

PECA, TRABALHO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
FALHAS = []
SORTEIO = random.Random(1)
LETRAS = string.ascii_letters + "áçõüéñ"


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


def palavra():
    return "".join(SORTEIO.choice(LETRAS) for _ in range(SORTEIO.randint(3, 7)))


def texto():
    return " ".join(palavra() for _ in range(SORTEIO.randint(3, 8)))


def numero_ou_faixa():
    return SORTEIO.choice([str(SORTEIO.randint(1, 40)), f"{SORTEIO.randint(1, 15)}-{SORTEIO.randint(16, 30)}"])


LARGA = r"[^/.:\s]*"  # a primeira forma: tudo menos os separadores e os espacos, ate o vazio
ESTREITAS = {  # as outras formas, cada uma com quem sorteia uma parte que a segue
    r"\d+": lambda: str(SORTEIO.randint(1, 40)),
    r"\d+(-\d+)?": numero_ou_faixa,
    r"[0-9a-f]{4}": lambda: "".join(SORTEIO.choice("0123456789abcdef") for _ in range(4)),
    r"[a-zçã]+": lambda: "".join(SORTEIO.choice("abxzçã") for _ in range(SORTEIO.randint(2, 5))),
}
FORMAS = {LARGA: numero_ou_faixa, **ESTREITAS}
TITULO = SORTEIO.choice(["## ", "### ", "§ "])
ABRE, FECHA = SORTEIO.choice([("`", "`"), ("[", "]"), ("«", "»")])
ENTRE = SORTEIO.choice([" ", "  ", " · "])
SEPARADOR = SORTEIO.choice(["/", ".", ":"])
N = SORTEIO.randint(3, 4)
DA_CONF = [LARGA] + [SORTEIO.choice(list(ESTREITAS)) for _ in range(N - 1)]
TAMANHOS = sorted({1, N} | {t for t in range(2, N) if SORTEIO.random() < 0.5})
FORA_DOS_TAMANHOS = [t for t in range(1, N + 1) if t not in TAMANHOS]
CONF = {"versao_schema": 1, "titulo": TITULO, "codigo": {"abre": ABRE, "fecha": FECHA, "entre": ENTRE},
        "partes": {"separador": SEPARADOR, "formas": DA_CONF, "tamanhos": TAMANHOS}}


def codigo(tamanho=None):
    tamanho = SORTEIO.choice(TAMANHOS) if tamanho is None else tamanho
    return [FORMAS[f]() for f in DA_CONF[:tamanho]]


def chave(partes):
    """A ordem natural pela regra: os trechos de algarismos pelo valor, os outros pelo texto."""
    return [(tuple(int(p) if k % 2 else p for k, p in enumerate(re.split(r"(\d+)", parte))), parte)
            for parte in partes]


def validos(quantos):
    """Codigos sorteados que nenhum e o comeco de outro, em ordem natural."""
    escolhidos = []
    while len(escolhidos) < quantos:
        c = codigo()
        if all(c[:len(o)] != o and o[:len(c)] != c for o in escolhidos):
            escolhidos.append(c)
    return sorted(escolhidos, key=chave)


def marcado(partes):
    return f"{ABRE}{SEPARADOR.join(partes)}{FECHA}"


def titulo(codigos):
    return ENTRE.join(marcado(c) for c in codigos)


def grava(nome, conteudo):
    caminho = TRABALHO / nome
    if isinstance(conteudo, bytes):
        caminho.write_bytes(conteudo)
    else:
        caminho.write_text(conteudo if isinstance(conteudo, str) else json.dumps(conteudo, ensure_ascii=False),
                           encoding="utf-8")
    return caminho


def roda(configuracao, *dicionarios):
    r = subprocess.run([sys.executable, "-I", str(PECA / "confere_dicionario.py"), str(configuracao),
                        *map(str, dicionarios)], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def numeros_do_resumo(saida):
    return [int(n) for n in re.findall(r"\d+", saida.strip().split("\n")[-1])]


def erros_de(saida):
    return [l for l in saida.split("\n") if l.startswith("ERRO ")]


def duvida(linhas, titulos, resto):
    linhas.append(TITULO + resto)
    titulos.append(len(linhas))
    linhas += ["", texto(), "", SORTEIO.choice(["Aberta.", "Respondida."]), "",
               f"- 2026-10-{SORTEIO.randint(10, 30)}: {texto()}", ""]


TRABALHO.mkdir(parents=True)
CONFIGURACAO = grava("configuracao.json", CONF)
LINHAS, TITULOS = ["# " + texto(), "", texto(), ""], []
for _ in range(SORTEIO.randint(5, 8)):
    duvida(LINHAS, TITULOS, titulo(validos(SORTEIO.randint(1, 3))))
duvida(LINHAS, TITULOS, titulo([["9"], ["10"]]))
LINHAS += ["```", TITULO + texto(), TITULO, "```", "", "#" + TITULO + texto(), f"{texto()} {TITULO}{texto()}", ""]
CERTO = "\n".join(LINHAS) + "\n"
DICIONARIO = grava("dicionario.md", CERTO)

cod, out = roda(CONFIGURACAO, DICIONARIO)
confere(cod == 0 and not erros_de(out), f"o dicionário certo passa com 0: {out}")
confere(numeros_do_resumo(out) == [1, len(TITULOS), 0], f"o resumo diz os dicionários, os títulos e os erros: {out}")
confere(roda(CONFIGURACAO, DICIONARIO) == (cod, out), "duas rodadas dão o mesmo")

UM, DOIS, CHEIO = validos(1)[0], validos(2), codigo(N)
FORA_DA_FORMA = codigo(N)
FORA_DA_FORMA[SORTEIO.randrange(1, N)] += "§"
RUINS = {  # o titulo fora da regra e quantos erros ele da
    "texto que não é código": (f"{marcado(UM)}{ENTRE}{palavra()}", 1),
    "código sem a marca do fim": (f"{ABRE}99", 1),
    "código sem a marca do começo": (f"99{FECHA}", 1),
    "código vazio": (f"{ABRE}{FECHA}", 1),
    "marca do começo dentro do código": (f"{ABRE}9{ABRE}x{FECHA}", 1),
    "marca do fim dentro do código": (f"{ABRE}9{FECHA}x{FECHA}", 1),
    "título vazio": ("", 1),
    "códigos separados por outra coisa": (f"{marcado(DOIS[0])}{ENTRE * 2}{marcado(DOIS[1])}", 1),
    "código com partes demais": (marcado(CHEIO + [FORMAS[DA_CONF[1]]()]), 1),
    "parte que só tem a forma no começo": (marcado(FORA_DA_FORMA), 1),
    "código que é o começo de outro": (titulo([CHEIO[:1], CHEIO]), 1),
    "código mais longo antes do começo dele": (titulo([CHEIO, CHEIO[:1]]), 2),
    "código repetido": (titulo([UM, UM]), 1),
    "códigos fora da ordem natural": (titulo([["10"], ["9"]]), 1),
}
if FORA_DOS_TAMANHOS:
    RUINS["código com um tamanho que não vale"] = (marcado(codigo(SORTEIO.choice(FORA_DOS_TAMANHOS))), 1)
for numero, (nome, (resto, quantos)) in enumerate(RUINS.items()):
    linhas, titulos = list(LINHAS), list(TITULOS)
    duvida(linhas, titulos, resto)
    ruim = grava(f"ruim-{numero}.md", "\n".join(linhas) + "\n")
    cod, out = roda(CONFIGURACAO, ruim)
    erros = erros_de(out)
    confere(cod == 1 and len(erros) == quantos and all(l.startswith(f"ERRO {ruim}:{titulos[-1]}: ") for l in erros),
            f"{nome}: sai com 1, com {quantos} ERRO na linha do título: {out}")
    confere(numeros_do_resumo(out) == [1, len(titulos), len(erros)], f"{nome}: o resumo conta o erro: {out}")

DOIS_DICIONARIOS = grava("segundo.md", CERTO + TITULO + RUINS["código repetido"][0] + "\n")
cod, out = roda(CONFIGURACAO, DICIONARIO, DOIS_DICIONARIOS)
erros = erros_de(out)
confere(cod == 1 and len(erros) == 1 and erros[0].startswith(f"ERRO {DOIS_DICIONARIOS}:{len(LINHAS) + 1}: ")
        and numeros_do_resumo(out) == [2, 2 * len(TITULOS) + 1, 1],
        f"com dois dicionários, o ERRO diz o de cada problema, e o resumo conta os dois: {out}")


def com(mudanca):
    conf = copy.deepcopy(CONF)
    mudanca(conf)
    return conf


CONFIGURACOES_RUINS = {
    "campo que o molde não conhece": com(lambda c: c.update({palavra(): 1})),
    "campo do código que o molde não conhece": com(lambda c: c["codigo"].update({palavra(): "x"})),
    "configuração sem as partes": com(lambda c: c.pop("partes")),
    "começo do título vazio": com(lambda c: c.update(titulo="")),
    "começo do título com quebra de linha": com(lambda c: c.update(titulo=f"{TITULO}\n")),
    "marca de entre vazia": com(lambda c: c["codigo"].update(entre="")),
    "marca do começo vazia": com(lambda c: c["codigo"].update(abre="")),
    "separador vazio": com(lambda c: c["partes"].update(separador="")),
    "nenhuma forma": com(lambda c: c["partes"].update(formas=[])),
    "forma vazia": com(lambda c: c["partes"]["formas"].__setitem__(0, "")),
    "forma que não compila": com(lambda c: c["partes"]["formas"].__setitem__(0, "(")),
    "nenhum tamanho": com(lambda c: c["partes"].update(tamanhos=[])),
    "tamanho zero": com(lambda c: c["partes"].update(tamanhos=[0])),
    "tamanho que passa do número de formas": com(lambda c: c["partes"].update(tamanhos=[N + 1])),
    "tamanho repetido": com(lambda c: c["partes"].update(tamanhos=[1, 1])),
    "outra versão": com(lambda c: c.update(versao_schema=2)),
}
for numero, (nome, conf) in enumerate(CONFIGURACOES_RUINS.items()):
    cod, out = roda(grava(f"configuracao-{numero}.json", conf), DICIONARIO)
    confere(cod == 2 and out.startswith("ERRO") and not erros_de(out), f"{nome}: sai com 2, sem conferir nada: {out}")
LATIN = grava("latin.md", f"{TITULO}{marcado(UM)}\nç".encode("latin-1", "replace"))
OUTRAS_ENTRADAS = {
    "configuração que não é JSON": (grava("nao-json.json", "{" + texto()), DICIONARIO),
    "dicionário que falta": (CONFIGURACAO, TRABALHO / "sumido.md"),
    "dicionário que não se lê em UTF-8": (CONFIGURACAO, LATIN),
}
for nome, (configuracao, dicionario) in OUTRAS_ENTRADAS.items():
    cod, out = roda(configuracao, DICIONARIO, dicionario)
    confere(cod == 2 and out.startswith("ERRO") and not erros_de(out), f"{nome}: sai com 2, sem conferir nada: {out}")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
