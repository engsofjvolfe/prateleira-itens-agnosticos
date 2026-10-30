"""Testes de itens.py.

O documento e sorteado aqui, com uma semente fixa (o sorteio e o mesmo em toda rodada): um
manual numerado com capa, sumario, corpo e anexos, em paginas, escrito num padrao de
transcricao e com formas de linha que nao sao os de nenhum documento real. Os itens tem
numeros de ate tres niveis e titulos sorteados, com caracteres que o padrao escapa e com
trechos destacados; uns tem o titulo na linha seguinte, umas entradas do sumario tem o
numero sozinho numa linha. Entre os itens ha texto e notas de rodape numeradas, e na capa
uma data que parece numero de item. O titulo de uma entrada do sumario pode ser so o comeco
do titulo do item.

Os testes conferem regras que valem para qualquer documento, nunca uma lista pronta:
  - os itens que saem sao os do documento, na ordem, com a serie, o numero, o titulo sem
    as marcas, a pagina e a linha; nem a nota de rodape nem a capa passam por item;
  - sem erro no documento, nenhum problema; com um erro posto no documento sorteado (um
    numero que salta, um repetido, uma entrada do sumario sem item, um titulo diferente),
    o problema dele e so ele, na linha dele; com os quatro, os quatro;
  - os grupos, para varios tamanhos, e tambem com um sumario que comeca depois dos
    primeiros itens: cada item num grupo so, na ordem; cada grupo, menos o primeiro,
    comeca na primeira vez que aparece uma entrada do sumario; cada um tem o tamanho em
    entradas, menos o ultimo, que tem de 1 ao tamanho; as paginas de cada grupo sao a do
    primeiro e a do ultimo item;
  - todo erro para tudo, sem gravar nada; duas rodadas dao a mesma saida.
Uso:
    python3 -I teste_itens.py <pasta de itens.py> <pasta de trabalho nova>
Precisa do extrator_comum.py, do extrator, na pasta irma "extrator" ou na mesma pasta.
"""
import json
import math
import random
import string
import subprocess
import sys
from pathlib import Path

PECA, TRABALHO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
FALHAS = []
SORTEIO = random.Random(1)


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


PADRAO = {"titulo_pagina": "=== {rotulo} / folha {arquivo} ===", "rotulo_numerada": "pg {numero}",
          "rotulo_sem_numero": "pg ?", "rotulo_sem_paginas": "inteiro", "sem_texto": "(vazio)", "escape": "^",
          "escapar": ["^", "<", ">", "#"], "escapar_no_comeco": ["="],
          "destaques": {"forte": {"abre": "<<", "fecha": ">>"}},
          "tabela": {"inicio": "#", "meio": "#", "fim": "#", "separador": "-"}}
SEP = ":"
FORMAS = {
    "item": [
        {"expressao": rf"^(?P<numero>\d+(?:{SEP}\d+)+)(?:\s+(?P<titulo>\S.*))?$", "serie": "corpo",
         "linhas_do_titulo": 1},
        {"expressao": r"^(?P<numero>\d+)\s+(?P<titulo>\S.*)$", "serie": "corpo", "so_se_no_sumario": True},
        {"expressao": r"^Anexo (?P<numero>[A-Z])$", "serie": "anexo", "linhas_do_titulo": 2},
        {"expressao": rf"^(?P<numero>[A-Z](?:{SEP}\d+)+)\s+(?P<titulo>\S.*)$", "serie": "anexo"},
    ],
    "sumario": [
        {"expressao": rf"^(?P<numero>\d+(?:{SEP}\d+)*)\s+(?P<titulo>.+?)\s*\.{{2,}}", "serie": "corpo"},
        {"expressao": r"^Anexo (?P<numero>[A-Z])\s+(?P<titulo>.+?)\s*\.{2,}", "serie": "anexo"},
    ],
    "numero_sozinho": rf"^\d+(?:{SEP}\d+)*$",
    "separador": SEP,
}
LETRAS = string.ascii_letters + "áâãçéêíóôõú"
# o titulo nao tem ponto: no sumario, os pontos seguidos separam o titulo da pagina
NO_TITULO = LETRAS + string.digits + "".join(c for c in string.punctuation if c != ".")


