"""
Lista os itens numerados de transcricoes de documentos (uma norma, um manual) e confere a
numeracao deles. Para cada documento:
  - acha cada item no corpo, pelas formas de linha dadas, com o numero, o titulo, a pagina
    e a linha;
  - confere a sequencia: cada numero vem logo depois do anterior (o proximo do mesmo nivel,
    o primeiro filho ou o proximo de um nivel acima); o que salta, repete ou sai de ordem e
    problema;
  - confere o sumario: cada entrada numerada do sumario tem o item no corpo, com o titulo
    comecando pelo titulo da entrada;
  - divide as entradas do sumario em grupos de um tamanho dado, cada grupo com os itens que
    ficam debaixo das entradas dele e as paginas do arquivo que eles ocupam.

Tres entradas: a configuracao do extrator, lida como o extrator a le, contra o molde dela
(dela se usa o padrao: o modelo do titulo de
pagina, para dividir a transcricao em paginas, e as marcas de destaque e o escape, que se
tiram da linha antes de reconhecer um item), a configuracao dos itens (as formas de linha,
o tamanho do grupo e, para cada documento, a transcricao e as faixas de paginas do sumario
e do corpo; campo que o molde dela nao conhece e erro) e o arquivo de saida, um JSON com
os itens, os problemas e os grupos de cada documento. Os caminhos da configuracao dos
itens partem de --raiz (padrao: a pasta atual).

Uma forma de item e uma expressao regular com os grupos "numero" e, se houver, "titulo";
o numero e uma sequencia de partes separadas pelo "separador" das formas, cada parte um
numero ou uma letra (A = 1). Cada forma tem a sua "serie" (por exemplo, as secoes e os anexos): a sequencia se
confere dentro de cada serie. Opcoes da forma: "linhas_do_titulo", quantas linhas
seguintes, nao vazias, fazem o titulo quando a linha nao o traz; "so_se_no_sumario", para
aceitar o item so quando o sumario tem a entrada com o mesmo numero e a linha comeca pelo
titulo dela (assim uma nota de rodape numerada nao passa por item).

Uso:
    python3 -I itens.py <configuracao do extrator.json> <itens.json> <saida.json>
Sai com codigo 1 se houver problema em algum documento; a saida e gravada assim mesmo,
com os problemas.
"""

import argparse
import json
import re
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "extrator", PASTA):  # na prateleira, o extrator fica na pasta irma
    sys.path.insert(0, str(pasta))
from extrator_comum import (ErroDeDados, confere_padrao, le_conferido, le_configuracao,  # noqa: E402
                            paginas_da_transcricao, paginas_das_faixas, texto_simples)

MOLDE = PASTA / "esquemas" / "itens-numerados.schema.json"  # o molde da configuracao dos itens

DIGITOS = re.compile(r"^\d+$")
LETRA = re.compile(r"^[A-Za-z]$")


def partes(numero, separador):
    """Com o separador ".": "7.13.1" -> (7, 13, 1); "A" -> (1,); "B.2" -> (2, 2)."""
    out = []
    for p in numero.split(separador):
        if DIGITOS.match(p):
            out.append(int(p))
        elif LETRA.match(p):
            out.append(ord(p.upper()) - ord("A") + 1)
        else:
            raise ValueError(f"parte de número que não é número nem letra: {p!r} em {numero!r}")
    return tuple(out)


def seguintes(anterior):
    """Os numeros que podem vir logo depois do anterior."""
    if anterior is None:
        return {(1,)}
    out = {anterior + (1,)}
    for k in range(len(anterior)):
        out.add(anterior[:k] + (anterior[k] + 1,))
    return out


def normal(texto):
    return " ".join(texto.split()).casefold()


def compila(formas):
    try:
        return [dict(f, rx=re.compile(f["expressao"])) for f in formas]
    except re.error as e:
        raise ErroDeDados(f"expressão de forma que não compila: {e}")


