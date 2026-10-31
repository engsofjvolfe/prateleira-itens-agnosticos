"""
Diz quais arquivos de uma pasta tem texto em comum com os arquivos de outras pastas. Texto
em comum e uma sequencia de N palavras seguidas igual nos dois arquivos. As palavras sao
comparadas sem diferenca de maiuscula, de acento escrito de um jeito ou de outro (as formas
sao juntadas pela NFC) e do que fica entre elas: espaco, quebra de linha ou pontuacao. A NFC
vem do texto_comum.py, do extrator, na pasta irma "extrator" ou na mesma pasta.

Texto e o arquivo que se le em UTF-8 e nao tem o byte zero. Um arquivo examinado que nao e
texto sai no relatorio com "não" na coluna texto, nunca pulado calado; um comparado que nao
e texto so e contado. Um arquivo nunca e comparado com ele mesmo, e o relatorio nunca e
lido. Nome de arquivo ou de pasta que casa com um padrao de --pular fica de fora, com tudo
o que tiver dentro, nos dois lados. Com --lista, sao examinados so os arquivos dela, um
caminho por linha, a partir da pasta examinada ("-" le a lista da entrada padrao).

O relatorio e um TSV com cabecalho e uma linha por arquivo examinado, em ordem de caminho:
arquivo; texto ("sim" ou "não"); sequencias (as de N palavras do arquivo, cada uma contada
uma vez); em_comum (quantas delas aparecem em algum arquivo comparado); mais_parecido (o
arquivo comparado que tem mais delas; no empate, o primeiro na ordem das pastas e dos
caminhos); em_comum_com_ele (quantas ele tem).

Sai com codigo 0 quando todo arquivo examinado e texto e nenhum tem texto em comum; 1
quando algum tem texto em comum ou nao e texto; 2 quando um argumento ou a lista nao serve,
e entao nao grava nada.

Uso:
    python3 -I texto_em_comum.py <pasta examinada> <pasta comparada> [<pasta comparada> ...]
        --palavras <N> --saida <relatorio.tsv> [--pular <padrao>]... [--lista <arquivo ou ->]
"""

import argparse
import csv
import fnmatch
import os
import re
import sys
from collections import Counter
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "extrator", PASTA):  # na prateleira, o extrator fica na pasta irma
    sys.path.insert(0, str(pasta))
from texto_comum import nfc  # noqa: E402

PALAVRA = re.compile(r"[^\W_]+")  # letras e algarismos seguidos
COLUNAS = ["arquivo", "texto", "sequencias", "em_comum", "mais_parecido", "em_comum_com_ele"]
SIM, NAO = "sim", "não"
COMECO = 65536  # bytes lidos primeiro: o byte zero logo no comeco ja diz que nao e texto


class ErroDeUso(Exception):
    """Argumento ou lista que nao serve: nada e gravado."""


def texto_de(caminho):
    """O texto do arquivo, ou None quando ele nao e texto (nao se le em UTF-8, tem o byte
    zero ou nao se abre)."""
    try:
        with open(caminho, "rb") as f:
            dados = f.read(COMECO)
            if b"\0" in dados:
                return None
            dados += f.read()
    except OSError:
        return None
    if b"\0" in dados:
        return None
    try:
        return dados.decode("utf-8")
    except UnicodeDecodeError:
        return None


def sequencias(texto, n):
    """As sequencias de n palavras seguidas do texto, cada uma uma vez."""
    palavras = PALAVRA.findall(nfc(texto.casefold()))
    return {" ".join(palavras[i:i + n]) for i in range(len(palavras) - n + 1)}


def pulado(relativo, pular):
    """Se alguma parte do caminho casa com um dos padroes."""
    return any(fnmatch.fnmatchcase(parte, padrao) for parte in Path(relativo).parts for padrao in pular)


def em_ordem(caminhos, pasta):
    return sorted(set(caminhos), key=lambda p: p.relative_to(pasta).as_posix())


def da_pasta(pasta, pular):
    """Os arquivos da pasta e das subpastas; atalhos para pastas nao sao seguidos."""
    achados = []
    for raiz, pastas, nomes in os.walk(pasta):
        pastas[:] = [p for p in pastas if not pulado(p, pular)]
        achados += [Path(raiz) / nome for nome in nomes if not pulado(nome, pular)]
    return em_ordem(achados, pasta)


def da_lista(pasta, lista, pular):
    """Os arquivos nomeados na lista, a partir da pasta; linhas vazias nao contam."""
    try:
        texto = sys.stdin.read() if lista == "-" else Path(lista).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise ErroDeUso(f"a lista não se lê: {lista}: {e}")
    caminhos = []
    for numero, nome in enumerate(texto.splitlines(), 1):
        if not nome:
            continue
        relativo = Path(nome)
        if relativo.is_absolute() or ".." in relativo.parts or not (pasta / relativo).is_file():
            raise ErroDeUso(f"{lista}, linha {numero}: não é um arquivo dentro de {pasta}: {nome}")
        if not pulado(relativo, pular):
            caminhos.append(pasta / relativo)
    return em_ordem(caminhos, pasta)


