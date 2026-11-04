"""Testes do listas_e_tabelas.py, com projetos inventados aqui, sorteados e com letras de fora do
ASCII: a configuracao, os modelos, tres listas num arquivo JSON (de objetos com campo unico, de
textos e de objetos sem campo unico), uma tabela CSV noutra pasta e as mudancas noutra, rodando
de outra pasta. Conferem regras, nunca uma frase pronta:
  - em cada forma sorteada do JSON (o recuo, tambem nenhum e o vazio, o escape fora do ASCII e o
    fim) e do CSV (a quebra de linha), o arquivo gravado e o que o json.dumps e o modulo csv do
    Python gravam, nessa forma, com as entradas juntadas ao fim de cada lista, na ordem, com as
    chaves na ordem das mudancas, e os campos trocados, e o resto como estava; os arquivos de
    entrada nao mudam;
  - o campo montado, no primeiro nivel ou dentro de uma lista da entrada, e cada item pelo
    texto do modelo, sorteado (palavras e campos em ordem sorteada, um campo duas vezes, linhas
    com dois espacos no fim), lido com as quebras \\r\\n como \\n e sem a quebra do fim, com cada
    campo trocado pelo valor (tambem o numero), os itens juntos com as linhas do texto entre no
    meio (vazio, de uma linha ou de duas), ou um na linha seguinte ao outro sem ele;
  - a chave da troca acha a linha tambem em outra forma Unicode;
  - o arquivo sem nada de fora do ASCII nos dados recebe as entradas novas como sao, sem escape;
  - o valor unico com outras maiusculas, e o objeto que so difere de outro no 1 e no verdadeiro,
    nao sao problema;
  - duas rodadas, em copias do mesmo projeto, dao o mesmo; rodar de novo as mesmas mudancas sai
    com 1, sem gravar nada;
  - o arquivo que nao volta igual (um espaco no fim de uma linha, as quebras \\r\\n, os
    separadores sem espaco, uma chave repetida e o escape em maiusculas, no JSON; aspas onde nao
    precisa, a falta da quebra do fim e as quebras misturadas, no CSV), o valor unico repetido
    (da lista, em outra forma Unicode, ou das mudancas), a entrada sem ele, a entrada da lista
    sem campo unico repetida (o texto e o objeto, com as chaves e os textos em outra forma
    Unicode), o campo montado que nao e lista de itens, o item sem um campo do
    modelo, com um a mais ou com um valor que nao e texto nem inteiro (tambem dentro de uma
    lista da entrada), a troca sem a chave, com a chave de nenhuma linha ou de duas, com uma
    coluna que a tabela nao tem, que nao muda nada ou que troca de novo a mesma coluna da mesma
    linha saem com 1, com o lugar no ERRO (o arquivo e a linha em que ele deixa de voltar igual,
    ou as mudancas e o caminho do valor), e nada e gravado;
  - a configuracao, as mudancas, um modelo, a lista e a tabela que nao servem (que faltam, que
    nao se leem, que saem do molde, tambem com um grupo vazio, que nomeiam o que nao existe, o
    arquivo de lista e de tabela, o caminho que nao leva a uma lista, a tabela sem cabecalho,
    com coluna repetida, com linha de outro tamanho ou sem a chave, o arquivo que e uma pasta ou
    uma das entradas, a configuracao, as mudancas ou um modelo, mesmo quando ele se le como lista
    ou como tabela, e o valor que nao se escreve em UTF-8) saem com 2, e nada e gravado.
Uso:
    python3 -I teste_listas_e_tabelas.py <pasta do listas_e_tabelas.py> <pasta de trabalho nova>
Precisa do extrator_comum.py, do texto_comum.py e do documento_gerado.py, nas pastas irmas da
peca.
"""
import copy
import csv
import io
import json
import random
import shutil
import string
import subprocess
import sys
import unicodedata
from pathlib import Path

PECA, TRABALHO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
FALHAS = []
SORTEIO = random.Random(1)
ACENTUADAS = "áçõüéñ"  # letras que a forma NFD escreve com o acento separado
LETRAS = string.ascii_letters + ACENTUADAS + "€✓"
USADOS = set()
RECUOS = [None, "", 1, 2, 4, "\t"]  # os do json.dumps: numa linha so, sem recuo, com espacos ou com tabulacao
FINS_JSON = ["\n", "", " \n", "\n\n"]
FINS_CSV = ["\n", "\r\n", "\r"]


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


def palavra():
    return "".join(SORTEIO.choice(LETRAS) for _ in range(SORTEIO.randint(3, 8)))


def linha():
    """Uma linha sorteada, de palavras, sempre com uma letra acentuada e uma do ASCII."""
    return " ".join(palavra() for _ in range(SORTEIO.randint(2, 5))) + f" {SORTEIO.choice(ACENTUADAS)}x"


def nome():
    """Um nome sorteado, de letras que o \\w casa, que nao saiu antes."""
    while True:
        sorteado = "".join(SORTEIO.choice(string.ascii_lowercase + ACENTUADAS) for _ in range(SORTEIO.randint(4, 8)))
        if sorteado not in USADOS:
            USADOS.add(sorteado)
            return sorteado


