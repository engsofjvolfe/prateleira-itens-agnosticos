"""Testes de confere_changelog.py.

Tudo e inventado e sorteado, com uma semente fixa (outra vem com --semente): os nomes da
configuracao (a secao do que nao foi publicado, a marca da versao retirada, os tipos de
mudanca e o fim do item), com letras de fora do ASCII; os modelos dos links; e os
changelogs, com as versoes, as datas, os tipos e os itens sorteados, e os identificadores de
pre-lancamento e de construcao, de letras do ASCII, maiusculas e minusculas, e hifen. Nada e
de um projeto real. Os testes conferem o que a peca faz, nunca uma frase pronta:
  - o changelog na forma passa: com versao retirada ou sem, com a secao do que nao foi
    publicado com tipos ou vazia, sem versao nenhuma, com item de varias linhas e com o
    comeco de varios paragrafos; com os pre-lancamentos na ordem da precedencia, como no
    exemplo da especificacao, e com metadados de construcao; e, com os modelos dos links, com
    os links de cada secao, tambem com uma versao so, e sem link nenhum quando nao ha versao;
  - cada defeito da ERRO na linha dele, e so nela: o titulo que falta; o titulo no comeco; a
    secao do que nao foi publicado que falta, repetida ou depois de uma versao; a versao com
    zero na frente, sem a data, com a data que nao existe, com outra marca de retirada, fora
    da ordem ou repetida; a versao fora da forma do Versionamento Semantico (o pre-lancamento
    ou o identificador vazio, o identificador so de algarismos com zero na frente ou com
    outro sinal, o algarismo de fora do ASCII, os metadados vazios); o pre-lancamento fora da
    ordem, a versao normal depois do pre-lancamento dela e as versoes que so mudam nos
    metadados de construcao; a data fora da ordem; o tipo desconhecido, fora da ordem,
    repetido ou sem item; a versao sem tipo; o item sem o fim, tambem o de varias linhas com o
    fim so na primeira; a linha com um espaco no comeco, a solta e o titulo de nivel 4; a
    linha em branco que falta antes ou depois de um titulo, a dobrada e a que fica entre
    itens; o arquivo sem a quebra no fim ou com linha em branco no fim; o item fora de um
    tipo; a continuacao fora de um item; os links sem os modelos deles; e, com os modelos, o
    link errado, a mais, que falta, fora da ordem, ou sem a linha em branco antes;
  - com --indice, o conferido e o changelog do indice do git, e nao o da pasta, com as
    quebras de linha lidas como as de um arquivo, de qualquer pasta de onde o comando roda;
  - a configuracao fora do molde (tambem com os links dentro dela), de outra versao, sem
    tipo, com tipo vazio ou repetido, com o fim vazio ou com um nome de duas linhas; o
    arquivo dos links que nao existe, fora do molde, de outra versao, sem um modelo, com um
    modelo de duas linhas, sem o lugar de um campo dele ou com o de outro, com o erro que
    diz o arquivo; o changelog que nao existe e o que nao e UTF-8; e, com --indice, o
    arquivo fora do indice, o do indice que nao e UTF-8 e o de fora de um repositorio: saem
    com 2;
  - os erros saem em ordem de linha, e a mesma entrada da a mesma saida.
Uso:
    python3 -I teste_confere_changelog.py <pasta de confere_changelog.py> <pasta de trabalho nova> [--semente N]
Precisa do git, que o teste roda sem a configuracao do sistema e da conta e sem subir da pasta
de trabalho (que poderia estar dentro de outro repositorio).
"""
import argparse
import datetime
import itertools
import json
import os
import random
import string
import subprocess
import sys
import unicodedata
from pathlib import Path

LEITOR = argparse.ArgumentParser(description="Testes de confere_changelog.py.")
LEITOR.add_argument("peca", type=Path, help="a pasta de confere_changelog.py")
LEITOR.add_argument("trabalho", type=Path, help="uma pasta de trabalho nova")
LEITOR.add_argument("--semente", type=int, default=17, help="a semente do sorteio")
ARGS = LEITOR.parse_args()

PROGRAMA = ARGS.peca.resolve() / "confere_changelog.py"
TRABALHO = ARGS.trabalho.resolve()
GIT = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
       "GIT_CEILING_DIRECTORIES": str(TRABALHO)}
