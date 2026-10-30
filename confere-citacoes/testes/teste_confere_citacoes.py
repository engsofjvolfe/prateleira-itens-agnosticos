"""Testes do confere_citacoes.py, com configuracao, fontes e textos inventados aqui: as
marcas da referencia e do trecho, o modelo do titulo de pagina, a marca de supressao, os
grupos de equivalentes e as palavras sao sorteados, com letras de fora do ASCII. Conferem
o que a peca faz, nunca uma frase pronta: em que arquivo e linha sai cada ERRO, o codigo
de saida e o resumo contando os erros que sairam. Casos: trecho certo na pagina citada; o
mesmo trecho com outra pagina; trecho que cruza duas paginas, com o intervalo e so com uma
delas; trecho que aparece em duas paginas; equivalentes; espacos e quebras de linha
diferentes; pedacos partidos na supressao, com pontas; pagina de rotulo que nao e numero;
trecho que so esta num bloco ignorado ou antes da primeira pagina; maiusculas; paginas que
nao se leem; fonte que nao existe ou com bloco que nao fecha; referencia sem trecho e
trecho sem referencia; configuracao e argumentos que nao servem (codigo 2); duas rodadas
dao o mesmo. Uso:
    python3 -I teste_confere_citacoes.py <pasta do confere_citacoes.py> <pasta de trabalho nova>
"""
import json
import random
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

PECA, TRABALHO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
SCRIPT = PECA / "confere_citacoes.py"
FALHAS = []
SORTEIO = random.Random(7)
LETRAS = "abcdefghijklmnop" + "áçõüéñ"  # com letras de fora do ASCII
SIMBOLOS = "@#%&=+!?"


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


def palavra():
    return "".join(SORTEIO.choice(LETRAS) for _ in range(SORTEIO.randint(4, 9)))


def frase(n):
    return " ".join(palavra() for _ in range(n))


def marca():
    return "".join(SORTEIO.choice(SIMBOLOS) for _ in range(3)) + palavra()


def roda(configuracao, fontes, *textos):
    """(codigo, [(arquivo, linha) de cada ERRO], linhas que sairam)."""
    r = subprocess.run([sys.executable, "-I", str(SCRIPT), str(configuracao), str(fontes), *map(str, textos)],
                       capture_output=True, text=True, encoding="utf-8")
    linhas = r.stdout.strip().split("\n") if r.stdout.strip() else []
    erros = []
    for linha in linhas:
        m = re.match(r"^ERRO (.+?):(\d+): ", linha)
        if m:
            erros.append((m.group(1), int(m.group(2))))
    return r.returncode, erros, linhas


def numeros_do_resumo(linhas):
    return [int(n) for n in re.findall(r"\d+", linhas[-1])] if linhas else []


TRABALHO.mkdir(parents=True)
FONTES = TRABALHO / palavra()
FONTES.mkdir()

# a configuracao inventada
REF, ABRE, FECHA = marca(), marca(), marca()
SEP, INTERVALO = SORTEIO.choice([(",", "~"), (";", "-"), ("/", "~")])
SUPRESSAO = SORTEIO.choice(["[...]", "(…)", "<-->"])
PONTAS = " .,;:"
TITULO = f"{marca()} {{rotulo}} {marca()} {{arquivo}} {marca()}"
IMAGEM_ABRE, IMAGEM_FECHA = marca(), marca()
MODELO_ARQUIVO = f"{palavra()}-{{fonte}}.{palavra()}"
CONFIGURACAO = {
    "versao_schema": 1,
    "referencia": f"^{re.escape(REF)} (?P<fonte>\\S+) \\| (?P<paginas>.+)$",
    "citacao": f"^{re.escape(ABRE)}(?P<trecho>.+){re.escape(FECHA)}$",
    "paginas": {"separador": SEP, "intervalo": INTERVALO},
    "fontes": {"arquivo": MODELO_ARQUIVO, "titulo_pagina": TITULO,
               "ignorar": [{"abre": f"^{re.escape(IMAGEM_ABRE)}", "fecha": f"^{re.escape(IMAGEM_FECHA)}$"}]},
    "supressao": SUPRESSAO,
    "pontas": PONTAS,
    "equivalentes": ["'’‘", "-–"],
}


