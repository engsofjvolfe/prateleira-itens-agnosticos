"""A forma do registro das chamadas e a gravacao de uma linha nele.

O registro e um arquivo de texto com uma linha por chamada registrada: um objeto JSON com a
sessao, a ferramenta e a entrada que ela recebeu, sem mais nada. A linha nunca se parte,
porque o JSON escreve a quebra de linha de um texto como escape, e cada linha termina com a
quebra. A ordem das linhas e a das chamadas. So biblioteca padrao.
"""
import fcntl
import json
import os

SESSAO, FERRAMENTA, ENTRADA = "sessao", "ferramenta", "entrada"  # as chaves de uma linha
PERMISSAO = 0o666  # a do arquivo que nasce, antes da mascara do sistema (umask), como a de um arquivo comum
CODIFICACAO, QUEBRA = "utf-8", "\n"


def linha(sessao, ferramenta, entrada):
    """O texto da linha de uma chamada, com a quebra do fim; as partes vem conferidas pelo
    evento.py."""
    return json.dumps({SESSAO: sessao, FERRAMENTA: ferramenta, ENTRADA: entrada}, ensure_ascii=False) + QUEBRA


def acrescenta(caminho, texto):
    """Poe o texto no fim do registro, com o arquivo trancado, para que duas chamadas ao mesmo
    tempo nao misturem as linhas. O arquivo que nao existe nasce; a pasta dele tem de existir."""
    bruto = texto.encode(CODIFICACAO)
    descritor = os.open(caminho, os.O_WRONLY | os.O_APPEND | os.O_CREAT, PERMISSAO)
    try:
        fcntl.flock(descritor, fcntl.LOCK_EX)
        feito = 0
        while feito < len(bruto):
            feito += os.write(descritor, bruto[feito:])
    finally:
        os.close(descritor)  # fechar solta a tranca
