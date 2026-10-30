"""
O protocolo dos ganchos de um programa: o que o programa que roda os ganchos manda a eles e
o que ele espera de volta. Tudo o que e de um programa vem de um arquivo de dados do
projeto, lido pelo molde em esquemas/protocolo.schema.json; no codigo fica so a forma que a
peca trata.

O arquivo diz:
  - o nome, no programa, de cada um dos dois eventos que os ganchos tratam: "antes" de uma
    chamada de ferramenta e "fim" de uma resposta;
  - a chave do evento que traz cada parte dele: o nome do evento, a sessao, a ferramenta
    chamada, a entrada dela, a pasta de onde ela roda e o aviso de que o fim da resposta ja
    foi travado uma vez ("fim_repetido");
  - cada resposta que um gancho da, um modelo em JSON em que {texto}, em qualquer texto de
    dentro dele, vira o texto do gancho: "nega" barra a chamada, com o motivo; "contexto"
    entrega um texto antes da chamada; "trava" nao deixa a resposta acabar, com o motivo;
  - as ferramentas do programa que os ganchos olham, cada uma com os campos da entrada
    dela: a de terminal e o campo do comando; as de busca e o campo do padrao; os campos do
    caminho do arquivo escrito, as ferramentas que trocam um trecho (o campo do trecho de
    antes, o do de depois e o que pede todas as vezes) e as que gravam o arquivo inteiro (o
    campo do texto); as de leitura, com o campo do caminho, o da linha em que a leitura
    comeca, o de quantas linhas ela le, quantas ela le sem esse campo e o numero que o
    programa da a primeira linha; e as que leem por outro modelo e entregam um resumo.

Da tambem o arquivo em que um gancho anota o que guarda de uma sessao, ou de cada chave dela,
como um documento, dentro da pasta da sessao: cada nome e a impressao digital do id da
sessao ou da chave, e por isso nunca sai da pasta das anotacoes.

Nao se roda: os ganchos o importam. Precisa do extrator_comum.py, do extrator, duas pastas
acima (na prateleira, em ganchos/protocolo/) ou na pasta irma (numa copia de teste). So
biblioteca padrao.
"""
import hashlib
import json
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent.parent / "extrator", PASTA.parent / "extrator"):  # a ultima posta e a primeira lida
    sys.path.insert(0, str(pasta))
from extrator_comum import ErroDeDados, le_conferido, preenche  # noqa: E402

MOLDE = PASTA / "esquemas" / "protocolo.schema.json"
EVENTOS = ("antes", "fim")  # os eventos que os ganchos tratam, pelo nome no molde
PARTES = ("sessao", "ferramenta", "entrada", "pasta", "fim_repetido")  # as partes do evento, alem do nome dele
RESPOSTAS = ("nega", "contexto", "trava")  # as respostas, pelo nome no molde
TEXTO = "texto"  # o campo do modelo de resposta que recebe o texto do gancho, escrito {texto}


def sem_repetir(itens, onde):
    """Os itens, quando nenhum se repete; erro que diz onde e quais, senao."""
    repetidos = sorted({x for x in itens if itens.count(x) > 1})
    if repetidos:
        raise ErroDeDados(f"{onde}: repetido(s): {repetidos}")
    return itens


def textos_de(valor):
    """Cada texto de dentro de um valor JSON, nos objetos e nas listas."""
    if isinstance(valor, str):
        yield valor
    elif isinstance(valor, dict):
        for v in valor.values():
            yield from textos_de(v)
    elif isinstance(valor, list):
        for v in valor:
            yield from textos_de(v)


def modelo(dados, qual):
    """O modelo de uma resposta, que o molde ja conferiu ser um objeto: erro quando um texto
    de dentro dele tem outro campo que nao {texto}, ou quando nenhum tem o {texto}."""
    valor, tem_o_texto = dados["respostas"][qual], False
    for escrito in textos_de(valor):
        try:
            trocado = preenche(escrito, **{TEXTO: ""})
        except ErroDeDados as e:
            raise ErroDeDados(f"respostas/{qual}: {e}") from None
        tem_o_texto = tem_o_texto or trocado != escrito
    if not tem_o_texto:
        raise ErroDeDados(f"respostas/{qual}: não tem o lugar do texto, {{{TEXTO}}}")
    return valor


