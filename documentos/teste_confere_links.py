"""Testa o confere_links.py com repositorios inventados.

Uso: python3 -I teste_confere_links.py <pasta do confere_links.py> <pasta de trabalho nova ou vazia>

Mostra cada caso que falhou, com o que saiu e o que se esperava, e sai com codigo 0
quando tudo passa. Precisa do git; so usa a biblioteca padrao.
"""

import subprocess
import sys
from pathlib import Path

PROGRAMA = "confere_links.py"  # a ferramenta, na pasta dada
INICIO_DO_ERRO = "ERRO "  # o comeco de uma linha de erro da ferramenta
ANTES_DO_MOTIVO = " — "  # numa linha ERRO, o que separa o link do motivo
CODIFICACAO = "utf-8"  # a dos arquivos dos repositorios inventados
DOCUMENTO = "a.md"  # em cada grupo de links, o documento com um link em cada linha

# cada linha do documento principal; os numeros das linhas esperadas saem daqui
A = [
    "# Título Á",                                                        # 1
    "",                                                                   # 2
    "## Seção com `código` e [link](b.md)",                              # 3
    "",                                                                   # 4
    "## Repetido",                                                        # 5
    "## Repetido",                                                        # 6
    "",                                                                   # 7
    "Certo [b](b.md) e [x](b.md#seção-b); quebrado [y](nao-existe.md).",  # 8
    "Âncora quebrada [z](b.md#nada) e título com código"                  # 9
    " [w](b.md#montar_deckpy--das-planilhas).",
    "Texto que quebra [texto do",                                         # 10
    "link](b.md#seção-b) e outro [texto",                                 # 11
    "quebrado](b.md#errada).",                                            # 12
    "No mesmo arquivo [r](#repetido-1), [s](#título-á), [t](#repetido-2)"  # 13
    " e [u](#seção-com-código-e-link).",
    "Externos [e](https://example.org/x#y) e [m](mailto:a@b.c).",         # 14
    "Imagem ![i](img.png) e ![j](falta.png); âncora em imagem [v](img.png#x).",  # 15
    "Com espaço [k](<pasta com espaço/c.md#c>) e [l](pasta%20com%20espa%C3%A7o/c.md#c).",  # 16
    "Pasta [p](pasta%20com%20espa%C3%A7o/) e âncora em pasta [q](pasta%20com%20espa%C3%A7o/#c).",  # 17
    "Código na linha `[n](nao-existe.md)` não conta.",                    # 18
    "",                                                                   # 19
    "```",                                                                # 20
    "[dentro](nao-existe.md)",                                            # 21
    "```",                                                                # 22
    "",                                                                   # 23
    "~~~~",                                                               # 24
    "[dentro](nao-existe.md)",                                            # 25
    "```",                                                                # 26
    "ainda dentro [d](nao-existe.md)",                                    # 27
    "~~~~",                                                               # 28
    "Fora de novo [g](outro.md).",                                        # 29
]

B = ["# B", "", "## Seção B", "", "## `montar_deck.py` — das planilhas", ""]

ESPERADO = [
    "ERRO a.md:8: nao-existe.md — o arquivo não existe",
    "ERRO a.md:9: b.md#nada — a âncora não é de nenhum título nem marcador",
    "ERRO a.md:12: b.md#errada — a âncora não é de nenhum título nem marcador",
    "ERRO a.md:13: #repetido-2 — a âncora não é de nenhum título nem marcador",
    "ERRO a.md:15: falta.png — o arquivo não existe",
    "ERRO a.md:15: img.png#x — âncora num arquivo que não é Markdown",
    "ERRO a.md:17: pasta%20com%20espa%C3%A7o/#c — âncora num arquivo que não é Markdown",
    "ERRO a.md:29: outro.md — o arquivo não existe",
    "ERRO novo.md:1: a.md#sumiu — a âncora não é de nenhum título nem marcador",
    "21 link(s) interno(s), 14 com âncora, 9 erro(s).",
]

# os links para uma linha de um arquivo, um em cada linha do documento, e se cada um da erro
LINKS_DE_LINHA = [
    ("[a primeira](t.txt#L1)", False),
    ("[a ultima](t.txt#L3)", False),
    ("[depois da ultima](t.txt#L4)", True),
    ("[a linha zero](t.txt#L0)", True),
    ("[com l minusculo](t.txt#l1)", True),
    ("[a ultima, sem quebra no fim](u.txt#L2)", False),
    ("[depois da ultima, sem quebra no fim](u.txt#L3)", True),
    ("[num Markdown](m.md#L2)", False),
    ("[depois do fim do Markdown](m.md#L3)", True),
    ("[no proprio documento](#L1)", False),
    ("[numa pasta](p/#L1)", True),
    ("[com espaco](<e e.txt#L1>)", False),
]
# cada arquivo pela lista das linhas dele, ou pelo texto exato: u.txt, cuja ultima linha nao termina em quebra
ARQUIVOS_DE_LINHA = {
    "t.txt": ["um", "dois", "tres"], "u.txt": "um\ndois", "m.md": ["# M", "texto"], "p/x.txt": ["x"], "e e.txt": ["e"],
}

