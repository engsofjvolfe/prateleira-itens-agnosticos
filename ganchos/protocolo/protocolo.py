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

Nao se roda: os ganchos o importam. Precisa do extrator_comum.py, do extrator, duas pastas
acima (na prateleira, em ganchos/protocolo/) ou na pasta irma (numa copia de teste). So
biblioteca padrao.
"""
import json
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent.parent / "extrator", PASTA.parent / "extrator"):  # a ultima posta e a primeira lida
    sys.path.insert(0, str(pasta))
from extrator_comum import ErroDeDados, campo, le_conferido, preenche  # noqa: E402

MOLDE = PASTA / "esquemas" / "protocolo.schema.json"
VERSAO = json.loads(MOLDE.read_text(encoding="utf-8"))["properties"]["versao_schema"]["const"]  # a do molde
EVENTOS = ("antes", "fim")  # os eventos que os ganchos tratam, pelo nome no molde
PARTES = ("sessao", "ferramenta", "entrada", "pasta", "fim_repetido")  # as partes do evento, alem do nome dele
RESPOSTAS = ("nega", "contexto", "trava")  # as respostas, pelo nome no molde
TEXTO = "texto"  # o campo do modelo de resposta que recebe o texto do gancho, escrito {texto}
CAMPOS_DA_TROCA = ("antes", "depois", "todas")
CAMPOS_DA_LEITURA = ("campo_caminho", "campo_comeco", "campo_quantas")
MINIMOS_DA_LEITURA = {"linhas_sem_limite": 1, "primeira_linha": 0}  # cada numero de uma leitura e o menor dele


def texto(valor):
    """O valor, quando ele e um texto que nao esta vazio."""
    if not isinstance(valor, str) or not valor:
        raise ErroDeDados(f"tem de ser um texto que não está vazio: {valor!r}")
    return valor


def no_caminho(caminho, ler, valor):
    """ler(valor), com o caminho do valor no erro."""
    try:
        return ler(valor)
    except ErroDeDados as e:
        raise ErroDeDados(f"{caminho}: {e}") from None


def nome(dados, caminho):
    """O texto do campo no caminho ("a/b"), que nao pode estar vazio."""
    return no_caminho(caminho, texto, campo(dados, caminho, str))


def lista(dados, caminho, ler):
    """[ler(item)] de cada item da lista do campo no caminho."""
    return [no_caminho(f"{caminho}/{k}", ler, v) for k, v in enumerate(campo(dados, caminho, list))]


def objeto(dados, caminho, ler):
    """{chave: ler(valor)} do objeto do campo no caminho."""
    return {c: no_caminho(f"{caminho}/{c}", ler, v) for c, v in campo(dados, caminho, dict).items()}


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
    """O modelo de uma resposta: um objeto em que so {texto} e campo, e que o tem pelo menos
    uma vez."""
    valor = campo(dados, f"respostas/{qual}", dict)
    tem_o_texto = False
    for escrito in textos_de(valor):
        trocado = no_caminho(f"respostas/{qual}", lambda t: preenche(t, **{TEXTO: ""}), escrito)
        tem_o_texto = tem_o_texto or trocado != escrito
    if not tem_o_texto:
        raise ErroDeDados(f"respostas/{qual}: não tem o lugar do texto, {{{TEXTO}}}")
    return valor


def leitura(item):
    """(nome, {campos e numeros}) de uma ferramenta de leitura."""
    dados = {c: nome(item, c) for c in CAMPOS_DA_LEITURA}
    for numero, minimo in MINIMOS_DA_LEITURA.items():
        dados[numero] = campo(item, numero, int)
        if dados[numero] < minimo:
            raise ErroDeDados(f"{numero} tem de ser {minimo} ou mais: {dados[numero]}")
    return nome(item, "nome"), dados


def ler(caminho):
    """O protocolo do arquivo, lido pelo molde e conferido campo por campo: os eventos pelo
    nome no programa, as chaves, os modelos das respostas e as ferramentas. Erro
    (ErroDeDados) quando a versao nao e a do molde, quando um campo falta, e de outro tipo
    ou esta vazio, quando os dois eventos tem o mesmo nome, quando duas partes tem a mesma
    chave, quando nao ha campo de caminho de escrita, quando uma ferramenta se repete numa
    lista e quando um modelo nao tem o lugar do texto ou tem outro campo."""
    dados = le_conferido(Path(caminho), MOLDE)
    if campo(dados, "versao_schema", int) != VERSAO:
        raise ErroDeDados(f"versao_schema: o molde é o da versão {VERSAO}")
    nomes_dos_eventos = {e: nome(dados, f"eventos/{e}") for e in EVENTOS}
    sem_repetir(list(nomes_dos_eventos.values()), "os nomes dos eventos")
    chaves = {p: nome(dados, f"chaves/{p}") for p in ("evento",) + PARTES}
    sem_repetir(list(chaves.values()), "as chaves do evento")
    buscas = lista(dados, "buscas", lambda item: (nome(item, "nome"), nome(item, "campo_padrao")))
    leituras = lista(dados, "leituras", leitura)
    sem_repetir([n for n, _ in buscas], "as ferramentas de busca")
    sem_repetir([n for n, _ in leituras], "as ferramentas de leitura")
    campos_caminho = lista(dados, "escritas/campos_caminho", texto)
    if not campos_caminho:
        raise ErroDeDados("escritas/campos_caminho: não tem nenhum campo")
    return {
        "eventos": {n: e for e, n in nomes_dos_eventos.items()},
        "chaves": chaves,
        "respostas": {r: modelo(dados, r) for r in RESPOSTAS},
        "terminal": {c: nome(dados, f"terminal/{c}") for c in ("ferramenta", "campo_comando")},
        "buscas": dict(buscas),
        "escritas": {
            "campos_caminho": campos_caminho,
            "trocas": objeto(dados, "escritas/trocas", lambda t: {c: nome(t, c) for c in CAMPOS_DA_TROCA}),
            "inteiros": objeto(dados, "escritas/inteiros", texto),
        },
        "leituras": dict(leituras),
        "resumos": sem_repetir(lista(dados, "resumos", texto), "as ferramentas que resumem"),
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
