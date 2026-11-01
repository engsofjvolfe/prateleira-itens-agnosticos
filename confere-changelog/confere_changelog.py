"""
Confere a forma de um changelog em Markdown, a do Keep a Changelog 1.1.0, com as versoes do
Versionamento Semantico 2.0.0. A forma do Markdown e a das versoes ficam no codigo; o que
muda de um uso para outro vem da configuracao, so dados: o nome da secao do que nao foi
publicado, a marca da versao retirada, os tipos de mudanca, o fim de cada item e os modelos
dos links.

- o comeco: a primeira linha e o titulo, "# " e um texto; as outras, ate a primeira secao,
  sao texto livre, sem titulo;
- as secoes, "## ": a primeira e a do que nao foi publicado, "## [<nao_publicado>]", que nao
  se repete; cada outra e uma versao, "## [<versao>] - AAAA-MM-DD", com " [<removida>]" no
  fim quando ela foi retirada. A versao e a do Versionamento Semantico inteiro, tambem com o
  pre-lancamento e os metadados de construcao, pela expressao que a especificacao da; a data
  existe; e as versoes vem da mais nova para a mais velha, pela precedencia da
  especificacao, sem duas com a mesma, com as datas na mesma ordem;
- os tipos de mudanca, "### <tipo>": so os da lista, na ordem dela, sem repetir; cada tipo
  com um item ou mais, e cada versao com um tipo ou mais;
- os itens: "- " e o texto, com a continuacao em linhas que comecam por dois espacos; a
  ultima linha de cada item termina com o fim do item;
- as linhas em branco: uma antes e uma depois de cada titulo, e uma antes dos links; o
  arquivo termina com uma quebra de linha, sem linha em branco no fim;
- os links, so com os modelos deles na configuracao e quando ha versao: no fim, um por
  secao, na ordem delas, "[<titulo da secao>]: <link>", com o link feito pelo modelo.

Toda outra linha e erro. O changelog e o arquivo dado ou, com --indice, o texto que o indice
do git tem dele, o que vai no proximo commit, lido pelo git, com as quebras de linha lidas
como na leitura de um arquivo de texto. Mostra uma linha "ERRO arquivo:linha: motivo" por
problema, em ordem de linha, e um resumo; sai com 0 sem erro, 1 com erro e 2 quando a
configuracao, o changelog ou um argumento nao serve. Usa so a biblioteca padrao, o git (com
--indice) e o extrator_comum.py, da peca extrator, na pasta irma "extrator" ou na mesma
pasta.

Uso:
    python3 -I confere_changelog.py <configuracao.json> <CHANGELOG.md> [--indice]
"""

import argparse
import datetime
import io
import re
import subprocess
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "extrator", PASTA):  # na prateleira, a peca extrator fica na pasta irma
    sys.path.insert(0, str(pasta))
from extrator_comum import ErroDeDados, le_conferido, le_texto, preenche  # noqa: E402

MOLDE = PASTA / "esquemas" / "confere-changelog.schema.json"
CODIFICACAO = "utf-8"
CAMPOS_DOS_LINKS = {"nao_publicado": ("anterior",), "versao": ("versao", "anterior"), "primeira": ("versao",)}
# o lugar de cada modelo de link: a secao do que nao foi publicado, depois da versao mais nova; uma versao, depois da
# anterior a ela; e a versao mais velha

# A forma do Markdown do Keep a Changelog.
QUEBRA = "\n"
TITULO = re.compile(r"# \S.*")  # o titulo, na primeira linha
CABECA = "#"  # o comeco de todo titulo
SECAO, TIPO, ITEM, CONTINUACAO = "## ", "### ", "- ", "  "
TITULOS = ("secao", "tipo")  # as classes de linha que sao titulos
DATA = r"[0-9]{4}-[0-9]{2}-[0-9]{2}"
LINK = re.compile(r"\[[^\]]+\]: \S+")

# A versao do Versionamento Semantico 2.0.0: a expressao com grupos de nome que a especificacao da (semver.md, na
# pergunta "Is there a suggested regular expression (RegEx) to check a SemVer string?"), sem as ancoras, que vem da
# forma do titulo; compilada com re.ASCII, para o \d ser so o algarismo do ASCII, como a especificacao pede.
SEMVER = (r"(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
          r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
          r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
          r"(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?")