SORTE = random.Random(ARGS.semente)
FALHAS = []
LETRAS = string.ascii_lowercase + "áçõüé"
ITEM, CONTINUACAO, TIPO = "- ", "  ", "### "  # a forma, pelo README


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


# ---- o sorteio ----

def palavra():
    return "".join(SORTE.choice(LETRAS) for _ in range(SORTE.randint(3, 8)))


def frase():
    return " ".join(palavra() for _ in range(SORTE.randint(2, 6)))


def identificador(primeira=None):
    """Um identificador de pre-lancamento ou de construcao, de letras do ASCII e hifen: a primeira letra dada, ou
    sorteada, e as outras sorteadas."""
    return (primeira or SORTE.choice(string.ascii_letters)) + "".join(
        SORTE.choice(string.ascii_letters + "-") for _ in range(SORTE.randint(0, 5)))


NOMES = iter(sorted({palavra().capitalize() for _ in range(40)}))
NAO_PUBLICADO, REMOVIDA = f"{next(NOMES)} {next(NOMES)}", next(NOMES).upper()
TIPOS = [next(NOMES) for _ in range(SORTE.randint(4, 6))]
SORTE.shuffle(TIPOS)
FIM = SORTE.choice([unicodedata.lookup("HORIZONTAL ELLIPSIS"), "!", ";", "."])
CONFIG = {"versao_schema": 1, "nao_publicado": NAO_PUBLICADO, "removida": REMOVIDA, "tipos": TIPOS,
          "fim_do_item": FIM}
SITIO = f"https://{palavra()}.invalido/{palavra()}"
LINKS = {"nao_publicado": f"{SITIO}/{{anterior}}...{palavra()}", "versao": f"{SITIO}/{{anterior}}...{{versao}}",
         "primeira": f"{SITIO}/{palavra()}/{{versao}}"}


def datas(quantas):
    """As datas de tantas versoes, da mais nova para a mais velha, algumas iguais."""
    dia, saida = datetime.date(2031, 12, 31), []
    for _ in range(quantas):
        dia -= datetime.timedelta(days=SORTE.randint(0, 60))
        saida.append(dia)
    return saida


def versoes_sorteadas(quantas):
    """(versao, data) da mais nova para a mais velha, as datas na mesma ordem, algumas iguais."""
    numeros = set()
    while len(numeros) < quantas:
        numeros.add((SORTE.randint(0, 3), SORTE.randint(0, 12), SORTE.randint(0, 12)))
    return [(".".join(str(n) for n in numero), dia) for numero, dia in zip(sorted(numeros, reverse=True),
                                                                            datas(quantas))]


def item(linhas=None):
    """Um item de tantas linhas, ou de uma a tres, a ultima com o fim."""
    textos = [frase() for _ in range(linhas or SORTE.randint(1, 3))]
    textos[-1] += FIM
    return [ITEM + textos[0]] + [CONTINUACAO + t for t in textos[1:]]


def sorteados():
    """De um tipo a todos, na ordem da lista, cada um com de um a tres itens."""
    escolhidos = sorted(SORTE.sample(range(len(TIPOS)), SORTE.randint(1, len(TIPOS))))
    return [(TIPOS[i], [item() for _ in range(SORTE.randint(1, 3))]) for i in escolhidos]


def secao(titulo, tipos):
    """O titulo, a linha em branco e cada tipo, com os itens dele e a linha em branco."""
    linhas = [titulo, ""]
    for nome, itens in tipos:
        linhas += [TIPO + nome, ""] + [linha for i in itens for linha in i] + [""]
    return linhas


def titulo_da_versao(versao, data, retirada=False):
    return f"## [{versao}] - {data.isoformat()}" + (f" [{REMOVIDA}]" if retirada else "")


def links_de(versoes):
    """As linhas dos links, como o README as escreve, de cada secao, na ordem."""
    nomes = [v for v, _ in versoes]
    saida = [f"[{NAO_PUBLICADO}]: " + LINKS["nao_publicado"].replace("{anterior}", nomes[0])]
    for i, nome in enumerate(nomes):
        if i + 1 < len(nomes):
            saida.append(f"[{nome}]: " + LINKS["versao"].replace("{versao}", nome).replace("{anterior}", nomes[i + 1]))
        else:
            saida.append(f"[{nome}]: " + LINKS["primeira"].replace("{versao}", nome))
    return saida


