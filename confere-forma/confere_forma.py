"""
Confere a forma de documentos Markdown contra uma descricao dela: o esqueleto dos documentos,
um Markdown so com o texto que todos tem igual, a configuracao, so com a forma, e os arquivos
de padroes proibidos:

- abertura: as linhas com texto antes do primeiro divisor ou da primeira secao sao, na ordem,
  as da abertura do esqueleto, uma para cada uma;
- secoes: as linhas que casam com a expressao "secao" dao, no grupo "titulo", os titulos,
  que tem de ser os das secoes do esqueleto, na mesma ordem;
- o esqueleto: a abertura dele sao as linhas com texto antes do primeiro divisor ou da
  primeira secao, e os titulos, o grupo "titulo" de cada linha de secao; fora delas, so
  divisores. Cada linha do esqueleto vale letra por letra, menos as lacunas: a marca de uma
  lacuna da configuracao vale pelo trecho que casa com a expressao dela;
- divisores: logo antes de cada secao (sem contar linhas em branco) vem um divisor, e um
  divisor so vem logo antes de uma secao;
- comeco das secoes: com "comeco_das_secoes", a primeira linha com texto depois do titulo
  de cada secao casa com essa expressao;
- fecho: cada secao tem um bloco de fecho, uma linha que casa com "abre" seguida das que
  casam com "continua", e ele e a ultima coisa da secao; linha que casa com "continua"
  fora de um bloco de fecho e erro;
- siglas: com "siglas", cada sigla (o trecho que casa com a expressao "padrao", buscado na
  linha sem os trechos que casam com "trechos_fora"), na primeira vez em que aparece nas
  linhas que nao casam com "fora_de", vem na forma da primeira vez: o texto da linha logo
  antes dela termina pelo que casa com "antes", e o logo depois comeca pelo que casa com
  "depois", cada um quando ha;
- proibidos: cada linha que casa com o "padrao" de uma regra, e nao com o "exceto" dela;
  as regras vem de arquivos de dados proprios, cada um dado com --proibidos e conferido
  contra o molde dele pelo proibidos_comum.py desta pasta, como o marcas-de-ia.json; as de
  todos se somam, e duas com o mesmo nome sao erro;
- italico: cada nome da lista so aparece dentro de italico, nas linhas que nao casam com
  "fora_de"; italico e o trecho entre duas marcas iguais da lista, coladas ao texto, e a
  marca dobrada (negrito) nao conta;
- palavras: as do corpo das secoes, sem os blocos de fecho e as linhas que casam com
  "fora_de"; fora do minimo e do maximo, sai um AVISO, que nao muda o codigo de saida.

Com --rodape, o rodape do modelo dado que o texto tem no fim, lido pelo rodape_comum.py, da
peca rodape, fica fora da conferencia: o texto se confere sem ele, cada linha no numero dela.

Mostra uma linha "ERRO arquivo:linha: motivo" por problema, uma "AVISO arquivo: motivo"
para o tamanho e um resumo; sai com 0 sem erro, 1 com erro e 2 quando a configuracao, o
esqueleto, o modelo do rodape ou um argumento nao serve. Usa so a biblioteca padrao, o
proibidos_comum.py, desta pasta, o extrator_comum.py, da peca extrator, e o rodape_comum.py,
da peca rodape, nas pastas irmas ou na mesma pasta.

Uso:
    python3 -I confere_forma.py <configuracao.json> <esqueleto.md> <texto.md>... [--proibidos <arquivo.json>]...
        [--rodape <modelo.md>]
"""

import argparse
import re
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "extrator", PASTA.parent / "rodape", PASTA):  # na prateleira, as pastas irmas
    sys.path.insert(0, str(pasta))
from extrator_comum import ErroDeDados, compila, expressao, le_conferido, le_texto, repetidos  # noqa: E402
from proibidos_comum import achados, regras_proibidas  # noqa: E402
from rodape_comum import le_modelo, opcao_rodape, separa  # noqa: E402

