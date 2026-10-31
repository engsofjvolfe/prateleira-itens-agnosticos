"""Testes do markdown_comum.py no que so as pecas que o importam usam: os titulos, com a linha,
o nivel e o texto de cada um, e as linhas fora de codigo, com o numero de cada uma. O resto
do modulo (a ancora, o codigo na linha, os marcadores) o teste do confere_links.py confere.
Um documento inventado aqui, sorteado e com letras de fora do ASCII: titulos de nivel 1 a 6,
com recuo de zero a tres espacos e com ou sem os # do fim, um titulo repetido tres vezes,
paragrafos, blocos de codigo com cercas dos dois sinais, com linhas de titulo dentro e com
cercas que nao fecham o bloco (a do outro sinal, a mais curta e a com texto depois), e
linhas que nao sao titulo (sete #, # sem espaco, recuo de quatro espacos). Confere regras,
nunca uma frase pronta: cada titulo fora de bloco de codigo, e so ele, sai na ordem, com a
linha, o nivel, o texto sem os # e os espacos das pontas e a ancora, com -1 e -2 no titulo
repetido; as linhas fora de codigo sao as do documento menos as dos blocos, cercas
incluidas, cada uma com o numero dela, a partir de 1; duas leituras dao o mesmo. Uso:
    python3 -I teste_markdown_comum.py <pasta do markdown_comum.py> <pasta de trabalho nova>
"""
import random
import string
import sys
from pathlib import Path

PECA, TRABALHO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
sys.path.insert(0, str(PECA))
from markdown_comum import ancora, linhas_fora_de_codigo, titulos  # noqa: E402

FALHAS = []
SORTEIO = random.Random(1)
LETRAS = string.ascii_letters + "áçõüéñ"


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

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