def linhas_das_faixas(paginas, faixas, padrao):
    """[(pagina do arquivo, numero da linha, texto da linha sem as marcas)] das paginas que as
    faixas cobrem."""
    total = max((n for _, n, _ in paginas), default=0)
    dentro = set(paginas_das_faixas(faixas, total))
    return [(n, i, texto_simples(l, padrao)) for _, n, ls in paginas if n in dentro for i, l in ls]


def entradas_do_sumario(linhas, formas, junta):
    """[(serie, numero, titulo, linha)] do sumario: a linha que e so um numero se junta com
    a seguinte nao vazia, e cada linha que casa com uma forma de entrada vira entrada."""
    textos, i = [], 0
    while i < len(linhas):
        n, num, l = linhas[i]
        if junta and junta.match(l.strip()):
            j = next((k for k in range(i + 1, len(linhas)) if linhas[k][2].strip()), None)
            if j is not None:
                textos.append((num, f"{l.strip()} {linhas[j][2].strip()}"))
                i = j + 1
                continue
        textos.append((num, l.strip()))
        i += 1
    out = []
    for num, texto in textos:
        for f in formas:
            m = f["rx"].match(texto)
            if m:
                out.append((f["serie"], m.group("numero"), (m.groupdict().get("titulo") or "").strip(), num))
                break
    return out


def titulo_seguinte(linhas, i, quantas):
    seguintes_ = [l.strip() for _, _, l in linhas[i + 1:] if l.strip()][:quantas]
    return " ".join(seguintes_)


def itens_do_corpo(linhas, formas, sumario):
    """[{serie, numero, titulo, pagina_arquivo, linha}] do corpo, na ordem."""
    no_sumario = {(s, n): t for s, n, t, _ in sumario}
    out = []
    for i, (pagina, num, linha) in enumerate(linhas):
        texto = linha.strip()
        for f in formas:
            m = f["rx"].match(texto)
            if not m:
                continue
            titulo = (m.groupdict().get("titulo") or "").strip()
            if not titulo and f.get("linhas_do_titulo"):
                titulo = titulo_seguinte(linhas, i, f["linhas_do_titulo"])
            if f.get("so_se_no_sumario"):
                esperado = no_sumario.get((f["serie"], m.group("numero")))
                if esperado is None or not normal(titulo).startswith(normal(esperado)):
                    continue
            out.append({"serie": f["serie"], "numero": m.group("numero"), "titulo": titulo,
                        "pagina_arquivo": pagina, "linha": num})
            break
    return out


def problemas_da_sequencia(itens, separador):
    problemas, ultimo, vistos = [], {}, set()
    for item in itens:
        chave, p = item["serie"], partes(item["numero"], separador)
        if (chave, p) in vistos:
            problemas.append({"tipo": "repetido", "numero": item["numero"], "linha": item["linha"],
                              "detalhe": f"o número {item['numero']} já apareceu antes"})
        elif p not in seguintes(ultimo.get(chave)):
            antes = separador.join(map(str, ultimo[chave])) if chave in ultimo else "nenhum"
            problemas.append({"tipo": "fora_de_sequencia", "numero": item["numero"], "linha": item["linha"],
                              "detalhe": f"depois de {antes} ({chave})"})
        else:
            ultimo[chave] = p
            vistos.add((chave, p))
    return problemas


def problemas_do_sumario(sumario, itens):
    out, no_corpo = [], {}
    for item in itens:
        no_corpo.setdefault((item["serie"], item["numero"]), item)
    for serie, numero, titulo, linha in sumario:
        item = no_corpo.get((serie, numero))
        if item is None:
            out.append({"tipo": "sumario_sem_item", "numero": numero, "linha": linha,
                        "detalhe": f"a entrada {numero} {titulo!r} do sumário não tem item no corpo"})
        elif not normal(item["titulo"]).startswith(normal(titulo)):
            out.append({"tipo": "titulo_diferente", "numero": numero, "linha": item["linha"],
                        "detalhe": f"no sumário: {titulo!r}; no corpo: {item['titulo']!r}"})
    return out