def changelog(versoes, nao_publicado=True, links=False, retirada=None):
    """As linhas de um changelog na forma: o comeco, de dois paragrafos; a secao do que nao foi
    publicado, com tipos ou vazia; as versoes, a de indice retirada com a marca, a primeira
    com todos os tipos e o primeiro tipo com um item de tres linhas e outro de uma; e os
    links, quando pedidos."""
    linhas = [f"# {frase()}", "", frase(), frase(), "", frase(), ""]
    linhas += secao(f"## [{NAO_PUBLICADO}]", sorteados() if nao_publicado else [])
    for i, (versao, data) in enumerate(versoes):
        tipos = [(TIPOS[0], [item(3), item(1)])] + [(t, [item()]) for t in TIPOS[1:]] if i == 0 else sorteados()
        linhas += secao(titulo_da_versao(versao, data, i == retirada), tipos)
    return linhas + links_de(versoes) if links and versoes else linhas[:-1]


# ---- a peça ----

TRABALHO.mkdir(parents=True)
NUMEROS = itertools.count()


def grava_json(dados):
    caminho = TRABALHO / f"configuracao-{next(NUMEROS)}.json"
    caminho.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    return caminho


DADOS_DOS_LINKS = {"versao_schema": 1, **LINKS}  # o arquivo do --links, pelo README
CONFIGURACAO, MODELOS = grava_json(CONFIG), grava_json(DADOS_DOS_LINKS)


def grava(linhas, sufixo="\n", caminho=None):
    caminho = caminho or TRABALHO / f"changelog-{next(NUMEROS)}.md"
    caminho.write_text("\n".join(linhas) + sufixo, encoding="utf-8")
    return caminho


def roda(changelog_, config=CONFIGURACAO, indice=False, pasta=TRABALHO, links=None):
    """A peca rodada da pasta dada, com o git sem a configuracao do sistema e da conta, e com o
    arquivo dos links, quando dado."""
    return subprocess.run([sys.executable, "-I", str(PROGRAMA), str(config), str(changelog_),
                           *(["--indice"] if indice else []), *(["--links", str(links)] if links else [])],
                          capture_output=True, text=True, env=GIT, cwd=pasta)


def linhas_dos_erros(resultado, caminho):
    """A linha de cada ERRO do changelog, na ordem da saida."""
    prefixo = f"ERRO {caminho}:"
    return [int(l[len(prefixo):].split(":", 1)[0]) for l in resultado.stdout.splitlines() if l.startswith(prefixo)]


def passa(caso, linhas, links=None):
    caminho = grava(linhas)
    resultado = roda(caminho, links=links)
    confere(resultado.returncode == 0 and not linhas_dos_erros(resultado, caminho),
            f"passa: {caso}: saiu com {resultado.returncode}: {resultado.stdout[-600:]}")


def acusa(caso, linhas, esperadas, sufixo="\n", links=None):
    """O changelog da ERRO nas linhas esperadas (contadas de 1), e so nelas."""
    caminho = grava(linhas, sufixo)
    resultado = roda(caminho, links=links)
    achadas = sorted(set(linhas_dos_erros(resultado, caminho)))
    confere(resultado.returncode == 1 and achadas == sorted(set(esperadas)),
            f"acusa: {caso}: esperado ERRO nas linhas {sorted(set(esperadas))}, saiu com {resultado.returncode} e "
            f"ERRO nas linhas {achadas}: {resultado.stdout[-600:]}")


def nao_serve(caso, config, caminho=None, indice=False, links=None):
    """A rodada sai com 2; com o arquivo dos links, o erro diz o arquivo."""
    resultado = roda(caminho or grava(BASE), config, indice, links=links)
    confere(resultado.returncode == 2 and (links is None or str(links) in resultado.stdout),
            f"não serve: {caso}: saiu com {resultado.returncode}: {resultado.stdout}")


# ---- o changelog na forma ----

