"""Testes de destino_da_limpeza.py.

Tudo e inventado: os textos dos avisos, a pasta das anotacoes, os nomes e o que tem cada
arquivo de destino e de origem, sorteado com uma semente fixa (outra vem com --semente); e o
protocolo do programa que roda o gancho, sorteado (os eventos, as chaves e as respostas), com
a ferramenta de terminal, os campos do caminho, uma ferramenta que troca um trecho e uma que
grava o arquivo inteiro. Os testes conferem o que o gancho faz, nunca uma frase pronta:
  - no destino, passa a escrita que so cresce, entre blocos, depois de sair texto de uma
    origem na mesma resposta, pela troca de uma vez, pela troca de todas e pela escrita
    inteira; e bloqueada, na resposta que nega, com o texto do aviso e o caminho, a que muda
    ou tira uma linha, a que poe texto grudado num bloco ou no meio dele e a da ferramenta
    que o gancho nao sabe ler; e bloqueada a que chega sem nada saido, com o texto e as
    origens;
  - so conta como saida a escrita que tira ou muda texto de um arquivo de origem, ou de um
    arquivo dentro de uma pasta de origem; a que so acrescenta, a de fora das origens e a da
    ferramenta que o gancho nao sabe ler nao contam;
  - o fim da resposta apaga a anotacao, que fica na pasta da configuracao; cada sessao tem
    a sua, e o id da sessao nunca vira caminho;
  - o caminho por atalho ou com ".." e o mesmo arquivo;
  - a escrita que nao muda nada passa; a troca que nao se aplica passa (a ferramenta a
    recusa);
  - no terminal, o comando com o nome de um destino e bloqueado, o resto passa;
  - com a configuracao fora do molde ou sem um campo, o aviso que nao existe, a entrada que
    nao e JSON, o evento desconhecido, a ferramenta sem campo de caminho ou a sessao sem id,
    o que nomeia um destino, mesmo escrito como no JSON, e bloqueado com o erro, e o resto
    sai com erro; o protocolo fora da forma e a falta da opcao de um aviso saem com erro;
  - o gancho nunca escreve no destino nem nas origens; a mesma entrada da a mesma saida.
Uso:
    python3 -I teste_destino_da_limpeza.py <pasta de destino_da_limpeza.py> <pasta de trabalho nova> [--semente N]
O protocolo inventado vem do protocolo_inventado.py, da pasta de testes do protocolo.
"""
import argparse
import json
import random
import string
import subprocess
import sys
from pathlib import Path

LEITOR = argparse.ArgumentParser(description="Testes de destino_da_limpeza.py.")
LEITOR.add_argument("peca", type=Path, help="a pasta de destino_da_limpeza.py")
LEITOR.add_argument("trabalho", type=Path, help="uma pasta de trabalho nova")
LEITOR.add_argument("--semente", type=int, default=11, help="a semente do sorteio")
ARGS = LEITOR.parse_args()
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "protocolo" / "testes"))
import protocolo_inventado  # noqa: E402

PROGRAMA = ARGS.peca.resolve() / "destino_da_limpeza.py"
TRABALHO = ARGS.trabalho.resolve()
SORTE = random.Random(ARGS.semente)
FALHAS = []

TROCA, INTEIRO, OUTRA, CONCHA = "Trocador", "Gravador", "Riscador", "Concha"  # as ferramentas inventadas
CONFIG = {"versao_schema": 1, "estado": "notas"}
AVISOS = {"muda": "t-muda.txt", "sem_origem": "t-sem.txt", "terminal": "t-term.txt"}  # o arquivo de cada aviso
OPCOES = {"muda": "--aviso-muda", "sem_origem": "--aviso-sem-origem", "terminal": "--aviso-terminal"}  # pelo README
PROTOCOLO = protocolo_inventado.inventado(
    SORTE, {"ferramenta": CONCHA, "campo_comando": "linha"},
    escritas={"campos_caminho": ["alvo_x", "alvo_y"],
              "trocas": {TROCA: {"antes": "velho", "depois": "novo", "todas": "todos"}},
              "inteiros": {INTEIRO: "inteiro"}})


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


# ---- o sorteio ----

def palavra():
    return "".join(SORTE.choice(string.ascii_lowercase) for _ in range(SORTE.randint(3, 9)))


def linha():
    return " ".join(palavra() for _ in range(SORTE.randint(2, 6)))


def bloco():
    """Um bloco de duas a quatro linhas cheias, para ter sempre um meio."""
    return [linha() for _ in range(SORTE.randint(2, 4))]


