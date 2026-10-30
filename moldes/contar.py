"""
Conta os trechos das analises que caem em cada documento, so pelas regras: quantos, e
quantos de cada tipo, grupo, marca e aula. Diz tambem quantos trechos ha em cada classe do
lugares.py, com o total.

Um trecho conta em cada documento em que cai e, dentro dele, em cada tipo, grupo e marca
que tem. O trecho de fora, ou com problema na classe, nao cai em documento nenhum.

As entradas, o aviso de erro e a gravacao sao os do entrada.py, desta pasta.

Uso:
    python3 -I contar.py <pasta das analises> <forma.json> <regras.json> <saida.md>
Sai com codigo 1 quando ha problema (a saida e gravada, com a lista deles) ou erro (nada e
gravado).
"""
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # com -I, a pasta do script nao entra sozinha
import entrada  # noqa: E402
import lugares  # noqa: E402
from relatorio import por_chave, por_quantidade, tabela, tabela_das_classes  # noqa: E402


def contar(trechos, regras):
    """(documentos, classes, problemas): para cada documento, {"trechos": n, "tipos",
    "grupos", "marcas", "aulas": Counter}; o Counter das classes; os problemas, [(id, o que
    houve)], na ordem dos trechos."""
    docs = {d["id"]: {"trechos": 0, "tipos": collections.Counter(), "grupos": collections.Counter(),
                      "marcas": collections.Counter(), "aulas": collections.Counter()} for d in regras["documentos"]}
    classes, problemas = collections.Counter(), []
    for t in trechos:
        classe, caidos = lugares.lugar(t, regras)
        classes[classe] += 1
        if classe[0] == "fora":
            continue
        if classe[0] == "problema":
            problemas.append((t["id"], classe[1]))
        problemas += [(t["id"], f"grupo desconhecido {g!r}") for g in lugares.grupos_desconhecidos(t, regras)]
        for d in caidos:
            docs[d]["trechos"] += 1
            docs[d]["tipos"].update(lugares.valor(t, "tipo"))
            docs[d]["grupos"].update(lugares.valor(t, "grupo"))
            docs[d]["marcas"].update(lugares.marcas(t, regras))
            docs[d]["aulas"][t["aula"]] += 1
    return docs, classes, problemas


def relatorio(trechos, notas, regras, docs, classes, problemas):
    nomes_grupos = {g["id"]: f"{g['id']} {g['nome']}" for g in regras["grupos"]}
    saida = ["# Contagem por documento", "",
             f"{len(trechos)} trechos com campos e {sum(notas.values())} notas sem campos.", ""]
    saida += tabela_das_classes(classes, regras) + [""]
    for d in regras["documentos"]:
        info = docs[d["id"]]
        saida += [f"## {d['nome']}", "", f"{info['trechos']} trechos.", ""]
        saida += tabela(["Tipo", "Trechos"], por_quantidade(info["tipos"]), numericas=(1,)) + [""]
        saida += tabela(["Grupo", "Trechos"], [(nomes_grupos.get(g, g), n) for g, n in por_chave(info["grupos"])],
                        numericas=(1,)) + [""]
        if info["marcas"]:
            linhas = [(m["nome"], info["marcas"][m["id"]]) for m in regras["marcas"] if info["marcas"][m["id"]]]
            saida += tabela(["Marca", "Trechos"], linhas, numericas=(1,)) + [""]
        saida += tabela(["Aula", "Trechos"], por_chave(info["aulas"]), numericas=(1,)) + [""]
    if problemas:
        saida += ["## Problemas", ""] + [f"- {i}: {m}" for i, m in problemas] + [""]
    return "\n".join(saida)


def trabalho(a, regras, trechos, notas):
    """(texto, resumo, codigo de saida) da contagem; o codigo e 1 quando ha problema."""
    docs, classes, problemas = contar(trechos, regras)
    texto = relatorio(trechos, notas, regras, docs, classes, problemas)
    return texto, f"{len(trechos)} trechos; {len(problemas)} problema(s)", 1 if problemas else 0


def main(argv=None):
    p = entrada.argumentos("Conta os trechos das análises que caem em cada documento.",
                           "o relatório, em markdown")
    return entrada.rodar(p, trabalho, argv)


if __name__ == "__main__":
    sys.exit(main())
