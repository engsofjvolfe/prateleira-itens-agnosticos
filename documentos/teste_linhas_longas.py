"""Confere que nenhuma linha passa do limite de caracteres: em cada arquivo dado e, numa
pasta, em cada arquivo dela e das subpastas cujo nome segue o padrao. Mostra
arquivo:linha (tamanho) de cada linha acima do limite, em ordem. Sai com codigo 0 quando
nenhuma passa, 1 quando alguma passa e 2 quando um argumento nao serve: o limite que nao e
um inteiro de 1 para cima, ou o arquivo ou a pasta que nao existe. Uso:
    python3 -I teste_linhas_longas.py <limite> <padrao do nome> <arquivo ou pasta>...
Por exemplo: 120 "*.py" scripts
"""
import argparse
import sys
from pathlib import Path


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
    falhas = [f"{arquivo}:{n} ({len(linha)})"
              for arquivo in arquivos
              for n, linha in enumerate(arquivo.read_text(encoding="utf-8").split("\n"), 1)
              if len(linha) > a.limite]
    print("\n".join(falhas) or f"nenhuma linha passa de {a.limite} caracteres")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
