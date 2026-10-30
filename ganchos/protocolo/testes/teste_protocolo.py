"""Testes do protocolo.py, com protocolos e eventos inventados: os nomes dos eventos, as
chaves, os modelos das respostas, as ferramentas e os campos de cada uma sao sorteados, com
letras de fora do ASCII, e nada e de um programa de verdade. A semente e fixa (outra vem com
--semente). Os testes conferem o que o modulo faz, nunca uma frase pronta:
  - o protocolo lido da os eventos pelo nome no programa, as chaves, os modelos, a
    ferramenta de terminal, as de busca, os campos das escritas, as de leitura, com os
    numeros, e as que resumem; as listas de ferramentas vazias e os menores numeros de uma
    leitura passam;
  - o evento lido da "antes" ou "fim" e cada parte que ele traz, e so elas; o evento sem o
    nome, com outro nome, com o nome que nao e texto ou noutra chave, que nao e objeto ou
    que nao e JSON e erro;
  - cada resposta e uma copia do modelo dela com o texto no lugar de {texto}, em todo texto
    de dentro dele, tambem nas listas e nos objetos de dentro, com as chaves e o que nao e
    texto como estao; o texto entra como e, com chaves, aspas, barra e quebra de linha; o
    modelo nao muda;
  - e erro, com o que ou onde na mensagem: a versao que nao e a do molde; campo
    desconhecido, que falta, de outro tipo ou vazio, tambem numa ferramenta de uma lista ou
    numa troca; os dois eventos com o mesmo nome; duas partes com a mesma chave; nenhum
    campo de caminho de escrita; a ferramenta repetida numa lista; o modelo sem {texto},
    com outro campo ou que nao e objeto; o numero de uma leitura abaixo do menor;
  - duas leituras e duas respostas dao o mesmo.
Uso:
    python3 -I teste_protocolo.py <pasta do protocolo.py> <pasta de trabalho nova> [--semente N]
Precisa do extrator_comum.py, do extrator, onde o modulo o acha.
"""
import argparse
import copy
import json
import random
import string
import sys
from pathlib import Path

LEITOR = argparse.ArgumentParser(description="Testes do protocolo.py.")
LEITOR.add_argument("peca", type=Path, help="a pasta do protocolo.py")
LEITOR.add_argument("trabalho", type=Path, help="uma pasta de trabalho nova")
LEITOR.add_argument("--semente", type=int, default=3, help="a semente do sorteio")
ARGS = LEITOR.parse_args()
PECA, TRABALHO = ARGS.peca.resolve(), ARGS.trabalho.resolve()
sys.path.insert(0, str(PECA))
import protocolo  # noqa: E402

SORTE = random.Random(ARGS.semente)
ACENTOS = "áçõüé"
LETRAS = string.ascii_lowercase + ACENTOS
LUGAR = "{texto}"  # como o README escreve o lugar do texto num modelo
PARTES = ("evento", "sessao", "ferramenta", "entrada", "pasta", "fim_repetido")  # as chaves, pelo README
VERSAO = json.loads((PECA / "esquemas" / "protocolo.schema.json").read_text(encoding="utf-8"))[
    "properties"]["versao_schema"]["const"]
TIRA = object()  # o valor que, em com(), tira o campo
FALHAS = []
USADOS = set()


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


def nome():
    """Um nome sorteado que nao saiu antes, com uma letra de fora do ASCII."""
    while True:
        sorteado = "".join(SORTE.choice(LETRAS) for _ in range(SORTE.randint(3, 8))) + SORTE.choice(ACENTOS)
        if sorteado not in USADOS:
            USADOS.add(sorteado)
            return sorteado


def modelo():
    """Um modelo de resposta: objetos e listas aninhados, o lugar do texto num texto de um
    objeto de dentro e noutro de uma lista, uma chave com o lugar do texto, que fica como
    esta, um texto sem ele, um numero, um booleano e um nulo."""
    return {nome(): {nome(): f"{nome()} {LUGAR} {nome()}", f"{nome()}{LUGAR}": nome()},
            nome(): [SORTE.randint(0, 99), True, LUGAR, {nome(): None}]}


def inventado():
    return {
        "versao_schema": VERSAO,
        "eventos": {"antes": nome(), "fim": nome()},
        "chaves": {p: nome() for p in PARTES},
        "respostas": {r: modelo() for r in ("nega", "contexto", "trava")},
        "terminal": {"ferramenta": nome(), "campo_comando": nome()},
        "buscas": [{"nome": nome(), "campo_padrao": nome()} for _ in range(2)],
        "escritas": {"campos_caminho": [nome(), nome()],
                     "trocas": {nome(): {"antes": nome(), "depois": nome(), "todas": nome()}},
                     "inteiros": {nome(): nome()}},
        "leituras": [{"nome": nome(), "campo_caminho": nome(), "campo_comeco": nome(), "campo_quantas": nome(),
                      "linhas_sem_limite": SORTE.randint(2, 5000), "primeira_linha": SORTE.randint(1, 3)}],
        "resumos": [nome(), nome()],
    }


