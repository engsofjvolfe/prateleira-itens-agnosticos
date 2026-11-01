"""Testes de leitura_completa.py.

Tudo e inventado: os comandos que cortam, o prefixo, na configuracao da leitura do terminal,
os textos do motivo e do fim, a pasta das anotacoes e os arquivos lidos, com o numero de
linhas sorteado, com uma semente fixa (outra vem com --semente), e letras de fora do ASCII;
e o protocolo do programa que roda o gancho, sorteado (os eventos, as chaves e as
respostas), com a ferramenta de terminal, uma de busca, uma que resume e uma de leitura, que
da a primeira linha um numero sorteado e le, sem o campo das quantas, um numero sorteado de
linhas. Nada e de um projeto real nem de um programa de verdade. Os testes conferem o que o
gancho faz, nunca uma frase pronta:
  - no terminal, barra o comando que corta, de uma ou de duas palavras, tambem com outras no
    meio, depois de um operador, de um prefixo e de uma atribuicao, com o caminho e dentro de
    $( ) ou de crases; e o comando que nao se le; deixa passar o resto, tambem o nome do
    comando como argumento, entre aspas, num comentario ou como parte de outro nome;
  - a ferramenta de busca e a que resume sao barradas sempre;
  - na leitura, passa a que comeca na primeira linha, sem o campo do comeco ou com ele ate a
    primeira linha; a que continua na linha seguinte a ultima lida, em pedacos de tamanhos
    sorteados, ate o fim; e a que repete o ultimo pedaco; e barrada, com o arquivo, as linhas
    lidas e as que ele tem, a que comeca em outra linha, tambem a que pula uma linha ou volta
    menos que o ultimo pedaco; a leitura sem o campo das quantas le as linhas sem limite;
  - as linhas do arquivo sao as separadas pela quebra de linha, com ou sem ela no fim; o que
    nao e texto UTF-8, o que nao existe e a pasta ficam de fora;
  - o caminho parte da pasta da chamada, e o caminho por atalho ou com ".." e o mesmo arquivo;
  - no fim, com arquivo lido em parte, trava, com o texto do fim e cada arquivo uma vez, na
    ordem dos caminhos, com as linhas lidas e as que ele tem, e a leitura continua depois da
    trava; o arquivo lido ate o fim nao entra; na volta da trava, libera e apaga as
    anotacoes; sem nada lido em parte, nao diz nada;
  - cada sessao tem a sua pasta, e cada arquivo lido em parte a sua anotacao nela, na pasta
    da configuracao, com os nomes tirados do id da sessao e do caminho, e nada mais fica ali;
    o id da sessao nunca vira caminho; a anotacao nova e um arquivo novo, que toma o lugar
    da de antes;
  - o bloqueio e a resposta que nega do protocolo, com o texto do motivo e a parte que
    bloqueou;
  - antes de uma chamada, o erro a barra: a configuracao fora do molde ou de outra versao, o
    comando sem palavra, a configuracao da leitura do terminal fora do molde, o texto do
    motivo que falta, a ferramenta desconhecida, a leitura sem o caminho ou sem o id da
    sessao e o numero que nao e inteiro ou fica abaixo do menor; no fim, a configuracao fora
    do molde, o texto do fim que falta e a sessao sem id saem com erro; o protocolo fora da
    forma, a entrada que nao e JSON, o evento desconhecido e a falta de uma opcao do comando
    tambem;
  - o gancho nunca escreve nos arquivos lidos, e a mesma entrada da a mesma saida.
Uso:
    python3 -I teste_leitura_completa.py <pasta de leitura_completa.py> <pasta de trabalho nova> [--semente N]
O protocolo inventado vem do protocolo_inventado.py, da pasta de testes do protocolo.
"""
import argparse
import hashlib
import json
import random
import string
import subprocess
import sys
from pathlib import Path

