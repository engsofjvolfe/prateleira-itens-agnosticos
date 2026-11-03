"""
Grava um pacote do Anki (.apkg) no esquema antigo da colecao, o 11, que o Anki ainda importa:
um zip com a colecao (um banco SQLite) e a lista das midias, sem nenhuma. O pacote tem um
baralho, um tipo de nota com um modelo de cartao e as notas, cada uma com um cartao novo, na
ordem dada. Os ids do baralho e do tipo de nota saem do hash do nome de cada um; o guid de
cada nota, do hash da chave dela; os ids das notas e dos cartoes e todas as datas do banco e
das entradas do zip, da data dada. Os mesmos dados dao sempre os mesmos bytes, e o Anki, ao
importar o pacote de novo, acha cada nota pelo guid e a atualiza em vez de duplica-la.

Nao se roda: o gera_apkg.py o importa. So biblioteca padrao.
"""
import hashlib
import html
import io
import json
import pathlib
import re
import sqlite3
import zipfile

VERSAO = 11  # o esquema da colecao
COLECAO = "collection.anki2"  # o banco, dentro do zip
MIDIAS = "media"  # a lista das midias, dentro do zip
SEM_MIDIAS = b"{}"  # a lista das midias quando nao ha nenhuma
SEPARADOR = chr(0x1F)  # entre os campos de uma nota
PADRAO = 1  # o id do baralho padrao e o das opcoes padrao de baralho, que toda colecao tem
NOME_PADRAO = "Default"  # o nome do baralho padrao e o das opcoes padrao
FAIXA = 1 << 30  # os ids do baralho e do tipo de nota ficam entre FAIXA e o dobro dela
BYTES_DO_ID = 4  # do hash do nome, para o id do baralho e o do tipo de nota
BYTES_DO_GUID = 8  # do hash da chave, para o guid da nota
BYTES_DA_SOMA = 4  # do sha1 do primeiro campo sem HTML, para a soma da nota
NOVO = 0  # o tipo e a fila de um cartao novo
NAO_SINCRONIZADO = -1  # o usn do que nunca foi sincronizado
CHEIO = "1"  # o valor de um campo preenchido, para achar os campos de que a frente precisa
ENTRADAS = {"compressao": zipfile.ZIP_DEFLATED, "sistema": 3, "permissoes": 0o644 << 16}  # 3: Unix
ETIQUETA_HTML = re.compile(r"<[^>]*>")
CAMPO_DO_MODELO = re.compile(r"\{\{([^{}]+?)\}\}")  # {{Nome}} ou {{filtro:Nome}}

ESQUEMA = """
CREATE TABLE col (id integer primary key, crt integer not null, mod integer not null, scm integer not null,
    ver integer not null, dty integer not null, usn integer not null, ls integer not null, conf text not null,
    models text not null, decks text not null, dconf text not null, tags text not null);
CREATE TABLE notes (id integer primary key, guid text not null, mid integer not null, mod integer not null,
    usn integer not null, tags text not null, flds text not null, sfld integer not null, csum integer not null,
    flags integer not null, data text not null);
CREATE TABLE cards (id integer primary key, nid integer not null, did integer not null, ord integer not null,
    mod integer not null, usn integer not null, type integer not null, queue integer not null,
    due integer not null, ivl integer not null, factor integer not null, reps integer not null,
    lapses integer not null, left integer not null, odue integer not null, odid integer not null,
    flags integer not null, data text not null);
CREATE TABLE revlog (id integer primary key, cid integer not null, usn integer not null, ivl integer not null,
    lastIvl integer not null, factor integer not null, time integer not null, type integer not null);
CREATE TABLE graves (usn integer not null, oid integer not null, type integer not null);
CREATE INDEX ix_notes_usn on notes (usn);
CREATE INDEX ix_cards_usn on cards (usn);
CREATE INDEX ix_revlog_usn on revlog (usn);
CREATE INDEX ix_cards_nid on cards (nid);
CREATE INDEX ix_cards_sched on cards (did, queue, due);
CREATE INDEX ix_revlog_cid on revlog (cid);
CREATE INDEX ix_notes_csum on notes (csum);
"""

