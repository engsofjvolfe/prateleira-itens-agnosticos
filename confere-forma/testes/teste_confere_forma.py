"""Testes do confere_forma.py, com configuracao e documentos inventados aqui: as marcas da
secao, do divisor e do fecho, os titulos (com caracteres que sao especiais numa expressao
regular), a abertura, os padroes proibidos, os nomes e as palavras sao sorteados, com
letras de fora do ASCII. Conferem o que a peca faz, nunca uma frase pronta: em que arquivo e
linha sai cada ERRO, se sai AVISO, o codigo de saida e o resumo contando os erros e os
avisos que sairam. Cada defeito vai num documento proprio, que anota a linha em que o erro
tem de sair: abertura fora do modelo, a mais ou que falta; secoes fora de ordem, que faltam
ou a mais; secao sem divisor e divisor fora do lugar; secao sem fecho, com dois, com texto
depois dele e linha de bloco fora dele; padrao proibido, com e sem a excecao; nome fora do
italico (o mais curto dentro do mais longo nao conta de novo; negrito nao e italico; as
duas marcas valem; a linha de fora nao e conferida). As regras proibidas vem de dois
arquivos de dados sorteados, uma em cada um: sem eles nada e proibido, e num arquivo so dao
o mesmo. O marcas-de-ia.json da peca pega os exemplos do README, o caractere invisivel e o
resto de citacao, na linha deles, e deixa passar o documento certo e a tipografia comum. O
tamanho fora dos limites da AVISO e nao muda o codigo. Com o modelo do rodape, o rodape do
fim (com o divisor, um padrao proibido e um nome fora do italico) fica fora da conferencia e
das palavras, o texto antes dele se confere como sem ele, o rodape que nao esta no fim se
confere, e os textos sem rodape dao os mesmos ERRO; sem o modelo, o rodape se confere.
Configuracao, arquivos de proibidos, o modelo do rodape e argumentos que nao servem saem com
2, e o erro de um arquivo de proibidos ou do modelo diz o arquivo; duas rodadas dao o mesmo.
Uso:
    python3 -I teste_confere_forma.py <pasta do confere_forma.py> <pasta de trabalho nova>
"""
import json
import random
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

PECA, TRABALHO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
SCRIPT = PECA / "confere_forma.py"
FALHAS = []
SORTEIO = random.Random(11)
LETRAS = "abcdefghijklmnop" + "áçõüéñ"  # com letras de fora do ASCII
SIMBOLOS = "@#%&=+!?"


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


def palavra():
    return "".join(SORTEIO.choice(LETRAS) for _ in range(SORTEIO.randint(4, 9)))


def frase(n):
    return " ".join(palavra() for _ in range(n))


def marca():
    return "".join(SORTEIO.choice(SIMBOLOS) for _ in range(3)) + palavra()


def roda(configuracao, *textos, proibidos=None, rodape=None):
    """(codigo, [(arquivo, linha) de cada ERRO], [arquivo de cada AVISO], linhas que sairam);
    proibidos: os arquivos de padroes proibidos, e None da os dois do teste; rodape: o modelo do rodape, se houver."""
    extras = [a for p in (PROIBIDOS if proibidos is None else proibidos) for a in ("--proibidos", str(p))]
    extras += ["--rodape", str(rodape)] if rodape is not None else []
    r = subprocess.run([sys.executable, "-I", str(SCRIPT), str(configuracao), *map(str, textos), *extras],
                       capture_output=True, text=True, encoding="utf-8")
    linhas = r.stdout.strip().split("\n") if r.stdout.strip() else []
    erros = [(m.group(1), int(m.group(2))) for m in (re.match(r"^ERRO (.+?):(\d+): ", l) for l in linhas) if m]
    avisos = [m.group(1) for m in (re.match(r"^AVISO (.+?): ", l) for l in linhas) if m]
    return r.returncode, erros, avisos, linhas


