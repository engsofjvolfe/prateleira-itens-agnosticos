"""Le transcricoes de sessoes gravadas em JSONL, como as de um programa de IA: os arquivos de uma pasta e das
subpastas dela cujo nome segue um padrao, cada um com um evento JSON por linha.

Entrega cada linha que nao esta em branco, com a transcricao e o numero da linha, e o evento dela, que e None quando a
linha nao esta na codificacao dada ou nao e um objeto JSON; e os blocos do conteudo da mensagem de um evento. O
padrao, a codificacao e os nomes dos campos vem do programa que o importa. So biblioteca padrao.
"""
import json


def eventos(pasta, padrao, codificacao):
    """(transcricao, numero da linha, evento) de cada linha que nao esta em branco das transcricoes da pasta e das
    subpastas dela, as transcricoes na ordem do caminho e as linhas na ordem delas."""
    for transcricao in sorted(p for p in pasta.rglob(padrao) if p.is_file()):
        with transcricao.open("rb") as arquivo:
            for numero, bruta in enumerate(arquivo, 1):
                if bruta.strip():
                    yield transcricao, numero, le_linha(bruta, codificacao)


def le_linha(bruta, codificacao):
    """O evento de uma linha: o objeto JSON dela; None quando ela nao esta na codificacao ou nao e um objeto JSON."""
    try:
        lido = json.loads(bruta.decode(codificacao))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return lido if isinstance(lido, dict) else None


def blocos(evento, mensagem, conteudo):
    """(posicao, bloco) de cada bloco do conteudo da mensagem do evento -- mensagem e conteudo sao os nomes dos dois
    campos --, quando a mensagem e um objeto e o conteudo uma lista; o bloco que nao e objeto fica de fora."""
    corpo = evento.get(mensagem)
    lista = corpo.get(conteudo) if isinstance(corpo, dict) else None
    return [(k, b) for k, b in enumerate(lista) if isinstance(b, dict)] if isinstance(lista, list) else []
