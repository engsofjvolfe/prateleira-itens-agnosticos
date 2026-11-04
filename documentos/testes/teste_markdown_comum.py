"""Testes do markdown_comum.py no que so as pecas que o importam usam: os titulos, com a linha,
o nivel e o texto de cada um, as linhas fora de codigo, com o numero de cada uma, o caminho a
partir de uma pasta, o alvo e o link como vao num documento e os documentos de um repositorio
git pelos padroes dados. O resto do modulo (a ancora, o codigo na linha, os marcadores e os
links) o teste do confere_links.py confere. Um documento inventado aqui, sorteado e com
letras de fora do ASCII: titulos de nivel 1 a 6, com recuo de zero a tres espacos e com ou
sem os # do fim, um titulo repetido tres vezes, paragrafos, blocos de codigo com cercas dos
dois sinais, com linhas de titulo dentro e com cercas que nao fecham o bloco (a do outro
sinal, a mais curta e a com texto depois), e linhas que nao sao titulo (sete #, # sem
espaco, recuo de quatro espacos). Confere regras, nunca uma frase pronta: cada titulo fora
de bloco de codigo, e so ele, sai na ordem, com a linha, o nivel, o texto sem os # e os
espacos das pontas e a ancora, com -1 e -2 no titulo repetido; as linhas fora de codigo sao
as do documento menos as dos blocos, cercas incluidas, cada uma com o numero dela, a partir
de 1; o caminho de um arquivo a partir de uma pasta, de outra, da do arquivo e de uma dada
com "..", com espacos nos nomes; o alvo vai entre < e > com espaco, tabulacao ou parenteses,
e so entao, tambem no link; os documentos de um repositorio git inventado, com nomes
sorteados, sao, em ordem, os versionados e os novos que seguem um dos padroes, sem os que o
.gitignore deixa de fora, os apagados, os que seguem um padrao de fora e os de outros
padroes, e a pasta sem git e erro do git; o git roda na pasta dada: a saida dele e a raiz do
repositorio, e os caminhos que ele da com -z sao os do indice, cada um uma vez, sem nenhum
vazio; duas leituras dao o mesmo. Uso:
    python3 -I teste_markdown_comum.py <pasta do markdown_comum.py> <pasta de trabalho nova>
Precisa do git, que o teste roda sem a configuracao do sistema e da conta e sem subir da
pasta de trabalho.
"""
import os
import random
import string
import subprocess
import sys
from pathlib import Path

PECA, TRABALHO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
sys.path.insert(0, str(PECA))
from markdown_comum import (alvo_de_link, ancora, caminho_relativo, caminhos_do_git,  # noqa: E402
                            documentos_do_repositorio, linhas_fora_de_codigo, link_markdown, saida_do_git, titulos)

FALHAS = []
SORTEIO = random.Random(1)
LETRAS = string.ascii_letters + "áçõüéñ"
os.environ.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", GIT_CEILING_DIRECTORIES=str(TRABALHO))


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


def texto():
    return " ".join("".join(SORTEIO.choice(LETRAS) for _ in range(SORTEIO.randint(2, 7)))
                    for _ in range(SORTEIO.randint(1, 4)))


