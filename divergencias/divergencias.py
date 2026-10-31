"""
Confere a lista dos fatos que as fontes dizem de formas diferentes e grava o documento
deles: para cada fato, a forma que o material ensina e as outras, cada uma com o que diz e
a fonte que a da.

A lista e um JSON com o molde esquemas/divergencias.schema.json: o "versao_schema" e as
"divergencias", cada uma com o "fato", a forma "ensinada" e as "outras", uma ou mais; cada
forma com o que ela "diz" e a "fonte". O fato e o que a forma diz sao uma linha so, com
alguma letra; a fonte pode ter mais de uma linha, como uma citacao em bloco. Campo que o
molde nao conhece, ou que falta, e erro.

O documento e o cabecalho dado (o titulo e a abertura, por exemplo), sem os espacos e as
quebras do fim, e, para cada divergencia, na ordem da lista: o titulo de segundo nivel com o
fato e, para cada forma, a ensinada primeiro e as outras na ordem delas, um paragrafo com o
rotulo dela (o de --ensinada ou o de --outra, como vem no comando) e o que ela diz, e um
paragrafo com a fonte, sem os espacos e as quebras das pontas. Os blocos se separam por uma
linha em branco, e o documento termina com uma quebra de linha. A citacao da fonte nao se
confere aqui: o documento gravado vai para a peca que confere citacoes, como o
confere-citacoes.

Sao problema, e nada e gravado: o fato repetido, sem contar maiusculas, a forma Unicode e os
espacos; e a forma que diz o mesmo que outra do mesmo fato, sem contar a forma Unicode e os
espacos. Com --conferir, nada e gravado: o documento gravado tem de ser o que o script
gravaria agora.

Mostra uma linha ERRO por problema, com a lista e o caminho do valor nela, e um resumo. Sai
com codigo 0 com o documento gravado ou em dia; 1 com problema na lista, ou com o documento
que nao esta em dia; e 2, sem nada gravado, quando a lista ou o cabecalho nao se leem em
UTF-8, a lista nao e JSON ou sai do molde, o cabecalho esta vazio, um rotulo nao e uma linha
so com alguma letra (a regra "linha" do molde), ou o documento e um dos arquivos de entrada
ou nao e um arquivo. Precisa do extrator_comum.py e do texto_comum.py, do extrator, e do
grava_ou_confere.py, do grava-ou-confere, nas pastas irmas ou na mesma pasta.

Uso:
    python3 -I divergencias.py <divergencias.json> <cabecalho.md> <documento.md>
        --ensinada <rotulo> --outra <rotulo> [--conferir]
"""

import argparse
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "grava-ou-confere", PASTA.parent / "extrator", PASTA):  # na prateleira, as pastas irmas
    sys.path.insert(0, str(pasta))
from extrator_comum import ErroDeDados, expressao, le_conferido, le_json, le_texto  # noqa: E402
from grava_ou_confere import grava_ou_confere, opcao_conferir  # noqa: E402
from texto_comum import espacos_juntos, nfc  # noqa: E402

MOLDE = PASTA / "esquemas" / "divergencias.schema.json"  # o molde da lista
LINHA = "$defs/linha/pattern"  # no molde, a regra de uma linha so com alguma letra, que tambem vale para os rotulos
TITULO = "## "  # o comeco do titulo de cada fato no documento
QUEBRA = "\n"  # o fim do documento
ENTRE_BLOCOS = "\n\n"  # a linha em branco entre dois blocos do documento


def comparavel(texto):
    """O texto para comparar com outro: na forma Unicode NFC, com os espacos juntos."""
    return espacos_juntos(nfc(texto))


def formas(divergencia):
    """[(caminho, forma)] da divergencia: a ensinada e, depois, as outras, na ordem; o caminho e o da forma dentro
    da divergencia."""
    return [("ensinada", divergencia["ensinada"])] + [(f"outras/{k}", f) for k, f in enumerate(divergencia["outras"])]


