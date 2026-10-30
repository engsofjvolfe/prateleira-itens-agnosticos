"""
Testes da peca das marcas (marcas.py). Tudo e inventado e sorteado aqui, com semente fixa (o
sorteio e o mesmo em toda rodada; outra semente vem com --semente): os niveis, com acento;
as unidades e as regioes de cada uma, numa ordem que se escreve, com niveis pulados,
regioes que nao recebem codigos, regioes do meio do caminho no esperado e fora dele, e
regioes irmas; os codigos de cada regiao, um deles esperado em duas, e os que valem em
qualquer regiao; e o texto certo, em arquivos, com comentarios que nao sao marca,
comentarios vazios, marcas no meio da linha, duas na mesma linha, marca em tres linhas,
marcas em NFD e com outros espacos, e numeros de linha com buracos (os das linhas de codigo,
que o programa que usa a peca tira). Uma unidade tem sempre todos esses casos.

Conferem regras, nunca uma frase pronta:
  - as marcas saem na ordem, com o arquivo, o numero dado, o nivel e o codigo em NFC;
    comentario que nao comeca por um nivel nao e marca; um comentario vai ate o primeiro
    fim; o que nao fecha sai sem nivel, e nada depois dele sai;
  - o caminho de cada marca e o do lugar dela: abrir um nivel fecha os de dentro, e cada
    arquivo comeca sem nada aberto;
  - o texto certo nao da aviso;
  - cada estrago do texto da exatamente os avisos do caso dele, cada um com o caso, o
    arquivo, a linha, a unidade e o codigo; FALTA so no caso da falta; o texto do aviso diz
    o codigo e, quando ha, o lugar de antes; todos os casos aparecem;
  - varios estragos juntos saem em ordem de arquivo e linha; duas rodadas, e o esperado e os
    codigos que existem em outra ordem, dao os mesmos avisos;
  - com um nivel so, a unidade e a regiao;
  - niveis e esperado que nao servem dao ErroDeMarcas, que diz o que esta errado.
Uso:
    python3 -I teste_marcas.py <pasta da peca> <pasta de trabalho nova> [--semente N]
Grava na pasta de trabalho, para mostrar o que falhou, as linhas de cada arquivo inventado,
com o numero de cada uma, como a peca as recebe.
"""
import argparse
import collections
import random
import string
import sys
import unicodedata
from pathlib import Path


def argumentos():
    p = argparse.ArgumentParser(description="Testes da peça das marcas.")
    p.add_argument("peca", type=Path, help="a pasta da peça")
    p.add_argument("trabalho", type=Path, help="uma pasta de trabalho nova")
    p.add_argument("--semente", type=int, default=1, help="a semente do sorteio")
    return p.parse_args()


ARGS = argumentos()
PECA, TRABALHO = ARGS.peca.resolve(), ARGS.trabalho.resolve()
SORTEIO = random.Random(ARGS.semente)
sys.path.insert(0, str(PECA))
import marcas  # noqa: E402

FALHAS = []
CASOS_VISTOS = set()
ABRE, FECHA = "<!--", "-->"  # o comeco e o fim de um comentario HTML, como o Markdown os escreve
LETRAS = string.ascii_lowercase
ACENTOS = "áâãçéêíóôõú"
JUNTAS = ["/", "-", ".", ":", "§", "_", "#"]  # o que separa os pedacos de um codigo
FORMAS = ["simples", "espacos", "nfd"]  # os jeitos de escrever uma marca, que dao a mesma marca
FORMATOS = ["so", "duas", "no-meio"]  # as marcas de dentro numa linha: sozinha, duas, no meio da prosa
VAZIOS = ["<!-->", "<!--->", "<!---->"]  # comentarios vazios
USADAS = set()

Peca = collections.namedtuple("Peca", "nivel codigo forma caminho")  # uma marca escrita numa linha, e o caminho dela


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
        print(f"FALHA: {descricao}")
    return condicao


def nfc(texto):
    return unicodedata.normalize("NFC", texto)


def nfd(texto):
    return unicodedata.normalize("NFD", texto)


def comentario_de(*partes):
    """Um comentario HTML com as palavras dadas: uma marca, quando sao um nivel e um codigo."""
    return f"{ABRE} {' '.join(partes)} {FECHA}"


def qualquer_nivel(niveis):
    return SORTEIO.choice(list(niveis.abrem) + [niveis.dentro])


# ---------- o sorteio ----------

def palavra(acento=False):
    """Uma palavra que nao saiu antes, com acento quando pedido."""
    while True:
        letras = [SORTEIO.choice(LETRAS) for _ in range(SORTEIO.randint(3, 8))]
        if acento:
            letras.insert(SORTEIO.randint(0, len(letras)), SORTEIO.choice(ACENTOS))
        nova = "".join(letras)
        if nova not in USADAS:
            USADAS.add(nova)
            return nova


def palavras(minimo=2, maximo=6):
    return " ".join(palavra(SORTEIO.random() < 0.2) for _ in range(SORTEIO.randint(minimo, maximo)))


def codigo():
    """Um codigo que nao saiu antes: uma palavra e, as vezes, outros pedacos, entre sinais."""
    texto = palavra(SORTEIO.random() < 0.3)
    for _ in range(SORTEIO.randint(0, 2)):
        texto += SORTEIO.choice(JUNTAS) + SORTEIO.choice([palavra(), str(SORTEIO.randint(0, 999))])
    return texto