LEITOR = argparse.ArgumentParser(description="Testes de leitura_completa.py.")
LEITOR.add_argument("peca", type=Path, help="a pasta de leitura_completa.py")
LEITOR.add_argument("trabalho", type=Path, help="uma pasta de trabalho nova")
LEITOR.add_argument("--semente", type=int, default=13, help="a semente do sorteio")
ARGS = LEITOR.parse_args()
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "protocolo" / "testes"))
import protocolo_inventado  # noqa: E402

PECA = ARGS.peca.resolve()
PROGRAMA = PECA / "leitura_completa.py"
TRABALHO = ARGS.trabalho.resolve()
SORTE = random.Random(ARGS.semente)
FALHAS = []

CONCHA, LUPA, RESUMIDOR, LEITORA = "Concha", "Lupa", "Resumidor", "Leitora"  # as ferramentas inventadas
PRIMEIRA = SORTE.randint(1, 3)  # o numero que a ferramenta de leitura da a primeira linha
SEM_LIMITE = SORTE.randint(4, 9)  # quantas linhas ela le sem o campo das quantas
PROTOCOLO = protocolo_inventado.inventado(
    SORTE, {"ferramenta": CONCHA, "campo_comando": "linha"}, buscas=[{"nome": LUPA, "campo_padrao": "termo"}],
    leituras=[{"nome": LEITORA, "campo_caminho": "alvo", "campo_comeco": "desde", "campo_quantas": "quantas",
               "linhas_sem_limite": SEM_LIMITE, "primeira_linha": PRIMEIRA}],
    resumos=[RESUMIDOR])
PREFIXO = protocolo_inventado.nomes_sorteados(SORTE, 1)[0]  # com uma letra de fora do ASCII
TERMINAL = {"versao_schema": 1, "prefixos": [PREFIXO]}  # a configuracao da leitura do terminal
CONFIG = {"versao_schema": 1, "estado": "notas", "comandos": ["corta", "versao acha"]}
OPCOES = {"motivo": "--motivo", "fim": "--fim"}  # a opcao de cada texto, pelo README


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


# ---- o sorteio ----

def palavra():
    return "".join(SORTE.choice(string.ascii_lowercase + "áçõü") for _ in range(SORTE.randint(3, 8)))


def texto(linhas, quebra_no_fim=True):
    """Um texto de tantas linhas, cada uma com uma a cinco palavras."""
    corpo = "\n".join(" ".join(palavra() for _ in range(SORTE.randint(1, 5))) for _ in range(linhas))
    return corpo + ("\n" if quebra_no_fim and linhas else "")


def grava(caminho, conteudo):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(conteudo, bytes):
        caminho.write_bytes(conteudo)
    else:
        caminho.write_text(conteudo, encoding="utf-8")
    return caminho


def impressao(nome):
    """A impressao digital (SHA-256) de um nome, que da o nome da anotacao, pelo README do protocolo."""
    return hashlib.sha256(nome.encode("utf-8")).hexdigest()


def eh_impressao(nome):
    return len(nome) == len(impressao("")) and set(nome) <= set(string.hexdigits.lower())


# ---- o projeto inventado ----

TRABALHO.mkdir(parents=True)
PASTA_CONFIG = TRABALHO / f"cfg-{palavra()}"
TEXTOS = {qual: f"texto inventado de {qual}: {palavra()} {palavra()}" for qual in OPCOES}
ARQUIVOS_DOS_TEXTOS = {qual: grava(PASTA_CONFIG / f"{qual}-{palavra()}.txt", t) for qual, t in TEXTOS.items()}
CONFIGURACAO = grava(PASTA_CONFIG / "config.json", json.dumps(CONFIG))
ARQUIVO_DO_TERMINAL = grava(PASTA_CONFIG / "terminal.json", json.dumps(TERMINAL, ensure_ascii=False))
ARQUIVO_DO_PROTOCOLO = grava(PASTA_CONFIG / "protocolo.json", json.dumps(PROTOCOLO, ensure_ascii=False))
NOTAS = PASTA_CONFIG / CONFIG["estado"]

