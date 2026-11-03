"""
Grava o CSV do baralho a partir da tabela Markdown: uma linha por linha da tabela e por coluna
de cartao, na ordem da tabela e, dentro dela, na das colunas de cartao, com o id, o assunto, a
coluna, as palavras-chave e a fonte que a tabela da, e a pergunta, a resposta e o trecho
vazios, que se escrevem pelo texto da fonte. Quando o CSV ja existe, a pergunta, a resposta e o
trecho de cada id que continua na tabela ficam como estavam, e o resto se grava de novo a
partir da tabela.

Sai com 0 quando grava e com 2, sem gravar nada, quando a configuracao, a tabela, o CSV que ja
existe ou um argumento nao servem. Usa so a biblioteca padrao e o baralho_comum, desta pasta.

Uso:
    python3 -I gera_csv.py <configuracao.json> <tabela.md> <baralho.csv>
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # o baralho_comum, nesta pasta
import baralho_comum as comum  # noqa: E402


def gera(a):
    conf = comum.le_configuracao(a.configuracao)
    linhas = comum.linhas_esperadas(a.tabela, conf)
    antes = {linha["id"]: linha for _, linha in comum.le_csv(a.csv)} if a.csv.exists() else {}
    mantidas = [linha for linha in linhas if linha["id"] in antes]
    for linha in mantidas:
        linha.update({c: antes[linha["id"]][c] for c in comum.DA_FONTE})
    comum.grava_csv(a.csv, linhas)
    sairam = len(antes.keys() - {linha["id"] for linha in linhas})
    print(f"{len(linhas)} linha(s) gravada(s) em {a.csv}: {len(mantidas)} com as colunas escritas de antes "
          f"({', '.join(comum.DA_FONTE)}); {sairam} linha(s) de antes que a tabela não dá mais")
    return 0


def main():
    p = argparse.ArgumentParser(description="Grava o CSV do baralho a partir da tabela.")
    p.add_argument("configuracao", help="a configuração do baralho")
    p.add_argument("tabela", help="a tabela Markdown")
    p.add_argument("csv", type=Path, help="o CSV a gravar")
    return comum.roda(gera, p.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
