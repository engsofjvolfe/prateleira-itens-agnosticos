"""
Os padroes proibidos, num lugar so, para toda peca que confere um texto contra eles: ler as
regras dos arquivos de padroes proibidos, cada um conferido contra o molde dele, e dizer as
regras em que um texto cai.

Nao se roda: o confere_forma.py e as outras pecas o importam. Usa so a biblioteca padrao e o
extrator_comum.py, da peca extrator, na pasta irma "extrator" ou na mesma pasta.
"""
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "extrator", PASTA):  # na prateleira, a peca extrator fica na pasta irma
    sys.path.insert(0, str(pasta))
from extrator_comum import ErroDeDados, compila, le_conferido, repetidos  # noqa: E402

MOLDE_DOS_PROIBIDOS = PASTA / "esquemas" / "proibidos.schema.json"  # o de cada arquivo de padroes proibidos


def regras_proibidas(caminhos):
    """[(nome, padrao, exceto)] das regras dos arquivos de padroes proibidos, na ordem dos
    arquivos e, em cada um, na da lista, com as expressoes compiladas (exceto e None na regra
    sem ele); cada arquivo e conferido contra o molde dele, e o erro diz o arquivo e a regra.
    Duas regras com o mesmo nome, no mesmo arquivo ou em dois, sao erro."""
    regras, lugares = [], []
    for caminho in caminhos:
        for k, regra in enumerate(le_conferido(caminho, MOLDE_DOS_PROIBIDOS)["proibidos"]):
            onde = f"{caminho}: /proibidos/{k}"
            exceto = compila(regra["exceto"], f"{onde}/exceto") if "exceto" in regra else None
            regras.append((regra["nome"], compila(regra["padrao"], f"{onde}/padrao"), exceto))
            lugares.append(onde)
    nomes = [nome for nome, _, _ in regras]
    mesmos = [f"{nome!r} em {', '.join(lugar for n, lugar in zip(nomes, lugares) if n == nome)}"
              for nome in repetidos(nomes)]
    if mesmos:
        raise ErroDeDados(f"padrão proibido com o mesmo nome em mais de uma regra: {'; '.join(mesmos)}")
    return regras


def achados(texto, regras):
    """Os nomes das regras em que o texto cai, na ordem delas: o padrao casa com ele e o
    exceto, quando a regra o tem, nao casa."""
    return [nome for nome, padrao, exceto in regras
            if padrao.search(texto) and not (exceto and exceto.search(texto))]