def comparados_de(pastas, pular, fora):
    """Os arquivos das pastas comparadas, na ordem das pastas e dos caminhos, cada um uma vez
    (o mesmo arquivo por dois caminhos conta no primeiro); os de fora nao entram."""
    comparados, vistos = [], set(fora)
    for pasta in pastas:
        for caminho in da_pasta(pasta, pular):
            if caminho.resolve() not in vistos:
                vistos.add(caminho.resolve())
                comparados.append(caminho)
    return comparados


def indice(comparados, n):
    """{sequencia: [posicoes dos arquivos comparados que a tem]} e quantos nao sao texto."""
    achadas, nao_texto = {}, 0
    for posicao, caminho in enumerate(comparados):
        texto = texto_de(caminho)
        if texto is None:
            nao_texto += 1
            continue
        for s in sequencias(texto, n):
            achadas.setdefault(s, []).append(posicao)
    return achadas, nao_texto


def valores_de(caminho, achadas, proprio, n):
    """(sequencias, em comum, posicao do mais parecido ou None, em comum com ele) de um arquivo
    examinado, ou None quando ele nao e texto; proprio e a posicao dele entre os comparados."""
    texto = texto_de(caminho)
    if texto is None:
        return None
    contagem, em_comum = Counter(), 0
    seqs = sequencias(texto, n)
    for s in seqs:
        outros = [p for p in achadas.get(s, ()) if p != proprio]
        em_comum += bool(outros)
        contagem.update(outros)
    mais = min(contagem, key=lambda p: (-contagem[p], p)) if contagem else None
    return len(seqs), em_comum, mais, contagem[mais] if contagem else 0


def argumentos(argv):
    p = argparse.ArgumentParser(description="Diz quais arquivos de uma pasta têm texto em comum com os de outras.")
    p.add_argument("examinada", type=Path)
    p.add_argument("comparadas", type=Path, nargs="+")
    p.add_argument("--palavras", type=int, required=True, help="quantas palavras seguidas formam uma sequência")
    p.add_argument("--saida", type=Path, required=True, help="o relatório, em TSV")
    p.add_argument("--pular", action="append", default=[], help="padrão de nome que fica de fora; pode repetir")
    p.add_argument("--lista", help="arquivo com os caminhos a examinar, ou - para a entrada padrão")
    a = p.parse_args(argv)
    if a.palavras < 1:
        raise ErroDeUso(f"--palavras precisa ser 1 ou mais: {a.palavras}")
    for pasta in (a.examinada, *a.comparadas):
        if not pasta.is_dir():
            raise ErroDeUso(f"a pasta não existe: {pasta}")
    if not a.saida.parent.is_dir():
        raise ErroDeUso(f"a pasta do relatório não existe: {a.saida.parent}")
    return a


def main(argv=None):
    try:
        a = argumentos(argv)
        examinados = (da_lista(a.examinada, a.lista, a.pular) if a.lista is not None
                      else da_pasta(a.examinada, a.pular))
    except ErroDeUso as e:
        print(f"ERRO: {e}")
        return 2
    fora = {a.saida.resolve()}
    examinados = [c for c in examinados if c.resolve() not in fora]
    comparados = comparados_de(a.comparadas, a.pular, fora)
    achadas, nao_texto_comparados = indice(comparados, a.palavras)
    posicoes = {caminho.resolve(): posicao for posicao, caminho in enumerate(comparados)}
    linhas, com_texto_em_comum, nao_texto = [], 0, 0
    for caminho in examinados:
        relativo = caminho.relative_to(a.examinada).as_posix()
        valores = valores_de(caminho, achadas, posicoes.get(caminho.resolve()), a.palavras)
        if valores is None:
            nao_texto += 1
            linhas.append([relativo, NAO, "", "", "", ""])
            continue
        total, em_comum, mais, com_ele = valores
        com_texto_em_comum += em_comum > 0
        linhas.append([relativo, SIM, total, em_comum, "" if mais is None else comparados[mais], com_ele])
    with open(a.saida, "w", encoding="utf-8", newline="") as f:
        escrita = csv.writer(f, delimiter="\t", lineterminator="\n")
        escrita.writerow(COLUNAS)
        escrita.writerows(linhas)
    print(f"{len(examinados)} arquivo(s) examinado(s): {com_texto_em_comum} com texto em comum, "
          f"{nao_texto} que não são texto; {len(comparados)} arquivo(s) comparado(s), "
          f"{nao_texto_comparados} que não são texto")
    return 0 if com_texto_em_comum == 0 and nao_texto == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