def grava(nome_do_arquivo, dados):
    caminho = TRABALHO / nome_do_arquivo
    caminho.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    return caminho


def erro_de(funcao, *argumentos):
    """A mensagem do ErroDeDados da chamada; None quando ela nao da erro."""
    try:
        funcao(*argumentos)
    except protocolo.ErroDeDados as e:
        return str(e)
    return None


def esperado(valor, escrito):
    """O que a resposta tem de ser: o lugar do texto trocado pelo texto em cada texto de
    dentro do valor; as chaves e o que nao e texto como estao."""
    if isinstance(valor, str):
        return valor.replace(LUGAR, escrito)
    if isinstance(valor, dict):
        return {k: esperado(v, escrito) for k, v in valor.items()}
    if isinstance(valor, list):
        return [esperado(v, escrito) for v in valor]
    return valor


TRABALHO.mkdir(parents=True)
CERTO = inventado()
LIDO = protocolo.ler(grava("protocolo.json", CERTO))


def com(caminho, valor):
    """Uma copia do protocolo certo com o valor no caminho ("a/0/b"); TIRA tira o campo."""
    dados = copy.deepcopy(CERTO)
    alvo, partes = dados, caminho.split("/")
    for parte in partes[:-1]:
        alvo = alvo[int(parte)] if isinstance(alvo, list) else alvo[parte]
    ultima = int(partes[-1]) if isinstance(alvo, list) else partes[-1]
    if valor is TIRA:
        del alvo[ultima]
    else:
        alvo[ultima] = valor
    return dados


# ---- o protocolo lido ----

confere(LIDO["eventos"] == {CERTO["eventos"]["antes"]: "antes", CERTO["eventos"]["fim"]: "fim"},
        "os eventos, pelo nome no programa")
confere(LIDO["chaves"] == CERTO["chaves"], "as chaves do evento")
confere(LIDO["respostas"] == CERTO["respostas"], "os modelos das respostas")
confere(LIDO["terminal"] == CERTO["terminal"], "a ferramenta de terminal")
confere(LIDO["buscas"] == {b["nome"]: b["campo_padrao"] for b in CERTO["buscas"]}, "as ferramentas de busca")
confere(LIDO["escritas"] == CERTO["escritas"], "os campos das escritas")
confere(LIDO["leituras"] == {lido["nome"]: {k: v for k, v in lido.items() if k != "nome"}
                             for lido in CERTO["leituras"]}, "as ferramentas de leitura, com os números")
confere(LIDO["resumos"] == CERTO["resumos"], "as ferramentas que resumem")
confere(protocolo.ler(grava("de-novo.json", CERTO)) == LIDO, "duas leituras dão o mesmo")
MINIMOS = com("leituras/0/linhas_sem_limite", 1)
MINIMOS["leituras"][0]["primeira_linha"] = 0
confere(erro_de(protocolo.ler, grava("minimos.json", MINIMOS)) is None, "os menores números de uma leitura passam")
VAZIAS = com("buscas", [])
VAZIAS.update(leituras=[], resumos=[])
VAZIAS["escritas"].update(trocas={}, inteiros={})
confere(erro_de(protocolo.ler, grava("vazias.json", VAZIAS)) is None, "as listas de ferramentas vazias passam")
SO_NA_LISTA = com("respostas/nega", {nome(): [nome(), {nome(): LUGAR}]})
confere(erro_de(protocolo.ler, grava("so-na-lista.json", SO_NA_LISTA)) is None,
        "o lugar do texto só numa lista de dentro do modelo passa")

# ---- o evento ----

CHAVES = CERTO["chaves"]


def evento(nome_do_evento, **partes):
    """O texto JSON de um evento com o nome e as partes dadas, mais uma chave que o protocolo
    nao conhece."""
    dados = {CHAVES["evento"]: nome_do_evento, nome(): nome()}
    dados.update({CHAVES[p]: v for p, v in partes.items()})
    return json.dumps(dados, ensure_ascii=False)


TODAS = {"sessao": nome(), "ferramenta": nome(), "entrada": {nome(): [nome(), SORTE.randint(0, 9)]},
         "pasta": nome(), "fim_repetido": True}
confere(protocolo.le_evento(LIDO, evento(CERTO["eventos"]["antes"], **TODAS)) == {"evento": "antes", **TODAS},
        "o evento de antes, com todas as partes")
ALGUMAS = {"sessao": nome(), "fim_repetido": False}
confere(protocolo.le_evento(LIDO, evento(CERTO["eventos"]["fim"], **ALGUMAS)) == {"evento": "fim", **ALGUMAS},
        "o evento de fim, com as partes que ele traz, e só elas")
