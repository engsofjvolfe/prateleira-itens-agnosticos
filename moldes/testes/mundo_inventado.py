"""
O mundo inventado dos testes da peca dos moldes, num lugar so: o sorteio e o que se espera
de cada caso. Nao se roda: os testes desta pasta o importam, dao a semente ao SORTEIO
(SORTEIO.seed) e a pasta onde cada mundo e gravado.

Tudo e sorteado: uma forma de analise com nomes, separadores, marcas e papeis que nao sao
os de nenhuma analise real, e um campo com a fonte que ele cita; regras com tipos de fora,
marcas, grupos e documentos, e com coisas a mais que as regras nao usam; e aulas com
slides, trechos, notas, titulos e texto solto. Cada trecho e de um caso: de estudo pelo
grupo, pelo caminho ou com marca e grupo; a espera do assunto; marcado, com uma ou duas
marcas; com a marca so onde ela nao se procura; de fora; com tipo de fora junto de outro;
sem documento; com grupo desconhecido. Todos os casos aparecem em toda semente, e tambem os
detalhes: parenteses, valor vazio, item repetido numa lista, dois caminhos, texto repetido
no slide, texto em NFD, trecho que comeca como nota, marca onde nao se procura; no destino,
em pedacos: dois pedacos ou mais, um em NFD, separador dentro dos parenteses, parentese
dentro de outro, valor vazio e pedaco repetido. Sorteadas tambem: a forma, as regras e as
analises erradas, cada uma com o que o erro dela tem de dizer.
"""
import collections
import copy
import hashlib
import json
import random
import string
import unicodedata

SORTEIO = random.Random()  # a semente vem do teste que o importa: SORTEIO.seed(n)

LETRAS = string.ascii_lowercase + "áâãçéêíóôõú"
ACENTOS = "áâãçéêíóôõú"
TITULOS = ["=", "%", "~", "@", "^"]
ITENS = ["* ", "+ ", "• ", "> ", "o- "]
SEPARADORES_TEXTO = [" :: ", " => ", " ~> ", " -- "]
SEPARADORES_CAMPOS = [" | ", " ¦ ", " // "]
SEPARADORES_LISTA = [",", ";", "&", " y ", " und "]
PARES = [("-", "->"), ("+", "+>"), (".", ".>")]  # um separador e outro que comeca por ele
SEPARADORES_PEDACOS = [" + ", "; ", " & ", " ¬ "]
PARES_PEDACOS = [(" ^", " ^^ "), (" %", " %% "), (" =", " == ")]  # um separador de pedacos e outro que comeca por ele
VAZIOS = ["∅", "n/a", "~0~", "·"]
EXTENSOES = [".txt", ".md", ".an"]
RESERVADAS = {"und"}  # as palavras dos separadores, que uma palavra sorteada nao pode ser
CASOS = ["grupo", "caminho", "assunto", "marca", "duas_marcas", "marca_errada", "fora", "misto", "orfao",
         "desconhecido", "marca_com_grupo"]
COM_PROBLEMA = {"marca_errada", "misto", "orfao", "desconhecido"}
DETALHES = ["nfd", "parenteses_no_texto", "como_nota", "nota_na_lista", "repetido_na_lista", "repete",
            "dois_pedacos", "parenteses_nos_pedacos", "vazio_nos_pedacos", "pedaco_repetido", "so_vazio"]


# ---------- o sorteio ----------

def palavra(alfabeto=LETRAS):
    while True:
        p = "".join(SORTEIO.choice(alfabeto) for _ in range(SORTEIO.randint(2, 7)))
        if p not in RESERVADAS:
            return p


def palavras(minimo=1, maximo=4):
    return " ".join(palavra() for _ in range(SORTEIO.randint(minimo, maximo)))


def distintos(sorteia, n):
    """n valores distintos, nenhum dentro de outro."""
    saida = []
    while len(saida) < n:
        v = sorteia()
        if not any(v in s or s in v for s in saida):
            saida.append(v)
    return saida


def ascii_():
    return palavra(string.ascii_lowercase)


def unicos(itens):
    return list(dict.fromkeys(itens))


def campo_do(forma, papel):
    return next(c for c in forma["campos"] if c.get("papel") == papel)


def papeis_da(forma):
    return [c["papel"] for c in forma["campos"] if "papel" in c]