# ---------- o documento sorteado ----------

def palavra(alfabeto):
    return "".join(SORTEIO.choice(alfabeto) for _ in range(SORTEIO.randint(1, 6)))


def titulo():
    """Um titulo sorteado que comeca por letra."""
    return " ".join([SORTEIO.choice(LETRAS) + palavra(NO_TITULO)]
                    + [palavra(NO_TITULO) for _ in range(SORTEIO.randint(0, 4))])


def escrita(pedacos):
    """A linha no padrao: pedacos [(texto, destacado)], cada caractere que se escapa com o
    escape, o destacado entre as marcas, e o escape no comeco se a linha comeca com um
    caractere do comeco."""
    esc, forte = PADRAO["escape"], PADRAO["destaques"]["forte"]
    texto = lambda s: "".join(esc + c if c in PADRAO["escapar"] else c for c in s)  # noqa: E731
    linha = "".join(forte["abre"] + texto(s) + forte["fecha"] if d else texto(s) for s, d in pedacos)
    return esc + linha if linha[:1] in PADRAO["escapar_no_comeco"] else linha


def com_destaque(texto):
    """Os pedacos de um texto, com um trecho de palavras seguidas destacado ou nenhum."""
    palavras = texto.split(" ")
    if SORTEIO.random() < 0.5:
        return [(texto, False)]
    a = SORTEIO.randrange(len(palavras))
    b = SORTEIO.randint(a + 1, len(palavras))
    antes, meio, depois = " ".join(palavras[:a]), " ".join(palavras[a:b]), " ".join(palavras[b:])
    pedacos = ((antes + (" " if antes else ""), False), (meio, True), ((" " if depois else "") + depois, False))
    return [p for p in pedacos if p[0]]


def ultimo_irmao(itens, i):
    """Se o item i, de [(numero em partes, serie)], e folha e o ultimo dos irmaos: o
    seguinte da mesma serie e de um nivel acima, ou nao ha."""
    n, s = itens[i]
    seguinte = next((m for m, t in itens[i + 1:] if t == s), None)
    return seguinte is None or len(seguinte) < len(n)


def arvore():
    """[(numero em partes, serie)] em ordem: secoes de ate tres niveis e anexos de dois, com
    pelo menos um item de terceiro nivel que e o ultimo dos irmaos e um de segundo nivel."""
    while True:
        itens = []

        def filhos(pai, nivel):
            for k in range(1, SORTEIO.randint(0, 3) + 1):
                itens.append((pai + (k,), "corpo"))
                if nivel < 3:
                    filhos(pai + (k,), nivel + 1)
        for k in range(1, SORTEIO.randint(3, 5) + 1):
            itens.append(((k,), "corpo"))
            filhos((k,), 2)
        for k in range(1, SORTEIO.randint(1, 2) + 1):
            itens.append(((k,), "anexo"))
            itens += [((k, j), "anexo") for j in range(1, SORTEIO.randint(1, 3) + 1)]
        if any(len(n) == 3 and ultimo_irmao(itens, i) for i, (n, _) in enumerate(itens)) \
                and any(len(n) == 2 and s == "corpo" for n, s in itens):
            return itens


def numero(partes, serie):
    primeira = chr(ord("A") + partes[0] - 1) if serie == "anexo" else str(partes[0])
    return SEP.join([primeira] + [str(p) for p in partes[1:]])


