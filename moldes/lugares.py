"""
Onde cada trecho das analises cai, pelas regras de um arquivo de dados: fora do material
e por que regra, com que marcas e em que documentos. Nada da materia fica no codigo: os
tipos de fora, as marcas, os grupos, os documentos e os caminhos vem das regras, e os
trechos vem do analises.py, com o valor e o texto de cada papel. As regras chegam
conferidas contra o molde do arquivo em que elas estao.

As regras:
  - "fora": cada regra tira do material o trecho cujos tipos sao todos dela;
  - "marcas": a marca acompanha o trecho que tem o texto dela no texto de um dos papeis
    dela; o trecho fica no material, com a marca;
  - "grupos": os grupos que as analises usam; "pelo_assunto" diz que o documento do trecho
    desse grupo vem do assunto dele, decidido numa leitura;
  - "documentos": cada um recebe os trechos de um dos grupos dele ou de um dos caminhos
    dele, ou todos os trechos ("todos"). Os que nao recebem todos sao os de conteudo.
As regras podem vir dentro de um arquivo maior, como o formato de um material, que traz
tambem o que elas nao usam.
"""
import analises

SEM_DOCUMENTO = "sem documento de conteúdo"  # o problema do trecho de estudo que nao cai em documento de conteudo


class ErroDeRegras(ValueError):
    """Regras que nao combinam com a forma das analises; a mensagem diz cada problema."""


def valor(trecho, papel):
    return trecho["papeis"][papel]["valor"]


def texto(trecho, papel):
    return trecho["papeis"][papel]["texto"]


def marcas(trecho, regras):
    """Os ids das marcas do trecho, na ordem das regras."""
    return [m["id"] for m in regras["marcas"] if any(m["texto"] in texto(trecho, p) for p in m["papeis"])]


def classe(trecho, regras):
    """("fora", id da regra) quando todos os tipos do trecho sao de uma regra de fora;
    ("problema", o que houve) quando um tipo de fora vem junto de outro, ou quando o trecho
    nao tem grupo nem marca; ("estudo",) nos outros casos."""
    tipos = set(valor(trecho, "tipo"))
    for regra in regras["fora"]:
        de_fora = set(regra["tipos"])
        if tipos & de_fora:
            return ("fora", regra["id"]) if tipos <= de_fora else ("problema", "tipo de fora junto de outro tipo")
    if not valor(trecho, "grupo") and not marcas(trecho, regras):
        return ("problema", "sem grupo e sem marca")
    return ("estudo",)


def grupos_desconhecidos(trecho, regras):
    conhecidos = {g["id"] for g in regras["grupos"]}
    return [g for g in valor(trecho, "grupo") if g not in conhecidos]


def documentos(trecho, regras):
    """Os documentos em que o trecho cai pelo grupo, pelo caminho ou por receber todos, na
    ordem das regras."""
    grupos, caminhos = set(valor(trecho, "grupo")), set(valor(trecho, "caminho"))
    return [d["id"] for d in regras["documentos"]
            if d.get("todos") or grupos & set(d.get("grupos", [])) or caminhos & set(d.get("caminhos", []))]


def documentos_de_conteudo(regras):
    return [d["id"] for d in regras["documentos"] if not d.get("todos")]


def pelo_assunto(trecho, regras):
    """Os grupos do trecho cujo documento vem do assunto."""
    marcados = {g["id"] for g in regras["grupos"] if g.get("pelo_assunto")}
    return [g for g in valor(trecho, "grupo") if g in marcados]


def sem_documento(trecho, regras):
    """A classe do trecho de estudo que nao cai em documento de conteudo: ("assunto",) quando
    tem grupo cujo documento vem do assunto; senao ("marca", id da primeira marca dele, na
    ordem das regras); senao ("problema", SEM_DOCUMENTO)."""
    if pelo_assunto(trecho, regras):
        return ("assunto",)
    suas = marcas(trecho, regras)
    return ("marca", suas[0]) if suas else ("problema", SEM_DOCUMENTO)


def lugar(trecho, regras):
    """(classe, documentos) do trecho so pelas regras. A classe de um trecho de estudo diz se
    ele tem lugar: ("estudo",) quando cai num documento de conteudo; senao, a do
    sem_documento. Os documentos sao todos aqueles em que o trecho cai, os que recebem todos
    inclusive; nenhum para o trecho de fora ou com problema na classe."""
    c = classe(trecho, regras)
    if c != ("estudo",):
        return c, []
    caidos = documentos(trecho, regras)
    if set(caidos) & set(documentos_de_conteudo(regras)):
        return c, caidos
    return sem_documento(trecho, regras), caidos


def erros_das_regras(regras, forma):
    """Os problemas das regras contra a forma, cada um numa frase: marca sem texto, sem papel
    ou procurada num papel que a forma nao da; documento com caminho que o campo do caminho
    nao tem, quando o campo diz os valores dele."""
    campos = {c["papel"]: c for c in forma["campos"] if "papel" in c}
    erros = []
    for m in regras["marcas"]:
        if not m["texto"]:
            erros.append(f"marca {m['id']!r}: sem texto")
        if not m["papeis"]:
            erros.append(f"marca {m['id']!r}: sem papel onde se procura")
        erros += [f"marca {m['id']!r}: papel {p!r}, que a forma não dá" for p in m["papeis"] if p not in campos]
    campo = campos.get("caminho", {})
    if "valores" in campo:
        for d in regras["documentos"]:
            erros += [f"documento {d['id']!r}: caminho {c!r}, que o campo {campo['nome']!r} não tem"
                      for c in d.get("caminhos", []) if c not in campo["valores"]]
    return erros


def trechos_das_analises(pasta, forma, regras):
    """(trechos, notas por aula, aulas) das analises da pasta, como o analises.ler_analises
    os da, com as regras conferidas contra a forma: ErroDeRegras com cada problema delas."""
    trechos, notas, aulas = analises.ler_analises(pasta, forma)
    erros = erros_das_regras(regras, forma)
    if erros:
        raise ErroDeRegras("as regras: " + "; ".join(erros))
    return trechos, notas, aulas
