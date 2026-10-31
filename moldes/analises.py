"""
Le as analises por aula escritas numa forma declarada num arquivo de dados: a forma das
analises, com o molde em esquemas/forma-analise.schema.json. A forma chega ja lida pelo molde
dela; a leitura das analises confere so o que o molde nao ve.

A forma diz o padrao dos nomes dos arquivos e o que vem antes da chave da aula no nome; o
comeco de uma linha de titulo, que fecha o slide, e o de uma linha que abre um slide, com o
numero dele; a marca de cada item; o separador entre o texto do trecho e os campos, e o que
separa um campo do seguinte; o valor que quer dizer "nenhum" num campo em lista; o comeco
de um item sem campos, que e uma nota e nao um trecho; e os campos, em ordem, cada um com a
forma do valor e, se tiver, o papel. Nada da materia fica no codigo: tipos, grupos e
caminhos sao os que os arquivos trazem.

Formas de campo: "lista" (os itens entre os separadores dados; o que esta entre parenteses
nao conta), "pedacos" (os pedacos entre os separadores dados que ficam fora dos
parenteses, cada um inteiro, com o que esta entre parenteses; parentese que nao fecha, ou
que fecha sem abrir, e erro), "presenca" (quais dos valores dados aparecem no campo, na
ordem deles) e "texto" (o campo inteiro). Nas formas em lista, o valor vazio fica fora e
nada se repete. Papeis: "tipo", "grupo" e "caminho" dizem onde o trecho cai e pedem um
valor em lista; "destino" e o texto que diz para onde ele vai. Cada papel fica em um campo
so.

Cada trecho sai com o texto dele, o texto e o valor de cada campo e de cada papel, e um id
estavel, "aula/slide/posicao/hash": a posicao conta os trechos do slide, a partir de 1, e o
hash sao os primeiros digitos do SHA-1 do texto do trecho em NFC. Se o texto mudar, o id
muda, e a mudanca aparece em toda decisao guardada pelo id. O id se monta por id_do_trecho,
e um id, ou o comeco dele (a aula; a aula e o slide; a aula, o slide e a posicao), se le por
le_codigo, que le o que id_do_trecho escreve.

O nome de campo repetido e o id repetido sao achados pelo extrator_comum.py, e a NFC vem do
texto_comum.py, os dois do extrator, na pasta irma "extrator" ou na mesma pasta.
"""
import collections
import hashlib
import re
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "extrator", PASTA):  # na prateleira, o extrator fica na pasta irma
    sys.path.insert(0, str(pasta))
from extrator_comum import repetidos  # noqa: E402
from texto_comum import nfc  # noqa: E402

PAPEIS = ("tipo", "grupo", "caminho", "destino")  # o que um campo pode fazer, como o molde da forma declara
PAPEIS_EM_LISTA = ("tipo", "grupo", "caminho")  # os papeis que pedem um valor em lista
ABRE, FECHA = "(", ")"  # o que abre e o que fecha o texto entre parenteses, que as formas em lista tratam a parte
ENTRE_PARENTESES = re.compile(rf"\s*{re.escape(ABRE)}[^{re.escape(ABRE + FECHA)}]*{re.escape(FECHA)}")
SEPARADOR_DO_ID = "/"  # o que separa a aula, o slide, a posicao e o hash no id de um trecho
DIGITOS_DO_HASH = 4  # quantos digitos do SHA-1 do texto do trecho o id leva
NUMERO_DO_ID = re.compile(r"[1-9][0-9]*")  # o slide e a posicao, como o id os escreve: inteiros de 1 para cima
HASH_DO_ID = re.compile(f"[0-9a-f]{{{DIGITOS_DO_HASH}}}")  # o hash, como o id o escreve: digitos hexadecimais
Codigo = collections.namedtuple("Codigo", "aula slide posicao hash")
# o id de um trecho, ou o comeco dele, em partes, como le_codigo o le, com None no que ele nao tem


class ErroDeForma(ValueError):
    """Forma, arquivo ou linha fora do que a forma declara; a mensagem diz o que e onde."""


def id_do_trecho(aula, slide, posicao, texto):
    """O id de um trecho: a aula, o slide, a posicao e o hash do texto em NFC, separados por SEPARADOR_DO_ID."""
    resumo = hashlib.sha1(nfc(texto).encode("utf-8")).hexdigest()[:DIGITOS_DO_HASH]
    return SEPARADOR_DO_ID.join([aula, str(slide), str(posicao), resumo])


def le_codigo(texto):
    """O Codigo do id de um trecho, ou do comeco dele -- a aula; a aula e o slide; a aula, o slide e a posicao --, com
    cada parte como id_do_trecho a escreve; None quando o texto nao e um id nem o comeco de um."""
    aula, *resto = texto.split(SEPARADOR_DO_ID)
    numeros, resumo = resto[:2], resto[2:]
    if not aula or any(c.isspace() for c in aula) or len(resto) >= len(Codigo._fields):
        return None
    if not all(NUMERO_DO_ID.fullmatch(n) for n in numeros) or not all(HASH_DO_ID.fullmatch(r) for r in resumo):
        return None
    slide, posicao = (list(map(int, numeros)) + [None, None])[:2]
    return Codigo(aula, slide, posicao, resumo[0] if resumo else None)