TRABALHO.mkdir(parents=True)
linhas, esperados, em_codigo = [], [], set()
REPETIDO = texto()
casos = ["titulo"] * 8 + ["repetido"] * 3 + ["paragrafo"] * 4 + ["bloco"] * 2 + ["nao-titulo"] * 3
SORTEIO.shuffle(casos)
for caso in casos:
    if caso in ("titulo", "repetido"):
        nivel, nome = SORTEIO.randint(1, 6), REPETIDO if caso == "repetido" else texto()
        fim = SORTEIO.choice(["", " " + "#" * SORTEIO.randint(1, 3), " " + "#" * SORTEIO.randint(1, 3) + "  "])
        linhas.append(" " * SORTEIO.randint(0, 3) + "#" * nivel + " " * SORTEIO.randint(1, 2) + nome + fim)
        esperados.append((len(linhas), nivel, nome))
    elif caso == "paragrafo":
        linhas += [texto(), texto()]
    elif caso == "bloco":
        sinal = SORTEIO.choice("`~")
        cerca = " " * SORTEIO.randint(0, 3) + sinal * SORTEIO.randint(4, 5)
        outra = ("~" if sinal == "`" else "`") * (len(cerca.strip()) + 1)
        # nada aqui fecha o bloco: a cerca do outro sinal, a mais curta, a com texto depois e a de dois sinais; um
        # titulo vem logo depois de cada uma, para o bloco fechado antes da hora aparecer
        dentro = [f"## {texto()}", outra, f"# {texto()}", sinal * 3, f"## {texto()}",
                  f"{cerca.strip()}{sinal} {texto()}", f"# {texto()}", sinal * 2]
        comeco = len(linhas) + 1
        linhas += [cerca] + dentro + [cerca.strip() + sinal]
        em_codigo.update(range(comeco, len(linhas) + 1))
    else:
        linhas += ["#" * 7 + " " + texto(), "#" + texto(), "    # " + texto()]
    linhas.append("")
DOCUMENTO = "\n".join(linhas) + "\n"

vistas, esperado = {}, []
for linha, nivel, nome in esperados:
    base = ancora(nome)
    esperado.append((linha, nivel, nome, base if base not in vistas else f"{base}-{vistas[base]}"))
    vistas[base] = vistas.get(base, 0) + 1
achados = [tuple(t) for t in titulos(DOCUMENTO)]
confere(achados == esperado, f"cada título fora de bloco de código, e só ele, sai na ordem, com a linha, o nível, o "
                             f"texto e a âncora: {achados!r} no lugar de {esperado!r}")
repetidas = [t[3] for t in achados if t[2] == REPETIDO]
confere(len(repetidas) == 3 and repetidas[1:] == [f"{repetidas[0]}-1", f"{repetidas[0]}-2"],
        f"o título repetido ganha -1 e -2 na âncora: {repetidas!r}")
fora = list(linhas_fora_de_codigo(DOCUMENTO))
numeros = [n for n in range(1, len(linhas) + 1) if n not in em_codigo]
confere([n for n, _ in fora] == numeros and all(linhas[n - 1] == l for n, l in fora),
        "as linhas fora de código são as do documento menos as dos blocos, cada uma com o número dela, a partir de 1")
confere([tuple(t) for t in titulos(DOCUMENTO)] == achados and list(linhas_fora_de_codigo(DOCUMENTO)) == fora,
        "duas leituras dão o mesmo")

DE_LA, FUNDA, ARQUIVO = texto(), texto(), f"{texto()}.md"
ALVO = TRABALHO / DE_LA / FUNDA / ARQUIVO
for pasta, certo in ((TRABALHO / texto() / texto(), f"../../{DE_LA}/{FUNDA}/{ARQUIVO}"),
                     (TRABALHO / DE_LA / FUNDA, ARQUIVO),
                     (TRABALHO / DE_LA / texto() / "..", f"{FUNDA}/{ARQUIVO}")):
    confere(caminho_relativo(ALVO, pasta) == certo,
            f"o caminho a partir de {pasta}: {caminho_relativo(ALVO, pasta)!r} no lugar de {certo!r}")

NOME, SIMPLES = texto(), "".join(SORTEIO.choice(LETRAS) for _ in range(6)) + "/x.md#L3"
confere(alvo_de_link(SIMPLES) == SIMPLES and link_markdown(NOME, SIMPLES) == f"[{NOME}]({SIMPLES})",
        "o alvo sem espaço nem parênteses vai como vem, também no link")
for sinal in (" ", "\t", "(", ")"):
    alvo = SIMPLES[:3] + sinal + SIMPLES[3:]
    confere(alvo_de_link(alvo) == f"<{alvo}>" and link_markdown(NOME, alvo) == f"[{NOME}](<{alvo}>)",
            f"o alvo com {sinal!r} vai entre < e >, também no link")


