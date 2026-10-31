"""
O que as pecas da prateleira fazem do mesmo jeito com um texto, num lugar so: passar o texto
para a forma Unicode NFC, em que a mesma letra se escreve sempre do mesmo jeito (a letra com
acento, escrita como um caractere so ou como a letra e o acento separados, vira um caractere
so), e juntar os espacos, cada trecho de espacos (qualquer espaco do Unicode, com as quebras
de linha e as tabulacoes) virando um espaco so, sem espaco nas pontas.

Nao se roda: as pecas o importam da pasta do extrator. So biblioteca padrao.
"""
import unicodedata

FORMA = "NFC"  # a forma Unicode em que a mesma letra se escreve sempre do mesmo jeito
ESPACO = " "  # o que fica no lugar de cada trecho de espacos


def nfc(texto):
    """O texto na forma Unicode NFC; o caractere de compatibilidade, como uma ligadura, fica como esta."""
    return unicodedata.normalize(FORMA, texto)


def espacos_juntos(texto):
    """O texto com cada trecho de espacos (qualquer espaco do Unicode, com as quebras de linha e as tabulacoes)
    virando um espaco so, sem espaco nas pontas; as letras ficam como estao."""
    return ESPACO.join(texto.split())