def nfd(texto):
    return unicodedata.normalize("NFD", texto)


def em_nfd(valor):
    """O valor JSON com cada texto, tambem as chaves, na forma NFD."""
    if isinstance(valor, str):
        return nfd(valor)
    if isinstance(valor, list):
        return [em_nfd(v) for v in valor]
    if isinstance(valor, dict):
        return {nfd(k): em_nfd(v) for k, v in valor.items()}
    return valor


def objeto():
    """Uma entrada da lista de objetos sem campo unico, com texto, lista e um valor que nao e texto."""
    return {OUTRO: [linha(), SORTEIO.randint(0, 9)], C1: linha(), U: SORTEIO.choice([1, True, None])}


L, N, O, T, M1, M2 = (nome() for _ in range(6))  # as listas, a tabela e os modelos, pelo nome na configuracao
K_LISTA, K_GRUPO, K_NOMES, K_OBJETOS, U, F, G, S, OUTRO = (nome() for _ in range(9))  # as chaves do JSON
C1, C2, C3, D1 = (nome() for _ in range(4))  # os campos dos modelos
K, X, Y, Z = (nome() for _ in range(4))  # as colunas da tabela; K e a chave
DADOS, MODELOS, TABELAS, MUDANCAS = (nome() for _ in range(4))  # as pastas do projeto
QUEBRAS_DOS_MODELOS = ["\n", "\r\n"]  # as dos arquivos dos modelos, que a peca le como \n


def item_sorteado(campos):
    """O texto de um item de modelo sorteado: palavras e cada campo, um deles duas vezes, em ordem sorteada, em uma
    linha ou mais, algumas com dois espacos no fim."""
    partes = [f"{{{c}}}" for c in campos + [SORTEIO.choice(campos)]] + [palavra() for _ in range(SORTEIO.randint(1, 4))]
    SORTEIO.shuffle(partes)
    return partes[0] + "".join(SORTEIO.choice([" ", ", ", "  \n", "\n> "]) + parte for parte in partes[1:])


def entres():
    """Os textos entre dois itens: vazio (uma linha em branco entre eles), uma linha e duas."""
    return ["", palavra(), f"{palavra()}\n{linha()}"]


def montado(itens, item, entre):
    """O campo montado pela regra: cada item com os campos trocados, juntos pelo texto entre ou por uma quebra."""
    textos = []
    for valores in itens:
        texto = item
        for chave, valor in valores.items():
            texto = texto.replace("{" + chave + "}", str(valor))
        textos.append(texto)
    return ("\n" if entre is None else f"\n{entre}\n").join(textos)


def item_m1():
    return {C1: palavra(), C2: SORTEIO.choice([SORTEIO.randint(1, 999), f"{SORTEIO.randint(1, 99)}-{palavra()}"]),
            C3: linha()}


def entrada_nova():
    """Uma entrada das mudancas, com as chaves numa ordem sorteada."""
    partes = [(U, linha()), (OUTRO, SORTEIO.randint(-9, 99)), (F, [item_m1() for _ in range(SORTEIO.randint(1, 3))]),
              (S, [{F: [item_m1()], OUTRO: palavra()} for _ in range(SORTEIO.randint(1, 2))]),
              (G, [{D1: palavra()} for _ in range(SORTEIO.randint(1, 2))])]
    SORTEIO.shuffle(partes)
    return dict(partes)


def esperada(entrada, modelos):
    """A entrada como deve ficar no arquivo: cada campo montado pelo modelo dele, tambem os da lista de dentro."""
    item, entre, outro = modelos["item"], modelos["entre"], modelos["outro"]
    saida = {}
    for chave, valor in entrada.items():
        if chave == F:
            saida[chave] = montado(valor, item, entre)
        elif chave == G:
            saida[chave] = montado(valor, outro, None)
        elif chave == S:
            saida[chave] = [{k: montado(v, item, entre) if k == F else v for k, v in sub.items()} for sub in valor]
        else:
            saida[chave] = valor
    return saida


def valor_csv(fim):
    """Um valor de celula sorteado, as vezes com virgula, aspas ou a quebra de linha da tabela."""
    especiais = [",", "\"", " "] + (["\n"] if "\n" in fim else [])
    return palavra() + "".join(SORTEIO.choice(especiais + [palavra()]) for _ in range(SORTEIO.randint(0, 3)))


def json_na_forma(dados, forma):
    recuo, ascii, fim = forma
    return json.dumps(dados, indent=recuo, ensure_ascii=ascii) + fim


def csv_na_forma(registros, fim):
    saida = io.StringIO(newline="")
    csv.writer(saida, lineterminator=fim).writerows(registros)
    return saida.getvalue()


def grava(caminho, texto):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(texto.encode("utf-8"))
    return caminho


