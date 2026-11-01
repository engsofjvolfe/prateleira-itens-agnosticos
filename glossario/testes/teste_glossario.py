"""Testes do glossario.py, com listas, cabecalhos e documentos inventados aqui, sorteados e com
letras de fora do ASCII. Conferem regras, nunca uma frase pronta: o glossario e o cabecalho,
sem os espacos e as quebras do fim, e, em ordem alfabetica sem contar acentos nem
maiusculas, o titulo de segundo nivel de cada termo e, do termo da lista, a definicao e a
fonte, sem os espacos e as quebras das pontas, e, do termo de uma marca, o link para o lugar
dela, a partir da pasta do glossario, entre < e > quando o caminho tem espaco: a secao (o
titulo mais perto acima, de nivel 2 em diante, tambem o titulo da propria linha) ou o
documento (sob o titulo de nivel 1, ou antes de qualquer titulo), com o titulo do documento,
ou o caminho, e o da secao no texto; a marca com atributos, em maiusculas, em duas linhas,
com tags dentro ou em NFD conta, e a que esta num bloco de codigo ou no codigo na linha nao;
o termo da lista e de uma marca sai so com a definicao; o glossario dado entre os documentos
fica de fora; sem termo, o glossario e so o cabecalho; com --conferir, nada e gravado, o
glossario em dia sai com 0 e o mudado ou o que falta, com 1; o termo repetido na lista (com
outras maiusculas, outra forma Unicode ou outros espacos), a marca vazia, o termo marcado em
dois lugares e dois titulos com a mesma ancora (dois termos, ou um termo e o titulo do
cabecalho) saem com 1, com o ERRO no lugar de cada um e nada gravado; a lista fora do molde,
que nao e JSON ou nao se le em UTF-8, o cabecalho que falta, vazio ou fora do UTF-8, o
documento que falta ou fora do UTF-8 e o glossario que e uma entrada ou uma pasta saem com 2,
sem nada gravado; duas rodadas dao o mesmo. Uso:
    python3 -I teste_glossario.py <pasta do glossario.py> <pasta de trabalho nova>
Precisa do extrator_comum.py, do texto_comum.py, do markdown_comum.py, do grava_ou_confere.py
e do documento_gerado.py, nas pastas irmas da peca.
"""
import copy
import json
import random
import subprocess
import sys
import unicodedata
from pathlib import Path

PECA, TRABALHO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
FALHAS = []
SORTEIO = random.Random(1)
MINUSCULAS = "abcdefghijklmnopqrstuvwxyzáçéõü"
COMECOS = ["Á", "á", "A", "a", "É", "é", "E", "e", "Ç", "c", "Z", "z"]  # para a ordem sem acentos nem maiusculas


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


def palavra():
    return "".join(SORTEIO.choice(MINUSCULAS) for _ in range(SORTEIO.randint(3, 8)))


def frase():
    return " ".join(palavra() for _ in range(SORTEIO.randint(2, 6)))


def ancora(titulo):
    """A ancora de um titulo so de letras e espacos, como o GitHub a da."""
    return titulo.lower().replace(" ", "-")


USADOS = set()


def termo():
    """Um termo novo, de uma ou duas palavras, que comeca por letra com ou sem acento, maiuscula ou nao."""
    while True:
        t = SORTEIO.choice(COMECOS) + palavra() + (f" {palavra()}" if SORTEIO.random() < 0.5 else "")
        if ancora(t) not in USADOS:
            USADOS.add(ancora(t))
            return t


def definicao(pontas=False):
    fonte = f"> *{frase()}*\n> *\"{frase()}\"*"
    return {"termo": termo(), "definicao": f" \n{frase()}\n{frase()}  \n" if pontas else frase(),
            "fonte": f"\n{fonte}\n\n" if pontas else fonte}


def grava(caminho, conteudo):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(conteudo, bytes):
        caminho.write_bytes(conteudo)
    else:
        caminho.write_text(conteudo, encoding="utf-8")
    return caminho


def grava_lista(caminho, termos, **outros):
    return grava(caminho, json.dumps({"versao_schema": 1, "termos": termos, **outros}, ensure_ascii=False, indent=1))


def roda(lista, cabecalho, glossario, *documentos, conferir=False):
    comando = [sys.executable, "-I", str(PECA / "glossario.py"), str(lista), str(cabecalho), str(glossario),
               *map(str, documentos)] + (["--conferir"] if conferir else [])
    r = subprocess.run(comando, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def erros_de(saida):
    return [l for l in saida.split("\n") if l.startswith("ERRO ")]


def le(caminho):
    return caminho.read_text(encoding="utf-8")


def sem_acentos(t):
    return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c)).casefold()


