"""Gancho que guarda o arquivo para onde uma limpeza leva o que tira de outros arquivos.

O destino (--destino) so cresce: o que ele ja tem nunca muda nem sai, e o texto novo entra
entre blocos, separado deles por uma linha em branco. E so recebe texto na mesma resposta
em que saiu texto de uma origem (--origem, um arquivo ou uma pasta): a limpeza tira
primeiro da origem e depois poe no destino.

- Antes de uma chamada de ferramenta que escreve arquivo: numa origem, a escrita que tira ou
  muda texto que la estava fica anotada para a sessao; no destino, e bloqueada a escrita
  que nao so cresce, a que chega sem nada anotado e a da ferramenta que o gancho nao sabe
  ler.
- Antes de uma chamada do terminal: e bloqueado o comando que tem o nome de um destino.
- No fim de uma resposta: a anotacao e apagada; a resposta seguinte comeca sem nada saido.

Quando tratar um evento da erro e a entrada tem o nome de um destino, o gancho bloqueia, com
o erro no motivo; nos outros eventos, e com o protocolo que nao se le, sai com o erro. A
pasta das anotacoes vem da configuracao (--config), lida pelo molde dela com o
extrator_comum.py, do extrator, que fica duas pastas acima (na prateleira, em
ganchos/<peca>/) ou na pasta irma (numa copia de teste); os textos dos bloqueios, dos
arquivos dados no comando (--aviso-muda, --aviso-sem-origem, --aviso-terminal). O evento,
as ferramentas, os campos delas e a resposta vem do protocolo do programa que roda o gancho
(--protocolo), lido pelo protocolo.py, da pasta irma protocolo, que da tambem o arquivo da
anotacao de cada sessao. So biblioteca padrao.
"""
import argparse
import difflib
import json
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent.parent / "extrator", PASTA.parent / "extrator", PASTA.parent / "protocolo"):
    sys.path.insert(0, str(pasta))  # a ultima posta e a primeira lida
import extrator_comum  # noqa: E402
import protocolo  # noqa: E402

MOLDE = PASTA / "esquemas" / "destino-da-limpeza.schema.json"
TIRAM, INSERE = ("replace", "delete"), "insert"  # as operacoes do difflib que tiram ou mudam linhas, e a que poe
AVISOS = {  # os textos dos bloqueios, pelo nome da opcao do comando que os da, e a ajuda de cada opcao
    "muda": "texto do bloqueio da escrita que não só faz o destino crescer, entre blocos",
    "sem_origem": "texto do bloqueio da escrita no destino sem nada saído de uma origem",
    "terminal": "texto do bloqueio do comando de terminal que nomeia um destino",
}
QUEBRA, ITEM = "\n", "- "


def ler_configuracao(caminho):
    """A configuracao, lida pelo molde dela: a pasta das anotacoes, a partir da pasta da
    configuracao."""
    arquivo = Path(caminho).resolve()
    dados = extrator_comum.le_conferido(arquivo, MOLDE)
    return {"estado": arquivo.parent / dados["estado"]}


def resolvido(caminho):
    return Path(caminho).expanduser().resolve()


def dentro(arquivo, lugares):
    """Se o arquivo e um dos lugares ou esta dentro de um deles."""
    return any(arquivo == lugar or lugar in arquivo.parents for lugar in lugares)


def nomeados(destinos, texto):
    """Os destinos cujo nome esta no texto, como esta ou escrito como num JSON."""
    return [d for d in destinos if d.name in texto or json.dumps(d.name)[1:-1] in texto]


def nega(proto, motivo, caminhos):
    """A resposta que bloqueia a ferramenta: o motivo e uma linha para cada caminho."""
    return protocolo.resposta(proto, "nega", QUEBRA.join([motivo] + [ITEM + str(c) for c in caminhos]))


# ---- o texto do arquivo antes e depois da escrita ----

def depois_da_troca(texto, entrada, campos):
    """O texto do arquivo depois da troca: na primeira vez em que o trecho de antes aparece,
    ou em todas, quando a entrada pede; o mesmo texto, quando o trecho nao esta nele (a
    ferramenta recusa a troca)."""
    vezes = -1 if entrada.get(campos["todas"]) else 1  # -1: todas
    return texto.replace(entrada[campos["antes"]], entrada[campos["depois"]], vezes)


def textos_da_escrita(escritas, ferramenta, entrada, arquivo):
    """(texto de antes, texto de depois) do arquivo, ou None quando o gancho nao sabe ler a
    ferramenta."""
    antes = extrator_comum.le_texto(arquivo) if arquivo.is_file() else ""
    if ferramenta in escritas["trocas"]:
        return antes, depois_da_troca(antes, entrada, escritas["trocas"][ferramenta])
    if ferramenta in escritas["inteiros"]:
        return antes, entrada[escritas["inteiros"][ferramenta]]
    return None


