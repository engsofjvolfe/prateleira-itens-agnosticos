"""
A forma de um arquivo JSON ou CSV, tirada dele, num lugar so: ler o arquivo com a forma dele,
refazer o texto dos dados nessa forma, dizer a primeira linha em que o arquivo nao volta igual e
gravar os textos refeitos.

O JSON e o que o json.dumps do Python grava: com o recuo da segunda linha, ou numa linha so; com
o escape fora do ASCII quando o arquivo so tem ASCII e os dados tem algum caractere de fora; e com
o que vem depois do valor, como a quebra de linha do fim. O CSV e o do modulo csv do Python
(virgula, aspas duplas so onde precisa), com o cabecalho na primeira linha, sem coluna repetida,
cada linha com os campos dele, e com a quebra de linha com que o arquivo termina.

Nao se roda: o listas_e_tabelas.py o importa desta pasta. Precisa do extrator_comum.py, do
extrator, na pasta irma ou na mesma pasta.
"""

import collections
import csv
import io
import json
import re
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "extrator", PASTA):  # na prateleira, a pasta irma
    sys.path.insert(0, str(pasta))
from extrator_comum import ErroDeDados, de_json, le_texto, repetidos  # noqa: E402

CODIFICACAO = "utf-8"  # a dos arquivos que se gravam
QUEBRA = "\n"  # a quebra de linha do json.dumps e a que divide um texto em linhas, para dizer onde ele muda
FORA_DO_VALOR = " \t\n\r"  # os espacos que o JSON aceita antes e depois de um valor
RECUO = re.compile(r"[ \t]*")  # o recuo de uma linha de JSON
FINS_DE_LINHA = ("\r\n", "\n", "\r")  # as quebras com que um CSV pode terminar cada linha, a mais longa primeiro


class Json(collections.namedtuple("Json", "texto dados recuo ascii fim")):
    """Um arquivo JSON lido: o texto, os dados, que mudam, e a forma (o recuo, ou None numa linha so, o escape fora
    do ASCII e o que vem depois do valor)."""

    def refeito(self):
        """O texto dos dados de agora, na forma do arquivo."""
        return json.dumps(self.dados, indent=self.recuo, ensure_ascii=self.ascii) + self.fim

    def forma(self):
        """A forma, para a mensagem de erro."""
        return f"o json.dumps com o recuo {self.recuo!r}, o escape fora do ASCII {self.ascii} e o fim {self.fim!r}"


class Csv(collections.namedtuple("Csv", "texto registros fim")):
    """Um arquivo CSV lido: o texto, os registros, que mudam, cada um com a linha do arquivo em que termina e os
    valores, o cabecalho primeiro, e a forma (a quebra de linha)."""

    def refeito(self):
        """O texto dos registros de agora, na forma do arquivo."""
        saida = io.StringIO(newline="")
        csv.writer(saida, lineterminator=self.fim).writerows(valores for _, valores in self.registros)
        return saida.getvalue()

    def forma(self):
        """A forma, para a mensagem de erro."""
        return f"o módulo csv com a quebra de linha {self.fim!r}"


def le_json_na_forma(caminho):
    """O Json do arquivo, com a forma tirada dele; ErroDeDados quando ele nao se le em UTF-8 ou como JSON."""
    texto = le_texto(caminho, exato=True)
    dados = de_json(texto, caminho)
    corpo = texto.rstrip(FORA_DO_VALOR)
    linhas = corpo.split(QUEBRA)
    recuo = RECUO.match(linhas[1]).group() if len(linhas) > 1 else None
    ascii = texto.isascii() and not json.dumps(dados, ensure_ascii=False).isascii()
    return Json(texto, dados, recuo, ascii, texto[len(corpo):])


def le_csv_na_forma(caminho):
    """O Csv do arquivo, com a quebra de linha tirada dele; ErroDeDados quando ele nao se le em UTF-8 ou como CSV,
    nao tem cabecalho, tem uma coluna repetida no cabecalho ou uma linha com outro numero de campos."""
    texto = le_texto(caminho, exato=True)
    leitor, registros = csv.reader(io.StringIO(texto, newline="")), []
    try:
        for valores in leitor:
            registros.append((leitor.line_num, valores))
    except csv.Error as e:
        raise ErroDeDados(f"{caminho}:{leitor.line_num}: não se lê como CSV ({e})")
    if not registros:
        raise ErroDeDados(f"{caminho}: a tabela não tem cabeçalho")
    linha, cabecalho = registros[0]
    mesmas = repetidos(cabecalho)
    if mesmas:
        raise ErroDeDados(f"{caminho}:{linha}: coluna(s) repetida(s) no cabeçalho: {mesmas}")
    for linha, valores in registros[1:]:
        if len(valores) != len(cabecalho):
            raise ErroDeDados(f"{caminho}:{linha}: {len(valores)} campo(s), e não os {len(cabecalho)} do cabeçalho")
    fim = next((f for f in FINS_DE_LINHA if texto.endswith(f)), csv.excel.lineterminator)
    return Csv(texto, registros, fim)


def linha_que_nao_volta(lido):
    """A primeira linha em que o arquivo lido (Json ou Csv) nao volta igual, refeito na forma dele; None quando ele
    volta igual."""
    refeito = lido.refeito()
    if refeito == lido.texto:
        return None
    a, b = lido.texto.split(QUEBRA), refeito.split(QUEBRA)
    return next((n for n, (x, y) in enumerate(zip(a, b), start=1) if x != y), min(len(a), len(b)) + 1)


def grava(textos):
    """Grava cada texto, {arquivo: texto}, no arquivo dele, em UTF-8, com as quebras de linha como estao;
    ErroDeDados, antes de gravar qualquer um, quando um texto nao se escreve em UTF-8."""
    binarios = {}
    for arquivo, texto in textos.items():
        try:
            binarios[arquivo] = texto.encode(CODIFICACAO)
        except UnicodeEncodeError as e:
            raise ErroDeDados(f"{arquivo}: o texto mudado não se escreve em UTF-8 ({e})")
    for arquivo, binario in binarios.items():
        Path(arquivo).write_bytes(binario)
