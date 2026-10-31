"""Testa o confere_links.py com repositorios git inventados.

Os nomes dos documentos, dos arquivos e das pastas, os titulos, os marcadores, os textos dos
links, o numero de linhas dos arquivos e a ordem dos casos sao sorteados, sempre os mesmos,
porque a semente e fixa (outra vem com --semente), com letras de fora do ASCII. O teste
confere regras, nunca uma frase pronta:
  - cada link quebrado, e so ele, sai numa linha ERRO com o documento, a linha do comeco do
    alvo e o alvo, em ordem de documento e de linha, e depois delas so sai o resumo;
  - o mesmo problema sai sempre com o mesmo motivo, e problemas diferentes, com motivos
    diferentes;
  - o resumo diz, nessa ordem, o numero de links internos, o dos com ancora e o de erros;
  - o codigo de saida e 1 com link quebrado e 0 sem nenhum;
  - a pasta sem git e o documento, ou o Markdown de destino de uma ancora, que nao se le em
    UTF-8 saem com 2 e so com uma linha ERRO, que diz a pasta ou o arquivo;
  - duas rodadas dao a mesma saida.
Uso:
    python3 -I teste_confere_links.py <pasta do confere_links.py> <pasta de trabalho nova> [--semente N]
Precisa do git, que o teste roda sem a configuracao do sistema e da conta (que poderia deixar
arquivos de fora) e sem subir da pasta de trabalho (que poderia estar dentro de outro
repositorio).
"""
import argparse
import os
import random
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

LEITOR = argparse.ArgumentParser(description="Testa o confere_links.py com repositórios git inventados.")
LEITOR.add_argument("peca", type=Path, help="a pasta do confere_links.py")
LEITOR.add_argument("trabalho", type=Path, help="uma pasta de trabalho nova ou vazia")
LEITOR.add_argument("--semente", type=int, default=3, help="a semente do sorteio")
ARGS = LEITOR.parse_args()
PROGRAMA = ARGS.peca.resolve() / "confere_links.py"
TRABALHO = ARGS.trabalho.resolve()
if TRABALHO.exists() and (not TRABALHO.is_dir() or any(TRABALHO.iterdir())):
    print(f"ERRO: a pasta de trabalho precisa ser nova ou estar vazia: {TRABALHO}")
    sys.exit(2)
GIT = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
       "GIT_CEILING_DIRECTORIES": str(TRABALHO)}

SORTE = random.Random(ARGS.semente)
FALHAS = []
USADAS = set()  # as palavras ja sorteadas, para que nenhuma se repita
CODIFICACAO = "utf-8"  # a dos arquivos dos repositorios e a da saida
LATIN = "latin-1"  # a dos arquivos que nao se leem em UTF-8
LETRAS = "abcdefghijklmnopqrstuvwxyz"
ACENTUADAS = "áéíóúâêôãõçàüñ"  # letras com acento; em latin-1, nenhuma forma um caractere do UTF-8
PONTUACAO = ".,;:!?'/+=*@"  # pontuacao no meio de uma palavra de titulo, que sai da ancora
SOLTAS = "—·:/&+"  # pontuacao solta entre espacos num titulo: sai da ancora, e os espacos ficam
ESQUEMA = LETRAS + LETRAS.upper() + "0123456789+.-"  # os caracteres de um esquema, como https, depois do primeiro
ATRIBUTOS = ("id", "name")  # os atributos de uma tag HTML que marcam um lugar
ASPAS = ('"', "'", "")  # o valor de um atributo entre aspas duplas, entre simples ou sem aspas
TAGS = ("a", "span", "div", "p")
CERCAS = "`~"  # os sinais de uma cerca de bloco de codigo
LINHA_DE_ERRO = re.compile(r"^ERRO (.+?):(\d+): (.+) — (.+)$")  # ERRO arquivo:linha: alvo — motivo
NUMERO = re.compile(r"\d+")
# os problemas de um link, como o teste os separa
FALTA, SEM_LINHA = "o arquivo falta", "a linha falta"
FORA, SEM_ANCORA = "âncora fora de um Markdown", "a âncora falta"


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)