def projeto(pasta, forma=None, fim_csv=None, entre=None, quebra=None):
    """Um projeto inventado na pasta, com os arquivos gravados, e o que o teste precisa saber dele; o que nao vem,
    sorteado."""
    forma = forma or (SORTEIO.choice(RECUOS), SORTEIO.choice([True, False]), SORTEIO.choice(FINS_JSON))
    fim_csv = fim_csv or SORTEIO.choice(FINS_CSV)
    p = {"pasta": pasta, "forma": forma, "fim_csv": fim_csv, "ascii_das_entradas": False,
         "conf_caminho": pasta / DADOS / "configuração.json", "lista": pasta / DADOS / "listas.json",
         "tabela": pasta / TABELAS / "tabela.csv", "mud_caminho": pasta / MUDANCAS / "mudanças.json",
         "modelos": {"item": item_sorteado([C1, C2, C3]), "entre": SORTEIO.choice(entres()) if entre is None else entre,
                     "outro": item_sorteado([D1])}}
    quebra = quebra or SORTEIO.choice(QUEBRAS_DOS_MODELOS)
    for arquivo, texto in p["modelos"].items():
        grava(pasta / DADOS / MODELOS / f"{arquivo}.md", f"{texto}\n".replace("\n", quebra))
    p["conf"] = {"versao_schema": 1,
                 "modelos": {M1: {"item": f"{MODELOS}/item.md", "entre": f"{MODELOS}/entre.md"},
                             M2: {"item": f"{MODELOS}/outro.md"}},
                 "listas": {L: {"arquivo": "listas.json", "lista": K_LISTA, "unico": U, "montados": {F: M1, G: M2}},
                            N: {"arquivo": "listas.json", "lista": f"{K_GRUPO}/{K_NOMES}"},
                            O: {"arquivo": "listas.json", "lista": f"{K_GRUPO}/{K_OBJETOS}"}},
                 "tabelas": {T: {"arquivo": f"../{TABELAS}/tabela.csv", "chave": K}}}
    existentes = [{U: linha(), F: linha(), OUTRO: SORTEIO.randint(0, 9), S: [{F: linha()}]}
                  for _ in range(SORTEIO.randint(2, 5))]
    p["dados"] = {"versao_schema": 1, OUTRO: f"á {palavra()}", K_LISTA: existentes,
                  K_GRUPO: {K_NOMES: [linha() for _ in range(SORTEIO.randint(1, 4))], OUTRO: [1, True, None],
                            K_OBJETOS: [objeto() for _ in range(SORTEIO.randint(1, 3))]}}
    grava(p["lista"], json_na_forma(p["dados"], forma))
    colunas = [K, X, Y, Z]
    SORTEIO.shuffle(colunas)
    linhas = [{K: f"{palavra()}{SORTEIO.choice(ACENTUADAS)}-{i}", **{c: valor_csv(fim_csv) for c in (X, Y, Z)}}
              for i in range(SORTEIO.randint(3, 7))]
    p["colunas"], p["linhas"] = colunas, linhas
    grava(p["tabela"], csv_na_forma([colunas] + [[l[c] for c in colunas] for l in linhas], fim_csv))
    a, b = SORTEIO.sample(range(len(linhas)), 2)
    p["mud"] = {"versao_schema": 1,
                "listas": {L: [entrada_nova() for _ in range(SORTEIO.randint(1, 3))], N: [linha(), linha()],
                           O: [objeto()]},
                "tabelas": {T: [{K: linhas[a][K], X: valor_csv(fim_csv)},
                                {Y: valor_csv(fim_csv), K: nfd(linhas[b][K]), Z: valor_csv(fim_csv)}]}}
    return p


def grava_entradas(p):
    """Grava a configuracao e as mudancas do projeto, as que estao em dados (None: o caso ja gravou o arquivo)."""
    for chave, caminho in (("conf", p["conf_caminho"]), ("mud", p["mud_caminho"])):
        if p[chave] is not None:
            grava(caminho, json.dumps(p[chave], ensure_ascii=p["ascii_das_entradas"], indent=1))


def estado(pasta):
    """{arquivo: bytes} de cada arquivo da pasta."""
    return {c: c.read_bytes() for c in sorted(pasta.rglob("*")) if c.is_file()}


def roda(p):
    r = subprocess.run([sys.executable, "-I", str(PECA / "listas_e_tabelas.py"), str(p["conf_caminho"]),
                        str(p["mud_caminho"])], capture_output=True, text=True, cwd=TRABALHO)
    return r.returncode, r.stdout + r.stderr


def esperados(p):
    """(texto da lista, texto da tabela) pela regra: as entradas no fim de cada lista e os campos trocados."""
    dados = copy.deepcopy(p["dados"])
    dados[K_LISTA] += [esperada(e, p["modelos"]) for e in p["mud"]["listas"][L]]
    dados[K_GRUPO][K_NOMES] += p["mud"]["listas"][N]
    dados[K_GRUPO][K_OBJETOS] += p["mud"]["listas"][O]
    linhas = copy.deepcopy(p["linhas"])
    por_chave = {unicodedata.normalize("NFC", l[K]): l for l in linhas}
    for troca in p["mud"]["tabelas"][T]:
        por_chave[unicodedata.normalize("NFC", troca[K])].update({c: v for c, v in troca.items() if c != K})
    tabela = csv_na_forma([p["colunas"]] + [[l[c] for c in p["colunas"]] for l in linhas], p["fim_csv"])
    return json_na_forma(dados, p["forma"]), tabela