TRABALHO.mkdir(parents=True)
SECAO, DIVISOR, BLOCO = marca() + " ", marca(), marca()
ABRE = f"{BLOCO} {palavra()}:"
TITULO_DO_DOCUMENTO, SUBTITULO = marca(), f"{frase(6)} ({palavra()})."
TITULOS = [f"{k}. {frase(2)} [{palavra().upper()}?] (+{palavra()})*" for k in range(1, 5)]
NOME_LONGO = f"{palavra().capitalize()} {palavra()}"
NOME_CURTO = NOME_LONGO.split()[0]  # esta dentro do longo
NOME_COM_PONTO = f"{palavra()[0].upper()}. {palavra()}"
PROIBIDO, PROIBIDO_FORA_DO_BLOCO = marca(), marca()
OUTRA_MARCA = SORTEIO.choice(["/", "^", "¦"])  # a segunda marca de italico, que nao e letra
FORA = f"^({re.escape(SECAO.strip())}|{re.escape(BLOCO)})"
CONFIGURACAO = {
    "versao_schema": 1,
    "abertura": [{"padrao": f"^{re.escape(TITULO_DO_DOCUMENTO)} .+$"}, {"igual": SUBTITULO}],
    "secao": f"^{re.escape(SECAO)}(?P<titulo>.+)$",
    "titulos": TITULOS,
    "divisor": f"^{re.escape(DIVISOR)}$",
    "fecho": {"abre": f"^{re.escape(ABRE)}", "continua": f"^{re.escape(BLOCO)}"},
    "italico": {"nomes": [NOME_LONGO, NOME_CURTO, NOME_COM_PONTO], "marcas": ["*", OUTRA_MARCA], "fora_de": FORA},
    "palavras": {"fora_de": FORA, "minimo": 0, "maximo": 10 ** 6},
}


def grava_configuracao(dados):
    caminho = TRABALHO / f"{palavra()}.json"
    caminho.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    return caminho


def proibidos(*regras, **campos):
    """Um arquivo de padroes proibidos com as regras dadas e os campos a mais."""
    return grava_configuracao({"versao_schema": 1, "proibidos": list(regras), **campos})


REGRA = {"nome": palavra(), "padrao": re.escape(PROIBIDO)}
REGRA_COM_EXCECAO = {"nome": palavra(), "padrao": re.escape(PROIBIDO_FORA_DO_BLOCO), "exceto": f"^{re.escape(BLOCO)}"}
PROIBIDOS = [proibidos(REGRA), proibidos(REGRA_COM_EXCECAO)]  # uma regra em cada arquivo


class Documento:
    """As linhas de um documento e as linhas em que um ERRO tem de sair."""

    def __init__(self):
        self.linhas, self.erros = [], []

    def poe(self, linha="", erro=False):
        self.linhas.append(linha)
        if erro:
            self.erros.append(len(self.linhas))
        return len(self.linhas)

    def grava(self):
        caminho = TRABALHO / f"{palavra()}.md"
        caminho.write_text("\n".join(self.linhas) + "\n", encoding="utf-8")
        return caminho


def abertura(d, titulo=True, subtitulo=True, sem_subtitulo=False, a_mais=False):
    d.poe(f"{TITULO_DO_DOCUMENTO} {frase(3)}" if titulo else frase(4), erro=not titulo)
    d.poe()
    if not sem_subtitulo:
        d.poe(SUBTITULO if subtitulo else f"{SUBTITULO} {palavra()}", erro=not subtitulo)
        d.poe()
    if a_mais:
        d.poe(frase(5), erro=True)
        d.poe()


def fecho(d):
    """O bloco de fecho, com um nome fora do italico e o proibido que vale dentro dele: nada disso e erro."""
    linha = d.poe(f"{ABRE} {frase(3)} {NOME_LONGO}")
    d.poe(f"{BLOCO} {frase(5)} {PROIBIDO_FORA_DO_BLOCO}")
    return linha