def unicos(itens):
    """Os itens sem repetir, na ordem em que vem."""
    return list(dict.fromkeys(itens))


def sem_parenteses(texto):
    anterior = None
    while anterior != texto:
        anterior, texto = texto, ENTRE_PARENTESES.sub("", texto)
    return texto


def ordem_natural(chave):
    """A chave em pedacos de texto e numero, para 2 vir antes de 10."""
    return [int(p) if p.isdecimal() else p for p in re.split(r"(\d+)", chave)]


def chave_natural(texto):
    """A chave para por textos na ordem natural (ordem_natural), com o proprio texto para desempatar."""
    return ordem_natural(texto), texto


def mais_longos_primeiro(separadores):
    """Os separadores, do mais longo ao mais curto, para que um separador que comeca por
    outro seja achado inteiro."""
    return sorted(separadores, key=len, reverse=True)


def sem_vazio(partes, vazio):
    """As partes sem os espacos das pontas, sem a parte em branco, sem o valor vazio e sem
    repetir, na ordem em que vem."""
    itens = []
    for parte in partes:
        parte = parte.strip()
        if parte and parte != vazio and parte not in itens:
            itens.append(parte)
    return itens


def em_lista(bruto, campo, vazio):
    """Os itens entre os separadores do campo, sem o que esta entre parenteses, sem o valor
    vazio e sem repetir, na ordem do texto."""
    padrao = "|".join(re.escape(s) for s in mais_longos_primeiro(campo["separadores"]))
    return sem_vazio(re.split(padrao, sem_parenteses(bruto)), vazio)


def em_pedacos(bruto, campo, vazio):
    """Os pedacos entre os separadores do campo que ficam fora dos parenteses, cada um
    inteiro, com o que esta entre parenteses; sem o valor vazio e sem repetir, na ordem do
    texto. ErroDeForma, que diz o campo, quando um parentese fecha sem abrir ou nao fecha."""
    separadores = mais_longos_primeiro(campo["separadores"])
    pedacos, inicio, nivel, i = [], 0, 0, 0
    while i < len(bruto):
        separador = next((s for s in separadores if bruto.startswith(s, i)), None) if nivel == 0 else None
        if separador is not None:
            pedacos.append(bruto[inicio:i])
            i = inicio = i + len(separador)
            continue
        nivel += (bruto[i] == ABRE) - (bruto[i] == FECHA)
        if nivel < 0:
            raise ErroDeForma(f"campo {campo['nome']!r}: parêntese que fecha sem abrir")
        i += 1
    if nivel:
        raise ErroDeForma(f"campo {campo['nome']!r}: parêntese que não fecha")
    return sem_vazio(pedacos + [bruto[inicio:]], vazio)


def presentes(bruto, campo, vazio):
    """Os valores do campo que aparecem no texto, na ordem da forma."""
    return [v for v in campo["valores"] if v in bruto]


def inteiro(bruto, campo, vazio):
    return bruto.strip()


FORMAS = {  # cada forma de campo, como o molde da forma declara: se o valor e uma lista e como se le
    "lista": {"em_lista": True, "le": em_lista},
    "pedacos": {"em_lista": True, "le": em_pedacos},
    "presenca": {"em_lista": True, "le": presentes},
    "texto": {"em_lista": False, "le": inteiro},
}


def erros_da_forma(forma):
    """Os problemas da forma, ja conferida pelo molde dela, que a leitura nao pode deixar
    passar e o molde nao ve, cada um numa frase: nome de campo repetido; papel em mais de um
    campo, em nenhum, ou num campo cujo valor nao e lista quando o papel pede lista."""
    campos = forma["campos"]
    erros = [f"o campo {n!r} aparece mais de uma vez" for n in repetidos([c["nome"] for c in campos])]
    donos = {p: [] for p in PAPEIS}
    for c in campos:
        papel = c.get("papel")
        if papel is not None:
            donos[papel].append(c["nome"])
        if papel in PAPEIS_EM_LISTA and not FORMAS[c["forma"]]["em_lista"]:
            erros.append(f"campo {c['nome']!r}: o papel {papel!r} pede um valor em lista, "
                         f"e a forma {c['forma']!r} não dá lista")
    for papel, donos_do_papel in donos.items():
        if not donos_do_papel:
            erros.append(f"nenhum campo tem o papel {papel!r}")
        elif len(donos_do_papel) > 1:
            erros.append(f"o papel {papel!r} está em mais de um campo: {', '.join(donos_do_papel)}")
    return erros