def documento():
    """O documento sorteado: [{"numero", "partes", "serie", "titulo", "jeito", "no_sumario",
    "titulo_no_sumario"}]; o jeito diz como o item se escreve: "linha" (numero e titulo),
    "seguinte" (o titulo na linha seguinte) ou "anexo" (o titulo nas duas linhas seguintes);
    o titulo no sumario e o comeco do titulo, palavras inteiras."""
    out = []
    for partes, serie in arvore():
        if serie == "anexo" and len(partes) == 1:
            jeito, t = "anexo", f"({palavra(LETRAS)}) {titulo()}"
        elif serie == "corpo" and len(partes) > 1:
            jeito, t = SORTEIO.choice(["linha", "linha", "seguinte"]), titulo()
        else:
            jeito, t = "linha", titulo()
        out.append({"numero": numero(partes, serie), "partes": partes, "serie": serie, "titulo": t, "jeito": jeito,
                    "no_sumario": len(partes) == 1 or (serie == "corpo" and len(partes) == 2),
                    "titulo_no_sumario": comeco(t)})
    return out


def comeco(texto):
    palavras = texto.split(" ")
    return " ".join(palavras[:SORTEIO.randint(1, len(palavras))])


QUANTAS_LINHAS = {"linha": 1, "seguinte": 3, "anexo": 3}


def linhas_do_item(item):
    """As linhas de um item no corpo, no padrao, pelo jeito dele."""
    num = [(item["numero"], SORTEIO.random() < 0.3)]
    if item["jeito"] == "anexo":
        um, dois = item["titulo"].split(" ", 1)
        return [escrita([(f"Anexo {item['numero']}", False)]), escrita([(um, False)]), escrita(com_destaque(dois))]
    if item["jeito"] == "seguinte":
        return [escrita(num), "", escrita(com_destaque(item["titulo"]))]
    return [escrita(num + [(" ", False)] + com_destaque(item["titulo"]))]


def linhas_do_sumario(itens):
    """As linhas do sumario, uma entrada para cada item que vai nele."""
    out = []
    for item in itens:
        pagina = f" {'.' * SORTEIO.randint(2, 9)} {SORTEIO.randint(1, 99)}"
        t = item["titulo_no_sumario"]
        if item["serie"] == "anexo":
            out.append(escrita([(f"Anexo {item['numero']} {t}{pagina}", False)]))
        elif SORTEIO.random() < 0.3:
            out += [escrita([(item["numero"], False)]), escrita([(t + pagina, False)])]
        else:
            out.append(escrita([(f"{item['numero']} {t}{pagina}", False)]))
    return out


def nota_de_rodape(itens):
    """Uma linha que comeca por um numero sozinho e nao e item: o texto nao comeca pelo
    titulo da entrada do sumario com esse numero."""
    n = SORTEIO.randint(1, 9)
    entrada = next((i["titulo_no_sumario"] for i in itens if i["no_sumario"] and i["numero"] == str(n)), None)
    texto = titulo()
    while entrada and texto.casefold().startswith(entrada.casefold()):
        texto = titulo()
    return escrita([(f"{n} {texto}", False)])


def transcricao(itens, sumario, inserir=None):
    """(texto, itens esperados, total de paginas, primeira linha de cada pagina) do
    documento: capa, sumario e o corpo em paginas sorteadas, com texto e notas de rodape
    entre os itens. inserir = (k, linha): uma linha posta logo depois das linhas do item k.
    Cada item esperado leva a pagina e a linha dele."""
    capa = [escrita([(titulo(), False)]), escrita([(SEP.join(str(SORTEIO.randint(1, 31)) for _ in range(3)), False)])]
    paginas, esperados, corpo = [("capa", capa), ("i", sumario)], [], []
    for k, item in enumerate(itens):
        if SORTEIO.random() < 0.25 and corpo:
            paginas.append((str(len(paginas) - 1), corpo))
            corpo = []
        if SORTEIO.random() < 0.3:
            corpo.append(escrita([(titulo(), False)]))
        if SORTEIO.random() < 0.15:
            corpo.append(nota_de_rodape(itens))
        esperados.append((item, len(paginas) + 1, len(corpo)))
        corpo += linhas_do_item(item)
        if inserir and inserir[0] == k:
            corpo.append(inserir[1])
    paginas.append((str(len(paginas) - 1), corpo))
    texto, onde = [], {}
    for n, (rotulo, ls) in enumerate(paginas, start=1):
        texto += [PADRAO["titulo_pagina"].format(rotulo=rotulo, arquivo=n), ""]
        onde[n] = len(texto) + 1
        texto += ls + [""]
    return ("\n".join(texto), [dict(i, pagina_arquivo=p, linha=onde[p] + k) for i, p, k in esperados], len(paginas),
            onde)