def ler(caminho):
    """O protocolo do arquivo, lido pelo molde, que confere a versao, cada campo e o tipo e o
    tamanho dele: os eventos pelo nome no programa, as chaves, os modelos das respostas e as
    ferramentas. Erro (ErroDeDados) tambem no que o molde nao ve: os dois eventos com o mesmo
    nome, duas partes com a mesma chave, a ferramenta de busca ou de leitura repetida e o
    modelo sem o lugar do texto ou com outro campo."""
    dados = le_conferido(Path(caminho), MOLDE)
    eventos, chaves, buscas, leituras = dados["eventos"], dados["chaves"], dados["buscas"], dados["leituras"]
    sem_repetir([eventos[e] for e in EVENTOS], "os nomes dos eventos")
    sem_repetir([chaves[p] for p in ("evento",) + PARTES], "as chaves do evento")
    sem_repetir([b["nome"] for b in buscas], "as ferramentas de busca")
    sem_repetir([lida["nome"] for lida in leituras], "as ferramentas de leitura")
    return {
        "eventos": {n: e for e, n in eventos.items()},
        "chaves": chaves,
        "respostas": {r: modelo(dados, r) for r in RESPOSTAS},
        "terminal": dados["terminal"],
        "buscas": {b["nome"]: b["campo_padrao"] for b in buscas},
        "escritas": dados["escritas"],
        "leituras": {lida["nome"]: {c: v for c, v in lida.items() if c != "nome"} for lida in leituras},
        "resumos": dados["resumos"],
    }


def le_evento(protocolo, entrada):
    """{parte: valor} do evento que chega em texto JSON: "evento", que e "antes" ou "fim", e
    cada parte que o evento traz, pela chave dela no protocolo. Erro (ErroDeDados) quando o
    texto nao e um objeto JSON e quando o nome do evento falta ou e de outro evento."""
    try:
        dados = json.loads(entrada)
    except json.JSONDecodeError as e:
        raise ErroDeDados(f"o evento não se lê como JSON ({e})") from None
    if not isinstance(dados, dict):
        raise ErroDeDados(f"o evento não é um objeto: {dados!r}")
    chaves = protocolo["chaves"]
    evento = dados.get(chaves["evento"])
    if not isinstance(evento, str) or evento not in protocolo["eventos"]:
        raise ErroDeDados(f"evento desconhecido: {evento!r}")
    return {"evento": protocolo["eventos"][evento], **{p: dados[chaves[p]] for p in PARTES if chaves[p] in dados}}


def preenchido(valor, escrito):
    """Uma copia do valor JSON com {texto} trocado pelo texto escrito em cada texto de dentro
    dele."""
    if isinstance(valor, str):
        return preenche(valor, **{TEXTO: escrito})
    if isinstance(valor, dict):
        return {k: preenchido(v, escrito) for k, v in valor.items()}
    if isinstance(valor, list):
        return [preenchido(v, escrito) for v in valor]
    return valor


def resposta(protocolo, qual, escrito):
    """A resposta "nega", "contexto" ou "trava", com o texto do gancho no lugar de {texto}."""
    return preenchido(protocolo["respostas"][qual], escrito)


def anotacao(pasta, sessao, *chaves):
    """O arquivo, na pasta, em que um gancho anota o que guarda da sessao; com chaves, como o
    caminho de um documento, o de cada chave, dentro da pasta da sessao, uma pasta dentro da
    outra na ordem das chaves. Cada nome e a impressao digital do id da sessao ou da chave, e
    por isso nunca sai da pasta; a sessao sem id e a chave que nao e texto sao erro
    (ErroDeDados)."""
    if not isinstance(sessao, str) or not sessao:
        raise ErroDeDados(f"sessão sem id: {sessao!r}")
    for chave in chaves:
        if not isinstance(chave, str):
            raise ErroDeDados(f"chave de anotação que não é texto: {chave!r}")
    return Path(pasta).joinpath(*(hashlib.sha256(nome.encode("utf-8")).hexdigest() for nome in (sessao, *chaves)))