def comentario(niveis, tipo=None):
    """Um comentario que nao e marca: de prosa, de uma palavra seguida de um nivel e um
    codigo, ou vazio (o dado, ou um sorteado)."""
    tipo = tipo or SORTEIO.choice(["prosa", "com-nivel", "vazio"])
    if tipo == "prosa":
        return comentario_de(palavras())
    if tipo == "com-nivel":
        return comentario_de(palavra(), qualquer_nivel(niveis), codigo())
    return tipo if tipo in VAZIOS else SORTEIO.choice(VAZIOS)


def escrita(peca):
    """O texto de uma peca da linha: a prosa como esta, ou a marca na forma dela."""
    if isinstance(peca, str):
        return peca
    if peca.forma == "multilinha":
        return ABRE
    if peca.forma == "espacos":
        return f"{ABRE}\t{peca.nivel}   {peca.codigo}  {FECHA}"
    texto = comentario_de(peca.nivel, peca.codigo)
    return nfd(texto) if peca.forma == "nfd" else texto


def texto(entrada):
    return " ".join(map(escrita, entrada["pecas"]))


def nova(pecas, papel, caminho):
    """Uma linha: as pecas dela, o papel (para os estragos), o caminho no fim dela e o numero."""
    return {"pecas": list(pecas), "papel": papel, "caminho": caminho, "numero": None}


def cortes(caminho):
    """Os caminhos que um texto abre ate chegar a este, de fora para dentro, com ele."""
    return [tuple(caminho[:k + 1]) + (None,) * (len(caminho) - k - 1) for k, c in enumerate(caminho) if c is not None]


def mais_funda(caminho):
    return max(k for k, c in enumerate(caminho) if c is not None)


def caminho_da_unidade(unidade, n):
    """O caminho da unidade aberta, com os n niveis que abrem regiao."""
    return (unidade,) + (None,) * (n - 1)


def sorteia_caminhos(unidade, n):
    """Os caminhos das regioes de uma unidade, numa ordem que se escreve: debaixo de cada
    comeco, as vezes as que pulam o nivel seguinte, primeiro, e depois as de cada codigo
    dele; as folhas sempre, as do meio as vezes."""
    def sob(prefixo):
        k = len(prefixo)
        if k == n:
            return []
        saida = sob(prefixo + [None]) if k < n - 1 and SORTEIO.random() < 0.4 else []
        for c in [codigo() for _ in range(SORTEIO.randint(1, 3 if k == n - 1 else 2))]:
            if k == n - 1 or SORTEIO.random() < 0.3:
                saida.append(tuple(prefixo + [c] + [None] * (n - k - 1)))
            saida += sob(prefixo + [c])
        return saida
    return sob([unidade])


def sorteia_unidade(n, vitrine):
    """Uma unidade: o codigo, as regioes do esperado e os codigos que valem em qualquer
    regiao. A vitrine tem todos os casos de regiao, nesta ordem: uma que pula os niveis do
    meio e nao recebe codigos; uma do meio do caminho; duas folhas irmas seguidas, a segunda
    com um codigo da primeira; e uma folha debaixo de um nivel do meio que nao esta no
    esperado. Ela tem tambem o jeito de escrever de algumas linhas."""
    unidade = codigo()
    u = {"unidade": unidade, "formatos": {}, "vitrine": {}}
    if vitrine:
        meio = [[codigo() for _ in range(n - 3)] for _ in range(2)]
        itens = [codigo(), codigo()]
        pula = (unidade,) + (None,) * (n - 2) + (codigo(),)
        do_meio = (unidade, itens[0]) + (None,) * (n - 2)
        irmas = [(unidade, itens[0], *meio[0], codigo()) for _ in range(2)]
        u["vitrine"] = {"pula": pula, "do_meio": do_meio, "irma1": irmas[0], "irma2": irmas[1],
                        "debaixo": (unidade, itens[1], *meio[1], codigo())}
        caminhos = list(u["vitrine"].values())
        u["formatos"] = {do_meio: {"vezes": 1, "ocorrencias": ["duas"], "formas": ["nfd", "espacos"]},
                         irmas[0]: {"ocorrencias": ["no-meio"]}, irmas[1]: {"abre_no_meio": True},
                         pula: {"comentarios": ["com-nivel", *VAZIOS, "prosa"]}}
        quantos = {pula: 0, do_meio: 2}
    else:
        caminhos = sorteia_caminhos(unidade, n)
        if SORTEIO.random() < 0.4:
            caminhos.insert(0, caminho_da_unidade(unidade, n))
        quantos = {}
    regioes = []
    for c in caminhos:
        recebe = quantos.get(c) != 0 if vitrine else SORTEIO.random() < 0.8
        k = quantos.get(c, SORTEIO.randint(1, 3)) if vitrine else SORTEIO.randint(0, 3) if recebe else 0
        regioes.append(marcas.Regiao(c, [codigo() for _ in range(k)], recebe))
    if vitrine:
        k1, k2 = caminhos.index(u["vitrine"]["irma1"]), caminhos.index(u["vitrine"]["irma2"])
        regioes[k2] = regioes[k2]._replace(codigos=regioes[k2].codigos + [regioes[k1].codigos[0]])
    receptoras = any(r.recebe for r in regioes)
    u["regioes"] = regioes
    u["livres"] = [codigo() for _ in range(2 if vitrine else SORTEIO.randint(0, 2) if receptoras else 0)]
    return u