def tem_erro(saida, *partes):
    return any(l.startswith("ERRO") and all(parte in l for parte in partes) for l in saida.split("\n"))


TRABALHO.mkdir(parents=True)

# ---- as formas: o arquivo gravado e o da forma dele, com as mudancas ----

FORMAS = [(recuo, ascii, SORTEIO.choice(FINS_JSON), FINS_CSV[k % len(FINS_CSV)])
          for k, (recuo, ascii) in enumerate((r, a) for r in RECUOS for a in (True, False))]
for numero, (recuo, ascii, fim, fim_csv) in enumerate(FORMAS):
    variantes = entres()
    entre = variantes[numero % len(variantes)]
    quebra = QUEBRAS_DOS_MODELOS[numero % len(QUEBRAS_DOS_MODELOS)]
    p = projeto(TRABALHO / "formas" / str(numero), (recuo, ascii, fim), fim_csv, entre, quebra)
    grava_entradas(p)
    entradas = {c: b for c, b in estado(p["pasta"]).items() if c not in (p["lista"], p["tabela"])}
    cod, out = roda(p)
    forma = (f"recuo {recuo!r}, escape {ascii}, fim {fim!r}, quebra do CSV {fim_csv!r}, texto entre {entre!r}, "
             f"quebra dos modelos {quebra!r}")
    lista, tabela = esperados(p)
    confere(cod == 0, f"{forma}: as mudanças certas saem com 0: {out}")
    confere(p["lista"].read_bytes() == lista.encode("utf-8"),
            f"{forma}: a lista é a do json.dumps na forma dela, com as entradas no fim de cada lista e os campos "
            f"montados")
    confere(p["tabela"].read_bytes() == tabela.encode("utf-8"),
            f"{forma}: a tabela é a do módulo csv na forma dela, com os campos trocados")
    confere(all(c.read_bytes() == b for c, b in entradas.items()), f"{forma}: os arquivos de entrada não mudam")
    depois = estado(p["pasta"])
    cod, out = roda(p)
    confere(cod == 1 and tem_erro(out) and estado(p["pasta"]) == depois,
            f"{forma}: as mesmas mudanças de novo saem com 1, sem gravar nada: {out}")

DUAS = TRABALHO / "duas"
p = projeto(DUAS / "a")
grava_entradas(p)
shutil.copytree(DUAS / "a", DUAS / "b")
roda(p)
roda({**p, "conf_caminho": DUAS / "b" / p["conf_caminho"].relative_to(DUAS / "a"),
      "mud_caminho": DUAS / "b" / p["mud_caminho"].relative_to(DUAS / "a")})
confere([b for b in estado(DUAS / "a").values()] == [b for b in estado(DUAS / "b").values()],
        "duas rodadas, em cópias do mesmo projeto, dão o mesmo")


def caso(pasta, muda, forma=None, fim_csv=None):
    """(codigo, saida, se nada foi gravado, projeto) de um projeto com a mudanca do caso."""
    p = projeto(pasta, forma, fim_csv)
    muda(p)
    grava_entradas(p)
    antes = estado(pasta)
    cod, out = roda(p)
    return cod, out, estado(pasta) == antes, p


def onde(p, caminho):
    """O comeco do ERRO de um valor das mudancas."""
    return f"{p['mud_caminho']}: {caminho}: "


# ---- os problemas: saem com 1, com o lugar, sem gravar nada ----

def entrada(p, k=0):
    return p["mud"]["listas"][L][k]


def com_duas(p):
    """As mudancas com duas entradas na lista dos objetos, ao menos."""
    if len(p["mud"]["listas"][L]) < 2:
        p["mud"]["listas"][L].append(entrada_nova())


def unico_da_lista(p):
    j = SORTEIO.randrange(len(p["dados"][K_LISTA]))
    entrada(p)[U] = nfd(p["dados"][K_LISTA][j][U])
    return [onde(p, f"/listas/{L}/0/{U}"), f"/{K_LISTA}/{j}/{U} "]


def unico_das_mudancas(p):
    com_duas(p)
    entrada(p, 1)[U] = nfd(entrada(p)[U])
    return [onde(p, f"/listas/{L}/1/{U}"), f"/listas/{L}/0/{U}"]


def sem_unico(p):
    del entrada(p)[U]
    return [onde(p, f"/listas/{L}/0")]


def entrada_que_nao_e_objeto(p):
    p["mud"]["listas"][L][0] = linha()
    return [onde(p, f"/listas/{L}/0")]


def texto_repetido(p):
    j = SORTEIO.randrange(len(p["dados"][K_GRUPO][K_NOMES]))
    p["mud"]["listas"][N][1] = nfd(p["dados"][K_GRUPO][K_NOMES][j])
    return [onde(p, f"/listas/{N}/1"), f"/{K_GRUPO}/{K_NOMES}/{j} "]