def operacoes(antes, depois):
    """(linhas de antes, linhas de depois, operacoes que levam umas as outras), sempre as
    mesmas para os mesmos textos: o difflib sem a heuristica que pula linhas repetidas."""
    velhas, novas = antes.splitlines(), depois.splitlines()
    return velhas, novas, difflib.SequenceMatcher(None, velhas, novas, autojunk=False).get_opcodes()


def tira_texto(antes, depois):
    """Se alguma linha de antes sai ou muda."""
    return any(op in TIRAM for op, *_ in operacoes(antes, depois)[2])


def cheia(linhas, i):
    """Se a linha i existe e nao esta em branco."""
    return 0 <= i < len(linhas) and bool(linhas[i].strip())


def so_cresce(antes, depois):
    """Se nenhuma linha de antes sai ou muda e cada trecho novo fica entre blocos: nenhuma
    ponta dele e uma linha cheia encostada numa linha cheia de antes."""
    velhas, novas, ops = operacoes(antes, depois)
    for op, i1, _, j1, j2 in ops:
        if op in TIRAM:
            return False
        grudado = (cheia(velhas, i1 - 1) and cheia(novas, j1)) or (cheia(velhas, i1) and cheia(novas, j2 - 1))
        if op == INSERE and grudado:
            return False
    return True


# ---- eventos ----

def antes_da_escrita(config, proto, lugares, partes):
    entrada, escritas = partes["entrada"], proto["escritas"]
    campos = [campo for campo in escritas["campos_caminho"] if campo in entrada]
    if not campos:
        raise KeyError(f"nenhum campo de caminho conhecido na entrada: {escritas['campos_caminho']}")
    arquivo = resolvido(entrada[campos[0]])
    destino, origem = arquivo in lugares.destinos, dentro(arquivo, lugares.origens)
    if not (destino or origem):
        return None
    textos = textos_da_escrita(escritas, partes["ferramenta"], entrada, arquivo)
    nota = protocolo.anotacao(config["estado"], partes["sessao"])  # anota que saiu texto de uma origem
    if destino:
        if textos is None or not so_cresce(*textos):
            return nega(proto, config["avisos"]["muda"], [arquivo])
        if textos[0] != textos[1] and not nota.exists():
            return nega(proto, config["avisos"]["sem_origem"], lugares.origens)
        return None
    if textos is not None and tira_texto(*textos):
        nota.parent.mkdir(parents=True, exist_ok=True)
        nota.touch()
    return None


def antes_do_terminal(config, proto, lugares, partes):
    achados = nomeados(lugares.destinos, partes["entrada"][proto["terminal"]["campo_comando"]])
    return nega(proto, config["avisos"]["terminal"], achados) if achados else None


def no_fim(config, proto, lugares, partes):
    protocolo.anotacao(config["estado"], partes["sessao"]).unlink(missing_ok=True)
    return None


def tratar(config, proto, lugares, entrada):
    partes = protocolo.le_evento(proto, entrada)
    if partes["evento"] == "fim":
        return no_fim(config, proto, lugares, partes)
    if partes["ferramenta"] == proto["terminal"]["ferramenta"]:
        return antes_do_terminal(config, proto, lugares, partes)
    return antes_da_escrita(config, proto, lugares, partes)


def main(argumentos=None):
    leitor = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    leitor.add_argument("--config", required=True, type=Path, help="JSON com a pasta das anotações")
    leitor.add_argument("--protocolo", required=True, type=Path,
                        help="JSON com o protocolo do programa que roda o gancho")
    leitor.add_argument("--destino", action="append", required=True, type=Path, dest="destinos",
                        help="arquivo que só cresce com o que sai das origens (pode repetir)")
    leitor.add_argument("--origem", action="append", required=True, type=Path, dest="origens",
                        help="arquivo ou pasta de onde a limpeza tira texto (pode repetir)")
    for aviso, ajuda in AVISOS.items():
        leitor.add_argument(f"--aviso-{aviso.replace('_', '-')}", required=True, type=Path, dest=aviso, help=ajuda)
    args = leitor.parse_args(argumentos)
    lugares = argparse.Namespace(destinos=[resolvido(d) for d in args.destinos],
                                 origens=[resolvido(o) for o in args.origens])
    entrada = sys.stdin.read()
    proto = protocolo.ler(args.protocolo)  # sem o protocolo nao ha como responder: o erro sai
    try:
        config = dict(ler_configuracao(args.config), avisos={
            aviso: extrator_comum.le_texto(getattr(args, aviso)).strip() for aviso in AVISOS})
        saida = tratar(config, proto, lugares, entrada)
    except Exception as erro:  # o que nao se confere nao passa, quando toca um destino
        achados = nomeados(lugares.destinos, entrada)
        if not achados:
            raise
        saida = nega(proto, f"{type(erro).__name__}: {erro}", achados)
    if saida is not None:
        print(json.dumps(saida, ensure_ascii=False))


if __name__ == "__main__":
    main()