def linhas_das_ocorrencias(codigos, niveis, caminho, formato, multilinha):
    """As linhas das marcas dos codigos, na ordem: sozinha, duas na mesma linha ou no meio da
    prosa (os primeiros formatos e formas sao os do formato da regiao; os outros, sorteados);
    a do codigo multilinha, na primeira vez, em tres linhas."""
    formatos, formas = list(formato.get("ocorrencias", ())), list(formato.get("formas", ()))
    linhas, i = [], 0

    def peca(c):
        return Peca(niveis.dentro, c, formas.pop(0) if formas else SORTEIO.choice(FORMAS), caminho)

    while i < len(codigos):
        if codigos[i] == multilinha:
            multilinha = None
            linhas += [nova([Peca(niveis.dentro, codigos[i], "multilinha", caminho)], "multilinha", caminho),
                       nova([f"{niveis.dentro} {codigos[i]}"], "multilinha", caminho),
                       nova([FECHA], "multilinha", caminho)]
            i += 1
            continue
        jeito = formatos.pop(0) if formatos else SORTEIO.choices(FORMATOS, [6, 2, 2])[0]
        if jeito == "duas" and i + 1 < len(codigos) and codigos[i + 1] != multilinha:
            pecas, i = [peca(codigos[i]), peca(codigos[i + 1])], i + 2
        elif jeito == "no-meio":
            pecas, i = [palavras(1, 3), peca(codigos[i]), palavras(1, 3)], i + 1
        else:
            pecas, i = [peca(codigos[i])], i + 1
        linhas.append(nova(pecas, "dentro", caminho))
    return linhas


def escreve_unidade(u, niveis, multilinha):
    """As linhas da unidade: a marca dela e um titulo; depois, cada regiao do esperado, aberta
    pelas marcas que faltam para chegar a ela (com um titulo depois de cada nivel do meio),
    com prosa, as marcas dos codigos dela e dos que valem em qualquer regiao postos nela, as
    vezes um comentario, e uma linha de prosa no fim. Guarda em u a linha que abre cada
    regiao e a ultima de cada uma."""
    n, unidade = len(niveis.abrem), u["unidade"]
    abertos = list(caminho_da_unidade(unidade, n))
    linhas = [nova([Peca(niveis.abrem[0], unidade, SORTEIO.choice(FORMAS), tuple(abertos))], "unidade", tuple(abertos)),
              nova([palavras()], "prosa", tuple(abertos))]
    u["abertas"], u["fins"] = {tuple(abertos): linhas[0]}, {}
    receptoras = [tuple(r.caminho) for r in u["regioes"] if r.recebe]
    onde_livre = {c: SORTEIO.sample(receptoras, min(len(receptoras), SORTEIO.randint(1, 2))) for c in u["livres"]}
    for regiao in u["regioes"]:
        caminho = tuple(regiao.caminho)
        formato = u["formatos"].get(caminho, {})
        for k in range(1, n):
            if caminho[k] == abertos[k]:
                continue
            abertos[k:] = [caminho[k]] + [None] * (n - k - 1)
            aberto = tuple(abertos)
            peca = Peca(niveis.abrem[k], caminho[k], SORTEIO.choice(FORMAS), aberto)
            no_meio = aberto == caminho and formato.get("abre_no_meio", SORTEIO.random() < 0.2)
            linhas.append(nova([palavras(1, 2), peca, palavras(1, 2)] if no_meio else [peca], "abre", aberto))
            u["abertas"][aberto] = linhas[-1]
            if aberto != caminho:
                linhas.append(nova([palavras()], "prosa", aberto))
        linhas.append(nova([palavras()], "prosa", caminho))
        codigos = [c for c in regiao.codigos for _ in range(formato.get("vezes") or SORTEIO.randint(1, 2))]
        codigos += [c for c, lugares in onde_livre.items() if caminho in lugares]
        SORTEIO.shuffle(codigos)
        linhas += linhas_das_ocorrencias(codigos, niveis, caminho, formato,
                                         multilinha[1] if multilinha and multilinha[0] == caminho else None)
        tipos = formato.get("comentarios", [None] if SORTEIO.random() < 0.3 else [])
        linhas += [nova([comentario(niveis, t)], "comentario", caminho) for t in tipos]
        linhas.append(nova([palavras()], "fim-da-regiao", caminho))
        u["fins"][caminho] = linhas[-1]
    return linhas


