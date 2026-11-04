"""
Os campos que se montam por um modelo, num lugar so: ler os modelos, dizer o que vai entre dois
itens e montar, em qualquer nivel de uma entrada, cada campo que tem um modelo.

O modelo e o texto do item e, opcional, o texto que vai entre dois itens, cada um o texto de um
arquivo em UTF-8, com cada quebra de linha como "\\n" e sem a quebra do fim. Os campos do modelo
sao os {campo} que a expressao CAMPO, do extrator_comum, acha no texto do item.

O campo montado vem como uma lista de itens, um ou mais, cada um um objeto com os campos do
modelo, e so eles, cada valor um texto ou um numero inteiro. Cada item vira o texto do item com
cada {campo} trocado pelo valor dele, e os itens se juntam um na linha seguinte ao outro, com as
linhas do texto entre no meio, quando o modelo o tem. O campo que nao e uma lista de itens, o
item sem um campo do modelo, com um campo que o modelo nao usa e o valor de outro tipo sao
problema, com o caminho do valor.

Nao se roda: o listas_e_tabelas.py e o configuracao.py o importam desta pasta. Precisa do
extrator_comum.py, do extrator, na pasta irma ou na mesma pasta.
"""

import collections
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "extrator", PASTA):  # na prateleira, a pasta irma
    sys.path.insert(0, str(pasta))
from extrator_comum import CAMPO, ErroDeDados, do_tipo, le_texto, preenche  # noqa: E402

QUEBRA = "\n"  # a quebra de linha dos modelos e a que junta os itens de um campo montado
TIPOS_DO_VALOR = ("string", "integer")  # os tipos do JSON Schema que o valor de um campo de item pode ter

# o texto do item, o texto entre dois itens (None sem ele) e os campos do item, em ordem
Modelo = collections.namedtuple("Modelo", "item entre campos")


def sem_quebra_do_fim(texto):
    """O texto sem a quebra de linha do fim, quando ele tem uma."""
    return texto[:-len(QUEBRA)] if texto.endswith(QUEBRA) else texto


def le_modelo(item, entre=None):
    """O Modelo dos arquivos do item e do texto entre (ou None sem ele); ErroDeDados quando um deles nao se le em
    UTF-8 ou o item nao tem texto."""
    texto = sem_quebra_do_fim(le_texto(item))
    if not texto.strip():
        raise ErroDeDados(f"{item}: o item do modelo não tem texto")
    texto_entre = None if entre is None else sem_quebra_do_fim(le_texto(entre))
    return Modelo(texto, texto_entre, sorted(set(CAMPO.findall(texto))))


def juncao(modelo):
    """O que vai entre dois itens montados pelo modelo: uma quebra de linha, com as linhas do texto entre e outra
    quebra no meio, quando o modelo o tem."""
    return QUEBRA if modelo.entre is None else QUEBRA + modelo.entre + QUEBRA


def monta(itens, modelo, onde):
    """(valor, problemas [(caminho, motivo)]) do campo: o texto dos itens, cada um pelo modelo, juntos; com
    problema, os itens como vem. onde e o caminho do campo."""
    if not isinstance(itens, list) or not itens or not all(isinstance(item, dict) for item in itens):
        return itens, [(onde, "não é uma lista de itens, objetos com os campos do modelo, com um item ou mais")]
    problemas = []
    for k, item in enumerate(itens):
        problemas += [(f"{onde}/{k}/{c}", "falta: o modelo usa esse campo") for c in modelo.campos if c not in item]
        problemas += [(f"{onde}/{k}/{c}", "o modelo não usa esse campo") for c in item if c not in modelo.campos]
        problemas += [(f"{onde}/{k}/{c}", "não é texto nem número inteiro") for c, v in item.items()
                      if c in modelo.campos and not any(do_tipo(v, tipo) for tipo in TIPOS_DO_VALOR)]
    if problemas:
        return itens, problemas
    return juncao(modelo).join(preenche(modelo.item, **item) for item in itens), []


def montada(valor, modelos, onde):
    """(valor, problemas) do valor de uma entrada com cada campo que tem modelo ({campo: Modelo}), em qualquer nivel,
    trocado pelo texto dele. onde e o caminho do valor."""
    if isinstance(valor, list):
        partes = [montada(v, modelos, f"{onde}/{k}") for k, v in enumerate(valor)]
        return [v for v, _ in partes], [p for _, ps in partes for p in ps]
    if not isinstance(valor, dict):
        return valor, []
    saida, problemas = {}, []
    for chave, v in valor.items():
        if chave in modelos:
            saida[chave], erros = monta(v, modelos[chave], f"{onde}/{chave}")
        else:
            saida[chave], erros = montada(v, modelos, f"{onde}/{chave}")
        problemas += erros
    return saida, problemas