DOCS = TRABALHO / f"docs-{palavra()}"
TOTAL = SEM_LIMITE * SORTE.randint(5, 7) + SORTE.randint(1, SEM_LIMITE - 1)  # mais que quatro leituras sem limite
LONGO = grava(DOCS / f"longo-{palavra()}.md", texto(TOTAL))
TOTAL_OUTRO = SORTE.randint(2, 3 * SEM_LIMITE)
OUTRO = grava(DOCS / f"outro-{palavra()}.md", texto(TOTAL_OUTRO))  # o nome vem depois do de LONGO, na ordem
CURTO = grava(DOCS / f"curto-{palavra()}.md", texto(SEM_LIMITE))  # cabe numa leitura sem limite, com a quebra no fim
SEM_QUEBRA_LINHAS = SORTE.randint(2, SEM_LIMITE)
SEM_QUEBRA = grava(DOCS / f"sem-quebra-{palavra()}.md", texto(SEM_QUEBRA_LINHAS, quebra_no_fim=False))
VAZIO = grava(DOCS / f"vazio-{palavra()}.md", "")
BINARIO = grava(DOCS / f"binario-{palavra()}.bin", b"\xff\x80\n" * TOTAL)  # com quebras de linha, mas nao e UTF-8
ATALHO = TRABALHO / f"atalho-{palavra()}"
ATALHO.symlink_to(DOCS, target_is_directory=True)
ANTES = {c: c.read_bytes() for c in DOCS.iterdir()}


# ---- o gancho ----

SESSOES = iter(f"sessao-{n}-{palavra()}" for n in range(10 ** 6))


def nova_sessao():
    return next(SESSOES)


def evento(sessao, ferramenta, entrada, pasta=TRABALHO):
    return protocolo_inventado.evento(PROTOCOLO, "antes", sessao=sessao, ferramenta=ferramenta, entrada=entrada,
                                      pasta=str(pasta))


def leitura(sessao, caminho, desde=None, quantas=None, pasta=TRABALHO):
    """A leitura do arquivo, com o comeco e as quantas so quando dados."""
    entrada = {"alvo": str(caminho)}
    entrada.update({campo: valor for campo, valor in (("desde", desde), ("quantas", quantas)) if valor is not None})
    return evento(sessao, LEITORA, entrada, pasta)


def terminal(linha):
    return evento(nova_sessao(), CONCHA, {"linha": linha})


def fim(sessao, repetido=False):
    return protocolo_inventado.evento(PROTOCOLO, "fim", sessao=sessao, fim_repetido=repetido)


def rodar(entrada, config=None, protocolo=None, textos=None, leitura_do_terminal=None):
    """O gancho, rodado da pasta dele, que nao e a da chamada, com os textos dados ({qual: caminho}) ou os de
    sempre, e com a configuracao da leitura do terminal: a dada, a de sempre ou, com False, nenhuma."""
    argumentos = [sys.executable, "-I", str(PROGRAMA), "--config", str(config or CONFIGURACAO),
                  "--protocolo", str(protocolo or ARQUIVO_DO_PROTOCOLO)]
    if leitura_do_terminal is not False:
        argumentos += ["--terminal", str(leitura_do_terminal or ARQUIVO_DO_TERMINAL)]
    for qual, caminho in (ARQUIVOS_DOS_TEXTOS if textos is None else textos).items():
        argumentos += [OPCOES[qual], str(caminho)]
    return subprocess.run(argumentos, input=entrada, capture_output=True, text=True, cwd=PECA)


def saida(entrada):
    """O que o gancho escreve; falha quando ele sai com erro."""
    resultado = rodar(entrada)
    confere(resultado.returncode == 0, f"{entrada[:150]}: saiu com {resultado.returncode}: "
                                       f"{resultado.stderr.strip()[-300:]}")
    return resultado.stdout


