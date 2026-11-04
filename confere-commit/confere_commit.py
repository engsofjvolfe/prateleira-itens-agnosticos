"""
Confere um commit antes de ele se fazer: roda, uma por uma, as conferencias de uma lista sobre
os arquivos do commit como estao no indice do git, e sai com erro quando alguma falha, para o
gancho pre-commit barrar o commit.

Cada conferencia tem um nome, os padroes do git (pathspec) dos arquivos que ela olha, os de
fora e o comando, uma lista de argumentos. Os arquivos do commit sao os que o indice muda em
relacao ao ultimo commit. A conferencia roda quando o commit muda algum que segue um dos
padroes e nenhum dos de fora; no comando, o argumento "{arquivos}" vira esses arquivos, os que
o commit nao apaga, em ordem, e a conferencia que o tem e nao tem nenhum deles nao roda; e
"{principal}", dentro de qualquer argumento, vira a pasta principal do repositorio (a da
primeira worktree), onde ficam as pastas que o git nao guarda.

Os arquivos do indice se copiam para uma pasta nova, que some no fim, e cada comando roda nela,
com o git apontado para o repositorio e para o indice do commit: o caminho relativo de um
argumento e o do arquivo do indice, e o git, de dentro do comando, da os arquivos do commit. A
saida de cada comando vai direto para a saida da peca, como ele a escreve.

Mostra, de cada conferencia, se rodou e com quantos arquivos, a saida dela e, quando ela sai
com outro codigo que nao 0, uma linha "ERRO <nome>: motivo"; e um resumo. Sai com 0 sem erro, 1
quando alguma conferencia falha e 2 quando a configuracao, o git ou o programa de um comando
nao serve; o que se acha antes de rodar (o programa que nao se acha, tambem) nao deixa rodar
nenhuma. Usa so a biblioteca padrao, o git, o extrator_comum.py, do extrator, e o
markdown_comum.py, do documentos, nas pastas irmas ou na mesma pasta.

Uso:
    python3 -I confere_commit.py <configuracao.json>
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "extrator", PASTA.parent / "documentos", PASTA):  # na prateleira, as pastas irmas
    sys.path.insert(0, str(pasta))
from extrator_comum import ErroDeDados, le_conferido, preenche, repetidos  # noqa: E402
from markdown_comum import CODIFICACAO_DO_GIT, QUEBRA, caminhos_do_git, padroes_do_git, saida_do_git  # noqa: E402

MOLDE = PASTA / "esquemas" / "confere-commit.schema.json"
ARQUIVOS = "{arquivos}"  # o argumento do comando que vira os arquivos do commit
PRINCIPAL = "principal"  # o campo que, num argumento, vira a pasta principal do repositorio
WORKTREE = "worktree "  # o comeco da linha de cada worktree na lista do git, a da pasta principal primeiro
INDICE = "GIT_INDEX_FILE"  # o indice do commit que o git da ao gancho, quando nao e o de sempre


def le_configuracao(caminho):
    """As conferencias da configuracao, conferida contra o molde; o que o molde nao ve se confere aqui: o nome
    repetido e, num argumento, o campo que nao e o da pasta principal, como o {arquivos} no meio de outro texto."""
    conferencias = le_conferido(caminho, MOLDE)["conferencias"]
    nomes = repetidos([conferencia["nome"] for conferencia in conferencias])
    if nomes:
        raise ErroDeDados(f"{caminho}: conferência com o mesmo nome mais de uma vez: {nomes}")
    for conferencia in conferencias:
        for argumento in conferencia["comando"]:
            if argumento != ARQUIVOS:
                try:
                    preenche(argumento, **{PRINCIPAL: ""})
                except ErroDeDados as e:
                    raise ErroDeDados(f"{caminho}: a conferência {conferencia['nome']!r}: {e}") from None
    return conferencias


def pelo_git(funcao, pasta, *argumentos):
    """O que a funcao do modulo de Markdown da do git rodado na pasta; erro (ErroDeDados) com a mensagem dele quando
    o git nao roda ou sai com outro codigo que nao 0."""
    try:
        return funcao(pasta, *argumentos)
    except subprocess.CalledProcessError as e:
        motivo = e.stderr.decode(CODIFICACAO_DO_GIT, "replace").strip()
        raise ErroDeDados(f"{pasta}: o git não deu {' '.join(argumentos)} ({motivo})") from None
    except OSError as e:
        raise ErroDeDados(f"o git não roda ({e})") from None


def pasta_principal(topo):
    """A pasta principal do repositorio: a da primeira worktree da lista do git."""
    for linha in pelo_git(saida_do_git, topo, "worktree", "list", "--porcelain").splitlines():
        if linha.startswith(WORKTREE):
            return linha[len(WORKTREE):]
    raise ErroDeDados(f"{topo}: o git não deu a pasta principal do repositório")


def do_commit(topo, conferencia):
    """Os caminhos, a partir da raiz e em ordem, dos arquivos que o commit muda e que seguem um dos padroes da
    conferencia e nenhum dos de fora; na conferencia que tem o {arquivos}, so os que ele nao apaga."""
    filtro = ["--diff-filter=d"] if ARQUIVOS in conferencia["comando"] else []
    return sorted(pelo_git(caminhos_do_git, topo, "diff", "--cached", "--name-only", "--no-renames", "-z", *filtro,
                           "--", *padroes_do_git(conferencia["arquivos"], conferencia["fora"])))


def comando(conferencia, arquivos, principal):
    """O comando da conferencia, com o {arquivos} trocado pelos arquivos e o {principal} pela pasta principal."""
    saida = []
    for argumento in conferencia["comando"]:
        saida += arquivos if argumento == ARQUIVOS else [preenche(argumento, **{PRINCIPAL: principal})]
    return saida


def programa_existe(programa, pasta):
    """Se o programa do comando se acha: o que tem pasta no nome, pelo caminho a partir da pasta em que o comando
    roda; o outro, nas pastas do PATH."""
    return shutil.which(os.path.join(pasta, programa) if os.path.dirname(programa) else programa) is not None


def main(argv=None):
    p = argparse.ArgumentParser(description="Roda as conferências de uma lista sobre os arquivos do commit, "
                                            "como estão no índice do git.")
    p.add_argument("configuracao", type=Path, help="as conferências, em JSON")
    a = p.parse_args(argv)
    with tempfile.TemporaryDirectory() as copia:
        try:
            conferencias = le_configuracao(a.configuracao)
            topo = pelo_git(saida_do_git, Path.cwd(), "rev-parse", "--show-toplevel").rstrip(QUEBRA)
            repositorio = pelo_git(saida_do_git, topo, "rev-parse", "--absolute-git-dir").rstrip(QUEBRA)
            principal = pasta_principal(topo)
            planos = [(conferencia, do_commit(topo, conferencia)) for conferencia in conferencias]
            pelo_git(saida_do_git, topo, "checkout-index", "--all", f"--prefix={copia}{os.sep}")
            comandos = {c["nome"]: comando(c, arquivos, principal) for c, arquivos in planos if arquivos}
            sem_programa = sorted(nome for nome, cmd in comandos.items() if not programa_existe(cmd[0], copia))
            if sem_programa:
                raise ErroDeDados(f"conferência com um programa que não se acha: {sem_programa}")
        except ErroDeDados as e:
            print(f"ERRO: {e}")
            return 2
        ambiente = dict(os.environ, GIT_DIR=repositorio, GIT_WORK_TREE=copia)
        if INDICE in os.environ:  # pelo caminho inteiro, porque o comando roda em outra pasta
            ambiente[INDICE] = str(Path(os.environ[INDICE]).resolve())
        rodadas, falhas, sem_rodar = 0, 0, 0
        for conferencia, arquivos in planos:
            nome = conferencia["nome"]
            if not arquivos:
                print(f"{nome}: nenhum arquivo do commit")
                continue
            print(f"{nome}: {len(arquivos)} arquivo(s) do commit", flush=True)
            rodadas += 1
            try:
                codigo = subprocess.run(comandos[nome], cwd=copia, env=ambiente).returncode
            except OSError as e:
                sem_rodar += 1
                print(f"ERRO {nome}: o comando não roda ({e})")
                continue
            if codigo != 0:
                falhas += 1
                print(f"ERRO {nome}: a conferência saiu com o código {codigo}")
    print(f"{len(planos)} conferência(s), {rodadas} rodada(s), {falhas + sem_rodar} com erro")
    return 2 if sem_rodar else 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