def separadores_de_pedacos(separador_campos):
    """Os separadores de um campo em pedacos: um par em que um comeca pelo outro, um a mais e,
    as vezes, o proprio separador dos campos, em ordem sorteada."""
    curto, longo = SORTEIO.choice(PARES_PEDACOS)
    escolhidos = [curto, longo, SORTEIO.choice(SEPARADORES_PEDACOS)]
    if SORTEIO.random() < 0.5:
        escolhidos.append(separador_campos)
    return SORTEIO.sample(escolhidos, len(escolhidos))


def sorteia_forma():
    titulo = SORTEIO.choice(TITULOS)
    outro = SORTEIO.choice([t for t in TITULOS if t != titulo])
    curto, longo = SORTEIO.choice(PARES)
    separador_campos = SORTEIO.choice(SEPARADORES_CAMPOS)
    nomes = distintos(ascii_, SORTEIO.randint(4, 6))
    campos = [
        {"nome": nomes[0], "forma": "lista", "papel": "tipo",
         "separadores": SORTEIO.sample([curto, longo, SORTEIO.choice(SEPARADORES_LISTA)], 3)},
        {"nome": nomes[1], "forma": "lista", "papel": "grupo", "separadores": SORTEIO.sample(SEPARADORES_LISTA, 2)},
        {"nome": nomes[2], "forma": "presenca", "papel": "caminho",
         "valores": distintos(lambda: f"{palavra()}»{palavra()}", 3)},
        {"nome": nomes[3], "forma": "pedacos", "papel": "destino",
         "separadores": separadores_de_pedacos(separador_campos)},
    ]
    campos += [SORTEIO.choice([{"nome": n, "forma": "texto"},
                               {"nome": n, "forma": "lista", "separadores": SORTEIO.sample(SEPARADORES_LISTA, 2)},
                               {"nome": n, "forma": "pedacos",
                                "separadores": separadores_de_pedacos(separador_campos)}])
               for n in nomes[4:]]
    SORTEIO.shuffle(campos)
    SORTEIO.choice(campos)["fonte"] = f"{ascii_()}{SORTEIO.choice(['-', '_', ':'])}{SORTEIO.randint(1, 999)}"
    prefixo = ascii_() + SORTEIO.choice(["-", "_", "."])
    extensao = SORTEIO.choice(EXTENSOES)
    return {"versao_schema": 1, "arquivos": f"{prefixo}*{extensao}", "prefixo_arquivo": prefixo,
            "prefixo_titulo": titulo, "prefixo_slide": f"{SORTEIO.choice([titulo * 3, outro])} {ascii_()} ",
            "marca_item": SORTEIO.choice(ITENS), "separador_texto": SORTEIO.choice(SEPARADORES_TEXTO),
            "separador_campos": separador_campos, "vazio": SORTEIO.choice(VAZIOS),
            "nota_sem_campos": palavras(1, 2), "campos": campos}


def sorteia_regras(forma, mundo):
    """As regras e, no mundo, o papel de cada grupo e de cada caminho nos casos."""
    caminhos = campo_do(forma, "caminho")["valores"]
    papeis = papeis_da(forma)
    tipos = distintos(lambda: f"{palavra().capitalize()} {palavra()}", 8)
    mundo["conteudo"], mundo["de_fora"] = tipos[:5], tipos[5:]
    nomes = distintos(lambda: palavras(1, 3), 11)
    ids = distintos(ascii_, 10)
    fora = [{"id": ids[0], "nome": nomes[0], "tipos": tipos[5:]}]
    if SORTEIO.random() < 0.5:
        fora = [{"id": ids[0], "nome": nomes[0], "tipos": tipos[5:6]},
                {"id": ids[1], "nome": nomes[1], "tipos": tipos[6:]}]
    textos = distintos(lambda: f"⟨{palavra()}⟩", 3)
    marcas = [{"id": ids[2 + k], "nome": nomes[2 + k], "texto": textos[k],
               "papeis": SORTEIO.sample(papeis, SORTEIO.randint(1, len(papeis) - 1) if k == 0 else
                                        SORTEIO.randint(1, len(papeis)))} for k in range(SORTEIO.randint(2, 3))]
    SORTEIO.shuffle(marcas)
    codigos = distintos(lambda: f"{SORTEIO.choice(string.ascii_uppercase)}{SORTEIO.randint(0, 99)}", 6)
    n_assunto = SORTEIO.randint(1, 2)
    mundo["assunto"], mundo["orfao"] = codigos[:n_assunto], codigos[n_assunto]
    mundo["de_documento"], mundo["desconhecido"] = codigos[n_assunto + 1:5], codigos[5]
    grupos = [{"id": g, "nome": palavras(1, 3), **({"pelo_assunto": True} if g in mundo["assunto"] else {})}
              for g in codigos[:5]]
    SORTEIO.shuffle(grupos)
    mundo["caminho_de_documento"], mundo["caminho_livre"] = caminhos[0], caminhos[2]
    documentos = [
        {"id": ids[5], "nome": nomes[5], "grupos": list(mundo["de_documento"]), "caminhos": []},
        {"id": ids[6], "nome": nomes[6], "grupos": [], "caminhos": [caminhos[0]]},
        {"id": ids[7], "nome": nomes[7], "grupos": SORTEIO.sample(mundo["de_documento"], SORTEIO.randint(0, 1)),
         "caminhos": SORTEIO.sample(caminhos[:2], SORTEIO.randint(0, 2))},
    ]
    for d in documentos:
        for chave in ("grupos", "caminhos"):
            if not d[chave] and SORTEIO.random() < 0.5:
                del d[chave]
    documentos += [{"id": ids[8 + k], "nome": nomes[8 + k], "todos": True} for k in range(SORTEIO.randint(1, 2))]
    SORTEIO.choice(documentos)[ascii_()] = {ascii_(): [palavras()]}  # o que o documento traz e as regras nao usam
    SORTEIO.shuffle(documentos)
    regras = {"fora": fora, "marcas": marcas, "grupos": grupos, "documentos": documentos}
    regras["a_mais_" + ascii_()] = [palavras()]  # o que o arquivo traz e as regras nao usam
    return regras


