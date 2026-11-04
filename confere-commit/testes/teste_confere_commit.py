"""Testes do confere_commit.py, com repositorios git inventados aqui: os nomes das pastas, dos arquivos e das
conferencias, os padroes, os textos e o codigo da conferencia que falha sao sorteados, com letras de fora do ASCII
e espacos nos nomes. As conferencias rodam a conferencia_inventada.py, desta pasta, que grava o que recebeu.
Conferem o que a peca faz, nunca uma frase pronta:
  - cada conferencia roda so quando o commit muda um arquivo dos padroes dela e de nenhum dos de fora; com o
    {arquivos}, ela recebe esses arquivos, em ordem, sem os apagados, sem os que nao estao no indice e sem os de
    outros padroes, com o texto do indice, e nao o da pasta; sem o {arquivos}, roda tambem pelo arquivo apagado;
  - a conferencia roda numa pasta que nao e a do repositorio, em que o git da os arquivos do indice;
  - o {principal} vira a pasta principal do repositorio, tambem numa worktree, onde os arquivos sao os do indice dela;
  - a conferencia que sai com outro codigo que nao 0 da uma linha ERRO com o nome dela, e a peca sai com 1; sem
    nenhuma, com 0; o resumo conta as conferencias, as rodadas e as com erro;
  - pelo gancho pre-commit do git, o commit com uma conferencia que falha nao se faz, e o que passa se faz; no commit
    com caminhos, a conferencia recebe so eles, com o texto da pasta, que vai no commit; com outro indice, dado ao
    git pelo caminho a partir da pasta, a conferencia recebe os arquivos dele;
  - no primeiro commit do repositorio, os arquivos do indice contam;
  - saem com 2, sem rodar nenhuma conferencia: a configuracao que nao existe, que nao e JSON, de outra versao, sem
    conferencias, com campo que o molde nao conhece, com conferencia de campo que o molde nao conhece ou sem um
    campo, com nome sem letra, com o mesmo nome duas vezes, sem padroes ou com padrao repetido, com comando vazio,
    com o {arquivos} no meio de outro texto ou com um campo que nao existe, numa conferencia que nao rodaria; o
    programa que nao se acha; a pasta que nao e de um repositorio git; e o git que nao se acha; o programa que se
    acha e nao roda sai com 2, com uma linha ERRO com o nome da conferencia;
  - duas rodadas dao a mesma saida.
Uso:
    python3 -I teste_confere_commit.py <pasta do confere_commit.py> <pasta de trabalho nova>
Precisa do git, que o teste roda sem a configuracao do sistema e da conta, sem nada do git de fora e sem subir da
pasta de trabalho, e das pastas irmas extrator e documentos da peca.
"""
import json
import os
import random
import re
import string
import subprocess
import sys
from pathlib import Path

PECA, TRABALHO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
SCRIPT = PECA / "confere_commit.py"
INVENTADA = PECA / "testes" / "conferencia_inventada.py"
FALHAS = []
SORTEIO = random.Random(5)
LETRAS = string.ascii_lowercase + "áçõüéñ"
USADAS = set()
NUMERO = re.compile(r"\d+")


def palavra():
    """Uma palavra sorteada, com letras de fora do ASCII, que ainda nao saiu."""
    while True:
        nova = "".join(SORTEIO.choice(LETRAS) for _ in range(SORTEIO.randint(3, 7)))
        if nova not in USADAS:
            USADAS.add(nova)
            return nova


def nome():
    """Um nome de arquivo, de pasta ou de conferencia, com um espaco."""
    return f"{palavra()} {palavra()}"


# o git sem a configuracao do sistema e da conta, sem nada do git de fora e sem subir da pasta de trabalho
GIT = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
GIT.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", GIT_CEILING_DIRECTORIES=str(TRABALHO),
           GIT_AUTHOR_NAME=palavra(), GIT_AUTHOR_EMAIL=f"{palavra()}@{palavra()}",
           GIT_COMMITTER_NAME=palavra(), GIT_COMMITTER_EMAIL=f"{palavra()}@{palavra()}")


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