def nome():
    """Um nome de arquivo ou de pasta sorteado, com letras de fora do ASCII e um espaco."""
    return f"{texto().split()[0]} {texto().split()[0]}"


def git(pasta, *argumentos):
    subprocess.run(["git", "-C", str(pasta), *argumentos], check=True, capture_output=True)


EXTENSOES = [f".{''.join(SORTEIO.choice(string.ascii_lowercase) for _ in range(3))}" for _ in range(3)]
SEGUEM, OUTRO, FORA_DE = EXTENSOES[:2], EXTENSOES[2], nome()  # duas extensoes que seguem, uma que nao e uma pasta
REPOSITORIO = TRABALHO / "repositorio"
versionados = [f"{nome()}{e}" for e in SEGUEM] + [f"{nome()}/{nome()}{SEGUEM[0]}", f"{nome()}{OUTRO}"]
novo, ignorado, apagado = f"{nome()}{SEGUEM[1]}", f"{nome()}{SEGUEM[0]}", f"{nome()}{SEGUEM[0]}"
de_fora, sozinho = f"{FORA_DE}/{nome()}{SEGUEM[0]}", f"{nome()}{SEGUEM[1]}"
REPOSITORIO.mkdir()
git(REPOSITORIO, "init", "-q")
for arquivo in versionados + [novo, ignorado, apagado, de_fora, sozinho]:
    (REPOSITORIO / arquivo).parent.mkdir(parents=True, exist_ok=True)
    (REPOSITORIO / arquivo).write_text(texto(), encoding="utf-8")
(REPOSITORIO / ".gitignore").write_text(f"{ignorado}\n", encoding="utf-8")
git(REPOSITORIO, "add", "--", *versionados, apagado, de_fora, sozinho)
(REPOSITORIO / apagado).unlink()
PADROES, FORA = [f"*{e}" for e in SEGUEM], [f"{FORA_DE}/*", sozinho]
seguem = [a for a in versionados if not a.endswith(OUTRO)] + [novo]
achados = documentos_do_repositorio(REPOSITORIO, PADROES, FORA)
confere(achados == sorted(seguem), f"os documentos do repositório são, em ordem, os versionados e os novos que seguem "
                                   f"um dos padrões, e nenhum de fora: {achados!r} no lugar de {sorted(seguem)!r}")
sem_fora = documentos_do_repositorio(REPOSITORIO, PADROES)
confere(sem_fora == sorted(seguem + [de_fora, sozinho]),
        f"sem os padrões de fora, os que seguem um deles entram: {sem_fora!r}")
confere(documentos_do_repositorio(REPOSITORIO, PADROES, FORA) == achados, "duas listas dão o mesmo")
NO_INDICE = versionados + [apagado, de_fora, sozinho]
caminhos = caminhos_do_git(REPOSITORIO, "ls-files", "--cached", "-z")
confere(len(caminhos) == len(NO_INDICE) and set(caminhos) == set(NO_INDICE),
        f"os caminhos que o git dá com -z, na pasta dada, são os do índice, cada um uma vez, sem nenhum vazio: "
        f"{caminhos!r}")
raiz = saida_do_git(REPOSITORIO, "rev-parse", "--show-toplevel").rstrip("\n")
confere(raiz == str(REPOSITORIO.resolve()), f"o git roda na pasta dada: {raiz!r}")
SEM_GIT = TRABALHO / "sem-git"
SEM_GIT.mkdir()
for nome_da_funcao, funcao in (("documentos_do_repositorio", lambda: documentos_do_repositorio(SEM_GIT, PADROES)),
                               ("saida_do_git", lambda: saida_do_git(SEM_GIT, "rev-parse", "--show-toplevel"))):
    try:
        funcao()
        confere(False, f"{nome_da_funcao}: a pasta sem git é erro do git")
    except subprocess.CalledProcessError as e:
        confere(e.stderr.strip(), f"{nome_da_funcao}: o erro do git traz a mensagem dele")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
