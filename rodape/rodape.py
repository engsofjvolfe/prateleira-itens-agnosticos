"""
Grava ou confere o rodape no fim de cada documento de um repositorio git, feito de um modelo
Markdown pelo rodape_comum.py, desta pasta: o rodape de cada documento e o modelo, com o alvo
de cada link para um arquivo a partir da pasta do documento.

Os documentos sao os arquivos do repositorio, os versionados e os novos que o .gitignore nao
deixa de fora, que seguem um dos padroes do git (pathspec) de "documentos", na
configuracao, e nenhum dos de "fora"; o modelo, se for um deles, fica de fora. A configuracao
e um JSON com o molde esquemas/rodape.schema.json: o "versao_schema", 1, os "documentos", um
padrao ou mais, e os de "fora", que podem nao ser nenhum, cada padrao numa linha so, sem
repetir.

O documento esta em dia quando termina no rodape dele, depois de uma linha em branco, com
uma quebra de linha no fim. Sem --conferir, o documento que nao esta em dia passa a estar: o
rodape do modelo que ele tem no fim, com qualquer alvo nos links, sai, e o dele entra; o que
esta em dia nao se grava. Com --conferir, nada e gravado: o documento que nao esta em dia sai
numa linha ERRO, com a linha do rodape que ele tem no fim ou, sem nenhum, a ultima com texto.

Mostra uma linha por documento gravado, ou uma ERRO por documento que nao esta em dia, e um
resumo; sai com 0 com os documentos em dia ou gravados, 1 com algum que nao esta em dia, com
--conferir, e 2, sem nada gravado, quando o git nao lista os arquivos da pasta, a
configuracao nao e JSON ou sai do molde, o modelo nao serve (o rodape_comum.py diz quando) ou
um documento nao se le em UTF-8. Precisa do extrator_comum.py, do extrator, do
markdown_comum.py, do documentos, e do grava_ou_confere.py, do grava-ou-confere, nas pastas
irmas ou na mesma pasta.

Uso:
    python3 -I rodape.py <raiz do repositorio> <configuracao.json> <modelo.md> [--conferir]
"""

import argparse
import subprocess
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "grava-ou-confere", PASTA.parent / "documentos", PASTA.parent / "extrator", PASTA):
    sys.path.insert(0, str(pasta))  # na prateleira, as pastas irmas
from extrator_comum import ErroDeDados, le_conferido, le_texto  # noqa: E402
from grava_ou_confere import grava_ou_confere, opcao_conferir  # noqa: E402
from markdown_comum import CODIFICACAO_DO_GIT, QUEBRA, documentos_do_repositorio  # noqa: E402
from rodape_comum import com_rodape, le_modelo, separa  # noqa: E402

MOLDE = PASTA / "esquemas" / "rodape.schema.json"  # o molde da configuracao
FALTA = "falta o rodapé no fim"
FORA_DA_FORMA = "o rodapé do fim não é o deste documento (o alvo de um link, os espaços ou as linhas em branco)"


def documentos(raiz, configuracao, modelo):
    """[(caminho a partir da raiz, arquivo)] dos documentos, em ordem, sem o modelo; ErroDeDados quando a configuracao
    nao serve ou o git nao lista os arquivos."""
    conf = le_conferido(configuracao, MOLDE)
    try:
        lista = documentos_do_repositorio(raiz, conf["documentos"], conf["fora"])
    except subprocess.CalledProcessError as e:
        motivo = e.stderr.decode(CODIFICACAO_DO_GIT, "replace").strip()
        raise ErroDeDados(f"{raiz}: o git não lista os arquivos ({motivo})")
    except FileNotFoundError as e:
        raise ErroDeDados(f"{raiz}: o git não roda ({e})")
    return [(nome, raiz / nome) for nome in lista if (raiz / nome).resolve() != Path(modelo).resolve()]


def ultima_com_texto(texto):
    """O numero da ultima linha com texto, ou 1 no texto vazio."""
    return len(texto.rstrip().split(QUEBRA))


def main(argv=None):
    p = argparse.ArgumentParser(description="Grava ou confere o rodapé no fim de cada documento de um repositório git.")
    p.add_argument("raiz", type=Path, help="a raiz do repositório")
    p.add_argument("configuracao", type=Path, help="os padrões dos documentos, em JSON")
    p.add_argument("modelo", type=Path, help="o modelo do rodapé, em Markdown")
    opcao_conferir(p, "não grava: confere que cada documento termina no rodapé dele")
    a = p.parse_args(argv)
    try:
        modelo = le_modelo(a.modelo)
        textos = [(nome, arquivo, le_texto(arquivo)) for nome, arquivo in documentos(a.raiz, a.configuracao, a.modelo)]
    except ErroDeDados as e:
        print(f"ERRO: {e}")
        return 2
    fora_do_dia = 0
    for nome, arquivo, texto in textos:
        corpo, linha = separa(texto, modelo)
        certo = com_rodape(corpo, modelo, arquivo)
        if texto == certo:
            continue
        fora_do_dia += 1
        onde, motivo = (ultima_com_texto(texto), FALTA) if linha is None else (linha, FORA_DA_FORMA)
        grava_ou_confere(arquivo, certo, a.conferir, falta=f"ERRO {nome}:{onde}: {motivo}",
                         em_dia=f"{nome}: o rodapé está em dia", gravado=f"{nome}: o rodapé foi gravado")
    if a.conferir:
        print(f"{len(textos)} documento(s), {fora_do_dia} sem o rodapé em dia.")
        return 1 if fora_do_dia else 0
    print(f"{len(textos)} documento(s), {fora_do_dia} gravado(s) com o rodapé.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