def git(pasta, *argumentos, **ambiente):
    """A saida do git rodado na pasta, com o que se der a mais no ambiente; o erro dele vai para o teste."""
    return subprocess.run(["git", "-C", str(pasta), *argumentos], check=True, capture_output=True,
                          env=dict(GIT, **ambiente)).stdout.decode("utf-8")


def commit(pasta, *caminhos):
    """O codigo do git commit na pasta, so com os caminhos dados, quando houver."""
    so_eles = ["--", *caminhos] if caminhos else []
    return subprocess.run(["git", "-C", str(pasta), "commit", "-q", "-m", palavra(), *so_eles],
                          capture_output=True, env=GIT).returncode


def roda(configuracao, pasta, **ambiente):
    """(codigo, linhas da saida) do confere_commit.py rodado na pasta, com o que se der a mais no ambiente."""
    r = subprocess.run([sys.executable, "-I", str(SCRIPT), str(configuracao)], cwd=pasta, capture_output=True,
                       env=dict(GIT, **ambiente))
    return r.returncode, r.stdout.decode("utf-8").splitlines()


def escreve(caminho, texto):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8")
    return caminho


def grava_json(dados):
    return escreve(TRABALHO / f"{palavra()}.json", json.dumps(dados, ensure_ascii=False))


TRABALHO.mkdir(parents=True)
RAIZ = TRABALHO / nome()
TEXTOS, OUTROS, FORA_DO_GIT = nome(), nome(), nome()  # a pasta dos textos, a de outro padrao e a que o git nao guarda
EXTENSAO = f".{palavra()}"
MUDA, NOVO, IGUAL, APAGADO, DE_FORA, SEM_INDICE = (f"{TEXTOS}/{nome()}{EXTENSAO}" for _ in range(6))
OUTRO = f"{OUTROS}/{nome()}.{palavra()}"
NA_PRINCIPAL = f"{FORA_DO_GIT}/{palavra()}.py"  # a conferencia que so a pasta principal tem
REGISTROS = {chave: TRABALHO / f"{palavra()}.json" for chave in ("textos", "nenhum", "apagado", "falha", "principal")}
NOMES = {chave: nome() for chave in REGISTROS}
CODIGO_DA_FALHA = SORTEIO.randint(3, 9)
TEXTO = {caminho: f"{nome()}\n" for caminho in (MUDA, NOVO, IGUAL, APAGADO, DE_FORA, SEM_INDICE, OUTRO)}
NO_INDICE, NA_PASTA = f"{nome()}\n", f"{nome()}\n"  # o texto do MUDA no indice e na pasta, depois do primeiro commit

RAIZ.mkdir()
git(RAIZ, "init", "-q")
for caminho in (MUDA, IGUAL, APAGADO):
    escreve(RAIZ / caminho, TEXTO[caminho])
escreve(RAIZ / ".gitignore", f"{FORA_DO_GIT}/\n")
git(RAIZ, "add", "--", MUDA, IGUAL, APAGADO, ".gitignore")
commit(RAIZ)
escreve(RAIZ / NA_PRINCIPAL, INVENTADA.read_text(encoding="utf-8"))
for caminho in (NOVO, DE_FORA, SEM_INDICE, OUTRO):
    escreve(RAIZ / caminho, TEXTO[caminho])
escreve(RAIZ / MUDA, NO_INDICE)
git(RAIZ, "add", "--", MUDA, NOVO, DE_FORA, OUTRO)
git(RAIZ, "rm", "-q", "--", APAGADO)
escreve(RAIZ / MUDA, NA_PASTA)  # a pasta muda depois do indice
INDICE_DEPOIS = sorted([".gitignore", MUDA, IGUAL, NOVO, DE_FORA, OUTRO])


def inventada(chave, codigo=0, programa=None):
    """O comando da conferencia inventada, que grava no registro da chave e sai com o codigo."""
    return [sys.executable, "-I", programa or str(INVENTADA), str(REGISTROS[chave]), str(codigo)]


def conferencia(chave, arquivos, fora, *comando):
    return {"nome": NOMES[chave], "arquivos": arquivos, "fora": fora, "comando": [*comando]}