def palavra():
    """Uma palavra sorteada, em minusculas, sempre com uma letra com acento, que ainda nao saiu."""
    while True:
        letras = [SORTE.choice(LETRAS + ACENTUADAS) for _ in range(SORTE.randint(2, 6))]
        letras.insert(SORTE.randrange(len(letras) + 1), SORTE.choice(ACENTUADAS))
        nova = "".join(letras)
        if nova not in USADAS:
            USADAS.add(nova)
            return nova


def maiusculas(texto):
    """O texto com uma ou mais letras em maiusculas, sorteadas."""
    certa = SORTE.randrange(len(texto))
    return "".join(c.upper() if i == certa or SORTE.random() < 0.3 else c for i, c in enumerate(texto))


def pontuada(texto):
    """O texto com uma ou duas pontuacoes sorteadas no meio."""
    letras = list(texto)
    for _ in range(SORTE.randint(1, 2)):
        letras.insert(SORTE.randint(1, len(letras) - 1), SORTE.choice(PONTUACAO))
    return "".join(letras)


def frase(*partes):
    """Uma linha com as partes entre palavras sorteadas."""
    return " ".join([palavra(), *(f"{parte} {palavra()}" for parte in partes)]) + "."


def link(alvo):
    """Um link sorteado para o alvo: com ou sem !, com ou sem colchetes no texto, com ou sem
    titulo, com ou sem espacos nos parenteses, e com o alvo entre <> quando ele tem espaco e,
    sem espaco, as vezes."""
    texto = f"{palavra()} [{palavra()}] {palavra()}" if SORTE.random() < 0.3 else palavra()
    escrito = f"<{alvo}>" if " " in alvo or SORTE.random() < 0.3 else alvo
    titulo = f' "{palavra()}"' if SORTE.random() < 0.3 else ""
    antes, depois = (" " * SORTE.randint(0, 1) for _ in range(2))
    return f"{SORTE.choice(['', '!'])}[{texto}]({antes}{escrito}{titulo}{depois})"


def falta():
    """O nome de um arquivo que nao existe, com uma extensao sorteada ou sem nenhuma."""
    return palavra() + SORTE.choice([".md", ".txt", ".png", ""])


def esquema():
    """Um esquema de link externo sorteado, como https: ou mailto:."""
    return SORTE.choice(LETRAS) + "".join(SORTE.choice(ESQUEMA) for _ in range(SORTE.randint(0, 5))) + ":"


def em_latin():
    """Um texto sorteado em latin-1, que nao se le em UTF-8."""
    dados = frase(palavra()).encode(LATIN)
    try:
        dados.decode(CODIFICACAO)
    except UnicodeDecodeError:
        return dados
    confere(False, f"o texto em latin-1 não se lê em UTF-8: {dados!r}")
    return dados


def marcador(valor, nome=None, aspas=None, maiuscula=False, antes=""):
    """Uma tag HTML sorteada que marca o valor pelo atributo dado ou sorteado, com letras em
    maiusculas sorteadas (uma pelo menos, quando pedido), e entre as aspas dadas ou sorteadas;
    o texto de antes vai na tag, antes do atributo."""
    tag, nome = SORTE.choice(TAGS), nome or SORTE.choice(ATRIBUTOS)
    nome = maiusculas(nome) if maiuscula else "".join(c.upper() if SORTE.random() < 0.2 else c for c in nome)
    aspas = SORTE.choice(ASPAS) if aspas is None else aspas
    return f"<{tag}{antes} {nome}={aspas}{valor}{aspas}></{tag}>"


