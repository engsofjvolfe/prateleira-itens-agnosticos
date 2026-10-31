"""
Le um texto em colunas separadas por tabulacao (TSV), com o cabecalho dado: a primeira
linha e o cabecalho, e cada linha seguinte da um valor por coluna. As linhas em branco nao
contam, e os espacos das pontas de cada valor saem; aspas sao texto como outro qualquer. A
linha com menos colunas que o cabecalho tem vazias as que faltam, no fim: um editor que
tira os espacos do fim da linha tira tambem as tabulacoes das colunas vazias do fim. A
leitura do arquivo fica com o programa que importa o modulo: aqui chega o texto, com o nome
que as mensagens de erro usam. A coluna repetida e achada pelo extrator_comum.py, do
extrator, na pasta irma "extrator" ou na mesma pasta.
"""
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "extrator", PASTA):  # na prateleira, o extrator fica na pasta irma
    sys.path.insert(0, str(pasta))
from extrator_comum import repetidos  # noqa: E402

SEPARADOR = "\t"  # o que separa uma coluna da seguinte


class ErroDeTabela(ValueError):
    """Texto fora da forma da tabela; a mensagem diz o nome e a linha."""


def ler(texto, cabecalho, nome):
    """[(numero da linha, {coluna: valor})] das linhas depois do cabecalho, contadas a partir
    de 1, como num editor; sem as linhas em branco, sem os espacos das pontas de cada valor e
    com vazias as colunas que faltam no fim de uma linha. ErroDeTabela, que diz o nome e a
    linha, quando a primeira linha nao e o cabecalho dado ou uma linha tem mais colunas que
    ele. Cabecalho vazio ou com coluna repetida e erro de uso (ValueError)."""
    colunas = list(cabecalho)
    if not colunas or repetidos(colunas):
        raise ValueError(f"cabeçalho vazio ou com coluna repetida: {colunas}")
    linhas = texto.splitlines()
    if not linhas or [c.strip() for c in linhas[0].split(SEPARADOR)] != colunas:
        raise ErroDeTabela(f"{nome}, linha 1: o cabeçalho deve ser {', '.join(colunas)}, separados por tabulação")
    saida = []
    for n, linha in enumerate(linhas[1:], 2):
        valores = [v.strip() for v in linha.split(SEPARADOR)]
        if not "".join(valores):
            continue
        if len(valores) > len(colunas):
            raise ErroDeTabela(f"{nome}, linha {n}: {len(valores)} coluna(s); a tabela tem {len(colunas)}")
        saida.append((n, dict(zip(colunas, valores + [""] * (len(colunas) - len(valores))))))
    return saida
