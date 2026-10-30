"""A configuracao da peca e o evento da chamada de ferramenta, num lugar so, para os dois
ganchos.

A configuracao diz as ferramentas que ficam fora do registro, as livres, que a cancela deixa
passar sem regra, e, para cada outra ferramenta, o campo da entrada que a cancela confere; e
lida pelo molde dela, em esquemas/, com o extrator_comum.py, do extrator, que fica duas
pastas acima (na prateleira, em ganchos/<peca>/) ou na pasta irma (numa copia de teste). O
evento e lido pelo protocolo do programa que roda os ganchos, com o protocolo.py, da pasta
irma protocolo, e as partes dele que os ganchos usam, pelo molde delas. Este modulo poe as
duas pastas no caminho de importacao dos ganchos. O gancho que nao consegue fazer o trabalho
dele, ou que barra a chamada, diz o motivo e sai com o codigo que o comando dele da para
barrar. So biblioteca padrao.
"""
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent.parent / "extrator", PASTA.parent / "extrator", PASTA.parent / "protocolo"):
    sys.path.insert(0, str(pasta))  # a ultima posta e a primeira lida
from extrator_comum import ErroDeDados, conferido, le_conferido  # noqa: E402
import protocolo  # noqa: E402

MOLDES = PASTA / "esquemas"  # os moldes da configuracao, da lista das regras e das partes do evento
PARTES = ("sessao", "ferramenta", "entrada", "pasta")  # as partes do evento que os ganchos usam
EVENTO = "antes"  # o evento que os ganchos tratam, pelo nome que o protocolo.py da a ele


def ler_configuracao(caminho):
    """A configuracao, lida pelo molde dela."""
    return le_conferido(caminho, MOLDES / "chamadas-permitidas.schema.json")


def ler_protocolo(caminho):
    """O protocolo do programa que roda os ganchos, lido pelo protocolo.py."""
    return protocolo.ler(caminho)


def chamada(proto, texto):
    """{parte: valor} do evento que chega em texto JSON, lido pelo protocolo e conferido: o
    evento que nao e o de antes de uma chamada e a falta de uma parte, que diz a chave dela no
    programa, sao erro, e as partes, pelo molde delas, a de texto que nao e texto e a entrada
    que nao e objeto tambem."""
    partes = protocolo.le_evento(proto, texto)
    if partes["evento"] != EVENTO:
        raise ErroDeDados(f"o evento não é o de antes de uma chamada: {partes['evento']!r}")
    faltam = [proto["chaves"][parte] for parte in PARTES if parte not in partes]
    if faltam:
        raise ErroDeDados(f"o evento não tem a(s) chave(s) {faltam}")
    return conferido(partes, MOLDES / "evento.schema.json", "o evento")


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