def nega(escrito):
    return protocolo_inventado.texto_da(PROTOCOLO, "nega", escrito)


def trava(escrito):
    return protocolo_inventado.texto_da(PROTOCOLO, "trava", escrito)


def situacao(caminho, lidas, total):
    """Um arquivo lido em parte, como o README o escreve: caminho: lidas/total."""
    return f"{caminho}: {lidas}/{total}"


def passa(entrada, caso):
    escrito = saida(entrada)
    confere(escrito == "", f"passa: {caso}: {escrito[:300]}")


def barra(entrada, parte, caso):
    """A chamada e barrada, na resposta que nega, com o texto do motivo e a parte."""
    motivo = nega(saida(entrada))
    confere(motivo is not None and TEXTOS["motivo"] in motivo and parte in motivo, f"barra: {caso}: {motivo}")


def barrada_pelo_erro(entrada, caso, **opcoes):
    """A chamada que da erro e barrada, na resposta que nega."""
    resultado = rodar(entrada, **opcoes)
    confere(resultado.returncode == 0 and nega(resultado.stdout) is not None, f"o erro barra: {caso}")


def travado(sessao, *situacoes):
    """O texto da trava do fim, quando ele traz o texto do fim e cada situacao uma vez; None, senao."""
    motivo = trava(saida(fim(sessao))) or ""
    return motivo if TEXTOS["fim"] in motivo and all(motivo.count(s) == 1 for s in situacoes) else None


def notas_da_sessao(sessao):
    """Os arquivos da pasta da sessao, que tem o nome tirado do id dela, pelo README do protocolo."""
    pasta = NOTAS / impressao(sessao)
    return sorted(pasta.iterdir()) if pasta.is_dir() else []


# ---- o terminal ----

BARRADOS = ["corta x", "corta", "eco x | corta", "eco x; corta -n 3 y", "eco x && corta", f"{PREFIXO} corta x",
            f"{PREFIXO} -z corta x", "/caminho/corta x", 'eco "$(corta x)"', "eco `corta x`", "VAR=1 corta x",
            "x=$(corta y)", "versao acha x", "versao -C d acha x", "eco 'sem fim", 'eco "$(sem fim"']
LIVRES = ["eco corta", "eco 'corta x'", "eco x # corta", "cortador x", "acha x", "versao lista", "eco x | eco"]
for linha in BARRADOS:
    barra(terminal(linha), "", f"o comando {linha!r}")
for linha in LIVRES:
    passa(terminal(linha), f"o comando {linha!r}")
barra(terminal("eco ok; corta -n 3 y"), "corta -n 3 y", "o bloqueio mostra a parte do comando que corta")

# ---- a busca e o resumo ----

for ferramenta, entrada in ((LUPA, {"termo": palavra()}), (LUPA, {}), (RESUMIDOR, {palavra(): palavra()}),
                            (RESUMIDOR, {})):
    barra(evento(nova_sessao(), ferramenta, entrada), ferramenta, f"a ferramenta {ferramenta} com {entrada}")

# ---- a leitura inteira ----

sessao = nova_sessao()
passa(leitura(sessao, CURTO), "a leitura sem limite de um arquivo que cabe nela")
passa(leitura(sessao, SEM_QUEBRA, quantas=SEM_QUEBRA_LINHAS), "todas as linhas de um arquivo sem a quebra no fim")
passa(leitura(sessao, VAZIO), "a leitura de um arquivo vazio")
confere(saida(fim(sessao)) == "", "os arquivos lidos inteiros não travam o fim")

sessao = nova_sessao()
passa(leitura(sessao, SEM_QUEBRA, quantas=SEM_QUEBRA_LINHAS - 1),
      "um arquivo sem a quebra no fim, menos a última linha")
confere(travado(sessao, situacao(SEM_QUEBRA, SEM_QUEBRA_LINHAS - 1, SEM_QUEBRA_LINHAS)),
        "a última linha, sem a quebra no fim, conta")

