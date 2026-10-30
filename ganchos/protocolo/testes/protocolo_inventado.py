"""
Um protocolo inventado, para os testes dos ganchos que usam o protocolo.py: os nomes dos
eventos, as chaves do evento e os modelos das respostas sao sorteados, com letras de fora do
ASCII, e as ferramentas sao as que cada teste da. Da tambem o evento em texto JSON e o texto
que uma resposta do gancho traz. Nao se roda: os testes dos ganchos o importam desta pasta.
"""
import json
from pathlib import Path

LUGAR = "{texto}"  # o lugar do texto num modelo de resposta, como o README do protocolo o escreve
PARTES = ("evento", "sessao", "ferramenta", "entrada", "pasta", "fim_repetido")  # as chaves, pelo README
RESPOSTAS = ("nega", "contexto", "trava")
LETRAS, ACENTOS = "abcdefghijklmnop", "áçõüé"
VERSAO = json.loads((Path(__file__).resolve().parent.parent / "esquemas" / "protocolo.schema.json")
                    .read_text(encoding="utf-8"))["properties"]["versao_schema"]["const"]


def nomes_sorteados(sorte, quantos):
    """Os nomes sorteados, todos diferentes, cada um com uma letra de fora do ASCII."""
    saida = []
    while len(saida) < quantos:
        nome = "".join(sorte.choice(LETRAS) for _ in range(sorte.randint(3, 7))) + sorte.choice(ACENTOS)
        if nome not in saida:
            saida.append(nome)
    return saida


def inventado(sorte, terminal, buscas=(), escritas=None, leituras=(), resumos=()):
    """Um protocolo completo: as ferramentas dadas (terminal e um objeto com a ferramenta e o
    campo do comando; buscas e leituras, listas como as do molde; escritas, o objeto do
    molde, ou um campo de caminho sorteado e nenhuma troca nem inteiro) e o resto sorteado.
    Cada modelo de resposta tem chaves so dele, com o lugar do texto num texto de dentro."""
    nomes = iter(nomes_sorteados(sorte, 3 + len(PARTES) + 3 * len(RESPOSTAS)))
    return {
        "versao_schema": VERSAO,
        "eventos": {"antes": next(nomes), "fim": next(nomes)},
        "chaves": {p: next(nomes) for p in PARTES},
        "respostas": {r: {next(nomes): sorte.randint(0, 9), next(nomes): [f"{next(nomes)} {LUGAR}"]}
                      for r in RESPOSTAS},
        "terminal": dict(terminal),
        "buscas": list(buscas),
        "escritas": escritas or {"campos_caminho": [next(nomes)], "trocas": {}, "inteiros": {}},
        "leituras": list(leituras),
        "resumos": list(resumos),
    }


def evento(protocolo, qual, **partes):
    """O texto JSON do evento qual ("antes" ou "fim"), com as partes dadas pelo nome no molde."""
    dados = {protocolo["chaves"]["evento"]: protocolo["eventos"][qual]}
    dados.update({protocolo["chaves"][p]: valor for p, valor in partes.items()})
    return json.dumps(dados, ensure_ascii=False)


def bate(modelo, valor, achados):
    """Se o valor e o modelo com um texto no lugar de {texto}; guarda em achados cada texto
    que ficou no lugar dele."""
    if isinstance(modelo, str) and LUGAR in modelo:
        antes, _, depois = modelo.partition(LUGAR)
        if not (isinstance(valor, str) and len(valor) >= len(antes) + len(depois)
                and valor.startswith(antes) and valor.endswith(depois)):
            return False
        achados.append(valor[len(antes):len(valor) - len(depois)])
        return True
    if isinstance(modelo, dict):
        return isinstance(valor, dict) and modelo.keys() == valor.keys() and all(
            bate(modelo[k], valor[k], achados) for k in modelo)
    if isinstance(modelo, list):
        return isinstance(valor, list) and len(modelo) == len(valor) and all(
            bate(m, v, achados) for m, v in zip(modelo, valor))
    return modelo == valor


def texto_da(protocolo, qual, saida):
    """O texto que a saida do gancho traz no lugar de {texto}, quando ela e a resposta qual
    ("nega", "contexto" ou "trava"); None quando ela e outra coisa ou o gancho nao disse
    nada. A saida e o texto que o gancho escreveu."""
    try:
        valor = json.loads(saida)
    except json.JSONDecodeError:
        return None
    achados = []
    return achados[0] if bate(protocolo["respostas"][qual], valor, achados) and len(set(achados)) == 1 else None
