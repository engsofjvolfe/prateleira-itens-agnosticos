"""Testes de busca_por_palavra.py.

Tudo e inventado aqui: os comandos de busca, as opcoes, o padrao livre, o prefixo, o texto do
motivo, o arquivo da busca exata e a forma dos padroes dela; e o protocolo do programa que
roda o gancho, sorteado (os eventos, as chaves e as respostas), com a ferramenta de terminal
e a de busca. Nada e de um projeto real nem de um programa de verdade. Os testes conferem o
que o gancho faz, nunca uma frase pronta:
  - no terminal, bloqueia a busca com padrao que nao e livre: dado sem opcao; com a opcao
    curta sozinha, junto de outras ou com o valor colado; com a longa, com o valor depois do
    = ou na palavra seguinte; repetida; e o padrao de uma opcao que vem depois de um livre
    dado sem opcao. Bloqueia tambem a busca com os padroes tirados de um arquivo e a busca
    sem padrao; a busca depois de um operador, de um prefixo e de uma atribuicao, com o
    caminho e dentro de $( ) ou de crases; a busca de duas palavras, tambem com outras no
    meio; e o comando que nao se le;
  - deixa passar a busca so com o padrao livre, dado dessas formas, e o comando que nao e
    uma busca, mesmo com o nome dela como argumento, entre aspas ou num comentario;
  - com --exatas, deixa passar a busca exata: cada padrao inteiro na forma, dado dessas
    formas, e so o arquivo da exata, com o caminho a partir da pasta do evento, relativo ou
    inteiro, tambem depois de --, repetido e nas buscas sem opcao de padrao e de duas
    palavras; e o padrao livre continua passando. Bloqueia o padrao fora da forma ou so com
    parte dela, a busca sem arquivo, com outro arquivo, com um a mais (tambem depois de --,
    ou o valor de uma opcao que o gancho nao conhece), a que mistura o padrao exato com uma
    palavra ou com o livre, a com os padroes tirados de um arquivo e a de outra pasta, que
    acha outro arquivo com o mesmo nome. Sem --exatas, a busca exata e bloqueada, e a
    ferramenta de busca nao muda com ele;
  - com --exatas de dois arquivos, cada um com a sua forma, deixa passar a busca exata de
    cada um e bloqueia a busca num deles com a forma do outro e a que le os dois;
  - na ferramenta de busca, bloqueia o padrao que nao e livre e a busca sem padrao, e deixa
    passar o livre;
  - o bloqueio e a resposta que nega do protocolo, com o texto do motivo e a parte que
    bloqueou;
  - configuracao com campo desconhecido ou que falta, protocolo fora da forma, a falta do
    texto do motivo, evento de fim, evento desconhecido, ferramenta desconhecida, entrada
    que nao e JSON e, com --exatas, o arquivo que nao existe, tambem o segundo de dois, e a
    forma que nao e expressao regular dao erro;
  - duas rodadas dao o mesmo.
Uso:
    python3 -I teste_busca_por_palavra.py <pasta de busca_por_palavra.py> <pasta de trabalho nova>
Precisa do extrator_comum.py, do extrator, do leitura_do_terminal.py, da leitura-do-terminal,
e do protocolo.py, do protocolo, onde o gancho os acha: na prateleira, ou nas pastas irmas da
copia. O protocolo inventado vem do protocolo_inventado.py, da pasta de testes do protocolo.
"""
import json
import random
import subprocess
import sys
from pathlib import Path

PECA, TRABALHO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "protocolo" / "testes"))
import protocolo_inventado  # noqa: E402

PROGRAMA = PECA / "busca_por_palavra.py"
FALHAS = []