def texto(blocos):
    return "\n\n".join("\n".join(b) for b in blocos) + "\n"


def grava(caminho, conteudo):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(conteudo, encoding="utf-8")
    return caminho


def linhas_de(arquivo):
    return arquivo.read_text(encoding="utf-8").splitlines()


# ---- o projeto inventado ----

TRABALHO.mkdir(parents=True)
PASTA_CONFIG = TRABALHO / f"cfg-{palavra()}"
TEXTOS = {nome: f"texto inventado de {nome}: {linha()}" for nome in AVISOS.values()}
for nome, conteudo in TEXTOS.items():
    grava(PASTA_CONFIG / nome, conteudo)
CONFIGURACAO = grava(PASTA_CONFIG / "config.json", json.dumps(CONFIG))
ARQUIVO_DO_PROTOCOLO = grava(PASTA_CONFIG / "protocolo.json", json.dumps(PROTOCOLO, ensure_ascii=False))
NOTAS = PASTA_CONFIG / CONFIG["estado"]

GUARDA = TRABALHO / f"guarda-{palavra()}"
DESTINO = GUARDA / f"{palavra()}-ç.md"  # com letra fora do ASCII, que o JSON pode escrever escapada
REPETIDA = linha()  # a linha que fecha um bloco e fica no meio de outro, para a troca de todas
BLOCOS = [bloco() for _ in range(SORTE.randint(4, 7))]
BLOCOS[1].append(REPETIDA)
BLOCOS[3].insert(1, REPETIDA)
grava(DESTINO, texto(BLOCOS))
ATALHO = TRABALHO / f"atalho-{palavra()}"
ATALHO.symlink_to(GUARDA, target_is_directory=True)

PASTA_ORIGEM = TRABALHO / f"origens-{palavra()}"
ORIGENS_DA_PASTA = [grava(PASTA_ORIGEM / f"{palavra()}.md", texto([bloco(), bloco()])),
                    grava(PASTA_ORIGEM / palavra() / f"{palavra()}.md", texto([bloco(), bloco()]))]
SOLTA = grava(TRABALHO / f"solta-{palavra()}.md", texto([bloco(), bloco()]))
FORA = grava(TRABALHO / f"fora-{palavra()}.md", texto([bloco(), bloco()]))
ORIGENS = [PASTA_ORIGEM, SOLTA]
ANTES = {c: c.read_bytes() for c in [DESTINO, SOLTA, FORA] + ORIGENS_DA_PASTA}


# ---- o gancho ----

def rodar(entrada, config=None, protocolo=None, avisos=None):
    """O gancho, com os avisos dados ({aviso: caminho}, ou os de sempre)."""
    argumentos = [sys.executable, "-I", str(PROGRAMA), "--config", str(config or CONFIGURACAO),
                  "--protocolo", str(protocolo or ARQUIVO_DO_PROTOCOLO), "--destino", str(DESTINO)]
    for origem in ORIGENS:
        argumentos += ["--origem", str(origem)]
    for aviso, caminho in (avisos if avisos is not None else {a: PASTA_CONFIG / n for a, n in AVISOS.items()}).items():
        argumentos += [OPCOES[aviso], str(caminho)]
    return subprocess.run(argumentos, input=entrada, capture_output=True, text=True, cwd=TRABALHO)


def saida(entrada, config=None):
    """O que o gancho escreve; falha quando ele sai com erro."""
    resultado = rodar(entrada, config)
    confere(resultado.returncode == 0, f"{str(entrada)[:100]}: saiu com {resultado.returncode}: "
                                       f"{resultado.stderr.strip()[-300:]}")
    return resultado.stdout


def bloqueio(escrito):
    return protocolo_inventado.texto_da(PROTOCOLO, "nega", escrito)


def evento(sessao, ferramenta, entrada):
    return protocolo_inventado.evento(PROTOCOLO, "antes", sessao=sessao, ferramenta=ferramenta, entrada=entrada)


def troca(sessao, caminho, velho, novo, todos=None):
    entrada = {"alvo_x": str(caminho), "velho": velho, "novo": novo}
    return evento(sessao, TROCA, entrada if todos is None else dict(entrada, todos=todos))


def inteiro(sessao, caminho, conteudo):
    return evento(sessao, INTEIRO, {"alvo_y": str(caminho), "inteiro": conteudo})


def fim(sessao):
    return protocolo_inventado.evento(PROTOCOLO, "fim", sessao=sessao, fim_repetido=False)


SESSOES = iter(f"sessao-{n}-{palavra()}" for n in range(10 ** 6))


