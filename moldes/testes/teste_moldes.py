"""
Testes das partes da peca dos moldes que outros programas importam: o leitor das analises
(analises.py), as regras de lugar (lugares.py), as tabelas (relatorio.py), a leitura de
tabelas em texto (tabela.py), a tabela dos destinos (destinos.py), o limite por aula
(limite.py) e o molde da forma das analises. A contagem e as listas, com as entradas
comuns dos dois, tem o teste delas, o teste_contar_e_separar.py.

O mundo e sorteado pelo mundo_inventado.py, desta pasta, com uma semente fixa (o sorteio e
o mesmo em toda rodada; outra semente vem com --semente). Sorteados aqui: tabelas em
texto, a tabela dos destinos dos pedacos lidos e lugares para o limite, com todos os casos
das regras dele.

Os testes conferem regras que valem para qualquer forma, nunca uma lista pronta:
  - os moldes declaram as formas de campo e os papeis que o codigo conhece; a forma com a
    fonte que um campo cita passa pelo molde;
  - cada trecho sorteado e lido de volta, na ordem, com o texto, cada campo e cada papel;
    as notas sao contadas, e o que vem depois de um titulo nao e lido; os pedacos sao os
    escritos, inteiros, sem o vazio e sem repetir;
  - o id e aula/slide/posicao/hash, unico; a posicao conta os trechos do slide; o hash e o
    do texto em NFC; outro texto da outro id; o le_codigo le de volta cada id, e cada comeco
    dele, nas partes dele, e nao le o que nao e id nem comeco de um;
  - o lugar de cada trecho e o do caso dele: a classe, as marcas, os documentos e os grupos
    que as regras nao tem; um mesmo problema sai sempre com a mesma frase, e problemas
    diferentes com frases diferentes;
  - a tabela tem o cabecalho, o alinhamento e uma linha por item; a das classes tem uma
    linha por regra de fora e por marca, as outras classes com trecho e o total, e cada
    classe tem um rotulo so dela;
  - a tabela em texto da cada linha com o numero dela e os valores sem os espacos das
    pontas, sem as linhas em branco, com qualquer fim de linha; a linha com menos colunas
    tem vazias as que faltam no fim; cabecalho errado e linha com mais colunas sao erro que
    diz o nome e a linha;
  - a tabela dos destinos da a cada trecho os ids dos pedacos dele, na ordem e sem repetir,
    comparando em NFC, e lista uma vez cada pedaco sem linha, com os trechos dele; a linha
    com a unidade vazia, com a tabulacao do fim ou sem ela, nao falta; linha repetida, sem
    destino ou que contradiz outra e erro que diz a linha; destino que nao esta em pedacos
    e erro; cada id que o programa que usa a tabela nao conhece sai com o pedaco dele;
  - o limite: trata a aula que diz pelo menos as partes pedidas, so pelos lugares diretos; a
    decisao vale no lugar da conta; a unidade com itens tem material quando algum item e
    tratado; o lugar ate a ultima aula fica em unidade com material, mesmo em item so
    mencionado; depois da ultima, so fica o que cai em entrada tratada; cada trecho sem
    lugar sai na lista certa; as perguntas de cada trecho de depois vao so para aulas ate a
    ultima; a ordem dos lugares nao muda o que fica; entradas que se contradizem sao erro
    que diz cada uma;
  - forma, regras e analises erradas: a conferencia da parte errada (a forma, as regras ou
    a leitura) e a que pega o erro e diz o que esta errado, e a leitura das analises pelas
    regras para com o erro dessa parte;
  - duas rodadas dao a mesma saida.
Uso:
    python3 -I teste_moldes.py <pasta da peca> <pasta de trabalho nova> [--semente N]
Precisa do extrator_comum.py, do extrator, na pasta irma "extrator" da peca ou na propria
pasta da peca.
"""
import argparse
import collections
import copy
import json
import re
import sys
import unicodedata
from pathlib import Path


def argumentos():
    p = argparse.ArgumentParser(description="Testes das partes comuns da peça dos moldes.")
    p.add_argument("peca", type=Path, help="a pasta da peça")
    p.add_argument("trabalho", type=Path, help="uma pasta de trabalho nova")
    p.add_argument("--semente", type=int, default=1, help="a semente do sorteio")
    return p.parse_args()


ARGS = argumentos()
PECA, TRABALHO = ARGS.peca.resolve(), ARGS.trabalho.resolve()
for pasta in (PECA.parent / "extrator", PECA):  # na prateleira, o extrator fica na pasta irma
    sys.path.insert(0, str(pasta))
sys.path.insert(1, str(Path(__file__).resolve().parent))
import analises  # noqa: E402
import destinos  # noqa: E402
import extrator_comum  # noqa: E402
import limite  # noqa: E402
import lugares  # noqa: E402
import relatorio  # noqa: E402
import tabela  # noqa: E402
from mundo_inventado import (CASOS, SORTEIO, ascii_, classe_esperada, classes_esperadas, diz,  # noqa: E402
                             distintos, documentos_esperados, escreve_caso, frases_dos_problemas,
                             grupos_desconhecidos_esperados, id_esperado, marcas_esperadas, palavra, palavras,
                             sorteia_caso, sorteia_chaves, sorteia_mundo, unicos, variantes)  # -- nesta pasta

SORTEIO.seed(ARGS.semente)
FALHAS = []
CLASSES_DO_LIMITE = [("unidade",), ("limite",), ("depois",)]  # as classes da aplicacao das unidades e do limite
ERRO_DA_PARTE = {"forma": analises.ErroDeForma, "regras": lugares.ErroDeRegras,  # o erro da leitura pelas regras,
                 "analises": analises.ErroDeForma}  # para cada parte errada


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
        print(f"FALHA: {descricao}")
    return condicao


# ---------- os testes ----------

def teste_moldes_declaram():
    molde = json.loads((PECA / "esquemas" / "forma-analise.schema.json").read_text(encoding="utf-8"))
    campo = molde["$defs"]["campo"]["properties"]
    confere(campo["forma"]["enum"] == list(analises.FORMAS), "o molde da forma declara as formas que o código lê")
    confere(campo["papel"]["enum"] == list(analises.PAPEIS), "o molde da forma declara os papéis que o código conhece")