def secao(d, titulo, divisor=True, com_fecho=True, corpo=()):
    """Uma secao certa, com as linhas dadas no corpo; devolve a linha do titulo."""
    if divisor:
        d.poe(DIVISOR)
        d.poe()
    titulo_em = d.poe(SECAO + titulo, erro=False)
    d.poe()
    d.poe(f"{frase(9)} *{NOME_LONGO}* e ***{NOME_COM_PONTO}*** {frase(2)} {OUTRA_MARCA}{NOME_CURTO}{OUTRA_MARCA}.")
    d.poe(f"* **{palavra()}:** {frase(4)} {palavra()}{NOME_CURTO}{palavra()}")  # colado a outras letras, nao e o nome
    for linha, erro in corpo:
        d.poe(linha, erro=erro)
    d.poe()
    if com_fecho:
        fecho(d)
    d.poe()
    return titulo_em


def documento(titulos=TITULOS, **mudancas):
    """Um documento com a abertura e as secoes certas, menos o que as mudancas dizem."""
    d = Documento()
    abertura(d, **{k: v for k, v in mudancas.items() if k in ("titulo", "subtitulo", "sem_subtitulo", "a_mais")})
    for k, titulo in enumerate(titulos):
        extras = mudancas.get("secoes", {}).get(k, {})
        linha = secao(d, titulo, **extras)
        if k in mudancas.get("erro_no_titulo", ()):
            d.erros.append(linha)
    return d


def ultima_com_texto(d):
    return max(k for k, l in enumerate(d.linhas, start=1) if l.strip())


CASOS = {
    "certo": documento(),
    "título fora do modelo": documento(titulo=False),
    "subtítulo diferente": documento(subtitulo=False),
    "linha a mais na abertura": documento(a_mais=True),
    "seções fora de ordem": documento(titulos=[TITULOS[0], TITULOS[2], TITULOS[1], TITULOS[3]], erro_no_titulo=(1, 2)),
    "seção a mais": documento(titulos=TITULOS + [f"{frase(2)}"], erro_no_titulo=(len(TITULOS),)),
    "seção sem divisor": documento(secoes={1: {"divisor": False}}, erro_no_titulo=(1,)),
    "seção sem fecho": documento(secoes={2: {"com_fecho": False}}, erro_no_titulo=(2,)),
    "divisor fora do lugar": documento(secoes={1: {"corpo": [(DIVISOR, True)]}}),
    "texto depois do fecho": None,
    "dois fechos": None,
    "linha de bloco fora do fecho": documento(secoes={2: {"corpo": [(f"{BLOCO} {frase(4)}", True)]}}),
    "padrões proibidos": documento(secoes={0: {"corpo": [(f"{frase(2)} {PROIBIDO} {frase(2)}", True),
                                                         (f"{frase(2)} {PROIBIDO_FORA_DO_BLOCO}", True)]}}),
    "nomes fora do itálico": documento(secoes={3: {"corpo": [(f"{frase(2)} {NOME_LONGO} {frase(2)}", True),
                                                              (f"{frase(2)} {NOME_CURTO}.", True),
                                                              (f"{frase(2)} **{NOME_COM_PONTO}** {frase(2)}", True),
                                                              (f"{SECAO.strip()}{frase(2)} {NOME_LONGO}", False)]}}),
}

d = documento()  # texto depois do fecho: depois do bloco da ultima secao
d.poe(frase(4), erro=True)
CASOS["texto depois do fecho"] = d
d = documento()  # dois fechos na ultima secao
CASOS["dois fechos"] = d
d.poe()
d.erros.append(fecho(d))
falta = documento(titulos=TITULOS[:-1])
falta.erros.append(ultima_com_texto(falta))
CASOS["seção que falta"] = falta
sem_sub = documento(sem_subtitulo=True)
sem_sub.erros.append(1)
CASOS["falta linha na abertura"] = sem_sub

