"""
Confere a forma de documentos Markdown contra uma descricao dela, dada na configuracao e nos
arquivos de padroes proibidos:

- abertura: as linhas com texto antes do primeiro divisor ou da primeira secao, uma para
  cada item, na ordem; cada item e um texto "igual" ou uma expressao "padrao";
- secoes: as linhas que casam com a expressao "secao" dao, no grupo "titulo", os titulos,
  que tem de ser os da lista "titulos", na mesma ordem;
- divisores: logo antes de cada secao (sem contar linhas em branco) vem um divisor, e um
  divisor so vem logo antes de uma secao;
- fecho: cada secao tem um bloco de fecho, uma linha que casa com "abre" seguida das que
  casam com "continua", e ele e a ultima coisa da secao; linha que casa com "continua"
  fora de um bloco de fecho e erro;
- proibidos: cada linha que casa com o "padrao" de uma regra, e nao com o "exceto" dela;
  as regras vem de arquivos de dados proprios, cada um dado com --proibidos e conferido
  contra o molde dele, como o marcas-de-ia.json desta pasta; as de todos se somam, e duas
  com o mesmo nome sao erro;
- italico: cada nome da lista so aparece dentro de italico, nas linhas que nao casam com
  "fora_de"; italico e o trecho entre duas marcas iguais da lista, coladas ao texto, e a
  marca dobrada (negrito) nao conta;
- palavras: as do corpo das secoes, sem os blocos de fecho e as linhas que casam com
  "fora_de"; fora do minimo e do maximo, sai um AVISO, que nao muda o codigo de saida.

Mostra uma linha "ERRO arquivo:linha: motivo" por problema, uma "AVISO arquivo: motivo"
para o tamanho e um resumo; sai com 0 sem erro, 1 com erro e 2 quando a configuracao ou um
argumento nao serve. Usa so a biblioteca padrao e o extrator_comum.py, da peca extrator, na
pasta irma "extrator" ou na mesma pasta.

Uso:
    python3 -I confere_forma.py <configuracao.json> <texto.md>... [--proibidos <arquivo.json>]...
"""

import argparse
import re
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "extrator", PASTA):  # na prateleira, a peca extrator fica na pasta irma
    sys.path.insert(0, str(pasta))
from extrator_comum import ErroDeDados, compila, expressao, le_conferido, le_texto, repetidos  # noqa: E402

MOLDE = PASTA / "esquemas" / "confere-forma.schema.json"
MOLDE_DOS_PROIBIDOS = PASTA / "esquemas" / "proibidos.schema.json"  # o de cada arquivo do --proibidos
PALAVRA = re.compile(r"\w+")  # o que se conta como palavra


def item_da_abertura(item):
    """("igual", texto) ou ("padrao", expressao compilada) de um item da abertura, que o molde
    ja conferiu ter um so dos dois."""
    if "igual" in item:
        return "igual", item["igual"]
    return "padrao", expressao(item, "padrao")


def le_configuracao(caminho):
    """A configuracao, conferida contra o molde, com as expressoes compiladas; o grupo do titulo
    e o minimo que passa do maximo, que o molde nao ve, conferidos aqui."""
    dados = le_conferido(caminho, MOLDE)
    conf = {"abertura": [item_da_abertura(item) for item in dados["abertura"]]}
    for nome, caminho_ in (("secao", "secao"), ("divisor", "divisor"), ("fecho_abre", "fecho/abre"),
                           ("fecho_continua", "fecho/continua"), ("italico_fora", "italico/fora_de"),
                           ("palavras_fora", "palavras/fora_de")):
        conf[nome] = expressao(dados, caminho_)
    if "titulo" not in conf["secao"].groupindex:
        raise ErroDeDados("a expressão secao não tem o grupo titulo")
    conf.update(titulos=dados["titulos"], nomes=dados["italico"]["nomes"], marcas=dados["italico"]["marcas"],
                minimo=dados["palavras"]["minimo"], maximo=dados["palavras"]["maximo"])
    if conf["minimo"] > conf["maximo"]:
        raise ErroDeDados("o mínimo de palavras é maior que o máximo")
    return conf


