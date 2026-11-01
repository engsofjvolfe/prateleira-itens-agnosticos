"""Gancho da leitura completa: todo documento se le inteiro, do comeco ao fim.

Antes de uma chamada de ferramenta:
  - do terminal: barra o comando que roda um comando que corta um documento, como grep,
    head ou sed, tambem dentro de outro, de $( ) ou de crases, ou depois de um prefixo, como
    xargs; o de mais de uma palavra, como git grep, conta tambem com outras palavras no meio;
    e barra o comando que nao se le;
  - de busca ou de resumo: barra sempre;
  - de leitura: deixa passar so a leitura que comeca na primeira linha do arquivo, a que
    continua na linha seguinte a ultima lida e a que repete o ultimo pedaco (como quando ele
    nao chegou); anota, para a sessao, ate onde cada arquivo foi lido, numa anotacao de cada
    arquivo, e o arquivo lido ate o fim perde a dele. O que nao e um arquivo de texto UTF-8
    fica de fora.
O bloqueio e a resposta que nega, com o texto do motivo e a parte que bloqueou. O erro ao
tratar uma chamada tambem a bloqueia, com o erro como motivo. A anotacao se grava de uma vez:
o texto vai para um arquivo novo, na pasta das anotacoes, que toma o lugar dela; outra
chamada, ao mesmo tempo, le a de antes ou a de depois, nunca metade.

No fim de uma resposta: com arquivo lido em parte, trava, com o texto do fim e uma linha
para cada arquivo, com as linhas lidas e as que ele tem, na ordem dos caminhos; as anotacoes
ficam, para a leitura continuar. Na volta da trava (fim_repetido), libera e apaga as
anotacoes da sessao. O erro no fim, e o protocolo ou o evento que nao se le, saem como erro.

A pasta das anotacoes e os comandos que cortam vem da configuracao (--config), lida pelo
molde dela com o extrator_comum.py, do extrator, que fica duas pastas acima (na prateleira,
em ganchos/<peca>/) ou na pasta irma (numa copia de teste); os prefixos, da configuracao da
leitura do terminal (--terminal); os textos, dos arquivos dados no comando (--motivo e
--fim). O evento, as ferramentas, os campos delas e as respostas vem do protocolo do
programa que roda o gancho (--protocolo), lido pelo protocolo.py, da pasta irma protocolo,
que da tambem a pasta das anotacoes de cada sessao e o arquivo da anotacao de cada arquivo
lido, dentro dela. O comando de terminal e a configuracao da leitura do terminal sao lidos
pelo leitura_do_terminal.py, da pasta irma leitura-do-terminal. So biblioteca padrao.
"""
import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent.parent / "extrator", PASTA.parent / "extrator", PASTA.parent / "leitura-do-terminal",
              PASTA.parent / "protocolo"):
    sys.path.insert(0, str(pasta))  # a ultima posta e a primeira lida
from extrator_comum import ErroDeDados, campo, le_conferido, le_texto  # noqa: E402
from leitura_do_terminal import ComandoIlegivel, comandos_achados, prefixos_do_terminal  # noqa: E402
import protocolo  # noqa: E402

MOLDE = PASTA / "esquemas" / "leitura-completa.schema.json"
CODIFICACAO = "utf-8"
QUEBRA, ITEM = "\n", "- "
NADA_LIDO = {"inicio": 0, "lidas": 0}  # o arquivo sem anotacao: so a primeira linha abre a leitura


def ler_configuracao(caminho, leitura):
    """A configuracao, lida pelo molde dela: a pasta das anotacoes, a partir da pasta da
    configuracao, e as palavras de cada comando que corta; e os prefixos, da configuracao da
    leitura do terminal (leitura)."""
    arquivo = Path(caminho).resolve()
    dados = le_conferido(arquivo, MOLDE)
    return {"estado": arquivo.parent / dados["estado"], "prefixos": prefixos_do_terminal(leitura),
            "comandos": [comando.split() for comando in dados["comandos"]]}


def situacao(caminho, lidas, total):
    """O arquivo, as linhas lidas dele, do comeco, e as que ele tem: caminho: lidas/total."""
    return f"{caminho}: {lidas}/{total}"


# ---- o terminal ----

def comando_que_corta(config, comando):
    """A parte do comando, ou de um comando de dentro dele, que roda um comando que corta, da
    palavra dele em diante; o sinal sem fechar, quando o comando nao se le; None quando nada
    corta."""
    achados = comandos_achados(comando, config["comandos"], config["prefixos"])  # le o comando so no next
    try:
        return next((parte for _, _, parte in achados), None)
    except ComandoIlegivel as erro:
        return str(erro)


# ---- a leitura ----

def linhas(arquivo):
    """Quantas linhas o arquivo tem, separadas pela quebra de linha; None quando ele nao e um
    arquivo de texto UTF-8."""
    if not arquivo.is_file():
        return None
    try:
        partes = arquivo.read_bytes().decode(CODIFICACAO).split(QUEBRA)
    except UnicodeDecodeError:
        return None
    return len(partes) - (partes[-1] == "")  # a quebra no fim nao abre outra linha


def numero(entrada, nome, sem_ele, minimo):
    """O numero inteiro do campo da entrada, ou sem_ele quando o campo falta ou e nulo; erro
    quando ele nao e inteiro ou fica abaixo do minimo."""
    if entrada.get(nome) is None:
        return sem_ele
    valor = campo(entrada, nome, int)
    if valor < minimo:
        raise ErroDeDados(f"o campo {nome} da leitura fica abaixo de {minimo}: {valor}")
    return valor