def nova_sessao():
    return next(SESSOES)


def tira_de(sessao, arquivo):
    """O que o gancho escreve diante da troca que tira de um arquivo uma linha sorteada."""
    alvo = SORTE.choice([l for l in linhas_de(arquivo) if l.strip()])
    return saida(troca(sessao, arquivo, alvo + "\n", ""))


def aberta():
    """Uma sessao em que ja saiu texto de uma origem nesta resposta."""
    sessao = nova_sessao()
    tira_de(sessao, SOLTA)
    return sessao


def cresce(caminho=DESTINO):
    """A escrita inteira que poe um bloco novo entre dois blocos sorteados, ou no fim."""
    k = SORTE.randint(1, len(BLOCOS))
    return lambda sessao: inteiro(sessao, caminho, texto(BLOCOS[:k] + [bloco()] + BLOCOS[k:]))


def passa(escrito, caso):
    confere(bloqueio(escrito) is None, f"passa: {caso}")


def barra(escrito, aviso, caminhos, caso):
    motivo = bloqueio(escrito)
    confere(motivo is not None, f"bloqueia: {caso}")
    confere(motivo is None or TEXTOS[AVISOS[aviso]] in motivo, f"o bloqueio traz o texto de {aviso}: {caso}")
    confere(motivo is None or all(str(c) in motivo for c in caminhos), f"o bloqueio traz os caminhos: {caso}")


# ---- o destino só cresce, depois de sair texto de uma origem ----

ULTIMA = BLOCOS[0][-1]
for caso, escrita in {
    "bloco novo entre blocos, pela escrita inteira": cresce(),
    "bloco novo no fim": lambda s: inteiro(s, DESTINO, texto(BLOCOS + [bloco()])),
    "bloco novo no começo": lambda s: inteiro(s, DESTINO, texto([bloco()] + BLOCOS)),
    "bloco novo depois de um bloco, pela troca": lambda s: troca(s, DESTINO, ULTIMA, f"{ULTIMA}\n\n{linha()}"),
    "troca de uma vez, onde a linha fecha um bloco": lambda s: troca(s, DESTINO, REPETIDA, f"{REPETIDA}\n\n{linha()}"),
}.items():
    passa(saida(escrita(aberta())), caso)
    barra(saida(escrita(nova_sessao())), "sem_origem", ORIGENS, f"{caso}, sem nada saído")

sessao = aberta()
barra(saida(troca(sessao, DESTINO, REPETIDA, f"{REPETIDA}\n\n{linha()}", todos=True)), "muda", [DESTINO],
      "troca de todas, que gruda o texto novo no meio de um bloco")
passa(saida(troca(sessao, DESTINO, ULTIMA, f"{ULTIMA}\n\n{linha()}", todos=True)), "troca de todas, entre blocos")
passa(saida(inteiro(nova_sessao(), DESTINO, texto(BLOCOS))), "escrita que não muda nada, sem nada saído")
passa(saida(troca(nova_sessao(), DESTINO, f"{linha()} {linha()}", linha())), "troca que não se aplica")

sessao = aberta()
k = SORTE.randrange(len(BLOCOS))
i = SORTE.randrange(len(BLOCOS[k]) - 1)
mudado = [list(b) for b in BLOCOS]
mudado[k][i] += f" {palavra()}"
sem_linha = BLOCOS[:k] + [BLOCOS[k][:i] + BLOCOS[k][i + 1:]] + BLOCOS[k + 1:]
for caso, escrita in {
    "linha mudada": inteiro(sessao, DESTINO, texto(mudado)),
    "linha tirada": inteiro(sessao, DESTINO, texto(sem_linha)),
    "bloco tirado": inteiro(sessao, DESTINO, texto(BLOCOS[:k] + BLOCOS[k + 1:])),
    "palavra no meio de uma linha": troca(sessao, DESTINO, BLOCOS[k][i], f"{BLOCOS[k][i]} {palavra()}"),
    "linha grudada no fim de um bloco": troca(sessao, DESTINO, BLOCOS[k][-1], f"{BLOCOS[k][-1]}\n{linha()}"),
    "linha grudada no começo de um bloco": troca(sessao, DESTINO, BLOCOS[k][0], f"{linha()}\n{BLOCOS[k][0]}"),
    "linha no meio de um bloco": troca(sessao, DESTINO, BLOCOS[k][i], f"{BLOCOS[k][i]}\n{linha()}"),
    "bloco grudado depois de um bloco": troca(sessao, DESTINO, BLOCOS[k][-1], f"{BLOCOS[k][-1]}\n{linha()}\n"),
    "ferramenta que o gancho não sabe ler": evento(sessao, OUTRA, {"alvo_x": str(DESTINO)}),
}.items():
    barra(saida(escrita), "muda", [DESTINO], caso)

