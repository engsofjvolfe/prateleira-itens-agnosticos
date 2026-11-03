"""Testes do baralho-anki, com configuracoes, tabelas, fontes, modelos de cartao e padroes
proibidos inventados aqui, sorteados e com letras de fora do ASCII. Conferem regras, nunca uma
frase pronta:

- gera_csv.py: uma linha por linha da tabela e por coluna de cartao, em ordem, com o id (o
  nome da fonte sem a extensao e o identificador da coluna), o assunto, a coluna, as
  palavras-chave e a fonte da tabela, e a pergunta, a resposta e o trecho vazios; a tabela e a
  primeira do arquivo, fora dos blocos de codigo, e a segunda fica de fora; de novo, a
  pergunta, a resposta e o trecho de cada id que continua ficam, as palavras-chave vem da
  tabela e a linha que a tabela nao da mais sai; a configuracao, a tabela ou o CSV que nao
  servem saem com 2, sem gravar nada;
- confere_baralho.py: o CSV certo sai com 0, com o trecho achado na fonte em NFD, com outros
  espacos e com as marcas de enfase no texto ou no trecho; cada defeito sai com 1 e o ERRO na
  linha dele (o campo diferente da tabela, o id que a tabela nao da, o cartao que falta, o id
  repetido, o campo vazio ou so com espacos, como a pergunta, a resposta e o trecho, o trecho
  que nao esta na fonte, a fonte que nenhuma pasta tem, a linha fora da ordem e o padrao
  proibido de cada arquivo, na pergunta e na resposta, que o exceto deixa passar); a primeira
  pasta que tem a fonte vale; o arquivo de padroes proibidos ou a fonte que nao servem saem
  com 2;
- gera_apkg.py: o pacote e um zip com o banco e a lista vazia das midias, com a data da
  configuracao; o banco tem o baralho e o tipo de nota com os ids do hash do nome (tambem com
  outros nomes sorteados), os campos
  com a letra do editor, os modelos e o estilo como estao nos arquivos, os campos de que a
  frente precisa (um de dois, um deles com filtro, ou o unico), e uma nota e um cartao por
  linha, em ordem, com o guid do hash do id, o HTML escapado, as enfases nas etiquetas, as
  palavras-chave em linhas e as etiquetas da fonte e da coluna; duas rodadas dao os mesmos
  bytes, e outra data, outros bytes com os mesmos guids; a marca sem par, a etiqueta com
  espaco, o id repetido, o modelo que falta ou fora do UTF-8, a data que nao se le e o CSV que
  nao serve saem com 2, sem gravar nada;
- conferido.py: com --gravar, o sha256 da tabela e o de cada fonte, da primeira pasta que a
  tem, na ordem da tabela; sem ele, o registro em dia sai com 0, e a fonte ou a tabela que
  mudaram, a fonte sem registro, a do registro que a tabela nao nomeia e a que nenhuma pasta
  tem saem com 1, com um ERRO para cada uma; com --gravar, a fonte que falta sai com 2, sem
  gravar; o registro fora do molde sai com 2.

Uso:
    python3 -I teste_baralho_anki.py <pasta do baralho-anki> <pasta de trabalho nova>
Precisa do extrator_comum.py e do texto_comum.py, da peca extrator, do markdown_comum.py, da
peca documentos, e do proibidos_comum.py, da peca confere-forma, nas pastas irmas da peca.
"""
import copy
import csv
import datetime
import hashlib
import html
import io
import json
import random
import re
import sqlite3
import subprocess
import sys
import unicodedata
import zipfile
from pathlib import Path

PECA, TRABALHO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
FALHAS = []
SORTEIO = random.Random(5)
MINUSCULAS = "abcdefghijklmnopqrstuvwxyzáçéõü"
COLUNAS = ["id", "assunto", "coluna", "pergunta", "resposta", "palavras_chave", "trecho", "fonte"]
QUEBRA, SEPARADOR, SEPARADOR_DE_CAMPOS = "<br>", " ; ", chr(0x1F)
ESCAPES = {"<": "&lt;", ">": "&gt;", "&": "&amp;"}
ENFASES = [{"marca": "*", "etiqueta": "i"}, {"marca": "**", "etiqueta": "b"},  # a curta antes da longa
           {"marca": "~~", "etiqueta": "s"}]
FAIXA = 1 << 30
AMOSTRAS = 4  # os outros nomes sorteados do baralho e do tipo de nota, para a regra dos ids


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


def palavra():
    return "".join(SORTEIO.choice(MINUSCULAS) for _ in range(SORTEIO.randint(3, 8)))


def frase():
    return " ".join(palavra() for _ in range(SORTEIO.randint(2, 5)))


def identificador(texto):
    """O identificador pela regra: minusculas sem acento, as partes de letras e numeros ligadas por hifen."""
    sem_acento = "".join(c for c in unicodedata.normalize("NFD", texto) if not unicodedata.combining(c)).lower()
    return "-".join(re.findall(r"[a-z0-9]+", sem_acento))


USADOS = set()


def novo(faz):
    """Um nome feito por faz(), com o identificador ainda nao usado."""
    while True:
        nome = faz()
        if identificador(nome) not in USADOS:
            USADOS.add(identificador(nome))
            return nome


def grava(caminho, conteudo):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(conteudo, bytes):
        caminho.write_bytes(conteudo)
    else:
        caminho.write_text(conteudo, encoding="utf-8", newline="")
    return caminho


