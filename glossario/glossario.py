"""
Grava o glossario de um projeto, ou confere que o gravado esta em dia: cada termo que o
projeto define, em ordem alfabetica, com a definicao e a fonte que a da, ou com o link para
o lugar do documento em que ele e definido.

Duas entradas dao os termos. A lista das definicoes, um JSON com o molde
esquemas/glossario.schema.json: o "versao_schema" e os "termos", cada um com o "termo", numa
linha so, com alguma letra, a "definicao" e a "fonte", textos com alguma letra que podem ter
mais de uma linha, como uma citacao em bloco. E os documentos dados, que definem um termo
marcando-o com <dfn>termo</dfn>, a marca do HTML para "aqui este termo e definido", fora dos
blocos de codigo e do codigo na linha; o termo da marca e o texto dela, sem as tags de
dentro, com os espacos juntos e na forma NFC.

O glossario e o cabecalho dado (o titulo e a abertura, por exemplo), sem os espacos e as
quebras do fim, e, para cada termo, em ordem alfabetica sem contar acentos nem maiusculas,
o titulo de segundo nivel com o termo, cuja ancora e o endereco dele, e: o termo da lista,
um paragrafo com a definicao e outro com a fonte, sem os espacos e as quebras das pontas; o
termo de uma marca, um paragrafo com o link para o lugar dela, a secao (o titulo mais perto
acima da marca, de nivel 2 em diante) ou o documento, quando o titulo mais perto e o de nivel
1 ou nao ha titulo, com o titulo do documento (o de nivel 1, ou o caminho dele a partir da
pasta do glossario) e o da secao no texto do link. O termo que esta na lista e numa marca
sai so com a definicao da lista. Os blocos se separam por uma linha em branco, e o glossario
termina com uma quebra de linha. A citacao da fonte nao se confere aqui: o glossario gravado
vai para a peca que confere citacoes, como o confere-citacoes.

Sao problema, e nada e gravado: o termo repetido na lista, sem contar maiusculas, a forma
Unicode e os espacos; a marca vazia; o termo marcado em mais de um lugar; e dois titulos do
glossario com a mesma ancora, como dois termos que so diferem na pontuacao, ou um termo e um
titulo do cabecalho. Com --conferir, nada e gravado: o glossario gravado tem de ser o que o
script gravaria agora.

Mostra uma linha ERRO por problema e um resumo. Sai com 0 com o glossario gravado ou em dia;
1 com problema, ou com o glossario que nao esta em dia; e 2, sem nada gravado, quando a
lista, o cabecalho ou um documento nao se leem em UTF-8, a lista nao e JSON ou sai do molde,
o cabecalho esta vazio, ou o glossario e a lista, o cabecalho ou uma pasta. O glossario dado
entre os documentos fica de fora deles. Precisa do extrator_comum.py e do texto_comum.py, do
extrator, do markdown_comum.py, do documentos, e do grava_ou_confere.py e do
documento_gerado.py, do grava-ou-confere, nas pastas irmas ou na mesma pasta.

Uso:
    python3 -I glossario.py <definicoes.json> <cabecalho.md> <glossario.md> [<documento.md>...] [--conferir]
"""

import argparse
import os
import re
import sys
import unicodedata
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "grava-ou-confere", PASTA.parent / "documentos", PASTA.parent / "extrator", PASTA):
    sys.path.insert(0, str(pasta))  # na prateleira, as pastas irmas
from documento_gerado import confere_destino, em_blocos, le_cabecalho  # noqa: E402
from extrator_comum import ErroDeDados, le_conferido, le_texto, repetidos  # noqa: E402
from grava_ou_confere import grava_ou_confere, opcao_conferir  # noqa: E402
from markdown_comum import QUEBRA, TAG_HTML, ancora, texto_fora_de_codigo, titulos  # noqa: E402
from texto_comum import espacos_juntos, nfc  # noqa: E402

MOLDE = PASTA / "esquemas" / "glossario.schema.json"  # o molde da lista das definicoes
DFN = re.compile(r"<dfn(?:\s[^>]*)?>(.*?)</dfn>", re.IGNORECASE | re.DOTALL)  # a marca de um termo definido
TITULO = "## "  # o comeco do titulo de cada termo no glossario
ENTRE_LUGARES = " › "  # entre o titulo do documento e o da secao, no texto do link
ALVO_ENTRE_SINAIS = re.compile(r"[\s()]")  # o alvo de link com um destes vai entre < e >


def comparavel(termo):
    """O termo para comparar com outro: na forma Unicode NFC, com os espacos juntos, sem maiusculas."""
    return espacos_juntos(nfc(termo)).casefold()


def alfabetica(termo):
    """A chave da ordem alfabetica: o termo sem os acentos e sem maiusculas; o termo, no fim, desempata."""
    sem_acentos = "".join(c for c in unicodedata.normalize("NFKD", termo) if not unicodedata.combining(c))
    return sem_acentos.casefold(), termo


def visivel(texto):
    """O texto como aparece: sem as tags HTML, com os espacos juntos, em NFC."""
    return nfc(espacos_juntos(TAG_HTML.sub("", texto)))