def nao_procurados(marca, forma):
    """Os lugares do trecho onde a marca nao se procura."""
    extras = [("campo", c["nome"]) for c in forma["campos"] if "papel" not in c]
    return [("texto",)] + extras + [("papel", p) for p in papeis_da(forma) if p not in marca["papeis"]]


def sorteia_caso(tipo, mundo, detalhes=()):
    """Um caso: os itens de cada papel, as marcas postas e onde, e o que se espera dele."""
    regras = mundo["regras"]
    caso = {"tipo": tipo, "tipos": SORTEIO.sample(mundo["conteudo"], SORTEIO.randint(1, 2)), "grupos": [],
            "caminhos": [], "postas": [], "regra_de_fora": None, "detalhes": set(detalhes)}
    livre = SORTEIO.sample([mundo["caminho_livre"]], SORTEIO.randint(0, 1))
    if tipo == "grupo":
        caso["grupos"] = SORTEIO.sample(mundo["de_documento"], 1) + SORTEIO.sample(
            [mundo["orfao"]] + mundo["assunto"], SORTEIO.randint(0, 1))
        caso["caminhos"] = SORTEIO.sample(campo_do(mundo["forma"], "caminho")["valores"], SORTEIO.randint(0, 2))
    elif tipo == "caminho":
        caso["grupos"] = [mundo["orfao"]]
        caso["caminhos"] = [mundo["caminho_de_documento"]] + livre
    elif tipo == "assunto":
        caso["grupos"] = SORTEIO.sample(mundo["assunto"], 1) + SORTEIO.sample([mundo["orfao"]], SORTEIO.randint(0, 1))
        caso["caminhos"] = livre
    elif tipo in ("marca", "duas_marcas", "marca_errada", "orfao"):
        caso["grupos"] = [mundo["orfao"]] if tipo == "orfao" else []
        caso["caminhos"] = livre
    elif tipo == "fora":
        regra = SORTEIO.choice(regras["fora"])
        caso["regra_de_fora"] = regra["id"]
        caso["tipos"] = SORTEIO.sample(regra["tipos"], SORTEIO.randint(1, len(regra["tipos"])))
        caso["grupos"] = SORTEIO.sample(mundo["de_documento"], SORTEIO.randint(0, 1))
    elif tipo == "misto":
        caso["tipos"] = SORTEIO.sample([SORTEIO.choice(mundo["de_fora"]), SORTEIO.choice(mundo["conteudo"])], 2)
        caso["grupos"] = SORTEIO.sample(mundo["de_documento"], 1)
    elif tipo == "desconhecido":
        caso["grupos"] = SORTEIO.sample([SORTEIO.choice(mundo["de_documento"]), mundo["desconhecido"]], 2)
    elif tipo == "marca_com_grupo":
        caso["grupos"] = SORTEIO.sample(mundo["de_documento"], 1)
    achadas = {"marca": 1, "marca_com_grupo": 1, "duas_marcas": 2, "orfao": 0, "marca_errada": 0}
    for marca in SORTEIO.sample(regras["marcas"], achadas.get(tipo, SORTEIO.randint(0, 1))):
        caso["postas"].append((marca["id"], ("papel", SORTEIO.choice(marca["papeis"]))))
    if tipo == "marca_errada":
        marca = next(m for m in regras["marcas"] if len(m["papeis"]) < len(papeis_da(mundo["forma"])))
        caso["postas"].append((marca["id"], SORTEIO.choice([o for o in nao_procurados(marca, mundo["forma"])
                                                            if o[0] == "papel"])))
    if SORTEIO.random() < 0.5:
        marca = SORTEIO.choice(regras["marcas"])
        caso["postas"].append((marca["id"], SORTEIO.choice(nao_procurados(marca, mundo["forma"]))))
    if tipo == "caminho" and "dois_caminhos" in caso["detalhes"]:
        caso["caminhos"] = [mundo["caminho_de_documento"], mundo["caminho_livre"]]
    return caso


