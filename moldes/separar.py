"""
Lista, para a leitura inteira, os trechos de estudo que caem num documento de conteudo,
so pelas regras, ou os que esperam o assunto para ter documento: cada um com o id, os
tipos, os grupos, os caminhos, as marcas, o destino e o texto, aula por aula.

As entradas, o aviso de erro e a gravacao sao os do entrada.py, desta pasta. O documento
pedido tem de ser de conteudo; senao, e erro, como qualquer entrada errada, que sai com
codigo 2 e nao grava nada.

Uso:
    python3 -I separar.py <pasta das analises> <forma.json> <regras.json> <saida.md> --documento <id>
    python3 -I separar.py <pasta das analises> <forma.json> <regras.json> <saida.md> --assunto
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # com -I, a pasta do script nao entra sozinha
import entrada  # noqa: E402
import lugares  # noqa: E402

NENHUM = "—"  # o que a lista mostra no lugar de um valor vazio


def selecionar(trechos, regras, documento=None):
    """Os trechos que caem no documento de conteudo dado (todos de estudo, porque o trecho que
    cai num documento de conteudo e de estudo); sem documento, os que esperam o assunto. Na
    ordem dos trechos."""
    escolhidos = []
    for t in trechos:
        classe, caidos = lugares.lugar(t, regras)
        if (classe == ("assunto",)) if documento is None else (documento in caidos):
            escolhidos.append(t)
    return escolhidos


def listar(trechos, regras, titulo):
    saida, aula = [f"# {titulo}", "", f"{len(trechos)} trechos.", ""], None
    for t in trechos:
        if t["aula"] != aula:
            aula = t["aula"]
            saida += [f"## aula {aula}", ""]
        tipos, grupos, caminhos = (", ".join(lugares.valor(t, p)) or NENHUM for p in ("tipo", "grupo", "caminho"))
        marcas = ", ".join(lugares.marcas(t, regras)) or NENHUM
        saida.append(f"- `{t['id']}` {tipos} | g {grupos} | {caminhos} | m {marcas} | → {lugares.texto(t, 'destino')}")
        saida.append(f"  {t['texto']}")
    return "\n".join(saida) + "\n"


def trabalho(a, regras, trechos, notas):
    """(texto, resumo, codigo de saida) da lista do documento pedido, ou dos trechos que
    esperam o assunto; documento que nao e de conteudo e erro (ValueError)."""
    if a.documento is not None and a.documento not in lugares.documentos_de_conteudo(regras):
        raise ValueError(f"documento de conteúdo desconhecido {a.documento!r}")
    escolhidos = selecionar(trechos, regras, a.documento)
    nomes = {d["id"]: d["nome"] for d in regras["documentos"]}
    titulo = nomes[a.documento] if a.documento is not None else "Trechos que esperam o assunto"
    return listar(escolhidos, regras, titulo), f"{len(escolhidos)} trechos", 0


def main(argv=None):
    p = entrada.argumentos("Lista os trechos de um documento, ou os que esperam o assunto.", "a lista, em markdown")
    qual = p.add_mutually_exclusive_group(required=True)
    qual.add_argument("--documento", help="o id de um documento de conteúdo")
    qual.add_argument("--assunto", action="store_true", help="os trechos que esperam o assunto")
    return entrada.rodar(p, trabalho, argv)


if __name__ == "__main__":
    sys.exit(main())
