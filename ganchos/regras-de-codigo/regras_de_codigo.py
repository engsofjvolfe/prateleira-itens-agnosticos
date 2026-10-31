"""Gancho para as regras de codigo.

Um so programa para os eventos ligados a ele; o evento vem no JSON que o programa que roda o
gancho manda pela entrada padrao.

- Antes de uma chamada de ferramenta que escreve arquivo: anota o arquivo; no
  primeiro arquivo da tarefa, entrega as regras antes da escrita. O arquivo de
  um formato da lista sem_conferencia (a extensao, sem contar maiusculas), como
  um texto ou uma planilha, fica de fora; os outros, sem extensao ou de
  extensao que a lista nao traz, entram.
- Antes de uma chamada do terminal: bloqueia o comando que escreve em arquivo,
  roda codigo escrito dentro dele ou nao pode ser lido.
- No fim de uma resposta: com arquivos anotados, trava o encerramento e pede a
  conferencia; na volta da conferencia, libera. Nos dois casos a anotacao e
  apagada.

As listas e a pasta da anotacao vem da configuracao (--config), lida pelo molde dela com o
extrator_comum.py, do extrator, que fica duas pastas acima (na prateleira, em
ganchos/<peca>/) ou na pasta irma (numa copia de teste); os prefixos, da configuracao da
leitura do terminal (--terminal); os textos, dos arquivos dados no comando: as regras
(--regras), a ordem de conferir (--fim) e o aviso do bloqueio (--bloqueio). O evento, as
ferramentas e as respostas vem do protocolo do programa (--protocolo), lido pelo
protocolo.py, da pasta irma protocolo, que da tambem o arquivo da anotacao de cada sessao,
com o nome tirado do id dela. O comando de terminal e a configuracao da leitura do terminal
sao lidos pelo leitura_do_terminal.py, da pasta irma leitura-do-terminal. So biblioteca
padrao.
"""
import argparse
import json
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent.parent / "extrator", PASTA.parent / "extrator", PASTA.parent / "leitura-do-terminal",
              PASTA.parent / "protocolo"):
    sys.path.insert(0, str(pasta))  # a ultima posta e a primeira lida
from extrator_comum import le_conferido, le_texto  # noqa: E402
from leitura_do_terminal import (DUPLICACAO, ESCRITA, FECHA_DESCRITOR, OPCAO, TEXTO_EMBUTIDO,  # noqa: E402
                                 ComandoIlegivel, eh_redirecionamento, lidos, opcao_bate, posicoes_de_comando,
                                 prefixos_do_terminal)
import protocolo  # noqa: E402

MOLDE = PASTA / "esquemas" / "regras-de-codigo.schema.json"
CODIFICACAO = "utf-8"

# Textos.
QUEBRA = "\n"
ITEM_DE_LISTA = "- "
SEPARADOR_DE_TEXTOS = QUEBRA * 2


def ler_configuracao(caminho, leitura):
    """A configuracao, lida pelo molde dela, com os prefixos da configuracao da leitura do terminal (leitura) entre
    os dados do terminal."""
    arquivo = Path(caminho).resolve()
    dados = le_conferido(arquivo, MOLDE)
    terminal = dados["terminal"]
    return {
        "estado": arquivo.parent / dados["estado"],
        "sem_conferencia": {formato.casefold() for formato in dados["sem_conferencia"]},
        "terminal": {
            "destinos_livres": set(terminal["destinos_livres"]),
            "prefixos": prefixos_do_terminal(leitura),
            "sempre_escrevem": set(terminal["sempre_escrevem"]),
            "escrevem_com_opcao": {
                nome: list(opcoes) for nome, opcoes in terminal["escrevem_com_opcao"].items()
            },
            "leem_codigo_sem_arquivo": set(terminal["leem_codigo_sem_arquivo"]),
        },
    }


def juntar(caminhos):
    return SEPARADOR_DE_TEXTOS.join(le_texto(c).strip() for c in caminhos)


# ---- analise do comando de terminal ----

def destino_livre(terminal, operador, destino):
    if destino is None or destino[1]:
        return False
    alvo = destino[0]
    if operador.endswith(DUPLICACAO) and (alvo.isdigit() or alvo == FECHA_DESCRITOR):
        return True
    return alvo in terminal["destinos_livres"]


def redirecionamento_que_escreve(terminal, partes):
    for numero, (texto, operador) in enumerate(partes):
        if not operador:
            continue
        if TEXTO_EMBUTIDO in texto:
            return texto
        if ESCRITA in texto and eh_redirecionamento(texto):
            destino = partes[numero + 1] if numero + 1 < len(partes) else None
            if not destino_livre(terminal, texto, destino):
                return " ".join([texto] + ([destino[0]] if destino else []))
    return None


