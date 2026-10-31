"""
O que os scripts desta pasta fazem do mesmo jeito, num lugar so: as quatro entradas do
comando (a pasta das analises, a forma delas, as regras de lugar e o arquivo de saida), a
leitura delas, o aviso de erro e a gravacao da saida.

A forma das analises e as regras sao lidas contra os moldes delas, em esquemas/ (o campo
que o molde nao conhece, o que falta e o valor de outro tipo ou fora da forma sao erro, que
diz o caminho do valor), e as regras sao conferidas contra a forma. Precisa do
extrator_comum.py, do extrator, na pasta irma "extrator" ou na mesma pasta.
"""
import argparse
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "extrator", PASTA):  # na prateleira, o extrator fica na pasta irma
    sys.path.insert(0, str(pasta))
import extrator_comum  # noqa: E402
import lugares  # noqa: E402

MOLDES = PASTA / "esquemas"  # os moldes da forma das analises e das regras
# o que uma entrada errada levanta: o erro da leitura pelo molde e o das conferencias que ele nao faz (ValueError)
ERROS = (extrator_comum.ErroDeDados, ValueError)


def argumentos(descricao, saida):
    """O leitor do comando com as quatro entradas, a que o script junta as opcoes dele;
    'saida' diz o que o script grava."""
    p = argparse.ArgumentParser(description=descricao)
    p.add_argument("analises", type=Path, help="a pasta das análises")
    p.add_argument("forma", type=Path, help="a forma das análises")
    p.add_argument("regras", type=Path, help="as regras de lugar")
    p.add_argument("saida", type=Path, help=saida)
    return p


def ler(a):
    """(regras, trechos, notas por aula) das entradas do comando: a forma e as regras
    conferidas contra os moldes delas, e as regras contra a forma."""
    forma = extrator_comum.le_conferido(a.forma, MOLDES / "forma-analise.schema.json")
    regras = extrator_comum.le_conferido(a.regras, MOLDES / "regras.schema.json")
    trechos, notas, _ = lugares.trechos_das_analises(a.analises, forma, regras)
    return regras, trechos, notas


def erro(e):
    """Mostra o erro de uma entrada e que nada foi gravado; devolve o codigo de saida da entrada que nao serve, 2."""
    print(f"ERRO: {e}")
    print("Nada foi gravado.")
    return 2


def gravar(caminho, texto):
    """Grava o texto em UTF-8, criando a pasta do arquivo quando ela ainda nao existe."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8")


def rodar(p, trabalho, argv=None):
    """Le o comando pelo leitor p e as entradas dele, faz o trabalho do script e grava o
    texto: trabalho(a, regras, trechos, notas) devolve (texto, resumo, codigo de saida), e a
    tela mostra o resumo e o arquivo gravado. Uma entrada errada, na leitura ou no trabalho,
    da ERRO, e nada e gravado."""
    a = p.parse_args(argv)
    try:
        texto, resumo, codigo = trabalho(a, *ler(a))
    except ERROS as e:
        return erro(e)
    gravar(a.saida, texto)
    print(f"{resumo}; saída: {a.saida}")
    return codigo