def grava_json(caminho, dados):
    return grava(caminho, json.dumps(dados, ensure_ascii=False, indent=1))


def le(caminho):
    return Path(caminho).read_text(encoding="utf-8")


def roda(script, *argumentos):
    r = subprocess.run([sys.executable, "-I", str(PECA / script), *map(str, argumentos)], capture_output=True,
                       text=True)
    return r.returncode, r.stdout + r.stderr


def linhas_dos_erros(saida, caminho):
    """Os numeros de linha dos ERRO do arquivo, na saida."""
    return {int(m.group(1)) for m in re.finditer(rf"^ERRO {re.escape(str(caminho))}:(\d+): ", saida, re.M)}


def erros_de(saida):
    return [l for l in saida.split("\n") if l.startswith("ERRO ")]


def le_csv(caminho):
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def texto_csv(linhas):
    """O texto do CSV pela regra: o cabecalho e as linhas, com as aspas do padrao e cada linha
    terminada em \\n."""
    texto = io.StringIO()
    escritor = csv.DictWriter(texto, fieldnames=COLUNAS, lineterminator="\n")
    escritor.writeheader()
    escritor.writerows(linhas)
    return texto.getvalue()


def grava_csv(caminho, linhas):
    return grava(caminho, texto_csv(linhas))


def com_enfase():
    """(Markdown, HTML) de umas palavras, uma delas entre as marcas de uma enfase sorteada, e de um
    sinal que o HTML escapa."""
    partes = [(p, p) for p in [palavra() for _ in range(SORTEIO.randint(2, 4))]]
    k, e = SORTEIO.randrange(len(partes)), SORTEIO.choice(ENFASES)
    p = partes[k][0]
    partes[k] = (f"{e['marca']}{p}{e['marca']}", f"<{e['etiqueta']}>{p}</{e['etiqueta']}>")
    sinal = SORTEIO.choice(sorted(ESCAPES))
    partes.insert(SORTEIO.randrange(len(partes) + 1), (sinal, ESCAPES[sinal]))
    return " ".join(m for m, _ in partes), " ".join(h for _, h in partes)


def frase_da_fonte():
    """(o trecho do CSV, o HTML dele, a frase no texto da fonte): as mesmas palavras, que no texto
    vem em NFD, com outros espacos e uma quebra de linha; uma delas tem as marcas de uma enfase
    no texto ou no trecho."""
    palavras = [palavra() for _ in range(SORTEIO.randint(3, 6))]
    palavras[0] = "é" + palavras[0]  # uma letra que muda em NFD
    k, e = SORTEIO.randrange(len(palavras)), SORTEIO.choice(ENFASES)
    marcadas = [f"{e['marca']}{p}{e['marca']}" if i == k else p for i, p in enumerate(palavras)]
    em_html = [f"<{e['etiqueta']}>{p}</{e['etiqueta']}>" if i == k else p for i, p in enumerate(palavras)]
    if SORTEIO.random() < 0.5:  # as marcas no texto
        no_texto, trecho, html_ = marcadas, palavras, palavras
    else:  # as marcas no trecho
        no_texto, trecho, html_ = palavras, marcadas, em_html
    texto = unicodedata.normalize("NFD", "  ".join(no_texto[:2]) + " \n " + " ".join(no_texto[2:]))
    return " ".join(trecho), " ".join(html_), texto


def celula(partes):
    return SEPARADOR.join(m for m, _ in partes)


def partes_da_tabela(linhas, cartoes=None):
    """(antes, a tabela, depois) do texto de uma tabela: antes, uma frase e um bloco de codigo com
    linhas de tabela; depois, uma segunda tabela, com o mesmo cabecalho e uma linha do mesmo
    numero de celulas, e outra frase. O bloco e a segunda tabela ficam de fora pela regra."""
    cartoes = cartoes or CARTOES
    cabecalho = ["#", ASSUNTO, *cartoes, FONTE]
    titulo, separador = "| " + " | ".join(cabecalho) + " |", "|" + "---|" * len(cabecalho)
    tabela = [titulo, separador]
    for k, l in enumerate(linhas):
        celulas = [celula(l["cartoes"].get(c, l["cartoes"][CARTOES[0]])) for c in cartoes]
        tabela.append("| " + " | ".join([str(k + 1), l["assunto"][0], *celulas, l["fonte"]]) + " |")
    antes = [frase(), "", "```", f"| {palavra()} | {palavra()} |", "|---|---|", f"| {palavra()} | {palavra()} |",
             "```", ""]
    depois = ["", titulo, separador, "| " + " | ".join(palavra() for _ in cabecalho) + " |", "", frase(), ""]
    return antes, tabela, depois


def tabela_md(linhas, cartoes=None):
    antes, tabela, depois = partes_da_tabela(linhas, cartoes)
    return "\n".join(antes + tabela + depois)


def variante(nome, muda):
    conf = copy.deepcopy(CONF)
    muda(conf)
    return grava_json(TRABALHO / "configuracoes" / f"{nome}.json", conf)


TRABALHO.mkdir(parents=True)
ASSUNTO, FONTE = novo(lambda: palavra().capitalize()), novo(lambda: palavra().capitalize())
CARTOES = [novo(lambda: f"{palavra().capitalize()} / {palavra()}") for _ in range(3)]
# os campos da nota: todas as colunas do CSV, em ordem sorteada, com a pergunta no primeiro, que e o campo
# de ordenar do Anki e precisa ter enfase para o sfld sem as etiquetas se conferir
OUTRAS = [c for c in COLUNAS if c != "pergunta"]
COLUNAS_DA_NOTA = ["pergunta", *SORTEIO.sample(OUTRAS, len(OUTRAS))]
NOMES = [novo(lambda: palavra().capitalize()) for _ in COLUNAS_DA_NOTA]
CAMPOS = [{"nome": nome, "coluna": coluna, **({"palavras_chave": True} if coluna == "palavras_chave" else {})}
          for nome, coluna in zip(NOMES, COLUNAS_DA_NOTA)]
