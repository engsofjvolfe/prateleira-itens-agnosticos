"""
A configuracao do listas-e-tabelas, num lugar so: le-la pelo molde dela,
esquemas/listas-e-tabelas.schema.json, com os arquivos a partir da pasta dela e os modelos ja
lidos, e conferir o que o molde nao ve: o campo montado por um modelo que ela nao tem e o arquivo
que e de lista e de tabela ao mesmo tempo.

Nao se roda: o listas_e_tabelas.py o importa desta pasta. Precisa do campos_montados.py, desta
pasta, e do extrator_comum.py, do extrator, na pasta irma ou na mesma pasta.
"""

import collections
import os
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "extrator", PASTA):  # na prateleira, a pasta irma; e esta, a dos modulos da peca
    sys.path.insert(0, str(pasta))
from campos_montados import le_modelo  # noqa: E402
from extrator_comum import ErroDeDados, le_conferido  # noqa: E402

MOLDE = PASTA / "esquemas" / "listas-e-tabelas.schema.json"  # o molde da configuracao
LISTAS, TABELAS = "listas", "tabelas"  # os dois grupos da configuracao e das mudancas, como nos moldes

Lista = collections.namedtuple("Lista", "arquivo lista unico modelos")  # modelos: {campo montado: Modelo}
Tabela = collections.namedtuple("Tabela", "arquivo chave")


def da_pasta(pasta, arquivo):
    """O caminho do arquivo a partir da pasta, sem os "." e ".." do meio."""
    return Path(os.path.normpath(Path(pasta) / arquivo))


def le_configuracao(caminho):
    """(listas, tabelas, arquivos dos modelos): {nome: Lista} e {nome: Tabela}, com os arquivos a partir da pasta da
    configuracao; ErroDeDados quando ela ou um modelo nao servem, quando uma lista monta um campo por um modelo que
    ela nao tem ou quando um arquivo e de lista e de tabela."""
    conf = le_conferido(caminho, MOLDE)
    pasta = Path(caminho).parent
    modelos, arquivos = {}, []
    for nome, m in conf.get("modelos", {}).items():
        item, entre = da_pasta(pasta, m["item"]), (da_pasta(pasta, m["entre"]) if "entre" in m else None)
        modelos[nome] = le_modelo(item, entre)
        arquivos += [a for a in (item, entre) if a is not None]
    listas = {}
    for nome, lista in conf.get(LISTAS, {}).items():
        montados = lista.get("montados", {})
        faltam = sorted(set(montados.values()) - modelos.keys())
        if faltam:
            raise ErroDeDados(f"{caminho}: a lista {nome} monta campos por modelo(s) que a configuração não tem: "
                              f"{faltam}")
        listas[nome] = Lista(da_pasta(pasta, lista["arquivo"]), lista["lista"], lista.get("unico"),
                             {c: modelos[m] for c, m in montados.items()})
    tabelas = {nome: Tabela(da_pasta(pasta, t["arquivo"]), t["chave"]) for nome, t in conf.get(TABELAS, {}).items()}
    nos_dois = sorted({str(lista.arquivo) for lista in listas.values()} & {str(t.arquivo) for t in tabelas.values()})
    if nos_dois:
        raise ErroDeDados(f"{caminho}: arquivo(s) de lista e de tabela ao mesmo tempo: {nos_dois}")
    return listas, tabelas, arquivos