def grupos(sumario, itens, tamanho):
    """Os grupos de entradas do sumario, cada um com os itens do corpo que ficam desde a
    primeira entrada dele ate antes da primeira do grupo seguinte."""
    if tamanho < 1:
        raise ErroDeDados(f"o tamanho do grupo tem de ser 1 ou mais, e {tamanho}")
    if not itens:
        return []
    posicao = {}
    for k, i in enumerate(itens):
        posicao.setdefault((i["serie"], i["numero"]), k)  # a primeira vez que o numero aparece
    inicios = [posicao[(s, n)] for s, n, _, _ in sumario if (s, n) in posicao]
    cortes = sorted(set(inicios))[::tamanho]
    cortes = [0] + cortes[1:] if cortes else [0]  # o que vem antes da primeira entrada fica no primeiro grupo
    out = []
    for k, ini in enumerate(cortes):
        fim = cortes[k + 1] if k + 1 < len(cortes) else len(itens)
        dele = itens[ini:fim]
        out.append({"id": str(k + 1), "itens": [i["numero"] for i in dele],
                    "paginas_arquivo": [dele[0]["pagina_arquivo"], dele[-1]["pagina_arquivo"]]})
    return out


def documento(doc, config, padrao, raiz):
    caminho = raiz / doc["transcricao"]
    try:
        texto = caminho.read_text(encoding="utf-8")
    except OSError as e:
        raise ErroDeDados(f"{doc['transcricao']}: não se lê ({e})")
    paginas = paginas_da_transcricao(texto, padrao["titulo_pagina"])
    formas = {k: compila(v) for k, v in config["formas"].items() if k in ("item", "sumario")}
    junta = re.compile(config["formas"]["numero_sozinho"]) if config["formas"].get("numero_sozinho") else None
    sumario = entradas_do_sumario(linhas_das_faixas(paginas, doc["sumario"], padrao), formas["sumario"], junta)
    itens = itens_do_corpo(linhas_das_faixas(paginas, doc["corpo"], padrao), formas["item"], sumario)
    problemas = problemas_da_sequencia(itens, config["formas"]["separador"]) + problemas_do_sumario(sumario, itens)
    return {"transcricao": doc["transcricao"], "itens": itens, "problemas": problemas,
            "grupos": grupos(sumario, itens, config["grupo"])}


def main(argv=None):
    p = argparse.ArgumentParser(description="Lista e confere os itens numerados de transcrições.")
    p.add_argument("extrator", type=Path, help="a configuração do extrator (o modelo do título de página)")
    p.add_argument("itens", type=Path, help="a configuração dos itens")
    p.add_argument("saida", type=Path)
    p.add_argument("--raiz", type=Path, default=Path("."), help="de onde partem os caminhos das transcrições")
    a = p.parse_args(argv)
    try:
        padrao = le_configuracao(a.extrator)["padrao"]
        confere_padrao(padrao)
        config = le_conferido(a.itens, MOLDE)
        saida = [documento(d, config, padrao, a.raiz) for d in config["documentos"]]
    except (ErroDeDados, KeyError, ValueError, TypeError) as e:
        detalhe = f"falta a informação {e}" if isinstance(e, KeyError) else str(e)
        print(f"ERRO: {detalhe}")
        print("Nada foi gravado.")
        return 1
    a.saida.parent.mkdir(parents=True, exist_ok=True)
    a.saida.write_text(json.dumps({"versao_schema": 1, "documentos": saida}, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
    for d in saida:
        print(f"{d['transcricao']}: {len(d['itens'])} item(ns), {len(d['grupos'])} grupo(s), "
              f"{len(d['problemas'])} problema(s)")
        for prob in d["problemas"]:
            print(f"CONFERIR: linha {prob['linha']}: {prob['tipo']}: {prob['detalhe']}")
    print(f"saída: {a.saida}")
    return 1 if any(d["problemas"] for d in saida) else 0


if __name__ == "__main__":
    sys.exit(main())