def separar_campos(resto, forma, onde):
    """{nome: texto} dos campos de um trecho, de 'resto' (o que vem depois do separador do
    texto): o primeiro campo comeca pelo nome e ': ', e cada um dos outros pelo separador de
    campos, o nome e ': '."""
    nomes = [c["nome"] for c in forma["campos"]]
    aberturas = [f"{nomes[0]}: "] + [f"{forma['separador_campos']}{n}: " for n in nomes[1:]]
    posicoes, inicio = [0], len(aberturas[0])
    for nome, abertura in zip(nomes[1:], aberturas[1:]):
        pos = resto.find(abertura, inicio)
        if pos < 0:
            raise ErroDeForma(f"{onde}: sem o campo {nome!r}")
        posicoes.append(pos)
        inicio = pos + len(abertura)
    brutos = {}
    for i, nome in enumerate(nomes):
        fim = posicoes[i + 1] if i + 1 < len(nomes) else len(resto)
        brutos[nome] = resto[posicoes[i] + len(aberturas[i]):fim]
    return brutos


def chave_da_aula(caminho, forma):
    nome = nfc(Path(caminho).stem)
    if not nome.startswith(forma["prefixo_arquivo"]):
        raise ErroDeForma(f"{caminho}: nome fora do padrão")
    return nome[len(forma["prefixo_arquivo"]):]


def ler_analise(caminho, forma):
    """(trechos, notas) de um arquivo, numa forma ja conferida. Cada trecho: id, aula, slide,
    posicao, texto, brutos (o texto de cada campo), valores (o valor de cada campo, pela forma
    dele) e papeis ({papel: {"valor", "texto"}}, os do campo que tem o papel)."""
    aula = chave_da_aula(caminho, forma)
    campos = forma["campos"]
    campo_do_papel = {c["papel"]: c["nome"] for c in campos if "papel" in c}
    abre_campos = forma["separador_texto"] + campos[0]["nome"] + ": "
    trechos, notas, slide, posicao = [], 0, None, 0
    for n, linha in enumerate(Path(caminho).read_text(encoding="utf-8").splitlines(), 1):
        onde = f"{Path(caminho).name}:{n}"
        if linha.startswith(forma["prefixo_slide"]):
            numero = linha[len(forma["prefixo_slide"]):].strip()
            if not numero.isdecimal():
                raise ErroDeForma(f"{onde}: slide sem número")
            slide, posicao = int(numero), 0
            continue
        if linha.startswith(forma["prefixo_titulo"]):
            slide = None
            continue
        if slide is None or not linha.strip():
            continue
        if not linha.startswith(forma["marca_item"]):
            raise ErroDeForma(f"{onde}: linha fora da forma")
        corpo = linha[len(forma["marca_item"]):]
        pos = corpo.find(abre_campos)
        if pos < 0:
            if corpo.startswith(forma["nota_sem_campos"]):
                notas += 1
                continue
            raise ErroDeForma(f"{onde}: item sem os campos")
        texto = corpo[:pos].strip()
        brutos = separar_campos(corpo[pos + len(forma["separador_texto"]):], forma, onde)
        try:
            valores = {c["nome"]: FORMAS[c["forma"]]["le"](brutos[c["nome"]], c, forma["vazio"]) for c in campos}
        except ErroDeForma as e:
            raise ErroDeForma(f"{onde}: {e}") from None
        posicao += 1
        papeis = {p: {"valor": valores[c], "texto": brutos[c]} for p, c in campo_do_papel.items()}
        trechos.append({"id": id_do_trecho(aula, slide, posicao, texto), "aula": aula, "slide": slide,
                        "posicao": posicao, "texto": texto, "brutos": brutos, "valores": valores,
                        "papeis": papeis})
    return trechos, notas


def ler_analises(pasta, forma):
    """(trechos, notas por aula, aulas em ordem natural) dos arquivos da pasta que seguem o
    padrao da forma, ja conferida pelo molde dela. ErroDeForma quando a forma tem problema
    que o molde nao ve (todos numa mensagem), quando nenhum arquivo segue o padrao, quando
    dois arquivos dao a mesma aula, numa linha fora da forma e quando um id se repete."""
    erros = erros_da_forma(forma)
    if erros:
        raise ErroDeForma("a forma das análises: " + "; ".join(erros))
    arquivos = {}
    for arquivo in sorted(c for c in Path(pasta).glob(forma["arquivos"]) if c.is_file()):
        aula = chave_da_aula(arquivo, forma)
        if aula in arquivos:
            raise ErroDeForma(f"{pasta}: a aula {aula!r} está em dois arquivos, {arquivos[aula].name} e {arquivo.name}")
        arquivos[aula] = arquivo
    if not arquivos:
        raise ErroDeForma(f"{pasta}: nenhum arquivo {forma['arquivos']}")
    aulas = sorted(arquivos, key=chave_natural)
    trechos, notas = [], {}
    for aula in aulas:
        lidos, notas[aula] = ler_analise(arquivos[aula], forma)
        trechos += lidos
    mesmos = repetidos([t["id"] for t in trechos])
    if mesmos:
        raise ErroDeForma(f"ids repetidos: {mesmos}")
    return trechos, notas, aulas