VERSOES = versoes_sorteadas(SORTE.randint(3, 5))
RETIRADA = SORTE.randrange(1, len(VERSOES))
BASE = changelog(VERSOES, retirada=RETIRADA)
passa("com uma versão retirada", BASE)
passa("sem versão retirada", changelog(VERSOES))
passa("com a seção do que não foi publicado vazia", changelog(VERSOES, nao_publicado=False))
passa("sem versão nenhuma", changelog([]))
passa("só com a seção do que não foi publicado, vazia", changelog([], nao_publicado=False))
COM_OS_LINKS = changelog(VERSOES, links=True, retirada=RETIRADA)
passa("com os links", COM_OS_LINKS, links=MODELOS)
passa("com os links de uma versão só", changelog(VERSOES[:1], links=True), links=MODELOS)
passa("com os modelos dos links e sem versão", changelog([], links=True), links=MODELOS)

# ---- o pré-lançamento e os metadados de construção ----

# tres identificadores na ordem do ASCII, que nao e a das letras sem contar maiusculas: o primeiro com a maiuscula da
# letra do terceiro, e o segundo com uma letra antes dela
DEPOIS, ANTES = sorted(SORTE.sample(string.ascii_lowercase, 2), reverse=True)
A, B, C = identificador(DEPOIS.upper()), identificador(ANTES), identificador(DEPOIS)
NUCLEO = ".".join(str(SORTE.randint(0, 9)) for _ in range(3))
CONSTRUCAO = f"{identificador()}.0{SORTE.randint(0, 9)}"  # os metadados podem ter zero na frente
CADEIA = [f"{NUCLEO}-{A}", f"{NUCLEO}-{A}.1", f"{NUCLEO}-{A}.{B}", f"{NUCLEO}-{B}", f"{NUCLEO}-{B}.2",
          f"{NUCLEO}-{B}.11", f"{NUCLEO}-{C}.1", f"{NUCLEO}+{CONSTRUCAO}"]  # da menor precedencia para a maior
PRE = list(zip(reversed(CADEIA), datas(len(CADEIA))))
passa("os pré-lançamentos na ordem da precedência, como no exemplo da especificação", changelog(PRE))
COM_PRE = changelog(PRE)
TITULOS_PRE = {v: k for k, l in enumerate(COM_PRE) for v, _ in PRE if l.startswith(f"## [{v}] ")}
TROCADO = list(COM_PRE)
ONZE, DOIS = TITULOS_PRE[f"{NUCLEO}-{B}.11"], TITULOS_PRE[f"{NUCLEO}-{B}.2"]
TROCADO[ONZE] = COM_PRE[ONZE].replace(f"-{B}.11]", f"-{B}.2]")
TROCADO[DOIS] = COM_PRE[DOIS].replace(f"-{B}.2]", f"-{B}.11]")
acusa("o pré-lançamento fora da ordem da precedência", TROCADO, [DOIS + 1])
NORMAL_DEPOIS = changelog(list(zip([f"{NUCLEO}-{C}.1", NUCLEO], datas(2))))
acusa("a versão normal depois do pré-lançamento dela", NORMAL_DEPOIS,
      [k + 1 for k, l in enumerate(NORMAL_DEPOIS) if l.startswith(f"## [{NUCLEO}] ")])
SO_NOS_METADADOS = changelog(list(zip([f"{NUCLEO}+{identificador()}", f"{NUCLEO}+{CONSTRUCAO}"], datas(2))))
acusa("as versões que só mudam nos metadados de construção", SO_NOS_METADADOS,
      [k + 1 for k, l in enumerate(SO_NOS_METADADOS) if l.startswith(f"## [{NUCLEO}+{CONSTRUCAO}] ")])

# ---- cada defeito, na linha dele ----

S = [k for k, l in enumerate(BASE) if l.startswith("## ")]  # as secoes: a do que nao foi publicado e as versoes
T = [k for k in range(S[1], S[2]) if BASE[k].startswith(TIPO)]  # os tipos da primeira versao, todos
(V1, D1), (V2, D2) = VERSOES[0], VERSOES[1]


def com(k, *novas, tira=1):
    """Uma copia da base com as linhas novas no lugar de tira linhas a partir de k."""
    return BASE[:k] + list(novas) + BASE[k + tira:]


def sem_fim(linha):
    return linha[:-len(FIM)]


