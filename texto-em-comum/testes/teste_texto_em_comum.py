"""Testes do texto_em_comum.py, com pastas e textos inventados aqui. As palavras sao sorteadas
com semente fixa (o sorteio e o mesmo em toda rodada; outra semente pode vir como terceiro
argumento), cada uma diferente das outras e com acento, para que so o texto copiado de
proposito seja comum. Conferem regras, nunca uma frase pronta:
  - um trecho de L palavras copiado (L >= N), com outras maiusculas, acentos na forma NFD e
    outra pontuacao e quebra de linha entre as palavras, da L - N + 1 sequencias em comum,
    contadas no arquivo de onde veio; um trecho de N - 1 palavras nao da nenhuma;
  - o mais parecido e o arquivo com mais sequencias; no empate, o da primeira pasta dada;
  - arquivo vazio e texto sem sequencias; arquivo com o byte zero (tambem longe do comeco)
    ou fora do UTF-8 nao e texto; o codigo de saida diz se ha texto em comum ou arquivo que
    nao e texto;
  - o que casa com --pular fica de fora nos dois lados, tambem com --lista, e sem --pular
    entra;
  - um arquivo nao e comparado com ele mesmo, nem quando duas pastas comparadas chegam a
    ele, e o relatorio nao e lido;
  - com --lista (de arquivo ou da entrada padrao), so os arquivos dela, cada um uma vez;
    lista ou argumento que nao serve da o codigo 2 e nao grava nada;
  - o relatorio tem uma linha por arquivo, em ordem de caminho, e duas rodadas dao a mesma
    saida.
Uso:
    python3 -I teste_texto_em_comum.py <pasta do texto_em_comum.py> <pasta de trabalho nova> [semente]
"""
import csv
import random
import string
import subprocess
import sys
import unicodedata
from pathlib import Path

PECA, TRABALHO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
FALHAS = []
SORTEIO = random.Random(int(sys.argv[3]) if len(sys.argv) > 3 else 1)
LETRAS = string.ascii_lowercase
ACENTOS = "áâãçéêíóôõúü"
SEPARADORES = [" ", "\n", ", ", ". ", " — ", "\n\n", "; ", " (", ") ", "\t", " * "]
N = SORTEIO.randint(4, 9)
USADAS = set()


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


def palavra():
    """Uma palavra nova, com pelo menos um acento."""
    while True:
        letras = [SORTEIO.choice(LETRAS) for _ in range(SORTEIO.randint(4, 9))]
        letras.insert(SORTEIO.randint(0, len(letras)), SORTEIO.choice(ACENTOS))
        p = "".join(letras)
        if p not in USADAS:
            USADAS.add(p)
            return p


def palavras(k):
    return [palavra() for _ in range(k)]


def junta(lista):
    return "".join(SORTEIO.choice(SEPARADORES) + p for p in lista).lstrip()


def disfarca(lista):
    """As mesmas palavras em maiusculas, com os acentos na forma NFD."""
    return [unicodedata.normalize("NFD", p.upper()) for p in lista]