def comando_que_escreve(terminal, palavras):
    for posicao in posicoes_de_comando(palavras, terminal["prefixos"]):
        nome = Path(palavras[posicao]).name
        seguintes = palavras[posicao + 1:]
        if nome in terminal["sempre_escrevem"]:
            return nome
        for opcao in terminal["escrevem_com_opcao"].get(nome, []):
            for palavra in seguintes:
                if opcao_bate(opcao, palavra):
                    return f"{nome} {palavra}"
        sem_arquivo = all(palavra.startswith(OPCAO) for palavra in seguintes)
        if nome in terminal["leem_codigo_sem_arquivo"] and sem_arquivo:
            return nome
    return None


def parte_que_escreve(terminal, comando):
    """Primeira parte do comando, ou de um comando de dentro dele, que escreve em arquivo ou roda codigo escrito
    nele; None se nao ha."""
    for partes, simples in lidos(comando):
        achado = redirecionamento_que_escreve(terminal, partes)
        for palavras in simples:
            achado = achado or comando_que_escreve(terminal, palavras)
        if achado:
            return achado
    return None


# ---- eventos ----

def antes_do_terminal(config, proto, entrada):
    try:
        parte = parte_que_escreve(config["terminal"], entrada[proto["terminal"]["campo_comando"]])
    except ComandoIlegivel as erro:
        parte = str(erro)
    if parte is None:
        return None
    motivo = juntar([config["bloqueio"]]) + QUEBRA + parte
    return protocolo.resposta(proto, "nega", motivo)


def antes_da_escrita(config, proto, entrada, anotacao):
    campos = [campo for campo in proto["escritas"]["campos_caminho"] if campo in entrada]
    if not campos:
        raise KeyError(proto["escritas"]["campos_caminho"])
    if Path(entrada[campos[0]]).suffix.casefold() in config["sem_conferencia"]:
        return None
    primeira = not anotacao.exists()
    anotacao.parent.mkdir(parents=True, exist_ok=True)
    with anotacao.open("a", encoding=CODIFICACAO) as arquivo:
        arquivo.write(entrada[campos[0]] + QUEBRA)
    if not primeira:
        return None
    return protocolo.resposta(proto, "contexto", juntar(config["regras"]))


def antes(config, proto, partes, anotacao):
    if partes["ferramenta"] == proto["terminal"]["ferramenta"]:
        return antes_do_terminal(config, proto, partes["entrada"])
    return antes_da_escrita(config, proto, partes["entrada"], anotacao)


def no_fim(config, proto, partes, anotacao):
    if not anotacao.exists():
        return None
    caminhos = list(dict.fromkeys(le_texto(anotacao).splitlines()))
    anotacao.unlink()
    if partes.get("fim_repetido"):
        return None
    lista = QUEBRA.join(ITEM_DE_LISTA + caminho for caminho in caminhos)
    motivo = juntar(config["regras"] + [config["fim"]]) + QUEBRA + lista
    return protocolo.resposta(proto, "trava", motivo)


TRATADORES = {"antes": antes, "fim": no_fim}  # pelo nome que o protocolo.py da a cada evento


def main(argumentos=None):
    leitor = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    leitor.add_argument("--config", required=True, type=Path, help="JSON com as listas e a pasta da anotação")
    leitor.add_argument("--terminal", required=True, type=Path,
                        help="JSON da leitura do terminal, com os prefixos do shell")
    leitor.add_argument("--protocolo", required=True, type=Path,
                        help="JSON com o protocolo do programa que roda o gancho")
    leitor.add_argument("--regras", action="append", required=True, type=Path,
                        help="texto de regras, na ordem em que são entregues (pode repetir)")
    leitor.add_argument("--fim", required=True, type=Path, help="texto da ordem de conferir")
    leitor.add_argument("--bloqueio", required=True, type=Path, help="texto do bloqueio no terminal")
    args = leitor.parse_args(argumentos)
    config = dict(ler_configuracao(args.config, args.terminal), regras=list(args.regras),
                  fim=args.fim, bloqueio=args.bloqueio)
    proto = protocolo.ler(args.protocolo)
    partes = protocolo.le_evento(proto, sys.stdin.read())
    anotacao = protocolo.anotacao(config["estado"], partes["sessao"])
    saida = TRATADORES[partes["evento"]](config, proto, partes, anotacao)
    if saida is not None:
        print(json.dumps(saida, ensure_ascii=False))


if __name__ == "__main__":
    main()