acusa("a primeira linha sem o título", com(0, frase()), [1])
acusa("um título no começo", com(2, f"{TIPO}{frase()}", tira=0), [3])
acusa("falta a seção do que não foi publicado", BASE[:S[0]] + BASE[S[1]:], [S[0] + 1])
acusa("a seção do que não foi publicado repetida", com(S[2], f"## [{NAO_PUBLICADO}]", "", tira=0), [S[2] + 1])
DEPOIS_DA_VERSAO = BASE[:S[0]] + BASE[S[1]:S[2]] + BASE[S[0]:S[1]] + BASE[S[2]:]
acusa("a seção do que não foi publicado depois de uma versão", DEPOIS_DA_VERSAO, [S[0] + 1, S[0] + S[2] - S[1] + 1])
acusa("a versão com zero na frente", com(S[2], f"## [0{V2}] - {D2.isoformat()}"), [S[2] + 1])
acusa("a versão sem a data", com(S[2], f"## [{V2}]"), [S[2] + 1])
acusa("a data que não existe", com(S[2], f"## [{V2}] - {D2.year}-02-30"), [S[2] + 1])
acusa("outra marca de retirada", com(S[2], f"## [{V2}] - {D2.isoformat()} [{palavra()}]"), [S[2] + 1])
ALGARISMO_DE_FORA = unicodedata.lookup("ARABIC-INDIC DIGIT THREE")  # um algarismo que nao e do ASCII
for caso, versao in (("o pré-lançamento vazio", f"{V2}-"), ("o identificador vazio", f"{V2}-{A}..{B}"),
                     ("o identificador só de algarismos com zero na frente", f"{V2}-0{SORTE.randint(1, 9)}"),
                     ("o identificador com outro sinal", f"{V2}-{A}_{B}"),
                     ("o algarismo de fora do ASCII", f"{V2}-{SORTE.randint(1, 9)}{ALGARISMO_DE_FORA}"),
                     ("os metadados de construção vazios", f"{V2}+"),
                     ("o identificador de construção vazio", f"{V2}+{A}..1")):
    acusa(f"a versão fora da forma do Versionamento Semântico: {caso}", com(S[2], titulo_da_versao(versao, D2)),
          [S[2] + 1])
FORA_DA_ORDEM = com(S[1], titulo_da_versao(V2, D1))
FORA_DA_ORDEM[S[2]] = titulo_da_versao(V1, D2)
acusa("a versão fora da ordem", FORA_DA_ORDEM, [S[2] + 1])
acusa("a versão repetida", com(S[2], titulo_da_versao(V1, D2)), [S[2] + 1])
acusa("a data fora da ordem", com(S[2], titulo_da_versao(V2, D1 + datetime.timedelta(days=1))), [S[2] + 1])
acusa("o tipo desconhecido", com(T[0], f"{TIPO}{frase()}"), [T[0] + 1])
TROCADOS = com(T[0], TIPO + TIPOS[1])
TROCADOS[T[1]] = TIPO + TIPOS[0]
acusa("os tipos fora da ordem", TROCADOS, [T[1] + 1])
acusa("o tipo repetido", com(T[1], TIPO + TIPOS[0]), [T[1] + 1])
acusa("o tipo sem item", com(T[1] + 2, tira=T[2] - T[1] - 2), [T[1] + 1])
acusa("a versão sem tipo", com(S[2] + 2, tira=S[3] - S[2] - 2), [S[2] + 1])
acusa("o item sem o fim", com(T[0] + 5, sem_fim(BASE[T[0] + 5])), [T[0] + 6])
NA_PRIMEIRA = com(T[0] + 2, BASE[T[0] + 2] + FIM)
NA_PRIMEIRA[T[0] + 4] = sem_fim(BASE[T[0] + 4])
acusa("o item de várias linhas com o fim só na primeira", NA_PRIMEIRA, [T[0] + 5])
acusa("a linha com um espaço no começo", com(T[0] + 6, " " + frase(), tira=0), [T[0] + 7])
acusa("a linha solta", com(T[0] + 6, frase(), tira=0), [T[0] + 7])
acusa("o título de nível 4", com(T[0] + 6, f"#### {frase()}", tira=0), [T[0] + 7])
acusa("falta a linha em branco antes do título", com(T[1] - 1), [T[1]])
acusa("falta a linha em branco depois do título", com(T[1] + 1), [T[1] + 1])
acusa("a linha em branco dobrada", com(T[1], "", tira=0), [T[1] + 1])
acusa("a linha em branco entre itens", com(T[0] + 5, "", tira=0), [T[0] + 6])
acusa("o arquivo sem a quebra no fim", BASE, [len(BASE)], sufixo="")
acusa("a linha em branco no fim", BASE, [len(BASE) + 1], sufixo="\n\n")
acusa("o item fora de um tipo", com(S[1] + 2, *item(1), "", tira=0), [S[1] + 3])
acusa("a continuação fora de um item", com(S[0] + 2, CONTINUACAO + frase(), "", tira=0), [S[0] + 3])