def junta(pedacos, separadores):
    """Os pedacos entre separadores sorteados; o separador sem espaco nas pontas ganha, as
    vezes, um espaco de cada lado."""
    texto = pedacos[0]
    for pedaco in pedacos[1:]:
        sep = SORTEIO.choice(separadores)
        texto += (sep if sep != sep.strip() else SORTEIO.choice(["", " "]) + sep + SORTEIO.choice(["", " "])) + pedaco
    return texto


def bruto_em_lista(itens, separadores, vazio, entre_parenteses):
    """O texto de um campo em lista: os itens entre separadores sorteados, ou o vazio, com
    os textos entre parenteses depois de itens sorteados."""
    pedacos = list(itens) or [vazio]
    for extra in entre_parenteses:
        k = SORTEIO.randrange(len(pedacos))
        pedacos[k] += f" ({extra})"
    return junta(pedacos, separadores)


def bruto_em_pedacos(separadores, vazio, marcas, detalhes):
    """(texto, valor) de um campo em pedacos. Cada pedaco tem palavras e, as vezes, um texto
    entre parenteses com um separador dentro (as vezes com um parentese dentro de outro);
    cada marca entra como palavra de um pedaco sorteado. Pelos detalhes: dois pedacos ou
    mais, o primeiro com acento e escrito em NFD; o valor vazio como pedaco; um pedaco
    repetido; so o valor vazio. O valor e o dos pedacos escritos, sem o vazio e sem
    repetir."""
    pedacos = [] if "so_vazio" in detalhes else [
        palavras(1, 3) for _ in range(SORTEIO.randint(2 if "dois_pedacos" in detalhes else 1, 3))]
    if "dois_pedacos" in detalhes and pedacos:
        pedacos[0] = unicodedata.normalize("NFD", f"{pedacos[0]} {palavra()}{SORTEIO.choice(ACENTOS)}{palavra()}")
    if pedacos and ("parenteses_nos_pedacos" in detalhes or SORTEIO.random() < 0.3):
        dentro = f"{palavras(1, 2)}{SORTEIO.choice(separadores)}{palavras(1, 2)}"
        if SORTEIO.random() < 0.5:
            dentro = f"{palavra()} ({dentro}) {palavra()}"
        pedacos[SORTEIO.randrange(len(pedacos))] += f" ({dentro})"
    for marca in marcas:
        if pedacos:
            pedacos[SORTEIO.randrange(len(pedacos))] += f" {marca}"
        else:
            pedacos.append(marca)
    escritos = list(pedacos)
    if "pedaco_repetido" in detalhes and pedacos:
        escritos.insert(SORTEIO.randint(1, len(escritos)), SORTEIO.choice(pedacos))
    if "vazio_nos_pedacos" in detalhes or not escritos:
        escritos.insert(SORTEIO.randint(0, len(escritos)), vazio)
    return junta(escritos, separadores), unicos(p for p in escritos if p != vazio)


def compoe_linha(forma, texto, brutos):
    """A linha de um trecho, do texto dele e do texto de cada campo."""
    campos = [f"{c['nome']}: {brutos[c['nome']]}" for c in forma["campos"]]
    return forma["marca_item"] + texto + forma["separador_texto"] + forma["separador_campos"].join(campos)