class Documento:
    """Um documento inventado: o nome (o caminho no repositorio), as linhas e, de cada link
    interno fora de codigo, em ordem, o numero da linha do comeco do alvo, o alvo como sai no
    ERRO (sem os <>) e o problema que se espera, ou None."""

    def __init__(self, nome, blocos):
        """Os blocos (linhas, links), na ordem dada, separados por uma linha em branco; cada link
        e (indice da linha no bloco, alvo, problema)."""
        self.nome, self.linhas, self.links = nome, [], []
        for linhas, links in blocos:
            if self.linhas:
                self.linhas.append("")
            comeco = len(self.linhas) + 1
            self.linhas += linhas
            self.links += [(comeco + i, alvo, problema) for i, alvo, problema in links]

    def texto(self):
        return "\n".join(self.linhas) + "\n"


def titulos(alvo):
    """Os blocos de titulos de um documento, as ancoras que valem nele e a que nao vale: um
    titulo sorteado, com palavras com maiusculas e com pontuacao no meio, um codigo na linha,
    um link para o alvo (que conta como link do documento), uma tag HTML e pontuacao solta; e
    um titulo repetido de duas a quatro vezes, com e sem maiusculas, cuja ancora ganha -1,
    -2... depois da primeira vez."""
    palavras = [palavra() for _ in range(SORTE.randint(1, 3))]
    codigo, no_link, na_tag, tag = palavra(), palavra(), palavra(), SORTE.choice(TAGS)
    partes = [*((pontuada(maiusculas(p)), p) for p in palavras), (f"`{pontuada(maiusculas(codigo))}`", codigo),
              (f"[{maiusculas(no_link)}]({alvo})", no_link), (f"<{tag}>{maiusculas(na_tag)}</{tag}>", na_tag),
              (SORTE.choice(SOLTAS), "")]
    SORTE.shuffle(partes)
    nivel = "#" * SORTE.randint(1, 6)
    blocos = [([f"{' ' * SORTE.randint(0, 3)}{nivel} {' '.join(e for e, _ in partes)}"], [(0, alvo, None)])]
    base, vezes = palavra(), SORTE.randint(2, 4)
    blocos += [([f"{'#' * SORTE.randint(1, 6)} {SORTE.choice([base, maiusculas(base)])}"], []) for _ in range(vezes)]
    certas = ["-".join(a for _, a in partes), base, *(f"{base}-{n}" for n in range(1, vezes))]
    return blocos, certas, [f"{base}-{vezes}"]


def destino():
    """O documento de destino das ancoras, com os blocos na ordem sorteada, e as ancoras que
    valem nele e as que nao valem: as dos titulos; as dos marcadores pelo id e pelo name, entre
    aspas duplas, entre simples e sem aspas, com o atributo em maiusculas e depois de outro
    atributo, valem; o valor do outro atributo, o de um texto sem tag, o que falta e os de um
    bloco de codigo (com um titulo), de um codigo na linha e de um comentario de varias linhas
    nao valem."""
    blocos, certas, quebradas = titulos(TEXTO)
    for nome in ATRIBUTOS:
        for aspas in ASPAS:
            certas.append(palavra())
            blocos.append(([frase(marcador(certas[-1], nome, aspas))], []))
    certas.append(palavra())
    blocos.append(([marcador(certas[-1], maiuscula=True)], []))
    outro, aspas = palavra(), SORTE.choice(ASPAS)
    certas.append(palavra())
    blocos.append(([marcador(certas[-1], antes=f" data-{SORTE.choice(LETRAS)}={aspas}{outro}{aspas}")], []))
    sem_tag, nenhum, no_bloco, titulo_no_bloco, na_linha, no_comentario = (palavra() for _ in range(6))
    quebradas += [outro, sem_tag, nenhum, no_bloco, titulo_no_bloco, na_linha, no_comentario]
    cerca, crase = SORTE.choice(CERCAS) * SORTE.randint(3, 5), "`" * SORTE.randint(1, 2)
    blocos += [([frase(f"{SORTE.choice(ATRIBUTOS)}={sem_tag}")], []),
               ([cerca, f"## {titulo_no_bloco}", frase(marcador(no_bloco)), cerca], []),
               ([frase(f"{crase}{marcador(na_linha)}{crase}")], []),
               (["<!--", frase(marcador(no_comentario)), "-->"], [])]
    SORTE.shuffle(blocos)
    return Documento(f"{palavra()}.md", blocos), certas, quebradas