def sorteia_mundo():
    """Os niveis, as unidades (a vitrine, no primeiro arquivo, e outras), o texto de cada
    uma, em dois ou tres arquivos que comecam e acabam com prosa e cujos nomes vem na ordem
    contraria a de leitura, os numeros das linhas, com buracos, o esperado, os codigos que
    existem (os das unidades e outros) e, na ordem, as marcas e os caminhos que a leitura
    tem de dar."""
    n = SORTEIO.randint(3, 4)
    niveis = marcas.Niveis([palavra(SORTEIO.random() < 0.5) for _ in range(n)], palavra(True))
    unidades = [sorteia_unidade(n, True)] + [sorteia_unidade(n, False) for _ in range(SORTEIO.randint(2, 3))]
    u_multi, caminho_multi, codigo_multi = SORTEIO.choice([(u, tuple(r.caminho), r.codigos[0]) for u in unidades
                                                           for r in u["regioes"] if r.codigos])
    blocos = [escreve_unidade(u, niveis, (caminho_multi, codigo_multi) if u is u_multi else None) for u in unidades]
    ordem = [0] + SORTEIO.sample(range(1, len(unidades)), len(unidades) - 1)
    divisoes = sorted(SORTEIO.sample(range(1, len(unidades)), SORTEIO.randint(1, 2)))
    nomes = sorted((f"{palavra()}.md" for _ in divisoes + [None]), reverse=True)
    arquivos = {}
    for nome, a, b in zip(nomes, [0] + divisoes, divisoes + [len(unidades)]):
        entradas = [nova([palavras()], "titulo", (None,) * n)]
        for j in ordem[a:b]:
            entradas += blocos[j]
        entradas.append(nova([palavras()], "fim", entradas[-1]["caminho"]))
        numero = 0
        for e in entradas:
            numero += 1 if SORTEIO.random() < 0.85 else SORTEIO.randint(2, 5)
            e["numero"] = numero
        arquivos[nome] = entradas
    codigos = [c for u in unidades for r in u["regioes"] for c in r.codigos]
    codigos += [c for u in unidades for c in u["livres"]]
    m = {"niveis": niveis, "unidades": unidades, "arquivos": arquivos,
         "esperados": {u["unidade"]: marcas.Esperado(u["regioes"], u["livres"]) for u in unidades},
         "regioes": {tuple(r.caminho): r for u in unidades for r in u["regioes"]},
         "existem": list(dict.fromkeys(codigos)) + [codigo() for _ in range(SORTEIO.randint(2, 4))],
         "posicao": {id(e): (nome, i) for nome, entradas in arquivos.items() for i, e in enumerate(entradas)},
         "marcas": [], "caminhos": []}
    for nome, entradas in arquivos.items():
        for e in entradas:
            for p in e["pecas"]:
                if isinstance(p, Peca):
                    m["marcas"].append((nome, e["numero"], nfc(p.nivel), nfc(p.codigo)))
                    m["caminhos"].append(p.caminho)
    return m


def grava(m):
    """As linhas de cada arquivo inventado, com o numero de cada uma, na pasta de trabalho."""
    for nome, entradas in m["arquivos"].items():
        (TRABALHO / f"{nome}.txt").write_text("".join(f"{e['numero']}\t{texto(e)}\n" for e in entradas),
                                              encoding="utf-8")


# ---------- os testes ----------

def le(linhas, niveis):
    """As marcas de todos os arquivos, lidas como o programa que usa a peca as le, na ordem dos arquivos."""
    lidas = []
    for nome, entradas in linhas.items():
        lidas += marcas.marcas_das_linhas([(e["numero"], texto(e)) for e in entradas], nome, niveis)
    return lidas


def avisos_de(linhas, m, esperados=None, existem=None):
    return marcas.confere(le(linhas, m["niveis"]), m["niveis"], m["esperados"] if esperados is None else esperados,
                          m["existem"] if existem is None else existem)


def copia(m):
    return {nome: [dict(e, pecas=list(e["pecas"])) for e in entradas] for nome, entradas in m["arquivos"].items()}


def teste_leitura(m):
    lidas = le(copia(m), m["niveis"])
    confere([(x.arquivo, x.linha, x.nivel, x.codigo) for x in lidas] == m["marcas"],
            "as marcas saem na ordem, com o arquivo, o número dado, o nível e o código em NFC; comentário que não "
            "começa por um nível não é marca")
    confere([c for _, c in marcas.com_caminho(lidas, m["niveis"])] == m["caminhos"],
            "o caminho de cada marca: abrir um nível fecha os de dentro, e cada arquivo começa sem nada aberto")
    niveis, nome = m["niveis"], palavra()
    c1, c2 = codigo(), codigo()
    engole = marcas.marcas_das_linhas([(1, f"{ABRE} {palavra()}"), (2, comentario_de(niveis.dentro, c1)),
                                       (3, f"{palavra()} {comentario_de(niveis.dentro, c2)}")], nome, niveis)
    confere([(x.linha, x.codigo) for x in engole] == [(3, c2)], "um comentário vai até o primeiro fim de comentário")
    sem_fim = marcas.marcas_das_linhas([(2, comentario_de(niveis.dentro, c1)), (5, f"{palavra()} {ABRE} {palavra()}"),
                                        (6, f"{ABRE} {niveis.dentro} {c2}")], nome, niveis)
    confere([tuple(x) for x in sem_fim] == [(nome, 2, niveis.dentro, c1), (nome, 5, None, None)],
            "o comentário que não fecha sai sem nível, na linha dele, e nada depois dele sai")


def confere_avisos(nome, avisos, esperados, dizem=None):
    """Os avisos sao os esperados, (caso, arquivo, linha, unidade, codigo), e so eles; o
    texto de cada um diz o codigo e, nos casos de dizem, o texto dado."""
    obtidos = collections.Counter((a.caso, a.arquivo, a.linha, a.unidade, a.codigo) for a in avisos)
    confere(obtidos == collections.Counter(esperados),
            f"{nome}: os avisos do caso, e só eles: esperados {sorted(map(str, esperados))}, vieram "
            f"{sorted(map(str, obtidos.elements()))}")
    confere(all(a.tipo == (marcas.FALTA if a.caso == "falta" else marcas.ERRO) for a in avisos),
            f"{nome}: FALTA só no caso da falta, ERRO nos outros")
    confere(all(a.codigo is None or a.codigo in a.texto for a in avisos), f"{nome}: o texto de cada aviso diz o código")
    for caso, dito in (dizem or {}).items():
        confere(all(dito in a.texto for a in avisos if a.caso == caso), f"{nome}: o aviso {caso} diz {dito}")
    CASOS_VISTOS.update(a.caso for a in avisos)


