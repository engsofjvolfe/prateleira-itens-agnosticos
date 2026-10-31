"""Confere que nenhuma linha passa do limite de caracteres: em cada arquivo dado e, numa
pasta, em cada arquivo dela e das subpastas cujo nome segue o padrao. O tamanho de uma linha
e o numero de caracteres dela, sem a quebra do fim, qualquer que seja ela. Escreve uma linha
ERRO por linha acima do limite, com o arquivo, o numero da linha e o tamanho dela, em ordem
de arquivo e de linha, e um resumo. Sai com codigo 0 quando nenhuma passa, 1 quando alguma
passa e 2, so com o ERRO do que nao serve, quando um argumento nao serve: o limite que nao e
um inteiro de 1 para cima, o arquivo ou a pasta que nao existe, ou o arquivo que nao se le em
UTF-8. Le os arquivos com o extrator_comum.py, do extrator, na pasta irma "extrator" ou na
mesma pasta. Uso:
    python3 -I linhas_longas.py <limite> <padrao do nome> <arquivo ou pasta>...
Por exemplo: 120 "*.py" scripts
"""
import argparse
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "extrator", PASTA):  # na prateleira, o extrator fica na pasta irma
    sys.path.insert(0, str(pasta))
from extrator_comum import ErroDeDados, le_texto  # noqa: E402

QUEBRA = "\n"  # o que separa as linhas do texto lido, qualquer que seja a quebra no arquivo


def longas(arquivos, limite):
    """(arquivo, numero da linha, tamanho) de cada linha acima do limite, em ordem."""
    return [(arquivo, n, len(linha)) for arquivo in arquivos
            for n, linha in enumerate(le_texto(arquivo).split(QUEBRA), 1) if len(linha) > limite]


def main(argv=None):
    p = argparse.ArgumentParser(description="Confere que nenhuma linha passa do limite de caracteres.")
    p.add_argument("limite", type=int, help="o maior tamanho de linha que passa")
    p.add_argument("padrao", help="o padrão do nome dos arquivos das pastas, como *.py")
    p.add_argument("alvos", type=Path, nargs="+", help="os arquivos e as pastas")
    a = p.parse_args(argv)
    if a.limite < 1:
        print(f"ERRO: o limite precisa ser um inteiro de 1 para cima: {a.limite}")
        return 2
    faltam = [str(alvo) for alvo in a.alvos if not alvo.exists()]
    if faltam:
        print(f"ERRO: não existe(m): {faltam}")
        return 2
    arquivos = sorted({arq for alvo in a.alvos for arq in (alvo.rglob(a.padrao) if alvo.is_dir() else [alvo])
                       if arq.is_file()})
    try:
        falhas = longas(arquivos, a.limite)
    except ErroDeDados as e:
        print(f"ERRO: {e}")
        return 2
    for arquivo, n, tamanho in falhas:
        print(f"ERRO {arquivo}:{n}: a linha tem {tamanho} caractere(s), mais que o limite de {a.limite}")
    print(f"{len(arquivos)} arquivo(s), {len(falhas)} linha(s) com mais de {a.limite} caractere(s).")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