# ---- a leitura em pedaços ----

sessao, lidas = nova_sessao(), 0
while lidas < TOTAL:
    quantas = SORTE.randint(1, 2 * SEM_LIMITE) if lidas else None
    passa(leitura(sessao, LONGO, desde=PRIMEIRA + lidas if lidas else None, quantas=quantas),
          f"a leitura que continua depois de {lidas} linhas lidas")
    lidas += quantas or SEM_LIMITE
    if lidas < TOTAL:
        confere(travado(sessao, situacao(LONGO, lidas, TOTAL)), f"o fim trava com {lidas} de {TOTAL} linhas lidas")
confere(saida(fim(sessao)) == "", "o arquivo lido até o fim, em pedaços, não trava o fim")

sessao = nova_sessao()
barra(leitura(sessao, LONGO, desde=PRIMEIRA + SORTE.randint(1, TOTAL - 1)), situacao(LONGO, 0, TOTAL),
      "a leitura que começa no meio")
PRIMEIRO, SEGUNDO = SORTE.randint(1, SEM_LIMITE), SORTE.randint(2, SEM_LIMITE)
passa(leitura(sessao, LONGO, desde=PRIMEIRA, quantas=PRIMEIRO), "a leitura com o começo na primeira linha")
passa(leitura(sessao, LONGO, desde=PRIMEIRA + PRIMEIRO, quantas=SEGUNDO), "a leitura que continua")
LIDAS = PRIMEIRO + SEGUNDO
barra(leitura(sessao, LONGO, desde=PRIMEIRA + LIDAS + 1), situacao(LONGO, LIDAS, TOTAL), "a leitura que pula uma linha")
barra(leitura(sessao, LONGO, desde=PRIMEIRA + LIDAS - 1), situacao(LONGO, LIDAS, TOTAL),
      "a leitura que volta menos que o último pedaço")
MENOR = SORTE.randint(1, SEGUNDO - 1)
passa(leitura(sessao, LONGO, desde=PRIMEIRA + PRIMEIRO, quantas=MENOR), "a leitura que repete o último pedaço, menor")
confere(travado(sessao, situacao(LONGO, PRIMEIRO + MENOR, TOTAL)), "a repetição do último pedaço conta até onde leu")
passa(leitura(sessao, LONGO, desde=PRIMEIRA + PRIMEIRO + MENOR), "a leitura continua depois da repetição")
passa(leitura(sessao, LONGO, desde=PRIMEIRA - 1, quantas=1), "a leitura que começa antes da primeira linha")
confere(travado(sessao, situacao(LONGO, 1, TOTAL)), "a leitura que recomeça conta do começo")

# ---- o que fica de fora ----

sessao = nova_sessao()
for caso, caminho in (("o arquivo que não é texto UTF-8", BINARIO),
                      ("o arquivo que não existe", DOCS / "nao-existe.md"), ("a pasta", DOCS)):
    passa(leitura(sessao, caminho, desde=PRIMEIRA + SORTE.randint(1, SEM_LIMITE)), f"{caso} fica de fora")
confere(saida(fim(sessao)) == "", "o que fica de fora não trava o fim")

# ---- o caminho ----

sessao = nova_sessao()
passa(leitura(sessao, Path(DOCS.name) / LONGO.name), "a leitura pelo caminho a partir da pasta da chamada")
passa(leitura(sessao, ATALHO / LONGO.name, desde=PRIMEIRA + SEM_LIMITE), "a leitura continua pelo atalho")
passa(leitura(sessao, DOCS / ".." / DOCS.name / LONGO.name, desde=PRIMEIRA + 2 * SEM_LIMITE),
      "a leitura continua pelo caminho com ..")
passa(leitura(sessao, LONGO.name, desde=PRIMEIRA + 3 * SEM_LIMITE, pasta=DOCS),
      "a leitura continua a partir de outra pasta da chamada")