def anotado(nota):
    """{"caminho", "inicio", "lidas", "total"} da anotacao de um arquivo lido em parte: o
    caminho dele e, contadas a partir de 0, a primeira do arquivo, a linha em que comecou o
    ultimo pedaco, as linhas lidas e as que ele tem."""
    return json.loads(nota.read_text(encoding=CODIFICACAO))


def anota(nota, dados, pasta):
    """Grava a anotacao de uma vez: o texto vai para um arquivo novo, na pasta dada, fora da
    pasta da sessao, e ele toma o lugar da anotacao."""
    nota.parent.mkdir(parents=True, exist_ok=True)
    descritor, nova = tempfile.mkstemp(dir=pasta)
    with os.fdopen(descritor, "w", encoding=CODIFICACAO) as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False)
    os.replace(nova, nota)


def antes_da_leitura(config, leitura, partes):
    """A parte que barra a leitura, ou None quando ela passa: passa a que comeca na primeira
    linha (ou antes dela), na linha seguinte a ultima lida ou no comeco do ultimo pedaco. A
    que passa fica anotada; o arquivo lido ate o fim perde a anotacao."""
    entrada = partes["entrada"]
    arquivo = (Path(partes.get("pasta", "")) / Path(entrada[leitura["campo_caminho"]]).expanduser()).resolve()
    total = linhas(arquivo)
    if total is None:
        return None
    primeira = leitura["primeira_linha"]
    comeco = max(numero(entrada, leitura["campo_comeco"], primeira, 0) - primeira, 0)
    quantas = numero(entrada, leitura["campo_quantas"], leitura["linhas_sem_limite"], 1)
    nota = protocolo.anotacao(config["estado"], partes["sessao"], str(arquivo))
    antes = anotado(nota) if nota.is_file() else NADA_LIDO
    if comeco not in (0, antes["inicio"], antes["lidas"]):
        return situacao(arquivo, antes["lidas"], total)
    if comeco + quantas < total:
        anota(nota, {"caminho": str(arquivo), "inicio": comeco, "lidas": comeco + quantas, "total": total},
              config["estado"])
    else:
        nota.unlink(missing_ok=True)
    return None


# ---- os eventos ----

def antes(config, proto, partes):
    """A parte que barra a chamada, ou None quando ela passa. A ferramenta que o protocolo nao
    da como de terminal, de busca, de resumo nem de leitura e erro."""
    ferramenta = partes["ferramenta"]
    if ferramenta == proto["terminal"]["ferramenta"]:
        return comando_que_corta(config, partes["entrada"][proto["terminal"]["campo_comando"]])
    if ferramenta in proto["buscas"] or ferramenta in proto["resumos"]:
        return ferramenta
    if ferramenta in proto["leituras"]:
        return antes_da_leitura(config, proto["leituras"][ferramenta], partes)
    raise ErroDeDados(f"o protocolo não dá a ferramenta {ferramenta!r} como de terminal, de busca, de resumo nem de "
                      f"leitura")


def no_fim(config, proto, partes):
    """A trava do fim, com cada arquivo lido em parte, ou None. Na volta da trava, libera e
    apaga as anotacoes da sessao."""
    sessao = protocolo.anotacao(config["estado"], partes["sessao"])
    if partes.get("fim_repetido"):
        if sessao.is_dir():
            shutil.rmtree(sessao)
        return None
    notas = sessao.iterdir() if sessao.is_dir() else []
    arquivos = sorted((a["caminho"], a["lidas"], a["total"]) for a in map(anotado, notas))
    if not arquivos:
        return None
    itens = [ITEM + situacao(*arquivo) for arquivo in arquivos]
    return protocolo.resposta(proto, "trava", QUEBRA.join([config["fim"]] + itens))


def tratar(args, proto, partes):
    """A resposta ao evento, ou None quando nao ha o que dizer."""
    config = ler_configuracao(args.config, args.terminal)
    if partes["evento"] == "fim":
        return no_fim(dict(config, fim=le_texto(args.fim).strip()), proto, partes)
    motivo = le_texto(args.motivo).strip()
    parte = antes(config, proto, partes)
    return None if parte is None else protocolo.resposta(proto, "nega", motivo + QUEBRA + parte)


def main(argumentos=None):
    leitor = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    leitor.add_argument("--config", required=True, type=Path,
                        help="JSON com a pasta das anotações e os comandos que cortam")
    leitor.add_argument("--terminal", required=True, type=Path,
                        help="JSON da leitura do terminal, com os prefixos do shell")
    leitor.add_argument("--protocolo", required=True, type=Path,
                        help="JSON com o protocolo do programa que roda o gancho")
    leitor.add_argument("--motivo", required=True, type=Path, help="o texto do motivo do bloqueio")
    leitor.add_argument("--fim", required=True, type=Path,
                        help="o texto da trava do fim, que vem antes da lista dos arquivos lidos em parte")
    args = leitor.parse_args(argumentos)
    proto = protocolo.ler(args.protocolo)  # sem o protocolo nao ha como responder: o erro sai
    partes = protocolo.le_evento(proto, sys.stdin.read())  # sem o evento nao se sabe o que responder: o erro sai
    try:
        saida = tratar(args, proto, partes)
    except Exception as erro:  # antes de uma chamada, o que nao se confere nao passa; no fim, o erro sai
        if partes["evento"] == "fim":
            raise
        saida = protocolo.resposta(proto, "nega", f"{type(erro).__name__}: {erro}")
    if saida is not None:
        print(json.dumps(saida, ensure_ascii=False))


if __name__ == "__main__":
    main()