def sem(linhas, tira):
    """As linhas sem as marcas para as quais tira(peca) e verdadeiro; a linha que fica sem
    nada ganha uma palavra."""
    for entradas in linhas.values():
        for e in entradas:
            e["pecas"] = [p for p in e["pecas"] if not isinstance(p, Peca) or not tira(p)] or [palavra()]
    return linhas


def troca(linhas, m, entrada, pecas):
    """As linhas com a linha do mundo dada trocada pelas pecas, no mesmo numero."""
    nome, i = m["posicao"][id(entrada)]
    linhas[nome][i]["pecas"] = list(pecas)
    return linhas


def linha(m, entrada):
    """(arquivo, numero) de uma linha do mundo."""
    return m["posicao"][id(entrada)][0], entrada["numero"]


def folhas(u):
    """As regioes do esperado de dentro de nenhuma outra, sem a da unidade."""
    caminhos = [tuple(r.caminho) for r in u["regioes"]]
    pais = {c for outro in caminhos for c in cortes(outro)[:-1]}
    return [r for r in u["regioes"] if tuple(r.caminho) not in pais and mais_funda(r.caminho) > 0]


def irmas_seguidas(u):
    """Os pares de folhas seguidas no esperado que so diferem no nivel mais fundo delas."""
    de_fora = {tuple(r.caminho) for r in folhas(u)}
    saida = []
    for r1, r2 in zip(u["regioes"], u["regioes"][1:]):
        a, b = tuple(r1.caminho), tuple(r2.caminho)
        if a in de_fora and b in de_fora and mais_funda(a) == mais_funda(b) and a[:mais_funda(a)] == b[:mais_funda(a)]:
            saida.append((r1, r2))
    return saida