OPCOES_PADRAO = {  # as opcoes padrao de baralho do Anki, que o baralho do pacote usa
    "id": PADRAO, "name": NOME_PADRAO, "mod": 0, "usn": 0, "dyn": False, "maxTaken": 60, "autoplay": True,
    "timer": 0, "replayq": True,
    "new": {"bury": True, "delays": [1, 10], "initialFactor": 2500, "ints": [1, 4, 7], "order": 1, "perDay": 20,
            "separate": True},
    "lapse": {"delays": [10], "leechAction": 0, "leechFails": 8, "minInt": 1, "mult": 0},
    "rev": {"bury": True, "ease4": 1.3, "fuzz": 0.05, "ivlFct": 1, "maxIvl": 36500, "minSpace": 1, "perDay": 100},
}


def hash_de(texto):
    return hashlib.sha256(texto.encode("utf-8")).digest()


def id_do_nome(nome):
    """O id do baralho ou do tipo de nota, do hash do nome, entre FAIXA e o dobro dela."""
    return FAIXA + int.from_bytes(hash_de(nome)[:BYTES_DO_ID], "big") % FAIXA


def guid(chave):
    """O guid da nota, do hash da chave dela."""
    return hash_de(chave)[:BYTES_DO_GUID].hex()


def sem_html(valor):
    """O texto do campo sem as etiquetas HTML e com as entidades trocadas pelos caracteres."""
    return html.unescape(ETIQUETA_HTML.sub("", valor))


def soma(texto):
    """A soma do primeiro campo, que o Anki usa para achar notas repetidas."""
    return int.from_bytes(hashlib.sha1(texto.encode("utf-8")).digest()[:BYTES_DA_SOMA], "big")


def requisitos(frente, campos):
    """Os campos de que a frente do cartao precisa, como o Anki os calcula no esquema antigo:
    [[0, "all", campos]] com os que, faltando, deixam a frente sem nenhum campo; senao,
    [[0, "any", campos]] com os que, sozinhos, a preenchem. Contam os campos simples do modelo,
    {{Nome}} e {{filtro:Nome}}."""
    def com(valores):
        return CAMPO_DO_MODELO.sub(lambda m: valores.get(m.group(1).split(":")[-1].strip(), ""), frente)
    vazia = com({})
    todos = [k for k, nome in enumerate(campos) if com({n: CHEIO for n in campos if n != nome}) == vazia]
    if todos:
        return [[0, "all", todos]]
    return [[0, "any", [k for k, nome in enumerate(campos) if com({nome: CHEIO}) != vazia]]]


def baralho(id_, nome, mod):
    """O baralho no esquema antigo, com as opcoes padrao."""
    return {"id": id_, "name": nome, "mod": mod, "usn": NAO_SINCRONIZADO, "conf": PADRAO, "desc": "", "dyn": 0,
            "collapsed": False, "browserCollapsed": False, "extendNew": 0, "extendRev": 0,
            "newToday": [0, 0], "revToday": [0, 0], "lrnToday": [0, 0], "timeToday": [0, 0]}


def tipo_de_nota(id_, tipo, id_do_baralho, mod):
    """O tipo de nota no esquema antigo: os campos, na ordem, com a letra do editor, e um modelo
    de cartao."""
    editor = tipo["editor"]
    campos = [{"name": nome, "ord": k, "sticky": False, "rtl": False, "font": editor["tipo_de_letra"],
               "size": editor["tamanho"], "media": []} for k, nome in enumerate(tipo["campos"])]
    modelo = {"name": tipo["cartao"], "ord": 0, "qfmt": tipo["frente"], "afmt": tipo["verso"], "bqfmt": "",
              "bafmt": "", "did": None, "bfont": "", "bsize": 0}
    return {"id": id_, "name": tipo["nome"], "type": 0, "mod": mod, "usn": NAO_SINCRONIZADO, "sortf": 0,
            "did": id_do_baralho, "tmpls": [modelo], "flds": campos, "css": tipo["estilo"], "latexPre": "",
            "latexPost": "", "latexsvg": False, "req": requisitos(tipo["frente"], tipo["campos"]), "tags": [],
            "vers": []}