def marcas(texto):
    """[(linha, termo)] de cada marca de termo do texto, fora dos blocos de codigo e do codigo na linha, na ordem: o
    termo como aparece, sem as tags de dentro, com os espacos juntos, em NFC."""
    fora = texto_fora_de_codigo(texto)
    return [(fora.count(QUEBRA, 0, m.start()) + 1, visivel(m.group(1))) for m in DFN.finditer(fora)]


def link(documento, texto, linha, glossario):
    """O link para o lugar de uma marca: a secao (o titulo mais perto acima da linha, de nivel 2 em diante) ou o
    documento, com o titulo do documento (o de nivel 1, ou o caminho) e o da secao, como aparecem, no texto; o
    caminho e o do documento a partir da pasta do glossario."""
    lista = titulos(texto)
    caminho = Path(os.path.relpath(Path(documento).resolve(), Path(glossario).resolve().parent)).as_posix()
    nome = next((visivel(t.texto) for t in lista if t.nivel == 1), caminho)
    acima = [t for t in lista if t.linha <= linha]
    perto = acima[-1] if acima else None
    if perto is not None and perto.nivel > 1:
        nome, caminho = f"{nome}{ENTRE_LUGARES}{visivel(perto.texto)}", f"{caminho}#{perto.ancora}"
    return f"[{nome}](<{caminho}>)" if ALVO_ENTRE_SINAIS.search(caminho) else f"[{nome}]({caminho})"


def glossario(lista, termos, cabecalho, documentos, destino):
    """(texto do glossario, quantos termos, erros): os termos da lista e os das marcas que a lista nao tem, em ordem
    alfabetica; cada erro, uma linha ERRO pronta."""
    erros, da_lista = [], {}
    for k, t in enumerate(termos):
        chave = comparavel(t["termo"])
        if chave in da_lista:
            erros.append(f"ERRO {lista}: /termos/{k}/termo: é o mesmo termo de /termos/{da_lista[chave][0]}/termo")
        else:
            da_lista[chave] = (k, t)
    marcados = {}
    for documento, texto in documentos:
        for linha, termo in marcas(texto):
            if not termo:
                erros.append(f"ERRO {documento}:{linha}: marca de termo vazia")
            else:
                marcados.setdefault(comparavel(termo), []).append((documento, texto, linha, termo))
    for lugares in marcados.values():
        if len(lugares) > 1:
            todos = ", ".join(f"{d}:{n}" for d, _, n, _ in lugares)
            erros += [f"ERRO {d}:{n}: o termo {termo!r} está marcado em mais de um lugar: {todos}"
                      for d, _, n, termo in lugares]
    entradas = [(nfc(t["termo"]), [t["definicao"].strip(), t["fonte"].strip()]) for _, t in da_lista.values()]
    entradas += [(lugares[0][3], [link(*lugares[0][:3], destino)]) for chave, lugares in marcados.items()
                 if chave not in da_lista]
    entradas.sort(key=lambda e: alfabetica(e[0]))
    texto = em_blocos(cabecalho, [bloco for termo, corpo in entradas for bloco in [TITULO + termo, *corpo]])
    erros += [f"ERRO {destino}: mais de um título do glossário tem a âncora #{a}"
              for a in repetidos([ancora(t.texto) for t in titulos(texto)])]
    return texto, len(entradas), erros


def main(argv=None):
    p = argparse.ArgumentParser(description="Grava o glossário: os termos da lista das definições e os que os "
                                            "documentos marcam.")
    p.add_argument("lista", type=Path, help="a lista das definições, em JSON")
    p.add_argument("cabecalho", type=Path, help="o começo do glossário, como o título e a abertura")
    p.add_argument("glossario", type=Path, help="o glossário, que o script grava")
    p.add_argument("documentos", type=Path, nargs="*", help="os documentos com as marcas <dfn>")
    opcao_conferir(p, "não grava: confere que o glossário gravado é o que as entradas dão")
    a = p.parse_args(argv)
    try:
        confere_destino(a.glossario, (a.lista, a.cabecalho))
        cabecalho = le_cabecalho(a.cabecalho)
        termos = le_conferido(a.lista, MOLDE)["termos"]
        documentos = [(d, le_texto(d)) for d in a.documentos if d.resolve() != a.glossario.resolve()]
    except ErroDeDados as e:
        print(f"ERRO: {e}")
        return 2
    texto, n, erros = glossario(a.lista, termos, cabecalho, documentos, a.glossario)
    for erro in erros:
        print(erro)
    if erros:
        print(f"{n} termo(s), {len(erros)} erro(s): nada foi gravado.")
        return 1
    return grava_ou_confere(a.glossario, texto, a.conferir,
                            falta=f"ERRO {a.glossario}: não é o glossário que as entradas dão agora.",
                            em_dia=f"{n} termo(s): o glossário está em dia.",
                            gravado=f"{n} termo(s) gravado(s) em {a.glossario}.")


if __name__ == "__main__":
    sys.exit(main())