NUMEROS = ("major", "minor", "patch")  # os grupos dos tres numeros da versao, na ordem
COM_PRE, SEM_PRE = 0, 1  # com os mesmos numeros, a versao com pre-lancamento vem antes da normal


def modelo_de_link(dados, nome):
    """O modelo do link, que o molde ja conferiu, com o lugar de cada campo dele, e de nenhum
    outro."""
    modelo = dados["links"][nome]
    try:
        preenche(modelo, **{c: "" for c in CAMPOS_DOS_LINKS[nome]})  # o lugar de outro campo e erro
    except ErroDeDados as e:
        raise ErroDeDados(f"links/{nome}: {e}") from None
    faltam = [c for c in CAMPOS_DOS_LINKS[nome] if f"{{{c}}}" not in modelo]
    if faltam:
        raise ErroDeDados(f"links/{nome}: o modelo não tem o lugar de {faltam}")
    return modelo


def le_configuracao(caminho):
    """A configuracao, lida pelo molde dela, com a forma do titulo de versao montada com a marca
    da versao retirada e os modelos dos links conferidos."""
    dados = le_conferido(caminho, MOLDE)
    conf = {nome: dados[nome] for nome in ("nao_publicado", "removida", "tipos", "fim_do_item")}
    conf["versao"] = re.compile(rf"{SECAO}\[(?P<versao>{SEMVER})\] - (?P<data>{DATA})"
                                rf"(?: \[{re.escape(conf['removida'])}\])?", re.ASCII)
    conf["links"] = {nome: modelo_de_link(dados, nome) for nome in CAMPOS_DOS_LINKS} if "links" in dados else None
    return conf


def le_changelog(arquivo, indice):
    """O texto do changelog: o do arquivo ou, com indice, o que o indice do git tem dele, o que
    vai no proximo commit, com as quebras de linha lidas como na leitura de um arquivo de texto.
    Erro (ErroDeDados) que diz o arquivo quando o texto nao se le."""
    if not indice:
        return le_texto(arquivo)
    caminho = Path(arquivo)
    try:
        lido = subprocess.run(["git", "-C", str(caminho.parent), "show", f":./{caminho.name}"], capture_output=True)
    except OSError as e:
        raise ErroDeDados(f"{arquivo}: o git não roda ({e})") from None
    if lido.returncode != 0:
        motivo = lido.stderr.decode(CODIFICACAO, "replace").strip()
        raise ErroDeDados(f"{arquivo}: o índice do git não o dá ({motivo})")
    try:
        return io.TextIOWrapper(io.BytesIO(lido.stdout), encoding=CODIFICACAO).read()
    except UnicodeDecodeError as e:
        raise ErroDeDados(f"{arquivo}: o do índice do git não se lê como texto em UTF-8 ({e})") from None


def precedencia(achada):
    """A chave que poe as versoes na ordem da precedencia do Versionamento Semantico 2.0.0
    (item 11 da especificacao): os tres numeros, pelo valor; com eles iguais, a versao com
    pre-lancamento antes da normal; entre dois pre-lancamentos, cada identificador, da
    esquerda para a direita, o so de algarismos pelo valor e antes do que tem letra ou hifen,
    este pela ordem do ASCII; com o comeco igual, o de mais identificadores depois. Os
    metadados de construcao nao contam."""
    numeros = tuple(int(achada.group(nome)) for nome in NUMEROS)
    pre = achada.group("prerelease")
    if pre is None:
        return numeros, (SEM_PRE,)
    return numeros, (COM_PRE, tuple((0, int(i), "") if i.isdigit() else (1, 0, i) for i in pre.split(".")))


def classe(linha):
    """A classe de uma linha do corpo: "secao", "tipo", "item", "continuacao", "branco" ou "outra"."""
    if linha.startswith(SECAO):
        return "secao"
    if linha.startswith(TIPO):
        return "tipo"
    if linha.startswith(ITEM) and linha[len(ITEM):len(ITEM) + 1].strip():
        return "item"
    if linha.startswith(CONTINUACAO) and linha[len(CONTINUACAO):len(CONTINUACAO) + 1].strip():
        return "continuacao"
    return "branco" if not linha else "outra"


