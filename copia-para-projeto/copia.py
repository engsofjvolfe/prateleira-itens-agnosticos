"""
Copia arquivos de uma peca da prateleira para um projeto, cada um para o destino dado, e
confere que as copias estao em dia. O arquivo com a mesma extensao do script de
referencia (um script do projeto) recebe na frente o cabecalho de comentario dele: as
linhas do comeco que comecam com o sinal de comentario dado em --comentario, como a da
licenca, e a linha em branco depois delas. Os outros vao como estao.

Com --conferir, nada e gravado: para cada arquivo, diz se a copia do projeto e a da peca,
com o cabecalho, e sai com codigo 1 se alguma nao e. O sinal de comentario vazio, o par sem
destino e o arquivo da peca ou o script de referencia que nao existe ou nao se le em UTF-8
sao erro, que sai com codigo 2, e nada e gravado. Grava e confere cada copia com o
grava_ou_confere.py, da peca grava-ou-confere, e le os arquivos com o extrator_comum.py, da
peca extrator, as duas nas pastas irmas ou na mesma pasta.

Uso:
    python3 -I copia.py <peca> <projeto> <script de referencia> <arquivo da peca>=<destino>... --comentario <sinal>
    python3 -I copia.py <peca> <projeto> <script> <arquivo>=<destino>... --comentario <sinal> --conferir
"""

import argparse
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "grava-ou-confere", PASTA.parent / "extrator", PASTA):  # na prateleira, as pastas irmas
    sys.path.insert(0, str(pasta))
from extrator_comum import ErroDeDados, le_texto  # noqa: E402
from grava_ou_confere import grava_ou_confere, opcao_conferir  # noqa: E402


def cabecalho(referencia, sinal):
    """As linhas do comeco do script de referencia que comecam com o sinal de comentario,
    com a linha em branco depois delas; nenhuma, se ele nao comeca por comentario."""
    linhas = le_texto(referencia).split("\n")
    fim = next((k for k, l in enumerate(linhas) if not l.startswith(sinal)), len(linhas))
    return "\n".join(linhas[:fim]) + "\n\n" if fim else ""


def copias(a):
    """[(destino, texto)] de cada arquivo da peca, com o cabecalho no que tem a extensao do
    script de referencia. ErroDeDados quando o sinal de comentario esta vazio, um par nao tem
    a forma ou um arquivo nao se le."""
    if not a.comentario:
        raise ErroDeDados("o sinal de comentário está vazio")
    cabeca, pares = cabecalho(a.referencia, a.comentario), []
    for par in a.arquivos:
        origem, sep, destino = par.partition("=")
        if not sep or not origem or not destino:
            raise ErroDeDados(f"{par!r} não tem a forma <arquivo da peça>=<destino no projeto>")
        texto = le_texto(a.peca / origem)
        mesma = Path(origem).suffix == a.referencia.suffix
        pares.append((a.projeto / destino, cabeca + texto if mesma else texto))
    return pares


def main(argv=None):
    p = argparse.ArgumentParser(description="Copia arquivos de uma peça para um projeto e confere as cópias.")
    p.add_argument("peca", type=Path)
    p.add_argument("projeto", type=Path)
    p.add_argument("referencia", type=Path, help="um script do projeto, de onde vem o cabeçalho")
    p.add_argument("arquivos", nargs="+", help="<arquivo da peça>=<destino no projeto>")
    p.add_argument("--comentario", required=True, help="o sinal que começa uma linha de comentário nos scripts")
    opcao_conferir(p, "só confere, sem gravar")
    a = p.parse_args(argv)
    try:
        pares = copias(a)
    except ErroDeDados as e:
        print(f"ERRO: {e}")
        return 2
    codigos = [grava_ou_confere(destino, texto, a.conferir, falta=f"{destino}: DIFERENTE da peça",
                                em_dia=f"{destino}: em dia", gravado=f"{destino}: copiado")
               for destino, texto in pares]
    return 1 if any(codigos) else 0


if __name__ == "__main__":
    sys.exit(main())
