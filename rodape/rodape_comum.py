"""
O rodape de um documento Markdown, feito de um modelo, num lugar so: ler o modelo, dar o
rodape de um documento, por o rodape no fim de um texto, separar de um texto o rodape que ele
tem no fim e por no leitor de argumentos de uma peca a opcao que da o modelo.

O modelo e um texto Markdown sem codigo, lido sem os espacos e as quebras das pontas, cujos
links valem a partir da pasta dele, como os de qualquer documento; cada link para um arquivo
tem de levar a um que existe. No rodape de um documento, o alvo de cada link para um arquivo
passa a ser o caminho do arquivo a partir da pasta do documento, entre < e > quando tem
espaco ou parenteses, com a ancora que tinha; o link com esquema (como https: ou mailto:) e o
que e so ancora ficam como estao. O texto com o rodape e o texto, sem os espacos e as quebras
do fim, uma linha em branco, o rodape e uma quebra de linha. O rodape que um texto tem no fim
e o do modelo, a partir do comeco de uma linha, com qualquer alvo nos links para arquivos e
com qualquer espaco ou quebra de linha onde o modelo tem um, seguido so de espacos e quebras.

Nao se roda: as pecas o importam da pasta irma "rodape" ou da propria pasta. Precisa do
extrator_comum.py, do extrator, e do markdown_comum.py, do documentos, nas pastas irmas ou
na mesma pasta.
"""

import collections
import re
import sys
from pathlib import Path
from urllib.parse import unquote

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "documentos", PASTA.parent / "extrator", PASTA):  # na prateleira, as pastas irmas
    sys.path.insert(0, str(pasta))
from extrator_comum import ErroDeDados, le_texto  # noqa: E402
from markdown_comum import (ALVO_DE_LINK, ANCORA, ESQUEMA, LINK, QUEBRA, alvo_de_link, alvo_sem_sinais,  # noqa: E402
                            caminho_relativo, texto_fora_de_codigo)

OPCAO = "--rodape"  # a opcao que da o modelo a uma peca
METAVAR = "MODELO"
ANTES = QUEBRA * 2  # entre o texto e o rodape: uma linha em branco
ESPACOS = re.compile(r"\s+")  # onde o rodape no fim de um texto pode ter outros espacos e quebras

# os pedacos do modelo, na ordem, cada um um texto, como vem, ou um Arquivo; e a expressao do rodape no fim de um texto
Modelo = collections.namedtuple("Modelo", "pedacos busca")
# o arquivo de um link do modelo, pelo caminho inteiro, e o resto do alvo: o sinal da ancora e ela, ou nada
Arquivo = collections.namedtuple("Arquivo", "caminho ancora")


def opcao_rodape(leitor, ajuda):
    """Poe no leitor de argumentos (argparse) a opcao que da o arquivo do modelo, com a ajuda dada; nos argumentos
    lidos, ela da o caminho em "rodape", ou None sem ela."""
    leitor.add_argument(OPCAO, type=Path, metavar=METAVAR, help=ajuda)


def busca(pedacos):
    """A expressao do rodape no fim de um texto: os textos dos pedacos, com qualquer espaco ou quebra onde eles tem um,
    e qualquer alvo no lugar de cada Arquivo, a partir do comeco de uma linha e seguido so de espacos e quebras."""
    partes = [f"(?:{ALVO_DE_LINK})" if isinstance(p, Arquivo) else r"\s+".join(map(re.escape, ESPACOS.split(p)))
              for p in pedacos]
    return re.compile(rf"(?m)^{''.join(partes)}\s*\Z")


def le_modelo(caminho):
    """O Modelo do arquivo, ou None sem ele. ErroDeDados, que diz o arquivo, quando ele nao se le em UTF-8, esta vazio,
    tem codigo ou tem um link para um arquivo que nao existe."""
    if caminho is None:
        return None
    texto = le_texto(caminho).strip()
    if not texto:
        raise ErroDeDados(f"{caminho}: o modelo do rodapé está vazio")
    if texto_fora_de_codigo(texto) != QUEBRA.join(texto.splitlines()):
        raise ErroDeDados(f"{caminho}: o modelo do rodapé tem código")
    pedacos, fim, pasta = [], 0, Path(caminho).resolve().parent
    for m in LINK.finditer(texto):
        alvo = alvo_sem_sinais(m.group(1))
        if ESQUEMA.match(alvo) or alvo.startswith(ANCORA):
            continue  # o link externo e o so de ancora ficam no texto, como estao
        nome, sinal, ancora = alvo.partition(ANCORA)
        arquivo = (pasta / unquote(nome)).resolve()
        if not arquivo.exists():
            raise ErroDeDados(f"{caminho}: o link {alvo} leva a um arquivo que não existe: {arquivo}")
        pedacos += [texto[fim:m.start(1)], Arquivo(arquivo, sinal + ancora)]
        fim = m.end(1)
    pedacos.append(texto[fim:])
    return Modelo(pedacos, busca(pedacos))


def rodape(modelo, documento):
    """O rodape do documento: o modelo, com o alvo de cada link para um arquivo a partir da pasta do documento."""
    pasta = Path(documento).resolve().parent
    return "".join(alvo_de_link(caminho_relativo(p.caminho, pasta) + p.ancora) if isinstance(p, Arquivo) else p
                   for p in modelo.pedacos)


def com_rodape(texto, modelo, documento):
    """O texto com o rodape do documento no fim: o texto, sem os espacos e as quebras do fim, uma linha em branco, o
    rodape e uma quebra de linha; sem texto, so o rodape e a quebra; sem modelo, o texto como vem."""
    if modelo is None:
        return texto
    corpo = texto.rstrip()
    return (corpo + ANTES if corpo else "") + rodape(modelo, documento) + QUEBRA


def separa(texto, modelo):
    """(corpo, linha): o texto sem o rodape do modelo que ele tem no fim, sem os espacos e as quebras de antes do
    rodape e com uma quebra de linha no fim, e a linha em que o rodape comeca; sem rodape no fim, ou sem modelo, o
    texto como vem e None."""
    achado = modelo.busca.search(texto) if modelo is not None else None
    if achado is None:
        return texto, None
    corpo = texto[:achado.start()].rstrip()
    return (corpo + QUEBRA if corpo else ""), texto.count(QUEBRA, 0, achado.start()) + 1