MOLDE = PASTA / "esquemas" / "confere-forma.schema.json"
PALAVRA = re.compile(r"\w+")  # o que se conta como palavra
OPCIONAIS_DAS_SIGLAS = ("antes", "depois", "trechos_fora")  # as expressoes das siglas que a configuracao pode nao ter


def le_configuracao(caminho):
    """A configuracao, conferida contra o molde, com as expressoes compiladas; o que o molde nao ve se confere aqui: o
    grupo do titulo, o minimo que passa do maximo, a marca de lacuna repetida, a expressao das siglas que casa com o
    texto vazio e as siglas sem o antes nem o depois."""
    dados = le_conferido(caminho, MOLDE)
    conf = {}
    for nome, caminho_ in (("secao", "secao"), ("divisor", "divisor"), ("fecho_abre", "fecho/abre"),
                           ("fecho_continua", "fecho/continua"), ("italico_fora", "italico/fora_de"),
                           ("palavras_fora", "palavras/fora_de")):
        conf[nome] = expressao(dados, caminho_)
    if "titulo" not in conf["secao"].groupindex:
        raise ErroDeDados("a expressão secao não tem o grupo titulo")
    conf.update(nomes=dados["italico"]["nomes"], marcas=dados["italico"]["marcas"],
                minimo=dados["palavras"]["minimo"], maximo=dados["palavras"]["maximo"])
    if conf["minimo"] > conf["maximo"]:
        raise ErroDeDados("o mínimo de palavras é maior que o máximo")
    lacunas = dados.get("lacunas", [])
    repetidas = repetidos([lacuna["marca"] for lacuna in lacunas])
    if repetidas:
        raise ErroDeDados(f"lacuna com a mesma marca mais de uma vez: {repetidas}")
    conf["lacunas"] = {lacuna["marca"]: compila(lacuna["padrao"], f"o campo lacunas/{k}/padrao")
                       for k, lacuna in enumerate(lacunas)}
    conf["comeco"] = expressao(dados, "comeco_das_secoes") if "comeco_das_secoes" in dados else None
    conf["siglas"] = le_siglas(dados) if "siglas" in dados else None
    return conf


def le_siglas(dados):
    """As expressoes das siglas da configuracao, compiladas: o padrao, o fora_de e, quando ha, o antes, o depois e os
    trechos_fora (None quando falta). Erro (ErroDeDados): a expressao que casa com o texto vazio e as siglas sem o antes
    nem o depois."""
    siglas = {nome: expressao(dados, f"siglas/{nome}") for nome in ("padrao", "fora_de")}
    siglas.update({nome: expressao(dados, f"siglas/{nome}") if nome in dados["siglas"] else None
                   for nome in OPCIONAIS_DAS_SIGLAS})
    for nome in ("padrao", *OPCIONAIS_DAS_SIGLAS):
        if siglas[nome] is not None and siglas[nome].fullmatch(""):
            raise ErroDeDados(f"o campo siglas/{nome} casa com o texto vazio")
    if siglas["antes"] is None and siglas["depois"] is None:
        raise ErroDeDados("as siglas não têm o antes nem o depois")
    return siglas


def partes(linhas, conf):
    """(secoes, divisores, abertura) de um texto em linhas: os indices das linhas de secao, em ordem, os das de divisor
    e os das linhas com texto antes do primeiro divisor ou da primeira secao, em ordem."""
    secoes = [k for k, l in enumerate(linhas) if conf["secao"].search(l)]
    divisores = {k for k, l in enumerate(linhas) if conf["divisor"].search(l)}
    fim = min(secoes[:1] + sorted(divisores)[:1] + [len(linhas)])
    return secoes, divisores, [k for k in range(fim) if linhas[k].strip()]


def titulo_de(linha, conf):
    """O titulo de uma linha de secao: o grupo titulo da expressao secao."""
    return conf["secao"].search(linha).group("titulo")


