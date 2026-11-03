"""
O que os scripts que geram um documento a partir de dados fazem do mesmo jeito antes de
grava-lo: ler o cabecalho que o projeto escreve (o titulo e a abertura, por exemplo), que nao
pode estar vazio; conferir que o arquivo do documento serve, sem ser um dos arquivos de
entrada, que ele gravaria por cima, nem uma pasta; e montar o texto, o cabecalho e os
blocos, como vem, com uma linha em branco entre um e o seguinte e uma quebra de linha no fim.

Nao se roda: as pecas o importam da pasta irma "grava-ou-confere" ou da propria pasta.
Precisa do extrator_comum.py, do extrator, na pasta irma "extrator" ou na mesma pasta.
"""

import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "extrator", PASTA):  # na prateleira, o extrator fica na pasta irma
    sys.path.insert(0, str(pasta))
from extrator_comum import ErroDeDados, le_texto  # noqa: E402

QUEBRA = "\n"  # o fim do documento
ENTRE_BLOCOS = "\n\n"  # a linha em branco entre dois blocos do documento


def le_cabecalho(caminho):
    """O cabecalho do documento, sem os espacos e as quebras do fim; ErroDeDados, que diz o arquivo, quando ele nao
    se le em UTF-8 ou esta vazio."""
    texto = le_texto(caminho).rstrip()
    if not texto:
        raise ErroDeDados(f"{caminho}: o cabeçalho está vazio")
    return texto


def confere_destino(destino, entradas):
    """ErroDeDados quando o arquivo do documento nao serve: e um dos arquivos de entrada, pelo caminho inteiro, ou
    existe e nao e um arquivo. A entrada que nao veio (None), como a de uma opcao que nao se deu, nao conta."""
    destino = Path(destino)
    if destino.resolve() in {Path(e).resolve() for e in entradas if e is not None}:
        raise ErroDeDados(f"o documento é um dos arquivos de entrada: {destino}")
    if destino.exists() and not destino.is_file():
        raise ErroDeDados(f"o documento não é um arquivo: {destino}")


def em_blocos(cabecalho, blocos):
    """O texto do documento: o cabecalho e os blocos, como vem, com uma linha em branco entre um e o seguinte e uma
    quebra de linha no fim."""
    return ENTRE_BLOCOS.join([cabecalho, *blocos]) + QUEBRA