def regras_proibidas(caminhos):
    """[(nome, padrao, exceto)] das regras dos arquivos de padroes proibidos, na ordem dos
    arquivos e, em cada um, na da lista, com as expressoes compiladas (exceto e None na regra
    sem ele); cada arquivo e conferido contra o molde dele, e o erro diz o arquivo e a regra.
    Duas regras com o mesmo nome, no mesmo arquivo ou em dois, sao erro."""
    regras, lugares = [], []
    for caminho in caminhos:
        for k, regra in enumerate(le_conferido(caminho, MOLDE_DOS_PROIBIDOS)["proibidos"]):
            onde = f"{caminho}: /proibidos/{k}"
            exceto = compila(regra["exceto"], f"{onde}/exceto") if "exceto" in regra else None
            regras.append((regra["nome"], compila(regra["padrao"], f"{onde}/padrao"), exceto))
            lugares.append(onde)
    nomes = [nome for nome, _, _ in regras]
    mesmos = [f"{nome!r} em {', '.join(lugar for n, lugar in zip(nomes, lugares) if n == nome)}"
              for nome in repetidos(nomes)]
    if mesmos:
        raise ErroDeDados(f"padrão proibido com o mesmo nome em mais de uma regra: {'; '.join(mesmos)}")
    return regras


def casa(item, linha):
    tipo, valor = item
    return linha == valor if tipo == "igual" else bool(valor.search(linha))


def vizinha(linhas, k, passo):
    """O indice da linha com texto mais perto de k, para tras (passo -1) ou para frente (1); None quando nao ha."""
    j = k + passo
    while 0 <= j < len(linhas):
        if linhas[j].strip():
            return j
        j += passo
    return None


def sem_italico(linha, marcas):
    """A linha sem as marcas de negrito (a marca dobrada) e sem os trechos em italico."""
    for m in marcas:
        linha = linha.replace(m * 2, "")
    for m in marcas:
        e = re.escape(m)
        linha = re.sub(f"{e}(?=\\S)(.+?)(?<=\\S){e}", " ", linha)
    return linha


def nomes_fora_do_italico(linha, conf):
    """Os nomes da lista que aparecem fora de italico na linha; o mais longo primeiro, e o
    lugar dele nao conta para um mais curto que esteja dentro dele."""
    resto, achados = sem_italico(linha, conf["marcas"]), []
    for nome in sorted(conf["nomes"], key=lambda n: (-len(n), n)):
        rx = re.compile(f"(?<!\\w){re.escape(nome)}(?!\\w)")
        if rx.search(resto):
            achados.append(nome)
            resto = rx.sub(" ", resto)
    return achados