def estragos(m):
    """[(nome, linhas, avisos esperados, o que o texto deles diz)]: cada estrago do texto
    certo, com os avisos que ele da."""
    niveis, unidades, regioes, saida = m["niveis"], m["unidades"], m["regioes"], []
    por_codigo = {u["unidade"]: u for u in unidades}
    titulos = [entradas[0] for entradas in m["arquivos"].values()]
    fins = [entradas[-1] for entradas in m["arquivos"].values()]
    todas = [e for entradas in m["arquivos"].values() for e in entradas]
    prosas = [e for e in todas if e["papel"] in ("prosa", "fim-da-regiao")]

    def da_unidade(u):
        return u["abertas"][caminho_da_unidade(u["unidade"], len(niveis.abrem))]

    def unidade_de(e):
        return por_codigo[e["caminho"][0]]

    def codigos_de(u):
        return sorted({c for r in u["regioes"] for c in r.codigos} | set(u["livres"]))

    def lugares_de(u, c):
        return [tuple(r.caminho) for r in u["regioes"] if c in r.codigos]

    def de_dentro(c):
        return comentario_de(niveis.dentro, c)

    def pecas_de_dentro(c):
        return [p for e in todas for p in e["pecas"]
                if isinstance(p, Peca) and p.nivel == niveis.dentro and p.codigo == c]

    def recebe(caminho):
        return caminho in regioes and regioes[caminho].recebe

    u, r = SORTEIO.choice([(u, r) for u in unidades for r in u["regioes"] if r.codigos])
    c, caminho = SORTEIO.choice(r.codigos), tuple(r.caminho)
    saida.append(("falta-na-regiao", sem(copia(m), lambda p: p.nivel == niveis.dentro and p.codigo == c
                                         and p.caminho == caminho),
                  [("falta", *linha(m, u["abertas"][caminho]), u["unidade"], c)], None))

    u, c = SORTEIO.choice([(u, c) for u in unidades for c in u["livres"]])
    saida.append(("falta-de-livre", sem(copia(m), lambda p: p.nivel == niveis.dentro and p.codigo == c),
                  [("falta", *linha(m, da_unidade(u)), u["unidade"], c)], None))

    u, r = SORTEIO.choice([(u, r) for u in unidades for r in folhas(u) if r.codigos])
    caminho = tuple(r.caminho)
    so_nela = [c for c in u["livres"] if all(p.caminho == caminho for p in pecas_de_dentro(c))]
    saida.append(("regiao-que-nao-foi-aberta", sem(copia(m), lambda p: p.caminho == caminho),
                  [("falta", *linha(m, da_unidade(u)), u["unidade"], c) for c in r.codigos + so_nela], None))

    e = SORTEIO.choice([e for e in prosas if e["papel"] == "prosa" and e["caminho"] in regioes
                        and regioes[e["caminho"]].codigos])
    errada = comentario_de(niveis.abrem[mais_funda(e["caminho"])])
    saida.append(("marca-de-regiao-sem-codigo", troca(copia(m), m, e, [palavras(1, 2), errada]),
                  [("fora-da-forma", *linha(m, e), e["caminho"][0], None)], None))
    e = SORTEIO.choice(titulos)
    errada = comentario_de(qualquer_nivel(niveis), codigo(), palavra())
    saida.append(("marca-com-tres-palavras", troca(copia(m), m, e, [errada]),
                  [("fora-da-forma", *linha(m, e), None, None)], None))

    e = SORTEIO.choice(fins)
    saida.append(("comentario-sem-fim", troca(copia(m), m, e, [palavras(1, 2), f"{ABRE} {palavras()}"]),
                  [("comentario-sem-fim", *linha(m, e), e["caminho"][0], None)], None))

    e, c = titulos[-1], SORTEIO.choice(m["existem"])
    saida.append(("codigo-fora-de-unidade", troca(copia(m), m, e, [de_dentro(c)]),
                  [("fora-de-unidade", *linha(m, e), None, c)], None))
    e, novo, nivel = SORTEIO.choice(titulos), codigo(), SORTEIO.choice(niveis.abrem[1:])
    saida.append(("regiao-fora-de-unidade", troca(copia(m), m, e, [comentario_de(nivel, novo)]),
                  [("fora-de-unidade", *linha(m, e), None, novo)], None))

    u, r = SORTEIO.choice([(u, r) for u in unidades for r in folhas(u)])
    caminho, novo = tuple(r.caminho), codigo()
    e, nivel = u["fins"][caminho], niveis.abrem[mais_funda(caminho)]
    saida.append(("regiao-desconhecida", troca(copia(m), m, e, [comentario_de(nivel, novo)]),
                  [("regiao-desconhecida", *linha(m, e), u["unidade"], novo)], None))
    u, novo = SORTEIO.choice(unidades), codigo()
    e = da_unidade(u)
    nome, i = m["posicao"][id(e)]
    titulo = m["arquivos"][nome][i + 1]
    linhas = troca(troca(copia(m), m, e, [comentario_de(niveis.abrem[0], novo)]), m, titulo,
                   [comentario_de(qualquer_nivel(niveis))])
    saida.append(("unidade-desconhecida", linhas, [("regiao-desconhecida", *linha(m, e), novo, novo),
                                                   ("fora-da-forma", *linha(m, titulo), novo, None)], None))

    u, r1, r2 = SORTEIO.choice([(u, a, b) for u in unidades for a, b in irmas_seguidas(u)])
    a, b = tuple(r1.caminho), tuple(r2.caminho)
    d, e = mais_funda(a), u["fins"][b]
    antes = "{}:{}".format(*linha(m, u["abertas"][a]))
    saida.append(("regiao-repetida", troca(copia(m), m, e, [comentario_de(niveis.abrem[d], a[d])]),
                  [("regiao-repetida", *linha(m, e), u["unidade"], a[d])], {"regiao-repetida": antes}))

    nome, i1 = m["posicao"][id(u["abertas"][a])]
    f1, i2, f2 = (m["posicao"][id(x)][1] for x in (u["fins"][a], u["abertas"][b], u["fins"][b]))
    confere(f1 + 1 == i2, "a segunda irmã começa logo depois do fim da primeira")
    linhas = copia(m)
    entradas, numeros = linhas[nome], [x["numero"] for x in linhas[nome]]
    entradas[i1:f2 + 1] = entradas[i2:f2 + 1] + entradas[i1:f1 + 1]
    for x, numero in zip(entradas, numeros):
        x["numero"] = numero
    saida.append(("fora-de-ordem", linhas, [("fora-de-ordem", nome, entradas[i1 + f2 - i2 + 1]["numero"], u["unidade"],
                                             a[d])], None))

    u, e = SORTEIO.choice(unidades), SORTEIO.choice(fins)
    nomes = list(m["arquivos"])
    primeira, segunda = sorted([linha(m, da_unidade(u)), linha(m, e)], key=lambda x: (nomes.index(x[0]), x[1]))
    saida.append(("unidade-em-dois-lugares", troca(copia(m), m, e, [comentario_de(niveis.abrem[0], u["unidade"])]),
                  [("unidade-em-dois-lugares", *segunda, u["unidade"], u["unidade"])],
                  {"unidade-em-dois-lugares": "{}:{}".format(*primeira)}))

    receptoras = [e for e in prosas if recebe(e["caminho"])]
    e, novo = SORTEIO.choice(receptoras), codigo()
    saida.append(("nao-existe", troca(copia(m), m, e, [palavras(1, 2), de_dentro(novo)]),
                  [("nao-existe", *linha(m, e), e["caminho"][0], novo)], None))

    e = SORTEIO.choice(receptoras)
    c = SORTEIO.choice([c for c in m["existem"] if c not in codigos_de(unidade_de(e))])
    saida.append(("outra-unidade", troca(copia(m), m, e, [de_dentro(c)]),
                  [("outra-unidade", *linha(m, e), e["caminho"][0], c)], None))

    for nome_, lugares in (("regiao-que-nao-recebe", [e for e in prosas if e["caminho"] in regioes
                                                       and not recebe(e["caminho"])]),
                           ("regiao-de-passagem", [e for e in prosas if e["caminho"] not in regioes])):
        e = SORTEIO.choice([e for e in lugares if codigos_de(unidade_de(e))])
        c = SORTEIO.choice(codigos_de(unidade_de(e)))
        saida.append((nome_, troca(copia(m), m, e, [de_dentro(c), palavras(1, 2)]),
                      [("regiao-que-nao-recebe", *linha(m, e), e["caminho"][0], c)], None))

    e, c = SORTEIO.choice([(e, c) for e in receptoras for c in codigos_de(unidade_de(e))
                           if lugares_de(unidade_de(e), c) and e["caminho"] not in lugares_de(unidade_de(e), c)
                           and c not in unidade_de(e)["livres"]])
    saida.append(("outra-regiao", troca(copia(m), m, e, [de_dentro(c)]),
                  [("outra-regiao", *linha(m, e), e["caminho"][0], c)], None))
    return saida