MOTIVO, TEXTO = "aviso.txt", "conteúdo inventado do aviso"
LIVRE = "^=="
CONFIG = {
    "versao_schema": 1,
    "padroes_livres": [LIVRE],
    "prefixos": ["embrulho"],
    "buscas": [
        {"comando": "acha", "opcoes_do_padrao": ["-p", "--padrao"], "opcoes_de_arquivo": ["-a", "--arquivo"]},
        {"comando": "versao acha", "opcoes_do_padrao": ["-p"], "opcoes_de_arquivo": []},
        {"comando": "cata", "opcoes_do_padrao": [], "opcoes_de_arquivo": []},
    ],
}
CONCHA, LUPA = "Concha", "Lupa"  # a ferramenta de terminal e a de busca inventadas
PROTOCOLO = protocolo_inventado.inventado(random.Random(5), {"ferramenta": CONCHA, "campo_comando": "linha"},
                                          buscas=[{"nome": LUPA, "campo_padrao": "termo"}])
INDICE, FORMA = "indice-inventado.txt", "%[0-9]+(:[0-9]+)*%"  # o arquivo da busca exata e a forma dos padroes dela
OUTRO_INDICE, OUTRA_FORMA = "outro-indice-inventado.txt", "#[a-z]+#"  # outro arquivo de busca exata, e a forma dele
NAO_EXISTE = "nao-existe.txt"  # um arquivo de busca exata que nao existe
SUB = "sub"  # uma pasta dentro da de trabalho, outra de onde o comando roda

L = f"'{LIVRE}'"  # o padrao livre, entre aspas, como se escreve no terminal
BARRADOS = [
    "acha palavra x", "acha -n palavra x", "acha -p palavra x", "acha -np palavra x", "acha -ppalavra x",
    "acha --padrao=palavra x", "acha --padrao palavra x", f"acha -p {L} -p palavra x", f"acha {L} -p palavra",
    "acha -a lista x", "acha --arquivo=lista x", f"acha -a {L} x", "acha", "acha -p", "acha -n",
    "eco x | acha palavra", "eco x; acha palavra", "embrulho acha palavra", "/caminho/acha palavra",
    "eco \"$(acha palavra)\"", "eco `acha palavra`", "VAR=1 acha palavra",
    "versao acha palavra", "versao -C d acha palavra", "cata palavra", "eco 'sem fim",
]
LIVRES = [
    f"acha {L} x", f"acha -n {L} x y", f"acha -p {L} x", f"acha --padrao={L} x", f"acha --padrao {L} x",
    f"acha -p{L} x", f"acha -np {L} x", f"versao acha {L}", f"cata {L}",
    "eco acha palavra", "eco 'acha palavra'", "versao lista", "eco x", "achado palavra", "eco x # acha palavra",
]
NA_FERRAMENTA = [({"termo": "palavra"}, True), ({"termo": LIVRE}, False), ({"outro": "x"}, True)]
EXATAS_PASSAM = [  # (comando, pasta de onde ele roda, dentro da de trabalho)
    (f"acha -p '%3%' {INDICE}", "."), (f"acha -p '%3%' -p '%3:12%' -p '%3:12:1%' {INDICE}", "."),
    (f"acha '%3:12%' {INDICE}", "."), (f"acha -n -p '%3%' {INDICE}", "."), (f"acha -p'%3%' {INDICE}", "."),
    (f"acha --padrao='%3%' {INDICE} {INDICE}", "."), (f"acha --padrao '%3%' -- {INDICE}", "."),
    (f"acha -p '%3%' ../{INDICE}", SUB), (f"acha -p '%3%' '{TRABALHO / INDICE}'", SUB),
    (f"cata '%3%' {INDICE}", "."), (f"versao acha -p '%3%' {INDICE}", "."), (f"acha {L} outro.txt", "."),
]
EXATAS_BARRADAS = [
    (f"acha -p '%palavra%' {INDICE}", "."), (f"acha -p '%3%x' {INDICE}", "."), (f"acha -p 'x%3%' {INDICE}", "."),
    ("acha -p '%3%' outro.txt", "."), ("acha -p '%3%'", "."), (f"acha -p '%3%' {INDICE} outro.txt", "."),
    (f"acha -p '%3%' {INDICE} -- -outro", "."), (f"acha -m 5 -p '%3%' {INDICE}", "."),
    (f"acha -p '%3%' -p palavra {INDICE}", "."), (f"acha -p '%3%' -p {L} {INDICE}", "."),
    (f"acha -a lista {INDICE}", "."), (f"acha -p '%3%' {INDICE}", SUB), ("acha -p", "."),
]
DUAS_EXATAS_PASSAM = [(f"acha -p '%3%' {INDICE}", "."), (f"acha -p '#abc#' {OUTRO_INDICE}", "."),
                      (f"acha -p '#abc#' -p '#de#' {OUTRO_INDICE}", ".")]