def objeto_repetido(p):
    j = SORTEIO.randrange(len(p["dados"][K_GRUPO][K_OBJETOS]))
    p["mud"]["listas"][O][0] = em_nfd(p["dados"][K_GRUPO][K_OBJETOS][j])
    return [onde(p, f"/listas/{O}/0"), f"/{K_GRUPO}/{K_OBJETOS}/{j} "]


def montado_que(valor):
    def muda(p):
        entrada(p)[F] = valor
        return [onde(p, f"/listas/{L}/0/{F}")]
    return muda


def item_sem_campo(p):
    del entrada(p)[F][0][C3]
    return [onde(p, f"/listas/{L}/0/{F}/0/{C3}")]


def item_com_campo_a_mais(p):
    a_mais = nome()
    entrada(p)[F][-1][a_mais] = palavra()
    return [onde(p, f"/listas/{L}/0/{F}/{len(entrada(p)[F]) - 1}/{a_mais}")]


def item_com_valor(valor):
    def muda(p):
        entrada(p)[F][0][C2] = valor
        return [onde(p, f"/listas/{L}/0/{F}/0/{C2}")]
    return muda


def montado_de_dentro(p):
    entrada(p)[S] = [{OUTRO: palavra()}, {F: linha()}]
    return [onde(p, f"/listas/{L}/0/{S}/1/{F}")]


def montado_sem_entre(p):
    entrada(p)[G] = [{D1: palavra()}, {D1: palavra(), C1: palavra()}]
    return [onde(p, f"/listas/{L}/0/{G}/1/{C1}")]


def troca(p, k=0):
    return p["mud"]["tabelas"][T][k]


def troca_sem_chave(p):
    p["mud"]["tabelas"][T][0] = {X: valor_csv(p["fim_csv"]), Y: valor_csv(p["fim_csv"])}
    return [onde(p, f"/tabelas/{T}/0")]


def chave_de_nenhuma(p):
    troca(p)[K] = palavra()
    return [onde(p, f"/tabelas/{T}/0/{K}")]


def chave_de_duas(p):
    i, j = SORTEIO.sample(range(len(p["linhas"])), 2)
    p["linhas"][j][K] = p["linhas"][i][K]
    grava(p["tabela"], csv_na_forma([p["colunas"]] + [[l[c] for c in p["colunas"]] for l in p["linhas"]],
                                    p["fim_csv"]))
    troca(p)[K] = p["linhas"][i][K]
    return [onde(p, f"/tabelas/{T}/0/{K}")]


def coluna_que_nao_ha(p):
    coluna = nome()
    troca(p)[coluna] = palavra()
    return [onde(p, f"/tabelas/{T}/0/{coluna}")]


def troca_que_nao_muda(p):
    linha_da_troca = next(l for l in p["linhas"] if l[K] == troca(p)[K])
    troca(p)[X] = linha_da_troca[X]
    return [onde(p, f"/tabelas/{T}/0/{X}")]


def troca_de_novo(p):
    trocas = p["mud"]["tabelas"][T]
    trocas.append({K: nfd(trocas[0][K]), X: palavra()})
    return [onde(p, f"/tabelas/{T}/{len(trocas) - 1}/{X}"), f"/tabelas/{T}/0/{X}"]


PROBLEMAS = {
    "o valor único de uma entrada da lista, em outra forma Unicode": unico_da_lista,
    "o valor único de outra entrada das mudanças": unico_das_mudancas,
    "a entrada sem o campo único": sem_unico,
    "a entrada que não é objeto, numa lista com campo único": entrada_que_nao_e_objeto,
    "o texto repetido numa lista sem campo único, em outra forma Unicode": texto_repetido,
    "o objeto repetido numa lista sem campo único, com as chaves e os textos em outra forma Unicode": objeto_repetido,
    "o campo montado que é texto": montado_que(linha()),
    "o campo montado vazio": montado_que([]),
    "o campo montado com um item que não é objeto": montado_que([item_m1(), palavra()]),
    "o item sem um campo do modelo": item_sem_campo,
    "o item com um campo que o modelo não usa": item_com_campo_a_mais,
    "o item com um campo booleano": item_com_valor(True),
    "o item com um campo nulo": item_com_valor(None),
    "o item com um número com ponto": item_com_valor(1.5),
    "o item com uma lista num campo": item_com_valor([palavra()]),
    "o campo montado de dentro de uma lista da entrada": montado_de_dentro,
    "o item de um modelo sem texto entre": montado_sem_entre,
    "a troca sem a chave": troca_sem_chave,
    "a chave que nenhuma linha tem": chave_de_nenhuma,
    "a chave que duas linhas têm": chave_de_duas,
    "a coluna que a tabela não tem": coluna_que_nao_ha,
    "a troca que não muda nada": troca_que_nao_muda,
    "a troca de novo da mesma coluna da mesma linha, pela chave em outra forma Unicode": troca_de_novo,
}
for numero, (descricao, muda) in enumerate(PROBLEMAS.items()):
    partes = []
    cod, out, nada, _ = caso(TRABALHO / "problemas" / str(numero), lambda p: partes.extend(muda(p)))
    confere(cod == 1 and tem_erro(out, *partes) and nada,
            f"{descricao}: sai com 1, com o lugar no ERRO ({partes}), sem gravar nada: {out}")