CONF = grava_configuracao(CONFIGURACAO)
arquivos = {nome: caso.grava() for nome, caso in CASOS.items()}
codigo, erros, avisos, linhas = roda(CONF, arquivos["certo"])
confere(codigo == 0 and not erros and not avisos, f"o documento certo sai sem ERRO, sem AVISO e com 0: {linhas}")
codigo, erros, avisos, linhas = roda(CONF, *arquivos.values())
ERROS_DE_TODOS = erros
confere(codigo == 1, f"com defeito sai com 1: {codigo}")
for nome, caminho in arquivos.items():
    achados = sorted(linha for arquivo, linha in erros if arquivo == str(caminho))
    confere(achados == sorted(CASOS[nome].erros),
            f"{nome}: ERRO nas linhas {achados}, e não em {sorted(CASOS[nome].erros)}")
resumo = [int(n) for n in re.findall(r"\d+", linhas[-1])] if linhas else []
confere(resumo == [len(arquivos), len(erros), len(avisos)],
        f"o resumo conta os textos, os ERRO e os AVISO: {linhas[-1:]}")
confere(roda(CONF, *arquivos.values())[3] == linhas, "duas rodadas dão o mesmo")
codigo, erros, _, _ = roda(CONF, arquivos["padrões proibidos"], proibidos=[])
confere(codigo == 0 and not erros, f"sem arquivo de padrões proibidos, nada é proibido: {codigo}, {erros}")
confere(roda(CONF, *arquivos.values(), proibidos=[proibidos(REGRA, REGRA_COM_EXCECAO)])[1] == ERROS_DE_TODOS,
        "as regras num arquivo só dão os mesmos ERRO que em dois")

MARCAS_DE_IA = PECA / "marcas-de-ia.json"
codigo, erros, _, linhas = roda(CONF, arquivos["certo"], proibidos=PROIBIDOS + [MARCAS_DE_IA])
confere(codigo == 0 and not erros, f"o marcas-de-ia.json deixa passar o documento certo: {codigo}, {linhas}")
INVISIVEIS = [unicodedata.lookup(n) for n in ("NO-BREAK SPACE", "ZERO WIDTH SPACE", "LEFT-TO-RIGHT MARK")]
RESTOS = ["oaicite", "contentReference", "utm_source="]  # os exemplos do README, como os INVISIVEIS
TIPOGRAFIA = " ".join(unicodedata.lookup(n) for n in ("EM DASH", "EN DASH", "LEFT DOUBLE QUOTATION MARK",
                                                      "RIGHT DOUBLE QUOTATION MARK", "HORIZONTAL ELLIPSIS",
                                                      "DEGREE SIGN", "MICRO SIGN"))
MARCADO = documento(secoes={1: {"corpo": [(f"{palavra()}{c}{palavra()} {frase(2)}", True) for c in INVISIVEIS]
                                + [(f"{frase(2)} {palavra()}{r}{palavra()}", True) for r in RESTOS]
                                + [(f"{frase(2)} {TIPOGRAFIA} {frase(2)}", False)]}})
codigo, erros, _, linhas = roda(CONF, MARCADO.grava(), proibidos=[MARCAS_DE_IA])
confere(codigo == 1 and sorted(linha for _, linha in erros) == sorted(MARCADO.erros),
        f"o marcas-de-ia.json pega cada exemplo na linha dele e deixa passar a tipografia comum: {codigo}, {linhas}")

def palavras(linhas):
    """As palavras que a linha do tamanho de um texto, na saida, diz que ele tem."""
    return int(re.search(r": (\d+) palavra", next(l for l in linhas if " palavra" in l)).group(1))


PALAVRAS = palavras(roda(CONF, arquivos["certo"])[3])
for minimo, maximo, descricao in ((PALAVRAS + 1, PALAVRAS + 9, "acima do tamanho"),
                                  (0, PALAVRAS - 1, "abaixo do tamanho")):
    conf = grava_configuracao(dict(CONFIGURACAO, palavras={"fora_de": FORA, "minimo": minimo, "maximo": maximo}))
    codigo, erros, avisos, _ = roda(conf, arquivos["certo"])
    confere(codigo == 0 and not erros and avisos == [str(arquivos["certo"])],
            f"tamanho fora dos limites ({descricao}) dá AVISO e sai com 0: {codigo}, {avisos}")