def grava_configuracao(dados, nome=None):
    caminho = TRABALHO / f"{nome or palavra()}.json"
    caminho.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    return caminho


def titulo(rotulo, arquivo):
    return TITULO.replace("{rotulo}", str(rotulo)).replace("{arquivo}", str(arquivo))


def grava_fonte(nome, linhas):
    (FONTES / MODELO_ARQUIVO.replace("{fonte}", nome)).write_text("\n".join(linhas) + "\n", encoding="utf-8")


# a fonte inventada: quatro paginas, a ultima com rotulo que nao e numero
A = SORTEIO.randint(10, 500)
B, C, D = A + 1, A + 2, "r" + palavra()
ANTES, P1, P3, P4, P7 = frase(8), frase(9), frase(8), frase(7), frase(8)
P2_INICIO, P2_FIM = frase(5), frase(5)
P5_A, P5_B = frase(4), frase(4)
P6_A, P6_B = frase(4), frase(4)
P8 = f"{frase(3)} {palavra()}é{palavra()} {frase(2)}"  # com letra que o NFD decompoe
FONTE = palavra()
grava_fonte(FONTE, [
    ANTES,
    titulo(A, 1), frase(6), P1 + ".", frase(5), P6_A, P6_B + ",", frase(4), P4 + ";", frase(6),
    titulo(B, 2), frase(6), IMAGEM_ABRE + " " + palavra(), P3, IMAGEM_FECHA, frase(5), P2_INICIO,
    titulo(C, 3), P2_FIM + ".", f"{P5_A}  \t’{P5_B}’ {frase(3)}", P4 + ".", frase(6),
    titulo(D, 4), frase(3), P7, P8, frase(4),
])
QUEBRADA = palavra()  # fonte com um bloco ignorado que nao fecha
grava_fonte(QUEBRADA, [titulo(A, 1), frase(6), IMAGEM_ABRE, frase(4), titulo(B, 2), frase(6)])


def cita(fonte, paginas, trecho):
    return [f"{REF} {fonte} | {paginas}", f"{ABRE}{trecho}{FECHA}"]


def pags(*partes):
    return f"{SEP} ".join(str(p) for p in partes)


def intervalo(de, ate):
    return f"{de}{INTERVALO}{ate}"


def monta(blocos):
    """(linhas do texto, [linha esperada do ERRO de cada bloco que erra]); cada bloco e
    (linhas, deslocamento da linha do erro dentro do bloco, ou None quando nao erra)."""
    linhas, esperados = [f"# {frase(3)}", ""], []
    for bloco, erro in blocos:
        linhas += [frase(10), ""]
        if erro is not None:
            esperados.append(len(linhas) + 1 + erro)
        linhas += bloco + [""]
    return linhas, esperados


P1_PALAVRAS = P1.split()
certos, _ = monta([
    (cita(FONTE, A, P1), None),
    (cita(FONTE, intervalo(B, C), f"{P2_INICIO} {P2_FIM}"), None),
    (cita(FONTE, C, P4), None),
    (cita(FONTE, C, f"{P5_A} '{P5_B}'"), None),
    (cita(FONTE, A, f"{P6_A}   {P6_B}"), None),
    (cita(FONTE, A, f"{' '.join(P1_PALAVRAS[:3])} {SUPRESSAO} {' '.join(P1_PALAVRAS[-3:])}:"), None),
    (cita(FONTE, D, P7), None),
    (cita(FONTE, D, unicodedata.normalize("NFD", P8)), None),
    (cita(FONTE, pags(A, C), P4), None),
    (cita(FONTE, pags(B, A), "  ".join(P1_PALAVRAS)), None),
])
errados, ESPERADOS = monta([
    (cita(FONTE, B, P1), 1),
    (cita(FONTE, B, f"{P2_INICIO} {P2_FIM}"), 1),
    (cita(FONTE, B, P3), 1),
    (cita(FONTE, A, ANTES), 1),
    (cita(FONTE, A, P1.upper()), 1),
    (cita(FONTE, intervalo(C, A), P1), 0),
    (cita(FONTE, f"{A}{SEP}", P1), 0),
    (cita(palavra(), A, P1), 0),
    (cita(QUEBRADA, A, frase(3)), 0),
    ([cita(FONTE, A, P1)[0], frase(4)], 0),
    ([cita(FONTE, A, P1)[1]], 0),
    (cita(FONTE, A, f"{' '.join(P1_PALAVRAS[:3])} {SUPRESSAO} {frase(4)}"), 1),
])
CERTO, ERRADO = TRABALHO / f"{palavra()}.md", TRABALHO / f"{palavra()}.md"
CERTO.write_text("\n".join(certos) + "\n", encoding="utf-8")
ERRADO.write_text("\n".join(errados) + "\n", encoding="utf-8")
CONF = grava_configuracao(CONFIGURACAO)