def le_esqueleto(caminho, conf):
    """(abertura, titulos) do esqueleto dos documentos, cada um [(texto, expressao)]: a abertura, as linhas com texto
    antes do primeiro divisor ou da primeira secao, e os titulos, o de cada linha de secao. A expressao casa com o que
    o texto faz no documento: o texto, letra por letra, e cada marca de lacuna (a mais longa primeiro) pelo trecho que
    casa com a expressao dela. Erro (ErroDeDados), que diz o arquivo: a linha com texto que nao e da abertura, de secao
    nem de divisor, a lacuna que o esqueleto nao tem e a linha que, com as lacunas, nao compila."""
    linhas = le_texto(caminho).split("\n")
    secoes, divisores, abertura = partes(linhas, conf)
    soltas = [k for k, l in enumerate(linhas) if l.strip() and k not in abertura and k not in divisores
              and k not in secoes]
    if soltas:
        raise ErroDeDados(f"{caminho}:{soltas[0] + 1}: linha do esqueleto que não é da abertura, de seção nem divisor")
    lugares = [(k, linhas[k]) for k in abertura] + [(k, titulo_de(linhas[k], conf)) for k in secoes]
    marcas = sorted(conf["lacunas"], key=lambda m: (-len(m), m))
    busca = re.compile("|".join(map(re.escape, marcas))) if marcas else None

    def nas_lacunas(texto):
        return list(busca.finditer(texto)) if busca else []

    sem_lugar = sorted(set(marcas) - {m.group() for _, texto in lugares for m in nas_lacunas(texto)})
    if sem_lugar:
        raise ErroDeDados(f"{caminho}: lacuna que o esqueleto não tem: {sem_lugar}")

    def forma(k, texto):
        pedacos, fim = [], 0
        for m in nas_lacunas(texto):
            pedacos += [re.escape(texto[fim:m.start()]), f"(?:{conf['lacunas'][m.group()].pattern})"]
            fim = m.end()
        return compila("".join(pedacos) + re.escape(texto[fim:]), f"{caminho}:{k + 1}: a linha, com as lacunas,")

    formas = [(texto, forma(k, texto)) for k, texto in lugares]
    return formas[:len(abertura)], formas[len(abertura):]


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
    resto, fora = sem_italico(linha, conf["marcas"]), []
    for nome in sorted(conf["nomes"], key=lambda n: (-len(n), n)):
        rx = re.compile(f"(?<!\\w){re.escape(nome)}(?!\\w)")
        if rx.search(resto):
            fora.append(nome)
            resto = rx.sub(" ", resto)
    return fora


def termina_por(texto, forma):
    """Se o texto termina por um trecho que casa com a expressao da forma."""
    return any(forma.fullmatch(texto, k) for k in range(len(texto) + 1))


def sem_os_trechos(linha, trechos):
    """A linha com cada trecho que casa com a expressao trocado por espacos, no mesmo lugar; sem expressao, a linha."""
    return linha if trechos is None else trechos.sub(lambda t: " " * len(t.group()), linha)


def na_forma(linha, achado, siglas):
    """Se a sigla achada na linha vem na forma da primeira vez: o texto logo antes dela termina pelo que casa com o
    antes, e o logo depois comeca pelo que casa com o depois, cada um quando ha."""
    antes, depois = siglas["antes"], siglas["depois"]
    return ((antes is None or termina_por(linha[:achado.start()], antes))
            and (depois is None or depois.match(linha[achado.end():]) is not None))


def siglas_fora_da_forma(linhas, siglas):
    """[(indice da linha, sigla)] de cada sigla cuja primeira vez, nas linhas que nao casam com fora_de, nao vem na
    forma da primeira vez; a sigla se busca na linha sem os trechos_fora, que viram espacos no mesmo lugar, e a forma
    se confere na linha inteira."""
    vistas, fora = set(), []
    for k, linha in enumerate(linhas):
        if siglas["fora_de"].search(linha):
            continue
        for achado in siglas["padrao"].finditer(sem_os_trechos(linha, siglas["trechos_fora"])):
            if achado.group() in vistas:
                continue
            vistas.add(achado.group())
            if not na_forma(linha, achado, siglas):
                fora.append((k, achado.group()))
    return fora