def teste_fonte(mundo):
    """A forma sorteada, com a fonte que um dos campos cita, passa pelo molde."""
    try:
        lida = extrator_comum.le_conferido(mundo["arquivo_forma"], PECA / "esquemas" / "forma-analise.schema.json")
        confere(lida == mundo["forma"] and any("fonte" in c for c in lida["campos"]),
                "a forma com a fonte que um campo cita passa pelo molde")
    except extrator_comum.ErroDeDados as e:
        confere(False, f"a forma com a fonte que um campo cita passa pelo molde: {e}")


def teste_leitura(mundo):
    trechos, notas, aulas = analises.ler_analises(mundo["pasta"], mundo["forma"])
    esperados = mundo["esperados"]
    confere(aulas == [a["chave"] for a in mundo["aulas"]], f"aulas em ordem natural: {aulas}")
    confere(notas == {a["chave"]: a["notas"] for a in mundo["aulas"]}, f"notas contadas por aula: {notas}")
    confere(len(trechos) == len(esperados), f"todos os trechos lidos, e só eles: {len(trechos)} de {len(esperados)}")
    erradas = collections.Counter()
    for t, (caso, chave, slide, posicao) in zip(trechos, esperados):
        papeis = {c["papel"]: {"valor": caso["valores"][c["nome"]], "texto": caso["brutos"][c["nome"]]}
                  for c in mundo["forma"]["campos"] if "papel" in c}
        erradas.update(nome for nome, certo in [
            ("id", t["id"] == id_esperado(caso, chave, slide, posicao)),
            ("aula, slide e posição", (t["aula"], t["slide"], t["posicao"]) == (chave, slide, posicao)),
            ("texto", t["texto"] == caso["texto"]), ("texto de cada campo", t["brutos"] == caso["brutos"]),
            ("valor de cada campo", t["valores"] == caso["valores"]),
            ("valor e texto de cada papel", t["papeis"] == papeis),
        ] if not certo)
    for nome, n in sorted(erradas.items()):
        confere(False, f"leitura: {nome} errado em {n} trecho(s)")
    confere(len({t["id"] for t in trechos}) == len(trechos), "ids únicos")
    confere(analises.ler_analises(mundo["pasta"], mundo["forma"])[0] == trechos, "duas leituras, os mesmos trechos")
    return trechos


def teste_id(mundo):
    forma = mundo["forma"]
    caso = escreve_caso(sorteia_caso("grupo", mundo, ["nfd"]), mundo)
    nfc = unicodedata.normalize("NFC", caso["linha"])
    outro = escreve_caso(sorteia_caso("grupo", mundo), mundo)["linha"]
    ids = {}
    for nome, linha in [("nfd", caso["linha"]), ("nfc", nfc), ("outro", outro)]:
        pasta = TRABALHO / "id" / nome
        pasta.mkdir(parents=True)
        (pasta / f"{forma['prefixo_arquivo']}7{mundo['extensao']}").write_text(
            f"{forma['prefixo_slide']}3\n{linha}\n", encoding="utf-8")
        ids[nome] = analises.ler_analises(pasta, forma)[0][0]["id"]
    confere(ids["nfd"] == ids["nfc"], "o mesmo texto em NFD e em NFC dá o mesmo id")
    confere(ids["outro"] != ids["nfc"], "outro texto dá outro id")
    confere(ids["outro"].rsplit("/", 1)[0] == ids["nfc"].rsplit("/", 1)[0] == "7/3/1",
            "o id começa pela aula, o slide e a posição")


def teste_codigo(trechos):
    """O le_codigo le de volta cada id lido, e cada comeco dele, nas partes dele, e nao le o que nao e id nem comeco de
    um."""
    s, digitos = analises.SEPARADOR_DO_ID, analises.DIGITOS_DO_HASH
    erradas = collections.Counter()
    for t in trechos:
        partes = [t["aula"], str(t["slide"]), str(t["posicao"])]
        resumo = t["id"].rsplit(s, 1)[-1]
        erradas["o id inteiro"] += analises.le_codigo(t["id"]) != analises.Codigo(t["aula"], t["slide"], t["posicao"],
                                                                                  resumo)
        for k, esperado in enumerate([(t["aula"], None, None), (t["aula"], t["slide"], None),
                                      (t["aula"], t["slide"], t["posicao"])], 1):
            erradas[f"o começo de {k} parte(s)"] += analises.le_codigo(s.join(partes[:k])) != analises.Codigo(
                *esperado, None)
    for nome, n in sorted(erradas.items()):
        confere(n == 0, f"código: {nome} lido errado em {n} trecho(s)")
    t = trechos[0]
    aula, slide, posicao, resumo = t["aula"], str(t["slide"]), str(t["posicao"]), t["id"].rsplit(s, 1)[-1]
    for descricao, texto in [
        ("vazio", ""), ("sem a aula", s.join(["", slide])), ("com uma parte a mais", s.join([t["id"], resumo])),
        ("com espaço na aula", s.join([f"{aula} {aula}", slide])), ("com uma parte vazia", s.join([aula, "", posicao])),
        ("com o slide zero", s.join([aula, "0"])), ("com zero na frente", s.join([aula, slide, "0" + posicao, resumo])),
        ("com o slide que não é número", s.join([aula, "x" + slide])),
        ("com o hash curto", s.join([aula, slide, posicao, resumo[:-1]])),
        ("com o hash em maiúsculas", s.join([aula, slide, posicao, "A" * digitos])),
        ("com o hash que não é hexadecimal", s.join([aula, slide, posicao, "g" * digitos])),
    ]:
        confere(analises.le_codigo(texto) is None, f"código: o texto {descricao} não é id nem começo de um: {texto!r}")