# os links para um marcador (o id ou o name de uma tag HTML), um em cada linha do documento, e se cada um da erro
LINKS_DE_MARCADOR = [
    ("[pelo id](m.md#pelo-id)", False),
    ("[pelo name](m.md#pelo-name)", False),
    ("[entre aspas simples](m.md#aspas-simples)", False),
    ("[sem aspas](m.md#sem-aspas)", False),
    ("[com o atributo em maiusculas](m.md#maiusculas)", False),
    ("[depois de outro atributo](m.md#depois-de-outro)", False),
    ("[pelo valor de outro atributo](m.md#na-classe)", True),
    ("[num texto sem tag](m.md#fora-de-tag)", True),
    ("[que falta](m.md#nao-ha)", True),
    ("[num bloco de codigo](m.md#no-bloco)", True),
    ("[no codigo da linha](m.md#no-codigo)", True),
    ("[num comentario](m.md#no-comentario)", True),
]
ARQUIVOS_DE_MARCADOR = {"m.md": [
    "# M",
    '<a id="pelo-id"></a>',
    '<a name="pelo-name"></a>',
    "<a id='aspas-simples'></a>",
    "<a id=sem-aspas></a>",
    '<a ID="maiusculas"></a>',
    '<a class="na-classe" id="depois-de-outro"></a>',
    "Texto com id=fora-de-tag e nenhuma tag.",
    "```",
    '<a id="no-bloco"></a>',
    "```",
    'Código na linha `<a id="no-codigo"></a>`.',
    "<!--",
    '<a id="no-comentario"></a>',
    "-->",
]}

# cada grupo de links: o nome, os links, os arquivos que eles alcancam e o que o grupo confere
GRUPOS = [
    ("linhas", LINKS_DE_LINHA, ARQUIVOS_DE_LINHA, "o link para uma linha só dá erro quando o arquivo não tem a linha"),
    ("marcadores", LINKS_DE_MARCADOR, ARQUIVOS_DE_MARCADOR,
     "o link para um marcador só dá erro quando o id ou o name falta fora de código e de comentário"),
]


def alvo(link):
    """O alvo de um link [texto](alvo), sem os <> em volta."""
    return link[link.index("](") + 2:-1].strip("<>")


def git(pasta, *args):
    subprocess.run(["git", "-C", str(pasta), *args], check=True, capture_output=True)


def roda(ferramenta, pasta):
    r = subprocess.run([sys.executable, "-I", str(ferramenta), str(pasta)],
                       capture_output=True, text=True)
    return r.returncode, r.stdout.splitlines(), r.stderr


def monta(pasta, arquivos, versionados):
    """Um repositorio git novo com os arquivos dados, cada um pela lista das linhas dele ou
    pelo texto exato, e os versionados no indice."""
    pasta.mkdir()
    git(pasta, "init", "-q")
    for nome, conteudo in arquivos.items():
        caminho = pasta / nome
        caminho.parent.mkdir(parents=True, exist_ok=True)
        texto = conteudo if isinstance(conteudo, str) else "\n".join(conteudo) + "\n"
        caminho.write_text(texto, encoding=CODIFICACAO)
    git(pasta, "add", "--", *versionados)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    ferramenta, trabalho = Path(argv[0]).resolve() / PROGRAMA, Path(argv[1]).resolve()
    if trabalho.exists() and (not trabalho.is_dir() or any(trabalho.iterdir())):
        print(f"a pasta de trabalho precisa ser nova ou estar vazia: {trabalho}", file=sys.stderr)
        return 2
    trabalho.mkdir(parents=True, exist_ok=True)
    falhas = []

    def caso(nome, obtido, esperado):
        if obtido != esperado:
            falhas.append(f"FALHOU {nome}\n  saiu:     {obtido!r}\n  esperado: {esperado!r}")

    com_erros = trabalho / "com-erros"
    monta(com_erros, {
        "a.md": A, "b.md": B, "img.png": [""], "pasta com espaço/c.md": ["# C"],
        "novo.md": ["Link [a](a.md#sumiu)."],
        "ignorado.md": ["Link [x](nao-existe.md)."], ".gitignore": ["ignorado.md"],
    }, ["a.md", "b.md", "img.png", "pasta com espaço/c.md", ".gitignore"])
    codigo, saida, _ = roda(ferramenta, com_erros)
    caso("links quebrados, um por linha, em ordem", saida, ESPERADO)
    caso("código de saída com erro", codigo, 1)
    caso("a mesma saída em duas rodadas", roda(ferramenta, com_erros)[1], saida)

    for nome, todos, arquivos, regra in GRUPOS:
        sem_erro = [link for link in todos if not link[1]]
        for pasta, links in ((trabalho / nome, todos), (trabalho / f"{nome}-sem-erro", sem_erro)):
            monta(pasta, {**arquivos, DOCUMENTO: [link for link, _ in links]}, [DOCUMENTO, *arquivos])
            codigo, saida, _ = roda(ferramenta, pasta)
            erros = sorted(linha.split(ANTES_DO_MOTIVO)[0] for linha in saida if linha.startswith(INICIO_DO_ERRO))
            esperados = sorted(f"{INICIO_DO_ERRO}{DOCUMENTO}:{n}: {alvo(link)}"
                               for n, (link, erro) in enumerate(links, 1) if erro)
            caso(f"{pasta.name}: {regra}", erros, esperados)
            caso(f"{pasta.name}: código de saída", codigo, 1 if esperados else 0)

    certo = trabalho / "certo"
    monta(certo, {"a.md": ["# A", "", "[b](b.md#b) e [a](#a)."], "b.md": ["# B"]},
          ["a.md", "b.md"])
    caso("tudo certo", roda(ferramenta, certo)[:2], (0, ["2 link(s) interno(s), 2 com âncora, 0 erro(s)."]))

    sem_git = trabalho / "sem-git"
    sem_git.mkdir()
    (sem_git / "a.md").write_text("[x](y.md)\n", encoding=CODIFICACAO)
    caso("pasta sem git", roda(ferramenta, sem_git)[0], 2)

    for f in falhas:
        print(f)
    print(f"{len(falhas)} falha(s).")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
