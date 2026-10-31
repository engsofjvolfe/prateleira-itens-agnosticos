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
na mesma pasta.
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

CODIFICACAO = "utf-8"  # a da lista que o git da
EXTENSAO = ".md"  # a dos documentos Markdown: os que se conferem e os unicos com ancora de titulo ou marcador
ANCORA = "#"  # o que separa, no alvo de um link, o arquivo da ancora
QUEBRA = "\n"  # o que separa as linhas do texto corrido
ERRO = "ERRO"  # o comeco de cada linha de erro
CERCA = re.compile(r"^ {0,3}(`{3,}|~{3,})")
CODIGO_NA_LINHA = re.compile(r"(`+)(?:(?!\1).)+?\1")
LINK = re.compile(r"!?\[(?:[^\[\]]|\[[^\[\]]*\])*\]\(\s*(<[^>]*>|[^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
TITULO = re.compile(r"^ {0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
ESQUEMA = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
TAG_HTML = re.compile(r"<[^>]+>")
LINK_NO_TITULO = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
LINHA = re.compile(r"L([1-9][0-9]*)")  # a ancora de uma linha do arquivo, pelo numero dela
COMENTARIO_HTML = re.compile(r"<!--.*?-->", re.DOTALL)
# um atributo de uma tag HTML como o CommonMark o le: o nome e o valor, sem aspas, entre simples ou entre duplas
ATRIBUTO_HTML = re.compile(r"""\s+([A-Za-z_:][A-Za-z0-9_.:-]*)(?:\s*=\s*(?:([^\s"'=<>`]+)|'([^']*)'|"([^"]*)"))?""")
TAG_DE_ABERTURA = re.compile(rf"<[A-Za-z][A-Za-z0-9-]*(?:{ATRIBUTO_HTML.pattern})*\s*/?>")
ATRIBUTOS_DE_MARCADOR = ("id", "name")  # os atributos de uma tag HTML que um link alcanca pela ancora


def documentos(raiz):
    saida = subprocess.run(["git", "-C", str(raiz), "ls-files", "--cached", "--others",
                            "--exclude-standard", "-z", "--", f"*{EXTENSAO}"],
                           capture_output=True, check=True).stdout.decode(CODIFICACAO)
    return sorted({p for p in saida.split("\0") if p and (raiz / p).is_file()})


def linhas_fora_de_codigo(texto):
    """(numero, linha) de cada linha fora de bloco de codigo."""
    cerca = None
    for n, linha in enumerate(texto.splitlines(), 1):
        m = CERCA.match(linha)
        if cerca:
            if m and m.group(1)[0] == cerca[0] and len(m.group(1)) >= len(cerca) \
                    and not linha.strip()[len(m.group(1)):].strip():
                cerca = None
            continue
        if m:
            cerca = m.group(1)
            continue
        yield n, linha


def texto_fora_de_codigo(texto):
    """O texto com as linhas dos blocos de codigo vazias e sem o codigo na linha; cada linha
    fica no numero dela."""
    linhas = texto.splitlines()
    fora = dict(linhas_fora_de_codigo(texto))
    return QUEBRA.join(CODIGO_NA_LINHA.sub("", fora.get(n, "")) for n in range(1, len(linhas) + 1))


def ancora(titulo):
    """A ancora que o GitHub da a um titulo: o texto como aparece, em minusculas, sem
    pontuacao, com hifen no lugar de cada espaco."""
    texto = LINK_NO_TITULO.sub(r"\1", titulo)
    texto = TAG_HTML.sub("", texto)
    texto = texto.replace("`", "").lower()
    return re.sub(r"[^\w\- ]", "", texto).replace(" ", "-")


def marcadores(texto):
    """O valor do id e do name de cada tag HTML fora de codigo e de comentario."""
    sem_comentario = COMENTARIO_HTML.sub("", texto_fora_de_codigo(texto))
    return {"".join(valor) for tag in TAG_DE_ABERTURA.finditer(sem_comentario)
            for nome, *valor in ATRIBUTO_HTML.findall(tag.group()) if nome.lower() in ATRIBUTOS_DE_MARCADOR}


def ancoras(caminho, cache):
    """As ancoras de um arquivo Markdown: as dos titulos e os marcadores."""
    if caminho not in cache:
        texto = le_texto(caminho)
        vistas, todas = {}, marcadores(texto)
        for _, linha in linhas_fora_de_codigo(texto):
            m = TITULO.match(linha)
            if not m:
                continue
            base = ancora(m.group(2))
            n = vistas.get(base, 0)
            vistas[base] = n + 1
            todas.add(base if n == 0 else f"{base}-{n}")
        cache[caminho] = todas
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