def link(relativo, titulo_do_documento, secao):
    nome, alvo = titulo_do_documento or relativo, relativo
    if secao:
        nome, alvo = f"{nome} › {secao}", f"{relativo}#{ancora(secao)}"
    return f"[{nome}](<{alvo}>)" if " " in alvo else f"[{nome}]({alvo})"


def esperado(cabecalho, termos, marcados):
    """O glossario pela regra: [(termo, [blocos])] da lista e das marcas que a lista nao tem, em ordem alfabetica."""
    da_lista = {t["termo"].casefold() for t in termos}
    entradas = [(t["termo"], [t["definicao"].strip(), t["fonte"].strip()]) for t in termos]
    entradas += [(m, [l]) for m, l in marcados if m.casefold() not in da_lista]
    entradas.sort(key=lambda e: (sem_acentos(e[0]), e[0]))
    return "\n\n".join([cabecalho.rstrip()] + [b for t, corpo in entradas for b in [f"## {t}", *corpo]]) + "\n"


TRABALHO.mkdir(parents=True)
TERMOS = [definicao(pontas=k < 2) for k in range(SORTEIO.randint(5, 8))]
LISTA = grava_lista(TRABALHO / "definicoes.json", TERMOS)
TITULO_DO_CABECALHO = f"Glossário {palavra()}"
USADOS.add(ancora(TITULO_DO_CABECALHO))
CABECALHO = grava(TRABALHO / "cabecalho.md", f"# {TITULO_DO_CABECALHO}\n\n{frase()}\n{frase()}  \n\n \n")
SAIDA = TRABALHO / "saida" / "glossario.md"
A, B = TRABALHO / "textos" / "a.md", TRABALHO / "outra pasta" / "b.md"
RELATIVO_A, RELATIVO_B = "../textos/a.md", "../outra pasta/b.md"
TITULO_A, S1, S2, S3, S4 = frase(), frase(), frase(), frase(), frase()
M = [termo() for _ in range(7)]
while len(M) < 8:  # o termo escrito em NFD precisa de uma letra com acento
    candidato = termo()
    if unicodedata.normalize("NFD", candidato) != candidato:
        M.append(candidato)
NFD = unicodedata.normalize("NFD", M[7])
DA_LISTA_NUMA_MARCA = TERMOS[0]["termo"].swapcase()
LINHAS_A = [f"# {TITULO_A}", "", f"{frase()} <dfn>{M[0]}</dfn> {frase()}", "", f"## {S1}", "",
            f"{frase()} <dfn title=\"{palavra()}\">{M[1]}</dfn>", "", "```", f"<dfn>{termo()}</dfn>", "```", "",
            f"{frase()} `<dfn>{termo()}</dfn>` {frase()}", "", f"### {S2}", "", f"<DFN>{M[2]}</DFN>",
            f"<dfn>{M[3].split(' ')[0]}", f"{palavra()}</dfn>", f"<dfn><em>{M[4]}</em></dfn>",
            f"<dfn>{DA_LISTA_NUMA_MARCA}</dfn>", "", f"## {S3} <dfn>{M[5]}</dfn>", "", frase(), ""]
M[3] = f"{LINHAS_A[17][5:]} {LINHAS_A[18][:-6]}"  # o termo em duas linhas, com os espacos juntos
grava(A, "\n".join(LINHAS_A))
grava(B, "\n".join([f"{frase()} <dfn>{M[6]}</dfn>", "", f"## {S4}", "", f"{frase()} <dfn>{NFD}</dfn>", ""]))
MARCADOS = [(M[0], link(RELATIVO_A, TITULO_A, None)), (M[1], link(RELATIVO_A, TITULO_A, S1)),
            (M[2], link(RELATIVO_A, TITULO_A, S2)), (M[3], link(RELATIVO_A, TITULO_A, S2)),
            (M[4], link(RELATIVO_A, TITULO_A, S2)), (DA_LISTA_NUMA_MARCA, "o termo da lista fica"),
            (M[5], link(RELATIVO_A, TITULO_A, f"{S3} {M[5]}")), (M[6], link(RELATIVO_B, None, None)),
            (M[7], link(RELATIVO_B, None, S4))]
ESPERADO = esperado(le(CABECALHO), TERMOS, MARCADOS)

