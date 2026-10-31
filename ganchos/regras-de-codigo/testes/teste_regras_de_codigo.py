"""Testes de regras_de_codigo.py.

Tudo e inventado aqui: os textos das regras, os formatos sem conferencia, os comandos que
escrevem e os destinos livres; e, sorteados, com letras de fora do ASCII, o prefixo, na
configuracao da leitura do terminal, e o protocolo do programa que roda o gancho (os eventos,
as chaves e as respostas), com a ferramenta de terminal e os campos do caminho de escrita.
Nada e de um projeto real. Os testes conferem o que o gancho faz, nunca uma frase pronta:
  - antes da primeira escrita de uma tarefa, entrega todos os textos de regras (cada um
    de --regras), na resposta de contexto do protocolo, para arquivo de qualquer formato
    fora da lista sem conferencia, sem extensao ou de extensao desconhecida; nas escritas
    seguintes, nada;
  - o arquivo de um formato da lista, em maiusculas ou minusculas, nao recebe as regras,
    nao conta como a primeira escrita e nao vai para o fim;
  - no fim, com arquivos escritos, trava, na resposta que trava, e lista cada um uma vez,
    com as regras e a ordem de conferir; na volta da conferencia, libera e limpa; a tarefa
    seguinte recomeca;
  - no terminal, bloqueia, na resposta que nega, o comando que escreve em arquivo, que roda
    codigo escrito nele ou que nao se le, mostrando a parte que causou o bloqueio, e deixa
    passar o resto, inclusive o que esta entre aspas ou nao esta no lugar de comando; o
    terminal nao anota nada;
  - cada sessao tem a sua anotacao, e o id da sessao nunca vira caminho;
  - configuracao fora do molde (tambem com os prefixos, que vem da leitura do terminal), a
    configuracao da leitura do terminal fora do molde e a falta dela, protocolo fora da
    forma, sessao sem id, evento desconhecido, ferramenta sem campo de caminho conhecido,
    entrada que nao e JSON e a falta de um dos textos do comando (as regras, a ordem de
    conferir, o bloqueio) dao erro.
Uso:
    python3 -I teste_regras_de_codigo.py <pasta de regras_de_codigo.py> <pasta de trabalho nova>
O protocolo inventado vem do protocolo_inventado.py, da pasta de testes do protocolo.
"""
import json
import random
import string
import subprocess
import sys
from pathlib import Path

PECA, TRABALHO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "protocolo" / "testes"))
import protocolo_inventado  # noqa: E402

PROGRAMA = PECA / "regras_de_codigo.py"
FALHAS = []

TEXTOS = {nome: f"conteúdo inventado de {nome}" for nome in
          ("regra_a.txt", "regra_b.txt", "fecho.txt", "veto.txt", "extra.txt")}
REGRAS, EXTRA, FECHO, VETO = ("regra_a.txt", "regra_b.txt"), "extra.txt", "fecho.txt", "veto.txt"
TEXTOS_DO_COMANDO = [("--regras", nome) for nome in REGRAS] + [("--fim", FECHO), ("--bloqueio", VETO)]
PREFIXO = protocolo_inventado.nomes_sorteados(random.Random(3), 1)[0]  # com uma letra de fora do ASCII
TERMINAL = {"versao_schema": 1, "prefixos": [PREFIXO]}  # a configuracao da leitura do terminal
CONFIG = {
    "versao_schema": 1,
    "estado": "marcas",
    "sem_conferencia": [".txa", ".PLN"],
    "terminal": {
        "destinos_livres": ["/ralo/inventado"],
        "sempre_escrevem": ["copiador"],
        "escrevem_com_opcao": {"editor": ["-q", "--no-lugar"]},
        "leem_codigo_sem_arquivo": ["interprete"],
    },
}
CONCHA, ESCRITOR = "Concha", "Escritor"  # a ferramenta de terminal e uma que escreve, inventadas
PROTOCOLO = protocolo_inventado.inventado(
    random.Random(7), {"ferramenta": CONCHA, "campo_comando": "linha"},
    escritas={"campos_caminho": ["alvo_x", "alvo_y"], "trocas": {}, "inteiros": {}})