def teste_lugar(mundo, trechos):
    """Confere o lugar de cada trecho; devolve as frases dos problemas, para a contagem das
    classes."""
    regras, erradas = mundo["regras"], collections.Counter()
    for t, (caso, *_) in zip(trechos, mundo["esperados"]):
        classe, caidos = lugares.lugar(t, regras)
        esperada = classe_esperada(caso, mundo)
        if esperada[0] == "problema":
            erradas["classe de problema"] += classe[0] != "problema"
        else:
            erradas[f"classe {esperada[0]}"] += classe != esperada
        erradas["documentos"] += caidos != documentos_esperados(caso, mundo)
        erradas["marcas"] += lugares.marcas(t, regras) != marcas_esperadas(caso, mundo)
        erradas["grupos que as regras não têm"] += (lugares.grupos_desconhecidos(t, regras)
                                                    != grupos_desconhecidos_esperados(caso, mundo))
    for nome, n in sorted(erradas.items()):
        confere(n == 0, f"lugar: {nome} errado em {n} trecho(s)")
    frases = frases_dos_problemas(mundo, trechos, lugares.lugar)
    confere(all(len(f) == 1 for f in frases.values()), f"cada problema sai sempre com a mesma frase: {frases}")
    confere(len({min(f) for f in frases.values()}) == len(frases), "problemas diferentes, frases diferentes")
    presentes = {caso["tipo"] for caso, *_ in mundo["esperados"]}
    confere(presentes == set(CASOS), f"todos os casos sorteados: faltam {set(CASOS) - presentes}")
    return frases


def celulas(linha):
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", linha)[1:-1]]


def teste_tabelas(mundo, frases):
    k = SORTEIO.randint(2, 4)
    cabecalho = [palavra() for _ in range(k - 1)] + [f"{palavra()}|{palavra()}"]
    numericas = set(SORTEIO.sample(range(k), SORTEIO.randint(0, k)))
    linhas = [[SORTEIO.choice([palavras(1, 2), SORTEIO.randint(0, 999), f"{palavra()}|"]) for _ in range(k)]
              for _ in range(SORTEIO.randint(0, 5))]
    feita = relatorio.tabela(cabecalho, linhas, numericas)
    confere(len(feita) == len(linhas) + 2, "a tabela tem o cabeçalho, o alinhamento e uma linha por item")
    confere(celulas(feita[0]) == cabecalho, "o cabeçalho da tabela")
    confere(celulas(feita[1]) == ["---:" if i in numericas else "---" for i in range(k)], "o alinhamento da tabela")
    confere([celulas(t) for t in feita[2:]] == [[str(c) for c in linha] for linha in linhas],
            "cada linha da tabela, com a barra de dentro da célula escapada")

    regras = mundo["regras"]
    classes = classes_esperadas(mundo, frases)
    fora = SORTEIO.choice(regras["fora"])
    classes[("lido", fora["id"])] += SORTEIO.randint(1, 3)
    ausente = SORTEIO.choice(regras["marcas"])
    classes.pop(("marca", ausente["id"]), None)
    do_limite = SORTEIO.sample(CLASSES_DO_LIMITE, SORTEIO.randint(1, len(CLASSES_DO_LIMITE) - 1))
    for classe in do_limite:
        classes[classe] += SORTEIO.randint(1, 3)
    feita = relatorio.tabela_das_classes(classes, regras)
    corpo = [celulas(t) for t in feita[2:]]
    outras = [c for c in classes if c[0] not in ("estudo", "fora", "marca") and classes[c]]
    confere(len(corpo) == 1 + len(regras["fora"]) + len(regras["marcas"]) + len(outras) + 1,
            "a tabela das classes: estudo, cada regra de fora, cada marca, as outras com trecho e o total")
    confere(corpo[-1][1] == str(sum(classes.values())), "a última linha da tabela das classes é o total")
    linha_de = {rotulo: int(n) for rotulo, n in corpo[:-1]}
    for classe, nome in [(("marca", m["id"]), m["nome"]) for m in regras["marcas"]] + [
            (("fora", r["id"]), r["nome"]) for r in regras["fora"]] + [(("lido", fora["id"]), fora["nome"])]:
        confere(linha_de.get(relatorio.ROTULOS[classe[0]].format(nome)) == classes.get(classe, 0),
                f"a linha da classe {classe} na tabela das classes, com zero se não há trecho nela")
    for classe in CLASSES_DO_LIMITE:
        confere(linha_de.get(relatorio.ROTULOS[classe[0]]) == (classes[classe] if classe in do_limite else None),
                f"a classe {classe} sai na tabela das classes só quando há trecho nela, com quantos")
    todas = collections.Counter({classe: SORTEIO.randint(1, 3) for classe in CLASSES_DO_LIMITE})
    linha_de = {rotulo: int(n) for rotulo, n in (celulas(t) for t in relatorio.tabela_das_classes(todas, regras)[2:-1])}
    confere(all(linha_de.get(relatorio.ROTULOS[classe[0]]) == todas[classe] for classe in CLASSES_DO_LIMITE),
            "as classes da aplicação das unidades e do limite saem juntas, cada uma com quantos")
    confere(len(set(relatorio.ROTULOS.values())) == len(relatorio.ROTULOS), "cada classe tem um rótulo só dela")
    for estranha in [("lido", "nao-" + fora["id"]), (palavra(),)]:
        try:
            relatorio.tabela_das_classes(collections.Counter({estranha: 1}), regras)
            confere(False, f"classe desconhecida é erro: {estranha}")
        except ValueError:
            pass

    numeros = SORTEIO.sample(range(1, 200), SORTEIO.randint(3, 6))
    contagem = collections.Counter({str(n): SORTEIO.choice([1, 2]) for n in numeros})
    confere(relatorio.por_chave(contagem) == [(str(n), contagem[str(n)]) for n in sorted(numeros)],
            "por chave: na ordem natural (2 antes de 10)")
    confere(relatorio.por_quantidade(contagem) == sorted(contagem.items(), key=lambda kv: (-kv[1], int(kv[0]))),
            "por quantidade: do maior para o menor, o empate na ordem natural")


# ---------- a tabela em texto ----------

def com_espacos(valor):
    return SORTEIO.choice(["", " ", "  "]) + valor + SORTEIO.choice(["", " "])


