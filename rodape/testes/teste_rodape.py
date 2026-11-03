"""Testes do rodape.py, com repositorios git inventados aqui: os nomes das pastas e dos
documentos, a extensao deles, o modelo (tambem a quebra da primeira linha), os textos e os
padroes sao sorteados, com letras de fora do ASCII e
espaco no nome da pasta do arquivo para onde o rodape leva. Conferem regras, nunca uma frase
pronta:
  - com --conferir, cada documento que nao termina no rodape dele, e so ele, sai numa linha
    ERRO com o caminho e a linha (a do rodape que ele tem no fim ou, sem nenhum, a ultima com
    texto), em ordem de documento; o mesmo problema sai com o mesmo motivo, e o que falta e o
    que esta fora da forma, com motivos diferentes; o resumo diz quantos documentos e quantos
    fora do dia; o codigo e 1; nada e gravado;
  - sem --conferir, cada documento fora do dia, e so ele, ganha o rodape dele, a partir da
    pasta dele, e perde o rodape velho, com uma linha por documento e o resumo; o documento
    vazio fica so com o rodape; depois, o --conferir sai so com o resumo e com 0, e outra
    rodada nao muda nada;
  - os documentos sao os versionados e os novos que seguem os padroes; o que o .gitignore deixa
    de fora, o que segue um padrao de fora, o de outra extensao e o proprio modelo ficam como
    estao;
  - saem com 2, so com uma linha ERRO, que diz a pasta ou o arquivo, e sem nada gravado: a
    pasta sem git; a configuracao que nao e JSON, de outra versao, sem um campo, com campo que
    o molde nao conhece, sem documentos, com padrao repetido ou de mais de uma linha; o modelo
    que falta, vazio, com codigo ou com link para um arquivo que nao existe; e o documento que
    nao se le em UTF-8, tambem com outro documento para gravar antes dele;
  - duas rodadas dao a mesma saida.
Uso:
    python3 -I teste_rodape.py <pasta do rodape.py> <pasta de trabalho nova>
Precisa do git, que o teste roda sem a configuracao do sistema e da conta e sem subir da
pasta de trabalho, e das pastas irmas extrator, documentos e grava-ou-confere da peca.
"""
import json
import os
import random
import re
import string
import subprocess
import sys
from pathlib import Path

PECA, TRABALHO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
SCRIPT = PECA / "rodape.py"
GIT = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
       "GIT_CEILING_DIRECTORIES": str(TRABALHO)}
FALHAS = []
SORTEIO = random.Random(8)
LETRAS = string.ascii_lowercase + "áçõüéñ"
USADAS = set()
ERRO = re.compile(r"^ERRO (.+?):(\d+): (.+)$")
NUMERO = re.compile(r"\d+")
EXTENSAO, OUTRA_EXTENSAO = (f".{e}" for e in SORTEIO.sample(["md", "markdown", "mdown", "texto", "txt"], 2))
DIVISOR = SORTEIO.choice(["---", "***", "___"])  # a primeira linha do rodape, uma das quebras do Markdown


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


def palavra():
    """Uma palavra sorteada, com letras de fora do ASCII, que ainda nao saiu."""
    while True:
        nova = "".join(SORTEIO.choice(LETRAS) for _ in range(SORTEIO.randint(3, 7)))
        if nova not in USADAS:
            USADAS.add(nova)
            return nova


def frase():
    return " ".join(palavra() for _ in range(SORTEIO.randint(2, 6)))


def corpo():
    return "\n\n".join(frase() for _ in range(SORTEIO.randint(1, 4))) + "\n"


def git(pasta, *argumentos):
    subprocess.run(["git", "-C", str(pasta), *argumentos], check=True, capture_output=True, env=GIT)


def roda(raiz, configuracao, modelo, conferir):
    """(codigo, linhas da saida padrao) do rodape.py."""
    r = subprocess.run([sys.executable, "-I", str(SCRIPT), str(raiz), str(configuracao), str(modelo),
                        *(["--conferir"] if conferir else [])], capture_output=True, encoding="utf-8", env=GIT)
    return r.returncode, r.stdout.splitlines()


