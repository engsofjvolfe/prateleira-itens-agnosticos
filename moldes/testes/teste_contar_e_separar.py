"""
Testes dos dois scripts da peca dos moldes: a contagem (contar.py) e as listas
(separar.py), com as entradas comuns dos dois (entrada.py). As partes que eles importam tem
o teste delas, o teste_moldes.py.

O mundo e sorteado pelo mundo_inventado.py, desta pasta, com uma semente fixa (o sorteio e
o mesmo em toda rodada; outra semente vem com --semente), e tambem a forma, as regras e as
analises erradas.

Os testes conferem regras que valem para qualquer forma, nunca uma lista pronta:
  - a contagem de cada documento e de cada classe bate com o que foi sorteado, com um
    problema por trecho com problema; o do grupo desconhecido diz o grupo;
  - a lista do separar.py traz exatamente os trechos do documento, ou os que esperam o
    assunto; a lista de um documento que nao e de conteudo e ERRO, que sai com codigo 2, e
    nao grava;
  - sem erro, a saida e gravada, numa pasta que o script cria quando ela ainda nao existe,
    e a contagem traz a tabela das classes;
  - forma, regras e analises erradas dao ERRO, que diz o que esta errado (no que o molde
    pega, o caminho do valor) e sai com codigo 2, e nada e gravado; a analise que nao se le
    em UTF-8 tambem, e o ERRO diz o arquivo dela;
  - duas rodadas dao a mesma saida, e a ordem em que os arquivos foram criados nao muda
    nada; com problema nas analises, a contagem sai com codigo 1, e sem problema, com 0.
Uso:
    python3 -I teste_contar_e_separar.py <pasta da peca> <pasta de trabalho nova> [--semente N]
Precisa do extrator_comum.py, do extrator, na pasta irma "extrator" da peca ou na propria
pasta da peca, como os scripts.
"""
import argparse
import collections
import shutil
import subprocess
import sys
from pathlib import Path


def argumentos():
    p = argparse.ArgumentParser(description="Testes da contagem e das listas da peça dos moldes.")
    p.add_argument("peca", type=Path, help="a pasta da peça")
    p.add_argument("trabalho", type=Path, help="uma pasta de trabalho nova")
    p.add_argument("--semente", type=int, default=1, help="a semente do sorteio")
    return p.parse_args()


ARGS = argumentos()
PECA, TRABALHO = ARGS.peca.resolve(), ARGS.trabalho.resolve()
sys.path.insert(0, str(PECA))
sys.path.insert(1, str(Path(__file__).resolve().parent))
import analises  # noqa: E402
import contar  # noqa: E402
import lugares  # noqa: E402
import relatorio  # noqa: E402
from mundo_inventado import (COM_PROBLEMA, SORTEIO, classe_esperada, classes_esperadas, diz,  # noqa: E402
                             documentos_esperados, frases_dos_problemas, grava_aulas, grava_json, id_esperado,
                             marcas_esperadas, sorteia_mundo, valor_esperado, variantes)  # -- nesta pasta

SORTEIO.seed(ARGS.semente)
FALHAS = []


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
        print(f"FALHA: {descricao}")
    return condicao


def roda(script, *args):
    return subprocess.run([sys.executable, "-I", "-B", str(PECA / script), *map(str, args)],
                          capture_output=True, text=True)


def gravado(caminho):
    """O texto que um script gravou; FALHA, e texto vazio, quando ele nao gravou."""
    if confere(caminho.is_file(), f"a saída é gravada: {caminho.relative_to(TRABALHO)}"):
        return caminho.read_text(encoding="utf-8")
    return ""


def teste_contagem(mundo, trechos, frases):
    docs, classes, problemas = contar.contar(trechos, mundo["regras"])
    esperado = {d["id"]: {"trechos": 0, "tipos": collections.Counter(), "grupos": collections.Counter(),
                          "marcas": collections.Counter(), "aulas": collections.Counter()}
                for d in mundo["regras"]["documentos"]}
    com_problema = collections.Counter()
    for caso, chave, slide, posicao in mundo["esperados"]:
        for d in documentos_esperados(caso, mundo):
            esperado[d]["trechos"] += 1
            esperado[d]["tipos"].update(valor_esperado(caso, mundo, "tipo"))
            esperado[d]["grupos"].update(valor_esperado(caso, mundo, "grupo"))
            esperado[d]["marcas"].update(marcas_esperadas(caso, mundo))
            esperado[d]["aulas"][chave] += 1
        if caso["tipo"] in COM_PROBLEMA:
            com_problema[id_esperado(caso, chave, slide, posicao)] += 1
    for d in esperado:
        for chave in esperado[d]:
            confere(docs[d][chave] == esperado[d][chave], f"contagem: {chave} do documento {d}")
    confere(classes == classes_esperadas(mundo, frases), "contagem: cada classe")
    confere(collections.Counter(i for i, _ in problemas) == com_problema,
            "contagem: um problema por trecho com problema")
    desconhecidos = {id_esperado(c, *r) for c, *r in mundo["esperados"] if c["tipo"] == "desconhecido"}
    confere(all(mundo["desconhecido"] in m for i, m in problemas if i in desconhecidos),
            "o problema do grupo desconhecido diz o grupo")


