"""Testes do leitura_do_terminal.py, com comandos inventados: nenhum nome de comando, prefixo
ou opcao e de um programa de verdade. Conferem o que a leitura da, nunca uma frase pronta:
  - os prefixos da configuracao, lidos de volta, entre eles os sorteados, com letras de fora
    do ASCII, cada um fazendo comando a palavra que vem depois dele; a configuracao fora do
    molde (com campo desconhecido, sem os prefixos, com um prefixo vazio ou que nao e texto,
    com os prefixos fora de uma lista ou com outra versao) e erro, que diz o arquivo e o
    caminho do valor; a configuracao da peca segue o molde;
  - as palavras de cada comando simples: aspas simples e duplas, escape, continuacao de
    linha, comentario so no comeco de palavra, operadores com e sem espaco em volta, e os
    alvos de redirecionamento fora das palavras;
  - as palavras que rodam como comando: a primeira, menos a atribuicao, e todas as que vem
    depois de um prefixo, tambem dado com o caminho; o argumento, nao;
  - as palavras depois de um comando de uma ou mais palavras: a primeira pelo nome, tambem
    com o caminho, e as outras na ordem, com outras palavras no meio; nada quando as
    palavras nao comecam por ele, tambem com as palavras dele fora de ordem;
  - os comandos procurados que um comando roda: cada um, com o indice, as palavras depois
    dele e a parte do comando simples, depois de um operador, de um prefixo e dentro de $( )
    e de crases, na ordem do comando; dois procurados no mesmo lugar; nada quando o
    procurado e so um argumento; e o comando ilegivel e erro;
  - os comandos de dentro de $( ) e de crases, tambem entre aspas e um dentro do outro, na
    ordem: o de fora e, depois, cada um de dentro;
  - o comando com aspa, crase ou substituicao sem fechar e ilegivel, e o resto nao;
  - a opcao curta, sozinha ou junto de outras, e a longa, sozinha ou com =valor, batem; a
    parecida nao;
  - quais operadores sao de redirecionamento;
  - duas leituras dao o mesmo.
Uso:
    python3 -I teste_leitura_do_terminal.py <pasta do leitura_do_terminal.py> <pasta de trabalho nova>
Na pasta de trabalho ficam as configuracoes inventadas. Precisa do extrator_comum.py, do
extrator, onde a leitura o acha: na prateleira, ou na pasta irma da copia. Os nomes sorteados
vem do protocolo_inventado.py, da pasta de testes do protocolo.
"""
import json
import random
import sys
from pathlib import Path

PECA, TRABALHO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
sys.path.insert(0, str(PECA))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "protocolo" / "testes"))
import leitura_do_terminal as leitura  # noqa: E402
import protocolo_inventado  # noqa: E402
from extrator_comum import ErroDeDados  # noqa: E402 -- no caminho que o leitura_do_terminal.py poe

FALHAS = []
SORTE = random.Random(3)  # o sorteio e o mesmo em toda rodada
NOMES = protocolo_inventado.nomes_sorteados(SORTE, SORTE.randint(3, 6))  # cada um com uma letra de fora do ASCII
OUTRO = NOMES.pop()  # um campo que o molde nao conhece
SORTEADOS = NOMES[:-1] + [f"-{NOMES[-1]}"]  # prefixos sorteados: comandos e uma opcao, como -exec
PREFIXOS = {"embrulho", "-faz"} | set(SORTEADOS)  # os dos casos abaixo, inventados, e os sorteados
CONFIG = {"versao_schema": 1, "prefixos": SORTE.sample(sorted(PREFIXOS), len(PREFIXOS))}
ESTRAGADO = SORTE.randrange(len(CONFIG["prefixos"]))  # a posicao do prefixo que sai do molde


def com_prefixo(valor):
    """A configuracao com o valor no lugar de um dos prefixos."""
    prefixos = list(CONFIG["prefixos"])
    prefixos[ESTRAGADO] = valor
    return dict(CONFIG, prefixos=prefixos)


FORA_DO_MOLDE = {  # caso: (configuracao, o caminho do valor fora do molde)
    "campo desconhecido": ({**CONFIG, OUTRO: SORTEADOS}, f"/{OUTRO}"),
    "sem os prefixos": ({"versao_schema": CONFIG["versao_schema"]}, "/prefixos"),
    "prefixo vazio": (com_prefixo(""), f"/prefixos/{ESTRAGADO}"),
    "prefixo que não é texto": (com_prefixo(SORTE.randint(1, 9)), f"/prefixos/{ESTRAGADO}"),
    "prefixos fora de uma lista": (dict(CONFIG, prefixos=SORTEADOS[0]), "/prefixos"),
    "outra versão": (dict(CONFIG, versao_schema=CONFIG["versao_schema"] + 1), "/versao_schema"),
}

