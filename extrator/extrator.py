"""
Tira o texto de documentos -- PDF, HTML, XML, JSON ou outro tipo que tenha leitor -- e
grava a transcricao de cada um, pagina por pagina, na forma que a configuracao manda.

Duas entradas em JSON, com os moldes em esquemas/ (campo que o molde nao conhece e erro):
  - a configuracao: o padrao da transcricao (o titulo de cada pagina, os rotulos, a marca
    de pagina sem texto, os escapes, as marcas de destaque e a forma das tabelas), as
    "trocas" que valem em todo documento (opcional) e os leitores (as extensoes que cada um
    le e as opcoes padrao dele);
  - os documentos: para cada um, o arquivo, a transcricao a gravar, as opcoes dele, que
    valem por cima das do leitor, num documento com paginas a "numeracao" (as faixas de
    paginas com o numero impresso de cada uma), as "trocas" so dele e as "correcoes": cada
    uma troca, no texto de uma pagina ja escrito, o que a leitura deu pelo que o documento
    diz, conferido na imagem da pagina. A correcao diz quantas vezes o texto lido aparece
    na pagina ("vezes", padrao 1); se aparecer outro numero de vezes -- a leitura mudou --,
    e erro.

Uma troca e um texto que o leitor da e o que vai no lugar dele, em todo o texto lido,
antes de escrever: a ligadura tipografica pelas letras dela, o simbolo que uma fonte do
documento guarda com o codigo errado pelo simbolo que a pagina mostra. As trocas se fazem
numa passada so (o que uma troca escreve nao e trocado de novo). A mesma troca na
configuracao e no documento e erro, e a troca do documento que nao acha nada tambem.

Cada leitor e um modulo leitor_<nome>.py nesta pasta, com ler(arquivo, opcoes, contexto),
que devolve {"paginado": bool, "paginas": [{"arquivo", "ocr", "blocos"}]}. O contexto da o
leitor de outro nome ("leitor", para o leitor que passa um texto a outro) e se as paginas
de OCR se pulam ("pular_ocr"): a pagina pulada vem com "blocos" None. Um bloco e
("texto", conteudo) ou ("tabela", [[conteudo, ...], ...]), em que o conteudo e uma linha
escrita ou uma lista de pedacos (texto, destaques). Um tipo de arquivo novo e um leitor
novo e as extensoes dele na configuracao; os outros leitores nao mudam. Na configuracao,
um leitor pode usar o modulo de outro ("modulo"), com outras opcoes: dois perfis do mesmo
leitor, como um para HTML e outro para XML.

Uma linha do texto que se le como titulo de pagina e uma pagina cujo texto e a marca de
pagina sem texto sao erro: a transcricao ficaria ambigua.

A conferencia de uma transcricao ja feita pede o texto das paginas ao extrator, sem refazer
o OCR: le_documento(..., pular_ocr=True) e paginas_escritas, que da a pagina pulada sem texto.

Os caminhos dos documentos sao a partir de --raiz (padrao: a pasta atual). A transcricao
que ja existe nao e gravada por cima, a nao ser com --substituir; nesse caso, o que vem
antes do primeiro titulo de pagina (o registro de onde ela veio, por exemplo) fica como
esta. Com qualquer erro, em qualquer documento, nada e gravado.

Uso:
    python3 -I extrator.py <configuracao.json> <documentos.json>
    python3 -I extrator.py <configuracao.json> <documentos.json> --so <arquivo ou transcricao> --substituir
"""

import argparse
import importlib
import re
import subprocess
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA))
from extrator_comum import (MOLDES, ErroDeDados, como_padrao, confere_padrao, le_configuracao,  # noqa: E402
                            le_conferido, paginas_das_faixas, preenche, repetidos)

NOME_DE_LEITOR = re.compile(r"^[a-z0-9_]+$")


# ---------- rotulos das paginas ----------