def sorteia_tsv(fim):
    """(texto, cabecalho, linhas esperadas) de uma tabela sorteada, com o fim de linha dado:
    espacos nas pontas dos valores, valores vazios, linhas sem as colunas vazias do fim,
    aspas e parenteses, e linhas em branco (vazias, so com espacos ou so com tabulacoes, com
    o numero de colunas certo ou nao)."""
    cabecalho = distintos(ascii_, SORTEIO.randint(1, 4))
    linhas, esperado = [tabela.SEPARADOR.join(map(com_espacos, cabecalho))], []
    for _ in range(SORTEIO.randint(4, 9)):
        if SORTEIO.random() < 0.25:
            linhas.append(SORTEIO.choice(["", " ", tabela.SEPARADOR * len(cabecalho), f" {tabela.SEPARADOR} "]))
            continue
        valores = [SORTEIO.choice(["", palavras(1, 2), f'"{palavra()}', f"{palavra()} ({palavra()})"])
                   for _ in cabecalho]
        valores[SORTEIO.randrange(len(valores))] = palavras(1, 2)
        escritos = valores
        while not escritos[-1] and SORTEIO.random() < 0.5:  # o editor que tira as colunas vazias do fim
            escritos = escritos[:-1]
        linhas.append(tabela.SEPARADOR.join(map(com_espacos, escritos)))
        esperado.append((len(linhas), dict(zip(cabecalho, valores))))
    return fim.join(linhas) + SORTEIO.choice(["", fim]), cabecalho, esperado


def erro_de_tabela(ler, nome, linha, descricao):
    """Confere que ler() da ErroDeTabela que diz o nome e a linha."""
    try:
        ler()
        confere(False, f"tabela em texto: {descricao} é erro")
    except tabela.ErroDeTabela as e:
        confere(nome in str(e) and f"linha {linha}" in str(e),
                f"tabela em texto: o erro de {descricao} diz o nome e a linha {linha}: {e}")


def teste_tsv():
    nome = palavra()
    for fim in ("\n", "\r\n"):
        texto, cabecalho, esperado = sorteia_tsv(fim)
        confere(tabela.ler(texto, cabecalho, nome) == esperado,
                f"tabela em texto: cada linha com o número dela e os valores sem os espaços das pontas, sem as linhas "
                f"em branco (fim de linha {fim!r})")
        confere(tabela.ler(texto, tuple(cabecalho), nome) == esperado, "tabela em texto: o cabeçalho pode vir em tupla")
    linhas = texto.splitlines()
    outra = "x" + ascii_()
    primeiras = [("cabeçalho com outra coluna", [outra] + cabecalho[1:]), ("cabeçalho sem uma coluna", cabecalho[:-1]),
                 ("cabeçalho com uma coluna a mais", cabecalho + [outra])]
    if len(cabecalho) > 1:
        primeiras.append(("cabeçalho em outra ordem", cabecalho[::-1]))
    for descricao, colunas in primeiras:
        errado = "\n".join([tabela.SEPARADOR.join(colunas)] + linhas[1:])
        erro_de_tabela(lambda: tabela.ler(errado, cabecalho, nome), nome, 1, descricao)
    erro_de_tabela(lambda: tabela.ler("", cabecalho, nome), nome, 1, "texto vazio")
    n = SORTEIO.choice(esperado)[0]
    for k in (len(cabecalho) + 1, len(cabecalho) + SORTEIO.randint(2, 3)):
        errado = "\n".join(linhas[:n - 1] + [tabela.SEPARADOR.join(palavra() for _ in range(k))] + linhas[n:])
        erro_de_tabela(lambda: tabela.ler(errado, cabecalho, nome), nome, n, f"linha com {k} coluna(s)")
    curtos = [palavra() for _ in range(SORTEIO.randint(1, len(cabecalho)))]
    curta = "\n".join(linhas[:n - 1] + [tabela.SEPARADOR.join(curtos)] + linhas[n:])
    confere(dict(tabela.ler(curta, cabecalho, nome))[n] == dict(zip(cabecalho, curtos + [""] * len(cabecalho))),
            f"tabela em texto: a linha com {len(curtos)} coluna(s) de {len(cabecalho)} tem vazias as que faltam no fim")
    for colunas in ([], [cabecalho[0], cabecalho[0]]):
        try:
            tabela.ler(texto, colunas, nome)
            confere(False, f"tabela em texto: cabeçalho vazio ou com coluna repetida é erro: {colunas}")
        except tabela.ErroDeTabela:
            confere(False, f"tabela em texto: cabeçalho vazio ou repetido é erro de uso, não do texto: "
                    f"{colunas}")
        except ValueError:
            pass


# ---------- a tabela dos destinos ----------

def nfc(texto):
    return unicodedata.normalize("NFC", texto)


def sorteia_destinos(trechos):
    """(linhas da tabela, {pedaco: ids ou None}, caso de cada pedaco) dos pedacos dos destinos
    lidos, em NFC. Cada pedaco e de um caso: um id, varios, a unidade vazia ou sem linha;
    todos aparecem. Os dois primeiros pedacos de um trecho com dois ou mais nomeiam um mesmo
    id. As linhas vem em ordem sorteada, e os ids de cada pedaco sao os da ordem delas."""
    pedacos = unicos(nfc(p) for t in trechos for p in lugares.valor(t, "destino"))
    ids = distintos(ascii_, 6)
    com_dois = next(t for t in trechos if len(lugares.valor(t, "destino")) >= 2)
    primeiro, segundo = (nfc(p) for p in lugares.valor(com_dois, "destino")[:2])
    nomeados = {primeiro: [ids[0]] + SORTEIO.sample(ids[1:], SORTEIO.randint(0, 1)),
                segundo: SORTEIO.sample(ids[1:], SORTEIO.randint(0, 1)) + [ids[0]]}
    casos = {primeiro: "comum", segundo: "comum"}
    escolhas = {"um": lambda: SORTEIO.sample(ids, 1), "varios": lambda: SORTEIO.sample(ids, SORTEIO.randint(2, 3)),
                "vazia": lambda: [], "sem": lambda: None}
    for k, p in enumerate(q for q in pedacos if q not in nomeados):
        casos[p] = list(escolhas)[k] if k < len(escolhas) else SORTEIO.choice(list(escolhas))
        nomeados[p] = escolhas[casos[p]]()
    linhas = [(p, i) for p, lista in nomeados.items() if lista is not None for i in (lista or [""])]
    SORTEIO.shuffle(linhas)
    na_tabela = {}
    for p, i in linhas:
        na_tabela.setdefault(p, []).extend([i] if i else [])
    return linhas, {p: na_tabela.get(p) for p in nomeados}, casos, com_dois


