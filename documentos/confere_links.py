"""Confere os links internos dos documentos Markdown de um repositorio git.

Para cada arquivo .md do repositorio (os versionados e os novos que o .gitignore nao deixa
de fora), acha os links [texto](alvo) e ![texto](alvo) fora de codigo e confere que o
arquivo do alvo existe e, quando o alvo tem ancora (#...), que a ancora e a de um titulo
do arquivo de destino, calculada como o GitHub calcula, ou a de um marcador dele (o id ou o
name de uma tag HTML fora de codigo e de comentario, como <a id="x"></a>), ou, quando ela e
a de uma linha (#L12, que o GitHub e o VS Code abrem na linha), que o arquivo, de qualquer
tipo, tem essa linha. Links externos (com esquema, como https: ou mailto:) ficam de fora.

Uso: python3 -I confere_links.py <raiz do repositorio>

Escreve uma linha ERRO por link quebrado, em ordem de arquivo e linha, e um resumo; sai
com codigo 1 se houver erro e 2, so com o ERRO do que nao serve, se a pasta nao for um
repositorio git ou se um documento, ou o Markdown de destino de uma ancora, nao se ler em
UTF-8. Le os documentos com o extrator_comum.py, do extrator, na pasta irma "extrator" ou
na mesma pasta, e le o Markdown com o markdown_comum.py, desta pasta.
"""

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "extrator", PASTA):  # na prateleira, o extrator fica na pasta irma
    sys.path.insert(0, str(pasta))
from extrator_comum import ErroDeDados, le_texto  # noqa: E402
from markdown_comum import QUEBRA, marcadores, texto_fora_de_codigo, titulos  # noqa: E402

CODIFICACAO = "utf-8"  # a da lista que o git da
EXTENSAO = ".md"  # a dos documentos Markdown: os que se conferem e os unicos com ancora de titulo ou marcador
ANCORA = "#"  # o que separa, no alvo de um link, o arquivo da ancora
ERRO = "ERRO"  # o comeco de cada linha de erro
LINK = re.compile(r"!?\[(?:[^\[\]]|\[[^\[\]]*\])*\]\(\s*(<[^>]*>|[^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
ESQUEMA = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
LINHA = re.compile(r"L([1-9][0-9]*)")  # a ancora de uma linha do arquivo, pelo numero dela


def documentos(raiz):
    saida = subprocess.run(["git", "-C", str(raiz), "ls-files", "--cached", "--others",
                            "--exclude-standard", "-z", "--", f"*{EXTENSAO}"],
                           capture_output=True, check=True).stdout.decode(CODIFICACAO)
    return sorted({p for p in saida.split("\0") if p and (raiz / p).is_file()})


def ancoras(caminho, cache):
    """As ancoras de um arquivo Markdown: as dos titulos e os marcadores."""
    if caminho not in cache:
        texto = le_texto(caminho)
        cache[caminho] = {t.ancora for t in titulos(texto)} | marcadores(texto)
    return cache[caminho]


def links(texto):
    """(numero da linha, alvo) de cada link fora de codigo; o texto do link pode quebrar de
    uma linha para a outra, e a linha e a do comeco do alvo."""
    corrido = texto_fora_de_codigo(texto)
    for m in LINK.finditer(corrido):
        yield corrido.count(QUEBRA, 0, m.start(1)) + 1, m.group(1)


def problema(origem, alvo, cache):
    """O que há de errado com um link interno, ou None."""
    caminho, _, frag = alvo.partition(ANCORA)
    destino = (origem.parent / unquote(caminho)).resolve() if caminho else origem
    if not destino.exists():
        return "o arquivo não existe"
    if not frag:
        return None
    linha = LINHA.fullmatch(unquote(frag))
    if linha:
        if destino.is_dir() or int(linha.group(1)) > len(destino.read_bytes().splitlines()):
            return "o arquivo não tem essa linha"
        return None
    if destino.is_dir() or destino.suffix != EXTENSAO:
        return "âncora num arquivo que não é Markdown"
    if unquote(frag) not in ancoras(destino, cache):
        return "a âncora não é de nenhum título nem marcador"
    return None


def confere(raiz):
    erros, total, com_ancora, cache = [], 0, 0, {}
    for doc in documentos(raiz):
        origem = raiz / doc
        for n, alvo in links(le_texto(origem)):
            if alvo.startswith("<"):
                alvo = alvo[1:-1]
            if ESQUEMA.match(alvo):
                continue
            total += 1
            com_ancora += ANCORA in alvo
            motivo = problema(origem, alvo, cache)
            if motivo:
                erros.append(f"{ERRO} {doc}:{n}: {alvo} — {motivo}")
    return erros, total, com_ancora


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__.split("\n\n")[2], file=sys.stderr)
        return 2
    raiz = Path(argv[0]).resolve()
    try:
        erros, total, com_ancora = confere(raiz)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"{ERRO}: {raiz} não é um repositório git")
        return 2
    except ErroDeDados as e:
        print(f"{ERRO}: {e}")
        return 2
    for e in erros:
        print(e)
    print(f"{total} link(s) interno(s), {com_ancora} com âncora, {len(erros)} erro(s).")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