def com_maiusculas(p):
    j = SORTEIO.randrange(len(p["dados"][K_LISTA]))
    entrada(p)[U] = p["dados"][K_LISTA][j][U].swapcase()


def o_um_e_o_verdadeiro(p):
    p["dados"][K_GRUPO][K_OBJETOS][0][U] = 1
    grava(p["lista"], json_na_forma(p["dados"], p["forma"]))
    p["mud"]["listas"][O][0] = {**copy.deepcopy(p["dados"][K_GRUPO][K_OBJETOS][0]), U: True}


PASSAM = {"o valor único de uma entrada da lista com outras maiúsculas": com_maiusculas,
          "o objeto que só difere de um da lista no 1 e no verdadeiro": o_um_e_o_verdadeiro}
for numero, (descricao, muda) in enumerate(PASSAM.items()):
    cod, out, _, p = caso(TRABALHO / "passam" / str(numero), muda)
    lista, _ = esperados(p)
    confere(cod == 0 and p["lista"].read_bytes() == lista.encode("utf-8"), f"{descricao}: não é problema: {out}")

SO_ASCII = TRABALHO / "so-ascii"  # um arquivo cujos dados nao tem nada fora do ASCII: a forma nao diz o escape
CHAVE_ASCII = "".join(SORTEIO.choice(string.ascii_lowercase) for _ in range(SORTEIO.randint(3, 8)))
DADOS_ASCII = {CHAVE_ASCII: ["".join(SORTEIO.choice(string.ascii_letters) for _ in range(8)) for _ in range(3)]}
FORMA_ASCII = (SORTEIO.choice([1, 2, 4, "\t"]), False, SORTEIO.choice(FINS_JSON))
NOVAS_ASCII = [linha(), linha()]
grava(SO_ASCII / "lista.json", json_na_forma(DADOS_ASCII, FORMA_ASCII))
cod, out = roda({"conf_caminho": grava(SO_ASCII / "conf.json", json.dumps(
    {"versao_schema": 1, "listas": {L: {"arquivo": "lista.json", "lista": CHAVE_ASCII}}}, ensure_ascii=False)),
                 "mud_caminho": grava(SO_ASCII / "mud.json", json.dumps(
                     {"versao_schema": 1, "listas": {L: NOVAS_ASCII}}, ensure_ascii=False))})
confere(cod == 0 and (SO_ASCII / "lista.json").read_bytes() == json_na_forma(
    {CHAVE_ASCII: DADOS_ASCII[CHAVE_ASCII] + NOVAS_ASCII}, FORMA_ASCII).encode("utf-8"),
        f"o arquivo só com ASCII, sem nada de fora dele nos dados: as entradas novas vão como são, sem escape: {out}")


def lista_fora_da_forma(muda_texto):
    """O caso da lista gravada noutra forma: muda_texto(texto) da (texto novo, linha em que ele deixa de voltar)."""
    def muda(p):
        texto, n = muda_texto(p["lista"].read_bytes().decode("utf-8"), p)
        grava(p["lista"], texto)
        return [f"{p['lista']}:{n}: "]
    return muda


def espaco_no_fim_de_uma_linha(texto, p):
    linhas = texto.split("\n")
    n = SORTEIO.randrange(1, len(linhas) - 2)  # nem a primeira, nem a do fecho, cujo espaco iria com o fim do arquivo
    linhas[n] += " "
    return "\n".join(linhas), n + 1


def quebras_do_windows(texto, p):
    return texto.replace("\n", "\r\n"), 1


def separadores_sem_espaco(texto, p):
    return json.dumps(p["dados"], ensure_ascii=p["forma"][1], separators=(",", ":")) + p["forma"][2], 1


def chave_repetida(texto, p):
    return "{" + json.dumps(OUTRO) + ": 0, " + texto[1:], 1


def escape_em_maiusculas(texto, p):
    return texto.replace("\\u00e1", "\\u00E1"), 1


def tabela_fora_da_forma(muda_texto):
    def muda(p):
        texto, n = muda_texto(p["tabela"].read_bytes().decode("utf-8"), p)
        grava(p["tabela"], texto)
        return [f"{p['tabela']}:{n}"]
    return muda


def aspas_onde_nao_precisa(texto, p):
    return texto.replace(K, f"\"{K}\"", 1), 1


def sem_a_quebra_do_fim(texto, p):
    return texto[:-len(p["fim_csv"])], ""


def quebras_misturadas(texto, p):
    outra = next(f for f in FINS_CSV if f != p["fim_csv"] and not p["fim_csv"].startswith(f))
    return texto.replace(p["fim_csv"], outra, 1), 1


