"""
Grava o pacote do Anki (.apkg) a partir do CSV do baralho, ja conferido pelo
confere_baralho.py: uma nota por linha, na ordem do CSV, com os campos do tipo de nota da
configuracao, cada um com o texto da coluna dele, o HTML escapado e cada trecho entre duas
marcas de enfase dentro da etiqueta dela (no campo de palavras-chave, cada palavra-chave numa
linha); e com as etiquetas do nome da fonte (o nome do arquivo, sem a extensao) e da coluna. O
baralho, o tipo de nota e a data vem da configuracao; os modelos da frente e do verso do
cartao e o estilo, de arquivos dados no comando, cada um com o texto como esta. O mesmo CSV,
a mesma configuracao e os mesmos modelos dao sempre o mesmo pacote.

Sai com 0 quando grava e com 2, sem gravar nada, quando a configuracao, o CSV, um modelo ou um
argumento nao servem. Usa so a biblioteca padrao e o baralho_comum e o pacote_anki, desta
pasta.

Uso:
    python3 -I gera_apkg.py <configuracao.json> <baralho.csv> <baralho.apkg>
        --frente <frente.html> --verso <verso.html> --estilo <estilo.css>
"""
import argparse
import datetime
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # o baralho_comum e o pacote_anki, nesta pasta
import baralho_comum as comum  # noqa: E402
import pacote_anki  # noqa: E402


def com_enfases(texto, enfases):
    """O texto com o HTML escapado e cada trecho entre duas marcas de enfase dentro da etiqueta
    dela, as marcas mais longas primeiro; a marca que sobra sem par e erro (ValueError)."""
    saida = html.escape(texto, quote=False)
    ordem = sorted(enfases, key=lambda e: len(e["marca"]), reverse=True)
    for e in ordem:
        marca = re.escape(e["marca"])
        saida = re.sub(f"{marca}(.+?){marca}", lambda m: f"<{e['etiqueta']}>{m.group(1)}</{e['etiqueta']}>", saida)
    sobra = [e["marca"] for e in ordem if e["marca"] in saida]
    if sobra:
        raise ValueError(f"marca de ênfase sem par: {sobra}, em {texto!r}")
    return saida


def campo(linha, descricao, conf):
    """O HTML de um campo da nota: o texto da coluna dele; no de palavras-chave, uma por linha."""
    texto = linha[descricao["coluna"]]
    partes = texto.split(conf["tabela"]["separador"]) if descricao.get("palavras_chave") else [texto]
    return conf["nota"]["quebra"].join(com_enfases(parte, conf["enfases"]) for parte in partes)


def data_da(conf):
    """A data da configuracao, com o fuso; a que nao se le como data e erro (ValueError)."""
    try:
        return datetime.datetime.fromisoformat(conf["data"])
    except ValueError as e:
        raise ValueError(f"a data da configuração não se lê: {conf['data']} ({e})") from None


def gera(a):
    conf = comum.le_configuracao(a.configuracao)
    data = data_da(conf)
    notas = []
    for numero, linha in comum.le_csv(a.csv):
        try:
            campos = [campo(linha, descricao, conf) for descricao in conf["nota"]["campos"]]
        except ValueError as e:
            raise ValueError(f"{a.csv}:{numero}: {e}") from None
        notas.append((linha["id"], campos, [comum.nome_da_fonte(linha["fonte"]), comum.identificador(linha["coluna"])]))
    nota = conf["nota"]
    tipo = {"nome": nota["nome"], "cartao": nota["cartao"], "campos": [d["nome"] for d in nota["campos"]],
            "editor": nota["editor"], "frente": comum.le_texto(a.frente), "verso": comum.le_texto(a.verso),
            "estilo": comum.le_texto(a.estilo)}
    soma = pacote_anki.grava(a.apkg, conf["baralho"], tipo, notas, data)
    print(f"{len(notas)} nota(s) gravada(s) em {a.apkg} (sha256 {soma})")
    return 0


def main():
    p = argparse.ArgumentParser(description="Grava o pacote do Anki a partir do CSV do baralho.")
    p.add_argument("configuracao", help="a configuração do baralho")
    p.add_argument("csv", help="o CSV do baralho, já conferido")
    p.add_argument("apkg", help="o pacote a gravar")
    p.add_argument("--frente", required=True, help="o modelo da frente do cartão")
    p.add_argument("--verso", required=True, help="o modelo do verso do cartão")
    p.add_argument("--estilo", required=True, help="o estilo (CSS) do cartão")
    return comum.roda(gera, p.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