codigo, erros, linhas = roda(CONF, FONTES, CERTO)
confere(codigo == 0 and not erros, f"o texto só com citações certas sai sem ERRO e com 0: {codigo}, {linhas}")
confere(numeros_do_resumo(linhas)[-1:] == [0], f"o resumo conta 0 erro: {linhas[-1:]}")

codigo, erros, linhas = roda(CONF, FONTES, CERTO, ERRADO)
achados = sorted({linha for arquivo, linha in erros if arquivo == str(ERRADO)})
confere(codigo == 1, f"com citação errada sai com 1: {codigo}")
confere(not [e for e in erros if e[0] != str(ERRADO)], f"nenhum ERRO no texto certo: {erros}")
confere(achados == sorted(ESPERADOS),
        f"um ERRO em cada citação errada, na linha certa: {achados} != {sorted(ESPERADOS)}")
confere(numeros_do_resumo(linhas)[-1:] == [len(erros)], f"o resumo conta os ERRO que saíram: {linhas[-1:]}")
confere(roda(CONF, FONTES, CERTO, ERRADO)[2] == linhas, "duas rodadas dão o mesmo")


def com(caminho, valor):
    """Uma copia da configuracao com o valor no caminho ("a/b"); None tira o campo."""
    dados = json.loads(json.dumps(CONFIGURACAO))
    alvo, partes = dados, caminho.split("/")
    for parte in partes[:-1]:
        alvo = alvo[parte]
    if valor is None:
        del alvo[partes[-1]]
    else:
        alvo[partes[-1]] = valor
    return grava_configuracao(dados)


ESTRAGADAS = {
    "campo que o molde não conhece": com(palavra(), palavra()),
    "campo que falta": com("pontas", None),
    "expressão que não compila": com("referencia", "(?P<fonte>"),
    "referência sem o grupo das páginas": com("referencia", f"^{re.escape(REF)} (?P<fonte>\\S+)"),
    "trecho sem o grupo do trecho": com("citacao", f"^{re.escape(ABRE)}(.+)$"),
    "modelo de arquivo com outro campo": com("fontes/arquivo", "{fonte}-{" + palavra() + "}"),
    "grupo de equivalentes de um caractere só": com("equivalentes", ["x"]),
    "supressão vazia": com("supressao", ""),
}
for nome, caminho in ESTRAGADAS.items():
    codigo, erros, linhas = roda(caminho, FONTES, CERTO)
    confere(codigo == 2 and not erros, f"configuração com {nome} sai com 2, sem conferir: {codigo}, {linhas}")
codigo, erros, _ = roda(CONF, TRABALHO / palavra(), CERTO)
confere(codigo == 2 and not erros, f"pasta das fontes que não existe sai com 2: {codigo}")
codigo, erros, _ = roda(CONF, FONTES, TRABALHO / f"{palavra()}.md")
confere(codigo == 2 and not erros, f"texto que não existe sai com 2: {codigo}")
LATIN = TRABALHO / f"{palavra()}.md"
LATIN.write_bytes("\n".join(certos).encode("latin-1", errors="replace") + b"\xe9\xff")
codigo, erros, _ = roda(CONF, FONTES, LATIN)
confere(codigo == 2 and not erros, f"texto que não se lê em UTF-8 sai com 2: {codigo}")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