cod, out = roda(LISTA, CABECALHO, SAIDA, A, B, SAIDA)
confere(cod == 0 and SAIDA.is_file(), f"as entradas certas saem com 0 e gravam o glossário, com a pasta: {out}")
if SAIDA.is_file():
    confere(le(SAIDA) == ESPERADO, f"o glossário segue a regra:\n{le(SAIDA)}\nno lugar de:\n{ESPERADO}")
    primeira = SAIDA.read_bytes()
    roda(LISTA, CABECALHO, SAIDA, A, B)
    confere(SAIDA.read_bytes() == primeira, "duas rodadas dão o mesmo")
    cod, out = roda(LISTA, CABECALHO, SAIDA, A, B, conferir=True)
    confere(cod == 0 and SAIDA.read_bytes() == primeira, f"o glossário em dia passa no --conferir: {out}")
    grava(SAIDA, le(SAIDA) + palavra())
    mudado = SAIDA.read_bytes()
    cod, out = roda(LISTA, CABECALHO, SAIDA, A, B, conferir=True)
    confere(cod == 1 and SAIDA.read_bytes() == mudado, f"o glossário mudado sai com 1 no --conferir, sem gravar: {out}")
SUMIDO = TRABALHO / "sumido" / "glossario.md"
cod, out = roda(LISTA, CABECALHO, SUMIDO, A, B, conferir=True)
confere(cod == 1 and not SUMIDO.parent.exists(), f"o glossário que falta sai com 1 no --conferir, sem criar: {out}")
OUTRO = grava(TRABALHO / "saida" / "outro.md", f"# {frase()}\n\n<dfn>{termo()}</dfn>\n")
cod, out = roda(LISTA, CABECALHO, OUTRO, A, B, OUTRO)
confere(cod == 0 and le(OUTRO) == ESPERADO, f"o glossário dado entre os documentos fica de fora deles: {out}")
VAZIO = TRABALHO / "saida" / "vazio.md"
cod, out = roda(grava_lista(TRABALHO / "nenhum.json", []), CABECALHO, VAZIO)
confere(cod == 0 and VAZIO.is_file() and le(VAZIO) == le(CABECALHO).rstrip() + "\n",
        f"sem termo, o glossário é só o cabeçalho: {out}")

ANTES = TRABALHO / "saida" / "antes.md"
roda(LISTA, CABECALHO, ANTES, A, B)
GUARDADO = ANTES.read_bytes() if ANTES.is_file() else b""
VARIANTES = {"outras maiúsculas": str.swapcase, "a forma NFD": lambda t: unicodedata.normalize("NFD", t),
             "outros espaços": lambda t: f" {t.replace(' ', '  ' + chr(9))}  "}
for numero, (nome, muda) in enumerate(VARIANTES.items()):
    j = SORTEIO.randrange(len(TERMOS))
    repetido = dict(definicao(), termo=muda(TERMOS[j]["termo"]))
    cod, out = roda(grava_lista(TRABALHO / f"repetido-{numero}.json", TERMOS + [repetido]), CABECALHO, ANTES, A, B)
    confere(cod == 1 and any(l.startswith(f"ERRO {TRABALHO / f'repetido-{numero}.json'}: ")
                             and f"/termos/{len(TERMOS)}/termo" in l and f"/termos/{j}/termo" in l
                             for l in erros_de(out)),
            f"o termo repetido na lista, com {nome}, sai com 1 e o ERRO diz os dois: {out}")
    confere(ANTES.read_bytes() == GUARDADO, f"com o termo repetido, com {nome}, nada é gravado")

C = grava(TRABALHO / "textos" / "c.md", "\n".join([frase(), "<dfn> <em></em> </dfn>", frase(),
                                                    f"<dfn>{M[1].swapcase()}</dfn>", ""]))
cod, out = roda(LISTA, CABECALHO, ANTES, A, B, C)
erros = erros_de(out)
for lugar, descricao in ((f"{C}:2: ", "a marca só com tags e espaços"), (f"{C}:4: ", "o termo marcado de novo"),
                         (f"{A}:7: ", "o termo marcado antes")):
    confere(cod == 1 and any(l.startswith(f"ERRO {lugar}") for l in erros), f"{descricao}: ERRO no lugar dela: {out}")
confere(len(erros) == 3 and ANTES.read_bytes() == GUARDADO, f"só esses três ERRO, e nada é gravado: {out}")
E = grava(TRABALHO / "textos" / "e.md", "\n".join([frase(), frase(), "<dfn></dfn>", ""]))
cod, out = roda(LISTA, CABECALHO, ANTES, A, B, E)
erros = erros_de(out)
confere(cod == 1 and len(erros) == 1 and erros[0].startswith(f"ERRO {E}:3: ") and ANTES.read_bytes() == GUARDADO,
        f"a marca vazia: sai com 1, com o ERRO no lugar dela, e nada é gravado: {out}")