CONFERENCIAS = [
    conferencia("textos", [f"{TEXTOS}/*{EXTENSAO}"], [DE_FORA], *inventada("textos"), "{arquivos}"),
    conferencia("nenhum", [f"*.{palavra()}"], [], *inventada("nenhum"), "{arquivos}"),
    conferencia("apagado", [APAGADO], [], *inventada("apagado")),
    conferencia("falha", [f"{OUTROS}/*"], [], *inventada("falha", CODIGO_DA_FALHA), "{arquivos}"),
    conferencia("principal", [f"{TEXTOS}/*"], [], *inventada("principal", programa=f"{{principal}}/{NA_PRINCIPAL}")),
]
CONFIGURACAO = {"versao_schema": 1, "conferencias": CONFERENCIAS}
CONF = grava_json(CONFIGURACAO)
QUE_PASSA = grava_json(dict(CONFIGURACAO, conferencias=[c for c in CONFERENCIAS if c["nome"] != NOMES["falha"]]))
SO_A_DOS_TEXTOS = grava_json(dict(CONFIGURACAO, conferencias=CONFERENCIAS[:1]))


def registro(chave):
    """O que a conferencia da chave gravou, ou None quando ela nao rodou."""
    caminho = REGISTROS[chave]
    return json.loads(caminho.read_text(encoding="utf-8")) if caminho.exists() else None


def limpa_registros():
    for caminho in REGISTROS.values():
        if caminho.exists():
            caminho.unlink()


def erros(saida):
    return [linha for linha in saida if linha.startswith("ERRO")]


def resumo(saida):
    return [int(n) for n in NUMERO.findall(saida[-1])] if saida else []


codigo, saida = roda(CONF, RAIZ)
confere(codigo == 1, f"com uma conferência que falha, sai com 1: {codigo}, {saida}")
confere(len(erros(saida)) == 1 and NOMES["falha"] in erros(saida)[0],
        f"só a conferência que falha dá uma linha ERRO, com o nome dela: {erros(saida)}")
confere(resumo(saida) == [len(CONFERENCIAS), len(CONFERENCIAS) - 1, 1],
        f"o resumo conta as conferências, as rodadas e as com erro: {saida[-1:]}")
textos = registro("textos")
confere(textos is not None and textos["arquivos"] == sorted([MUDA, NOVO]),
        f"com o {{arquivos}}, a conferência recebe, em ordem, os arquivos do commit que seguem os padrões dela, sem os "
        f"apagados, os que não estão no índice, os de fora e os de outros padrões: {textos and textos['arquivos']}")
confere(textos is not None and textos["textos"] == {MUDA: NO_INDICE, NOVO: TEXTO[NOVO]},
        f"a conferência lê o texto do índice, e não o da pasta: {textos and textos['textos']}")
confere(textos is not None and Path(textos["pasta"]) != RAIZ.resolve() and textos["do_git"] == INDICE_DEPOIS,
        f"a conferência roda numa pasta que não é a do repositório, em que o git dá os arquivos do índice: {textos}")
confere(registro("nenhum") is None, "a conferência sem arquivo do commit não roda")
apagado = registro("apagado")
confere(apagado is not None and apagado["arquivos"] == [],
        f"sem o {{arquivos}}, a conferência roda pelo arquivo apagado e não recebe arquivo: {apagado}")
falha = registro("falha")
confere(falha is not None and falha["arquivos"] == [OUTRO], f"a conferência que falha recebe os arquivos dela: {falha}")
confere(registro("principal") is not None, "o {principal} vira a pasta principal do repositório")
confere(roda(CONF, RAIZ) == (codigo, saida), "duas rodadas dão a mesma saída")
limpa_registros()
codigo, saida = roda(QUE_PASSA, RAIZ)
confere(codigo == 0 and not erros(saida), f"sem conferência que falha, sai com 0: {codigo}, {saida}")

OUTRA_PASTA = TRABALHO / nome()
git(RAIZ, "worktree", "add", "-q", "-b", palavra(), str(OUTRA_PASTA))
NA_WORKTREE, TEXTO_DA_WORKTREE = f"{TEXTOS}/{nome()}{EXTENSAO}", f"{nome()}\n"
escreve(OUTRA_PASTA / NA_WORKTREE, TEXTO_DA_WORKTREE)
git(OUTRA_PASTA, "add", "--", NA_WORKTREE)
limpa_registros()
codigo, saida = roda(QUE_PASSA, OUTRA_PASTA)
textos = registro("textos")
confere(codigo == 0 and textos is not None and textos["textos"] == {NA_WORKTREE: TEXTO_DA_WORKTREE},
        f"numa worktree, os arquivos do commit são os do índice dela: {codigo}, {saida}, {textos}")
