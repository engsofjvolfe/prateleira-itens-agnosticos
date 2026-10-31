"""
A tabela dos destinos: o que cada pedaco do destino das analises nomeia. O destino de um
trecho e o campo do papel "destino", lido numa forma que da a lista dos pedacos dele (como
a forma "pedacos" do analises.py). Cada pedaco e escrito a mao, e o mesmo nome pode
aparecer escrito de varios jeitos; a tabela da a cada jeito os ids que ele nomeia, e as
analises nao mudam.

A tabela e um texto em colunas separadas por tabulacao, lido pelo tabela.py, com o
cabecalho "destino, unidade" e uma linha por id nomeado: o destino e o pedaco, como as
analises o escrevem; a unidade e o id que ele nomeia, como o projeto chama as coisas que
ganham material (uma unidade, um item, um conjunto). O pedaco que nomeia mais de um id tem
uma linha para cada; o que nao nomeia nenhum tem uma linha com a unidade vazia. Os textos
se comparam em NFC, pelo texto_comum.py, do extrator, na pasta irma "extrator" ou na mesma
pasta. O programa que usa a tabela confere os ids dela contra os que tem, pelo
desconhecidos().
"""
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "extrator", PASTA):  # na prateleira, o extrator fica na pasta irma
    sys.path.insert(0, str(pasta))
import lugares  # noqa: E402
import tabela  # noqa: E402
from analises import unicos  # noqa: E402
from texto_comum import nfc  # noqa: E402

CABECALHO = ("destino", "unidade")  # as colunas da tabela, na ordem


class ErroDeDestinos(ValueError):
    """Tabela dos destinos que se contradiz, ou destino que nao esta em pedacos; a mensagem
    diz cada problema e onde."""


def ler(texto, nome):
    """{pedaco: [ids]} da tabela, em NFC, os ids na ordem das linhas; o pedaco que nao nomeia
    nenhum id fica com a lista vazia. ErroDeDestinos, com a linha de cada problema, quando
    uma linha nao tem o destino, repete outra, ou da a unidade vazia a um pedaco que tem
    unidade em outra linha; os erros da forma da tabela vem do tabela.py."""
    nomeia, sem_unidade, erros = {}, set(), []
    for n, linha in tabela.ler(texto, CABECALHO, nome):
        pedaco, unidade = nfc(linha["destino"]), nfc(linha["unidade"])
        ids = nomeia.get(pedaco, [])
        repetida = unidade in ids if unidade else pedaco in sem_unidade
        contradiz = pedaco in sem_unidade if unidade else bool(ids)
        if not pedaco:
            erros.append(f"linha {n}: sem o destino")
        elif repetida:
            erros.append(f"linha {n}: repete uma linha de antes")
        elif contradiz:
            erros.append(f"linha {n}: o destino {pedaco!r} tem linha com a unidade vazia e linha com unidade")
        else:
            nomeia[pedaco] = ids + ([unidade] if unidade else [])
            if not unidade:
                sem_unidade.add(pedaco)
    if erros:
        raise ErroDeDestinos(f"{nome}: " + "; ".join(erros))
    return nomeia


def pedacos(trecho):
    """Os pedacos do destino do trecho; ErroDeDestinos quando a forma do campo do destino nao
    da uma lista."""
    valor = lugares.valor(trecho, "destino")
    if not isinstance(valor, list):
        raise ErroDeDestinos(f"{trecho['id']}: o destino não está em pedaços; o campo do destino precisa de uma "
                             "forma que dê lista")
    return valor


def ids_dos_trechos(trechos, nomeia):
    """({id do trecho: [ids]}, {pedaco: [ids dos trechos]}): para cada trecho, os ids que os
    pedacos do destino dele nomeiam, na ordem dos pedacos e sem repetir; e os pedacos que a
    tabela 'nomeia' nao tem, em NFC, cada um uma vez, na ordem em que aparecem, com os
    trechos de cada um. O pedaco sem linha nao da id nenhum."""
    ids, faltam = {}, {}
    for t in trechos:
        achados = []
        for pedaco in map(nfc, pedacos(t)):
            if pedaco in nomeia:
                achados += nomeia[pedaco]
            elif t["id"] not in faltam.setdefault(pedaco, []):
                faltam[pedaco].append(t["id"])
        ids[t["id"]] = unicos(achados)
    return ids, faltam


def desconhecidos(nomeia, conhecidos):
    """[(pedaco, id)] de cada id que a tabela 'nomeia' da a um pedaco e que nao esta entre os
    'conhecidos', na ordem da tabela."""
    return [(pedaco, i) for pedaco, ids in nomeia.items() for i in ids if i not in conhecidos]