FORA_DA_FORMA = {  # (descricao, mudanca, forma do JSON, quebra do CSV)
    "a lista com um espaço no fim de uma linha": (lista_fora_da_forma(espaco_no_fim_de_uma_linha),
                                                  (SORTEIO.choice([1, 2, 4, "\t"]), False, "\n"), None),
    "a lista com as quebras \\r\\n": (lista_fora_da_forma(quebras_do_windows), (2, True, "\n"), None),
    "a lista com os separadores sem espaço": (lista_fora_da_forma(separadores_sem_espaco), (None, False, ""), None),
    "a lista com uma chave repetida": (lista_fora_da_forma(chave_repetida), (None, True, "\n"), None),
    "a lista com o escape em maiúsculas": (lista_fora_da_forma(escape_em_maiusculas), (None, True, "\n"), None),
    "a tabela com aspas onde não precisa": (tabela_fora_da_forma(aspas_onde_nao_precisa), None, None),
    "a tabela sem a quebra do fim": (tabela_fora_da_forma(sem_a_quebra_do_fim), None, None),
    "a tabela com as quebras misturadas": (tabela_fora_da_forma(quebras_misturadas), None, None),
}
for numero, (descricao, (muda, forma, fim_csv)) in enumerate(FORA_DA_FORMA.items()):
    partes = []
    cod, out, nada, _ = caso(TRABALHO / "fora-da-forma" / str(numero), lambda p: partes.extend(muda(p)), forma, fim_csv)
    confere(cod == 1 and tem_erro(out, *partes) and nada,
            f"{descricao}: não volta igual, sai com 1, com o arquivo e a linha no ERRO ({partes}), sem gravar nada: "
            f"{out}")

# ---- as entradas que nao servem: saem com 2, sem gravar nada ----


def na_conf(muda_conf):
    def muda(p):
        muda_conf(p["conf"])
    return muda


def nas_mudancas(muda_mud):
    def muda(p):
        muda_mud(p["mud"])
    return muda


def grava_texto(chave_do_caminho, texto=None, binario=None):
    """O caso que grava o arquivo dado por cima (texto ou bytes), ou o apaga (os dois None)."""
    def muda(p):
        caminho = p[chave_do_caminho]
        if chave_do_caminho in ("conf_caminho", "mud_caminho"):
            p["conf" if chave_do_caminho == "conf_caminho" else "mud"] = None
        caminho.parent.mkdir(parents=True, exist_ok=True)
        if binario is not None:
            caminho.write_bytes(binario)
        elif texto is not None:
            caminho.write_text(texto, encoding="utf-8")
        else:
            caminho.unlink(missing_ok=True)  # a configuracao e as mudancas so se gravariam depois do caso
    return muda


def modelo(nome_do_arquivo, binario):
    def muda(p):
        (p["pasta"] / DADOS / MODELOS / nome_do_arquivo).write_bytes(binario)
    return muda


def tabela_com(registros):
    def muda(p):
        grava(p["tabela"], csv_na_forma(registros(p), p["fim_csv"]))
    return muda


def com_valor_que_nao_se_escreve(p):
    p["ascii_das_entradas"] = True
    troca(p)[X] = palavra() + chr(0xD800)


def tabela_num_modelo(p):
    """A tabela no arquivo do texto entre, gravado como um CSV que serve: so a regra das entradas o barra."""
    chave = palavra()
    grava(p["pasta"] / DADOS / MODELOS / "entre.md", f"{K},{X}\n{chave},{palavra()}\n")
    p["conf"]["tabelas"][T]["arquivo"] = f"{MODELOS}/entre.md"
    p["mud"]["tabelas"][T] = [{K: chave, X: palavra()}]


def sem_o_grupo(grupo, sem_montados=False):
    """O caso com o grupo vazio na configuracao e sem ele nas mudancas (os modelos: sem os campos montados)."""
    def muda(p):
        p["conf"][grupo] = {}
        if sem_montados:
            p["conf"]["listas"][L].pop("montados")
        else:
            p["mud"].pop(grupo)
    return muda


