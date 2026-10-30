"""Testes do leitura_do_terminal.py, com comandos inventados: nenhum nome de comando, prefixo
ou opcao e de um programa de verdade. Conferem o que a leitura da, nunca uma frase pronta:
  - as palavras de cada comando simples: aspas simples e duplas, escape, continuacao de
    linha, comentario so no comeco de palavra, operadores com e sem espaco em volta, e os
    alvos de redirecionamento fora das palavras;
  - as palavras que rodam como comando: a primeira, menos a atribuicao, e todas as que vem
    depois de um prefixo, tambem dado com o caminho; o argumento, nao;
  - os comandos de dentro de $( ) e de crases, tambem entre aspas e um dentro do outro, na
    ordem: o de fora e, depois, cada um de dentro;
  - o comando com aspa, crase ou substituicao sem fechar e ilegivel, e o resto nao;
  - a opcao curta, sozinha ou junto de outras, e a longa, sozinha ou com =valor, batem; a
    parecida nao;
  - quais operadores sao de redirecionamento;
  - duas leituras dao o mesmo.
Uso:
    python3 -I teste_leitura_do_terminal.py <pasta do leitura_do_terminal.py> <pasta de trabalho nova>
A pasta de trabalho nao e usada: a leitura nao grava nada.
"""
import sys
from pathlib import Path

PECA = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(PECA))
import leitura_do_terminal as leitura  # noqa: E402

FALHAS = []
PREFIXOS = {"embrulho", "-faz"}  # prefixos inventados: um comando e uma opcao

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
    """As palavras que rodam como comando, do comando e dos de dentro dele, na ordem."""
    return [p[i] for p in simples(comando) for i in leitura.posicoes_de_comando(p, PREFIXOS)]


def ilegivel(comando):
    try:
        list(leitura.lidos(comando))
    except leitura.ComandoIlegivel:
        return True
    return False


def tudo():
    """O que a leitura da para todos os casos, para comparar duas leituras."""
    return ([simples(c) for c in PALAVRAS], [comandos(c) for c in COMANDOS],
            [ilegivel(c) for c in ILEGIVEIS + LEGIVEIS])


for comando, esperado in PALAVRAS.items():
    confere(simples(comando) == esperado, f"as palavras de {comando!r}: {simples(comando)!r}")
for comando, esperado in COMANDOS.items():
    confere(comandos(comando) == esperado, f"os comandos de {comando!r}: {comandos(comando)!r}")
for comando in ILEGIVEIS:
    confere(ilegivel(comando), f"{comando!r} é ilegível")
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
