"""Testes do grava_ou_confere.py, com arquivos, textos e mensagens inventados aqui, os textos
com letras de fora do ASCII. Conferem o que a peca faz, nunca uma frase pronta: sem
conferir, o texto vai para o arquivo, em UTF-8, com as pastas que faltam, por cima do que
houver, sai a mensagem de gravado e o codigo e 0; conferindo, nada e gravado nem criado, e
sai a mensagem de em dia com 0, quando o arquivo e o texto, ou a de falta com 1, quando e
outro ou nao existe; o arquivo pode vir como caminho ou como texto; a opcao --conferir liga
"conferir" nos argumentos lidos, e a ajuda dada aparece na ajuda do script; duas rodadas
dao o mesmo. Uso:
    python3 -I teste_grava_ou_confere.py <pasta do grava_ou_confere.py> <pasta de trabalho nova>
"""
import argparse
import contextlib
import io
import random
import string
import sys
from pathlib import Path

PECA, TRABALHO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
sys.path.insert(0, str(PECA))
from grava_ou_confere import grava_ou_confere, opcao_conferir  # noqa: E402

FALHAS = []
SORTEIO = random.Random(1)
FORA_DO_ASCII = "áçõü€✓"  # letras que so uma codificacao de todas, como o UTF-8, grava
LETRAS = string.ascii_letters + " \n" + FORA_DO_ASCII


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


def nome():
    return "".join(SORTEIO.choice(string.ascii_lowercase) for _ in range(8))


def texto():
    """Um texto sorteado, sempre com as letras de fora do ASCII."""
    return "".join(SORTEIO.choice(LETRAS) for _ in range(200)) + FORA_DO_ASCII


def chama(arquivo, texto_, conferir):
    """(codigo, o que saiu, as mensagens inventadas dadas a peca)."""
    mensagens = {"falta": nome(), "em_dia": nome(), "gravado": nome()}
    saida = io.StringIO()
    with contextlib.redirect_stdout(saida):
        codigo = grava_ou_confere(arquivo, texto_, conferir, **mensagens)
    return codigo, saida.getvalue().strip(), mensagens


def le(arquivo):
    return arquivo.read_text(encoding="utf-8")


TRABALHO.mkdir(parents=True)
ARQUIVO, CONTEUDO, OUTRO = TRABALHO / nome() / nome() / f"{nome()}.{nome()}", texto(), texto()

codigo, saiu, m = chama(ARQUIVO, CONTEUDO, False)
confere(ARQUIVO.is_file() and le(ARQUIVO) == CONTEUDO, "grava o texto, em UTF-8, criando as pastas que faltam")
confere(codigo == 0 and saiu == m["gravado"], f"ao gravar, mostra a mensagem de gravado e devolve 0: {saiu!r}")
antes = ARQUIVO.read_bytes()

codigo, saiu, m = chama(ARQUIVO, CONTEUDO, True)
confere(codigo == 0 and saiu == m["em_dia"], f"com o arquivo igual ao texto, mostra a de em dia e devolve 0: {saiu!r}")
confere(ARQUIVO.read_bytes() == antes, "conferir não grava")
codigo, saiu, m = chama(ARQUIVO, OUTRO, True)
confere(codigo == 1 and saiu == m["falta"], f"com o arquivo diferente, mostra a de falta e devolve 1: {saiu!r}")
confere(ARQUIVO.read_bytes() == antes, "conferir, com o arquivo diferente, não grava")
SUMIDO = TRABALHO / nome() / f"{nome()}.{nome()}"
codigo, saiu, m = chama(SUMIDO, CONTEUDO, True)
confere(codigo == 1 and saiu == m["falta"] and not SUMIDO.parent.exists(),
        f"sem o arquivo, mostra a de falta, devolve 1 e não cria nada: {saiu!r}")

codigo, saiu, m = chama(ARQUIVO, OUTRO, False)
confere(codigo == 0 and le(ARQUIVO) == OUTRO, "grava por cima do arquivo diferente")
COMO_TEXTO = TRABALHO / f"{nome()}.{nome()}"
chama(str(COMO_TEXTO), CONTEUDO, False)
confere(COMO_TEXTO.is_file() and chama(str(COMO_TEXTO), CONTEUDO, True)[0] == 0, "o arquivo pode vir como texto")

uma = chama(ARQUIVO, CONTEUDO, False)[0], ARQUIVO.read_bytes()
confere(chama(ARQUIVO, CONTEUDO, False)[0] == uma[0] and ARQUIVO.read_bytes() == uma[1], "duas rodadas dão o mesmo")

leitor, ajuda = argparse.ArgumentParser(), nome()
opcao_conferir(leitor, ajuda)
confere(leitor.parse_args(["--conferir"]).conferir is True and leitor.parse_args([]).conferir is False,
        "a opção --conferir liga o conferir, e sem ela ele fica desligado")
confere(ajuda in leitor.format_help(), "a ajuda dada aparece na ajuda do script")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
