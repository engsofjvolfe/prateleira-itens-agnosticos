"""
Confere os codigos dos titulos de um dicionario das duvidas: o documento Markdown das
duvidas que as fontes deixam, cada uma sob um titulo com os codigos do que ela toca, para
que a busca por um codigo ache as duvidas dele.

Cada duvida comeca numa linha fora dos blocos de codigo que comeca pelo "titulo" da
configuracao (como "## "). O resto da linha tem de ser so de codigos, cada um entre as
marcas "abre" e "fecha" do "codigo", sem elas dentro, e separados pela marca "entre". Cada
codigo e uma sequencia de partes separadas pelo "separador" das "partes", com um numero de
partes que esta em "tamanhos"; cada parte casa inteira com a forma da posicao dela, em
"formas". Num titulo, nenhum codigo e o comeco de outro, parte por parte, nem se repete, e
os codigos vem em ordem natural, parte por parte: os trechos de algarismos se comparam pelo
valor (9 vem antes de 10), os outros pelo texto, e o codigo que e o comeco de outro viria
antes dele.

Mostra uma linha "ERRO arquivo:linha: motivo" por problema, na ordem dos dicionarios e das
linhas, e um resumo. Sai com 0 sem problema, 1 com problema e 2, sem nada conferido, quando
a configuracao sai do molde (esquemas/dicionario-das-duvidas.schema.json), uma forma nao
compila, um tamanho passa do numero de formas ou um dicionario nao se le em UTF-8. Precisa
do extrator_comum.py, do extrator, e do markdown_comum.py, do documentos, nas pastas irmas
ou na mesma pasta.

Uso:
    python3 -I confere_dicionario.py <configuracao.json> <dicionario.md>...
"""

import argparse
import re
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "documentos", PASTA.parent / "extrator", PASTA):  # na prateleira, as pastas irmas
    sys.path.insert(0, str(pasta))
from extrator_comum import ErroDeDados, compila, le_conferido, le_texto  # noqa: E402
from markdown_comum import linhas_fora_de_codigo  # noqa: E402

MOLDE = PASTA / "esquemas" / "dicionario-das-duvidas.schema.json"
ALGARISMOS = re.compile(r"(\d+)")  # os trechos de uma parte que se comparam pelo valor


def le_configuracao(caminho):
    """A configuracao, conferida contra o molde, com as formas compiladas; o tamanho que passa do numero de formas,
    que o molde nao ve, conferido aqui."""
    dados = le_conferido(caminho, MOLDE)
    partes = dados["partes"]
    formas = [compila(f, f"o campo partes/formas/{k}") for k, f in enumerate(partes["formas"])]
    grandes = sorted(t for t in partes["tamanhos"] if t > len(formas))
    if grandes:
        raise ErroDeDados(f"o campo partes/tamanhos: {grandes} passa(m) do número de formas, {len(formas)}")
    return dict(titulo=dados["titulo"], **dados["codigo"], separador=partes["separador"], formas=formas,
                tamanhos=sorted(partes["tamanhos"]))


def codigos_do_titulo(resto, conf):
    """Os codigos do resto do titulo, sem as marcas; None quando ele nao e so de codigos, cada um entre as marcas e
    sem elas dentro, separados pela marca de entre."""
    abre, fecha, saida = conf["abre"], conf["fecha"], []
    for pedaco in resto.split(conf["entre"]):
        dentro = pedaco[len(abre):len(pedaco) - len(fecha)]
        if not (pedaco.startswith(abre) and pedaco.endswith(fecha) and len(pedaco) > len(abre) + len(fecha)
                and abre not in dentro and fecha not in dentro):
            return None
        saida.append(dentro)
    return saida


def fora_da_forma(codigo, partes, conf):
    """O motivo por que o codigo, ja partido, nao segue a forma; None quando segue."""
    if len(partes) not in conf["tamanhos"]:
        return f"o código {codigo!r} tem {len(partes)} parte(s), e um código tem {conf['tamanhos']}"
    for k, (parte, forma) in enumerate(zip(partes, conf["formas"])):
        if not forma.fullmatch(parte):
            return f"o código {codigo!r}: a parte {k + 1}, {parte!r}, não segue a forma {forma.pattern}"
    return None


def natural(parte):
    """A chave da ordem natural de uma parte: os trechos de algarismos pelo valor, os outros pelo texto; a parte, no
    fim, desempata."""
    return tuple(int(p) if k % 2 else p for k, p in enumerate(ALGARISMOS.split(parte))), parte


def cobre(partes, outras):
    """Se o codigo e o comeco do outro, parte por parte; o mesmo codigo cobre a si mesmo."""
    return len(partes) <= len(outras) and outras[:len(partes)] == partes


def erros_do_titulo(resto, conf):
    """Os motivos por que o titulo, sem o comeco dele, sai da regra; nenhum quando ele a segue."""
    codigos = codigos_do_titulo(resto, conf)
    if codigos is None:
        return [f"o título não é só de códigos, cada um entre {conf['abre']} e {conf['fecha']}, separados por "
                f"{conf['entre']!r}"]
    partidos = [c.split(conf["separador"]) for c in codigos]
    erros = [m for m in (fora_da_forma(c, p, conf) for c, p in zip(codigos, partidos)) if m]
    if erros:
        return erros
    for i in range(len(partidos)):
        for j in range(i + 1, len(partidos)):
            if cobre(partidos[i], partidos[j]) or cobre(partidos[j], partidos[i]):
                erros.append(f"o código {codigos[i]!r} e o {codigos[j]!r}: um é o começo do outro, ou os dois são o "
                             f"mesmo")
    ordem = [tuple(natural(p) for p in partes) for partes in partidos]
    if ordem != sorted(ordem):
        erros.append("os códigos não estão em ordem natural, parte por parte")
    return erros


def confere_texto(texto, conf):
    """([(linha, motivo)], quantos titulos) de um dicionario: cada titulo de duvida fora dos blocos de codigo."""
    titulos = [(n, linha[len(conf["titulo"]):]) for n, linha in linhas_fora_de_codigo(texto)
               if linha.startswith(conf["titulo"])]
    return [(n, motivo) for n, resto in titulos for motivo in erros_do_titulo(resto, conf)], len(titulos)


def main(argv=None):
    p = argparse.ArgumentParser(description="Confere os códigos dos títulos de dicionários das dúvidas.")
    p.add_argument("configuracao", type=Path)
    p.add_argument("dicionarios", type=Path, nargs="+")
    a = p.parse_args(argv)
    try:
        conf = le_configuracao(a.configuracao)
        textos = [(d, le_texto(d)) for d in a.dicionarios]
    except ErroDeDados as e:
        print(f"ERRO: {e}")
        return 2
    erros = titulos = 0
    for dicionario, texto in textos:
        lista, n = confere_texto(texto, conf)
        for linha, motivo in lista:
            print(f"ERRO {dicionario}:{linha}: {motivo}")
        erros, titulos = erros + len(lista), titulos + n
    print(f"{len(textos)} dicionário(s), {titulos} título(s), {erros} erro(s)")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