def teste_scripts(mundo, frases):
    m, pasta = mundo, TRABALHO / "scripts"
    saidas = []
    for n, analises_ in enumerate([m["pasta"], m["pasta"], pasta / "ao-contrario"]):
        if n == 2:
            grava_aulas(analises_, m, ordem=-1)
        saida = pasta / f"rodada-{n}" / "contagem.md"  # numa pasta que ainda nao existe: o script a cria
        r = roda("contar.py", analises_, m["arquivo_forma"], m["arquivo_regras"], saida)
        confere(r.returncode == 1, f"a contagem sai com código 1 quando há problema: {r.stdout}{r.stderr}")
        saidas.append(gravado(saida))
    confere(saidas[0] == saidas[1], "a contagem é a mesma nas duas rodadas")
    confere(saidas[0] == saidas[2], "a contagem não muda com a ordem em que os arquivos foram criados")
    das_classes = "\n".join(relatorio.tabela_das_classes(classes_esperadas(m, frases), m["regras"]))
    confere(das_classes in saidas[0], "a contagem traz a tabela das classes")

    ids = {id_esperado(c, *r): (c, r) for c, *r in m["esperados"]}
    conteudo = [d["id"] for d in m["regras"]["documentos"] if not d.get("todos")]
    for qual in [["--documento", d] for d in conteudo] + [["--assunto"]]:
        textos = []
        for n in (1, 2):
            saida = pasta / f"lista-{'-'.join(qual)}-{n}.md"
            r = roda("separar.py", m["pasta"], m["arquivo_forma"], m["arquivo_regras"], saida, *qual)
            confere(r.returncode == 0, f"a lista {qual} sai sem erro: {r.stdout}{r.stderr}")
            textos.append(gravado(saida))
        confere(textos[0] == textos[1], f"a lista {qual} é a mesma nas duas rodadas")
        for i, (caso, _) in ids.items():
            classe = classe_esperada(caso, m)
            dentro = classe == ("assunto",) if qual == ["--assunto"] else (
                classe == ("estudo",) and qual[1] in documentos_esperados(caso, m))
            if not confere(textos[0].count(f"`{i}`") == int(dentro), f"a lista {qual} traz {i} só se ele é dela"):
                break
    todos = [d["id"] for d in m["regras"]["documentos"] if d.get("todos")]
    for documento in [SORTEIO.choice(todos), "nao-" + conteudo[0]]:
        saida = pasta / f"lista-errada-{documento}.md"
        r = roda("separar.py", m["pasta"], m["arquivo_forma"], m["arquivo_regras"], saida, "--documento", documento)
        confere(r.returncode == 2 and not saida.exists() and documento in r.stdout,
                f"a lista de um documento que não é de conteúdo é ERRO, que sai com 2, e não grava: {documento}")

    limpo = sorteia_mundo(TRABALHO / "limpo", com_problemas=False)
    r = roda("contar.py", limpo["pasta"], limpo["arquivo_forma"], limpo["arquivo_regras"], pasta / "limpo.md")
    confere(r.returncode == 0, f"sem problema, a contagem sai com código 0: {r.stdout}{r.stderr}")


def teste_erros(mundo):
    for nome, _, forma, regras, pasta, culpado in variantes(mundo, TRABALHO / "erros"):
        caso = TRABALHO / "erros" / nome
        f, r = grava_json(caso / "forma.json", forma), grava_json(caso / "regras.json", regras)
        for script, extra in [("contar.py", []), ("separar.py", ["--assunto"])]:
            saida = caso / f"saida-{script}.md"
            res = roda(script, pasta, f, r, saida, *extra)
            confere(res.returncode == 2 and not saida.exists() and res.stdout.startswith("ERRO")
                    and diz(res.stdout, culpado),
                    f"erro {nome} no {script}: ERRO que diz {culpado!r}, sai com 2, nada gravado: "
                    f"{res.stdout}{res.stderr}")


def teste_analise_fora_do_utf8(mundo):
    """A analise que nao se le em UTF-8 da ERRO, que diz o arquivo dela, e nada e gravado."""
    pasta = TRABALHO / "erros" / "fora-do-utf8"
    shutil.copytree(mundo["pasta"], pasta)
    arquivo = SORTEIO.choice(sorted(p for p in pasta.glob(mundo["forma"]["arquivos"]) if p.is_file()))
    arquivo.write_bytes(arquivo.read_bytes() + b"\xff")  # um byte que o UTF-8 nunca tem
    for script, extra in [("contar.py", []), ("separar.py", ["--assunto"])]:
        saida = pasta.parent / f"saida-fora-do-utf8-{script}.md"
        res = roda(script, pasta, mundo["arquivo_forma"], mundo["arquivo_regras"], saida, *extra)
        confere(res.returncode == 2 and not saida.exists() and res.stdout.startswith("ERRO")
                and arquivo.name in res.stdout,
                f"análise fora do UTF-8 no {script}: ERRO que diz o arquivo, nada gravado: {res.stdout}{res.stderr}")


def main():
    if TRABALHO.exists() and any(TRABALHO.iterdir()):
        sys.exit("a pasta de trabalho precisa ser nova ou vazia")
    TRABALHO.mkdir(parents=True, exist_ok=True)
    mundo = sorteia_mundo(TRABALHO / "mundo")
    trechos = analises.ler_analises(mundo["pasta"], mundo["forma"])[0]
    frases = frases_dos_problemas(mundo, trechos, lugares.lugar)
    teste_contagem(mundo, trechos, frases)
    teste_scripts(mundo, frases)
    teste_erros(mundo)
    teste_analise_fora_do_utf8(mundo)
    print(f"{len(FALHAS)} falha(s) (semente {ARGS.semente})")
    sys.exit(1 if FALHAS else 0)


if __name__ == "__main__":
    main()
