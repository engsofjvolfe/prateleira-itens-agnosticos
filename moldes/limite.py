"""
O limite de um material que cobre so as aulas ate uma ultima: de que entradas cada aula
trata e quais so menciona, e que lugares ficam no material.

Uma entrada e o que recebe trechos dentro de um documento: uma unidade sem itens, um item
de uma unidade, ou a unidade com itens, que e a entrada da parte de abertura dela. Entram:
  - os lugares (Lugar): cada um e um trecho de uma aula numa entrada, numa parte do molde
    dela, direto (o destino do trecho nomeia a entrada) ou nao (nomeia um conjunto de que a
    entrada e membro); a parte e um valor qualquer, que so se compara com outro;
  - a unidade de cada item ({item: unidade}); a unidade de algum item e unidade com itens;
  - as aulas em ordem e a ultima aula;
  - o numero de partes para tratar;
  - as decisoes ({entrada: [aulas]}): as aulas que tratam de uma entrada, no lugar da conta.

As regras:
  - uma aula trata de uma unidade sem itens, ou de um item, quando os lugares diretos dos
    trechos dela ali tem pelo menos o numero de partes para tratar, distintas; havendo
    decisao para a entrada, tratam as aulas da decisao. Da unidade com itens tratam as
    aulas que tratam de algum item dela. As outras aulas com lugar na entrada (ou, na
    unidade com itens, num item dela) so a mencionam;
  - a entrada tratada e aquela de que trata alguma aula ate a ultima; a unidade tratada, com
    itens ou sem, e a que tem material;
  - ficam o lugar de uma aula ate a ultima numa entrada cuja unidade tem material (o item so
    mencionado fica, na unidade dele, onde a aula o diz) e o lugar de uma aula depois da
    ultima numa entrada tratada; o resto sai;
  - o trecho que perdeu todos os lugares fica sem lugar, numa lista para os das aulas ate a
    ultima e noutra para os de depois;
  - o trecho de depois da ultima aula que fica vai para as perguntas das aulas ate a ultima
    que tratam das entradas em que ele ficou.
As aulas saem na ordem dada; as entradas, as partes, os lugares e os trechos, na ordem em
que aparecem nos lugares. A aula repetida e achada pelo extrator_comum.py, do extrator, na
pasta irma "extrator" ou na mesma pasta.
"""
import collections
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "extrator", PASTA):  # na prateleira, o extrator fica na pasta irma
    sys.path.insert(0, str(pasta))
from analises import unicos  # noqa: E402
from extrator_comum import repetidos  # noqa: E402

Lugar = collections.namedtuple("Lugar", "trecho aula entrada parte direto")
Limite = collections.namedtuple(
    "Limite", "partes tratam mencionam tratadas com_material ficam sem_lugar_ate sem_lugar_depois perguntas")
# partes: {entrada: {aula: [partes dos lugares diretos]}}; tratam e mencionam: {entrada: [aulas]};
# tratadas e com_material: [entradas]; ficam: [Lugar]; sem_lugar_ate e sem_lugar_depois: {trecho: [Lugar]};
# perguntas: {trecho de depois da ultima aula que fica: [aulas]}


class ErroDeLimite(ValueError):
    """Entradas do limite que se contradizem; a mensagem diz cada problema."""


def aulas_com_lugar(lugares, unidade_de):
    """{entrada: aulas com lugar nela}, as entradas na ordem em que aparecem; a unidade com
    itens recebe tambem as aulas com lugar nos itens dela."""
    saida = {}
    for lugar in lugares:
        for entrada in unicos([lugar.entrada, unidade_de.get(lugar.entrada, lugar.entrada)]):
            saida.setdefault(entrada, set()).add(lugar.aula)
    return saida