# ---- os links ----

PRIMEIRO_LINK = len(COM_OS_LINKS) - len(VERSOES) - 1  # o indice do link da secao do que nao foi publicado
acusa("os links sem os modelos deles", COM_OS_LINKS, range(PRIMEIRO_LINK + 1, len(COM_OS_LINKS) + 1))
ERRADO = SORTE.randrange(PRIMEIRO_LINK, len(COM_OS_LINKS))
acusa("o link com o endereço errado",
      COM_OS_LINKS[:ERRADO] + [COM_OS_LINKS[ERRADO] + palavra()] + COM_OS_LINKS[ERRADO + 1:], [ERRADO + 1],
      links=MODELOS)
acusa("o link a mais", COM_OS_LINKS + [f"[{palavra()}]: {SITIO}"], [len(COM_OS_LINKS) + 1], links=MODELOS)
acusa("falta o último link", COM_OS_LINKS[:-1], [len(COM_OS_LINKS) - 1], links=MODELOS)
acusa("os links fora da ordem", COM_OS_LINKS[:-2] + [COM_OS_LINKS[-1], COM_OS_LINKS[-2]],
      [len(COM_OS_LINKS) - 1, len(COM_OS_LINKS)], links=MODELOS)
acusa("falta a linha em branco antes dos links",
      COM_OS_LINKS[:PRIMEIRO_LINK - 1] + COM_OS_LINKS[PRIMEIRO_LINK:], [PRIMEIRO_LINK], links=MODELOS)
acusa("faltam os links", BASE, [len(BASE)], links=MODELOS)
SEM_VERSAO = changelog([])
acusa("o link sem versão", SEM_VERSAO + ["", f"[{NAO_PUBLICADO}]: {SITIO}"], [len(SEM_VERSAO) + 2], links=MODELOS)

# ---- o índice do git ----

REPOSITORIO = TRABALHO / "repositorio"
SUB = REPOSITORIO / palavra()  # uma pasta do repositorio, de onde o comando tambem roda
SUB.mkdir(parents=True)


def git(*args):
    subprocess.run(["git", "-C", str(REPOSITORIO), *args], check=True, capture_output=True, env=GIT)


def no_indice(nome, conteudo):
    """O arquivo do repositorio com o conteudo (texto ou bytes) no indice do git."""
    caminho = REPOSITORIO / nome
    if isinstance(conteudo, bytes):
        caminho.write_bytes(conteudo)
    else:
        caminho.write_text(conteudo, encoding="utf-8")
    git("add", "--", nome)
    return caminho


git("init", "-q")
COM_ERRO = com(0, frase())  # o titulo que falta: ERRO na linha 1
INDICE = no_indice("CHANGELOG.md", "\n".join(BASE) + "\n")
grava(COM_ERRO, caminho=INDICE)  # a pasta muda depois do indice
for pasta in (TRABALHO, SUB):
    resultado = roda(INDICE, indice=True, pasta=pasta)
    confere(resultado.returncode == 0 and not linhas_dos_erros(resultado, INDICE),
            f"com --indice, rodado de {pasta.name}, confere o changelog do índice: {resultado.stdout[-300:]}")
resultado = roda(INDICE)
confere(resultado.returncode == 1 and linhas_dos_erros(resultado, INDICE) == [1],
        f"sem --indice, confere o changelog da pasta: {resultado.stdout[-300:]}")
no_indice("CHANGELOG.md", "\n".join(COM_ERRO) + "\n")
grava(BASE, caminho=INDICE)
resultado = roda(INDICE, indice=True)
confere(resultado.returncode == 1 and linhas_dos_erros(resultado, INDICE) == [1],
        f"com --indice, o ERRO é o do changelog do índice: {resultado.stdout[-300:]}")