LUGAR = {c["coluna"]: k for k, c in enumerate(CAMPOS)}  # o lugar de cada coluna do CSV nos campos da nota
DATA = (f"20{SORTEIO.randint(30, 39)}-{SORTEIO.randint(1, 12):02d}-{SORTEIO.randint(1, 28):02d}T"
        f"{SORTEIO.randint(0, 23):02d}:{SORTEIO.randint(0, 59):02d}:{SORTEIO.randint(0, 59):02d}"
        f"{SORTEIO.choice('+-')}{SORTEIO.randint(0, 11):02d}:00")
CONF = {"versao_schema": 1,
        "tabela": {"assunto": ASSUNTO, "fonte": FONTE, "cartoes": CARTOES, "separador": SEPARADOR},
        "enfases": ENFASES, "baralho": f"{palavra().capitalize()}::{palavra().capitalize()}",
        "nota": {"nome": f"{palavra().capitalize()}: {palavra()}", "cartao": palavra().capitalize(),
                 "campos": CAMPOS, "quebra": QUEBRA,
                 "editor": {"tipo_de_letra": palavra().capitalize(), "tamanho": SORTEIO.randint(10, 30)}},
        "data": DATA}
CONFIGURACAO = grava_json(TRABALHO / "configuração.json", CONF)

PASTA_1, PASTA_2 = TRABALHO / "fontes um", TRABALHO / "fontes dois"
LINHAS = [{"assunto": com_enfase(), "fonte": f"{novo(palavra)}.md",
           "cartoes": {c: [com_enfase() for _ in range(SORTEIO.randint(1, 3))] for c in CARTOES},
           "frases": {c: frase_da_fonte() for c in CARTOES},
           "pasta": PASTA_1 if k == 0 else PASTA_2 if k == 1 else SORTEIO.choice([PASTA_1, PASTA_2])}
          for k in range(SORTEIO.randint(3, 5))]
TABELA = grava(TRABALHO / "tabela.md", tabela_md(LINHAS))
for l in LINHAS:
    grava(l["pasta"] / l["fonte"], "\n".join([f"# {frase()}", ""] + [x for c in CARTOES
                                                                      for x in (l["frases"][c][2], "", frase(), "")]))
ISCA = frase()  # so na copia da primeira fonte que esta na segunda pasta
grava(PASTA_2 / LINHAS[0]["fonte"], le(PASTA_1 / LINHAS[0]["fonte"]) + f"\n{ISCA}\n")
PASTAS = ["--pasta", PASTA_1, "--pasta", PASTA_2]


def stem(fonte):
    return fonte[:-len(".md")]


ESPERADAS = [{"id": f"{stem(l['fonte'])}-{identificador(c)}", "assunto": l["assunto"][0], "coluna": c,
              "pergunta": "", "resposta": "", "palavras_chave": celula(l["cartoes"][c]), "trecho": "",
              "fonte": l["fonte"]} for l in LINHAS for c in CARTOES]