def grava_json(caminho, dados):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    return caminho


TRABALHO.mkdir(parents=True)
RAIZ = TRABALHO / palavra()
DADOS, CABECALHO = palavra(), palavra()
LICENCA = f"{palavra()} {palavra()}/{palavra()}.txt"  # com espaco no nome da pasta
TEXTO_DO_RODAPE, TEXTO_DO_LINK = frase(), frase()


def rodape(pasta):
    """O rodape de um documento na pasta dada (a partir da raiz), como o teste o calcula."""
    alvo = Path(os.path.relpath(RAIZ / LICENCA, RAIZ / pasta)).as_posix()
    return f"{DIVISOR}\n\n*{TEXTO_DO_RODAPE} [{TEXTO_DO_LINK}](<{alvo}>).*"


def com(texto, pasta):
    return f"{texto.rstrip()}\n\n{rodape(pasta)}\n" if texto.strip() else f"{rodape(pasta)}\n"


PASTA_FUNDA = f"{palavra()}/{palavra()}"
SEM, CERTO, VELHO, ESPALHADO, NOVO, VAZIO = (
    f"{palavra()}{EXTENSAO}", f"{palavra()}/{palavra()}{EXTENSAO}", f"{PASTA_FUNDA}/{palavra()}{EXTENSAO}",
    f"{palavra()}/{palavra()}{EXTENSAO}", f"{palavra()}{EXTENSAO}", f"{palavra()}{EXTENSAO}")
IGNORADO, DE_FORA = f"{palavra()}{EXTENSAO}", f"{DADOS}/{palavra()}-{CABECALHO}{EXTENSAO}"
OUTRO = f"{palavra()}{OUTRA_EXTENSAO}"
MODELO = f"{DADOS}/{palavra()}{EXTENSAO}"
CORPOS = {nome: corpo() for nome in (SEM, CERTO, VELHO, ESPALHADO, NOVO, IGNORADO, DE_FORA, OUTRO)}
CORPOS[SEM] += f"\n{corpo()}"  # mais de um paragrafo: a ultima linha com texto nao e a primeira
CORPOS[VAZIO] = ""
ARQUIVOS = {
    LICENCA: frase(), SEM: CORPOS[SEM], CERTO: com(CORPOS[CERTO], Path(CERTO).parent),
    VELHO: com(CORPOS[VELHO], "."),  # o rodape de um documento de outra pasta
    ESPALHADO: f"{CORPOS[ESPALHADO]} \n\n\n{rodape(Path(ESPALHADO).parent).replace(' ', '  ', 2)}  \n\n",
    NOVO: CORPOS[NOVO], VAZIO: "", IGNORADO: CORPOS[IGNORADO], DE_FORA: CORPOS[DE_FORA], OUTRO: CORPOS[OUTRO],
    MODELO: f"\n{rodape(DADOS)}\n\n", ".gitignore": f"{IGNORADO}\n",
}
RAIZ.mkdir()
git(RAIZ, "init", "-q")
for nome, texto in ARQUIVOS.items():
    (RAIZ / nome).parent.mkdir(parents=True, exist_ok=True)
    (RAIZ / nome).write_text(texto, encoding="utf-8")
git(RAIZ, "add", "--", *(nome for nome in ARQUIVOS if nome not in (NOVO, IGNORADO)))
CONFIGURACAO = {"versao_schema": 1, "documentos": [f"*{EXTENSAO}"], "fora": [f"{DADOS}/*-{CABECALHO}{EXTENSAO}"]}
CONF = grava_json(TRABALHO / f"{palavra()}.json", CONFIGURACAO)


def ultima_com_texto(texto):
    return max([k for k, linha in enumerate(texto.split("\n"), 1) if linha.strip()], default=1)


def linha_do_rodape(texto):
    return texto.split("\n").index(DIVISOR) + 1