def links_esperados(conf, versoes):
    """As linhas dos links, na ordem das secoes; nenhuma sem os modelos ou sem versao."""
    if conf["links"] is None or not versoes:
        return []
    modelos = conf["links"]
    saida = [f"[{conf['nao_publicado']}]: {preenche(modelos['nao_publicado'], anterior=versoes[0])}"]
    for i, versao in enumerate(versoes):
        if i + 1 < len(versoes):
            saida.append(f"[{versao}]: {preenche(modelos['versao'], versao=versao, anterior=versoes[i + 1])}")
        else:
            saida.append(f"[{versao}]: {preenche(modelos['primeira'], versao=versao)}")
    return saida


class Conferencia:
    """A conferencia de um changelog, linha por linha; os erros ficam em erros, (linha, motivo)."""

    def __init__(self, texto, conf):
        self.conf, self.erros = conf, []
        self.linhas = texto.split(QUEBRA)
        if self.linhas[-1]:
            self.erro(len(self.linhas) - 1, "o arquivo não termina com uma quebra de linha")
        else:
            self.linhas.pop()
        self.corpo = next((k for k, l in enumerate(self.linhas) if l.startswith(SECAO)), len(self.linhas))
        self.links = len(self.linhas)
        while self.links > self.corpo and LINK.fullmatch(self.linhas[self.links - 1]):
            self.links -= 1
        self.classes = {k: classe(self.linhas[k]) for k in range(self.corpo, self.links)}
        # as versoes que se leem, na ordem, e a data e a precedencia de cada uma
        self.versoes, self.datas, self.chaves = [], [], []
        self.secoes = 0  # quantas secoes ja vieram
        self.tipos_vistos = []  # os indices dos tipos da secao atual, na ordem
        self.em_tipo = False  # se a linha esta dentro de um tipo de mudanca

    def erro(self, k, motivo):
        self.erros.append((k + 1, motivo))

    def confere(self):
        linhas = self.linhas
        if not linhas or not TITULO.fullmatch(linhas[0]):
            self.erro(0, "a primeira linha não é o título, '# ' e um texto")
        for k in range(1, self.corpo):
            if linhas[k].startswith(CABECA):
                self.erro(k, "título antes da primeira seção")
        if self.corpo == len(linhas):
            self.erro(max(len(linhas) - 1, 0), "falta a seção do que não foi publicado")
        if linhas and not linhas[-1]:
            self.erro(len(linhas) - 1, "linha em branco no fim do arquivo")
        for k in range(self.corpo, self.links):
            getattr(self, f"linha_{self.classes[k]}")(k)
        self.confere_links()
        return sorted(self.erros)

    # ---- as classes de linha ----

    def titulo(self, k):
        """As linhas em branco em volta de um titulo."""
        if k == 0 or self.linhas[k - 1]:
            self.erro(k, "falta a linha em branco antes do título")
        if k + 1 < len(self.linhas) and self.linhas[k + 1]:
            self.erro(k, "falta a linha em branco depois do título")

    def linha_secao(self, k):
        self.titulo(k)
        self.em_tipo, self.tipos_vistos = False, []
        linha, primeira = self.linhas[k], self.secoes == 0
        self.secoes += 1
        if linha == f"{SECAO}[{self.conf['nao_publicado']}]":
            if not primeira:
                self.erro(k, "a seção do que não foi publicado vem só no topo, uma vez")
            return
        achada = self.conf["versao"].fullmatch(linha)
        if not achada:
            self.erro(k, "título de seção fora da forma '## [versão] - AAAA-MM-DD', com a versão do "
                         "Versionamento Semântico")
            return
        if primeira:
            self.erro(k, "falta, no topo, a seção do que não foi publicado")
        if not any(self.classes[j] == "tipo" for j in range(k + 1, self.fim_da_secao(k))):
            self.erro(k, "versão sem nenhum tipo de mudança")
        self.confere_versao(k, achada)

    def confere_versao(self, k, achada):
        """A data, e a versao e a data contra as da versao anterior no arquivo."""
        versao, data, chave = achada.group("versao"), achada.group("data"), precedencia(achada)
        try:
            dia = datetime.date.fromisoformat(data)
        except ValueError:
            self.erro(k, f"data que não existe: {data}")
            dia = None
        if self.versoes:
            if chave == self.chaves[-1]:
                self.erro(k, f"versão repetida: {versao}, com a precedência de {self.versoes[-1]}")
            elif chave > self.chaves[-1]:
                self.erro(k, f"versão fora da ordem: {versao} vem antes de {self.versoes[-1]}")
            ultima = self.datas[-1]
            if dia and ultima and dia > ultima:
                self.erro(k, f"data fora da ordem: {data} vem depois da de {self.versoes[-1]}")
        self.versoes.append(versao)
        self.datas.append(dia)
        self.chaves.append(chave)

    def linha_tipo(self, k):
        self.titulo(k)
        self.em_tipo = True
        nome = self.linhas[k][len(TIPO):]
        if nome not in self.conf["tipos"]:
            self.erro(k, f"tipo de mudança desconhecido: {nome}")
        else:
            indice = self.conf["tipos"].index(nome)
            if indice in self.tipos_vistos:
                self.erro(k, f"tipo de mudança repetido: {nome}")
            elif self.tipos_vistos and indice < max(self.tipos_vistos):
                self.erro(k, f"tipo de mudança fora da ordem: {nome}")
            self.tipos_vistos.append(indice)
        seguinte = k + 1
        while seguinte < self.links and self.classes[seguinte] == "branco":
            seguinte += 1
        if seguinte >= self.links or self.classes[seguinte] != "item":
            self.erro(k, f"tipo de mudança sem item: {nome}")

    def linha_item(self, k):
        if not self.em_tipo:
            self.erro(k, "item fora de um tipo de mudança")
        fim = k
        while fim + 1 < self.links and self.classes[fim + 1] == "continuacao":
            fim += 1
        if not self.linhas[fim].endswith(self.conf["fim_do_item"]):
            self.erro(fim, f"item que não termina com {self.conf['fim_do_item']!r}")

    def linha_continuacao(self, k):
        if self.classes.get(k - 1) not in ("item", "continuacao"):
            self.erro(k, "continuação fora de um item")

    def linha_branco(self, k):
        """A linha em branco: so uma, depois de um titulo ou antes de um titulo ou dos links."""
        if k == len(self.linhas) - 1:
            return  # a linha em branco no fim ja e erro
        if not self.linhas[k - 1]:
            self.erro(k, "linha em branco a mais")
            return
        seguinte = k + 1
        while seguinte < self.links and self.classes[seguinte] == "branco":
            seguinte += 1  # as linhas em branco a mais dao erro cada uma; o lugar e o da primeira
        if not (self.classes.get(k - 1) in TITULOS or self.classes.get(seguinte) in TITULOS or seguinte == self.links):
            self.erro(k, "linha em branco fora do lugar: só antes e depois de um título, e antes dos links")

    def linha_outra(self, k):
        self.erro(k, "linha fora da forma do changelog")

    def fim_da_secao(self, k):
        """O indice do titulo da secao seguinte a de k, ou o comeco dos links."""
        return next((j for j in range(k + 1, self.links) if self.classes[j] == "secao"), self.links)

    # ---- os links ----

    def confere_links(self):
        achados = list(range(self.links, len(self.linhas)))
        if self.conf["links"] is None:
            for k in achados:
                self.erro(k, "link no fim, sem os modelos dos links na configuração")
            return
        esperados = links_esperados(self.conf, self.versoes)
        if achados and self.links > 0 and self.linhas[self.links - 1]:
            self.erro(self.links, "falta a linha em branco antes dos links")
        for i, esperado in enumerate(esperados):
            if i >= len(achados):
                self.erro(len(self.linhas) - 1, f"falta o link: {esperado}")
            elif self.linhas[achados[i]] != esperado:
                self.erro(achados[i], f"link fora do modelo; no lugar dele vem: {esperado}")
        for k in achados[len(esperados):]:
            self.erro(k, "link a mais")


def main(argv=None):
    p = argparse.ArgumentParser(description="Confere a forma de um changelog do Keep a Changelog.")
    p.add_argument("configuracao", type=Path)
    p.add_argument("changelog", type=Path)
    p.add_argument("--indice", action="store_true",
                   help="confere o changelog como o índice do git o tem, o que vai no próximo commit")
    a = p.parse_args(argv)
    try:
        conf = le_configuracao(a.configuracao)
        texto = le_changelog(a.changelog, a.indice)
    except ErroDeDados as e:
        print(f"ERRO: {e}")
        return 2
    erros = Conferencia(texto, conf).confere()
    for linha, motivo in erros:
        print(f"ERRO {a.changelog}:{linha}: {motivo}")
    print(f"{len(erros)} erro(s)")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