MESMA = [dict(definicao(), termo=f"{palavra()} {palavra()}")]
MESMA.append(dict(definicao(), termo=MESMA[0]["termo"].replace(" ", "-")))
for nome, termos in (("dois termos com a mesma âncora", TERMOS + MESMA),
                     ("um termo com a âncora do título do cabeçalho",
                      TERMOS + [dict(definicao(), termo=TITULO_DO_CABECALHO.lower())])):
    cod, out = roda(grava_lista(TRABALHO / "mesma.json", termos), CABECALHO, ANTES)
    confere(cod == 1 and len(erros_de(out)) == 1 and erros_de(out)[0].startswith(f"ERRO {ANTES}: ")
            and ANTES.read_bytes() == GUARDADO, f"{nome}: sai com 1, com um ERRO, e nada é gravado: {out}")


def com(mudanca):
    termos = copy.deepcopy(TERMOS)
    mudanca(termos[0])
    return termos


NAO_SERVEM = TRABALHO / "nao-servem"
LISTAS_RUINS = {
    "campo que o molde não conhece": com(lambda t: t.update({palavra(): frase()})),
    "termo sem a fonte": com(lambda t: t.pop("fonte")),
    "termo com quebra de linha no meio": com(lambda t: t.update(termo=f"{palavra()}\n{palavra()}")),
    "termo com quebra de linha no fim": com(lambda t: t.update(termo=f"{palavra()}\n")),
    "definição só com espaços": com(lambda t: t.update(definicao=" \n" + chr(9))),
    "fonte só com espaços": com(lambda t: t.update(fonte="  ")),
}
for numero, (nome, termos) in enumerate(LISTAS_RUINS.items()):
    saida = NAO_SERVEM / f"lista-{numero}.md"
    cod, out = roda(grava_lista(NAO_SERVEM / f"lista-{numero}.json", termos), CABECALHO, saida, A)
    confere(cod == 2 and out.startswith("ERRO") and not saida.exists(), f"{nome}: sai com 2, sem gravar nada: {out}")
OUTRAS = {
    "outra versão": lambda c: grava(c, json.dumps({"versao_schema": 2, "termos": []})),
    "campo da lista que o molde não conhece": lambda c: grava_lista(c, [], **{palavra(): 1}),
    "lista que não é JSON": lambda c: grava(c, "{" + frase()),
    "lista que não se lê em UTF-8": lambda c: grava(c, "{\"versao_schema\": 1, \"termos\": [], \"x\": \"é\"}"
                                                      .encode("latin-1")),
}
for numero, (nome, faz) in enumerate(OUTRAS.items()):
    lista, saida = NAO_SERVEM / f"outra-{numero}.json", NAO_SERVEM / f"outra-{numero}.md"
    faz(lista)
    cod, out = roda(lista, CABECALHO, saida, A)
    confere(cod == 2 and out.startswith("ERRO") and not saida.exists(), f"{nome}: sai com 2, sem gravar nada: {out}")
LATIN = f"# {frase()}\n".encode("latin-1", "replace") + "ç".encode("latin-1")
ENTRADAS_RUINS = {
    "cabeçalho que falta": (NAO_SERVEM / "sem-cabecalho.md", A),
    "cabeçalho vazio": (grava(NAO_SERVEM / "cabecalho-vazio.md", " \n\n"), A),
    "cabeçalho que não se lê em UTF-8": (grava(NAO_SERVEM / "cabecalho-latin.md", LATIN), A),
    "documento que falta": (CABECALHO, NAO_SERVEM / "sem-documento.md"),
    "documento que não se lê em UTF-8": (CABECALHO, grava(NAO_SERVEM / "documento-latin.md", LATIN)),
}
for numero, (nome, (cabecalho, documento)) in enumerate(ENTRADAS_RUINS.items()):
    saida = NAO_SERVEM / f"entrada-{numero}.md"
    cod, out = roda(LISTA, cabecalho, saida, A, documento)
    confere(cod == 2 and out.startswith("ERRO") and not saida.exists(), f"{nome}: sai com 2, sem gravar nada: {out}")
for nome, entrada in (("a lista", LISTA), ("o cabeçalho", CABECALHO)):
    antes = entrada.read_bytes()
    cod, out = roda(LISTA, CABECALHO, entrada, A)
    confere(cod == 2 and out.startswith("ERRO") and entrada.read_bytes() == antes,
            f"o glossário que é {nome}: sai com 2, sem gravar nada: {out}")
PASTA = NAO_SERVEM / "pasta.md"
PASTA.mkdir(parents=True)
cod, out = roda(LISTA, CABECALHO, PASTA, A)
confere(cod == 2 and out.startswith("ERRO") and not any(PASTA.iterdir()),
        f"o glossário que é uma pasta: sai com 2, sem gravar nada: {out}")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