def em_linhas(links):
    """Os links (alvo, problema) em blocos de uma linha, de um a tres em cada, na ordem sorteada."""
    links, blocos = SORTE.sample(links, len(links)), []
    while links:
        n = SORTE.randint(1, 3)
        juntos, links = links[:n], links[n:]
        blocos.append(([frase(*(link(alvo) for alvo, _ in juntos))],
                       [(0, alvo, problema) for alvo, problema in juntos]))
    return blocos


def externos():
    """Um bloco com links externos, de esquema sorteado, com e sem ancora, que nao contam."""
    alvos = [f"{esquema()}{palavra()}", f"{esquema()}//{palavra()}/{palavra()}#{palavra()}"]
    return [frase(*map(link, alvos))], []


def codigos():
    """Os blocos com codigo: um link num codigo na linha e um num bloco de codigo, que nao
    contam; e um bloco cercado por um sinal, com uma cerca do outro sinal e uma mais curta do
    mesmo sinal, que nao o fecham, cada uma seguida de um link, que nao conta, e, logo depois
    da cerca que o fecha, um link quebrado, que conta."""
    crase, cerca = "`" * SORTE.randint(1, 2), SORTE.choice(CERCAS) * SORTE.randint(3, 5)
    sinal = SORTE.choice(CERCAS)
    outro, n, depois = CERCAS.replace(sinal, ""), SORTE.randint(4, 6), falta()
    return [([frase(f"{crase}{link(falta())}{crase}")], []),
            ([f"{cerca}{palavra()}", frase(link(falta())), cerca], []),
            ([sinal * n, outro * SORTE.randint(3, n + 2), frase(link(falta())), sinal * SORTE.randint(3, n - 1),
              frase(link(falta())), sinal * SORTE.randint(n, n + 2), frase(link(depois))], [(6, depois, FALTA)])]


def em_duas_linhas():
    """Um bloco com dois links de texto quebrado em duas linhas, um certo e um quebrado; a linha
    de cada um e a do comeco do alvo."""
    certo, quebrado = f"{DESTINO.nome}#{SORTE.choice(CERTAS)}", f"{DESTINO.nome}#{palavra()}"
    return ([f"{palavra()} [{palavra()}", f"{palavra()}]({certo}) {palavra()} [{palavra()}",
             f"{palavra()}]({quebrado}) {palavra()}."], [(1, certo, None), (2, quebrado, SEM_ANCORA)])


def git(pasta, *args):
    subprocess.run(["git", "-C", str(pasta), *args], check=True, capture_output=True, env=GIT)


def monta(pasta, arquivos, fora=()):
    """Um repositorio git novo com os arquivos (texto ou bytes), todos no indice menos os de fora."""
    pasta.mkdir(parents=True)
    git(pasta, "init", "-q")
    for nome, conteudo in arquivos.items():
        caminho = pasta / nome
        caminho.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(conteudo, bytes):
            caminho.write_bytes(conteudo)
        else:
            caminho.write_text(conteudo, encoding=CODIFICACAO)
    git(pasta, "add", "--", *(nome for nome in arquivos if nome not in fora))
    return pasta


def roda(pasta):
    """(codigo de saida, linhas da saida padrao) do confere_links.py na pasta."""
    r = subprocess.run([sys.executable, "-I", str(PROGRAMA), str(pasta)], capture_output=True,
                       encoding=CODIFICACAO, env=GIT)
    return r.returncode, r.stdout.splitlines()