PALAVRAS = {  # comando -> as palavras de cada comando simples dele
    "eco a b": [["eco", "a", "b"]],
    "eco 'a b' \"c d\"": [["eco", "a b", "c d"]],
    "eco a\\ b": [["eco", "a b"]],
    "eco a\\\n  b": [["eco", "a", "b"]],
    "eco a # b c": [["eco", "a"]],
    "eco a#b": [["eco", "a#b"]],
    "eco a > b c": [["eco", "a", "c"]],
    "eco a>b": [["eco", "a"]],
    "eco a | ti b; te c && to d || tu e\nta f": [["eco", "a"], ["ti", "b"], ["te", "c"], ["to", "d"], ["tu", "e"],
                                                  ["ta", "f"]],
}

COMANDOS = {  # comando -> as palavras que rodam como comando, nele e nos de dentro dele
    "eco ti": ["eco"],
    "VAR=1 eco a": ["eco"],
    "embrulho 5 ti": ["embrulho", "5", "ti"],
    "/caminho/embrulho ti": ["/caminho/embrulho", "ti"],
    "ache . -faz ti {} ;": ["ache", "ti", "{}"],
    "/caminho/ti a": ["/caminho/ti"],
    "eco 'a; ti'": ["eco"],
    "eco \"a; ti\"": ["eco"],
    "eco \"$(ti a)\"": ["eco", "ti"],
    "eco `ti a`": ["eco", "ti"],
    "eco \"`ti a`\"": ["eco", "ti"],
    "eco \"a $(te \"b $(ti c)\")\"": ["eco", "te", "ti"],
    "x=$(ti a)": ["ti"],
    "ti \"$(te a)\" `to b`": ["ti", "te", "to"],
    "eco # ti; te": ["eco"],
}

DEPOIS = [  # (comando, palavras, as palavras depois do comando, ou None quando elas nao comecam por ele)
    (["ti"], ["ti", "a", "b"], ["a", "b"]),
    (["ti"], ["/caminho/ti", "a"], ["a"]),
    (["ti"], ["tio", "a"], None),
    (["ti"], ["eco", "ti"], None),
    (["ti"], [], None),
    (["te", "ti"], ["te", "ti", "a"], ["a"]),
    (["te", "ti"], ["te", "-C", "d", "ti", "a"], ["a"]),
    (["te", "ti"], ["te", "ta"], None),
    (["te", "ti"], ["ti", "te"], None),
    (["te", "ti", "to"], ["te", "x", "ti", "y", "to", "z"], ["z"]),
    (["te", "ti", "to"], ["te", "to", "ti"], None),
]

ACHADOS = [  # (comando, procurados, o que se acha: (indice, seguintes, parte), na ordem)
    ("eco a; ti b c", [["ti"]], [(0, ["b", "c"], "ti b c")]),
    ("ti a | to b", [["to"], ["ti"]], [(1, ["a"], "ti a"), (0, ["b"], "to b")]),
    ("embrulho 5 ti a", [["ti"]], [(0, ["a"], "ti a")]),
    ("eco ti a", [["ti"]], []),
    ("eco \"$(te -C d ti a)\"", [["ti"], ["te", "ti"]], [(1, ["a"], "te -C d ti a")]),
    ("te ti a", [["te"], ["te", "ti"]], [(0, ["ti", "a"], "te ti a"), (1, ["a"], "te ti a")]),
    ("eco `ti a` \"$(to b)\"", [["ti"], ["to"]], [(0, ["a"], "ti a"), (1, ["b"], "to b")]),
]

ILEGIVEIS = ["eco 'a", "eco \"a", "eco `a", "eco \"$(a\"", "eco \"$(a 'b)\""]
LEGIVEIS = ["eco 'a' \"b\" `c` \"$(d)\"", "eco \"a 'b' c\"", "eco 'a \"b\" c'"]

OPCOES = [  # (opcao, palavra, se bate)
    ("-q", "-q", True), ("-q", "-zq", True), ("-q", "-q.bak", True), ("-q", "-z", False), ("-q", "q", False),
    ("-q", "--q", False), ("-q", "-9q", False), ("--no-lugar", "--no-lugar", True),
    ("--no-lugar", "--no-lugar=1", True), ("--no-lugar", "--no-lugarx", False), ("--no-lugar", "-n", False),
]