def roda(nome, texto, paginas, grupo=2, formas=FORMAS, padrao=PADRAO, corpo=None):
    pasta = TRABALHO / nome
    pasta.mkdir(parents=True)
    (pasta / "manual.md").write_text(texto, encoding="utf-8")
    config = {"versao_schema": 1, "formas": formas, "grupo": grupo, "documentos": [
        {"transcricao": "manual.md", "sumario": [{"de": 2, "ate": 2}], "corpo": corpo or [{"de": 3, "ate": paginas}]}]}
    for arq, dados in (("extrator.json", {"versao_schema": 1, "padrao": padrao}), ("itens.json", config)):
        (pasta / arq).write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    r = subprocess.run([sys.executable, "-I", str(PECA / "itens.py"), str(pasta / "extrator.json"),
                        str(pasta / "itens.json"), str(pasta / "saida.json"), "--raiz", str(pasta)],
                       capture_output=True, text=True)
    saida = pasta / "saida.json"
    dados = json.loads(saida.read_text(encoding="utf-8"))["documentos"][0] if saida.exists() else None
    return r.returncode, r.stdout + r.stderr, dados, saida


def confere_itens(d, esperados, onde):
    achados = [(i["serie"], i["numero"], i["titulo"], i["pagina_arquivo"], i["linha"]) for i in d["itens"]]
    quer = [(i["serie"], i["numero"], i["titulo"], i["pagina_arquivo"], i["linha"]) for i in esperados]
    diferentes = [(a, b) for a, b in zip(achados, quer) if a != b][:3]
    confere(achados == quer, f"{onde}: os itens são os do documento, na ordem, com série, número, título sem as "
                             f"marcas, página e linha: {diferentes or (len(achados), len(quer))}")


def confere_grupos(d, chaves_do_sumario, tamanho, onde):
    grupos, itens = d["grupos"], d["itens"]
    confere([n for g in grupos for n in g["itens"]] == [i["numero"] for i in itens],
            f"{onde}: cada item num grupo só, na ordem")
    primeira = {}
    for k, i in enumerate(itens):
        primeira.setdefault((i["serie"], i["numero"]), k)
    inicios = sorted({primeira[c] for c in chaves_do_sumario if c in primeira})
    limites, k = [], 0
    for g in grupos:
        limites.append((k, k + len(g["itens"])))
        k += len(g["itens"])
    confere(len(grupos) == math.ceil(len(inicios) / tamanho), f"{onde}: um grupo a cada {tamanho} entradas")
    confere(all(a in inicios for a, _ in limites[1:]), f"{onde}: cada grupo começa numa entrada do sumário")
    contagem = [sum(1 for x in inicios if a <= x < b) for a, b in limites]
    confere(all(c == tamanho for c in contagem[:-1]) and 1 <= contagem[-1] <= tamanho,
            f"{onde}: {tamanho} entradas por grupo, e de 1 a {tamanho} no último: {contagem}")
    confere(all(g["paginas_arquivo"] == [itens[a]["pagina_arquivo"], itens[b - 1]["pagina_arquivo"]]
                for g, (a, b) in zip(grupos, limites)), f"{onde}: as páginas de cada grupo")
    confere(len({g["id"] for g in grupos}) == len(grupos), f"{onde}: cada grupo com um id próprio")