def texto_dos_destinos(linhas, fim="\n"):
    """O texto da tabela: o cabecalho e as linhas, cada destino em NFC ou NFD, com espacos nas
    pontas, a linha com a unidade vazia as vezes sem a tabulacao do fim, e linhas em branco
    no meio."""
    saida = [tabela.SEPARADOR.join(map(com_espacos, destinos.CABECALHO))]
    for p, i in linhas:
        if SORTEIO.random() < 0.2:
            saida.append(SORTEIO.choice(["", "  ", tabela.SEPARADOR]))
        escrito = com_espacos(unicodedata.normalize(SORTEIO.choice(["NFC", "NFD"]), p))
        if i or SORTEIO.random() < 0.5:  # sem a unidade, a tabulacao do fim pode faltar
            escrito += f"{tabela.SEPARADOR}{com_espacos(i)}"
        saida.append(escrito)
    return fim.join(saida)


def erro_de_destinos(ler, culpados, descricao):
    try:
        ler()
        confere(False, f"destinos: {descricao} é erro")
    except destinos.ErroDeDestinos as e:
        confere(all(c in str(e) for c in culpados), f"destinos: o erro de {descricao} diz {culpados}: {e}")


def teste_destinos(trechos):
    nome = palavra()
    linhas, nomeados, casos, com_dois = sorteia_destinos(trechos)
    confere(set(casos.values()) == {"comum", "um", "varios", "vazia", "sem"},
            f"destinos: todos os casos sorteados: {sorted(set(casos.values()))}")
    texto = texto_dos_destinos(linhas, SORTEIO.choice(["\n", "\r\n"]))
    lido = destinos.ler(texto, nome)
    confere(lido == {p: lista for p, lista in nomeados.items() if lista is not None},
            "destinos: a tabela dá a cada pedaço os ids, na ordem das linhas, e a lista vazia ao que não nomeia nenhum")
    ids, faltam = destinos.ids_dos_trechos(trechos, lido)
    esperados = {t["id"]: unicos(i for p in lugares.valor(t, "destino") for i in (nomeados[nfc(p)] or []))
                 for t in trechos}
    confere(ids == esperados, "destinos: cada trecho com os ids dos pedaços dele, na ordem dos pedaços e sem repetir")
    primeiro, segundo = (nfc(p) for p in lugares.valor(com_dois, "destino")[:2])
    comuns = set(nomeados[primeiro]) & set(nomeados[segundo])
    confere(comuns and all(ids[com_dois["id"]].count(i) == 1 for i in comuns),
            "destinos: o id que dois pedaços do trecho nomeiam sai uma vez")
    sem_linha = {}
    for t in trechos:
        for p in map(nfc, lugares.valor(t, "destino")):
            if nomeados[p] is None and t["id"] not in sem_linha.setdefault(p, []):
                sem_linha[p].append(t["id"])
    confere(list(faltam.items()) == list(sem_linha.items()),
            "destinos: cada pedaço sem linha uma vez, na ordem em que aparece, com os trechos dele; o da unidade vazia "
            "não falta")
    vazio = copy.deepcopy(trechos[0])
    vazio["papeis"]["destino"]["valor"] = []
    confere(destinos.ids_dos_trechos([vazio], lido) == ({vazio["id"]: []}, {}), "destinos: destino sem pedaço, sem id")
    confere(destinos.ids_dos_trechos(trechos, destinos.ler(texto, nome)) == (ids, faltam), "destinos: duas rodadas, "
            "a mesma saída")
    da_tabela = unicos(i for lista in lido.values() for i in lista)
    sem_nome = set(SORTEIO.sample(da_tabela, SORTEIO.randint(1, len(da_tabela))))
    outro = palavra()
    while outro in da_tabela:
        outro = palavra()
    conhecidos = set(da_tabela) - sem_nome | {outro}
    confere(destinos.desconhecidos(lido, conhecidos) == [(p, i) for p, lista in lido.items() for i in lista
                                                         if i in sem_nome],
            "destinos: cada id que o programa que usa a tabela não conhece sai com o pedaço dele, na ordem da tabela")
    confere(destinos.desconhecidos(lido, set(da_tabela)) == [], "destinos: com todos os ids conhecidos, nenhum sai")

    base = texto_dos_destinos(linhas).split("\n")
    com_ids = SORTEIO.choice([p for p, c in casos.items() if c in ("um", "varios", "comum")])
    sem_unidade = SORTEIO.choice([p for p, c in casos.items() if c == "vazia"])
    extras = [("linha repetida", (unicodedata.normalize("NFD", com_ids), f" {nomeados[com_ids][0]}")),
              ("linha com a unidade vazia repetida", (sem_unidade, "")),
              ("unidade vazia num destino com unidade", (com_ids, "")),
              ("unidade num destino com a unidade vazia", (sem_unidade, nomeados[com_ids][0])),
              ("linha sem o destino", ("", nomeados[com_ids][0]))]
    for descricao, (p, i) in extras:
        errado = "\n".join(base + [f"{p}{tabela.SEPARADOR}{i}"])
        erro_de_destinos(lambda: destinos.ler(errado, nome), (nome, f"linha {len(base) + 1}"), descricao)
    todos = "\n".join(base + [f"{p}{tabela.SEPARADOR}{i}" for _, (p, i) in extras])
    erro_de_destinos(lambda: destinos.ler(todos, nome), [f"linha {len(base) + k}" for k in range(1, len(extras) + 1)],
                     "cada linha errada, todas de uma vez")
    try:
        destinos.ler("\n".join([palavra()] + base[1:]), nome)
        confere(False, "destinos: a tabela sem o cabeçalho é erro")
    except ValueError as e:
        confere(nome in str(e), f"destinos: o erro do cabeçalho diz o nome da tabela: {e}")
    texto_corrido = copy.deepcopy(trechos[0])
    texto_corrido["papeis"]["destino"]["valor"] = texto_corrido["papeis"]["destino"]["texto"]
    erro_de_destinos(lambda: destinos.ids_dos_trechos([texto_corrido], lido), (texto_corrido["id"],),
                     "destino que não está em pedaços")