def escreve(caminho, *pedacos):
    """Grava os pedacos (listas de palavras) separados por palavras novas; devolve quantas
    sequencias de N palavras o arquivo tem (todas as palavras dele sao diferentes)."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    texto = []
    for pedaco in pedacos:
        texto += palavras(SORTEIO.randint(N, 2 * N)) + pedaco
    texto += palavras(SORTEIO.randint(N, 2 * N))
    caminho.write_text(junta(texto), encoding="utf-8")
    return max(0, len(texto) - N + 1)


def nome():
    return "".join(SORTEIO.choice(LETRAS) for _ in range(8))


def roda(examinada, comparadas, saida, *opcoes, entrada=None):
    r = subprocess.run([sys.executable, "-I", str(PECA / "texto_em_comum.py"), str(examinada),
                        *map(str, comparadas), "--palavras", str(N), "--saida", str(saida), *opcoes],
                       capture_output=True, text=True, input=entrada)
    return r.returncode, r.stdout + r.stderr


def relatorio(saida):
    """{arquivo: {coluna: valor}} e a lista dos arquivos na ordem do relatorio."""
    with open(saida, encoding="utf-8", newline="") as f:
        cabeca, *linhas = list(csv.reader(f, delimiter="\t"))
    return {l[0]: dict(zip(cabeca, l)) for l in linhas}, [l[0] for l in linhas]


def comprimento():
    return SORTEIO.randint(N, N + 6)


# ---------- as pastas inventadas ----------

A, B, EX = TRABALHO / nome(), TRABALHO / nome(), TRABALHO / nome()
PREFIXO = nome()[:3] + "-"  # nome() nunca tem hifen: so as pastas escondidas comecam assim
ESCONDIDA_A, ESCONDIDA_EX = f"{PREFIXO}{nome()}", f"{PREFIXO}{nome()}"
FONTE1, FONTE2, FONTE3 = palavras(200), palavras(200), palavras(60)
escreve(A / nome() / "fonte1.txt", FONTE1)
escreve(B / "fonte2.md", FONTE2)
escreve(A / ESCONDIDA_A / "fonte3.txt", FONTE3)
F1, F2 = str(next(A.rglob("fonte1.txt"))), str(B / "fonte2.md")

L1, L2, L3, LE, LP = comprimento(), comprimento(), comprimento(), comprimento(), comprimento()
while L3 == L2:
    L3 = comprimento()
COPIA = EX / nome() / nome() / "copia.md"
ESPERADO = {  # arquivo: (sequencias, em_comum, mais_parecido, em_comum_com_ele)
    COPIA.relative_to(EX).as_posix(): (escreve(COPIA, disfarca(FONTE1[:L1])), L1 - N + 1, F1, L1 - N + 1),
    "dois.txt": (escreve(EX / "dois.txt", FONTE1[50:50 + L2], disfarca(FONTE2[:L3])), L2 + L3 - 2 * N + 2,
                 F1 if L2 > L3 else F2, max(L2, L3) - N + 1),
    "empate.md": (escreve(EX / "empate.md", FONTE2[100:100 + LE], FONTE1[100:100 + LE]), 2 * (LE - N + 1), F1,
                  LE - N + 1),
    "curta.md": (escreve(EX / "curta.md", FONTE1[150:150 + N - 1]), 0, "", 0),
    "sozinho.md": (escreve(EX / "sozinho.md"), 0, "", 0),
    "de-escondida.md": (escreve(EX / "de-escondida.md", FONTE3[:LP]), 0, "", 0),
}
escreve(EX / ESCONDIDA_EX / "x.md", FONTE1[:L1])
(EX / "vazio.md").write_text("", encoding="utf-8")
NAO_TEXTO = ["binario.dat", "latin.txt", "zero-no-fim.txt"]
(EX / "binario.dat").write_bytes(bytes(SORTEIO.randrange(256) for _ in range(300)) + b"\0")
(EX / "latin.txt").write_bytes(" ".join(palavras(20)).encode("latin-1"))
(EX / "zero-no-fim.txt").write_bytes(" ".join(palavras(20000)).encode("utf-8") + b"\0")


def todos(pasta, pular=()):
    return sorted(p.relative_to(pasta).as_posix() for p in pasta.rglob("*")
                  if p.is_file() and not any(parte.startswith(pular) for parte in p.relative_to(pasta).parts))


# ---------- a rodada completa ----------

SAIDA = TRABALHO / "r1.tsv"
cod, out = roda(EX, [A, B], SAIDA, "--pular", f"{PREFIXO}*")
linhas, ordem = relatorio(SAIDA)
confere(cod == 1, f"com texto em comum, o código é 1: {cod} {out}")
confere(ordem == todos(EX, (PREFIXO,)), f"uma linha por arquivo, em ordem de caminho, sem o que foi pulado: {ordem}")
for arquivo, esperado in ESPERADO.items():
    l = linhas.get(arquivo, {})
    confere(l.get("texto") == "sim" and [l.get(c) for c in ("sequencias", "em_comum", "mais_parecido",
                                                            "em_comum_com_ele")] == list(map(str, esperado)),
            f"{arquivo}: esperado (sequências, em comum, mais parecido, com ele) {esperado}; veio {l}")
confere(linhas.get("vazio.md", {}).get("texto") == "sim" and linhas["vazio.md"].get("sequencias") == "0",
        f"o arquivo vazio é texto sem sequências: {linhas.get('vazio.md')}")
for arquivo in NAO_TEXTO:
    l = linhas.get(arquivo, {})
    confere(l.get("texto") == "não" and l.get("em_comum") == "",
            f"{arquivo} não é texto: {l}")

cod2, out2 = roda(EX, [A, B], TRABALHO / "r2.tsv", "--pular", f"{PREFIXO}*")
confere(cod2 == cod and out2 == out and (TRABALHO / "r2.tsv").read_bytes() == SAIDA.read_bytes(),
        "duas rodadas dão a mesma saída")

cod, out = roda(EX, [B, A], TRABALHO / "r3.tsv", "--pular", f"{PREFIXO}*")
l = relatorio(TRABALHO / "r3.tsv")[0].get("empate.md", {})
confere(l.get("mais_parecido") == F2, f"no empate, o mais parecido é o da primeira pasta dada: {l}")

cod, out = roda(EX, [A, B], TRABALHO / "r4.tsv")
linhas, ordem = relatorio(TRABALHO / "r4.tsv")
confere(ordem == todos(EX), f"sem --pular, todos os arquivos entram: {ordem}")
confere(linhas.get("de-escondida.md", {}).get("em_comum") == str(LP - N + 1),
        f"sem --pular, a pasta comparada que era pulada entra: {linhas.get('de-escondida.md')}")

# ---------- so texto, sem nada em comum ----------

LIMPA = TRABALHO / nome()
escreve(LIMPA / "a.md")
escreve(LIMPA / nome() / "b.txt")
cod, out = roda(LIMPA, [A, B], TRABALHO / "r5.tsv")
confere(cod == 0, f"só texto e nada em comum: código 0: {cod} {out}")
(LIMPA / "c.dat").write_bytes(b"\0")
cod, out = roda(LIMPA, [A, B], TRABALHO / "r6.tsv")
confere(cod == 1, f"um arquivo que não é texto: código 1: {cod} {out}")

# ---------- a pasta comparada com ela mesma, e o relatorio dentro dela ----------

MESMA = TRABALHO / nome()
UM = palavras(80)
escreve(MESMA / "um.md", UM)
LM = comprimento()
escreve(MESMA / "dois.md", UM[10:10 + LM])
escreve(MESMA / "tres.md")
SAIDA_DENTRO = MESMA / "relatorio.tsv"
cod, out = roda(MESMA, [MESMA], SAIDA_DENTRO)
cod2, out2 = roda(MESMA, [MESMA], SAIDA_DENTRO)
linhas, ordem = relatorio(SAIDA_DENTRO)
confere(linhas.get("um.md", {}).get("em_comum") == str(LM - N + 1)
        and linhas["um.md"].get("mais_parecido") == str(MESMA / "dois.md"),
        f"um arquivo não é comparado com ele mesmo: {linhas.get('um.md')}")
confere(linhas.get("tres.md", {}).get("em_comum") == "0", f"o arquivo sozinho não tem nada em comum: {linhas}")
confere(ordem == ["dois.md", "tres.md", "um.md"] and out2 == out,
        f"o relatório não é lido, nem examinado nem comparado: {ordem} {out} {out2}")
cod, out = roda(MESMA, [MESMA, TRABALHO], TRABALHO / "r9.tsv")
linhas = relatorio(TRABALHO / "r9.tsv")[0]
confere(linhas.get("tres.md", {}).get("em_comum") == "0"
        and linhas.get("um.md", {}).get("mais_parecido") == str(MESMA / "dois.md"),
        f"o arquivo achado por duas pastas comparadas conta uma vez, na primeira, e não casa com ele mesmo: {linhas}")

# ---------- a lista ----------

ESCOLHIDOS = sorted(SORTEIO.sample(todos(EX), 3))
LISTA = TRABALHO / "lista.txt"
LISTA.write_text("\n".join([ESCOLHIDOS[1], "", ESCOLHIDOS[0], ESCOLHIDOS[2], ESCOLHIDOS[0]]) + "\n", encoding="utf-8")
cod, out = roda(EX, [A, B], TRABALHO / "r7.tsv", "--lista", str(LISTA))
confere(relatorio(TRABALHO / "r7.tsv")[1] == ESCOLHIDOS, f"com --lista, só os arquivos dela, cada um uma vez: {out}")
cod, out = roda(EX, [A, B], TRABALHO / "r8.tsv", "--lista", "-", entrada=LISTA.read_text(encoding="utf-8"))
confere((TRABALHO / "r8.tsv").read_bytes() == (TRABALHO / "r7.tsv").read_bytes(),
        "a lista pela entrada padrão dá o mesmo relatório")
FORA_DO_PULO = todos(EX, (PREFIXO,))[0]
cod, out = roda(EX, [A, B], TRABALHO / "r10.tsv", "--lista", "-", "--pular", f"{PREFIXO}*",
                entrada=f"{ESCONDIDA_EX}/x.md\n{FORA_DO_PULO}\n")
confere(relatorio(TRABALHO / "r10.tsv")[1] == [FORA_DO_PULO], f"com --lista, --pular vale também: {out}")

# ---------- o que nao serve ----------

ERRADAS = {"caminho que não existe": nome(), "caminho para fora da pasta": f"../{B.name}/fonte2.md",
           "caminho absoluto": F2, "pasta em vez de arquivo": ESCONDIDA_EX}
for descricao, caminho in ERRADAS.items():
    saida = TRABALHO / f"{nome()}.tsv"
    cod, out = roda(EX, [A, B], saida, "--lista", "-", entrada=f"{ESCOLHIDOS[0]}\n{caminho}\n")
    confere(cod == 2 and not saida.exists(), f"lista com {descricao}: código 2, nada gravado: {cod} {out}")
for descricao, examinada, comparadas, saida, opcoes in (
        ("--palavras 0", EX, [A], TRABALHO / f"{nome()}.tsv", ["--palavras", "0"]),
        ("pasta examinada que não existe", TRABALHO / nome(), [A], TRABALHO / f"{nome()}.tsv", []),
        ("pasta comparada que não existe", EX, [A, TRABALHO / nome()], TRABALHO / f"{nome()}.tsv", []),
        ("pasta do relatório que não existe", EX, [A], TRABALHO / nome() / "r.tsv", [])):
    cod, out = roda(examinada, comparadas, saida, *opcoes)
    confere(cod == 2 and not saida.exists(), f"{descricao}: código 2, nada gravado: {cod} {out}")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
