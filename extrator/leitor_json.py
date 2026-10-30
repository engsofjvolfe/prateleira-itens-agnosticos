"""
Leitor de JSON: um documento cujo texto esta numa lista de partes (segmentos), como a
resposta de um servico que publica atos normativos. Cada parte tem o texto num campo, que
pode trazer marcacao HTML: esse texto passa pelo leitor de marcacao, com as opcoes padrao
dele. Um documento JSON nao tem paginas: sai uma pagina so.

Opcoes, todas obrigatorias:
  - "codificacao": a do arquivo;
  - "lista": o caminho ate a lista de partes, chave por chave (texto) ou posicao por
    posicao (numero, a partir de 0); lista vazia: o proprio documento e a lista;
  - "antes": os caminhos, do mesmo jeito, de textos que vem antes das partes, como o
    titulo do ato, quando ele nao esta nas partes; cada um tem de levar a um texto;
  - "campos": os campos que podem ter o texto de uma parte, na ordem de preferencia;
  - "leitor_do_texto": o nome do leitor que le o texto de cada parte.
Parte sem nenhum desses campos e erro, com os campos que ela tem: assim, nenhum texto fica
de fora sem aviso.
"""

import json
from pathlib import Path

OPCOES = ("codificacao", "lista", "antes", "campos", "leitor_do_texto")


def segue(dados, caminho):
    for passo in caminho:
        dados = dados[passo]
    return dados


def ler(arquivo, opcoes, contexto):
    dados = json.loads(Path(arquivo).read_text(encoding=opcoes["codificacao"]))
    lista = segue(dados, opcoes["lista"])
    if not isinstance(lista, list):
        raise ValueError(f"o caminho {opcoes['lista']} não leva a uma lista")
    modulo, opcoes_do_texto = contexto["leitor"](opcoes["leitor_do_texto"])
    blocos = []
    for caminho in opcoes["antes"]:
        texto = segue(dados, caminho)
        if not isinstance(texto, str):
            raise ValueError(f"o caminho {caminho} não leva a um texto")
        blocos += modulo.blocos_do_texto(texto, opcoes_do_texto)
    for i, parte in enumerate(lista):
        campo = next((c for c in opcoes["campos"] if isinstance(parte, dict) and isinstance(parte.get(c), str)), None)
        if campo is None:
            tem = sorted(parte) if isinstance(parte, dict) else type(parte).__name__
            raise ValueError(f"a parte {i} não tem nenhum dos campos {opcoes['campos']}; tem {tem}")
        blocos += modulo.blocos_do_texto(parte[campo], opcoes_do_texto)
    return {"paginado": False, "paginas": [{"arquivo": 1, "ocr": False, "blocos": blocos}]}
