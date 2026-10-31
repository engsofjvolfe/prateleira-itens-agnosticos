"""Testes do estraga.py, com uma peca inventada aqui (uma funcao que soma e um texto), testes
inventados dela e listas de estragos inventadas. Conferem regras, nunca uma frase pronta:
o estrago que quebra o que o teste confere e pego, o que nao quebra nao e, e o que nao se
aplica e erro; a contagem do fim e a das linhas; o codigo de saida diz se todos foram
pegos; a peca original nao muda; com --so, so rodam os estragos que batem com algum
filtro, na ordem da lista, e o filtro sem o sinal ou que nao bate com nenhum e erro; os
argumentos de --antes chegam ao teste; cada pasta de --irma fica ao lado da copia, sem a
pasta testes/, e duas com o mesmo nome sao erro; lista com campo desconhecido ou que falta
e pasta de trabalho que nao esta vazia sao erro; com erro, que sai com codigo 2, nada roda;
duas rodadas dao a mesma saida. Uso:
    python3 -I teste_estraga.py <pasta do estraga.py> <pasta de trabalho nova>
Precisa do extrator_comum.py, do extrator, na pasta irma "extrator" ou na mesma pasta.
"""
import json
import random
import re
import string
import subprocess
import sys
from pathlib import Path

PECA, TRABALHO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
FALHAS = []
SORTEIO = random.Random(1)


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


def nome():
    return "".join(SORTEIO.choice(string.ascii_lowercase) for _ in range(8))


# a peca inventada e os testes dela, escritos fora dela
PECA_INVENTADA = TRABALHO / "peca"
(PECA_INVENTADA / "testes").mkdir(parents=True)
COMENTARIO, TEXTO, ARQUIVO_DE_TEXTO = nome(), nome(), f"{nome()}.txt"
(PECA_INVENTADA / "calculo.py").write_text(f"def soma(a, b):\n    return a + b  # {COMENTARIO}\n", encoding="utf-8")
(PECA_INVENTADA / ARQUIVO_DE_TEXTO).write_text(f"{TEXTO}\n", encoding="utf-8")
(PECA_INVENTADA / "testes" / "nada.txt").write_text("", encoding="utf-8")
ARGUMENTO = nome()
IRMAS = {nome(): nome() for _ in range(2)}  # cada pasta irma inventada e a marca que ela tem
IRMA, MARCA = next(iter(IRMAS.items()))
CABECA = """import random, sys
from pathlib import Path
peca, *extra, trabalho = sys.argv[1:]
sys.path.insert(0, peca)
import calculo
r = random.Random(2)
ok = all(calculo.soma(a, b) == a + b for a, b in ((r.randint(-99, 99), r.randint(-99, 99)) for _ in range(50)))
"""
TESTES = {
    "soma": CABECA + "sys.exit(0 if ok else 1)\n",
    "argumento": CABECA + f"sys.exit(0 if ok and extra == [{ARGUMENTO!r}] else 1)\n",
    "irma": CABECA + f"irma = Path(peca).parent / {IRMA!r}\n"
                     f"sys.exit(0 if ok and (irma / {MARCA!r}).is_file() and not (irma / 'testes').exists() else 1)\n",
    "irmas": CABECA + f"pastas = [(Path(peca).parent / i, m) for i, m in {list(IRMAS.items())!r}]\n"
                      "sys.exit(0 if ok and all((p / m).is_file() and not (p / 'testes').exists() for p, m in pastas)"
                      " else 1)\n",
}
for t, codigo in TESTES.items():
    (TRABALHO / f"teste_{t}.py").write_text(codigo, encoding="utf-8")
for irma, marca in IRMAS.items():
    (TRABALHO / irma / "testes").mkdir(parents=True)
    (TRABALHO / irma / marca).write_text("", encoding="utf-8")