BLOQUEADOS = [
    "eco > saida", "eco >> saida", "eco &> saida", "eco >| saida", "eco >& saida", "eco 2> saida",
    "eco > 'nome com espaco'", "eco >", "eco>saida",
    "interprete <<FIM\nlinha\nFIM", "eco <<< texto", "eco <<-FIM",
    "copiador saida", "eco | copiador saida", "eco; copiador", "eco && copiador", "eco || copiador",
    "eco\ncopiador", "(copiador)", "VAR=1 copiador", "/caminho/copiador",
    "editor -q alvo", "editor -zq alvo", "editor -q.bak alvo", "editor --no-lugar alvo",
    "editor --no-lugar=1 alvo", "editor alvo -q", f"{PREFIXO} 5 editor -q alvo",
    "interprete", "interprete -z", "eco | interprete", "interprete < arquivo",
    "x=$(copiador)", 'eco "$(copiador)"', "eco `copiador`", 'eco "`copiador`"',
    'eco "a $(eco "b $(copiador)")"',
    "eco 'sem fim", 'eco "sem fim', 'eco "$(sem fim"', "eco `sem fim",
]

LIVRES = [
    "eco", "eco > /ralo/inventado", "eco 2>/ralo/inventado", "eco &> /ralo/inventado",
    "eco 2>&1", "eco >&2", "eco 2>&-", "eco '>' saida", 'eco ">>" saida', "eco \\> saida",
    "eco < entrada", "interprete arquivo", "interprete -z arquivo", "editor -z alvo",
    "editor --outra alvo", "editor --no-lugarx alvo", "eco copiador", "eco editor -q",
    "eco | eco", 'eco "texto com # ; | > e <<"', "eco # copiador > saida",
    'eco -m "linha um" -m "linha dois"', "VAR=1 eco", "eco a\\\n  b",
]

FORA_DO_MOLDE = {
    "campo desconhecido": dict(CONFIG, outro=1),
    "campo que falta": {chave: valor for chave, valor in CONFIG.items() if chave != "estado"},
    "campo desconhecido no terminal": dict(CONFIG, terminal=dict(CONFIG["terminal"], outro=[])),
    "prefixos no terminal": dict(CONFIG, terminal=dict(CONFIG["terminal"], prefixos=[PREFIXO])),
    "tipo errado": dict(CONFIG, estado=1),
    "tipo errado dentro de lista": dict(CONFIG, sem_conferencia=[".txa", 1]),
    "versao diferente": dict(CONFIG, versao_schema=CONFIG["versao_schema"] + 1),
    "nome vazio": dict(CONFIG, estado=""),
    "formatos que nao sao lista": dict(CONFIG, sem_conferencia=".txa"),
    "formato vazio": dict(CONFIG, sem_conferencia=[""]),
    "sem a lista de formatos": {chave: valor for chave, valor in CONFIG.items() if chave != "sem_conferencia"},
    "opcoes que nao sao lista": dict(CONFIG, terminal=dict(CONFIG["terminal"], escrevem_com_opcao={"editor": "-q"})),
}


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


def grava_json(nome, dados):
    caminho = TRABALHO / nome
    caminho.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    return caminho


def rodar(entrada, config, extras=(), protocolo=None, textos=None, leitura=None):
    """O gancho com os textos do comando (os dados, ou os de sempre), as regras a mais e a configuracao da leitura do
    terminal: a dada, a de sempre ou, com leitura falsa, nenhuma."""
    argumentos = [sys.executable, "-I", str(PROGRAMA), "--config", str(config),
                  "--protocolo", str(protocolo or ARQUIVO_DO_PROTOCOLO)]
    if leitura is not False:
        argumentos += ["--terminal", str(leitura or ARQUIVO_DO_TERMINAL)]
    for opcao, nome in TEXTOS_DO_COMANDO if textos is None else textos:
        argumentos += [opcao, str(TRABALHO / nome)]
    for extra in extras:
        argumentos += ["--regras", str(TRABALHO / extra)]
    return subprocess.run(argumentos, input=entrada, capture_output=True, text=True)