def erros_das_entradas(lugares, unidade_de, aulas, ultima, partes_para_tratar, decisoes):
    """Os problemas das entradas, cada um numa frase: o numero de partes para tratar que nao
    e um inteiro de 1 para cima; a aula repetida na ordem; a ultima aula que nao esta entre
    as aulas; o trecho com lugares de mais de uma aula, ou de uma aula que nao esta entre
    elas; o id que e item e unidade com itens; e a decisao para uma unidade com itens, para
    uma entrada sem lugar, ou com aula que nao esta entre as aulas, que vem depois da ultima
    ou que nao tem trecho na entrada."""
    erros = []
    if type(partes_para_tratar) is not int or partes_para_tratar < 1:
        erros.append(f"o número de partes para tratar deve ser um inteiro de 1 para cima: {partes_para_tratar!r}")
    repetidas = repetidos(aulas)
    if repetidas:
        erros.append(f"aula(s) repetida(s) na ordem das aulas: {repetidas}")
    if ultima not in aulas:
        erros.append(f"a última aula {ultima!r} não está entre as aulas")
    aulas_do_trecho = {}
    for lugar in lugares:
        aulas_do_trecho.setdefault(lugar.trecho, []).append(lugar.aula)
    for trecho, suas in aulas_do_trecho.items():
        suas = unicos(suas)
        if len(suas) > 1:
            erros.append(f"o trecho {trecho!r} tem lugares de mais de uma aula: {suas}")
        erros += [f"o trecho {trecho!r} é da aula {a!r}, que não está entre as aulas" for a in suas if a not in aulas]
    com_itens = set(unidade_de.values())
    erros += [f"{item!r} é item e unidade com itens ao mesmo tempo" for item in unidade_de if item in com_itens]
    com_lugar = aulas_com_lugar(lugares, unidade_de)
    depois = set(aulas[aulas.index(ultima) + 1:]) if ultima in aulas else set()
    for entrada, das_decisoes in decisoes.items():
        if entrada in com_itens:
            erros.append(f"decisão para a unidade com itens {entrada!r}: as aulas que tratam dela vêm dos itens")
            continue
        if entrada not in com_lugar:
            erros.append(f"decisão para {entrada!r}, onde nenhum trecho tem lugar")
            continue
        for a in das_decisoes:
            if a not in aulas:
                erros.append(f"decisão para {entrada!r}: a aula {a!r} não está entre as aulas")
            elif a in depois:
                erros.append(f"decisão para {entrada!r}: a aula {a!r} vem depois da última aula")
            elif a not in com_lugar[entrada]:
                erros.append(f"decisão para {entrada!r}: a aula {a!r} não tem trecho nela")
    return erros


def aplicar(lugares, unidade_de, aulas, ultima, partes_para_tratar, decisoes):
    """O Limite dos lugares, pelas regras do comeco deste arquivo. ErroDeLimite, com cada
    problema, quando as entradas se contradizem (erros_das_entradas)."""
    erros = erros_das_entradas(lugares, unidade_de, aulas, ultima, partes_para_tratar, decisoes)
    if erros:
        raise ErroDeLimite("o limite: " + "; ".join(erros))
    ate_a_ultima = set(aulas[:aulas.index(ultima) + 1])
    com_itens = set(unidade_de.values())

    def em_ordem(conjunto):
        return [a for a in aulas if a in conjunto]

    por_aula = {}
    for lugar in lugares:
        if lugar.direto:
            suas = por_aula.setdefault(lugar.entrada, {}).setdefault(lugar.aula, [])
            if lugar.parte not in suas:
                suas.append(lugar.parte)
    partes = {e: {a: por_aula[e][a] for a in em_ordem(por_aula[e])} for e in por_aula}
    com_lugar = aulas_com_lugar(lugares, unidade_de)

    def pela_conta(entrada):
        """As aulas que tratam de uma unidade sem itens ou de um item: as da decisao, ou as
        que dizem dela pelo menos as partes para tratar."""
        if entrada in decisoes:
            return em_ordem(decisoes[entrada])
        return [a for a in aulas if len(partes.get(entrada, {}).get(a, [])) >= partes_para_tratar]

    sem_itens = {e: pela_conta(e) for e in com_lugar if e not in com_itens}
    tratam = {e: sem_itens[e] if e in sem_itens else
              em_ordem({a for item, u in unidade_de.items() if u == e for a in sem_itens.get(item, [])})
              for e in com_lugar}
    mencionam = {e: [a for a in em_ordem(com_lugar[e]) if a not in tratam[e]] for e in com_lugar}
    tratadas = [e for e in com_lugar if ate_a_ultima & set(tratam[e])]
    tratada = set(tratadas)

    def fica(lugar):
        if lugar.aula in ate_a_ultima:
            return unidade_de.get(lugar.entrada, lugar.entrada) in tratada
        return lugar.entrada in tratada

    por_trecho = {}
    for lugar in lugares:
        por_trecho.setdefault(lugar.trecho, []).append(lugar)
    sem_lugar_ate, sem_lugar_depois, perguntas = {}, {}, {}
    for trecho, seus in por_trecho.items():
        ficaram = [lugar for lugar in seus if fica(lugar)]
        ate = seus[0].aula in ate_a_ultima
        if not ficaram:
            (sem_lugar_ate if ate else sem_lugar_depois)[trecho] = seus
        elif not ate:
            perguntas[trecho] = em_ordem({a for lugar in ficaram for a in tratam[lugar.entrada]} & ate_a_ultima)
    return Limite(partes, tratam, mencionam, tratadas, [e for e in tratadas if e not in unidade_de],
                  [lugar for lugar in lugares if fica(lugar)], sem_lugar_ate, sem_lugar_depois, perguntas)