# ---------- o limite ----------

def sorteia_limite():
    """Lugares sorteados para o limite, com todos os casos das regras dele, e o que cada caso
    deve dar. Os casos ficam em entradas proprias, e os lugares sorteados a mais, noutras."""
    aulas = sorteia_chaves(SORTEIO.randint(4, 6))
    corte = SORTEIO.randint(1, len(aulas) - 2)
    a, b = SORTEIO.sample(aulas[:corte + 1], 2)
    d = SORTEIO.choice(aulas[corte + 1:])
    n = SORTEIO.randint(1, 3)
    nomes = distintos(ascii_, 20)
    tratada, indireta, mencionada, decidida_nao, decidida_sim = nomes[:5]
    com_material, sem_material, item_tratado, item_mencionado, item_depois = nomes[5:10]
    itens_sem = nomes[10:12]
    soltas, soltas_com_itens, soltos_itens = nomes[12:15], nomes[15], nomes[16:18]
    unidade_de = {item_tratado: com_material, item_mencionado: com_material, item_depois: com_material}
    unidade_de.update({i: sem_material for i in itens_sem})
    unidade_de.update({i: soltas_com_itens for i in soltos_itens})
    partes = distintos(ascii_, n + 2) + [None]
    lugares_, casos = [], {}

    def trecho(caso, aula, *onde):
        """Um trecho novo da aula, com um lugar em cada (entrada, parte, direto)."""
        t = f"{aula}·{len(casos)}"
        casos[t] = caso
        lugares_.extend(limite.Lugar(t, aula, e, p, direto) for e, p, direto in onde)
        return t

    def diretos(entrada, quantas, caso, aula):
        """As partes dadas, diretas, em um trecho ou em um por parte."""
        escolhidas = SORTEIO.sample(partes, quantas)
        if SORTEIO.random() < 0.5:
            return [trecho(caso, aula, *[(entrada, p, True) for p in escolhidas])] if escolhidas else []
        return [trecho(caso, aula, (entrada, p, True)) for p in escolhidas]

    diretos(tratada, n, "tratada", a)
    diretos(tratada, n - 1, "tratada", b)
    diretos(tratada, n, "tratada_depois", d)
    so_indireta = trecho("so_indireta", a, *[(indireta, p, False) for p in SORTEIO.sample(partes, n + 1)])
    diretos(indireta, n - 1, "indireta", a)
    trecho("mencionada", b, (mencionada, SORTEIO.choice(partes), False))
    mencionada_depois = trecho("mencionada_depois", d, *[(mencionada, p, True) for p in SORTEIO.sample(partes, n)])
    diretos(decidida_nao, n, "decidida_nao", a)
    trecho("decidida_sim", b, (decidida_sim, SORTEIO.choice(partes), False))
    decidida_depois = trecho("decidida_depois", d, (decidida_sim, SORTEIO.choice(partes), True))
    diretos(item_tratado, n, "item_tratado", a)
    item_so_mencionado = trecho("item_mencionado", b, (item_mencionado, SORTEIO.choice(partes), False))
    trecho("item_depois", d, (item_depois, SORTEIO.choice(partes), True))
    abertura_depois = trecho("abertura_depois", d, (com_material, SORTEIO.choice(partes), True))
    for i in itens_sem:
        trecho("item_sem", a, (i, SORTEIO.choice(partes), False))
    diretos(sem_material, n, "abertura_sem", b)
    trecho("misto", SORTEIO.choice([a, b]), (tratada, SORTEIO.choice(partes), True),
           (indireta, SORTEIO.choice(partes), False))
    misto_depois = trecho("misto_depois", d, (tratada, SORTEIO.choice(partes), True),
                          (mencionada, SORTEIO.choice(partes), False))
    entradas = soltas + [soltas_com_itens] + soltos_itens
    for _ in range(SORTEIO.randint(10, 20)):
        trecho("solto", SORTEIO.choice(aulas), *[(SORTEIO.choice(entradas), SORTEIO.choice(partes),
                                                   SORTEIO.random() < 0.7) for _ in range(SORTEIO.randint(1, 3))])
    SORTEIO.shuffle(lugares_)
    entrada = {"lugares": lugares_, "unidade_de": unidade_de, "aulas": aulas, "ultima": aulas[corte],
               "partes_para_tratar": n, "decisoes": {decidida_nao: [], decidida_sim: [b]}}
    nomes_dos_casos = {"a": a, "b": b, "d": d, "tratada": tratada, "indireta": indireta, "mencionada": mencionada,
                       "decidida_nao": decidida_nao, "decidida_sim": decidida_sim, "com_material": com_material,
                       "sem_material": sem_material, "item_mencionado": item_mencionado, "item_depois": item_depois,
                       "so_indireta": so_indireta, "mencionada_depois": mencionada_depois,
                       "decidida_depois": decidida_depois, "item_so_mencionado": item_so_mencionado,
                       "abertura_depois": abertura_depois, "misto_depois": misto_depois}
    return entrada, nomes_dos_casos