def saida(entrada, extras=()):
    """O que o gancho escreve; falha quando ele sai com erro."""
    resultado = rodar(entrada, CONFIGURACAO, extras)
    confere(resultado.returncode == 0, f"{entrada}: saiu com {resultado.returncode}: {resultado.stderr.strip()}")
    return resultado.stdout


def da_erro(entrada, config=None, protocolo=None, leitura=None):
    return rodar(entrada, config or CONFIGURACAO, protocolo=protocolo, leitura=leitura).returncode != 0


def escrita(sessao, caminho, campo="alvo_x"):
    return protocolo_inventado.evento(PROTOCOLO, "antes", sessao=sessao, ferramenta=ESCRITOR,
                                      entrada={campo: caminho})


def terminal(sessao, linha):
    return protocolo_inventado.evento(PROTOCOLO, "antes", sessao=sessao, ferramenta=CONCHA, entrada={"linha": linha})


def fim(sessao, ativo=False):
    return protocolo_inventado.evento(PROTOCOLO, "fim", sessao=sessao, fim_repetido=ativo)


def contexto(escrito):
    return protocolo_inventado.texto_da(PROTOCOLO, "contexto", escrito) or ""


def bloqueio(escrito):
    return protocolo_inventado.texto_da(PROTOCOLO, "nega", escrito)


def trava(escrito):
    return protocolo_inventado.texto_da(PROTOCOLO, "trava", escrito)


TRABALHO.mkdir(parents=True)
for nome, texto in TEXTOS.items():
    (TRABALHO / nome).write_text(texto, encoding="utf-8")
CONFIGURACAO = grava_json("cfg.json", CONFIG)
ARQUIVO_DO_TERMINAL = grava_json("terminal.json", TERMINAL)
ARQUIVO_DO_PROTOCOLO = grava_json("protocolo.json", PROTOCOLO)

# começo: escrita de arquivo
primeira = saida(escrita("regras", "/a/b"), extras=[EXTRA])
for nome in REGRAS + (EXTRA,):
    confere(TEXTOS[nome] in contexto(primeira), f"a primeira escrita entrega {nome}")
confere(bloqueio(primeira) is None, "a escrita nunca e bloqueada")
confere(saida(escrita("regras", "/a/c")) == "", "a segunda escrita da tarefa nao repete as regras")
for numero, caminho in enumerate(["/a/x.md", "/a/y", "/a/z.json", "/a/.oculto", "/a/w.ABC"]):
    confere(contexto(saida(escrita(f"formato-{numero}", caminho))), f"{caminho} conta como escrita")
for numero, caminho in enumerate(["/a/nota.txa", "/a/nota.TXA", "/a/tabela.pln", "/a/b.c/tabela.Pln"]):
    sessao = f"sem-conferencia-{numero}"
    confere(saida(escrita(sessao, caminho)) == "", f"{caminho} não recebe as regras")
    confere(saida(fim(sessao)) == "", f"{caminho} não trava o fim")
confere(saida(escrita("texto-antes", "/a/nota.txa")) == "" and contexto(saida(escrita("texto-antes", "/a/c.x"))),
        "as regras saem na primeira escrita que pede a conferência, mesmo depois de um texto")
saida(escrita("misto", "/a/nota.txa"))
saida(escrita("misto", "/a/codigo.x"))
motivo = trava(saida(fim("misto"))) or ""
confere("/a/codigo.x" in motivo and "/a/nota.txa" not in motivo, "o fim lista só os arquivos que pedem a conferência")
confere(contexto(saida(escrita("outro-campo", "/a/b", campo="alvo_y"))), "o segundo campo de caminho conta")
confere("/a/b" in (trava(saida(fim("outro-campo"))) or ""), "o arquivo do segundo campo vai para o fim")
confere(contexto(saida(escrita("sessao-1", "/a/b"))) and contexto(saida(escrita("sessao-2", "/a/b"))),
        "cada sessao tem a sua tarefa")