def escreve_caso(caso, mundo):
    """Compoe a linha do trecho e guarda no caso o texto, o texto e o valor de cada campo."""
    forma, d = mundo["forma"], caso["detalhes"]
    textos_das_marcas = {m["id"]: m["texto"] for m in mundo["regras"]["marcas"]}
    postas = collections.defaultdict(list)
    for marca, onde in caso["postas"]:
        postas[onde].append(textos_das_marcas[marca])
    texto = palavras(2, 5)
    if "parenteses_no_texto" in d:
        texto += f" ({palavras(1, 2)})"
    if "como_nota" in d:
        texto = f"{forma['nota_sem_campos']} {texto}"
    if "nfd" in d:
        texto = unicodedata.normalize("NFD", f"{texto} {palavra()}{SORTEIO.choice(ACENTOS)}{palavra()}")
    texto = " ".join([texto] + postas[("texto",)])
    brutos, valores = {}, {}
    for c in forma["campos"]:
        nome, papel = c["nome"], c.get("papel")
        aqui = postas[("papel", papel) if papel else ("campo", nome)]
        if papel in ("tipo", "grupo"):
            itens = list(caso["tipos"] if papel == "tipo" else caso["grupos"])
            notas = []
            if papel == "tipo" and "repetido_na_lista" in d:
                itens.insert(SORTEIO.randrange(len(itens) + 1), SORTEIO.choice(itens))
            if papel == "tipo" and "nota_na_lista" in d:
                notas.append(palavras(1, 2))
            brutos[nome] = bruto_em_lista(itens, c["separadores"], forma["vazio"], notas + aqui)
            valores[nome] = unicos(itens)
        elif papel == "caminho":
            escolhidos = SORTEIO.sample(caso["caminhos"], len(caso["caminhos"]))
            juntos = f" {SORTEIO.choice(['e', '+', 'ou'])} ".join(escolhidos) or forma["vazio"]
            brutos[nome] = " ".join([juntos] + aqui)
            valores[nome] = [v for v in c["valores"] if v in escolhidos]
        elif c["forma"] == "pedacos":
            brutos[nome], valores[nome] = bruto_em_pedacos(c["separadores"], forma["vazio"], aqui, d)
        elif c["forma"] == "lista":
            itens = [palavra() for _ in range(SORTEIO.randint(1, 2))]
            brutos[nome] = bruto_em_lista(itens, c["separadores"], forma["vazio"], aqui)
            valores[nome] = unicos(itens)
        else:
            pedacos = palavras(1, 4).split()
            for marca in aqui:
                pedacos.insert(SORTEIO.randrange(len(pedacos) + 1), marca)
            brutos[nome] = valores[nome] = " ".join(pedacos)
    caso.update(texto=texto, brutos=brutos, valores=valores, linha=compoe_linha(forma, texto, brutos))
    return caso


def sorteia_chaves(n):
    """Chaves de aula cuja ordem natural e a ordem do numero: uma abaixo de 10, uma acima."""
    numeros = {SORTEIO.randint(1, 9), SORTEIO.randint(10, 40)}
    while len(numeros) < n:
        numeros.add(SORTEIO.randint(1, 40))
    return [f"{k}-{k + 1}" if SORTEIO.random() < 0.3 else str(k) for k in sorted(numeros)]


def linha_de_titulo(forma):
    return [f"{forma['prefixo_titulo']} {palavras()}", palavras()]


def sorteia_aulas(casos, mundo):
    """As aulas: a chave, as linhas do arquivo, os trechos (caso, slide, posicao) e as notas.
    A primeira tem sempre uma nota, uma linha em branco e um titulo seguido de texto solto e
    de uma linha com cara de trecho, que nao se le."""
    forma = mundo["forma"]
    unidades = [[c, c] if "repete" in c["detalhes"] else [c] for c in casos]
    chaves = sorteia_chaves(SORTEIO.randint(3, 4))
    cortes = sorted(SORTEIO.sample(range(1, len(unidades)), len(chaves) - 1))
    fatias = [unidades[a:b] for a, b in zip([0] + cortes, cortes + [len(unidades)])]
    aulas = []
    for k, (chave, fatia) in enumerate(zip(chaves, fatias)):
        linhas, trechos, notas = [], [], 0
        if SORTEIO.random() < 0.5:
            linhas += linha_de_titulo(forma)
        slide, i = SORTEIO.randint(1, 5), 0
        while i < len(fatia):
            linhas.append(f"{forma['prefixo_slide']}{slide}")
            posicao, n = 0, SORTEIO.randint(1, 3)
            primeiro = k == 0 and i == 0
            for unidade in fatia[i:i + n]:
                if primeiro or SORTEIO.random() < 0.3:
                    linhas.append(f"{forma['marca_item']}{forma['nota_sem_campos']} {palavras()}")
                    notas += 1
                if primeiro or SORTEIO.random() < 0.2:
                    linhas.append("")
                primeiro = False
                for caso in unidade:
                    posicao += 1
                    linhas.append(caso["linha"])
                    trechos.append((caso, slide, posicao))
            if (k == 0 and i == 0) or SORTEIO.random() < 0.4:
                solto = escreve_caso(sorteia_caso("grupo", mundo), mundo)["linha"]
                linhas += linha_de_titulo(forma) + [solto]
            i += n
            slide += SORTEIO.randint(1, 3)
        aulas.append({"chave": chave, "linhas": linhas, "trechos": trechos, "notas": notas})
    return aulas