def problemas(divergencias):
    """[(caminho, motivo)] de cada problema da lista, na ordem dela: o fato repetido, sem contar maiusculas, a forma
    Unicode e os espacos; e a forma que diz o mesmo que outra do mesmo fato, sem contar a forma Unicode e os espacos.
    O caminho e o do valor na lista."""
    erros, fatos = [], {}
    for k, d in enumerate(divergencias):
        onde = f"/divergencias/{k}"
        chave = comparavel(d["fato"]).casefold()
        if chave in fatos:
            erros.append((f"{onde}/fato", f"é o mesmo fato de {fatos[chave]}/fato"))
        fatos.setdefault(chave, onde)
        ditas = {}
        for caminho, forma in formas(d):
            dita = comparavel(forma["diz"])
            if dita in ditas:
                erros.append((f"{onde}/{caminho}/diz", f"diz o mesmo que {onde}/{ditas[dita]}/diz"))
            ditas.setdefault(dita, caminho)
    return erros


def documento(cabecalho, divergencias, ensinada, outra):
    """O texto do documento: o cabecalho e, para cada divergencia, o titulo com o fato e, para cada forma, o rotulo
    com o que ela diz e a fonte."""
    blocos = [cabecalho.rstrip()]
    for d in divergencias:
        blocos.append(TITULO + d["fato"])
        for caminho, forma in formas(d):
            rotulo = ensinada if caminho == "ensinada" else outra
            blocos += [f"{rotulo} {forma['diz']}", forma["fonte"].strip()]
    return ENTRE_BLOCOS.join(blocos) + QUEBRA


def entrada(a):
    """(divergencias, cabecalho): a lista, conferida pelo molde, e o cabecalho; ErroDeDados quando um rotulo, o
    documento, o cabecalho ou a lista nao servem."""
    linha = expressao(le_json(MOLDE), LINHA)
    for opcao, rotulo in (("--ensinada", a.ensinada), ("--outra", a.outra)):
        if not linha.search(rotulo):
            raise ErroDeDados(f"{opcao}: o rótulo precisa ser uma linha só, com alguma letra: {rotulo!r}")
    if a.documento.resolve() in (a.lista.resolve(), a.cabecalho.resolve()):
        raise ErroDeDados(f"o documento é um dos arquivos de entrada: {a.documento}")
    if a.documento.exists() and not a.documento.is_file():
        raise ErroDeDados(f"o documento não é um arquivo: {a.documento}")
    cabecalho = le_texto(a.cabecalho)
    if not cabecalho.strip():
        raise ErroDeDados(f"{a.cabecalho}: o cabeçalho está vazio")
    return le_conferido(a.lista, MOLDE)["divergencias"], cabecalho


def main(argv=None):
    p = argparse.ArgumentParser(description="Confere a lista das divergências e grava o documento delas.")
    p.add_argument("lista", type=Path, help="a lista das divergências, em JSON")
    p.add_argument("cabecalho", type=Path, help="o começo do documento, como o título e a abertura")
    p.add_argument("documento", type=Path, help="o documento das divergências, que o script grava")
    p.add_argument("--ensinada", required=True, help="o rótulo da forma que o material ensina, no documento")
    p.add_argument("--outra", required=True, help="o rótulo de cada uma das outras formas, no documento")
    opcao_conferir(p, "não grava: confere que o documento gravado é o que a lista dá")
    a = p.parse_args(argv)
    try:
        divergencias, cabecalho = entrada(a)
    except ErroDeDados as e:
        print(f"ERRO: {e}")
        return 2
    erros = problemas(divergencias)
    for onde, motivo in erros:
        print(f"ERRO {a.lista}: {onde}: {motivo}")
    if erros:
        print(f"{len(divergencias)} divergência(s), {len(erros)} erro(s): nada foi gravado.")
        return 1
    n = len(divergencias)
    return grava_ou_confere(a.documento, documento(cabecalho, divergencias, a.ensinada, a.outra), a.conferir,
                            falta=f"ERRO {a.documento}: não é o documento que a lista dá agora.",
                            em_dia=f"{n} divergência(s): o documento está em dia.",
                            gravado=f"{n} divergência(s) gravada(s) em {a.documento}.")


if __name__ == "__main__":
    sys.exit(main())