DUAS_EXATAS_BARRADAS = [(f"acha -p '#abc#' {INDICE}", "."), (f"acha -p '%3%' {OUTRO_INDICE}", "."),
                        (f"acha -p '%3%' {INDICE} {OUTRO_INDICE}", "."),
                        (f"acha -p '%3%' -p '#abc#' {INDICE} {OUTRO_INDICE}", ".")]

FORA_DO_MOLDE = {
    "campo desconhecido": dict(CONFIG, outro=1),
    "campo desconhecido numa busca": dict(CONFIG, buscas=[dict(CONFIG["buscas"][0], outro=1)]),
    "campo que falta": {chave: valor for chave, valor in CONFIG.items() if chave != "padroes_livres"},
    "prefixos que faltam": {chave: valor for chave, valor in CONFIG.items() if chave != "prefixos"},
    "campo que falta numa busca": dict(CONFIG, buscas=[{c: v for c, v in CONFIG["buscas"][0].items()
                                                         if c != "opcoes_de_arquivo"}]),
}


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


def grava_json(nome, dados):
    caminho = TRABALHO / nome
    caminho.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    return caminho


def rodar(entrada, config, *argumentos, protocolo=None, motivo=True):
    """O gancho rodado da pasta dele, que nao e a do evento; com o texto do motivo, menos com motivo falso."""
    texto_do_motivo = ["--motivo", str(TRABALHO / MOTIVO)] if motivo else []
    return subprocess.run([sys.executable, "-I", str(PROGRAMA), "--config", str(config),
                           "--protocolo", str(protocolo or ARQUIVO_DO_PROTOCOLO), *texto_do_motivo, *argumentos],
                          input=entrada, capture_output=True, text=True, cwd=PECA)


def saida(entrada, *argumentos):
    """O que o gancho escreve; falha quando ele sai com erro."""
    resultado = rodar(entrada, CONFIGURACAO, *argumentos)
    confere(resultado.returncode == 0, f"{entrada}: saiu com {resultado.returncode}: {resultado.stderr.strip()}")
    return resultado.stdout


def da_erro(entrada, config=None, *argumentos, protocolo=None):
    return rodar(entrada, config or CONFIGURACAO, *argumentos, protocolo=protocolo).returncode != 0


def evento(nome, entrada, pasta=".", qual="antes"):
    return protocolo_inventado.evento(PROTOCOLO, qual, sessao="s", pasta=str(TRABALHO / pasta), ferramenta=nome,
                                      entrada=entrada)


def terminal(linha, pasta="."):
    return evento(CONCHA, {"linha": linha}, pasta)


def ferramenta(entrada, nome=LUPA):
    return evento(nome, entrada)


def opcao_exata(arquivo, forma):
    """O --exatas de um arquivo da pasta de trabalho, com a forma dos padroes dele."""
    return ["--exatas", str(TRABALHO / arquivo), forma]


def bloqueio(escrito):
    """O motivo do bloqueio, quando o que o gancho escreveu e a resposta que nega; None, senao."""
    return protocolo_inventado.texto_da(PROTOCOLO, "nega", escrito)


def confere_exatas(passam, barradas, opcoes, rotulo):
    """Com as opcoes do --exatas, cada comando de passam passa e cada um de barradas e bloqueado, rodado da pasta
    dele."""
    for linha, pasta in passam:
        confere(saida(terminal(linha, pasta), *opcoes) == "", f"{rotulo}, deixa passar {linha!r} de {pasta}")
    for linha, pasta in barradas:
        motivo = bloqueio(saida(terminal(linha, pasta), *opcoes))
        confere(motivo is not None and TEXTO in motivo, f"{rotulo}, bloqueia {linha!r} de {pasta}")


