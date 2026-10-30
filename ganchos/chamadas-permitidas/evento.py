"""A configuracao da peca e o evento da chamada de ferramenta, num lugar so, para os dois
ganchos.

A configuracao diz as ferramentas que ficam fora do registro, as livres, que a cancela deixa
passar sem regra, e, para cada outra ferramenta, o campo da entrada que a cancela confere. O
evento e lido pelo protocolo do programa que roda os ganchos, com o protocolo.py, da pasta
irma protocolo. O gancho que nao consegue fazer o trabalho dele, ou que barra a chamada, diz
o motivo e sai com o codigo que o comando dele da para barrar. So biblioteca padrao.
"""
import sys
from pathlib import Path

import dados

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "protocolo"))  # a pasta irma
import protocolo  # noqa: E402

CHAVES = ("fora_do_registro", "livres", "campos")  # as da configuracao
PARTES = ("sessao", "ferramenta", "entrada", "pasta")  # as partes do evento que os ganchos usam
TEXTOS = ("sessao", "ferramenta", "pasta")  # as partes que sao texto
LISTAS = ("fora_do_registro", "livres")  # as chaves da configuracao que sao listas de ferramentas
EVENTO = "antes"  # o evento que os ganchos tratam, pelo nome que o protocolo.py da a ele


def ler_configuracao(caminho):
    """A configuracao, conferida chave por chave."""
    valor = dados.objeto(dados.le_json(caminho), str(caminho), CHAVES)
    for chave in LISTAS:
        dados.lista(valor[chave], f"{caminho}: {chave}", dados.texto)
    for ferramenta, campo in dados.objeto(valor["campos"], f"{caminho}: campos").items():
        dados.texto(campo, f"{caminho}: campos.{ferramenta}")
    return valor


def ler_protocolo(caminho):
    """O protocolo do programa que roda os ganchos, lido pelo protocolo.py."""
    return protocolo.ler(caminho)


def chamada(proto, texto):
    """{parte: valor} do evento que chega em texto JSON, lido pelo protocolo e conferido: o
    evento que nao e o de antes de uma chamada, a falta de uma parte, a parte de texto que nao
    e texto e a entrada que nao e objeto sao erro."""
    partes = protocolo.le_evento(proto, texto)
    if partes["evento"] != EVENTO:
        raise dados.ErroDeDados(f"o evento não é o de antes de uma chamada: {partes['evento']!r}")
    faltam = [proto["chaves"][parte] for parte in PARTES if parte not in partes]
    if faltam:
        raise dados.ErroDeDados(f"o evento não tem a(s) chave(s) {faltam}")
    for parte in TEXTOS:
        dados.texto(partes[parte], f"o evento: {parte}")
    dados.objeto(partes["entrada"], "o evento: entrada")
    return partes


def guarda(trabalho, prefixo, barra_com):
    """Roda o trabalho do gancho, que devolve None quando a chamada pode rodar ou o motivo de
    barra-la; com motivo, ou com qualquer erro no trabalho, diz o prefixo e o motivo e sai com
    o codigo que barra a chamada."""
    try:
        motivo = trabalho()
    except Exception as erro:  # o gancho que nao consegue trabalhar nao deixa a chamada rodar
        motivo = f"{type(erro).__name__}: {erro}"
    if motivo is not None:
        print(f"{prefixo}: {motivo}", file=sys.stderr)
        sys.exit(barra_com)