GEMEAS = [TRABALHO / nome() / IRMA for _ in range(2)]  # duas pastas com o mesmo nome, em lugares diferentes
for gemea in GEMEAS:
    gemea.mkdir(parents=True)

QUEBRA = {"nome": "quebra", "arquivo": "calculo.py", "de": "a + b", "para": "a - b"}
INOFENSIVO = {"nome": "inofensivo", "arquivo": "calculo.py", "de": COMENTARIO, "para": nome()}
AUSENTE = {"nome": "ausente", "arquivo": "calculo.py", "de": nome(), "para": "x"}
NO_TEXTO = {"nome": "no-texto", "arquivo": ARQUIVO_DE_TEXTO, "de": TEXTO, "para": ""}


def lista(nome_, estragos, **extra):
    caminho = TRABALHO / f"{nome_}.json"
    caminho.write_text(json.dumps(dict({"versao_schema": 1, "estragos": estragos}, **extra)), encoding="utf-8")
    return caminho


def roda(nome_, estragos, teste="soma", *opcoes, **extra):
    trabalho = TRABALHO / f"t-{nome_}"
    r = subprocess.run([sys.executable, "-I", str(PECA / "estraga.py"), str(PECA_INVENTADA),
                        str(TRABALHO / f"teste_{teste}.py"), str(lista(nome_, estragos, **extra)), str(trabalho),
                        *opcoes], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr, trabalho


def linha(saida, nome_):
    """A linha do estrago na saida, com a palavra logo depois do nome; None quando ele nao rodou."""
    return re.search(rf"^{re.escape(nome_)}: (\S+)", saida, re.M)


def veredito(saida, nome_):
    """O que a linha do estrago diz: a palavra logo depois do nome."""
    m = linha(saida, nome_)
    return m.group(1) if m else None


def contagem(saida):
    """(pegos, rodados), da linha do fim."""
    m = re.search(r"(\d+) de (\d+)", saida.strip().split("\n")[-1])
    return m.groups() if m else None


def nada_rodou(cod, saida, trabalho):
    return cod == 2 and saida.startswith("ERRO") and not trabalho.exists()


antes = {p: p.read_bytes() for p in PECA_INVENTADA.rglob("*") if p.is_file()}
cod, out, _ = roda("tres", [QUEBRA, INOFENSIVO, AUSENTE])
confere(veredito(out, "quebra") == "pego", f"o estrago que quebra o que o teste confere é pego: {out}")
confere(veredito(out, "inofensivo") not in (None, "pego", "ERRO:"), f"o estrago que não quebra nada não é pego: {out}")
confere(veredito(out, "ausente") == "ERRO:", f"o estrago cujo texto não está no arquivo é erro: {out}")
confere(cod == 1 and contagem(out) == ("1", "3"), f"um de três pego, e o código diz que nem todos: {out}")
confere({p: p.read_bytes() for p in PECA_INVENTADA.rglob("*") if p.is_file()} == antes, "a peça original não muda")
cod2, out2, _ = roda("tres-de-novo", [QUEBRA, INOFENSIVO, AUSENTE])
confere(out2 == out, "duas rodadas dão a mesma saída")
cod, out, _ = roda("so-pegos", [QUEBRA])
confere(cod == 0, f"com todos pegos, o código é 0: {out}")

cod, out, _ = roda("so-nome", [QUEBRA, INOFENSIVO, AUSENTE], "soma", "--so", "nome=quebra")
confere(veredito(out, "quebra") == "pego" and linha(out, "inofensivo") is None and linha(out, "ausente") is None,
        f"--so com um nome só roda o estrago desse nome: {out}")
confere(cod == 0 and contagem(out) == ("1", "1"), f"a contagem e o código são os dos estragos que rodaram: {out}")
cod, out, _ = roda("so-arquivo", [QUEBRA, NO_TEXTO], "soma", "--so", f"arquivo={ARQUIVO_DE_TEXTO}")
confere(linha(out, "no-texto") is not None and linha(out, "quebra") is None,
        f"--so com um arquivo só roda os estragos dele: {out}")
cod, out, _ = roda("so-dois", [QUEBRA, INOFENSIVO, AUSENTE], "soma", "--so", "nome=inofensivo", "--so", "nome=quebra")
ordem = [linha(out, n) for n in ("quebra", "inofensivo")]
confere(all(ordem) and ordem[0].start() < ordem[1].start() and linha(out, "ausente") is None,
        f"--so repetido roda os estragos que batem com qualquer um, na ordem da lista: {out}")
for descricao, filtro in (("sem o sinal", "para"), ("que não bate com nenhum estrago", f"nome={nome()}"),
                          ("com um campo que o estrago não tem", f"{nome()}={TEXTO}")):
    cod, out, trabalho = roda(nome(), [QUEBRA, NO_TEXTO], "soma", "--so", filtro)
    confere(nada_rodou(cod, out, trabalho), f"--so {descricao} é erro, sem rodar nada: {out}")

cod, out, _ = roda("argumento", [dict(INOFENSIVO)], "argumento", "--antes", ARGUMENTO)
confere(veredito(out, "inofensivo") != "pego", f"o argumento de --antes chega ao teste: {out}")
cod, out, _ = roda("sem-argumento", [dict(INOFENSIVO)], "argumento")
confere(veredito(out, "inofensivo") == "pego", f"sem --antes, o teste que pede o argumento falha: {out}")
cod, out, _ = roda("irma", [dict(INOFENSIVO)], "irma", "--irma", str(TRABALHO / IRMA))
confere(veredito(out, "inofensivo") != "pego", f"a pasta de --irma fica ao lado da cópia, sem testes/: {out}")
cod, out, _ = roda("sem-irma", [dict(INOFENSIVO)], "irma")
confere(veredito(out, "inofensivo") == "pego", f"sem --irma, o teste que pede a pasta irmã falha: {out}")
cod, out, _ = roda("irmas", [dict(INOFENSIVO)], "irmas", *[x for i in IRMAS for x in ("--irma", str(TRABALHO / i))])
confere(veredito(out, "inofensivo") != "pego", f"cada pasta de --irma fica ao lado da cópia, sem testes/: {out}")
cod, out, _ = roda("uma-irma", [dict(INOFENSIVO)], "irmas", "--irma", str(TRABALHO / IRMA))
confere(veredito(out, "inofensivo") == "pego", f"com uma pasta de --irma só, o teste que pede as duas falha: {out}")
cod, out, trabalho = roda(nome(), [QUEBRA], "soma", *[x for g in GEMEAS for x in ("--irma", str(g))])
confere(nada_rodou(cod, out, trabalho), f"duas pastas de --irma com o mesmo nome são erro, sem rodar nada: {out}")

for descricao, estragos, extra in (("campo desconhecido no estrago", [dict(QUEBRA, outro="x")], {}),
                                   ("campo desconhecido na lista", [QUEBRA], {"outra": 1}),
                                   ("campo que falta no estrago", [{k: v for k, v in QUEBRA.items() if k != "para"}],
                                    {})):
    cod, out, trabalho = roda(nome(), estragos, **extra)
    confere(nada_rodou(cod, out, trabalho), f"{descricao} é erro, sem rodar nada: {out}")
CHEIA, DENTRO = nome(), f"{nome()}.txt"  # uma pasta de trabalho que ja tem um arquivo
(TRABALHO / f"t-{CHEIA}").mkdir()
(TRABALHO / f"t-{CHEIA}" / DENTRO).write_text(TEXTO, encoding="utf-8")
cod, out, trabalho = roda(CHEIA, [QUEBRA])
confere(cod == 2 and out.startswith("ERRO") and [p.name for p in trabalho.iterdir()] == [DENTRO],
        f"a pasta de trabalho que não está vazia é erro, sem rodar nada: {out}")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