confere(da_erro(escrita("sem-campo", "/a/b", campo="desconhecido")),
        "ferramenta sem campo de caminho conhecido da erro")

# fim
for caminho in ("/a/um", "/a/dois", "/a/um"):
    saida(escrita("fim", caminho))
motivo = trava(saida(fim("fim"), extras=[EXTRA]))
confere(motivo is not None, "o fim com arquivos escritos trava")
motivo = motivo or ""
confere(motivo.count("/a/um") == 1 and motivo.count("/a/dois") == 1, "o fim lista cada arquivo uma vez")
for nome in REGRAS + (EXTRA, FECHO):
    confere(TEXTOS[nome] in motivo, f"o fim traz {nome}")
confere(saida(fim("fim")) == "", "depois de travar, o fim seguinte libera")
saida(escrita("volta", "/a/um"))
confere(saida(fim("volta", ativo=True)) == "", "na volta da conferencia o fim libera")
confere(saida(fim("volta")) == "", "a volta da conferencia limpa a anotacao")
confere(saida(fim("sem-escrita")) == "", "o fim sem escrita nao trava")
saida(escrita("recomeco", "/a/um"))
saida(fim("recomeco"))
confere(contexto(saida(escrita("recomeco", "/a/dois"))), "a tarefa seguinte recomeca com as regras")

# terminal
for linha in BLOQUEADOS:
    motivo = bloqueio(saida(terminal("terminal", linha)))
    confere(motivo is not None and TEXTOS[VETO] in motivo, f"bloqueia {linha!r}")
for linha in LIVRES:
    confere(saida(terminal("terminal", linha)) == "", f"deixa passar {linha!r}")
confere("-q" in (bloqueio(saida(terminal("terminal", "eco ok; editor -q alvo"))) or ""),
        "o bloqueio mostra a parte que escreve")
confere(saida(fim("terminal")) == "", "o terminal nao anota nada")

# entrada
confere(da_erro(escrita("", "/a/b")), "a sessao sem id da erro")
for sessao in ("../fora", "a/b", "..", ".oculta"):
    confere(contexto(saida(escrita(sessao, "/a/b"))), f"a sessao {sessao!r} tem a sua tarefa")
NOTAS = TRABALHO / CONFIG["estado"]
confere(not (TRABALHO / "fora").exists() and all(
    len(n.name) == 64 and set(n.name) <= set(string.hexdigits.lower()) for n in NOTAS.iterdir()),
    "o id da sessao nunca vira caminho")
confere(da_erro(json.dumps({PROTOCOLO["chaves"]["evento"]: "EventoInventado", PROTOCOLO["chaves"]["sessao"]: "e"})),
        "evento desconhecido da erro")
confere(da_erro("isto nao e json"), "entrada que nao e JSON da erro")
for numero, (caso, dados) in enumerate(FORA_DO_MOLDE.items()):
    confere(da_erro(fim("molde"), grava_json(f"fora-do-molde-{numero}.json", dados)),
            f"configuracao com {caso} da erro")
confere(da_erro(fim("leitura"), leitura=grava_json("terminal-sem-prefixos.json", {"versao_schema": 1})),
        "configuracao da leitura do terminal fora do molde da erro")
confere(da_erro(fim("leitura"), leitura=False), "sem a configuracao da leitura do terminal da erro")
SEM_RESPOSTAS = {chave: valor for chave, valor in PROTOCOLO.items() if chave != "respostas"}
confere(da_erro(fim("protocolo"), protocolo=grava_json("protocolo-sem-respostas.json", SEM_RESPOSTAS)),
        "protocolo fora da forma da erro")
for opcao in ("--regras", "--fim", "--bloqueio"):
    sem_ele = [(o, nome) for o, nome in TEXTOS_DO_COMANDO if o != opcao]
    confere(rodar(fim("textos"), CONFIGURACAO, textos=sem_ele).returncode != 0, f"sem o texto de {opcao} da erro")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