def confere_saida(nome, pasta, documentos):
    """Confere a saida do confere_links.py num repositorio com os documentos dados."""
    codigo, saida = roda(pasta)
    esperados = [(doc.nome, n, alvo, problema) for doc in sorted(documentos, key=lambda d: d.nome)
                 for n, alvo, problema in doc.links if problema]
    achados = [m.groups() for m in map(LINHA_DE_ERRO.match, saida) if m]
    alinhados = [(d, int(n), a) for d, n, a, _ in achados] == [e[:3] for e in esperados]
    confere(alinhados, f"{nome}: cada link quebrado, e só ele, sai numa linha ERRO com o documento, a linha do "
                       f"começo do alvo e o alvo, em ordem: {achados} em vez de {esperados}")
    if alinhados:
        motivos = {}
        for (*_, problema), (*_, motivo) in zip(esperados, achados):
            motivos.setdefault(problema, set()).add(motivo)
        confere(all(len(m) == 1 for m in motivos.values()),
                f"{nome}: o mesmo problema sai com o mesmo motivo: {motivos}")
        confere(len({min(m) for m in motivos.values()}) == len(motivos),
                f"{nome}: problemas diferentes saem com motivos diferentes: {motivos}")
    alvos = [alvo for doc in documentos for _, alvo, _ in doc.links]
    resumo = [len(alvos), sum("#" in alvo for alvo in alvos), len(esperados)]  # os links, os com ancora e os erros
    confere(len(saida) == len(achados) + 1 and [int(n) for n in NUMERO.findall(saida[-1])] == resumo,
            f"{nome}: depois das linhas ERRO, só o resumo, com {resumo}: {saida[len(achados):]}")
    confere(codigo == (1 if esperados else 0), f"{nome}: sai com {1 if esperados else 0}, e não com {codigo}")
    confere(roda(pasta) == (codigo, saida), f"{nome}: duas rodadas dão a mesma saída")


def confere_que_nao_serve(nome, pasta, diz):
    """A rodada que nao serve sai com 2 e so com uma linha ERRO, que diz a pasta ou o arquivo."""
    codigo, saida = roda(pasta)
    confere(codigo == 2, f"{nome}: sai com 2, e não com {codigo}")
    confere(len(saida) == 1 and saida[0].startswith("ERRO") and diz in saida[0],
            f"{nome}: só uma linha ERRO, que diz {diz}: {saida}")


# ---- os arquivos que os links alcancam ----

TEXTO, SEM_QUEBRA, IMAGEM = f"{palavra()}.txt", f"{palavra()}.txt", f"{palavra()}.png"
LINHAS_DO_TEXTO, LINHAS_SEM_QUEBRA = SORTE.randint(2, 9), SORTE.randint(2, 9)
PASTA = f"{palavra()} {palavra()}"  # com espaco no nome
INTERNO, TITULO_INTERNO = f"{PASTA}/{palavra()}.md", palavra()
ARQUIVOS = {
    TEXTO: "".join(f"{palavra()}\n" for _ in range(LINHAS_DO_TEXTO)),
    SEM_QUEBRA: "\n".join(palavra() for _ in range(LINHAS_SEM_QUEBRA)),  # sem quebra depois da ultima linha
    IMAGEM: b"\x89PNG\r\n\x1a\n",  # o comeco de um PNG, que nao e texto
    INTERNO: f"# {TITULO_INTERNO}\n",
}
DESTINO, CERTAS, QUEBRADAS = destino()

# ---- os links de uma linha so: (alvo, problema) ----

