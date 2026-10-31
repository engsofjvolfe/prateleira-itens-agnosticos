"""Testa o linhas_longas.py com pastas e arquivos inventados.

O limite, o padrao do nome, os nomes das pastas e dos arquivos e o tamanho, o texto e a
quebra de cada linha sao sorteados, sempre os mesmos, porque a semente e fixa (outra vem com
--semente), com letras de fora do ASCII, que sao um caractere so e mais de um byte. O teste
confere regras, nunca uma frase pronta:
  - cada linha acima do limite, e so ela, sai numa linha ERRO com o arquivo e o numero da
    linha, em ordem de arquivo e de linha, e o ERRO diz o tamanho dela; depois delas so sai
    o resumo; a linha do tamanho do limite passa;
  - o tamanho e o numero de caracteres, sem a quebra do fim, seja ela LF ou CR LF, e a
    ultima linha conta tambem sem quebra no fim;
  - o arquivo dado e conferido qualquer que seja o nome; numa pasta, so os arquivos que
    seguem o padrao, tambem nas subpastas e na subpasta cujo nome segue o padrao; o arquivo
    dado e achado numa pasta e conferido uma vez so;
  - o resumo diz, nessa ordem, o numero de arquivos conferidos, o de linhas acima do limite e
    o limite;
  - o codigo de saida e 1 com linha acima do limite e 0 sem nenhuma;
  - o limite zero ou negativo, o caminho que nao existe e o arquivo que nao se le em UTF-8
    saem com 2 e so com uma linha ERRO, que diz o limite ou o caminho; o limite que nao e um
    numero inteiro sai com 2, sem nada na saida padrao;
  - duas rodadas dao a mesma saida.
Uso:
    python3 -I teste_linhas_longas.py <pasta do linhas_longas.py> <pasta de trabalho nova> [--semente N]
"""
import argparse
import random
import re
import subprocess
import sys
from pathlib import Path

LEITOR = argparse.ArgumentParser(description="Testa o linhas_longas.py com pastas e arquivos inventados.")
LEITOR.add_argument("peca", type=Path, help="a pasta do linhas_longas.py")
LEITOR.add_argument("trabalho", type=Path, help="uma pasta de trabalho nova ou vazia")
LEITOR.add_argument("--semente", type=int, default=3, help="a semente do sorteio")
ARGS = LEITOR.parse_args()
PROGRAMA = ARGS.peca.resolve() / "linhas_longas.py"
TRABALHO = ARGS.trabalho.resolve()
if TRABALHO.exists() and (not TRABALHO.is_dir() or any(TRABALHO.iterdir())):
    print(f"ERRO: a pasta de trabalho precisa ser nova ou estar vazia: {TRABALHO}")
    sys.exit(2)

SORTE = random.Random(ARGS.semente)
FALHAS = []
USADOS = set()  # os nomes ja sorteados, para que nenhum se repita
CODIFICACAO = "utf-8"  # a dos arquivos e a da saida
LATIN = "latin-1"  # a do arquivo que nao se le em UTF-8
LETRAS = "abcdefghijklmnopqrstuvwxyz"
ACENTUADAS = "áéíóúâêôãõçàüñ"  # um caractere e dois bytes em UTF-8; em latin-1, um byte que o UTF-8 nao le
QUEBRAS = ("\n", "\r\n")  # as quebras de linha de um arquivo, que nao contam no tamanho
LINHA_DE_ERRO = re.compile(r"^ERRO (.+):(\d+): (.+)$")  # ERRO arquivo:linha: motivo
NUMERO = re.compile(r"-?\d+")


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)


def texto(tamanho, espacos=True):
    """Um texto sorteado de tantos caracteres, com uma letra com acento quando tem algum, e com
    espacos, quando pedido."""
    if tamanho == 0:
        return ""
    letras = [SORTE.choice(LETRAS + ACENTUADAS + (" " if espacos else "")) for _ in range(tamanho - 1)]
    letras.insert(SORTE.randrange(tamanho), SORTE.choice(ACENTUADAS))
    return "".join(letras)


def nome():
    """Um nome sorteado, sem espaco, que ainda nao saiu."""
    while True:
        novo = texto(SORTE.randint(3, 7), espacos=False)
        if novo not in USADOS:
            USADOS.add(novo)
            return novo


LIMITE = SORTE.randint(8, 40)
EXTENSAO, OUTRA = nome(), nome()  # a dos arquivos que seguem o padrao e a dos que nao seguem
PADRAO = f"*.{EXTENSAO}"
ARVORE = TRABALHO / "arvore"
# a pasta, subpastas e uma subpasta cujo nome segue o padrao
PASTAS = [ARVORE, ARVORE / nome(), ARVORE / nome() / nome(), ARVORE / f"{nome()}.{EXTENSAO}"]
CONFERIDOS = {}  # {caminho: [tamanho de cada linha]} de cada arquivo que o linhas_longas.py confere


def tamanhos():
    """Os tamanhos sorteados das linhas de um arquivo, muitos em volta do limite."""
    return [SORTE.choice([LIMITE - 1, LIMITE, LIMITE + 1, SORTE.randint(0, 2 * LIMITE)])
            for _ in range(SORTE.randint(1, 6))]


def grava(caminho, linhas, quebra=None, fim=None):
    """Grava no caminho uma linha de cada tamanho, separadas pela quebra dada ou sorteada, com ou
    sem quebra depois da ultima, como pedido ou sorteado; devolve o caminho."""
    quebra = SORTE.choice(QUEBRAS) if quebra is None else quebra
    fim = SORTE.random() < 0.5 if fim is None else fim
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes((quebra.join(texto(t) for t in linhas) + (quebra if fim else "")).encode(CODIFICACAO))
    return caminho