def grava_json(caminho, dados):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return caminho


def grava_aulas(pasta, mundo, ordem=1):
    """Grava os arquivos das aulas, na ordem dada (1 ou -1), mais uma pasta com nome de aula
    e um arquivo fora do padrao, que a leitura nao pode pegar."""
    forma, extensao = mundo["forma"], mundo["extensao"]
    pasta.mkdir(parents=True)
    for aula in mundo["aulas"][::ordem]:
        (pasta / f"{forma['prefixo_arquivo']}{aula['chave']}{extensao}").write_text(
            "\n".join(aula["linhas"]) + "\n", encoding="utf-8")
    (pasta / f"{forma['prefixo_arquivo']}0{extensao}").mkdir()
    (pasta / f"LEIA{extensao}").write_text(palavras() + "\n", encoding="utf-8")


def sorteia_mundo(pasta, com_problemas=True):
    """A forma, as regras, os casos (um de cada, com todos os detalhes, mais outros
    sorteados) e as aulas gravadas na pasta dada, com os arquivos de dados ao lado."""
    mundo = {"forma": sorteia_forma()}
    mundo["extensao"] = mundo["forma"]["arquivos"].rsplit("*", 1)[1]
    mundo["regras"] = sorteia_regras(mundo["forma"], mundo)
    tipos = [t for t in CASOS if com_problemas or t not in COM_PROBLEMA]
    forcados = {"grupo": ["nfd", "nota_na_lista", "repetido_na_lista", "dois_pedacos", "parenteses_nos_pedacos"],
                "caminho": ["dois_caminhos", "como_nota", "vazio_nos_pedacos"],
                "marca": ["repete", "parenteses_no_texto", "pedaco_repetido"]}
    casos = [sorteia_caso(t, mundo, forcados.get(t, ())) for t in tipos]
    casos += [sorteia_caso(SORTEIO.choice(tipos), mundo, [x for x in DETALHES if SORTEIO.random() < 0.15])
              for _ in range(SORTEIO.randint(10, 25))]
    SORTEIO.shuffle(casos)
    for caso in casos:
        escreve_caso(caso, mundo)
    mundo["aulas"] = sorteia_aulas(casos, mundo)
    mundo["pasta"] = pasta / "analises"
    grava_aulas(mundo["pasta"], mundo)
    mundo["arquivo_forma"] = grava_json(pasta / "forma.json", mundo["forma"])
    mundo["arquivo_regras"] = grava_json(pasta / "regras.json", mundo["regras"])
    mundo["esperados"] = [(caso, aula["chave"], slide, posicao)
                          for aula in mundo["aulas"] for caso, slide, posicao in aula["trechos"]]
    return mundo


# ---------- o que se espera de cada caso ----------

def id_esperado(caso, chave, slide, posicao):
    resumo = hashlib.sha1(unicodedata.normalize("NFC", caso["texto"]).encode("utf-8")).hexdigest()[:4]
    return f"{chave}/{slide}/{posicao}/{resumo}"


def marcas_esperadas(caso, mundo):
    procura = {m["id"]: m["papeis"] for m in mundo["regras"]["marcas"]}
    achadas = {m for m, onde in caso["postas"] if onde[0] == "papel" and onde[1] in procura[m]}
    return [m["id"] for m in mundo["regras"]["marcas"] if m["id"] in achadas]


def classe_esperada(caso, mundo):
    """A classe do caso; num caso com problema, ("problema", o tipo do caso)."""
    tipo = caso["tipo"]
    if tipo in ("grupo", "caminho", "desconhecido", "marca_com_grupo"):
        return ("estudo",)
    if tipo == "assunto":
        return ("assunto",)
    if tipo in ("marca", "duas_marcas"):
        return ("marca", marcas_esperadas(caso, mundo)[0])
    if tipo == "fora":
        return ("fora", caso["regra_de_fora"])
    return ("problema", tipo)


def documentos_esperados(caso, mundo):
    if caso["tipo"] in ("fora", "misto", "marca_errada"):
        return []
    grupos, caminhos = set(caso["grupos"]), set(caso["caminhos"])
    return [d["id"] for d in mundo["regras"]["documentos"]
            if d.get("todos") or grupos & set(d.get("grupos", [])) or caminhos & set(d.get("caminhos", []))]