def teste_juntos(m):
    """Uma falta no primeiro arquivo e tres erros em linhas diferentes, um deles no comeco do
    ultimo arquivo: os avisos de cada um, em ordem de arquivo e linha; duas rodadas, e o
    esperado e os codigos que existem em outra ordem, dao o mesmo."""
    niveis = m["niveis"]
    nomes = list(m["arquivos"])
    titulo = m["arquivos"][nomes[-1]][0]
    regioes = m["regioes"]
    u, r = SORTEIO.choice([(u, r) for u in m["unidades"] for r in u["regioes"]
                           if r.codigos and m["posicao"][id(u["abertas"][tuple(r.caminho)])][0] == nomes[0]])
    falta = SORTEIO.choice(r.codigos)
    outras = [e for entradas in m["arquivos"].values() for e in entradas if e["papel"] == "prosa" and e is not titulo]
    receptora = SORTEIO.choice([e for e in outras if e["caminho"] in regioes and regioes[e["caminho"]].recebe])
    errada = SORTEIO.choice([e for e in outras if e is not receptora])
    c, novo = SORTEIO.choice(m["existem"]), codigo()
    linhas = sem(copia(m), lambda p: p.nivel == niveis.dentro and p.codigo == falta and p.caminho == tuple(r.caminho))
    linhas = troca(troca(troca(linhas, m, titulo, [comentario_de(niveis.dentro, c)]), m, receptora,
                         [comentario_de(niveis.dentro, novo)]), m, errada, [comentario_de(niveis.dentro)])
    avisos = avisos_de(linhas, m)
    confere_avisos("juntos", avisos, [("falta", *linha(m, u["abertas"][tuple(r.caminho)]), u["unidade"], falta),
                                      ("fora-de-unidade", *linha(m, titulo), None, c),
                                      ("nao-existe", *linha(m, receptora), receptora["caminho"][0], novo),
                                      ("fora-da-forma", *linha(m, errada), errada["caminho"][0], None)])
    confere([(a.arquivo, a.linha) for a in avisos] == sorted(((a.arquivo, a.linha) for a in avisos),
                                                             key=lambda x: (nomes.index(x[0]), x[1])),
            "os avisos saem em ordem de arquivo e linha")
    confere(avisos_de(linhas, m) == avisos, "duas rodadas, os mesmos avisos")
    invertido = dict(reversed(list(m["esperados"].items())))
    confere(avisos_de(linhas, m, invertido, SORTEIO.sample(m["existem"], len(m["existem"]))) == avisos,
            "o esperado e os códigos que existem em outra ordem dão os mesmos avisos")


def teste_um_nivel():
    niveis = marcas.Niveis([palavra()], palavra(True))
    unidade, c1, c2, nome = codigo(), codigo(), codigo(), f"{palavra()}.md"
    esperados = {unidade: marcas.Esperado([marcas.Regiao((unidade,), [c1, c2], True)], [])}
    linhas = [(1, palavras()), (2, comentario_de(niveis.abrem[0], unidade)), (3, comentario_de(niveis.dentro, c1)),
              (5, f"{palavras()} {comentario_de(niveis.dentro, c2)}")]
    certo = marcas.confere(marcas.marcas_das_linhas(linhas, nome, niveis), niveis, esperados, [c1, c2])
    confere(certo == [], f"com um nível só, o texto certo não dá aviso: {certo}")
    sem_c2 = marcas.confere(marcas.marcas_das_linhas(linhas[:3], nome, niveis), niveis, esperados, [c1, c2])
    confere([(a.caso, a.linha, a.unidade, a.codigo) for a in sem_c2] == [("falta", 2, unidade, c2)],
            f"com um nível só, a falta fica na linha da unidade: {sem_c2}")


def erro_de_marcas(chamada, culpados, descricao):
    try:
        chamada()
        confere(False, f"{descricao} é ErroDeMarcas")
    except marcas.ErroDeMarcas as e:
        confere(all(c in str(e) for c in culpados), f"o erro de {descricao} diz {culpados}: {e}")