confere(protocolo.le_evento(LIDO, evento(CERTO["eventos"]["fim"])) == {"evento": "fim"}, "o evento só com o nome")
for descricao, entrada in [("sem o nome", json.dumps({CHAVES["sessao"]: nome()})),
                           ("com outro nome", evento(nome())),
                           ("com o nome que não é texto", evento(SORTE.randint(0, 9))),
                           ("com o nome noutra chave", json.dumps({nome(): CERTO["eventos"]["antes"]})),
                           ("que não é objeto", json.dumps([CERTO["eventos"]["antes"]])),
                           ("que não é JSON", "{" + nome())]:
    confere(erro_de(protocolo.le_evento, LIDO, entrada) is not None, f"o evento {descricao} é erro")

# ---- as respostas ----

ESCRITO = f'{nome()} {{{nome()}}} {LUGAR} "{nome()}"\n\\ {nome()}'
for qual in ("nega", "contexto", "trava"):
    antes = copy.deepcopy(LIDO["respostas"][qual])
    confere(protocolo.resposta(LIDO, qual, ESCRITO) == esperado(CERTO["respostas"][qual], ESCRITO),
            f"a resposta {qual}: o texto no lugar, em todo texto de dentro, como é")
    confere(LIDO["respostas"][qual] == antes, f"a resposta {qual} não muda o modelo")
confere(protocolo.resposta(LIDO, "nega", ESCRITO) == protocolo.resposta(LIDO, "nega", ESCRITO),
        "duas respostas dão o mesmo")

# ---- os erros ----

ESTRANHO, OUTRO_CAMPO = nome(), nome()
TROCA, INTEIRO = next(iter(CERTO["escritas"]["trocas"])), next(iter(CERTO["escritas"]["inteiros"]))
ERRADOS = [
    ("a versão que não é a do molde", com("versao_schema", VERSAO + 1), "versao_schema"),
    ("um campo desconhecido", com(ESTRANHO, 1), ESTRANHO),
    ("um campo desconhecido numa ferramenta de leitura", com(f"leituras/0/{ESTRANHO}", 1), ESTRANHO),
    ("um campo desconhecido numa troca", com(f"escritas/trocas/{TROCA}/{ESTRANHO}", 1), ESTRANHO),
    ("um campo que falta", com("terminal", TIRA), "terminal"),
    ("uma chave que falta", com("chaves/fim_repetido", TIRA), "fim_repetido"),
    ("um campo que falta numa busca", com("buscas/1/campo_padrao", TIRA), "buscas/1"),
    ("um campo que falta numa troca", com(f"escritas/trocas/{TROCA}/todas", TIRA), TROCA),
    ("o nome de um evento que não é texto", com("eventos/antes", SORTE.randint(0, 9)), "eventos/antes"),
    ("um número de leitura que não é número", com("leituras/0/linhas_sem_limite", "9"), "leituras/0"),
    ("uma lista que não é lista", com("resumos", nome()), "resumos"),
    ("uma chave vazia", com("chaves/sessao", ""), "chaves/sessao"),
    ("uma ferramenta que resume vazia", com("resumos/1", ""), "resumos/1"),
    ("um campo de caminho vazio", com("escritas/campos_caminho/0", ""), "escritas/campos_caminho/0"),
    ("o campo de um inteiro vazio", com(f"escritas/inteiros/{INTEIRO}", ""), INTEIRO),
    ("os dois eventos com o mesmo nome", com("eventos/fim", CERTO["eventos"]["antes"]), CERTO["eventos"]["antes"]),
    ("duas partes com a mesma chave", com("chaves/pasta", CHAVES["sessao"]), CHAVES["sessao"]),
    ("nenhum campo de caminho de escrita", com("escritas/campos_caminho", []), "campos_caminho"),
    ("uma busca repetida", com("buscas/1/nome", CERTO["buscas"][0]["nome"]), CERTO["buscas"][0]["nome"]),
    ("uma leitura repetida", com("leituras", CERTO["leituras"] * 2), CERTO["leituras"][0]["nome"]),
    ("uma ferramenta que resume repetida", com("resumos/1", CERTO["resumos"][0]), CERTO["resumos"][0]),
    ("um modelo sem o lugar do texto", com("respostas/trava", {nome(): nome(), nome(): [1, nome()]}), "trava"),
    ("um modelo com outro campo", com("respostas/contexto", {nome(): f"{LUGAR} {{{OUTRO_CAMPO}}}"}), OUTRO_CAMPO),
    ("um modelo que não é objeto", com("respostas/nega", [LUGAR]), "respostas/nega"),
    ("as linhas sem limite abaixo de 1", com("leituras/0/linhas_sem_limite", 0), "linhas_sem_limite"),
    ("a primeira linha abaixo de 0", com("leituras/0/primeira_linha", -1), "primeira_linha"),
]
for k, (descricao, dados, culpado) in enumerate(ERRADOS):
    mensagem = erro_de(protocolo.ler, grava(f"errado-{k}.json", dados))
    confere(mensagem is not None and culpado in mensagem,
            f"{descricao} é erro, e a mensagem diz {culpado!r}: {mensagem}")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