def limite_esperado(entrada):
    """O que as regras do limite dao para as entradas, contado a mao, um caso de cada vez."""
    lugares_, unidade_de, aulas = entrada["lugares"], entrada["unidade_de"], entrada["aulas"]
    partes_para_tratar, decisoes = entrada["partes_para_tratar"], entrada["decisoes"]
    ate = set(aulas[:aulas.index(entrada["ultima"]) + 1])
    com_itens = set(unidade_de.values())
    entradas = unicos(e for l in lugares_ for e in (l.entrada, unidade_de.get(l.entrada, l.entrada)))

    def diretas(e, aula):
        return {l.parte for l in lugares_ if l.entrada == e and l.aula == aula and l.direto}

    def tratam(e):
        if e in com_itens:
            return [x for x in aulas if any(x in tratam(i) for i, u in unidade_de.items() if u == e)]
        if e in decisoes:
            return [x for x in aulas if x in decisoes[e]]
        return [x for x in aulas if len(diretas(e, x)) >= partes_para_tratar]

    def com_lugar(e):
        return {l.aula for l in lugares_ if e in (l.entrada, unidade_de.get(l.entrada))}

    tratam_ = {e: tratam(e) for e in entradas}
    tratadas = {e for e in entradas if set(tratam_[e]) & ate}

    def fica(l):
        return (unidade_de.get(l.entrada, l.entrada) if l.aula in ate else l.entrada) in tratadas

    trechos = unicos(l.trecho for l in lugares_)
    seus = {t: [l for l in lugares_ if l.trecho == t] for t in trechos}
    return {
        "partes": {e: {x: set(diretas(e, x)) for x in aulas if diretas(e, x)} for e in entradas
                   if any(diretas(e, x) for x in aulas)},
        "tratam": tratam_,
        "mencionam": {e: [x for x in aulas if x in com_lugar(e) and x not in tratam_[e]] for e in entradas},
        "tratadas": tratadas,
        "com_material": tratadas - set(unidade_de),
        "ficam": [l for l in lugares_ if fica(l)],
        "sem_lugar_ate": {t: seus[t] for t in trechos if seus[t][0].aula in ate and not any(map(fica, seus[t]))},
        "sem_lugar_depois": {t: seus[t] for t in trechos if seus[t][0].aula not in ate and not any(map(fica, seus[t]))},
        "perguntas": {t: [x for x in aulas if x in ate and any(x in tratam_[l.entrada] for l in seus[t] if fica(l))]
                      for t in trechos if seus[t][0].aula not in ate and any(map(fica, seus[t]))},
    }


def confere_limite(r, esperado, aulas, como):
    """Confere o Limite contra o esperado; 'como' diz de que rodada ele e."""
    confere({e: {x: set(p) for x, p in por_aula.items()} for e, por_aula in r.partes.items()} == esperado["partes"]
            and all(len(p) == len(set(p)) for por_aula in r.partes.values() for p in por_aula.values()),
            f"limite ({como}): as partes distintas dos lugares diretos de cada aula em cada entrada")
    confere(all(list(por_aula) == [x for x in aulas if x in por_aula] for por_aula in r.partes.values()),
            f"limite ({como}): as partes de cada entrada na ordem das aulas")
    for campo in ("tratam", "mencionam", "sem_lugar_ate", "sem_lugar_depois", "perguntas"):
        confere(getattr(r, campo) == esperado[campo], f"limite ({como}): {campo}")
    confere(set(r.tratadas) == esperado["tratadas"] and len(r.tratadas) == len(set(r.tratadas)),
            f"limite ({como}): as entradas tratadas, cada uma uma vez")
    confere(set(r.com_material) == esperado["com_material"] and len(r.com_material) == len(set(r.com_material)),
            f"limite ({como}): as unidades com material, cada uma uma vez")
    confere(r.ficam == esperado["ficam"], f"limite ({como}): os lugares que ficam, na ordem dos lugares")


def lugares_de(entrada, trecho):
    return [l for l in entrada["lugares"] if l.trecho == trecho]