def confere_texto(arquivo, conf):
    """([(linha, motivo)], [aviso], palavras) de um texto."""
    linhas = le_texto(arquivo).split("\n")
    erros = []
    secoes = [k for k, l in enumerate(linhas) if conf["secao"].search(l)]
    divisores = {k for k, l in enumerate(linhas) if conf["divisor"].search(l)}
    com_texto = [k for k, l in enumerate(linhas) if l.strip()]
    ultima = com_texto[-1] if com_texto else 0

    fim = min(secoes[:1] + sorted(divisores)[:1] + [len(linhas)])
    abertura = [k for k in range(fim) if linhas[k].strip()]
    for i, item in enumerate(conf["abertura"]):
        if i >= len(abertura):
            erros.append((1, f"falta a linha {i + 1} da abertura"))
        elif not casa(item, linhas[abertura[i]]):
            erros.append((abertura[i] + 1, f"a linha {i + 1} da abertura está fora do modelo"))
    for k in abertura[len(conf["abertura"]):]:
        erros.append((k + 1, "linha a mais na abertura"))

    for i, k in enumerate(secoes):
        titulo = conf["secao"].search(linhas[k]).group("titulo")
        if i >= len(conf["titulos"]):
            erros.append((k + 1, f"seção a mais: {titulo}"))
        elif titulo != conf["titulos"][i]:
            erros.append((k + 1, f"seção fora do modelo: {titulo!r}; no lugar dela vem {conf['titulos'][i]!r}"))
    for titulo in conf["titulos"][len(secoes):]:
        erros.append((ultima + 1, f"falta a seção: {titulo}"))
    for k in secoes:
        if vizinha(linhas, k, -1) not in divisores:
            erros.append((k + 1, "seção sem divisor logo antes"))
    for k in sorted(divisores):
        if vizinha(linhas, k, 1) not in secoes:
            erros.append((k + 1, "divisor que não vem logo antes de uma seção"))

    blocos = {}  # linha que abre um bloco de fecho -> as linhas do bloco
    for k, l in enumerate(linhas):
        if conf["fecho_abre"].search(l):
            bloco = [k]
            while (bloco[-1] + 1 < len(linhas) and conf["fecho_continua"].search(linhas[bloco[-1] + 1])
                   and not conf["fecho_abre"].search(linhas[bloco[-1] + 1])):
                bloco.append(bloco[-1] + 1)
            blocos[k] = bloco
    nos_blocos = {j for b in blocos.values() for j in b}
    palavras = 0
    for i, k in enumerate(secoes):
        fim = secoes[i + 1] if i + 1 < len(secoes) else len(linhas)
        aberturas = [j for j in range(k + 1, fim) if j in blocos]
        if not aberturas:
            erros.append((k + 1, "seção sem bloco de fecho"))
        for j in aberturas[1:]:
            erros.append((j + 1, "seção com mais de um bloco de fecho"))
        if aberturas:
            depois = [j for j in range(blocos[aberturas[-1]][-1] + 1, fim) if linhas[j].strip() and j not in divisores]
            if depois:
                erros.append((depois[0] + 1, "texto depois do bloco de fecho"))
        palavras += sum(len(PALAVRA.findall(linhas[j])) for j in range(k + 1, fim)
                        if j not in nos_blocos and j not in divisores and not conf["palavras_fora"].search(linhas[j]))
    for k, l in enumerate(linhas):
        if k not in nos_blocos and conf["fecho_continua"].search(l):
            erros.append((k + 1, "linha de bloco fora do bloco de fecho"))
        for nome, padrao, exceto in conf["proibidos"]:
            if padrao.search(l) and not (exceto and exceto.search(l)):
                erros.append((k + 1, f"padrão proibido: {nome}"))
        if not conf["italico_fora"].search(l):
            for nome in nomes_fora_do_italico(l, conf):
                erros.append((k + 1, f"nome fora do itálico: {nome}"))

    avisos = []
    if not conf["minimo"] <= palavras <= conf["maximo"]:
        avisos.append(f"{palavras} palavras, fora de {conf['minimo']} a {conf['maximo']}")
    return sorted(erros), avisos, palavras


def main(argv=None):
    p = argparse.ArgumentParser(description="Confere a forma de documentos Markdown contra uma descrição dela.")
    p.add_argument("configuracao", type=Path)
    p.add_argument("textos", type=Path, nargs="+")
    p.add_argument("--proibidos", type=Path, action="append", default=[], metavar="ARQUIVO",
                   help="um arquivo de dados com padrões proibidos; pode se repetir")
    a = p.parse_args(argv)
    faltam = [str(t) for t in a.textos if not t.is_file()]
    if faltam:
        print(f"ERRO: não existe(m): {faltam}")
        return 2
    try:
        conf = dict(le_configuracao(a.configuracao), proibidos=regras_proibidas(a.proibidos))
        resultados = [(t, confere_texto(t, conf)) for t in a.textos]
    except ErroDeDados as e:
        print(f"ERRO: {e}")
        return 2
    erros = avisos = 0
    for texto, (lista, avisos_do_texto, palavras) in resultados:
        for linha, motivo in lista:
            print(f"ERRO {texto}:{linha}: {motivo}")
        for aviso in avisos_do_texto:
            print(f"AVISO {texto}: {aviso}")
        print(f"{texto}: {palavras} palavra(s)")
        erros, avisos = erros + len(lista), avisos + len(avisos_do_texto)
    print(f"{len(a.textos)} texto(s), {erros} erro(s), {avisos} aviso(s)")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