def grupos_desconhecidos_esperados(caso, mundo):
    """Os grupos do caso que as regras nao tem: o desconhecido, so no caso dele."""
    return [mundo["desconhecido"]] if caso["tipo"] == "desconhecido" else []


def valor_esperado(caso, mundo, papel):
    return caso["valores"][campo_do(mundo["forma"], papel)["nome"]]


def frases_dos_problemas(mundo, trechos, lugar):
    """{caso com problema: as classes que lugar(trecho, regras) da aos trechos dele}; com o
    lugar certo, uma so para cada caso, a frase do problema dele."""
    frases = collections.defaultdict(set)
    for t, (caso, *_) in zip(trechos, mundo["esperados"]):
        esperada = classe_esperada(caso, mundo)
        if esperada[0] == "problema":
            frases[esperada[1]].add(lugar(t, mundo["regras"])[0])
    return dict(frases)


def classes_esperadas(mundo, frases):
    """O Counter das classes dos casos, cada caso com problema na frase do problema dele (a
    primeira, em ordem, quando o lugar da mais de uma)."""
    return collections.Counter(min(frases[c[1]]) if c[0] == "problema" else c
                               for c in (classe_esperada(caso, mundo) for caso, *_ in mundo["esperados"]))


# ---------- a forma, as regras e as analises erradas ----------

