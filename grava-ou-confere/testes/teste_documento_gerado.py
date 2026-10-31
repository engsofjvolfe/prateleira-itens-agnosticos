"""Testes do documento_gerado.py, com arquivos e textos inventados aqui, sorteados e com letras
de fora do ASCII. Conferem regras, nunca uma frase pronta: o cabecalho vem sem os espacos e
as quebras do fim, e o vazio (tambem so de espacos e quebras), o que falta e o que nao se le
em UTF-8 sao erro (ErroDeDados) que diz o arquivo; o destino que e uma das entradas, tambem
por outro caminho que da no mesmo arquivo, e o que e uma pasta sao erro que diz o destino, e
o que nao existe ou e outro arquivo serve; o texto e o cabecalho e os blocos, como vem, com
uma linha em branco entre um e o seguinte e uma quebra de linha no fim, e, sem bloco, so o
cabecalho com a quebra; duas montagens dao o mesmo. Uso:
    python3 -I teste_documento_gerado.py <pasta do documento_gerado.py> <pasta de trabalho nova>
Precisa do extrator_comum.py, na pasta irma "extrator" da peca.
"""
import random
import string
import sys
from pathlib import Path

PECA, TRABALHO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
sys.path.insert(0, str(PECA))
from documento_gerado import confere_destino, em_blocos, le_cabecalho  # noqa: E402
from extrator_comum import ErroDeDados  # noqa: E402

FALHAS = []
SORTEIO = random.Random(1)
LETRAS = string.ascii_letters + "áçõüéñ€"


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


def texto():
    return " ".join("".join(SORTEIO.choice(LETRAS) for _ in range(SORTEIO.randint(2, 8)))
                    for _ in range(SORTEIO.randint(1, 6)))


def linhas():
    return "\n".join(texto() for _ in range(SORTEIO.randint(1, 4)))


def erro(funcao, *argumentos):
    """A mensagem do ErroDeDados que a funcao da, ou None quando ela nao da erro."""
    try:
        funcao(*argumentos)
    except ErroDeDados as e:
        return str(e)
    return None


TRABALHO.mkdir(parents=True)
CABECA = linhas()
CABECALHO = TRABALHO / "cabecalho.md"
CABECALHO.write_text(CABECA + "  \n\n " + chr(9) + "\n\n", encoding="utf-8")
confere(le_cabecalho(CABECALHO) == CABECA, "o cabeçalho vem sem os espaços e as quebras do fim")
for numero, vazio in enumerate(["", " \n\n" + chr(9) + " ", "\n"]):
    caminho = TRABALHO / f"vazio-{numero}.md"
    caminho.write_text(vazio, encoding="utf-8")
    e = erro(le_cabecalho, caminho)
    confere(e is not None and str(caminho) in e, f"o cabeçalho vazio é erro que diz o arquivo: {e!r}")
SUMIDO, LATIN = TRABALHO / "sumido.md", TRABALHO / "latin.md"
LATIN.write_bytes(f"# {texto()}".encode("latin-1", "replace") + "ç".encode("latin-1"))
for nome, caminho in (("o que falta", SUMIDO), ("o que não se lê em UTF-8", LATIN)):
    e = erro(le_cabecalho, caminho)
    confere(e is not None and str(caminho) in e, f"o cabeçalho {nome} é erro que diz o arquivo: {e!r}")

(TRABALHO / "sub").mkdir()
ENTRADAS = [TRABALHO / "lista.json", TRABALHO / "sub" / "cabecalho.md"]
for entrada in ENTRADAS:
    entrada.write_text(texto(), encoding="utf-8")
OUTRO_CAMINHO = TRABALHO / "sub" / ".." / "lista.json"
for destino in (ENTRADAS[0], ENTRADAS[1], OUTRO_CAMINHO, str(ENTRADAS[1])):
    e = erro(confere_destino, destino, ENTRADAS)
    confere(e is not None and str(destino) in e, f"o destino que é uma das entradas é erro que diz o destino: {e!r}")
PASTA = TRABALHO / "pasta.md"
PASTA.mkdir()
e = erro(confere_destino, PASTA, ENTRADAS)
confere(e is not None and str(PASTA) in e, f"o destino que é uma pasta é erro que diz o destino: {e!r}")
OUTRO = TRABALHO / "outro.md"
OUTRO.write_text(texto(), encoding="utf-8")
for destino in (TRABALHO / "novo" / "documento.md", OUTRO):
    confere(erro(confere_destino, destino, ENTRADAS) is None, f"o destino que não existe, ou é outro arquivo, serve: "
                                                              f"{destino}")

BLOCOS = [linhas() for _ in range(SORTEIO.randint(1, 4))] + [f"{texto()}  ", f"\n{texto()}\n"]
SORTEIO.shuffle(BLOCOS)
confere(em_blocos(CABECA, BLOCOS) == "\n\n".join([CABECA] + BLOCOS) + "\n",
        "o texto é o cabeçalho e os blocos, como vêm, com uma linha em branco entre eles e uma quebra no fim")
confere(em_blocos(CABECA, []) == CABECA + "\n", "sem bloco, o texto é só o cabeçalho, com a quebra do fim")
confere(em_blocos(CABECA, BLOCOS) == em_blocos(CABECA, list(BLOCOS)), "duas montagens dão o mesmo")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
