"""
Grava ou confere o registro da ultima conferencia de conteudo do baralho: o sha256 do arquivo
da tabela e o de cada fonte que ela nomeia, achada nas pastas dadas, em ordem. Sem --gravar,
confere: a tabela que mudou desde o registro, a fonte que mudou, que o registro nao tem ou que
nenhuma pasta tem, e a do registro que a tabela nao nomeia mais saem cada uma numa linha
"ERRO arquivo: motivo", com o arquivo do registro. Com --gravar, grava o registro com o sha256
de agora, em UTF-8, com as fontes na ordem da tabela: e o passo depois de conferir de novo as
linhas do CSV das fontes que mudaram.

Sai com 0 sem erro ou quando grava, 1 com erro e 2, sem gravar nada, quando a configuracao, a
tabela, o registro, uma fonte ou um argumento nao servem, ou quando, com --gravar, uma fonte
falta. O registro gravado tem a versao do molde dele. Usa so a biblioteca padrao, o
baralho_comum, desta pasta, e o extrator_comum.py, da peca extrator, que o baralho_comum acha.

Uso:
    python3 -I conferido.py <configuracao.json> <tabela.md> <conferido.json> --pasta <pasta das fontes>...
        [--gravar]
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA))  # o baralho_comum, nesta pasta
import baralho_comum as comum  # noqa: E402
import extrator_comum  # noqa: E402  (achado na pasta irma pelo baralho_comum)

MOLDE = PASTA / "esquemas" / "conferido.schema.json"  # o molde do registro, que da tambem a versao dele


def sha256(caminho):
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def atuais(a):
    """(sha256 da tabela, {fonte: sha256 ou None quando nenhuma pasta a tem}), com as fontes na
    ordem da tabela, cada uma uma vez."""
    conf = comum.le_configuracao(a.configuracao)
    fontes = dict.fromkeys(linha[conf["tabela"]["fonte"]] for linha in comum.tabela(a.tabela, conf))
    for fonte in fontes:
        caminho = comum.acha(fonte, a.pasta)
        fontes[fonte] = sha256(caminho) if caminho else None
    return sha256(a.tabela), fontes


def grava(a, tabela, fontes):
    faltam = [fonte for fonte, valor in fontes.items() if valor is None]
    if faltam:
        raise comum.ErroDeDados(f"fonte(s) que nenhuma pasta tem: {faltam}")
    versao = extrator_comum.le_json(MOLDE)["properties"]["versao_schema"]["const"]
    registro = {"versao_schema": versao, "tabela": tabela, "fontes": fontes}
    Path(a.conferido).write_text(json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(fontes)} fonte(s) gravada(s) em {a.conferido}")
    return 0


def confere(a, tabela, fontes):
    registro = comum.le_conferido(a.conferido, MOLDE)
    erros = [f"a tabela mudou desde a conferência: {a.tabela} ({tabela})"] if registro["tabela"] != tabela else []
    for fonte, valor in fontes.items():
        if valor is None:
            erros.append(f"fonte que nenhuma pasta tem: {fonte}")
        elif fonte not in registro["fontes"]:
            erros.append(f"fonte sem registro: {fonte} ({valor})")
        elif registro["fontes"][fonte] != valor:
            erros.append(f"fonte que mudou desde a conferência: {fonte} ({valor})")
    erros += [f"fonte do registro que a tabela não nomeia: {fonte}"
              for fonte in registro["fontes"] if fonte not in fontes]
    for motivo in erros:
        print(f"ERRO {a.conferido}: {motivo}")
    print(f"{len(fontes)} fonte(s), {len(erros)} erro(s)")
    return 1 if erros else 0


def trabalho(a):
    tabela, fontes = atuais(a)
    return grava(a, tabela, fontes) if a.gravar else confere(a, tabela, fontes)


def main():
    p = argparse.ArgumentParser(description="Grava ou confere o registro da última conferência de conteúdo.")
    p.add_argument("configuracao", help="a configuração do baralho")
    p.add_argument("tabela", help="a tabela Markdown")
    p.add_argument("conferido", help="o registro do sha256 da tabela e das fontes")
    p.add_argument("--pasta", action="append", required=True,
                   help="uma pasta das fontes; pode se repetir, e a primeira que tem a fonte vale")
    p.add_argument("--gravar", action="store_true", help="grava o registro com o sha256 de agora")
    return comum.roda(trabalho, p.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