def variantes(mundo, pasta):
    """(nome, onde o erro e pego, forma, regras, pasta das analises, o que a mensagem tem de
    dizer: um texto, varios ou nada) de cada erro. Onde: "molde" (o molde do arquivo: o
    campo que ele nao conhece, o que falta, o valor de outro tipo ou fora da forma; a
    mensagem diz o caminho do valor), "forma" (a conferencia da forma, no que o molde nao
    ve), "regras" (a das regras contra a forma) ou "analises" (a leitura dos arquivos). As
    analises erradas sao gravadas na pasta dada, uma pasta para cada erro."""
    forma, regras = mundo["forma"], mundo["regras"]
    estranho = "x" + ascii_()
    nomes = {c.get("papel", "extra"): c["nome"] for c in forma["campos"]}
    # o caminho, dentro da forma, do campo de cada papel; o lugar do primeiro documento de conteudo nas regras
    no_campo = {c["papel"]: f"/campos/{k}" for k, c in enumerate(forma["campos"]) if "papel" in c}
    de_conteudo = next(k for k, d in enumerate(regras["documentos"]) if not d.get("todos"))
    saida = []

    def na_forma(nome, onde, muda, culpado):
        f = copy.deepcopy(forma)
        muda(f)
        saida.append((nome, onde, f, regras, mundo["pasta"], culpado))

    def nas_regras(nome, onde, muda, culpado):
        r = copy.deepcopy(regras)
        muda(r)
        saida.append((nome, onde, forma, r, mundo["pasta"], culpado))

    def campo(f, papel):
        return next(c for c in f["campos"] if c.get("papel") == papel)

    na_forma("campo-a-mais-na-forma", "molde", lambda f: f.update({estranho: 1}), estranho)
    na_forma("campo-a-mais-num-campo", "molde", lambda f: campo(f, "destino").update({estranho: 1}), estranho)
    na_forma("falta-uma-chave", "molde", lambda f: f.pop("vazio"), "/vazio")
    na_forma("sem-campos", "molde", lambda f: f.update(campos=[]), "/campos")
    na_forma("forma-de-campo-desconhecida", "molde", lambda f: campo(f, "destino").update(forma=estranho),
             (f"{no_campo['destino']}/forma", estranho))
    na_forma("lista-sem-separadores", "molde", lambda f: campo(f, "grupo").pop("separadores"),
             f"{no_campo['grupo']}/separadores")
    na_forma("pedacos-sem-separadores", "molde", lambda f: campo(f, "destino").pop("separadores"),
             f"{no_campo['destino']}/separadores")
    na_forma("presenca-com-valor-vazio", "molde", lambda f: campo(f, "caminho").update(valores=[""]),
             f"{no_campo['caminho']}/valores/0")
    na_forma("papel-desconhecido", "molde", lambda f: campo(f, "destino").update(papel=estranho),
             (f"{no_campo['destino']}/papel", estranho))
    na_forma("papel-repetido", "forma",
             lambda f: f["campos"].append({"nome": estranho, "forma": "texto", "papel": "destino"}), estranho)
    na_forma("papel-faltando", "forma", lambda f: campo(f, "caminho").pop("papel"), "caminho")
    na_forma("papel-sem-lista", "forma",
             lambda f: (campo(f, "tipo").pop("papel"), campo(f, "destino").pop("separadores"),
                        campo(f, "destino").update(papel="tipo", forma="texto")), nomes["destino"])
    na_forma("campo-repetido", "forma", lambda f: f["campos"].append({"nome": nomes["destino"], "forma": "texto"}),
             nomes["destino"])
    nas_regras("campo-a-mais-na-regra-de-fora", "molde", lambda r: r["fora"][0].update({estranho: 1}), estranho)
    nas_regras("campo-a-mais-numa-marca", "molde", lambda r: r["marcas"][0].update({estranho: 1}), estranho)
    nas_regras("campo-a-mais-num-grupo", "molde", lambda r: r["grupos"][0].update({estranho: 1}), estranho)
    nas_regras("faltam-as-marcas", "molde", lambda r: r.pop("marcas"), "/marcas")
    nas_regras("marca-num-papel-que-a-forma-nao-da", "regras", lambda r: r["marcas"][0].update(papeis=[estranho]),
               estranho)
    nas_regras("marca-sem-texto", "molde", lambda r: r["marcas"][0].update(texto=""), "/marcas/0/texto")
    nas_regras("marca-sem-papel", "molde", lambda r: r["marcas"][0].update(papeis=[]), "/marcas/0/papeis")
    nas_regras("caminho-que-o-campo-nao-tem", "regras",
               lambda r: r["documentos"][de_conteudo].update(caminhos=[estranho]), estranho)
    nas_regras("grupos-que-nao-sao-lista", "molde", lambda r: r["documentos"][de_conteudo].update(grupos=1),
               f"/documentos/{de_conteudo}/grupos")

    def aula(nome, linhas, arquivo=None):
        analises = pasta / nome / "analises"
        analises.mkdir(parents=True)
        arquivo = arquivo or f"{forma['prefixo_arquivo']}5{mundo['extensao']}"
        if linhas is not None:
            (analises / arquivo).write_text("\n".join(linhas) + "\n", encoding="utf-8")
        return analises

    trecho = escreve_caso(sorteia_caso("grupo", mundo), mundo)
    slide = f"{forma['prefixo_slide']}2"
    arquivo = f"{forma['prefixo_arquivo']}5{mundo['extensao']}"
    ultimo = forma["campos"][-1]["nome"]
    sem_ultimo = trecho["linha"][:trecho["linha"].rindex(forma["separador_campos"] + ultimo + ": ")]
    for nome, linhas, culpado in [
        ("linha-fora-da-forma", [slide, trecho["linha"], palavras()], f"{arquivo}:3"),
        ("item-sem-campos", [slide, f"{forma['marca_item']}0 {palavras()}"], f"{arquivo}:2"),
        ("campo-faltando", [slide, sem_ultimo], ultimo),
        ("slide-sem-numero", [forma["prefixo_slide"] + ascii_(), trecho["linha"]], f"{arquivo}:1"),
        ("sem-analises", None, forma["arquivos"]),
        ("id-repetido", [slide, trecho["linha"], slide, trecho["linha"]], id_esperado(trecho, "5", 2, 1)),
    ]:
        saida.append((nome, "analises", forma, regras, aula(nome, linhas), culpado))
    for nome, quebrado in [("parentese-que-nao-fecha", f"{palavra()} ({palavras()}"),
                           ("parentese-que-fecha-sem-abrir", f"{palavra()}) {palavra()} ({palavra()}")]:
        linha = compoe_linha(forma, trecho["texto"], dict(trecho["brutos"], **{nomes["destino"]: quebrado}))
        saida.append((nome, "analises", forma, regras, aula(nome, [slide, linha]), (f"{arquivo}:2", nomes["destino"])))
    qualquer = dict(forma, arquivos=forma["prefixo_arquivo"] + "*")
    em_dois = aula("aula-em-dois-arquivos", [slide, trecho["linha"]], f"{forma['prefixo_arquivo']}5.a")
    (em_dois / f"{forma['prefixo_arquivo']}5.b").write_text(f"{slide}\n{trecho['linha']}\n", encoding="utf-8")
    saida.append(("aula-em-dois-arquivos", "analises", qualquer, regras, em_dois, f"{forma['prefixo_arquivo']}5.b"))
    return saida


def diz(mensagem, culpado):
    """Se a mensagem diz o culpado: um texto, cada um de varios, ou nada (None)."""
    return all(c in mensagem for c in ((culpado,) if isinstance(culpado, str) else culpado or ()))