confere(travado(sessao, situacao(LONGO, 4 * SEM_LIMITE, TOTAL)), "os caminhos do mesmo arquivo são um arquivo só")

# ---- a trava do fim ----

sessao = nova_sessao()
passa(leitura(sessao, OUTRO, quantas=1), "a leitura de um arquivo")
passa(leitura(sessao, LONGO), "a leitura de outro")
passa(leitura(sessao, CURTO), "a leitura de um terceiro, inteiro")
motivo = travado(sessao, situacao(LONGO, SEM_LIMITE, TOTAL), situacao(OUTRO, 1, TOTAL_OUTRO)) or ""
confere(motivo and str(CURTO) not in motivo, "o fim lista cada arquivo lido em parte, uma vez, e só eles")
confere(motivo.find(str(LONGO)) < motivo.find(str(OUTRO)), "o fim lista os arquivos na ordem dos caminhos")
confere(motivo and trava(saida(fim(sessao))) == motivo,
        "a trava não apaga as anotações, e as mesmas anotações dão a mesma trava")
confere(saida(fim(sessao, repetido=True)) == "", "na volta da trava, o fim libera")
barra(leitura(sessao, LONGO, desde=PRIMEIRA + SEM_LIMITE), situacao(LONGO, 0, TOTAL),
      "a volta da trava apaga as anotações")
confere(saida(fim(sessao)) == "", "depois da volta da trava, o fim não trava")
confere(saida(fim(nova_sessao())) == "", "o fim sem nada lido não diz nada")

# ---- a anotação ----

uma, outra = nova_sessao(), nova_sessao()
passa(leitura(uma, LONGO), "a primeira leitura de uma sessão")
barra(leitura(outra, LONGO, desde=PRIMEIRA + SEM_LIMITE), situacao(LONGO, 0, TOTAL),
      "outra sessão não continua a leitura desta")
confere(travado(uma, situacao(LONGO, SEM_LIMITE, TOTAL)) and saida(fim(outra)) == "",
        "cada sessão trava só com o que ela leu")
NOTAS_DE_UMA = notas_da_sessao(uma)
confere([n.name for n in NOTAS_DE_UMA] == [impressao(str(LONGO))],
        "a anotação de um arquivo fica na pasta da sessão, com o nome tirado do caminho")
ANTES_DA_CONTINUACAO = NOTAS_DE_UMA[0].stat().st_ino if NOTAS_DE_UMA else None
passa(leitura(uma, LONGO, desde=PRIMEIRA + SEM_LIMITE), "a leitura continua na mesma sessão")
NOTAS_DE_UMA = notas_da_sessao(uma)
confere(len(NOTAS_DE_UMA) == 1 and NOTAS_DE_UMA[0].stat().st_ino != ANTES_DA_CONTINUACAO,
        "a anotação nova é um arquivo novo, que toma o lugar da de antes")
confere(NOTAS.is_dir() and all(eh_impressao(s.name) and s.is_dir() and all(eh_impressao(n.name) and n.is_file()
                                                                           for n in s.iterdir())
                               for s in NOTAS.iterdir()),
        "na pasta da configuração, só as pastas das sessões, e nelas só as anotações, com os nomes tirados dos ids")
FUGA = f"../../{palavra()}"
saida(leitura(FUGA, LONGO))
confere(not (NOTAS / FUGA).resolve().exists(), "o id da sessão nunca vira caminho")

# ---- os erros ----