DOCUMENTOS = sorted([SEM, CERTO, VELHO, ESPALHADO, NOVO, VAZIO])
FALTAM = {SEM: ultima_com_texto(ARQUIVOS[SEM]), NOVO: ultima_com_texto(ARQUIVOS[NOVO]), VAZIO: 1}
FORA_DA_FORMA = {VELHO: linha_do_rodape(ARQUIVOS[VELHO]), ESPALHADO: linha_do_rodape(ARQUIVOS[ESPALHADO])}
ESPERADOS = sorted({**FALTAM, **FORA_DA_FORMA}.items())
ANTES = {nome: (RAIZ / nome).read_bytes() for nome in ARQUIVOS}

codigo, saida = roda(RAIZ, CONF, RAIZ / MODELO, conferir=True)
achados = [m.groups() for m in map(ERRO.match, saida) if m]
confere([(d, int(n)) for d, n, _ in achados] == ESPERADOS,
        f"com --conferir, cada documento fora do dia, e só ele, sai numa linha ERRO com o caminho e a linha, em ordem: "
        f"{achados} no lugar de {ESPERADOS}")
motivos = {d: m for d, _, m in achados}
if confere(set(motivos) == set(FALTAM) | set(FORA_DA_FORMA), f"os motivos de cada documento: {motivos}"):
    confere(len({motivos[d] for d in FALTAM}) == 1 and len({motivos[d] for d in FORA_DA_FORMA}) == 1
            and motivos[SEM] != motivos[VELHO], f"o mesmo problema sai com o mesmo motivo, e os dois, com motivos "
                                                f"diferentes: {motivos}")
confere(len(saida) == len(achados) + 1 and [int(n) for n in NUMERO.findall(saida[-1])] == [len(DOCUMENTOS),
                                                                                           len(ESPERADOS)],
        f"depois das linhas ERRO, só o resumo, com os documentos e os fora do dia: {saida[len(achados):]}")
confere(codigo == 1, f"com documento fora do dia, o --conferir sai com 1: {codigo}")
confere(all((RAIZ / nome).read_bytes() == ANTES[nome] for nome in ARQUIVOS), "o --conferir não grava nada")
confere(roda(RAIZ, CONF, RAIZ / MODELO, conferir=True) == (codigo, saida), "duas rodadas dão a mesma saída")

codigo, saida = roda(RAIZ, CONF, RAIZ / MODELO, conferir=False)
confere(codigo == 0 and len(saida) == len(ESPERADOS) + 1
        and [int(n) for n in NUMERO.findall(saida[-1])] == [len(DOCUMENTOS), len(ESPERADOS)]
        and all(any(nome in linha for linha in saida[:-1]) for nome, _ in ESPERADOS),
        f"sem --conferir, uma linha por documento gravado e o resumo, com 0: {codigo}, {saida}")
for nome in DOCUMENTOS:
    certo = com(CORPOS[nome], Path(nome).parent)
    confere((RAIZ / nome).read_text(encoding="utf-8") == certo,
            f"{nome}: o documento termina no rodapé dele, sem o velho: {(RAIZ / nome).read_text(encoding='utf-8')!r}")
confere((RAIZ / VAZIO).read_text(encoding="utf-8") == f"{rodape('.')}\n", "o documento vazio fica só com o rodapé")
confere(all((RAIZ / nome).read_bytes() == ANTES[nome] for nome in (IGNORADO, DE_FORA, OUTRO, MODELO, LICENCA)),
        "o documento que o .gitignore deixa de fora, o que segue um padrão de fora, o de outra extensão e o modelo "
        "ficam como estão")
codigo, saida = roda(RAIZ, CONF, RAIZ / MODELO, conferir=True)
confere(codigo == 0 and len(saida) == 1 and [int(n) for n in NUMERO.findall(saida[0])] == [len(DOCUMENTOS), 0],
        f"depois de gravar, o --conferir sai só com o resumo e com 0: {codigo}, {saida}")