PERGUNTAS = [com_enfase() for _ in ESPERADAS]
RESPOSTAS = [com_enfase() for _ in ESPERADAS]
CHEIAS = [dict(e, pergunta=PERGUNTAS[k][0], resposta=RESPOSTAS[k][0],
               trecho=LINHAS[k // len(CARTOES)]["frases"][e["coluna"]][0]) for k, e in enumerate(ESPERADAS)]
CHEIO = grava_csv(TRABALHO / "cheio.csv", CHEIAS)

# gera_csv.py
CSV = TRABALHO / "saida" / "baralho.csv"
CSV.parent.mkdir()
cod, out = roda("gera_csv.py", CONFIGURACAO, TABELA, CSV)
confere(cod == 0 and CSV.is_file(), f"as entradas certas saem com 0 e gravam o CSV: {out}")
if CSV.is_file():
    confere(CSV.read_bytes() == texto_csv(ESPERADAS).encode("utf-8"),
            f"o CSV tem o cabeçalho das colunas e uma linha por linha da tabela e por coluna de cartão, em ordem, "
            f"cada uma terminada em \\n: {CSV.read_bytes()!r}")
grava_csv(CSV, CHEIAS)
cod, out = roda("gera_csv.py", CONFIGURACAO, TABELA, CSV)
confere(cod == 0 and le_csv(CSV) == CHEIAS, f"de novo, a pergunta, a resposta e o trecho de cada id ficam: {out}")
NOVA_CELULA = [com_enfase()]
OUTRA = grava(TRABALHO / "outra.md", tabela_md([dict(LINHAS[0], cartoes=dict(LINHAS[0]["cartoes"],
                                                                                    **{CARTOES[0]: NOVA_CELULA}))]
                                               + LINHAS[1:]))
cod, out = roda("gera_csv.py", CONFIGURACAO, OUTRA, CSV)
confere(cod == 0 and le_csv(CSV) == [dict(CHEIAS[0], palavras_chave=celula(NOVA_CELULA))] + CHEIAS[1:],
        f"as palavras-chave vêm da tabela de agora, com a pergunta, a resposta e o trecho de antes: {out}")
grava_csv(CSV, CHEIAS)
cod, out = roda("gera_csv.py", CONFIGURACAO, grava(TRABALHO / "menor.md", tabela_md(LINHAS[:-1])), CSV)
confere(cod == 0 and le_csv(CSV) == CHEIAS[:-len(CARTOES)], f"a linha que a tabela não dá mais sai: {out}")

(TRABALHO / "nao-servem").mkdir()  # a pasta existe: o codigo 2 vem da entrada, e nao da pasta que falta
DUPLA = CARTOES + [CARTOES[0].upper()]
TABELA_DUPLA = grava(TRABALHO / "dupla.md", tabela_md(LINHAS, DUPLA))
CONFIGURACOES_RUINS = {
    "campo que o molde não conhece": (variante("desconhecido", lambda c: c.update({palavra(): 1})), TABELA),
    "outra versão": (variante("versao", lambda c: c.update(versao_schema=2)), TABELA),
    "coluna de campo que o CSV não tem":
        (variante("coluna", lambda c: c["nota"]["campos"][0].update(coluna=palavra())), TABELA),
    "nome de campo repetido": (variante("nome", lambda c: c["nota"]["campos"][1].update(nome=NOMES[0])), TABELA),
    "colunas de cartão com o mesmo identificador":
        (variante("dupla", lambda c: c["tabela"].update(cartoes=DUPLA)), TABELA_DUPLA),
    "marca de ênfase repetida":
        (variante("marca", lambda c: c["enfases"].append(dict(ENFASES[0], etiqueta="u"))), TABELA),
}
ANTES, DA_TABELA, DEPOIS = partes_da_tabela(LINHAS)
TABELAS_RUINS = {
    "tabela sem a coluna da fonte":
        "\n".join(ANTES + DA_TABELA + DEPOIS).replace(f" {FONTE} |", f" {novo(palavra)} |", 1),
    "texto sem tabela": f"{frase()}\n\n{frase()}\n",
    "tabela sem linhas": "\n".join(ANTES + DA_TABELA[:2] + DEPOIS),
    "linha com outro número de células": "\n".join(ANTES + DA_TABELA + [f"| {palavra()} | {palavra()} |"] + DEPOIS),
}
for numero, (nome, (configuracao, tabela)) in enumerate(CONFIGURACOES_RUINS.items()):
    saida = TRABALHO / "nao-servem" / f"configuracao-{numero}.csv"
    cod, out = roda("gera_csv.py", configuracao, tabela, saida)
    confere(cod == 2 and out.startswith("ERRO") and not saida.exists(), f"{nome}: sai com 2, sem gravar nada: {out}")
for numero, (nome, texto) in enumerate(TABELAS_RUINS.items()):
    saida = TRABALHO / "nao-servem" / f"tabela-{numero}.csv"
    cod, out = roda("gera_csv.py", CONFIGURACAO, grava(TRABALHO / "nao-servem" / f"tabela-{numero}.md", texto), saida)
    confere(cod == 2 and out.startswith("ERRO") and not saida.exists(), f"{nome}: sai com 2, sem gravar nada: {out}")
CSVS_RUINS = {
    "CSV com outro cabeçalho": grava(TRABALHO / "nao-servem" / "cabecalho.csv",
                                     le(CHEIO).replace(",".join(COLUNAS), ",".join([palavra()] + COLUNAS[1:]), 1)),
    "CSV com uma linha de outro número de campos": grava(TRABALHO / "nao-servem" / "campos.csv",
                                                         le(CHEIO) + f"{palavra()},{palavra()}\n"),
}
for nome, caminho in CSVS_RUINS.items():
    antes = caminho.read_bytes()
    cod, out = roda("gera_csv.py", CONFIGURACAO, TABELA, caminho)
    confere(cod == 2 and out.startswith("ERRO") and caminho.read_bytes() == antes,
            f"{nome}: sai com 2, sem gravar: {out}")

# confere_baralho.py
MARCA_1, MARCA_2, EXCETO = f"#{palavra()}#", f"%{palavra()}%", palavra()
PROIBIDOS = ["--proibidos", grava_json(TRABALHO / "proibidos" / "um.json", {"versao_schema": 1, "proibidos": [
                 {"nome": palavra(), "padrao": re.escape(MARCA_1), "exceto": re.escape(MARCA_1 + EXCETO)}]}),
             "--proibidos", grava_json(TRABALHO / "proibidos" / "dois.json", {"versao_schema": 1, "proibidos": [
                 {"nome": palavra(), "padrao": re.escape(MARCA_2)}]})]


def confere_csv(nome, linhas, *outros, pastas=None):
    caminho = grava_csv(TRABALHO / "conferir" / f"{nome}.csv", linhas)
    cod, out = roda("confere_baralho.py", CONFIGURACAO, TABELA, caminho, *(PASTAS if pastas is None else pastas),
                    *PROIBIDOS, *outros)
    return caminho, cod, out


def com(muda):
    linhas = [dict(l) for l in CHEIAS]
    muda(linhas)
    return linhas


cod, out = roda("confere_baralho.py", CONFIGURACAO, TABELA, CHEIO, *PASTAS, *PROIBIDOS)
confere(cod == 0 and not erros_de(out), f"o CSV certo sai com 0, sem ERRO, com os trechos achados nas fontes: {out}")
J = SORTEIO.randrange(1, len(CHEIAS) - 2)
FIM = len(CHEIAS) + 1  # a ultima linha do CSV
OUTRA_FONTE = next(l["fonte"] for l in LINHAS if l["fonte"] != CHEIAS[J]["fonte"])
DEFEITOS = {
    "palavras-chave diferentes das da tabela":
        (com(lambda ls: ls[J].update(palavras_chave=ls[J]["palavras_chave"] + palavra())), {J + 2}),
    "assunto diferente do da tabela": (com(lambda ls: ls[J].update(assunto=palavra())), {J + 2}),
    "coluna diferente da da tabela": (com(lambda ls: ls[J].update(coluna=palavra())), {J + 2}),
    "fonte diferente da da tabela": (com(lambda ls: ls[J].update(fonte=OUTRA_FONTE)), {J + 2}),
    "id que a tabela não dá": (com(lambda ls: ls[J].update(id=palavra())), {J + 2, FIM}),
    "cartão que falta": (com(lambda ls: ls.pop(J)), {FIM - 1}),
    "id repetido": (com(lambda ls: ls.append(dict(ls[J]))), {FIM + 1}),
    "pergunta vazia": (com(lambda ls: ls[J].update(pergunta="")), {J + 2}),
    "resposta vazia": (com(lambda ls: ls[J].update(resposta="")), {J + 2}),
    "trecho só com espaços": (com(lambda ls: ls[J].update(trecho=" " + chr(9) + " ")), {J + 2}),
    "trecho que não está na fonte": (com(lambda ls: ls[J].update(trecho=f"{ls[J]['trecho']} {palavra()}")), {J + 2}),
    "linha fora da ordem": (com(lambda ls: ls.insert(J + 1, ls.pop(J))), {J + 2}),
    "padrão proibido do primeiro arquivo, na pergunta":
        (com(lambda ls: ls[J].update(pergunta=f"{ls[J]['pergunta']} {MARCA_1}")), {J + 2}),
    "padrão proibido do segundo arquivo, na resposta":
        (com(lambda ls: ls[J + 1].update(resposta=f"{MARCA_2}{ls[J + 1]['resposta']}")), {J + 3}),
}
for numero, (nome, (linhas, esperadas)) in enumerate(DEFEITOS.items()):
    caminho, cod, out = confere_csv(f"defeito-{numero}", linhas)
    confere(cod == 1 and linhas_dos_erros(out, caminho) == esperadas
            and len(erros_de(out)) == len([l for l in erros_de(out) if l.startswith(f"ERRO {caminho}:")]),
            f"{nome}: sai com 1, com o ERRO na(s) linha(s) {sorted(esperadas)}: {out}")
    if nome == "linha fora da ordem":
        confere(len(erros_de(out)) == 1, f"a linha fora da ordem dá um ERRO só: {out}")
caminho, cod, out = confere_csv("excecao",
                                com(lambda ls: ls[J].update(resposta=f"{ls[J]['resposta']} {MARCA_1}{EXCETO}")))
confere(cod == 0 and not erros_de(out), f"o padrão proibido com o exceto passa: {out}")
SEM_PROIBIDOS = grava_csv(TRABALHO / "conferir" / "sem-proibidos.csv",
                          com(lambda ls: ls[J].update(pergunta=f"{ls[J]['pergunta']} {MARCA_1}")))
cod, out = roda("confere_baralho.py", CONFIGURACAO, TABELA, SEM_PROIBIDOS, *PASTAS)
confere(cod == 0 and not erros_de(out), f"sem arquivo de padrões proibidos, nenhum padrão é proibido: {out}")
ISCADO = com(lambda ls: ls[0].update(trecho=ISCA))
caminho, cod, out = confere_csv("isca", ISCADO)
confere(cod == 1 and linhas_dos_erros(out, caminho) == {2}, f"a fonte vem da primeira pasta que a tem: {out}")
caminho, cod, out = confere_csv("isca-invertida", ISCADO, pastas=["--pasta", PASTA_2, "--pasta", PASTA_1])
confere(cod == 0 and not erros_de(out), f"com a outra pasta antes, a fonte vem dela: {out}")
PASTA_DA_FONTE = {l["fonte"]: l["pasta"] for l in LINHAS}
SO_NA_SEGUNDA = {k + 2 for k, e in enumerate(CHEIAS)
                 if PASTA_DA_FONTE[e["fonte"]] == PASTA_2 and e["fonte"] != LINHAS[0]["fonte"]}
caminho, cod, out = confere_csv("uma-pasta", CHEIAS, pastas=["--pasta", PASTA_1])
confere(cod == 1 and linhas_dos_erros(out, caminho) == SO_NA_SEGUNDA,
        f"a fonte que nenhuma pasta tem: ERRO na linha: {out}")

LATIN = TRABALHO / "latin"
grava(LATIN / LINHAS[0]["fonte"], f"{frase()} ç\n".encode("latin-1"))


def proibidos(nome, regra):
    caminho = grava_json(TRABALHO / "proibidos" / f"{nome}.json", {"versao_schema": 1, "proibidos": [regra]})
    return ["--proibidos", caminho]


NAO_SERVEM = {  # nome: (os argumentos antes das pastas, os depois dos padroes proibidos)
    "arquivo de padrões proibidos com campo que o molde não conhece":
        ([], proibidos("campo", {"nome": palavra(), "padrao": palavra(), palavra(): 1})),
    "padrão que não compila": ([], proibidos("compila", {"nome": palavra(), "padrao": "("})),
    "o mesmo nome de regra em dois arquivos":
        ([], proibidos("mesmo", {"nome": json.loads(le(PROIBIDOS[1]))["proibidos"][0]["nome"], "padrao": palavra()})),
    "fonte que não se lê em UTF-8": (["--pasta", LATIN], []),
}
for nome, (antes, depois) in NAO_SERVEM.items():
    cod, out = roda("confere_baralho.py", CONFIGURACAO, TABELA, CHEIO, *antes, *PASTAS, *PROIBIDOS, *depois)
    confere(cod == 2 and out.startswith("ERRO"), f"{nome}: sai com 2: {out}")
cod, out = roda("confere_baralho.py", CONFIGURACAO, TABELA, CSVS_RUINS["CSV com outro cabeçalho"], *PASTAS)
confere(cod == 2 and out.startswith("ERRO"), f"o CSV com outro cabeçalho sai com 2: {out}")

# gera_apkg.py
FRENTE = grava(TRABALHO / "modelos" / "frente.html",
               f"{{{{{NOMES[LUGAR['pergunta']]}}}}} {palavra()} {{{{text:{NOMES[LUGAR['assunto']]}}}}}\n")
VERSO = grava(TRABALHO / "modelos" / "verso.html",
              f"{{{{FrontSide}}}}\n\n<hr id=answer>\n{{{{{NOMES[LUGAR['resposta']]}}}}} {palavra()}")
ESTILO = grava(TRABALHO / "modelos" / "estilo.css", f".{palavra()} {{\n  color: {palavra()};\n}}\n")
MODELOS = ["--frente", FRENTE, "--verso", VERSO, "--estilo", ESTILO]
(TRABALHO / "pacote").mkdir()
APKG = TRABALHO / "pacote" / "baralho.apkg"


def id_do(nome):
    return FAIXA + int.from_bytes(hashlib.sha256(nome.encode("utf-8")).digest()[:4], "big") % FAIXA


def com_nomes(baralho, nota):
    """A mudanca da configuracao que troca o nome do baralho e o do tipo de nota."""
    def muda(conf):
        conf.update(baralho=baralho)
        conf["nota"].update(nome=nota)
    return muda


def abre(caminho):
    """(as entradas do zip, a lista das midias, o banco) do pacote."""
    with zipfile.ZipFile(caminho) as pacote:
        entradas, midias = pacote.infolist(), pacote.read("media") if "media" in pacote.namelist() else None
        banco = sqlite3.connect(":memory:")
        banco.deserialize(pacote.read("collection.anki2"))
    return entradas, midias, banco


cod, out = roda("gera_apkg.py", CONFIGURACAO, CHEIO, APKG, *MODELOS)
confere(cod == 0 and APKG.is_file(), f"as entradas certas saem com 0 e gravam o pacote: {out}")
if APKG.is_file():
    PRIMEIRO = APKG.read_bytes()
    roda("gera_apkg.py", CONFIGURACAO, CHEIO, APKG, *MODELOS)
    confere(APKG.read_bytes() == PRIMEIRO, "duas rodadas dão os mesmos bytes")
    entradas, midias, banco = abre(APKG)
    data = datetime.datetime.fromisoformat(DATA)
    segundos, quando = int(data.timestamp()), (data.year, data.month, data.day, data.hour, data.minute,
                                               data.second - data.second % 2)
    confere([e.filename for e in entradas] == ["collection.anki2", "media"] and midias == b"{}",
            f"o pacote tem o banco e a lista vazia das mídias: {[e.filename for e in entradas]}, {midias!r}")
    confere(all(e.date_time == quando and e.compress_type == zipfile.ZIP_DEFLATED and e.create_system == 3
                and e.external_attr == 0o644 << 16 for e in entradas),
            f"as entradas do zip têm a data da configuração: {[e.date_time for e in entradas]}")
    crt, ver, modelos, baralhos = banco.execute("SELECT crt, ver, models, decks FROM col").fetchone()
    modelos, baralhos = json.loads(modelos), json.loads(baralhos)
    did, mid = id_do(CONF["baralho"]), id_do(CONF["nota"]["nome"])
    confere(crt == segundos and ver == 11, f"a coleção tem a data da configuração e o esquema 11: {crt}, {ver}")
    confere(list(modelos) == [str(mid)] and FAIXA <= mid < 2 * FAIXA and FAIXA <= did < 2 * FAIXA,
            f"um tipo de nota, com o id do hash do nome: {list(modelos)}")
    tipo = modelos.get(str(mid), {})
    editor = CONF["nota"]["editor"]
    confere(tipo.get("name") == CONF["nota"]["nome"] and tipo.get("did") == did
            and [f["name"] for f in tipo.get("flds", [])] == NOMES
            and all(f["font"] == editor["tipo_de_letra"] and f["size"] == editor["tamanho"]
                    for f in tipo.get("flds", [])),
            f"o tipo de nota tem o nome, os campos em ordem e a letra do editor: {tipo}")
    modelo = (tipo.get("tmpls") or [{}])[0]
    confere(modelo.get("name") == CONF["nota"]["cartao"] and modelo.get("qfmt") == le(FRENTE)
            and modelo.get("afmt") == le(VERSO) and tipo.get("css") == le(ESTILO),
            f"os modelos e o estilo são os dos arquivos, como estão: {modelo}")
    confere(tipo.get("req") == [[0, "any", sorted([LUGAR["pergunta"], LUGAR["assunto"]])]],
            f"a frente precisa de um dos dois campos dela: {tipo.get('req')}")
    confere(baralhos.get(str(did), {}).get("name") == CONF["baralho"] and str(1) in baralhos,
            f"o baralho tem o nome da configuração e o id do hash dele, com o padrão ao lado: {baralhos}")
    notas = banco.execute("SELECT id, guid, mid, mod, tags, flds, sfld, csum FROM notes ORDER BY id").fetchall()
    cartoes = banco.execute("SELECT id, nid, did, due, type, queue FROM cards ORDER BY id").fetchall()
    confere(len(notas) == len(CHEIAS) and len(cartoes) == len(CHEIAS), f"uma nota e um cartão por linha: {len(notas)}")
    base = segundos * 1000
    for k, (linha, nota, cartao) in enumerate(zip(CHEIAS, notas, cartoes)):
        l = LINHAS[k // len(CARTOES)]
        html_da_coluna = {"id": linha["id"], "assunto": l["assunto"][1], "coluna": linha["coluna"],
                          "pergunta": PERGUNTAS[k][1], "resposta": RESPOSTAS[k][1],
                          "palavras_chave": QUEBRA.join(h for _, h in l["cartoes"][linha["coluna"]]),
                          "trecho": l["frases"][linha["coluna"]][1], "fonte": linha["fonte"]}
        campos = [html_da_coluna[c["coluna"]] for c in CAMPOS]
        primeiro = html.unescape(re.sub(r"<[^>]*>", "", campos[0]))
        esperada = (base + k, hashlib.sha256(linha["id"].encode("utf-8")).digest()[:8].hex(), mid, segundos,
                    f" {stem(linha['fonte'])} {identificador(linha['coluna'])} ", SEPARADOR_DE_CAMPOS.join(campos),
                    primeiro, int.from_bytes(hashlib.sha1(primeiro.encode("utf-8")).digest()[:4], "big"))
        confere(nota == esperada, f"a nota {k} segue a regra: {nota}\nno lugar de: {esperada}")
        confere(cartao == (base + k, base + k, did, k + 1, 0, 0),
                f"o cartão {k} é novo, da nota e do baralho: {cartao}")
    guids = [n[1] for n in notas]
    OUTRA_DATA = variante("outra-data", lambda c: c.update(data="2041-01-02T03:04:05+00:00"))
    cod, out = roda("gera_apkg.py", OUTRA_DATA, CHEIO, TRABALHO / "pacote" / "outra-data.apkg", *MODELOS)
    if confere(cod == 0, f"outra data sai com 0: {out}"):
        _, _, outro = abre(TRABALHO / "pacote" / "outra-data.apkg")
        confere((TRABALHO / "pacote" / "outra-data.apkg").read_bytes() != PRIMEIRO
                and [g for g, in outro.execute("SELECT guid FROM notes ORDER BY id")] == guids,
                "outra data dá outros bytes, com os mesmos guids")
    for numero in range(AMOSTRAS):
        nome_do_baralho, nome_da_nota = palavra().capitalize(), palavra().capitalize()
        caminho = TRABALHO / "pacote" / f"nomes-{numero}.apkg"
        cod, out = roda("gera_apkg.py", variante(f"nomes-{numero}", com_nomes(nome_do_baralho, nome_da_nota)),
                        CHEIO, caminho, *MODELOS)
        if confere(cod == 0, f"outros nomes saem com 0: {out}"):
            _, _, outro = abre(caminho)
            modelos_, baralhos_ = (json.loads(v) for v in outro.execute("SELECT models, decks FROM col").fetchone())
            confere(list(modelos_) == [str(id_do(nome_da_nota))] and str(id_do(nome_do_baralho)) in baralhos_,
                    f"com outros nomes, os ids saem do hash de cada um, na faixa: {list(modelos_)}, {list(baralhos_)}")
    SO = grava(TRABALHO / "modelos" / "so.html", f"{{{{{NOMES[LUGAR['assunto']]}}}}}")
    cod, out = roda("gera_apkg.py", CONFIGURACAO, CHEIO, TRABALHO / "pacote" / "so.apkg", "--frente", SO,
                    "--verso", VERSO, "--estilo", ESTILO)
    if confere(cod == 0, f"a frente de um campo só sai com 0: {out}"):
        _, _, so = abre(TRABALHO / "pacote" / "so.apkg")
        req = json.loads(so.execute("SELECT models FROM col").fetchone()[0]).get(str(mid), {}).get("req")
        confere(req == [[0, "all", [LUGAR["assunto"]]]], f"a frente de um campo só precisa dele: {req}")

SEM_MODELO = ["--frente", TRABALHO / "modelos" / "falta.html", "--verso", VERSO, "--estilo", ESTILO]
MODELO_LATIN = ["--frente", FRENTE, "--verso", VERSO, "--estilo",
                grava(TRABALHO / "modelos" / "latin.css", "ç {}".encode("latin-1"))]
PACOTES_RUINS = {
    "marca de ênfase sem par": (com(lambda ls: ls[J].update(resposta=f"{palavra()} ~~ {palavra()}")), MODELOS),
    "etiqueta com espaço": (com(lambda ls: ls[J].update(fonte=f"{palavra()} {palavra()}.md")), MODELOS),
    "id repetido": (com(lambda ls: ls.append(dict(ls[J]))), MODELOS),
    "modelo que falta": (CHEIAS, SEM_MODELO),
    "modelo fora do UTF-8": (CHEIAS, MODELO_LATIN),
}
for numero, (nome, (linhas, modelos)) in enumerate(PACOTES_RUINS.items()):
    saida = TRABALHO / "pacote" / f"ruim-{numero}.apkg"
    cod, out = roda("gera_apkg.py", CONFIGURACAO, grava_csv(TRABALHO / "pacote" / f"ruim-{numero}.csv", linhas), saida,
                    *modelos)
    confere(cod == 2 and out.startswith("ERRO") and not saida.exists(), f"{nome}: sai com 2, sem gravar nada: {out}")
DATA_RUIM = variante("data", lambda c: c.update(data="2031-02-30T00:00:00Z"))
for nome, configuracao, csv_ in (("data que não se lê", DATA_RUIM, CHEIO),
                                 ("CSV com outro cabeçalho", CONFIGURACAO, CSVS_RUINS["CSV com outro cabeçalho"])):
    saida = TRABALHO / "pacote" / f"{identificador(nome)}.apkg"
    cod, out = roda("gera_apkg.py", configuracao, csv_, saida, *MODELOS)
    confere(cod == 2 and out.startswith("ERRO") and not saida.exists(), f"{nome}: sai com 2, sem gravar nada: {out}")

# conferido.py
REGISTRO = TRABALHO / "registro" / "conferido.json"
REGISTRO.parent.mkdir()


def sha(caminho):
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def roda_registro(registro, *outros):
    return roda("conferido.py", CONFIGURACAO, TABELA, registro, *outros)


cod, out = roda_registro(REGISTRO, *PASTAS, "--gravar")
ESPERADO = {"versao_schema": 1, "tabela": sha(TABELA),
            "fontes": {l["fonte"]: sha(l["pasta"] / l["fonte"]) for l in LINHAS}}
GRAVADO = json.loads(le(REGISTRO)) if REGISTRO.is_file() else None
confere(cod == 0 and GRAVADO == ESPERADO and list((GRAVADO or {}).get("fontes", {})) == [l["fonte"] for l in LINHAS],
        f"o --gravar grava o sha256 da tabela e o de cada fonte, da primeira pasta, na ordem da tabela: {out}")
cod, out = roda_registro(REGISTRO, *PASTAS)
confere(cod == 0 and not erros_de(out), f"o registro em dia sai com 0: {out}")
MUDADA = LINHAS[2]["pasta"] / LINHAS[2]["fonte"]
ORIGINAL = MUDADA.read_bytes()
grava(MUDADA, ORIGINAL + palavra().encode("utf-8"))
cod, out = roda_registro(REGISTRO, *PASTAS)
confere(cod == 1 and len(erros_de(out)) == 1 and LINHAS[2]["fonte"] in erros_de(out)[0],
        f"a fonte que mudou: sai com 1, com um ERRO, que a nomeia: {out}")
grava(MUDADA, ORIGINAL)
cod, out = roda("conferido.py", CONFIGURACAO, grava(TRABALHO / "registro" / "tabela.md", le(TABELA) + frase()),
                REGISTRO, *PASTAS)
confere(cod == 1 and len(erros_de(out)) == 1, f"a tabela que mudou: sai com 1, com um ERRO: {out}")
SOBRA = f"{palavra()}.md"
SEM_UMA = {k: v for k, v in ESPERADO["fontes"].items() if k != LINHAS[1]["fonte"]}
COM_SOBRA = dict(ESPERADO["fontes"], **{SOBRA: "0" * 64})
REGISTROS = {
    "a fonte sem registro": (dict(ESPERADO, fontes=SEM_UMA), LINHAS[1]["fonte"]),
    "a fonte do registro que a tabela não nomeia": (dict(ESPERADO, fontes=COM_SOBRA), SOBRA),
}
for numero, (nome, (registro, fonte)) in enumerate(REGISTROS.items()):
    cod, out = roda_registro(grava_json(TRABALHO / "registro" / f"r-{numero}.json", registro), *PASTAS)
    confere(cod == 1 and len(erros_de(out)) == 1 and fonte in erros_de(out)[0],
            f"{nome}: sai com 1, com um ERRO, que a nomeia: {out}")
NA_SEGUNDA = [l["fonte"] for l in LINHAS if l["pasta"] == PASTA_2 and l["fonte"] != LINHAS[0]["fonte"]]
cod, out = roda_registro(REGISTRO, "--pasta", PASTA_1)
confere(cod == 1 and len(erros_de(out)) == len(NA_SEGUNDA)
        and all(any(f in e for e in erros_de(out)) for f in NA_SEGUNDA),
        f"a fonte que nenhuma pasta tem: um ERRO para cada uma: {out}")
ANTES = REGISTRO.read_bytes() if REGISTRO.is_file() else None
cod, out = roda_registro(REGISTRO, "--pasta", PASTA_1, "--gravar")
confere(cod == 2 and out.startswith("ERRO") and ANTES is not None and REGISTRO.read_bytes() == ANTES,
        f"com --gravar, a fonte que falta sai com 2, sem gravar: {out}")
REGISTROS_RUINS = {"registro com campo que o molde não conhece": dict(ESPERADO, **{palavra(): 1}),
                   "registro com sha256 fora da forma": dict(ESPERADO, tabela=palavra())}
for numero, (nome, registro) in enumerate(REGISTROS_RUINS.items()):
    cod, out = roda_registro(grava_json(TRABALHO / "registro" / f"ruim-{numero}.json", registro), *PASTAS)
    confere(cod == 2 and out.startswith("ERRO"), f"{nome}: sai com 2: {out}")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