conf = grava_configuracao(dict(CONFIGURACAO, palavras={"fora_de": FORA, "minimo": PALAVRAS, "maximo": PALAVRAS}))
confere(not roda(conf, arquivos["certo"])[2], "o tamanho igual aos limites não dá AVISO")

ALVO_DO_RODAPE = TRABALHO / f"{palavra()}.txt"
ALVO_DO_RODAPE.write_text(frase(3), encoding="utf-8")
# o rodape, na pasta dos documentos, com o divisor, um padrao proibido e um nome fora do italico
RODAPE = [DIVISOR, "", f"{frase(3)} {PROIBIDO} [{NOME_LONGO}]({ALVO_DO_RODAPE.name}) {frase(2)}."]
MODELO = TRABALHO / f"{palavra()}.md"
MODELO.write_text("\n".join(RODAPE) + "\n", encoding="utf-8")


def com_rodape(caso, *depois):
    """O documento do caso com o rodape no fim, depois de uma linha em branco, e as linhas dadas depois dele; os erros
    sao os do caso, e rodape_em, a linha em que o rodape comeca."""
    d = Documento()
    d.linhas, d.erros = list(CASOS[caso].linhas), list(CASOS[caso].erros)
    while d.linhas and not d.linhas[-1].strip():
        d.linhas.pop()
    d.rodape_em = len(d.linhas) + 2
    d.linhas += ["", *RODAPE, *depois]
    return d


CERTO_COM_RODAPE = com_rodape("certo").grava()
codigo, erros, avisos, linhas = roda(CONF, CERTO_COM_RODAPE, rodape=MODELO)
confere(codigo == 0 and not erros and not avisos and palavras(linhas) == PALAVRAS,
        f"com o modelo, o rodapé do fim fica fora da conferência e das palavras: {codigo}, {linhas}")
codigo, erros, _, linhas = roda(CONF, CERTO_COM_RODAPE)
confere(codigo == 1 and erros and all(linha >= com_rodape("certo").rodape_em for _, linha in erros),
        f"sem o modelo, o rodapé se confere como o resto do texto: {codigo}, {linhas}")
DEFEITO = com_rodape("texto depois do fecho")
codigo, erros, _, linhas = roda(CONF, DEFEITO.grava(), rodape=MODELO)
confere(codigo == 1 and sorted(linha for _, linha in erros) == sorted(DEFEITO.erros),
        f"com o modelo, o texto antes do rodapé se confere como sem ele, cada linha no número dela: {linhas}")
NO_MEIO = com_rodape("certo", "", frase(4))
codigo, erros, _, linhas = roda(CONF, NO_MEIO.grava(), rodape=MODELO)
confere(codigo == 1 and any(linha >= NO_MEIO.rodape_em for _, linha in erros),
        f"o rodapé que não está no fim se confere como o resto do texto: {codigo}, {linhas}")
confere(roda(CONF, *arquivos.values(), rodape=MODELO)[1] == ERROS_DE_TODOS,
        "nos textos sem rodapé, o modelo não muda nenhum ERRO")
SEM_MODELO = TRABALHO / f"{palavra()}.md"
codigo, erros, _, linhas = roda(CONF, arquivos["certo"], rodape=SEM_MODELO)
confere(codigo == 2 and not erros and str(SEM_MODELO) in "\n".join(linhas),
        f"o modelo que não serve sai com 2, sem conferir, e o erro diz o arquivo: {codigo}, {linhas}")


def com(caminho, valor):
    """Uma copia da configuracao com o valor no caminho ("a/b"); None tira o campo."""
    dados = json.loads(json.dumps(CONFIGURACAO))
    alvo, partes = dados, caminho.split("/")
    for parte in partes[:-1]:
        alvo = alvo[parte]
    if valor is None:
        del alvo[partes[-1]]
    else:
        alvo[partes[-1]] = valor
    return grava_configuracao(dados)