confere(registro("principal") is not None,
        f"numa worktree, o {{principal}} vira a pasta principal, a que tem o que o git não guarda: {saida}")


def gancho(configuracao):
    """Liga o confere_commit.py, com a configuracao, no gancho pre-commit do repositorio da pasta principal."""
    caminho = escreve(RAIZ / ".git" / "hooks" / "pre-commit",
                      f'#!/bin/sh\nexec "{sys.executable}" -I "{SCRIPT}" "{configuracao}"\n')
    caminho.chmod(0o755)


gancho(CONF)
ANTES = git(RAIZ, "rev-parse", "HEAD")
confere(commit(RAIZ) != 0 and git(RAIZ, "rev-parse", "HEAD") == ANTES,
        "pelo gancho, o commit com uma conferência que falha não se faz")
gancho(QUE_PASSA)
limpa_registros()
feito = commit(RAIZ)
textos = registro("textos")
confere(feito == 0 and git(RAIZ, "rev-parse", "HEAD") != ANTES and textos is not None
        and textos["textos"] == {MUDA: NO_INDICE, NOVO: TEXTO[NOVO]},
        f"pelo gancho, o commit que passa se faz, e a conferência lê o texto do índice: {feito}, {textos}")
NO_INDICE_2, NA_PASTA_2, NOVO_2 = f"{nome()}\n", f"{nome()}\n", f"{nome()}\n"
escreve(RAIZ / MUDA, NO_INDICE_2)
escreve(RAIZ / NOVO, NOVO_2)
git(RAIZ, "add", "--", MUDA, NOVO)
escreve(RAIZ / MUDA, NA_PASTA_2)
limpa_registros()
feito = commit(RAIZ, MUDA)
textos = registro("textos")
confere(feito == 0 and textos is not None and textos["textos"] == {MUDA: NA_PASTA_2},
        f"no commit com caminhos, a conferência recebe só eles, com o texto da pasta, que vai no commit: {textos}")

OUTRO_INDICE = f".git/{palavra()}"  # dado ao git pelo caminho a partir da pasta do repositorio
NO_OUTRO_INDICE, TEXTO_DO_OUTRO_INDICE = f"{TEXTOS}/{nome()}{EXTENSAO}", f"{nome()}\n"
escreve(RAIZ / NO_OUTRO_INDICE, TEXTO_DO_OUTRO_INDICE)
git(RAIZ, "read-tree", "HEAD", GIT_INDEX_FILE=OUTRO_INDICE)
git(RAIZ, "add", "--", NO_OUTRO_INDICE, GIT_INDEX_FILE=OUTRO_INDICE)
limpa_registros()
codigo, saida = roda(SO_A_DOS_TEXTOS, RAIZ, GIT_INDEX_FILE=OUTRO_INDICE)
textos = registro("textos")
confere(codigo == 0 and textos is not None and textos["textos"] == {NO_OUTRO_INDICE: TEXTO_DO_OUTRO_INDICE}
        and NO_OUTRO_INDICE in textos["do_git"],
        f"com outro índice, dado pelo caminho a partir da pasta, a conferência recebe os arquivos dele: {saida}, "
        f"{textos}")

PRIMEIRO = TRABALHO / nome()
PRIMEIRO.mkdir()
git(PRIMEIRO, "init", "-q")
DO_PRIMEIRO, TEXTO_DO_PRIMEIRO = f"{TEXTOS}/{nome()}{EXTENSAO}", f"{nome()}\n"
escreve(PRIMEIRO / DO_PRIMEIRO, TEXTO_DO_PRIMEIRO)
git(PRIMEIRO, "add", "--", DO_PRIMEIRO)
limpa_registros()
codigo, saida = roda(SO_A_DOS_TEXTOS, PRIMEIRO)
textos = registro("textos")
confere(codigo == 0 and textos is not None and textos["textos"] == {DO_PRIMEIRO: TEXTO_DO_PRIMEIRO},
        f"no primeiro commit do repositório, os arquivos do índice contam: {codigo}, {saida}, {textos}")