# ---- o que conta como saída de uma origem ----

PELO_PONTO_PONTO = PASTA_ORIGEM / ORIGENS_DA_PASTA[1].parent.name / ".." / ORIGENS_DA_PASTA[0].name
for caso, tirar in {
    "linha tirada de um arquivo na pasta de origem": lambda s: tira_de(s, ORIGENS_DA_PASTA[0]),
    "linha tirada de um arquivo numa subpasta da pasta de origem": lambda s: tira_de(s, ORIGENS_DA_PASTA[1]),
    "linha tirada do arquivo de origem": lambda s: tira_de(s, SOLTA),
    "linha mudada no arquivo de origem": lambda s: saida(troca(s, SOLTA, linhas_de(SOLTA)[0], linha())),
    "escrita inteira sem um bloco": lambda s: saida(inteiro(s, ORIGENS_DA_PASTA[0], texto([bloco()]))),
    "caminho com ..": lambda s: tira_de(s, PELO_PONTO_PONTO),
}.items():
    sessao = nova_sessao()
    confere(bloqueio(tirar(sessao)) is None, f"a origem nunca é bloqueada: {caso}")
    passa(saida(cresce()(sessao)), f"depois de {caso}")

ULTIMA_SOLTA = linhas_de(SOLTA)[-1]
for caso, escrita in {
    "acréscimo na origem": lambda s: troca(s, SOLTA, ULTIMA_SOLTA, f"{ULTIMA_SOLTA}\n\n{linha()}"),
    "linha tirada de um arquivo de fora das origens": lambda s: troca(s, FORA, linhas_de(FORA)[0] + "\n", ""),
    "ferramenta que o gancho não sabe ler, na origem": lambda s: evento(s, OUTRA, {"alvo_y": str(SOLTA)}),
}.items():
    sessao = nova_sessao()
    saida(escrita(sessao))
    barra(saida(cresce()(sessao)), "sem_origem", ORIGENS, f"depois de {caso}")

# ---- a anotação ----

sessao = aberta()
confere(NOTAS.is_dir() and any(NOTAS.iterdir()), "a anotação fica na pasta da configuração")
confere(NOTAS.is_dir() and all(len(n.name) == 64 and set(n.name) <= set(string.hexdigits.lower())
                               for n in NOTAS.iterdir()), "o nome da anotação é a impressão digital da sessão")
barra(saida(cresce()(nova_sessao())), "sem_origem", ORIGENS, "outra sessão não usa a anotação desta")
confere(saida(fim(sessao)) == "", "o fim não diz nada")
barra(saida(cresce()(sessao)), "sem_origem", ORIGENS, "depois do fim da resposta")
confere(saida(fim(nova_sessao())) == "", "o fim sem anotação não diz nada")
FUGA = f"../../{palavra()}"
tira_de(FUGA, SOLTA)
confere(not (NOTAS / FUGA).resolve().exists(), "o id da sessão nunca vira caminho")
saida(fim(FUGA))

# ---- o atalho e o caminho com .. ----

PELO_ATALHO = ATALHO / DESTINO.name
passa(saida(cresce(PELO_ATALHO)(aberta())), "crescer pelo atalho, depois de sair texto")
barra(saida(cresce(PELO_ATALHO)(nova_sessao())), "sem_origem", ORIGENS, "crescer pelo atalho, sem nada saído")
barra(saida(inteiro(aberta(), PELO_ATALHO, texto(BLOCOS[1:]))), "muda", [DESTINO], "tirar pelo atalho")
barra(saida(cresce(GUARDA / ".." / GUARDA.name / DESTINO.name)(nova_sessao())), "sem_origem", ORIGENS,
      "crescer pelo caminho com .., sem nada saído")

# ---- o terminal ----

for comando in (f"cat {DESTINO}", f"cp {FORA} {DESTINO.name}", f'eco "{DESTINO.name}"', f"eco a; eco {DESTINO}"):
    barra(saida(evento(nova_sessao(), CONCHA, {"linha": comando})), "terminal", [DESTINO], comando)
for comando in ("eco ok", f"cat {FORA}", f"ls {GUARDA}", f"eco {DESTINO.stem}"):
    passa(saida(evento(nova_sessao(), CONCHA, {"linha": comando})), comando)