CRLF = no_indice(f"{palavra()}.md", ("\r\n".join(BASE) + "\r\n").encode("utf-8"))
for indice in (True, False):
    resultado = roda(CRLF, indice=indice)
    confere(resultado.returncode == 0, f"as quebras de linha do Windows se leem como as de um arquivo, com e sem "
                                       f"--indice ({indice}): {resultado.stdout[-300:]}")

# ---- o que não serve ----

for caso, dados in {
    "um campo desconhecido": dict(CONFIG, outro=1),
    "os tipos que faltam": {c: v for c, v in CONFIG.items() if c != "tipos"},
    "outra versão": dict(CONFIG, versao_schema=CONFIG["versao_schema"] + 1),
    "nenhum tipo": dict(CONFIG, tipos=[]),
    "um tipo vazio": dict(CONFIG, tipos=TIPOS + [""]),
    "um tipo repetido": dict(CONFIG, tipos=TIPOS + TIPOS[:1]),
    "o fim do item vazio": dict(CONFIG, fim_do_item=""),
    "um nome de duas linhas": dict(CONFIG, nao_publicado=f"{palavra()}\n{palavra()}"),
    "os links dentro dela": dict(CONFIG, links=LINKS),
}.items():
    nao_serve(f"a configuração com {caso}", grava_json(dados))
nao_serve("o arquivo dos links que não existe", CONFIGURACAO, links=TRABALHO / f"{palavra()}.json")
for caso, dados in {
    "um campo desconhecido": dict(DADOS_DOS_LINKS, outro=1),
    "outra versão": dict(DADOS_DOS_LINKS, versao_schema=DADOS_DOS_LINKS["versao_schema"] + 1),
    "um modelo que falta": {c: v for c, v in DADOS_DOS_LINKS.items() if c != "primeira"},
    "um modelo de duas linhas": dict(DADOS_DOS_LINKS, versao=f"{SITIO}/{{anterior}}\n{{versao}}"),
    "o modelo sem o lugar da versão anterior": dict(DADOS_DOS_LINKS, versao=f"{SITIO}/{{versao}}"),
    "o modelo sem o lugar da versão": dict(DADOS_DOS_LINKS, primeira=SITIO),
    "o modelo com o lugar de outro campo": dict(DADOS_DOS_LINKS, nao_publicado=f"{SITIO}/{{anterior}}/{{{palavra()}}}"),
}.items():
    nao_serve(f"o arquivo dos links com {caso}", CONFIGURACAO, links=grava_json(dados))
nao_serve("o changelog que não existe", CONFIGURACAO, TRABALHO / "nao-existe.md")
NAO_UTF8 = TRABALHO / "nao-utf8.md"
NAO_UTF8.write_bytes(b"# t\xff\n")
nao_serve("o changelog que não é UTF-8", CONFIGURACAO, NAO_UTF8)
FORA_DO_INDICE = grava(BASE, caminho=REPOSITORIO / f"{palavra()}.md")
nao_serve("com --indice, o arquivo fora do índice", CONFIGURACAO, FORA_DO_INDICE, indice=True)
nao_serve("com --indice, o do índice que não é UTF-8", CONFIGURACAO,
          no_indice(f"{palavra()}.md", b"# t\xff\n"), indice=True)
FORA_DO_REPOSITORIO = TRABALHO / "fora"
FORA_DO_REPOSITORIO.mkdir()
nao_serve("com --indice, o de fora de um repositório", CONFIGURACAO,
          grava(BASE, caminho=FORA_DO_REPOSITORIO / "CHANGELOG.md"), indice=True)

# ---- a ordem e a mesma entrada ----

DOIS_ERROS = grava(com(0, frase()), sufixo="")  # um erro na primeira linha e outro na última
ORDEM = linhas_dos_erros(roda(DOIS_ERROS), DOIS_ERROS)
confere(len(ORDEM) == 2 and ORDEM == sorted(ORDEM), f"os erros saem em ordem de linha: {ORDEM}")
REPETIDO = grava(com(T[1] - 1))
confere(roda(REPETIDO).stdout == roda(REPETIDO).stdout, "a mesma entrada dá a mesma saída")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
