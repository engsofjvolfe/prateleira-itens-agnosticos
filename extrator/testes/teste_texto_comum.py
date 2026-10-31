"""Testes do texto_comum.py, o que as pecas da prateleira fazem do mesmo jeito com um texto.

As palavras e os trechos de espacos sao sorteados, sempre os mesmos, porque a semente e fixa
(outra vem com --semente), com letras de fora do ASCII, cada uma escrita como um caractere so
ou como a letra e o acento separados. O teste confere regras, nunca uma frase pronta:
  - nfc da cada letra com acento como um caractere so, escrita assim ou como a letra e o
    acento separados, tambem misturadas no mesmo texto; o texto ja em NFC nao muda; e o
    caractere de compatibilidade, como uma ligadura, fica como esta;
  - espacos_juntos da as palavras do texto, na ordem, separadas por um espaco so: cada
    trecho de espacos, de qualquer espaco do Unicode, com as quebras de linha e as
    tabulacoes, vira um espaco, e os das pontas saem; as letras ficam como estao; o texto so
    de espacos, ou vazio, da o texto vazio;
  - duas rodadas dao o mesmo.
Uso:
    python3 -I teste_texto_comum.py <pasta do extrator> <pasta de trabalho nova> [--semente N]
A pasta de trabalho nao e usada: as funcoes nao gravam nada.
"""
import argparse
import random
import sys
import unicodedata
from pathlib import Path

LEITOR = argparse.ArgumentParser(description="Testes do módulo de texto comum.")
LEITOR.add_argument("peca", type=Path, help="a pasta do extrator")
LEITOR.add_argument("trabalho", type=Path, help="uma pasta de trabalho nova")
LEITOR.add_argument("--semente", type=int, default=5, help="a semente do sorteio")
ARGS = LEITOR.parse_args()
sys.path.insert(0, str(ARGS.peca.resolve()))
import texto_comum  # noqa: E402

SORTE = random.Random(ARGS.semente)
FALHAS = []
LETRAS = "abcdefghijklmnopqrstuvwxyz"
ACENTUADAS = "áéíóúâêôãõçàüñ"  # letras com acento, cada uma um caractere so na forma NFC
ESPACOS = " \t\n\r\f\v" + "".join(map(unicodedata.lookup, ("NO-BREAK SPACE", "EM SPACE", "IDEOGRAPHIC SPACE")))
# o espaco comum, os de controle e outros espacos do Unicode
COMPATIVEIS = "".join(map(unicodedata.lookup, ("LATIN SMALL LIGATURE FI", "SUPERSCRIPT TWO", "ROMAN NUMERAL TWELVE")))
# caracteres de compatibilidade, que a NFC deixa como estao


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)


def palavra():
    """Uma palavra sorteada, em NFC, sempre com uma letra com acento."""
    letras = [SORTE.choice(LETRAS + ACENTUADAS) for _ in range(SORTE.randint(2, 8))]
    letras.insert(SORTE.randrange(len(letras) + 1), SORTE.choice(ACENTUADAS))
    return "".join(letras)


def espacos():
    """Um trecho sorteado de espacos, de um ou mais."""
    return "".join(SORTE.choice(ESPACOS) for _ in range(SORTE.randint(1, 4)))


def separadas(texto):
    """O texto com cada letra com acento escrita como a letra e o acento separados."""
    return unicodedata.normalize("NFD", texto)


PALAVRAS = [palavra() for _ in range(SORTE.randint(3, 8))]
JUNTAS = " ".join(PALAVRAS)  # as palavras em NFC, separadas por um espaco so
MISTURADAS = "".join(separadas(c) if SORTE.random() < 0.5 else c for c in JUNTAS)
COM_COMPATIVEIS = " ".join(p + SORTE.choice(COMPATIVEIS) for p in PALAVRAS)
SOLTAS = espacos() + "".join(p + espacos() for p in PALAVRAS)  # espacos sorteados nas pontas e entre as palavras


def tudo():
    """O que as funcoes dao para os textos sorteados, para comparar duas rodadas."""
    return ([texto_comum.nfc(t) for t in (separadas(JUNTAS), MISTURADAS, JUNTAS, COM_COMPATIVEIS)],
            [texto_comum.espacos_juntos(t) for t in (SOLTAS, separadas(SOLTAS))])


# ---- nfc ----

confere(separadas(JUNTAS) != JUNTAS, "o texto sorteado tem letra com acento")
confere(texto_comum.nfc(separadas(JUNTAS)) == JUNTAS, "nfc junta a letra e o acento separados num caractere só")
confere(texto_comum.nfc(MISTURADAS) == JUNTAS, "nfc dá o mesmo texto com as letras escritas dos dois jeitos")
confere(texto_comum.nfc(JUNTAS) == JUNTAS, "nfc não muda o texto já em NFC")
confere(texto_comum.nfc(COM_COMPATIVEIS) == COM_COMPATIVEIS, "nfc deixa o caractere de compatibilidade como está")

# ---- espacos_juntos ----

confere(texto_comum.espacos_juntos(SOLTAS) == JUNTAS,
        f"espacos_juntos dá as palavras separadas por um espaço só: {texto_comum.espacos_juntos(SOLTAS)!r}")
for espaco in ESPACOS:
    um, outro = palavra(), palavra()
    confere(texto_comum.espacos_juntos(f"{espaco}{um}{espaco}{outro}{espaco}") == f"{um} {outro}",
            f"espacos_juntos troca {espaco!r} por um espaço e o tira das pontas")
confere(texto_comum.espacos_juntos(separadas(SOLTAS)) == separadas(JUNTAS),
        "espacos_juntos deixa as letras como estão")
for texto, descricao in ((espacos(), "só de espaços"), ("", "vazio")):
    confere(texto_comum.espacos_juntos(texto) == "", f"espacos_juntos dá o texto vazio para o texto {descricao}")

confere(tudo() == tudo(), "duas rodadas dão o mesmo")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s) (semente {ARGS.semente})")
sys.exit(1 if FALHAS else 0)