def conferido(pasta, linhas, quebra=None, fim=None):
    """Grava na pasta um arquivo que segue o padrao, que o linhas_longas.py confere."""
    CONFERIDOS[grava(pasta / f"{nome()}.{EXTENSAO}", linhas, quebra, fim)] = linhas


def roda(*argumentos):
    """(codigo de saida, linhas da saida padrao) do linhas_longas.py com os argumentos."""
    r = subprocess.run([sys.executable, "-I", str(PROGRAMA), *map(str, argumentos)], capture_output=True,
                       encoding=CODIFICACAO)
    return r.returncode, r.stdout.splitlines()


def numeros(linha):
    return [int(n) for n in NUMERO.findall(linha)]


def confere_saida(rodada, limite, alvos):
    """Confere a saida do linhas_longas.py com o limite e os alvos, que levam a todos os conferidos."""
    codigo, saida = roda(limite, PADRAO, *alvos)
    esperados = [(c, n, t) for c in sorted(CONFERIDOS) for n, t in enumerate(CONFERIDOS[c], 1) if t > limite]
    achados = [m.groups() for m in map(LINHA_DE_ERRO.match, saida) if m]
    alinhados = [(Path(c), int(n)) for c, n, _ in achados] == [(c, n) for c, n, _ in esperados]
    confere(alinhados, f"{rodada}: cada linha acima do limite, e só ela, sai numa linha ERRO com o arquivo e o "
                       f"número dela, em ordem: {achados} em vez de {esperados}")
    if alinhados:
        confere(all(t in numeros(motivo) for (*_, motivo), (*_, t) in zip(achados, esperados)),
                f"{rodada}: cada ERRO diz o tamanho da linha: {achados}")
    resumo = [len(CONFERIDOS), len(esperados), limite]
    confere(len(saida) == len(achados) + 1 and numeros(saida[-1]) == resumo,
            f"{rodada}: depois das linhas ERRO, só o resumo, com {resumo}: {saida[len(achados):]}")
    confere(codigo == (1 if esperados else 0), f"{rodada}: sai com {1 if esperados else 0}, e não com {codigo}")
    confere(roda(limite, PADRAO, *alvos) == (codigo, saida), f"{rodada}: duas rodadas dão a mesma saída")


def confere_que_nao_serve(rodada, argumentos, diz=None):
    """A rodada que nao serve sai com 2 e so com uma linha ERRO, que diz o que nao serve, ou,
    sem o que dizer, sem nada na saida padrao."""
    codigo, saida = roda(*argumentos)
    confere(codigo == 2, f"{rodada}: sai com 2, e não com {codigo}")
    if diz is None:
        confere(saida == [], f"{rodada}: nada na saída padrão: {saida}")
    else:
        confere(len(saida) == 1 and saida[0].startswith("ERRO") and diz in saida[0],
                f"{rodada}: só uma linha ERRO, que diz {diz}: {saida}")


# ---- os arquivos: em cada pasta, os que seguem o padrao, conferidos, e um que nao segue, com linha longa ----

for pasta in PASTAS:
    for _ in range(SORTE.randint(1, 3)):
        conferido(pasta, tamanhos())
    grava(pasta / f"{nome()}.{OUTRA}", [2 * LIMITE, *tamanhos()])
for quebra in QUEBRAS:  # com as duas quebras, a linha do tamanho do limite e a de um a mais
    linhas = [LIMITE, LIMITE + 1, *tamanhos()]
    SORTE.shuffle(linhas)
    conferido(SORTE.choice(PASTAS), linhas, quebra)
conferido(SORTE.choice(PASTAS), [*tamanhos(), LIMITE + 1], fim=False)  # a ultima linha, longa, sem quebra no fim
REPETIDO = SORTE.choice(list(CONFERIDOS))  # dado tambem como arquivo
linhas = [LIMITE + 1, *tamanhos()]
SOLTO = grava(TRABALHO / "soltos" / f"{nome()}.{OUTRA}", linhas)  # dado como arquivo, sem seguir o padrao
CONFERIDOS[SOLTO] = linhas
ALVOS = SORTE.sample([ARVORE, SOLTO, REPETIDO], 3)
ILEGIVEL = TRABALHO / "ilegiveis" / f"{nome()}.{EXTENSAO}"
ILEGIVEL.parent.mkdir()
ILEGIVEL.write_bytes(texto(LIMITE).encode(LATIN))
try:
    ILEGIVEL.read_bytes().decode(CODIFICACAO)
    confere(False, f"o arquivo em latin-1 não se lê em UTF-8: {ILEGIVEL}")
except UnicodeDecodeError:
    pass

# ---- as rodadas ----

confere_saida("com linhas acima do limite", LIMITE, ALVOS)
confere_saida("sem linha acima do limite", max(t for linhas in CONFERIDOS.values() for t in linhas), ALVOS)
for limite in (0, -SORTE.randint(1, LIMITE)):
    confere_que_nao_serve(f"o limite {limite}", (limite, PADRAO, *ALVOS), str(limite))
for limite in (nome(), f"{LIMITE}.{SORTE.randint(1, 9)}"):
    confere_que_nao_serve(f"o limite {limite}", (limite, PADRAO, *ALVOS))
FALTA = TRABALHO / nome()
confere_que_nao_serve("o caminho que não existe", (LIMITE, PADRAO, *ALVOS, FALTA), str(FALTA))
confere_que_nao_serve("o arquivo que não se lê em UTF-8", (LIMITE, PADRAO, *ALVOS, ILEGIVEL), str(ILEGIVEL))

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s) (semente {ARGS.semente})")
sys.exit(1 if FALHAS else 0)
