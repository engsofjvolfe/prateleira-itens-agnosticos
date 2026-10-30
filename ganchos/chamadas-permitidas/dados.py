"""A leitura conferida dos arquivos da peca, num lugar so: ler um texto ou um JSON e conferir,
valor por valor, a forma que o README da peca descreve. O que nao tem a forma e erro, com o
arquivo e o lugar do valor dentro dele. So biblioteca padrao.
"""
import json
from pathlib import Path

CODIFICACAO = "utf-8"
QUEBRA = "\n"


class ErroDeDados(Exception):
    """O que impede o trabalho; a mensagem diz o que e onde."""


def le_texto(caminho):
    """O texto de um arquivo em UTF-8."""
    try:
        return Path(caminho).read_text(encoding=CODIFICACAO)
    except (OSError, UnicodeDecodeError) as erro:
        raise ErroDeDados(f"{caminho}: não se lê como texto em UTF-8 ({erro})")


def le_json(caminho):
    """Os dados de um arquivo JSON em UTF-8."""
    try:
        return json.loads(le_texto(caminho))
    except json.JSONDecodeError as erro:
        raise ErroDeDados(f"{caminho}: não se lê como JSON ({erro})")


def objeto(valor, onde, chaves=None):
    """O objeto; com chaves, so quando ele tem exatamente essas."""
    if not isinstance(valor, dict):
        raise ErroDeDados(f"{onde}: não é um objeto: {valor!r}")
    if chaves is not None and set(valor) != set(chaves):
        raise ErroDeDados(f"{onde}: as chaves são {sorted(valor)}, e têm de ser {sorted(chaves)}")
    return valor


def texto(valor, onde):
    """O texto, quando ele tem ao menos um caractere."""
    if not isinstance(valor, str) or not valor:
        raise ErroDeDados(f"{onde}: não é um texto com ao menos um caractere: {valor!r}")
    return valor


def lista(valor, onde, item):
    """A lista, com cada item conferido por item(valor, onde)."""
    if not isinstance(valor, list):
        raise ErroDeDados(f"{onde}: não é uma lista: {valor!r}")
    return [item(v, f"{onde}[{k}]") for k, v in enumerate(valor)]