# ---- entradas erradas ----

FORA_DO_MOLDE = {
    "campo desconhecido": dict(CONFIG, outro=1),
    "campo que falta": {chave: valor for chave, valor in CONFIG.items() if chave != "estado"},
}
for numero, (caso, dados) in enumerate(FORA_DO_MOLDE.items()):
    errada = grava(PASTA_CONFIG / f"errada-{numero}.json", json.dumps(dados))
    motivo = bloqueio(saida(troca(nova_sessao(), DESTINO, ULTIMA, f"{ULTIMA}\n\n{linha()}"), errada))
    confere(motivo is not None and str(DESTINO) in motivo, f"configuração com {caso}: o que toca o destino é bloqueado")
    confere(rodar(troca(nova_sessao(), FORA, linha(), linha()), errada).returncode != 0,
            f"configuração com {caso}: o resto sai com erro")
SEM_AVISO = {a: PASTA_CONFIG / (n if a != "muda" else f"nao-{n}") for a, n in AVISOS.items()}
resultado = rodar(troca(nova_sessao(), DESTINO, ULTIMA, f"{ULTIMA}\n\n{linha()}"), avisos=SEM_AVISO)
confere(resultado.returncode == 0 and bloqueio(resultado.stdout) is not None,
        "o aviso que não existe: o que toca o destino é bloqueado")
confere(rodar(troca(nova_sessao(), FORA, linha(), linha()), avisos=SEM_AVISO).returncode != 0,
        "o aviso que não existe: o resto sai com erro")
for aviso in AVISOS:
    sem_ele = {a: PASTA_CONFIG / n for a, n in AVISOS.items() if a != aviso}
    confere(rodar(fim(nova_sessao()), avisos=sem_ele).returncode != 0, f"sem a opção do aviso {aviso}, sai com erro")
SEM_ESCRITAS = {chave: valor for chave, valor in PROTOCOLO.items() if chave != "escritas"}
SEM_ESCRITAS = grava(PASTA_CONFIG / "protocolo-sem-escritas.json", json.dumps(SEM_ESCRITAS, ensure_ascii=False))
confere(rodar(troca(nova_sessao(), DESTINO, ULTIMA, f"{ULTIMA}\n\n{linha()}"), protocolo=SEM_ESCRITAS).returncode != 0,
        "o protocolo fora da forma sai com erro")

ESCAPADO = json.dumps({"alvo_x": str(DESTINO)})  # o caminho do destino escrito como no JSON, com o escape
confere("\\u" in ESCAPADO, "o nome do destino tem letra que o JSON escapa")
CHAVES = PROTOCOLO["chaves"]


def desconhecido(caminho):
    """O texto JSON de um evento de nome desconhecido, com o caminho na entrada."""
    return json.dumps({CHAVES["evento"]: "Outro", CHAVES["sessao"]: nova_sessao(), CHAVES["ferramenta"]: TROCA,
                       CHAVES["entrada"]: {"alvo_x": str(caminho), "velho": "a", "novo": "b"}})


for caso, (com_destino, sem_destino) in {
    "entrada que não é JSON": (f"isto não é JSON {DESTINO}", "isto não é JSON"),
    "entrada que não é JSON, com o nome escapado": (f"{{ {ESCAPADO}", "{ {}"),
    "evento desconhecido": (desconhecido(DESTINO), desconhecido(FORA)),
    "ferramenta sem campo de caminho": (evento(nova_sessao(), TROCA, {"outro": str(DESTINO)}),
                                        evento(nova_sessao(), TROCA, {"outro": str(FORA)})),
    "sessão sem id": (troca("", DESTINO, ULTIMA, f"{ULTIMA}\n\n{linha()}"),
                      troca("", SOLTA, linhas_de(SOLTA)[0] + "\n", "")),
}.items():
    resultado = rodar(com_destino)
    confere(resultado.returncode == 0 and bloqueio(resultado.stdout) is not None,
            f"{caso}, nomeando o destino: bloqueia")
    confere(rodar(sem_destino).returncode != 0, f"{caso}, sem o destino: sai com erro")

# ---- o gancho só lê ----

confere(all(c.read_bytes() == conteudo for c, conteudo in ANTES.items()),
        "o gancho não escreve no destino nem nas origens")
REPETIDO = troca(nova_sessao(), DESTINO, BLOCOS[0][0], f"{linha()}\n{BLOCOS[0][0]}")
confere(rodar(REPETIDO).stdout == rodar(REPETIDO).stdout, "a mesma entrada dá a mesma saída")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