ESTRAGADAS = {
    "campo que o molde não conhece": com(palavra(), palavra()),
    "campo que falta": com("titulos", None),
    "item da abertura com os dois campos": com("abertura", [{"igual": "x", "padrao": "x"}]),
    "item da abertura sem campo": com("abertura", [{}]),
    "seção sem o grupo do título": com("secao", f"^{re.escape(SECAO)}(.+)$"),
    "expressão que não compila": com("divisor", "("),
    "mínimo maior que o máximo": com("palavras", {"fora_de": FORA, "minimo": 9, "maximo": 1}),
    "mínimo que não é número": com("palavras", {"fora_de": FORA, "minimo": "9", "maximo": 99}),
    "marca vazia": com("italico/marcas", [""]),
    "padrões proibidos, que vão em arquivo próprio": com("proibidos", [REGRA]),
    "título que não é texto": com("titulos", [1, 2]),
}
for nome, caminho in ESTRAGADAS.items():
    codigo, erros, _, linhas = roda(caminho, arquivos["certo"])
    confere(codigo == 2 and not erros, f"configuração com {nome} sai com 2, sem conferir: {codigo}, {linhas}")
NAO_E_JSON = TRABALHO / f"{palavra()}.json"
NAO_E_JSON.write_text("{" + palavra(), encoding="utf-8")
PROIBIDOS_QUE_NAO_SERVEM = {
    "campo que o molde não conhece": [proibidos(REGRA, **{palavra(): palavra()})],
    "outra versão": [proibidos(REGRA, versao_schema=2)],
    "regra com campo que o molde não conhece": [proibidos(dict(REGRA, **{palavra(): palavra()}))],
    "regra sem nome": [proibidos({"padrao": REGRA["padrao"]})],
    "regra com nome sem letra": [proibidos(dict(REGRA, nome=" "))],
    "regra sem padrão": [proibidos({"nome": palavra()})],
    "regra com padrão vazio": [proibidos({"nome": palavra(), "padrao": ""})],
    "regra com padrão que não compila": [proibidos({"nome": palavra(), "padrao": "("})],
    "regra com exceção que não compila": [proibidos(dict(REGRA, exceto="["))],
    "o mesmo nome em dois arquivos": [proibidos(REGRA), proibidos(dict(REGRA_COM_EXCECAO, nome=REGRA["nome"]))],
    "o mesmo nome duas vezes num arquivo": [proibidos(REGRA, dict(REGRA_COM_EXCECAO, nome=REGRA["nome"]))],
    "o mesmo arquivo duas vezes": [PROIBIDOS[0], PROIBIDOS[0]],
    "arquivo que não existe": [TRABALHO / f"{palavra()}.json"],
    "arquivo que não é JSON": [NAO_E_JSON],
}
for nome, caminhos in PROIBIDOS_QUE_NAO_SERVEM.items():
    codigo, erros, _, linhas = roda(CONF, arquivos["certo"], proibidos=caminhos)
    saida = "\n".join(linhas)
    confere(codigo == 2 and not erros and all(str(c) in saida for c in caminhos),
            f"padrões proibidos com {nome} saem com 2, sem conferir, e o erro diz o arquivo: {codigo}, {linhas}")
codigo, erros, _, _ = roda(CONF, TRABALHO / f"{palavra()}.md")
confere(codigo == 2 and not erros, f"texto que não existe sai com 2: {codigo}")
LATIN = TRABALHO / f"{palavra()}.md"
LATIN.write_bytes(arquivos["certo"].read_text(encoding="utf-8").encode("latin-1", errors="replace") + b"\xe9\xff")
codigo, erros, _, _ = roda(CONF, LATIN)
confere(codigo == 2 and not erros, f"texto que não se lê em UTF-8 sai com 2: {codigo}")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