FORA_DO_MOLDE = {
    "campo desconhecido": dict(CONFIG, outro=1),
    "os prefixos, que vêm da leitura do terminal": dict(CONFIG, prefixos=[PREFIXO]),
    "a pasta que falta": {chave: valor for chave, valor in CONFIG.items() if chave != "estado"},
    "os comandos que faltam": {chave: valor for chave, valor in CONFIG.items() if chave != "comandos"},
    "outra versão": dict(CONFIG, versao_schema=CONFIG["versao_schema"] + 1),
    "um comando sem palavra": dict(CONFIG, comandos=["corta", " "]),
    "um comando que não é texto": dict(CONFIG, comandos=["corta", 1]),
}
for numero, (caso, dados) in enumerate(FORA_DO_MOLDE.items()):
    errada = grava(PASTA_CONFIG / f"errada-{numero}.json", json.dumps(dados, ensure_ascii=False))
    barrada_pelo_erro(terminal("eco"), f"a configuração com {caso}", config=errada)
    confere(rodar(fim(nova_sessao()), config=errada).returncode != 0, f"a configuração com {caso}: o fim sai com erro")
SEM_PREFIXOS = grava(PASTA_CONFIG / "terminal-sem-prefixos.json", json.dumps({"versao_schema": 1}))
barrada_pelo_erro(terminal("eco"), "a configuração da leitura do terminal fora do molde",
                  leitura_do_terminal=SEM_PREFIXOS)
NAO_EXISTE = PASTA_CONFIG / f"nao-{palavra()}.txt"
barrada_pelo_erro(terminal("eco"), "o texto do motivo que falta", textos=dict(ARQUIVOS_DOS_TEXTOS, motivo=NAO_EXISTE))
confere(rodar(fim(nova_sessao()), textos=dict(ARQUIVOS_DOS_TEXTOS, fim=NAO_EXISTE)).returncode != 0,
        "o texto do fim que falta: o fim sai com erro")
for caso, entrada in {
    "a ferramenta desconhecida": evento(nova_sessao(), "Outra", {"alvo": str(LONGO)}),
    "a leitura sem o caminho": evento(nova_sessao(), LEITORA, {"outro": str(LONGO)}),
    "a leitura sem o id da sessão": leitura("", LONGO),
    "o começo que não é inteiro": leitura(nova_sessao(), LONGO, desde=str(PRIMEIRA)),
    "o começo que é sim ou não": leitura(nova_sessao(), LONGO, desde=True),
    "o começo abaixo de 0": leitura(nova_sessao(), LONGO, desde=-1),
    "as quantas que não são inteiro": leitura(nova_sessao(), LONGO, quantas=float(SEM_LIMITE)),
    "as quantas abaixo de 1": leitura(nova_sessao(), LONGO, quantas=0),
}.items():
    barrada_pelo_erro(entrada, caso)
SEM_LEITURAS = {chave: valor for chave, valor in PROTOCOLO.items() if chave != "leituras"}
SEM_LEITURAS = grava(PASTA_CONFIG / "protocolo-sem-leituras.json", json.dumps(SEM_LEITURAS, ensure_ascii=False))
confere(rodar(terminal("eco"), protocolo=SEM_LEITURAS).returncode != 0, "o protocolo fora da forma sai com erro")
confere(rodar("isto não é JSON").returncode != 0, "a entrada que não é JSON sai com erro")
confere(rodar(json.dumps({PROTOCOLO["chaves"]["evento"]: "Outro"})).returncode != 0,
        "o evento desconhecido sai com erro")
confere(rodar(fim("")).returncode != 0, "o fim sem o id da sessão sai com erro")
for qual, opcao in OPCOES.items():
    sem_ela = {q: c for q, c in ARQUIVOS_DOS_TEXTOS.items() if q != qual}
    confere(rodar(terminal("eco"), textos=sem_ela).returncode != 0, f"sem a opção {opcao}, sai com erro")
confere(rodar(terminal("eco"), leitura_do_terminal=False).returncode != 0, "sem a opção --terminal, sai com erro")

# ---- o gancho só lê ----

confere(all(c.read_bytes() == conteudo for c, conteudo in ANTES.items()), "o gancho não escreve nos arquivos lidos")
REPETIDA = leitura(nova_sessao(), LONGO, desde=PRIMEIRA + SEM_LIMITE)
confere(rodar(REPETIDA).stdout == rodar(REPETIDA).stdout, "a mesma entrada dá a mesma saída")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