def colecao(nome_do_baralho, tipo, notas, data):
    """Os bytes do banco da colecao. As notas sem o numero de campos do tipo, com etiqueta vazia
    ou com espaco, ou com a chave repetida sao erro (ValueError)."""
    segundos = int(data.timestamp())
    base = segundos * 1000  # os ids das notas e dos cartoes, como os do Anki, em milissegundos
    did, mid = id_do_nome(nome_do_baralho), id_do_nome(tipo["nome"])
    chaves = [chave for chave, _, _ in notas]
    if len(set(chaves)) != len(chaves):
        raise ValueError("nota com a chave repetida")
    banco = sqlite3.connect(":memory:")
    banco.executescript(ESQUEMA)
    configuracao = {"activeDecks": [did], "curDeck": did, "curModel": mid, "nextPos": len(notas) + 1,
                    "addToCur": True, "collapseTime": 1200, "dueCounts": True, "estTimes": True, "newBury": True,
                    "newSpread": 0, "sortBackwards": False, "sortType": "noteFld", "timeLim": 0}
    baralhos = {str(PADRAO): baralho(PADRAO, NOME_PADRAO, segundos), str(did): baralho(did, nome_do_baralho, segundos)}
    banco.execute("INSERT INTO col VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", (
        PADRAO, segundos, base, base, VERSAO, 0, 0, 0, json.dumps(configuracao, ensure_ascii=False),
        json.dumps({str(mid): tipo_de_nota(mid, tipo, did, segundos)}, ensure_ascii=False),
        json.dumps(baralhos, ensure_ascii=False), json.dumps({str(PADRAO): OPCOES_PADRAO}), json.dumps({})))
    for k, (chave, campos, etiquetas) in enumerate(notas):
        if len(campos) != len(tipo["campos"]):
            raise ValueError(f"nota {chave}: {len(campos)} campo(s), e não {len(tipo['campos'])}")
        if any(not e or any(c.isspace() for c in e) for e in etiquetas):
            raise ValueError(f"nota {chave}: etiqueta vazia ou com espaço: {etiquetas}")
        primeiro = sem_html(campos[0])
        banco.execute("INSERT INTO notes VALUES (?,?,?,?,?,?,?,?,?,?,?)", (
            base + k, guid(chave), mid, segundos, NAO_SINCRONIZADO, f" {' '.join(etiquetas)} ",
            SEPARADOR.join(campos), primeiro, soma(primeiro), 0, ""))
        banco.execute("INSERT INTO cards VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            base + k, base + k, did, 0, segundos, NAO_SINCRONIZADO, NOVO, NOVO, k + 1, 0, 0, 0, 0, 0, 0, 0, 0, ""))
    banco.commit()
    dados = banco.serialize()
    banco.close()
    return dados


def grava(caminho, nome_do_baralho, tipo, notas, data):
    """Grava o pacote no caminho e da o sha256 dele. tipo: {"nome", "cartao" (o nome do modelo de
    cartao), "campos" (os nomes, na ordem), "editor" ({"tipo_de_letra", "tamanho"} da letra dos
    campos no editor), "frente" e "verso" (os modelos do cartao) e "estilo" (o CSS)}; notas:
    [(chave, [o HTML de cada campo], [etiquetas])]; data: a data, com o fuso, do banco e das
    entradas do zip. O pacote se monta inteiro antes de ir para o arquivo."""
    quando = (data.year, data.month, data.day, data.hour, data.minute, data.second)
    saida = io.BytesIO()
    with zipfile.ZipFile(saida, "w") as pacote:
        for nome, conteudo in ((COLECAO, colecao(nome_do_baralho, tipo, notas, data)), (MIDIAS, SEM_MIDIAS)):
            entrada = zipfile.ZipInfo(nome, date_time=quando)
            entrada.compress_type = ENTRADAS["compressao"]
            entrada.create_system = ENTRADAS["sistema"]
            entrada.external_attr = ENTRADAS["permissoes"]
            pacote.writestr(entrada, conteudo)
    pathlib.Path(caminho).write_bytes(saida.getvalue())
    return hashlib.sha256(saida.getvalue()).hexdigest()