DEPOIS = {nome: (RAIZ / nome).read_bytes() for nome in ARQUIVOS}
codigo, saida = roda(RAIZ, CONF, RAIZ / MODELO, conferir=False)
confere(codigo == 0 and len(saida) == 1 and all((RAIZ / n).read_bytes() == DEPOIS[n] for n in ARQUIVOS),
        f"outra rodada não muda nada: {codigo}, {saida}")


def nao_serve(nome, raiz, configuracao, modelo, diz, intactos=()):
    """A rodada que nao serve sai com 2, so com uma linha ERRO que diz a pasta ou o arquivo, e nao grava nada."""
    antes = {n: (raiz / n).read_bytes() for n in intactos}
    codigo, saida = roda(raiz, configuracao, modelo, conferir=False)
    confere(codigo == 2 and len(saida) == 1 and saida[0].startswith("ERRO") and str(diz) in saida[0]
            and all((raiz / n).read_bytes() == b for n, b in antes.items()),
            f"{nome}: sai com 2, só com uma linha ERRO que diz {diz}, sem gravar nada: {codigo}, {saida}")


SEM_GIT = TRABALHO / palavra()
SEM_GIT.mkdir()
nao_serve("a pasta sem git", SEM_GIT, CONF, RAIZ / MODELO, SEM_GIT)
NAO_E_JSON = TRABALHO / f"{palavra()}.json"
NAO_E_JSON.write_text("{" + palavra(), encoding="utf-8")
CONFIGURACOES = {
    "que não é JSON": NAO_E_JSON,
    "de outra versão": dict(CONFIGURACAO, versao_schema=2),
    "sem um campo": {k: v for k, v in CONFIGURACAO.items() if k != "fora"},
    "com campo que o molde não conhece": dict(CONFIGURACAO, **{palavra(): [palavra()]}),
    "sem documentos": dict(CONFIGURACAO, documentos=[]),
    "com padrão repetido": dict(CONFIGURACAO, fora=CONFIGURACAO["fora"] * 2),
    "com padrão de mais de uma linha": dict(CONFIGURACAO, documentos=[f"*{EXTENSAO}\n{palavra()}"]),
}
for nome, dados in CONFIGURACOES.items():
    caminho = dados if isinstance(dados, Path) else grava_json(TRABALHO / f"{palavra()}.json", dados)
    nao_serve(f"a configuração {nome}", RAIZ, caminho, RAIZ / MODELO, caminho)
MODELOS = {"que falta": None, "vazio": " \n\n", "com código": f"{frase()} `{palavra()}`",
           "com link para um arquivo que não existe": f"{frase()} [{palavra()}]({palavra()}.txt)"}
for nome, texto in MODELOS.items():
    caminho = RAIZ / DADOS / f"{palavra()}{EXTENSAO}"
    if texto is not None:
        caminho.write_text(texto, encoding="utf-8")
    nao_serve(f"o modelo {nome}", RAIZ, CONF, caminho, caminho)
    if texto is not None:
        caminho.unlink()
ILEGIVEL = TRABALHO / palavra()
ANTES_DELE, DELE = sorted(f"{palavra()}{EXTENSAO}" for _ in range(2))  # o que se grava vem antes do ilegivel
ILEGIVEL.mkdir()
git(ILEGIVEL, "init", "-q")
(ILEGIVEL / LICENCA).parent.mkdir(parents=True)
(ILEGIVEL / LICENCA).write_text(frase(), encoding="utf-8")
(ILEGIVEL / DADOS).mkdir()
(ILEGIVEL / MODELO).write_text(rodape(DADOS), encoding="utf-8")
(ILEGIVEL / ANTES_DELE).write_text(corpo(), encoding="utf-8")
(ILEGIVEL / DELE).write_bytes(f"{frase()} ç".encode("latin-1"))
nao_serve("o documento que não se lê em UTF-8", ILEGIVEL, CONF, ILEGIVEL / MODELO, DELE, intactos=(ANTES_DELE,))

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
