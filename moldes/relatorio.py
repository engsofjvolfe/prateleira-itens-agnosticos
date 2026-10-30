"""Pedacos de relatorio em markdown, iguais em todos os scripts que contam ou conferem os
trechos das analises: a tabela, as ordenacoes e a tabela das classes dos trechos."""
from analises import ordem_natural

ROTULOS = {  # o rotulo de cada classe de trecho; {} e o nome da regra de fora ou da marca, ou o problema
    "estudo": "de estudo, com lugar nos documentos",
    "assunto": "de estudo, à espera do assunto",
    "unidade": "de estudo, à espera de unidade",
    "limite": "até a última aula, sem lugar depois do limite",
    "depois": "depois da última aula, sem lugar",
    "fora": "fora: {}",
    "lido": "fora pela leitura: {}",
    "marca": "marcados, à espera de lugar: {}",
    "problema": "problema: {}",
}
SO_COM_TRECHO = ("assunto", "unidade", "limite", "depois")  # as classes sem regra nem marca, que so saem com trecho


def celula(valor):
    """O texto de uma celula de tabela markdown: a barra vai escapada, para nao abrir outra
    coluna."""
    return str(valor).replace("|", "\\|")


def tabela(cabecalho, linhas, numericas=()):
    """Tabela markdown; as colunas cujos indices estao em 'numericas' alinham a direita."""
    alinhamento = ["---:" if i in numericas else "---" for i in range(len(cabecalho))]
    saida = ["| " + " | ".join(map(celula, cabecalho)) + " |", "| " + " | ".join(alinhamento) + " |"]
    saida += ["| " + " | ".join(map(celula, linha)) + " |" for linha in linhas]
    return saida


def por_quantidade(contagem):
    """Itens de um Counter, do maior para o menor; empate pela ordem natural da chave."""
    return sorted(contagem.items(), key=lambda kv: (-kv[1], ordem_natural(str(kv[0])), str(kv[0])))


def por_chave(contagem):
    return sorted(contagem.items(), key=lambda kv: (ordem_natural(str(kv[0])), str(kv[0])))


def tabela_das_classes(classes, regras):
    """A tabela de quantos trechos ha em cada classe, a ultima linha com o total. As classes
    sao as do lugares.py; ("lido", id de uma regra de fora), a do trecho que uma leitura pos
    fora; e as da aplicacao das unidades e do limite (limite.py): ("unidade",), o trecho de
    estudo que espera a unidade dele, ("limite",), o trecho de uma aula ate a ultima que
    perdeu o lugar no limite, e ("depois",), o de uma aula depois da ultima que ficou sem
    lugar. Saem sempre a de estudo com lugar, cada regra de fora e cada marca; as outras, so
    quando ha trecho nelas. Classe desconhecida e erro (ValueError)."""
    nomes = {(k, r["id"]): r["nome"] for k in ("fora", "lido") for r in regras["fora"]}
    nomes.update({("marca", m["id"]): m["nome"] for m in regras["marcas"]})
    possiveis = [(("estudo",), True)] + [((k,), False) for k in SO_COM_TRECHO]
    possiveis += [(("fora", r["id"]), True) for r in regras["fora"]]
    possiveis += [(("lido", r["id"]), False) for r in regras["fora"]]
    possiveis += [(("marca", m["id"]), True) for m in regras["marcas"]]
    possiveis += [(c, False) for c in sorted(c for c in classes if c[0] == "problema")]
    desconhecidas = sorted(set(classes) - {c for c, _ in possiveis})
    if desconhecidas:
        raise ValueError(f"classe(s) de trecho desconhecida(s): {desconhecidas}")
    linhas = [(ROTULOS[c[0]].format(nomes.get(c, c[-1])), classes.get(c, 0))
              for c, sempre in possiveis if sempre or classes.get(c)]
    return tabela(["Trechos", "Quantos"], linhas + [("total", sum(classes.values()))], numericas=(1,))