def teste_niveis_e_esperado_que_nao_servem(m):
    niveis, esperados, existem = m["niveis"], m["esperados"], m["existem"]
    a, b, dentro = niveis.abrem[0], niveis.abrem[1], niveis.dentro
    acentuado, espaco = palavra(True), f"{palavra()} {palavra()}"

    def com_niveis(outros):
        return lambda: marcas.confere([], outros, esperados, existem)

    erro_de_marcas(com_niveis(marcas.Niveis([], dentro)), [], "nenhum nível que abre região")
    erro_de_marcas(com_niveis(marcas.Niveis(a, dentro)), [a], "os níveis que abrem região num texto só")
    erro_de_marcas(com_niveis(marcas.Niveis([a, espaco], dentro)), [espaco], "nível com espaço")
    erro_de_marcas(com_niveis(marcas.Niveis([a, b, a], dentro)), [a], "nível repetido")
    erro_de_marcas(com_niveis(marcas.Niveis([a, b], a)), [a], "o nível de dentro igual a um que abre região")
    erro_de_marcas(com_niveis(marcas.Niveis([acentuado, nfd(acentuado)], dentro)), [acentuado],
                   "nível repetido, em NFC e em NFD")
    erro_de_marcas(lambda: marcas.marcas_das_linhas([], palavra(), marcas.Niveis([a, a], dentro)), [a],
                   "nível repetido na leitura")
    erro_de_marcas(lambda: marcas.com_caminho([], marcas.Niveis([a, a], dentro)), [a], "nível repetido no caminho")

    u = next(u for u in m["unidades"] if u["vitrine"])
    unidade, regioes, livres = u["unidade"], list(u["regioes"]), list(u["livres"])
    posicao = {nome: [tuple(r.caminho) for r in regioes].index(caminho) for nome, caminho in u["vitrine"].items()}
    pula, do_meio, debaixo = (regioes[posicao[nome]] for nome in ("pula", "do_meio", "debaixo"))
    c1, x = do_meio.codigos[0], codigo()

    def com(novas=regioes, outros_livres=livres, outros_existem=existem):
        return lambda: marcas.confere([], niveis, {**esperados, unidade: marcas.Esperado(novas, outros_livres)},
                                      outros_existem)

    def troca_regiao(nome, regiao):
        """As regioes da vitrine com a do nome dado trocada pela regiao dada."""
        k = posicao[nome]
        return regioes[:k] + [regiao] + regioes[k + 1:]

    def trocadas(nome1, nome2):
        """As regioes da vitrine com as duas dos nomes dados uma no lugar da outra."""
        saida = list(regioes)
        saida[posicao[nome1]], saida[posicao[nome2]] = regioes[posicao[nome2]], regioes[posicao[nome1]]
        return saida

    erro_de_marcas(com(troca_regiao("do_meio", do_meio._replace(caminho=do_meio.caminho[:-1]))), [unidade],
                   "caminho sem um código por nível")
    erro_de_marcas(com(troca_regiao("do_meio", do_meio._replace(caminho=(x,) + do_meio.caminho[1:]))), [unidade, x],
                   "caminho que não começa pela unidade")
    erro_de_marcas(com(troca_regiao("do_meio", do_meio._replace(caminho=do_meio.caminho[:-1] + (espaco,)))),
                   [espaco], "caminho com espaço")
    erro_de_marcas(com(regioes + [debaixo]), [debaixo.caminho[-1]], "região repetida")
    erro_de_marcas(com(troca_regiao("do_meio", do_meio._replace(recebe="sim"))), [unidade],
                   "recebe que não é True nem False")
    erro_de_marcas(com(troca_regiao("do_meio", do_meio._replace(codigos=c1))), [c1], "os códigos num texto só")
    erro_de_marcas(com(troca_regiao("do_meio", do_meio._replace(codigos=[c1, espaco]))), [espaco], "código com espaço")
    numero = SORTEIO.randint(1000, 9999)
    erro_de_marcas(com(troca_regiao("do_meio", do_meio._replace(codigos=[c1, numero]))), [str(numero)],
                   "código que não é texto")
    fim = f"{palavra()}-->{palavra()}"
    erro_de_marcas(com(troca_regiao("do_meio", do_meio._replace(codigos=[c1, fim])), outros_existem=existem + [fim]),
                   [fim], "código com o fim do comentário, também entre os que existem")
    erro_de_marcas(com(troca_regiao("do_meio", do_meio._replace(codigos=[c1, c1]))), [c1], "código repetido na região")
    erro_de_marcas(com(troca_regiao("pula", pula._replace(codigos=[x])), outros_existem=existem + [x]), [x],
                   "códigos numa região que não recebe")
    erro_de_marcas(com(outros_existem=[c for c in existem if c != c1]), [c1], "código que não existe")
    erro_de_marcas(com(outros_existem=[c for c in existem if c != livres[0]]), [livres[0]],
                   "código que vale em qualquer região e não existe")
    erro_de_marcas(com([r._replace(codigos=[], recebe=False) for r in regioes]), [unidade],
                   "códigos que valem em qualquer região sem região que recebe")
    erro_de_marcas(com(trocadas("pula", "do_meio")), [pula.caminho[-1]],
                   "região que pede fechado um nível que outra antes dela abriu")
    erro_de_marcas(com(trocadas("irma2", "debaixo")), [do_meio.caminho[1]],
                   "região que pede aberta outra vez uma região")
    erro_de_marcas(lambda: marcas.confere([], niveis, {**esperados, espaco: marcas.Esperado([], [])}, existem),
                   [espaco], "unidade com espaço")
    erro_de_marcas(lambda: marcas.confere([], niveis, {acentuado: marcas.Esperado([], []),
                                                       nfd(acentuado): marcas.Esperado([], [])}, existem),
                   [acentuado], "unidade repetida, em NFC e em NFD")
    erro_de_marcas(lambda: marcas.confere([], niveis, esperados, x), [x], "os códigos que existem num texto só")
    erro_de_marcas(lambda: marcas.confere([], niveis, esperados, existem + [espaco]), [espaco],
                   "código que existe com espaço")


def main():
    if TRABALHO.exists() and any(TRABALHO.iterdir()):
        sys.exit("a pasta de trabalho precisa ser nova ou vazia")
    TRABALHO.mkdir(parents=True, exist_ok=True)
    m = sorteia_mundo()
    grava(m)
    teste_leitura(m)
    certo = avisos_de(copia(m), m)
    confere(certo == [], f"o texto certo não dá aviso: {certo}")
    for nome, linhas, esperados, dizem in estragos(m):
        confere_avisos(nome, avisos_de(linhas, m), esperados, dizem)
    teste_juntos(m)
    teste_um_nivel()
    teste_niveis_e_esperado_que_nao_servem(m)
    confere(CASOS_VISTOS == set(marcas.CASOS),
            f"todos os casos de aviso aparecem: faltam {set(marcas.CASOS) - CASOS_VISTOS}")
    print(f"{len(FALHAS)} falha(s) (semente {ARGS.semente})")
    sys.exit(1 if FALHAS else 0)


if __name__ == "__main__":
    main()