ITENS = documento()
NO_SUMARIO = [i for i in ITENS if i["no_sumario"]]
SUMARIO = linhas_do_sumario(NO_SUMARIO)
CHAVES = [(i["serie"], i["numero"]) for i in NO_SUMARIO]
ESTADO = SORTEIO.getstate()  # cada transcricao comeca daqui: so muda o que o erro muda

# ---------- o documento sem erro ----------
TEXTO, ESPERADOS, PAGINAS, _ = transcricao(ITENS, SUMARIO)
for g in sorted({1, 2, 3, len(CHAVES) + 1}):
    cod, out, d, saida = roda(f"limpo-{g}", TEXTO, PAGINAS, grupo=g)
    if confere(cod == 0 and d is not None, f"sem erro no documento, sai com 0 e grava a saída: {out}"):
        confere(d["problemas"] == [], f"sem erro no documento, nenhum problema: {d['problemas']}")
        confere_itens(d, ESPERADOS, f"limpo, grupo {g}")
        confere_grupos(d, CHAVES, g, f"limpo, grupo {g}")
cod, out, d, saida = roda("limpo-de-novo", TEXTO, PAGINAS)
confere(saida.read_bytes() == (TRABALHO / "limpo-2/saida.json").read_bytes(), "duas rodadas dão a mesma saída")

# ---------- o sumario que comeca depois dos primeiros itens ----------
# sem as entradas das secoes ate a primeira que tem filhos: os filhos dela vem antes da
# primeira entrada que sobra (e a secao mesma, que so vale se esta no sumario, nao entra)
CORTE = next(i["partes"][0] for k, i in enumerate(ITENS[:-1]) if len(i["partes"]) == 1 and i["serie"] == "corpo"
             and len(ITENS[k + 1]["partes"]) == 2)
PARCIAL = [i for i in NO_SUMARIO if not (i["serie"] == "corpo" and i["partes"][0] <= CORTE)]
SORTEIO.setstate(ESTADO)
SUMARIO_PARCIAL = linhas_do_sumario(PARCIAL)
texto, _, paginas, _ = transcricao(ITENS, SUMARIO_PARCIAL)
for g in (1, 2):
    cod, out, d, _ = roda(f"sumario-parcial-{g}", texto, paginas, grupo=g)
    if confere(d is not None and d["itens"] and (d["itens"][0]["serie"], d["itens"][0]["numero"])
               not in [(i["serie"], i["numero"]) for i in PARCIAL],
               f"sumário parcial: há itens antes da primeira entrada: {out}"):
        confere_grupos(d, [(i["serie"], i["numero"]) for i in PARCIAL], g, f"sumário parcial, grupo {g}")

# ---------- um erro posto no documento sorteado ----------
SORTEIO.seed(2)  # os erros se sorteiam a parte, sem mudar o documento
K_SALTO = SORTEIO.choice([k for k, i in enumerate(ITENS) if i["serie"] == "corpo" and len(i["partes"]) == 3
                          and ultimo_irmao([(x["partes"], x["serie"]) for x in ITENS], k)])
K_TITULO = SORTEIO.choice([k for k, i in enumerate(ITENS) if i["serie"] == "corpo" and len(i["partes"]) == 2])
K_COPIA = SORTEIO.choice([k for k, i in enumerate(ITENS) if i["serie"] == "corpo" and len(i["partes"]) == 3
                          and k != K_SALTO] or [K_TITULO])
SALTO = ITENS[K_SALTO]["partes"][:-1] + (ITENS[K_SALTO]["partes"][-1] + SORTEIO.randint(2, 9),)
NOVO_TITULO = titulo()
while NOVO_TITULO.casefold().startswith(ITENS[K_TITULO]["titulo_no_sumario"].casefold()):
    NOVO_TITULO = titulo()
SOBRA = {"numero": str(max(i["partes"][0] for i in ITENS if i["serie"] == "corpo") + 1), "serie": "corpo"}
SOBRA["titulo_no_sumario"] = titulo()
SUMARIO_COM_SOBRA = SUMARIO + linhas_do_sumario([SOBRA])
COPIA = escrita([(f"{ITENS[K_COPIA]['numero']} {ITENS[K_COPIA]['titulo']}", False)])
DEPOIS = len(ITENS) - 1  # a copia vai depois do ultimo item