SIMPLES = [
    (TEXTO, None), (f"{TEXTO}#L1", None), (f"{TEXTO}#L{LINHAS_DO_TEXTO}", None),
    (f"{TEXTO}#L{LINHAS_DO_TEXTO + 1}", SEM_LINHA), (f"{TEXTO}#L0", FORA),
    (f"{TEXTO}#l{SORTE.randint(1, LINHAS_DO_TEXTO)}", FORA),
    (f"{SEM_QUEBRA}#L{LINHAS_SEM_QUEBRA}", None), (f"{SEM_QUEBRA}#L{LINHAS_SEM_QUEBRA + 1}", SEM_LINHA),
    (f"{DESTINO.nome}#L{len(DESTINO.linhas)}", None), (f"{DESTINO.nome}#L{len(DESTINO.linhas) + 1}", SEM_LINHA),
    ("#L1", None), (f"{INTERNO}#L1", None), (f"{quote(PASTA)}/#L1", SEM_LINHA),
    (falta(), FALTA), (f"{falta()}#{palavra()}", FALTA),
    (IMAGEM, None), (f"{IMAGEM}#{palavra()}", FORA),
    (f"{INTERNO}#{TITULO_INTERNO}", None), (f"{quote(INTERNO)}#{quote(TITULO_INTERNO)}", None),
    (f"{quote(PASTA)}/", None), (f"{quote(PASTA)}/#{palavra()}", FORA),
    (DESTINO.nome, None), *((f"{DESTINO.nome}#{a}", None) for a in CERTAS),
    *((f"{DESTINO.nome}#{a}", SEM_ANCORA) for a in QUEBRADAS),
]

# ---- o repositorio com erros: o documento principal, o de destino, um novo e um que o .gitignore deixa de fora ----

blocos, certas, quebradas = titulos(TEXTO)
proprias = [(f"#{a}", None) for a in certas] + [(f"#{a}", SEM_ANCORA) for a in quebradas]  # no proprio documento
blocos += [*em_linhas(SIMPLES + proprias), externos(), *codigos(), em_duas_linhas()]
SORTE.shuffle(blocos)
PRINCIPAL = Documento(f"{palavra()}.md", blocos)
quebrado = falta()
NOVO = Documento(f"{palavra()}.md", [([frase(link(quebrado))], [(0, quebrado, FALTA)])])
IGNORADO = f"{palavra()}.md"
COM_ERROS = [PRINCIPAL, DESTINO, NOVO]
problemas = {problema for doc in COM_ERROS for *_, problema in doc.links}
confere(problemas == {None, FALTA, SEM_LINHA, FORA, SEM_ANCORA}, f"o repositório tem todos os problemas: {problemas}")
confere_saida("com erros", monta(TRABALHO / "com-erros", {
    **ARQUIVOS, **{doc.nome: doc.texto() for doc in COM_ERROS},
    IGNORADO: frase(link(falta())) + "\n", ".gitignore": f"{IGNORADO}\n"}, fora=(NOVO.nome, IGNORADO)), COM_ERROS)

# ---- o repositorio sem erro: os links simples que valem ----

CERTO = Documento(f"{palavra()}.md", em_linhas([(alvo, p) for alvo, p in SIMPLES if p is None]))
confere_saida("sem erro", monta(TRABALHO / "sem-erro", {
    **ARQUIVOS, **{doc.nome: doc.texto() for doc in (CERTO, DESTINO)}}), [CERTO, DESTINO])

# ---- o que nao serve ----

sem_git = TRABALHO / "sem-git"
sem_git.mkdir()
(sem_git / f"{palavra()}.md").write_text(frase(link(falta())) + "\n", encoding=CODIFICACAO)
confere_que_nao_serve("pasta sem git", sem_git, str(sem_git))

legivel, ilegivel = sorted(f"{palavra()}.md" for _ in range(2))  # o que se le vem antes, com um link quebrado
confere_que_nao_serve("documento que não se lê em UTF-8", monta(TRABALHO / "documento-ilegivel", {
    legivel: frase(link(falta())) + "\n", ilegivel: em_latin()}), ilegivel)

ilegivel = f"{palavra()}.md"  # fora do git, so lido como destino de uma ancora, depois de um link quebrado
confere_que_nao_serve("Markdown de destino de uma âncora que não se lê em UTF-8", monta(
    TRABALHO / "destino-ilegivel", {f"{palavra()}.md": frase(link(falta()), link(f"{ilegivel}#{palavra()}")) + "\n",
                                    ilegivel: em_latin(), ".gitignore": f"{ilegivel}\n"}, fora=(ilegivel,)), ilegivel)

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s) (semente {ARGS.semente})")
sys.exit(1 if FALHAS else 0)
