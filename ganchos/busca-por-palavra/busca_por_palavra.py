"""Gancho contra a busca por palavra para achar ou decidir o que ler ou mudar.

Antes de uma chamada da ferramenta de terminal: bloqueia o comando, ou um comando de dentro
dele, que roda uma busca (como grep ou git grep) com um padrao que nao e um dos livres, como
o que lista os titulos de um texto; com os padroes tirados de um arquivo; ou sem padrao que
se leia. O comando que nao se le tambem e bloqueado. Antes de uma chamada de uma ferramenta
de busca: bloqueia a busca cujo padrao nao e um dos livres. O motivo do bloqueio e o texto
dado no comando, com a parte que o causou.

Com --exatas, um arquivo e uma forma, dado uma vez para cada arquivo, passa tambem, no
terminal, a busca exata: a que le so um desses arquivos, com cada padrao inteiro na forma
dele, uma expressao regular, como um codigo que o arquivo guarda. O caminho de cada arquivo
da busca parte da pasta de onde o comando roda, que o evento traz.

Pode barrar a mais, nunca a menos. Os padroes de uma busca sao o valor de cada opcao de
padrao (depois do = na longa, o resto da palavra depois da letra na curta, ou a palavra
seguinte) e, sem nenhuma, a primeira palavra solta; os arquivos sao as outras soltas. Solta
e a palavra que nao e opcao nem valor de opcao de padrao, e toda palavra depois de --. O
comando de busca de mais de uma palavra, como git grep, conta tambem com outras palavras no
meio. Uma palavra depois de um prefixo, como xargs, conta como comando.

As buscas do terminal, as opcoes e os padroes livres vem da configuracao (--config), lida
pelo molde dela com o extrator_comum.py, do extrator, que fica duas pastas acima (na
prateleira, em ganchos/<peca>/) ou na pasta irma (numa copia de teste); os prefixos, da
configuracao da leitura do terminal (--terminal); o texto do motivo, do arquivo dado no
comando (--motivo). O evento, as ferramentas e a resposta vem do protocolo do programa que
roda o gancho (--protocolo), lido pelo protocolo.py, da pasta irma protocolo. O comando e a
configuracao da leitura do terminal sao lidos pelo leitura_do_terminal.py, da pasta irma
leitura-do-terminal. So biblioteca padrao.
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent.parent / "extrator", PASTA.parent / "extrator", PASTA.parent / "leitura-do-terminal",
              PASTA.parent / "protocolo"):
    sys.path.insert(0, str(pasta))  # a ultima posta e a primeira lida
from extrator_comum import ErroDeDados, le_conferido, le_texto  # noqa: E402
from leitura_do_terminal import (ATRIBUICAO, OPCAO, OPCAO_LONGA, ComandoIlegivel, comandos_achados,  # noqa: E402
                                 letras_iniciais, opcao_bate, prefixos_do_terminal)
import protocolo  # noqa: E402

MOLDE = PASTA / "esquemas" / "busca-por-palavra.schema.json"
EVENTO = "antes"  # o evento que o gancho trata, pelo nome que o protocolo.py da a ele
QUEBRA = "\n"
FIM_DAS_OPCOES = "--"  # a palavra depois da qual toda palavra de uma busca e solta
Exata = collections.namedtuple("Exata", "arquivo forma pasta")
# a busca exata do --exatas: o arquivo, com o caminho resolvido; a forma de cada padrao, compilada; e a pasta de onde
# o comando roda


def ler_configuracao(caminho, leitura):
    """A configuracao, lida pelo molde dela, e os prefixos, da configuracao da leitura do terminal (leitura); cada
    campo e lido ja aqui, e o que falta e erro logo."""
    arquivo = Path(caminho).resolve()
    dados = le_conferido(arquivo, MOLDE)
    return {
        "livres": set(dados["padroes_livres"]),
        "prefixos": prefixos_do_terminal(leitura),
        "buscas": [{"palavras": busca["comando"].split(), "do_padrao": list(busca["opcoes_do_padrao"]),
                    "de_arquivo": list(busca["opcoes_de_arquivo"])} for busca in dados["buscas"]],
    }


def buscas_exatas(argumentos, partes):
    """As Exatas do --exatas, uma para cada arquivo dado, com a pasta de onde o comando do evento roda; nenhuma sem
    ele. O arquivo que nao existe e a forma que nao e expressao regular sao erro."""
    exatas = []
    for caminho, forma in argumentos or []:
        arquivo = Path(caminho).resolve()
        if not arquivo.is_file():
            raise FileNotFoundError(arquivo)
        exatas.append(Exata(arquivo, re.compile(forma), Path(partes["pasta"])))
    return exatas


def valor_da_opcao(opcao, palavra, seguinte):
    """(valor, se ele e a palavra seguinte) da opcao que bate com a palavra: o que vem depois do = na longa, ou o resto
    da palavra depois da letra da curta; sem nada ali, a palavra seguinte (None, no fim)."""
    if opcao.startswith(OPCAO_LONGA):
        _, sinal, valor = palavra.partition(ATRIBUICAO)
        return (valor, False) if sinal else (seguinte, True)
    letras = palavra[len(OPCAO):]
    resto = letras[letras_iniciais(letras).index(opcao[len(OPCAO):]) + 1:]
    return (resto, False) if resto else (seguinte, True)


def padroes_da_busca(busca, seguintes):
    """(padroes, arquivos, a opcao que tira os padroes de um arquivo, ou None): o valor de cada opcao de padrao e, sem
    nenhuma, a primeira palavra solta (None, sem ela); os arquivos sao as outras soltas. Solta e a palavra que nao e
    opcao nem valor de opcao de padrao, e toda palavra depois de FIM_DAS_OPCOES."""
    padroes, soltas, pular, fim = [], [], False, False
    for k, palavra in enumerate(seguintes):
        if pular:
            pular = False
        elif fim or not palavra.startswith(OPCAO):
            soltas.append(palavra)
        elif palavra == FIM_DAS_OPCOES:
            fim = True
        elif any(opcao_bate(opcao, palavra) for opcao in busca["de_arquivo"]):
            return padroes, soltas, palavra
        else:
            proxima = seguintes[k + 1] if k + 1 < len(seguintes) else None
            for opcao in busca["do_padrao"]:
                if opcao_bate(opcao, palavra):
                    valor, da_seguinte = valor_da_opcao(opcao, palavra, proxima)
                    padroes.append(valor)
                    pular = pular or da_seguinte
    if not padroes:
        return [soltas[0] if soltas else None], soltas[1:], None
    return padroes, soltas, None


def eh_exata(exata, padroes, arquivos):
    """Se a busca e a exata: cada padrao inteiro na forma, e ao menos um arquivo, todos o da exata, com o caminho
    partindo da pasta de onde o comando roda."""
    return (all(padrao is not None and exata.forma.fullmatch(padrao) for padrao in padroes) and bool(arquivos)
            and all((exata.pasta / arquivo).resolve() == exata.arquivo for arquivo in arquivos))


def passa(config, exatas, padroes, arquivos, de_arquivo):
    """Se a busca passa: sem padrao tirado de arquivo, e com todo padrao livre ou sendo a exata de um arquivo do
    --exatas."""
    if de_arquivo:
        return False
    if all(padrao in config["livres"] for padrao in padroes):
        return True
    return any(eh_exata(exata, padroes, arquivos) for exata in exatas)


def parte_barrada(config, exatas, comando):
    """A primeira busca barrada do comando ou de um comando de dentro dele, da palavra dela em diante; None quando nao
    ha."""
    buscas = config["buscas"]
    for indice, seguintes, parte in comandos_achados(comando, [b["palavras"] for b in buscas], config["prefixos"]):
        if not passa(config, exatas, *padroes_da_busca(buscas[indice], seguintes)):
            return parte
    return None


def parte_da_entrada(config, proto, exatas, ferramenta, entrada):
    """O que bloqueia a ferramenta: no terminal, a busca barrada ou o comando que nao se le;
    numa ferramenta de busca, o padrao que nao e livre; None quando nada bloqueia. A
    ferramenta que o protocolo nao da como de terminal nem de busca e erro (KeyError)."""
    terminal = proto["terminal"]
    if ferramenta == terminal["ferramenta"]:
        try:
            return parte_barrada(config, exatas, entrada[terminal["campo_comando"]])
        except ComandoIlegivel as erro:
            return str(erro)
    campo = proto["buscas"][ferramenta]
    padrao = entrada.get(campo)
    return None if padrao in config["livres"] else f"{ferramenta}: {padrao}"


def main(argumentos=None):
    leitor = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    leitor.add_argument("--config", required=True, type=Path, help="JSON com as buscas e os padrões livres")
    leitor.add_argument("--terminal", required=True, type=Path,
                        help="JSON da leitura do terminal, com os prefixos do shell")
    leitor.add_argument("--protocolo", required=True, type=Path,
                        help="JSON com o protocolo do programa que roda o gancho")
    leitor.add_argument("--motivo", required=True, type=Path, help="o texto do motivo do bloqueio")
    leitor.add_argument("--exatas", nargs=2, action="append", metavar=("ARQUIVO", "FORMA"),
                        help="o arquivo de uma busca exata e a forma de cada padrão dela, uma expressão regular; "
                             "uma vez para cada arquivo")
    args = leitor.parse_args(argumentos)
    config = dict(ler_configuracao(args.config, args.terminal), motivo=le_texto(args.motivo).strip())
    proto = protocolo.ler(args.protocolo)
    partes = protocolo.le_evento(proto, sys.stdin.read())
    if partes["evento"] != EVENTO:
        raise ErroDeDados(f"o gancho trata só o evento de antes de uma chamada, e chegou o de {partes['evento']}")
    parte = parte_da_entrada(config, proto, buscas_exatas(args.exatas, partes), partes["ferramenta"], partes["entrada"])
    if parte is not None:
        print(json.dumps(protocolo.resposta(proto, "nega", config["motivo"] + QUEBRA + parte), ensure_ascii=False))


if __name__ == "__main__":
    main()