def troca(itens, k, **campos):
    return [dict(i, **campos) if j == k else i for j, i in enumerate(itens)]


ERROS = {
    "salto": dict(itens=troca(ITENS, K_SALTO, numero=numero(SALTO, "corpo"), partes=SALTO),
                  problema=lambda e, o: ("fora_de_sequencia", e[K_SALTO]["numero"], e[K_SALTO]["linha"])),
    "repetido": dict(inserir=(DEPOIS, COPIA), problema=lambda e, o: (
        "repetido", ITENS[K_COPIA]["numero"], e[DEPOIS]["linha"] + QUANTAS_LINHAS[e[DEPOIS]["jeito"]])),
    "sumario-sem-item": dict(sumario=SUMARIO_COM_SOBRA, problema=lambda e, o: (
        "sumario_sem_item", SOBRA["numero"], o[2] + len(SUMARIO))),
    "titulo-diferente": dict(itens=troca(ITENS, K_TITULO, titulo=NOVO_TITULO),
                             problema=lambda e, o: ("titulo_diferente", e[K_TITULO]["numero"], e[K_TITULO]["linha"])),
}
ERROS["os-quatro"] = dict(itens=troca(ERROS["salto"]["itens"], K_TITULO, titulo=NOVO_TITULO),
                          sumario=SUMARIO_COM_SOBRA, inserir=(DEPOIS, COPIA))
for nome, erro_ in ERROS.items():
    SORTEIO.setstate(ESTADO)
    texto, esperados, paginas, onde = transcricao(erro_.get("itens", ITENS), erro_.get("sumario", SUMARIO),
                                                  erro_.get("inserir"))
    cod, out, d, _ = roda(nome, texto, paginas)
    if nome == "os-quatro":
        quer = sorted(ERROS[n]["problema"](esperados, onde) for n in ERROS if n != "os-quatro")
    else:
        quer = [erro_["problema"](esperados, onde)]
    if confere(cod == 1 and d is not None, f"{nome}: com problema, sai com 1 e grava a saída: {out}"):
        achados = sorted((p["tipo"], p["numero"], p["linha"]) for p in d["problemas"])
        confere(achados == quer, f"{nome}: o problema do erro, na linha dele, e só ele: {achados} != {quer}")

# ---------- erros: param tudo e nada e gravado ----------


def erro(nome, descricao, **kw):
    cod, out, d, saida = roda(nome, TEXTO, PAGINAS, **kw)
    confere(cod == 1 and out.startswith("ERRO") and not saida.exists(), f"{descricao} é erro, sem gravar nada: {out}")


erro("expressao-ruim", "expressão que não compila",
     formas=dict(FORMAS, item=[{"expressao": "(?P<numero>[", "serie": "corpo"}]))
erro("sem-sumario", "falta de informação", formas={k: v for k, v in FORMAS.items() if k != "sumario"})
erro("faixa-ruim", "faixa fora das páginas", corpo=[{"de": 3, "ate": PAGINAS + 5}])
erro("grupo-zero", "grupo de tamanho zero", grupo=0)
erro("campo-desconhecido", "campo que o molde não conhece",
     formas=dict(FORMAS, item=[dict(FORMAS["item"][0], linhas_do_titul=1)] + FORMAS["item"][1:]))
erro("padrao-desconhecido", "campo da configuração do extrator que o molde dela não conhece",
     padrao=dict(PADRAO, **{"titulo_pagina_" + palavra(string.ascii_lowercase): PADRAO["titulo_pagina"]}))
erro("padrao-ruim", "padrão em que a marca se confunde com o texto",
     padrao=dict(PADRAO, escapar=[c for c in PADRAO["escapar"] if c != "<"]))

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