def teste_limite():
    entrada, c = sorteia_limite()
    r = limite.aplicar(**entrada)
    confere_limite(r, limite_esperado(entrada), entrada["aulas"], "sorteado")
    confere(limite.aplicar(**entrada) == r, "limite: duas rodadas, a mesma saída")
    embaralhada = dict(entrada, lugares=SORTEIO.sample(entrada["lugares"], len(entrada["lugares"])))
    outra = limite.aplicar(**embaralhada)
    confere_limite(outra, limite_esperado(embaralhada), entrada["aulas"], "com os lugares em outra ordem")
    confere(set(outra.ficam) == set(r.ficam) and outra.tratam == r.tratam and outra.perguntas == r.perguntas
            and set(outra.sem_lugar_ate) == set(r.sem_lugar_ate), "limite: a ordem dos lugares não muda o que fica")

    n, a, b = entrada["partes_para_tratar"], c["a"], c["b"]

    def partes_em(e, aula, direto=None):
        return {l.parte for l in entrada["lugares"] if l.entrada == e and l.aula == aula
                and (direto is None or l.direto == direto)}

    for condicao, descricao in [
        (a in r.tratam[c["tratada"]], "trata a aula que diz as partes pedidas, diretas"),
        (len(partes_em(c["indireta"], a)) >= n > len(partes_em(c["indireta"], a, True))
         and a not in r.tratam[c["indireta"]], "os lugares indiretos não contam para tratar"),
        (len(partes_em(c["decidida_nao"], a, True)) >= n and r.tratam[c["decidida_nao"]] == [],
         "a decisão vale no lugar da conta, quando nenhuma aula trata"),
        (r.tratam[c["decidida_sim"]] == [b] and not partes_em(c["decidida_sim"], b, True),
         "a decisão vale no lugar da conta, quando a conta não trata"),
        (c["com_material"] in r.com_material and c["sem_material"] not in r.com_material
         and len(partes_em(c["sem_material"], b, True)) >= n,
         "a unidade com itens tem material só quando algum item dela é tratado"),
        (c["item_mencionado"] not in r.tratadas and set(lugares_de(entrada, c["item_so_mencionado"])) <= set(r.ficam),
         "o lugar até a última aula num item só mencionado fica, na unidade com material"),
        (c["item_depois"] not in r.tratadas and c["mencionada"] not in r.tratadas
         and c["mencionada_depois"] in r.sem_lugar_depois,
         "depois da última aula, sai o que não cai em entrada tratada"),
        (c["abertura_depois"] in r.perguntas and set(lugares_de(entrada, c["abertura_depois"])) <= set(r.ficam),
         "depois da última aula, o lugar na abertura de uma unidade com material fica"),
        (c["so_indireta"] in r.sem_lugar_ate,
         "o trecho até a última aula que perdeu todos os lugares sai na lista dele"),
        (r.perguntas.get(c["decidida_depois"]) == [b],
         "as perguntas do trecho de depois: as aulas que tratam da entrada"),
        (c["misto_depois"] in r.perguntas and not set(lugares_de(entrada, c["misto_depois"])) <= set(r.ficam),
         "o trecho de depois que perde um lugar e fica noutro vai para as perguntas"),
        (c["d"] in r.tratam[c["tratada"]] and c["d"] not in r.perguntas.get(c["misto_depois"], [c["d"]]),
         "as perguntas de um trecho de depois vão só para aulas até a última"),
    ]:
        confere(condicao, f"limite: {descricao}")

    estranho = "x" + ascii_()
    um = entrada["lugares"][0]
    outra_aula = next(x for x in entrada["aulas"] if x != um.aula)
    errados = [
        ("partes para tratar zero", {"partes_para_tratar": 0}, "0"),
        ("partes para tratar negativo", {"partes_para_tratar": -1}, "-1"),
        ("partes para tratar em texto", {"partes_para_tratar": str(n)}, repr(str(n))),
        ("partes para tratar booleano", {"partes_para_tratar": True}, "True"),
        ("partes para tratar com fração", {"partes_para_tratar": n + 0.5}, str(n + 0.5)),
        ("última aula que não está entre as aulas", {"ultima": estranho}, estranho),
        ("aula repetida", {"aulas": entrada["aulas"] + [a]}, a),
        ("lugar de aula que não está entre as aulas",
         {"lugares": entrada["lugares"] + [um._replace(trecho=estranho, aula=estranho)]}, estranho),
        ("trecho em duas aulas", {"lugares": entrada["lugares"] + [um._replace(aula=outra_aula)]}, um.trecho),
        ("item que é unidade com itens", {"unidade_de": dict(entrada["unidade_de"], **{c["com_material"]: estranho})},
         c["com_material"]),
        ("decisão para unidade com itens", {"decisoes": dict(entrada["decisoes"], **{c["com_material"]: [a]})},
         c["com_material"]),
        ("decisão para entrada sem lugar", {"decisoes": dict(entrada["decisoes"], **{estranho: []})}, estranho),
        ("decisão com aula que não está entre as aulas",
         {"decisoes": dict(entrada["decisoes"], **{c["decidida_sim"]: [b, estranho]})}, estranho),
        ("decisão com aula depois da última",
         {"decisoes": dict(entrada["decisoes"], **{c["decidida_sim"]: [b, c["d"]]})}, c["d"]),
        ("decisão com aula sem trecho na entrada",
         {"decisoes": dict(entrada["decisoes"], **{c["decidida_sim"]: [b, a]})}, a),
    ]
    for descricao, muda, culpado in errados:
        try:
            limite.aplicar(**dict(entrada, **muda))
            confere(False, f"limite: {descricao} é erro")
        except limite.ErroDeLimite as e:
            confere(culpado in str(e), f"limite: o erro de {descricao} diz {culpado!r}: {e}")
    juntos = [e for e in errados if e[0] in ("última aula que não está entre as aulas", "aula repetida",
                                             "trecho em duas aulas", "item que é unidade com itens")]
    try:
        limite.aplicar(**dict(entrada, **{k: v for _, muda, _ in juntos for k, v in muda.items()}))
        confere(False, "limite: várias entradas erradas são erro")
    except limite.ErroDeLimite as e:
        confere(all(culpado in str(e) for _, _, culpado in juntos), f"limite: várias entradas erradas, cada uma no "
                f"erro: {e}")


# ---------- a forma, as regras e as analises erradas ----------

def erros_na_funcao(onde, forma, regras, pasta):
    """O que a funcao que confere cada parte diz do erro: a lista de problemas da forma ou
    das regras, ou a mensagem do erro da leitura (vazia quando a leitura passa)."""
    if onde == "forma":
        return analises.erros_da_forma(forma)
    if onde == "regras":
        return lugares.erros_das_regras(regras, forma)
    try:
        analises.ler_analises(pasta, forma)
        return []
    except analises.ErroDeForma as e:
        return [str(e)]


def erro_da_leitura(forma, regras, pasta):
    """O erro que a leitura das analises pelas regras (lugares.trechos_das_analises)
    levanta, seja ele qual for, para a FALHA dizer qual veio; None quando ela passa."""
    try:
        lugares.trechos_das_analises(pasta, forma, regras)
    except Exception as e:  # qualquer um: o tipo dele e o que a conferencia olha
        return e
    return None


def teste_erros(mundo):
    for nome, onde, forma, regras, pasta, culpado in variantes(mundo, TRABALHO / "erros"):
        if onde not in ERRO_DA_PARTE:
            continue
        erros = erros_na_funcao(onde, forma, regras, pasta)
        confere(erros and any(diz(e, culpado) for e in erros),
                f"erro {nome}: a conferência da parte ({onde}) o pega e diz {culpado!r}: {erros}")
        erro = erro_da_leitura(forma, regras, pasta)
        confere(isinstance(erro, ERRO_DA_PARTE[onde]) and diz(str(erro), culpado),
                f"erro {nome}: a leitura pelas regras para com o erro da parte ({onde}), que diz {culpado!r}: {erro!r}")


def main():
    if TRABALHO.exists() and any(TRABALHO.iterdir()):
        sys.exit("a pasta de trabalho precisa ser nova ou vazia")
    TRABALHO.mkdir(parents=True, exist_ok=True)
    teste_moldes_declaram()
    mundo = sorteia_mundo(TRABALHO / "mundo")
    teste_fonte(mundo)
    trechos = teste_leitura(mundo)
    teste_id(mundo)
    teste_codigo(trechos)
    frases = teste_lugar(mundo, trechos)
    teste_tabelas(mundo, frases)
    teste_tsv()
    teste_destinos(trechos)
    teste_limite()
    teste_erros(mundo)
    print(f"{len(FALHAS)} falha(s) (semente {ARGS.semente})")
    sys.exit(1 if FALHAS else 0)


if __name__ == "__main__":
    main()