TRABALHO.mkdir(parents=True)
(TRABALHO / SUB).mkdir()
(TRABALHO / MOTIVO).write_text(TEXTO, encoding="utf-8")
(TRABALHO / INDICE).write_text("%3% conteúdo inventado\n", encoding="utf-8")
(TRABALHO / OUTRO_INDICE).write_text("#abc# conteúdo inventado\n", encoding="utf-8")
CONFIGURACAO = grava_json("cfg.json", CONFIG)
ARQUIVO_DO_PROTOCOLO = grava_json("protocolo.json", PROTOCOLO)
EXATA = opcao_exata(INDICE, FORMA)
DUAS_EXATAS = EXATA + opcao_exata(OUTRO_INDICE, OUTRA_FORMA)

for linha in BARRADOS:
    motivo = bloqueio(saida(terminal(linha)))
    confere(motivo is not None and TEXTO in motivo, f"bloqueia {linha!r}")
for linha in LIVRES:
    confere(saida(terminal(linha)) == "", f"deixa passar {linha!r}")
confere("palavra" in (bloqueio(saida(terminal("eco ok; acha palavra x"))) or ""),
        "o bloqueio mostra a parte que bloqueou")
for entrada, barrada in NA_FERRAMENTA:
    motivo = bloqueio(saida(ferramenta(entrada)))
    confere((motivo is not None and TEXTO in motivo) == barrada,
            f"na ferramenta de busca, {entrada} {'bloqueia' if barrada else 'passa'}")
confere(saida(terminal("acha palavra")) == saida(terminal("acha palavra")), "duas rodadas dão o mesmo")

confere_exatas(EXATAS_PASSAM, EXATAS_BARRADAS, EXATA, "com --exatas")
confere(bloqueio(saida(terminal(f"acha -p '%3%' {INDICE}"))) is not None, "sem --exatas, a busca exata é bloqueada")
confere(bloqueio(saida(ferramenta({"termo": "%3%"}), *EXATA)) is not None,
        "com --exatas, a ferramenta de busca bloqueia o padrão exato")
confere(saida(terminal(f"acha -p '%3%' x {INDICE}"), *EXATA) == saida(terminal(f"acha -p '%3%' x {INDICE}"), *EXATA),
        "com --exatas, duas rodadas dão o mesmo")
confere_exatas(DUAS_EXATAS_PASSAM, DUAS_EXATAS_BARRADAS, DUAS_EXATAS, "com --exatas de dois arquivos")

confere(da_erro(ferramenta({"termo": "x"}, nome="Outra")), "ferramenta desconhecida dá erro")
confere(da_erro(evento(CONCHA, {"linha": "eco"}, qual="fim")), "o evento de fim dá erro")
confere(da_erro(json.dumps({PROTOCOLO["chaves"]["evento"]: "Outro"})), "evento desconhecido dá erro")
confere(da_erro("isto nao e json"), "entrada que não é JSON dá erro")
confere(da_erro(terminal("eco"), None, *opcao_exata(NAO_EXISTE, FORMA)),
        "com --exatas, o arquivo que não existe dá erro")
confere(da_erro(terminal("eco"), None, *EXATA, *opcao_exata(NAO_EXISTE, OUTRA_FORMA)),
        "com --exatas de dois arquivos, o segundo que não existe dá erro")
confere(da_erro(terminal("eco"), None, *opcao_exata(INDICE, "(sem fechar")),
        "com --exatas, a forma que não é expressão regular dá erro")
for numero, (caso, dados) in enumerate(FORA_DO_MOLDE.items()):
    confere(da_erro(terminal("eco"), grava_json(f"fora-do-molde-{numero}.json", dados)),
            f"configuração com {caso} dá erro")
SEM_TERMINAL = {chave: valor for chave, valor in PROTOCOLO.items() if chave != "terminal"}
confere(da_erro(terminal("eco"), protocolo=grava_json("protocolo-sem-terminal.json", SEM_TERMINAL)),
        "protocolo fora da forma dá erro")
confere(rodar(terminal("eco"), CONFIGURACAO, motivo=False).returncode != 0, "sem o texto do motivo dá erro")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