def com_conferencia(k, **campos):
    """A configuracao com os campos dados na conferencia k; None tira o campo."""
    mudada = {c: v for c, v in dict(CONFERENCIAS[k], **campos).items() if v is not None}
    return grava_json(dict(CONFIGURACAO, conferencias=CONFERENCIAS[:k] + [mudada] + CONFERENCIAS[k + 1:]))


def caso(configuracao, pasta=RAIZ, **ambiente):
    """(configuracao, pasta em que a peca roda, o que vai a mais no ambiente) de um caso que nao serve."""
    return configuracao, pasta, ambiente


NENHUM = 1  # a conferencia que nao rodaria: o erro dela so a leitura da configuracao pega
SEM_GIT = TRABALHO / palavra()  # uma pasta vazia, fora de qualquer repositorio
SEM_GIT.mkdir()
NAO_SERVEM = {
    "a configuração que não existe": caso(TRABALHO / f"{palavra()}.json"),
    "a configuração que não é JSON": caso(escreve(TRABALHO / f"{palavra()}.json", "{" + palavra())),
    "a configuração de outra versão": caso(grava_json(dict(CONFIGURACAO, versao_schema=2))),
    "a configuração sem conferências": caso(grava_json(dict(CONFIGURACAO, conferencias=[]))),
    "a configuração com campo que o molde não conhece": caso(grava_json(dict(CONFIGURACAO, **{palavra(): palavra()}))),
    "a conferência com campo que o molde não conhece": caso(com_conferencia(NENHUM, **{palavra(): palavra()})),
    "a conferência sem um campo": caso(com_conferencia(NENHUM, fora=None)),
    "a conferência com nome sem letra": caso(com_conferencia(NENHUM, nome=" ")),
    "o mesmo nome duas vezes": caso(grava_json(dict(CONFIGURACAO, conferencias=CONFERENCIAS + [CONFERENCIAS[NENHUM]]))),
    "a conferência sem padrões": caso(com_conferencia(NENHUM, arquivos=[])),
    "a conferência com padrão repetido": caso(com_conferencia(NENHUM, arquivos=[f"*.{palavra()}"] * 2)),
    "a conferência com comando vazio": caso(com_conferencia(NENHUM, comando=[])),
    "o {arquivos} no meio de outro texto": caso(com_conferencia(NENHUM, comando=[*inventada("nenhum"),
                                                                                  f"{palavra()}{{arquivos}}"])),
    "um campo que não existe": caso(com_conferencia(NENHUM, comando=[*inventada("nenhum"), f"{{{palavra()}}}"])),
    "o programa que não se acha": caso(com_conferencia(0, comando=[str(TRABALHO / palavra()), "{arquivos}"])),
    "a pasta que não é de um repositório git": caso(QUE_PASSA, SEM_GIT),
    "o git que não se acha": caso(QUE_PASSA, PATH=str(SEM_GIT)),
}
for descricao, (configuracao, pasta, ambiente) in NAO_SERVEM.items():
    limpa_registros()
    codigo, saida = roda(configuracao, pasta, **ambiente)
    confere(codigo == 2 and len(erros(saida)) == 1 and all(registro(chave) is None for chave in REGISTROS),
            f"{descricao}: sai com 2, com uma linha ERRO, sem rodar nenhuma conferência: {codigo}, {saida}")
NAO_RODA = TRABALHO / palavra()  # um programa que se acha, mas que o sistema nao roda
NAO_RODA.write_bytes(bytes(SORTEIO.randrange(256) for _ in range(64)).replace(b"#!", b"!#"))
NAO_RODA.chmod(0o755)
codigo, saida = roda(com_conferencia(0, comando=[str(NAO_RODA), "{arquivos}"]), RAIZ)
confere(codigo == 2 and any(NOMES["textos"] in linha for linha in erros(saida)) and resumo(saida)[-1:] == [1],
        f"o programa que se acha e não roda sai com 2, com uma linha ERRO com o nome da conferência: {codigo}, {saida}")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