def confere_texto(arquivo, conf):
    """([(linha, motivo)], [aviso], palavras) de um texto, sem o rodape do modelo que ele tem no fim."""
    linhas = separa(le_texto(arquivo), conf["rodape"])[0].split("\n")
    erros = []
    secoes, divisores, abertura = partes(linhas, conf)
    com_texto = [k for k, l in enumerate(linhas) if l.strip()]
    ultima = com_texto[-1] if com_texto else 0

    for i, (_, forma) in enumerate(conf["abertura"]):
        if i >= len(abertura):
            erros.append((1, f"falta a linha {i + 1} da abertura"))
        elif not forma.fullmatch(linhas[abertura[i]]):
            erros.append((abertura[i] + 1, f"a linha {i + 1} da abertura está fora do esqueleto"))
    for k in abertura[len(conf["abertura"]):]:
        erros.append((k + 1, "linha a mais na abertura"))

    for i, k in enumerate(secoes):
        titulo = titulo_de(linhas[k], conf)
        if i >= len(conf["titulos"]):
            erros.append((k + 1, f"seção a mais: {titulo}"))
        elif not conf["titulos"][i][1].fullmatch(titulo):
            erros.append((k + 1, f"seção fora do esqueleto: {titulo!r}; no lugar dela vem {conf['titulos'][i][0]!r}"))
    for texto, _ in conf["titulos"][len(secoes):]:
        erros.append((ultima + 1, f"falta a seção: {texto}"))
    for k in secoes:
        if vizinha(linhas, k, -1) not in divisores:
            erros.append((k + 1, "seção sem divisor logo antes"))
        if conf["comeco"] is not None:
            j = vizinha(linhas, k, 1)
            if j is None or not conf["comeco"].search(linhas[j]):
                erros.append(((k if j is None else j) + 1, "a seção não começa na forma de comeco_das_secoes"))
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
        for nome in achados(l, conf["proibidos"]):
            erros.append((k + 1, f"padrão proibido: {nome}"))
        if not conf["italico_fora"].search(l):
            for nome in nomes_fora_do_italico(l, conf):
                erros.append((k + 1, f"nome fora do itálico: {nome}"))
    if conf["siglas"] is not None:
        erros += [(k + 1, f"sigla fora da forma da primeira vez: {sigla}")
                  for k, sigla in siglas_fora_da_forma(linhas, conf["siglas"])]

    avisos = []
    if not conf["minimo"] <= palavras <= conf["maximo"]:
        avisos.append(f"{palavras} palavras, fora de {conf['minimo']} a {conf['maximo']}")
    return sorted(erros), avisos, palavras


def main(argv=None):
    p = argparse.ArgumentParser(description="Confere a forma de documentos Markdown contra uma descrição dela.")
    p.add_argument("configuracao", type=Path)
    p.add_argument("esqueleto", type=Path, help="o esqueleto dos documentos: a abertura e os títulos das seções")
    p.add_argument("textos", type=Path, nargs="+")
    p.add_argument("--proibidos", type=Path, action="append", default=[], metavar="ARQUIVO",
                   help="um arquivo de dados com padrões proibidos; pode se repetir")
    opcao_rodape(p, "o modelo do rodapé que os textos têm no fim, que fica fora da conferência")
    a = p.parse_args(argv)
    faltam = [str(t) for t in a.textos if not t.is_file()]
    if faltam:
        print(f"ERRO: não existe(m): {faltam}")
        return 2
    try:
        conf = le_configuracao(a.configuracao)
        abertura, titulos = le_esqueleto(a.esqueleto, conf)
        conf.update(abertura=abertura, titulos=titulos, proibidos=regras_proibidas(a.proibidos),
                    rodape=le_modelo(a.rodape))
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