def romano(n):
    out = ""
    for valor, letras in ((1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"), (90, "xc"),
                          (50, "l"), (40, "xl"), (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")):
        while n >= valor:
            out, n = out + letras, n - valor
    return out


ESTILOS = {"arabico": str, "romano_minusculo": romano, "romano_maiusculo": lambda n: romano(n).upper()}


def rotulos(numeracao, total, padrao):
    """{pagina do arquivo: rotulo} das faixas da numeracao; cada faixa e {"de", "ate",
    "estilo", "primeiro"}: o numero impresso da pagina "de" e "primeiro"."""
    paginas_das_faixas(numeracao, total)
    out = {}
    for faixa in numeracao:
        if faixa["estilo"] not in ESTILOS:
            raise ErroDeDados(f"estilo de numeração desconhecido: {faixa['estilo']!r}; os que existem: "
                                 f"{sorted(ESTILOS)}")
        for n in paginas_das_faixas([faixa], total):
            numero = ESTILOS[faixa["estilo"]](faixa["primeiro"] + n - faixa["de"])
            out[n] = preenche(padrao["rotulo_numerada"], numero=numero)
    return out


# ---------- o texto de cada pagina ----------

def escapa_dentro(texto, padrao):
    return "".join(padrao["escape"] + c if c in padrao["escapar"] else c for c in texto)


def escapa_comeco(linha, padrao):
    return padrao["escape"] + linha if linha.startswith(tuple(padrao["escapar_no_comeco"])) else linha


def _vizinhos(letras):
    """Para cada caractere, os destaques do caractere que nao e espaco mais perto antes
    dele (nenhum, no comeco da linha)."""
    out, ultimo = [], frozenset()
    for c, d in letras:
        out.append(ultimo)
        if not c.isspace():
            ultimo = d
    return out


def com_destaques(pedacos, padrao):
    """A linha feita de pedacos (texto, destaques): cada caractere escapado e, onde os
    destaques mudam, so as marcas do que muda -- as que fecham, na ordem contraria a do
    padrao, e depois as que abrem, na ordem do padrao. O espaco leva so o destaque que os
    caracteres dos dois lados dele tem: assim a marca fica colada ao texto destacado."""
    marcas = padrao["destaques"]
    letras = [(c, frozenset(d)) for texto, d in pedacos for c in texto]
    desconhecidos = sorted({n for _, d in letras for n in d} - set(marcas))
    if desconhecidos:
        raise ErroDeDados(f"destaque sem marca no padrão: {desconhecidos}")
    antes, depois = _vizinhos(letras), _vizinhos(letras[::-1])[::-1]
    out, ativos = [], frozenset()
    for (c, d), a, p in zip(letras + [("", frozenset())], antes + [ativos], depois + [ativos]):
        d = a & p if c.isspace() else d
        if d != ativos:
            out += [marcas[n]["fecha"] for n in reversed(list(marcas)) if n in ativos - d]
            out += [marcas[n]["abre"] for n in marcas if n in d - ativos]
            ativos = d
        out.append(escapa_dentro(c, padrao))
    return "".join(out)


def linhas_de_texto(conteudo, padrao):
    """As linhas de um bloco de texto: uma linha escrita, com quebras, ou uma lista de
    pedacos com destaques."""
    if isinstance(conteudo, str):
        return [escapa_comeco(escapa_dentro(l, padrao), padrao) if l.strip() else "" for l in conteudo.split("\n")]
    linha = com_destaques(conteudo, padrao)
    return [escapa_comeco(linha, padrao) if linha.strip() else ""]


def tabela(linhas, padrao):
    t, largura = padrao["tabela"], max(len(l) for l in linhas)
    forma = lambda celulas: t["inicio"] + t["meio"].join(celulas) + t["fim"]  # noqa: E731
    celula = lambda c: escapa_dentro(c, padrao) if isinstance(c, str) else com_destaques(c, padrao)  # noqa: E731
    cheias = [[celula(c) for c in l] + [""] * (largura - len(l)) for l in linhas]
    return [forma(cheias[0]), forma([t["separador"]] * largura)] + [forma(l) for l in cheias[1:]]


def texto_da_pagina(blocos, padrao):
    """As linhas da pagina: sem linha em branco repetida, no comeco ou no fim; pagina sem
    texto fica sem linha nenhuma."""
    linhas = []
    for tipo, conteudo in blocos:
        if tipo == "texto":
            linhas += linhas_de_texto(conteudo, padrao)
        elif tipo == "tabela":
            linhas += [""] + tabela(conteudo, padrao) + [""]
        else:
            raise ErroDeDados(f"bloco de tipo desconhecido: {tipo!r}")
    limpas = []
    for linha in linhas:
        if linha or (limpas and limpas[-1]):
            limpas.append(linha)
    while limpas and not limpas[-1]:
        limpas.pop()
    return limpas


# ---------- um documento ----------

def le_entradas(configuracao, documentos):
    """(configuracao, [documentos]) das duas entradas, cada uma conferida contra o molde dela."""
    return (le_configuracao(configuracao),
            le_conferido(documentos, MOLDES / "extracao.schema.json")["documentos"])


def confere_opcoes(nome, opcoes, conhecidas, todas):
    """Erro quando as opcoes de um leitor tem uma que ele nao conhece ou, com todas, quando
    falta uma."""
    sobram = sorted(set(opcoes) - set(conhecidas))
    faltam = sorted(set(conhecidas) - set(opcoes)) if todas else []
    if sobram or faltam:
        raise ErroDeDados(f"leitor {nome!r}: opção(ões) que ele não conhece: {sobram}; que faltam: {faltam}; "
                          f"as dele: {sorted(conhecidas)}")


def leitor(nome, leitores):
    """(modulo, opcoes padrao) do leitor: o modulo leitor_<modulo>.py, em que <modulo> e o
    "modulo" do leitor na configuracao ou, sem ele, o proprio nome do leitor. As opcoes
    padrao sao todas as do leitor (OPCOES, no modulo dele), nem mais nem menos."""
    if nome not in leitores:
        raise ErroDeDados(f"leitor desconhecido: {nome!r}; os da configuração: {sorted(leitores)}")
    modulo = leitores[nome].get("modulo", nome)
    if not NOME_DE_LEITOR.match(modulo):
        raise ErroDeDados(f"nome de módulo de leitor fora da forma: {modulo!r}")
    carregado = importlib.import_module(f"leitor_{modulo}")
    confere_opcoes(nome, leitores[nome]["opcoes"], carregado.OPCOES, todas=True)
    return carregado, leitores[nome]["opcoes"]


def leitor_do_documento(doc, leitores):
    nome = doc.get("leitor")
    if nome is None:
        extensao = Path(doc["arquivo"]).suffix.lower()
        nomes = [n for n in sorted(leitores) if extensao in [e.lower() for e in leitores[n]["extensoes"]]]
        if len(nomes) != 1:
            raise ErroDeDados(f"{len(nomes)} leitor(es) para a extensão {extensao!r}: {nomes}; precisa ser um")
        nome = nomes[0]
    modulo, opcoes = leitor(nome, leitores)
    confere_opcoes(nome, doc.get("opcoes", {}), modulo.OPCOES, todas=False)
    return modulo, {**opcoes, **doc.get("opcoes", {})}


def trocas_do_documento(doc, config):
    """As trocas que valem no documento: as da configuracao e as dele."""
    gerais, proprias = config.get("trocas", {}), doc.get("trocas", {})
    repetidas = sorted(set(gerais) & set(proprias))
    if repetidas:
        raise ErroDeDados(f"troca que está na configuração e no documento: {repetidas}")
    if "" in gerais or "" in proprias:
        raise ErroDeDados("troca de um texto vazio")
    return {**gerais, **proprias}


def com_trocas(blocos, trocas, contagem):
    """Os blocos com as trocas feitas no texto deles -- linhas, pedacos e celulas --, numa
    passada so; conta, em contagem, quantas vezes cada troca achou o que trocar."""
    if not trocas:
        return blocos
    rx = re.compile("|".join(re.escape(d) for d in sorted(trocas, key=lambda d: (-len(d), d))))

    def troca(m):
        contagem[m.group(0)] = contagem.get(m.group(0), 0) + 1
        return trocas[m.group(0)]

    def no_conteudo(conteudo):
        if isinstance(conteudo, str):
            return rx.sub(troca, conteudo)
        return [(rx.sub(troca, texto), destaques) for texto, destaques in conteudo]

    out = []
    for tipo, conteudo in blocos:
        if tipo == "texto":
            out.append((tipo, no_conteudo(conteudo)))
        elif tipo == "tabela":
            out.append((tipo, [[no_conteudo(c) for c in linha] for linha in conteudo]))
        else:
            out.append((tipo, conteudo))
    return out


def corrige(corpo, pagina, correcoes):
    """As linhas da pagina com as correcoes dela, na ordem da lista."""
    texto = "\n".join(corpo)
    for c in correcoes:
        if c["pagina"] != pagina:
            continue
        vezes, esperado = texto.count(c["de"]), c.get("vezes", 1)
        if vezes != esperado:
            raise ErroDeDados(f"página {pagina} do arquivo: a correção de {c['de']!r} acha o texto {vezes} vez(es), "
                              f"e não {esperado}")
        texto = texto.replace(c["de"], c["para"])
    return texto.split("\n")


def le_documento(doc, config, raiz, pular_ocr=False):
    """O que o leitor le do documento; com pular_ocr, as paginas de OCR vem sem ler."""
    arquivo = raiz / doc["arquivo"]
    if not arquivo.is_file():
        raise ErroDeDados("o arquivo não existe")
    modulo, opcoes = leitor_do_documento(doc, config["leitores"])
    return modulo.ler(arquivo, opcoes, {"leitor": lambda nome: leitor(nome, config["leitores"]),
                                        "pular_ocr": pular_ocr})


def paginas_escritas(lido, doc, config):
    """([(posicao no arquivo, titulo, corpo)], resumo) do que o leitor leu: o corpo e as
    linhas da pagina, com as trocas e as correcoes; a pagina que o leitor pulou vem com o
    corpo None, sem as correcoes dela, e a troca do documento sem uso so e erro quando
    nenhuma pagina foi pulada."""
    padrao, paginas = config["padrao"], lido["paginas"]
    numeracao = doc.get("numeracao", [])
    if lido["paginado"]:
        nomes = rotulos(numeracao, len(paginas), padrao)
        rotulo = lambda n: nomes.get(n, padrao["rotulo_sem_numero"])  # noqa: E731
    elif numeracao:
        raise ErroDeDados("o documento não tem páginas, então não leva numeração")
    else:
        rotulo = lambda n: padrao["rotulo_sem_paginas"]  # noqa: E731
    correcoes = doc.get("correcoes", [])
    sem_pagina = sorted({c["pagina"] for c in correcoes} - {p["arquivo"] for p in paginas})
    if sem_pagina:
        raise ErroDeDados(f"correção para página que o documento não tem: {sem_pagina}")
    trocas, contagem = trocas_do_documento(doc, config), {}
    titulo, out, vazias = como_padrao(padrao["titulo_pagina"]), [], 0
    for p in paginas:
        cabeca = preenche(padrao["titulo_pagina"], rotulo=rotulo(p["arquivo"]), arquivo=p["arquivo"])
        if p["blocos"] is None:
            out.append((p["arquivo"], cabeca, None))
            continue
        escrito = texto_da_pagina(com_trocas(p["blocos"], trocas, contagem), padrao)
        if escrito == [padrao["sem_texto"]]:
            raise ErroDeDados(f"página {p['arquivo']} do arquivo: o texto dela é a marca de página sem texto")
        corpo = corrige(escrito or [padrao["sem_texto"]], p["arquivo"], correcoes)
        parecidas = [l for l in corpo if titulo.match(l)]
        if parecidas:
            raise ErroDeDados(f"página {p['arquivo']} do arquivo: linha que se lê como título de página: "
                              f"{parecidas[0]!r}")
        vazias += not escrito
        out.append((p["arquivo"], cabeca, corpo))
    sem_uso = sorted(set(doc.get("trocas", {})) - set(contagem))
    if sem_uso and all(p["blocos"] is not None for p in paginas):
        raise ErroDeDados(f"troca do documento que não acha nada no texto lido: {sem_uso}")
    ocr = sum(1 for p in paginas if p["ocr"])
    return out, (f"{len(paginas)} página(s), {vazias} sem texto, {ocr} pelo OCR, {sum(contagem.values())} "
                 f"troca(s), {len(correcoes)} correção(ões)")


def extrai(doc, config, raiz):
    """(linhas da transcricao, resumo) de um documento."""
    paginas, resumo = paginas_escritas(le_documento(doc, config, raiz), doc, config)
    return [linha for _, cabeca, corpo in paginas for linha in [cabeca, ""] + corpo + [""]], resumo


def cabecalho(texto, padrao):
    """As linhas antes do primeiro titulo de pagina de uma transcricao que ja existe."""
    titulo, linhas = como_padrao(padrao["titulo_pagina"]), texto.split("\n")
    for i, linha in enumerate(linhas):
        if titulo.match(linha):
            return linhas[:i]
    raise ErroDeDados("a transcrição que existe não tem nenhum título de página: não há como saber o que "
                         "guardar dela")


def prepara(config, documentos, raiz, so, substituir):
    """[(transcricao, texto, resumo)] de todos os documentos, ou ErroDeDados."""
    confere_padrao(config["padrao"])
    escolhidos = [d for d in documentos if not so or d["arquivo"] in so or d["saida"] in so]
    faltam = sorted(set(so) - {d["arquivo"] for d in documentos} - {d["saida"] for d in documentos})
    if faltam:
        raise ErroDeDados(f"--so com documento que não está na lista: {faltam}")
    mesmas = repetidos([d["saida"] for d in escolhidos])
    if mesmas:
        raise ErroDeDados(f"duas transcrições no mesmo arquivo: {mesmas}")
    prontos = []
    for doc in escolhidos:
        try:
            linhas, resumo = extrai(doc, config, raiz)
            saida = raiz / doc["saida"]
            if saida.exists():
                if not substituir:
                    raise ErroDeDados(f"{doc['saida']} já existe; só se grava por cima com --substituir")
                linhas = cabecalho(saida.read_text(encoding="utf-8"), config["padrao"]) + linhas
            prontos.append((saida, "\n".join(linhas), resumo))
        except (ErroDeDados, KeyError, ValueError, TypeError, OSError, UnicodeDecodeError, LookupError,
                subprocess.CalledProcessError) as e:
            detalhe = f"falta a informação {e}" if isinstance(e, KeyError) else str(e)
            raise ErroDeDados(f"{doc.get('arquivo', doc)}: {detalhe}")
    return prontos


def main(argv=None):
    p = argparse.ArgumentParser(description="Tira o texto de documentos e grava a transcrição de cada um.")
    p.add_argument("configuracao", type=Path)
    p.add_argument("documentos", type=Path)
    p.add_argument("--raiz", type=Path, default=Path("."), help="de onde partem os caminhos dos documentos")
    p.add_argument("--so", action="append", default=[], help="só este documento (o arquivo ou a transcrição)")
    p.add_argument("--substituir", action="store_true", help="grava por cima da transcrição que já existe")
    a = p.parse_args(argv)
    try:
        config, documentos = le_entradas(a.configuracao, a.documentos)
        prontos = prepara(config, documentos, a.raiz, a.so, a.substituir)
    except ErroDeDados as e:
        print(f"ERRO: {e}")
        print("Nada foi gravado.")
        return 1
    for saida, texto, resumo in prontos:
        saida.parent.mkdir(parents=True, exist_ok=True)
        saida.write_text(texto, encoding="utf-8")
        print(f"{saida}: {resumo}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