LATIN = f"{{\"versao_schema\": 1, \"{palavra()}\": \"ç\"}}".encode("latin-1", "replace")
NAO_SERVEM = {
    "a configuração que não é JSON": grava_texto("conf_caminho", "{" + linha()),
    "a configuração que não se lê em UTF-8": grava_texto("conf_caminho", binario=LATIN),
    "a configuração que falta": grava_texto("conf_caminho"),
    "a configuração com um campo que o molde não conhece": na_conf(lambda c: c.update({nome(): 1})),
    "a configuração de outra versão": na_conf(lambda c: c.update(versao_schema=2)),
    "a lista sem o arquivo": na_conf(lambda c: c["listas"][L].pop("arquivo")),
    "a lista sem o caminho": na_conf(lambda c: c["listas"][N].pop("lista")),
    "a tabela sem a chave": na_conf(lambda c: c["tabelas"][T].pop("chave")),
    "o campo único com quebra de linha": na_conf(lambda c: c["listas"][L].update(unico=f"{U}\n")),
    "os campos montados vazios": na_conf(lambda c: c["listas"][L].update(montados={})),
    "o modelo sem o item": na_conf(lambda c: c["modelos"][M2].pop("item")),
    "os modelos da configuração vazios": sem_o_grupo("modelos", sem_montados=True),
    "as listas da configuração vazias": sem_o_grupo("listas"),
    "as tabelas da configuração vazias": sem_o_grupo("tabelas"),
    "a lista com um campo montado por um modelo que não há": na_conf(lambda c: c["listas"][L]["montados"].update(
        {F: nome()})),
    "o mesmo arquivo de lista e de tabela": na_conf(lambda c: c["tabelas"][T].update(arquivo="listas.json")),
    "o item do modelo que falta": na_conf(lambda c: c["modelos"][M1].update(item=f"{MODELOS}/{nome()}.md")),
    "o texto entre que falta": na_conf(lambda c: c["modelos"][M1].update(entre=f"{MODELOS}/{nome()}.md")),
    "o item do modelo sem texto": modelo("outro.md", b" \n\n"),
    "o item do modelo que não se lê em UTF-8": modelo("item.md", "{x} ç".encode("latin-1")),
    "as mudanças que não são JSON": grava_texto("mud_caminho", "[" + linha()),
    "as mudanças que faltam": grava_texto("mud_caminho"),
    "as mudanças sem lista nem tabela": nas_mudancas(lambda m: [m.pop("listas"), m.pop("tabelas")]),
    "as mudanças com as listas sem nenhuma": nas_mudancas(lambda m: m.update(listas={})),
    "as mudanças com as tabelas sem nenhuma": nas_mudancas(lambda m: m.update(tabelas={})),
    "as mudanças com uma lista sem entrada": nas_mudancas(lambda m: m["listas"].update({N: []})),
    "as mudanças com uma tabela sem troca": nas_mudancas(lambda m: m["tabelas"].update({T: []})),
    "as mudanças de outra versão": nas_mudancas(lambda m: m.update(versao_schema=2)),
    "a troca com um valor que não é texto": nas_mudancas(lambda m: m["tabelas"][T][0].update({X: 1})),
    "a troca só com uma coluna": nas_mudancas(lambda m: m["tabelas"][T].append({K: palavra()})),
    "as mudanças com um campo que o molde não conhece": nas_mudancas(lambda m: m.update({nome(): []})),
    "a lista que a configuração não tem": nas_mudancas(lambda m: m["listas"].update({nome(): [1]})),
    "a tabela que a configuração não tem": nas_mudancas(lambda m: m["tabelas"].update({nome(): [{K: "a", X: "b"}]})),
    "a lista que falta": grava_texto("lista"),
    "a lista que não é JSON": grava_texto("lista", "{" + linha()),
    "a lista que não se lê em UTF-8": grava_texto("lista", binario=LATIN),
    "o caminho da lista que não leva a nada": na_conf(lambda c: c["listas"][L].update(lista=nome())),
    "o caminho da lista que leva a um objeto": na_conf(lambda c: c["listas"][N].update(lista=K_GRUPO)),
    "o caminho da lista que passa por uma lista": na_conf(lambda c: c["listas"][L].update(lista=f"{K_LISTA}/0")),
    "a tabela que falta": grava_texto("tabela"),
    "a tabela que não se lê em UTF-8": grava_texto("tabela", binario=f"{K},{X}\nç,a\n".encode("latin-1")),
    "a tabela que não se lê como CSV": tabela_com(lambda p: [p["colunas"], ["x" * (csv.field_size_limit() + 1)] * 4]),
    "a tabela sem cabeçalho": grava_texto("tabela", ""),
    "a tabela com uma coluna repetida": tabela_com(lambda p: [p["colunas"] + [X]] + [[palavra()] * 5
                                                                                   for _ in p["linhas"]]),
    "a tabela com uma linha de outro tamanho": tabela_com(lambda p: [p["colunas"]] + [[l[c] for c in p["colunas"]]
                                                                                     for l in p["linhas"]] + [[K]]),
    "a tabela sem a coluna da chave": na_conf(lambda c: c["tabelas"][T].update(chave=nome())),
    "a lista que é a configuração": na_conf(lambda c: c["listas"][L].update(arquivo="configuração.json")),
    "a tabela que é o arquivo das mudanças": na_conf(lambda c: c["tabelas"][T].update(
        arquivo=f"../{MUDANCAS}/mudanças.json")),
    "a lista que é a lista do arquivo das mudanças": na_conf(lambda c: c["listas"][N].update(
        arquivo=f"../{MUDANCAS}/mudanças.json", lista=f"listas/{N}")),
    "a tabela que é o arquivo de um modelo": tabela_num_modelo,
    "a lista que é uma pasta": na_conf(lambda c: c["listas"][L].update(arquivo=MODELOS)),
    "o valor que não se escreve em UTF-8": com_valor_que_nao_se_escreve,
}
for numero, (descricao, muda) in enumerate(NAO_SERVEM.items()):
    cod, out, nada, _ = caso(TRABALHO / "nao-servem" / str(numero), muda)
    confere(cod == 2 and out.startswith("ERRO") and nada, f"{descricao}: sai com 2, sem gravar nada: {out}")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