REDIRECIONAMENTOS = [(">", True), (">>", True), ("<", True), (">&", True), ("<(", False), ("|", False),
                     ("&&", False), (";", False)]


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)


def simples(comando):
    """As palavras de cada comando simples, do comando e dos de dentro dele, na ordem."""
    return [palavras for _, todos in leitura.lidos(comando) for palavras in todos]


def comandos(comando):
    """As palavras que rodam como comando, do comando e dos de dentro dele, na ordem, com os prefixos lidos."""
    return [p[i] for p in simples(comando) for i in leitura.posicoes_de_comando(p, LIDOS)]


def achados(comando, procurados):
    return list(leitura.comandos_achados(comando, procurados, LIDOS))


def grava(nome_do_arquivo, dados):
    """O arquivo novo, na pasta de trabalho, com os dados em JSON."""
    arquivo = TRABALHO / nome_do_arquivo
    arquivo.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    return arquivo


def erro_ao_ler(arquivo):
    """A mensagem do erro ao ler os prefixos da configuracao do arquivo; None quando ela se le."""
    try:
        leitura.prefixos_do_terminal(arquivo)
    except ErroDeDados as e:
        return str(e)
    return None


def ilegivel(comando, ler=lambda c: list(leitura.lidos(c))):
    try:
        ler(comando)
    except leitura.ComandoIlegivel:
        return True
    return False


def tudo():
    """O que a leitura da para todos os casos, para comparar duas leituras."""
    return (sorted(leitura.prefixos_do_terminal(ARQUIVO)), [simples(c) for c in PALAVRAS],
            [comandos(c) for c in COMANDOS], [leitura.depois_do_comando(c, p) for c, p, _ in DEPOIS],
            [achados(c, p) for c, p, _ in ACHADOS], [ilegivel(c) for c in ILEGIVEIS + LEGIVEIS])


TRABALHO.mkdir(parents=True)
ARQUIVO = grava("terminal.json", CONFIG)
LIDOS = leitura.prefixos_do_terminal(ARQUIVO)
confere(LIDOS == PREFIXOS, f"os prefixos lidos da configuração: {sorted(LIDOS)}")
for prefixo in SORTEADOS:
    confere(comandos(f"eco . {prefixo} ti") == ["eco", "ti"], f"o prefixo sorteado {prefixo!r} faz comando o seguinte")
for numero, (caso, (dados, caminho)) in enumerate(FORA_DO_MOLDE.items()):
    arquivo = grava(f"fora-do-molde-{numero}.json", dados)
    mensagem = erro_ao_ler(arquivo)
    confere(mensagem is not None and arquivo.name in mensagem and caminho in mensagem,
            f"a configuração com {caso} é erro, que diz o arquivo e o caminho {caminho}: {mensagem}")
confere(erro_ao_ler(PECA / "configuracao.json") is None, "a configuração da peça segue o molde")
for comando, esperado in PALAVRAS.items():
    confere(simples(comando) == esperado, f"as palavras de {comando!r}: {simples(comando)!r}")
for comando, esperado in COMANDOS.items():
    confere(comandos(comando) == esperado, f"os comandos de {comando!r}: {comandos(comando)!r}")
for comando, palavras, esperado in DEPOIS:
    achado = leitura.depois_do_comando(comando, palavras)
    confere(achado == esperado, f"depois de {comando!r} em {palavras!r}: {achado!r}")
for comando, procurados, esperado in ACHADOS:
    confere(achados(comando, procurados) == esperado,
            f"os procurados {procurados!r} em {comando!r}: {achados(comando, procurados)!r}")
for comando in ILEGIVEIS:
    confere(ilegivel(comando), f"{comando!r} é ilegível")
    confere(ilegivel(comando, lambda c: achados(c, [["eco"]])), f"{comando!r} é ilegível ao achar os procurados")
for comando in LEGIVEIS:
    confere(not ilegivel(comando), f"{comando!r} se lê")
for opcao, palavra, bate in OPCOES:
    confere(leitura.opcao_bate(opcao, palavra) == bate, f"{opcao!r} em {palavra!r}: {not bate}")
for operador, redireciona in REDIRECIONAMENTOS:
    confere(leitura.eh_redirecionamento(operador) == redireciona, f"{operador!r} é redirecionamento: {not redireciona}")
confere(tudo() == tudo(), "duas leituras dão o mesmo")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
