"""Testes do confere_forma.py, com o esqueleto, a configuracao e os documentos inventados aqui:
as marcas da secao, do divisor e do fecho, os titulos (com caracteres que sao especiais numa
expressao regular), a abertura, as lacunas, as siglas, os padroes proibidos, os nomes e as
palavras sao sorteados, com letras de fora do ASCII; a forma do comeco das secoes, a das siglas
na primeira vez (o que vem logo antes e logo depois delas) e o trecho de fora das siglas, uma
marcacao com uma sigla dentro, tambem sao inventados. Conferem o que a peca faz, nunca uma frase pronta:
em que arquivo e linha sai cada ERRO (quantos em cada linha), se sai AVISO, o codigo de saida e
o resumo contando os erros e os avisos que sairam. Cada defeito vai num documento proprio, que
anota a linha em que o erro tem de sair: abertura fora do esqueleto, a mais ou que falta;
secoes fora de ordem, que faltam, a mais ou com texto a mais no titulo; o titulo com outra
palavra na lacuna, que nao e erro, e com o que a lacuna nao aceita; secao sem divisor e divisor
fora do lugar; secao que comeca por uma linha fora da forma (so a primeira conta), so com o
fecho ou sem nada no fim; secao sem fecho, com dois, com texto depois dele e linha de bloco fora
dele; a sigla fora da forma na primeira vez (as duas de uma linha, a do fim da linha, a com a
explicacao longe, com o antes longe, com o depois longe, so com o antes, so com o depois, a que
antes so apareceu numa linha de fora ou dentro do trecho de fora), e nao sao erro a da forma na
primeira vez, tambem logo depois do trecho de fora, a de dentro do trecho de fora e as vezes
seguintes; cada texto com as siglas dele; sem o antes ou sem o depois, so o outro lado vale; a
forma se confere na linha inteira, tambem onde ha trecho de fora; padrao proibido, com e sem a
excecao; nome fora do italico (o mais curto dentro do
mais longo nao conta de novo; negrito nao e italico; as duas marcas valem; a linha de fora nao
e conferida). A lacuna de marca mais longa vale antes da que esta dentro dela. Os divisores do
esqueleto nao mudam nada; sem lacunas, o esqueleto vale letra por letra; sem o comeco das secoes
e sem as siglas, nada deles se confere. As regras proibidas vem de dois arquivos de dados
sorteados, uma em cada um: sem eles nada e proibido, e num arquivo so dao o mesmo. O
marcas-de-ia.json da peca pega os exemplos do README, o caractere invisivel e o resto de
citacao, na linha deles, e deixa passar o documento certo e a tipografia comum. O tamanho fora
dos limites da AVISO e nao muda o codigo. Com o modelo do rodape, o rodape do fim (com o
divisor, um padrao proibido e um nome fora do italico) fica fora da conferencia e das palavras,
o texto antes dele se confere como sem ele, o rodape que nao esta no fim se confere, e os
textos sem rodape dao os mesmos ERRO; sem o modelo, o rodape se confere. A configuracao, o
esqueleto, os arquivos de proibidos, o modelo do rodape e os argumentos que nao servem saem com
2, e o erro do esqueleto, de um arquivo de proibidos ou do modelo diz o arquivo; duas rodadas
dao o mesmo.
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
MAIUSCULAS = LETRAS.upper()
SIMBOLOS = "@#%&=+!?"
# a explicacao inventada de uma sigla vai entre estas aspas, de fora do ASCII
ABRE_EXPLICACAO, FECHA_EXPLICACAO = (unicodedata.lookup(f"{lado}-POINTING DOUBLE ANGLE QUOTATION MARK")
                                     for lado in ("LEFT", "RIGHT"))
# na primeira vez, a sigla vai entre estes colchetes, logo depois da explicacao; o trecho de fora abre com a chave
ABRE_SIGLA, FECHA_SIGLA = (unicodedata.lookup(f"MATHEMATICAL {lado} WHITE SQUARE BRACKET")
                           for lado in ("LEFT", "RIGHT"))
ABRE_TRECHO = unicodedata.lookup("LEFT WHITE CURLY BRACKET")
SIGLAS_SORTEADAS = set()


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


def sigla():
    """Uma sigla sorteada, de duas a quatro maiusculas, tambem de fora do ASCII, que ainda nao saiu."""
    while True:
        nova = "".join(SORTEIO.choice(MAIUSCULAS) for _ in range(SORTEIO.randint(2, 4)))
        if nova not in SIGLAS_SORTEADAS:
            SIGLAS_SORTEADAS.add(nova)
            return nova


def roda(configuracao, *textos, proibidos=None, rodape=None, esqueleto=None):
    """(codigo, [(arquivo, linha) de cada ERRO], [arquivo de cada AVISO], linhas que sairam);
    proibidos: os arquivos de padroes proibidos, e None da os dois do teste; rodape: o modelo do rodape, se houver;
    esqueleto: o do teste, quando None."""
    extras = [a for p in (PROIBIDOS if proibidos is None else proibidos) for a in ("--proibidos", str(p))]
    extras += ["--rodape", str(rodape)] if rodape is not None else []
    r = subprocess.run([sys.executable, "-I", str(SCRIPT), str(configuracao), str(esqueleto or ESQUELETO),
                        *map(str, textos), *extras], capture_output=True, text=True, encoding="utf-8")
    linhas = r.stdout.strip().split("\n") if r.stdout.strip() else []
    erros = [(m.group(1), int(m.group(2))) for m in (re.match(r"^ERRO (.+?):(\d+): ", l) for l in linhas) if m]
    avisos = [m.group(1) for m in (re.match(r"^AVISO (.+?): ", l) for l in linhas) if m]
    return r.returncode, erros, avisos, linhas


TRABALHO.mkdir(parents=True)
SECAO, DIVISOR, BLOCO = marca() + " ", marca(), marca()
ABRE = f"{BLOCO} {palavra()}:"
TITULO_DO_DOCUMENTO, SUBTITULO = marca(), f"{frase(6)} ({palavra()})."
LACUNA_DA_ABERTURA, LACUNA_DO_TITULO = (f"{{{palavra()}}}" for _ in range(2))  # as marcas, entre chaves
LACUNA_LONGA = LACUNA_DO_TITULO + palavra()  # a lacuna do titulo esta dentro dela
COM_LACUNA, COM_A_LONGA = 1, 3  # os titulos que, no esqueleto, tem uma lacuna no lugar da palavra do meio
# cada titulo em tres partes: o comeco, a palavra do meio (na que tem a lacuna longa, um numero) e o fim
PARTES_DOS_TITULOS = [(f"{k + 1}. {frase(2)} [{palavra().upper()}?] (+",
                       str(SORTEIO.randint(10, 999)) if k == COM_A_LONGA else palavra(), ")*") for k in range(4)]
TITULOS = ["".join(partes) for partes in PARTES_DOS_TITULOS]
NO_MEIO_DO_ESQUELETO = {COM_LACUNA: LACUNA_DO_TITULO, COM_A_LONGA: LACUNA_LONGA}  # o titulo -> a marca no meio
TITULOS_DO_ESQUELETO = [f"{a}{NO_MEIO_DO_ESQUELETO.get(k, b)}{c}" for k, (a, b, c) in enumerate(PARTES_DOS_TITULOS)]
ABERTURA_DO_ESQUELETO = [f"{TITULO_DO_DOCUMENTO} {LACUNA_DA_ABERTURA}", SUBTITULO]
NOME_LONGO = f"{palavra().capitalize()} {palavra()}"
NOME_CURTO = NOME_LONGO.split()[0]  # esta dentro do longo
NOME_COM_PONTO = f"{palavra()[0].upper()}. {palavra()}"
PROIBIDO, PROIBIDO_FORA_DO_BLOCO = marca(), marca()
OUTRA_MARCA = SORTEIO.choice(["/", "^", unicodedata.lookup("BROKEN BAR")])  # a segunda marca de italico, nao letra
FORA = f"^({re.escape(SECAO.strip())}|{re.escape(BLOCO)})"
NO_TRECHO = sigla()  # a sigla de dentro do trecho de fora
TRECHO = f"{ABRE_TRECHO}{NO_TRECHO}:"  # o trecho de fora, a marcacao que nao se le como sigla
CONFIGURACAO = {
    "versao_schema": 2,
    "lacunas": [{"marca": LACUNA_DA_ABERTURA, "padrao": f"[{LETRAS}]+(?: [{LETRAS}]+){{2}}"},
                {"marca": LACUNA_DO_TITULO, "padrao": f"[{LETRAS}]+|[0-9]+"},  # com uma alternativa no topo
                {"marca": LACUNA_LONGA, "padrao": "[0-9]+"}],
    "secao": f"^{re.escape(SECAO)}(?P<titulo>.+)$",
    "comeco_das_secoes": f"^[{LETRAS}]",
    "divisor": f"^{re.escape(DIVISOR)}$",
    "fecho": {"abre": f"^{re.escape(ABRE)}", "continua": f"^{re.escape(BLOCO)}"},
    # o antes sem o $ e o depois sem o ^: o lugar logo antes e logo depois da sigla vale pela peca, nao pela expressao
    "siglas": {"padrao": f"(?<!\\w)[{MAIUSCULAS}]{{2,4}}(?!\\w)", "fora_de": FORA, "trechos_fora": re.escape(TRECHO),
               "antes": f"{ABRE_EXPLICACAO}[^{FECHA_EXPLICACAO}]+{FECHA_EXPLICACAO} {re.escape(ABRE_SIGLA)}",
               "depois": re.escape(FECHA_SIGLA)},
    "italico": {"nomes": [NOME_LONGO, NOME_CURTO, NOME_COM_PONTO], "marcas": ["*", OUTRA_MARCA], "fora_de": FORA},
    "palavras": {"fora_de": FORA, "minimo": 0, "maximo": 10 ** 6},
}


def grava(texto, extensao=".md"):
    caminho = TRABALHO / f"{palavra()}{extensao}"
    caminho.write_text(texto, encoding="utf-8")
    return caminho


def grava_configuracao(dados):
    return grava(json.dumps(dados, ensure_ascii=False), ".json")


def grava_esqueleto(abertura, titulos, divisores=True, depois=()):
    """O esqueleto com as linhas da abertura e os titulos, cada titulo com o divisor antes, se houver, e as linhas
    dadas depois deles."""
    linhas = [linha for item in abertura for linha in (item, "")]
    for titulo in titulos:
        linhas += ([DIVISOR, ""] if divisores else []) + [SECAO + titulo, ""]
    return grava("\n".join(linhas + list(depois)) + "\n")


def proibidos(*regras, **campos):
    """Um arquivo de padroes proibidos com as regras dadas e os campos a mais."""
    return grava_configuracao({"versao_schema": 1, "proibidos": list(regras), **campos})


ESQUELETO = grava_esqueleto(ABERTURA_DO_ESQUELETO, TITULOS_DO_ESQUELETO)
REGRA = {"nome": palavra(), "padrao": re.escape(PROIBIDO)}
REGRA_COM_EXCECAO = {"nome": palavra(), "padrao": re.escape(PROIBIDO_FORA_DO_BLOCO), "exceto": f"^{re.escape(BLOCO)}"}
PROIBIDOS = [proibidos(REGRA), proibidos(REGRA_COM_EXCECAO)]  # uma regra em cada arquivo


class Documento:
    """As linhas de um documento e as linhas em que um ERRO tem de sair, uma vez para cada erro."""

    def __init__(self):
        self.linhas, self.erros = [], []

    def poe(self, linha="", erro=0):
        self.linhas.append(linha)
        self.erros += [len(self.linhas)] * int(erro)
        return len(self.linhas)

    def grava(self):
        return grava("\n".join(self.linhas) + "\n")


def abertura(d, titulo=True, subtitulo=True, sem_subtitulo=False, a_mais=False):
    d.poe(f"{TITULO_DO_DOCUMENTO} {frase(3)}" if titulo else frase(4), erro=not titulo)
    d.poe()
    if not sem_subtitulo:
        d.poe(SUBTITULO if subtitulo else f"{SUBTITULO} {palavra()}", erro=not subtitulo)
        d.poe()
    if a_mais:
        d.poe(frase(5), erro=True)
        d.poe()


def fecho(d, erro=False):
    """O bloco de fecho, com um nome fora do italico e o proibido que vale dentro dele: nada disso e erro."""
    linha = d.poe(f"{ABRE} {frase(3)} {NOME_LONGO}", erro=erro)
    d.poe(f"{BLOCO} {frase(5)} {PROIBIDO_FORA_DO_BLOCO}")
    return linha


def secao(d, titulo, divisor=True, com_fecho=True, antes=(), corpo=(), vazia=False):
    """Uma secao certa, com as linhas dadas antes do paragrafo do comeco e no corpo; vazia, so com o titulo e o fecho,
    se houver, que entao e o comeco da secao, fora da forma. Devolve a linha do titulo."""
    if divisor:
        d.poe(DIVISOR)
        d.poe()
    titulo_em = d.poe(SECAO + titulo)
    d.poe()
    for linha, erro in antes:
        d.poe(linha, erro=erro)
    if not vazia:
        d.poe(f"{frase(9)} *{NOME_LONGO}* e ***{NOME_COM_PONTO}*** {frase(2)} {OUTRA_MARCA}{NOME_CURTO}{OUTRA_MARCA}.")
        d.poe(f"* **{palavra()}:** {frase(4)} {palavra()}{NOME_CURTO}{palavra()}")  # colado a outras letras
        for linha, erro in corpo:
            d.poe(linha, erro=erro)
        d.poe()
    if com_fecho:
        fecho(d, erro=vazia and not antes)
    d.poe()
    return titulo_em


def documento(titulos=TITULOS, **mudancas):
    """Um documento com a abertura e as secoes certas, menos o que as mudancas dizem; o erro_no_titulo traz o indice
    de uma secao uma vez para cada erro no titulo dela."""
    d = Documento()
    abertura(d, **{k: v for k, v in mudancas.items() if k in ("titulo", "subtitulo", "sem_subtitulo", "a_mais")})
    for k, titulo in enumerate(titulos):
        linha = secao(d, titulo, **mudancas.get("secoes", {}).get(k, {}))
        d.erros += [linha] * list(mudancas.get("erro_no_titulo", ())).count(k)
    return d


def ultima_com_texto(d):
    return max(k for k, l in enumerate(d.linhas, start=1) if l.strip())


def explicacao():
    return f"{ABRE_EXPLICACAO}{frase(2)}{FECHA_EXPLICACAO}"


def na_forma(s):
    """A sigla na forma da primeira vez: a explicacao e, logo depois, a sigla entre os colchetes."""
    return f"{explicacao()} {ABRE_SIGLA}{s}{FECHA_SIGLA}"


S = [sigla() for _ in range(12)]
OUTRO_NA_LACUNA = [f"{a}{palavra() if k == COM_LACUNA else b}{c}" for k, (a, b, c) in enumerate(PARTES_DOS_TITULOS)]
FORA_DA_LACUNA = [f"{a}{sigla() if k == COM_LACUNA else b}{c}" for k, (a, b, c) in enumerate(PARTES_DOS_TITULOS)]
CASOS = {
    "certo": documento(),
    "título fora do modelo": documento(titulo=False),
    "subtítulo diferente": documento(subtitulo=False),
    "linha a mais na abertura": documento(a_mais=True),
    "seções fora de ordem": documento(titulos=[TITULOS[0], TITULOS[2], TITULOS[1], TITULOS[3]], erro_no_titulo=(1, 2)),
    "seção a mais": documento(titulos=TITULOS + [f"{frase(2)}"], erro_no_titulo=(len(TITULOS),)),
    "título com texto a mais": documento(titulos=[f"{TITULOS[0]} {palavra()}"] + TITULOS[1:], erro_no_titulo=(0,)),
    "título com outra palavra na lacuna": documento(titulos=OUTRO_NA_LACUNA),
    "título com o que a lacuna não aceita": documento(titulos=FORA_DA_LACUNA, erro_no_titulo=(COM_LACUNA,)),
    "seção sem divisor": documento(secoes={1: {"divisor": False}}, erro_no_titulo=(1,)),
    "seção que começa fora da forma": documento(secoes={1: {"antes": [(f"* **{palavra()}:** {frase(3)}", True),
                                                                      (f"{SECAO.strip()}{frase(2)}", False)]}}),
    "seção só com o fecho": documento(secoes={2: {"vazia": True}}),
    "seção vazia no fim": documento(secoes={3: {"vazia": True, "com_fecho": False}}, erro_no_titulo=(3, 3)),
    "seção sem fecho": documento(secoes={2: {"com_fecho": False}}, erro_no_titulo=(2,)),
    "divisor fora do lugar": documento(secoes={1: {"corpo": [(DIVISOR, True)]}}),
    "texto depois do fecho": None,
    "dois fechos": None,
    "linha de bloco fora do fecho": documento(secoes={2: {"corpo": [(f"{BLOCO} {frase(4)}", True)]}}),
    "siglas": documento(secoes={
        0: {"corpo": [(f"{frase(2)} {na_forma(S[0])} {frase(2)}.", False),  # na forma na primeira vez
                      (f"{frase(2)} {S[1]} {frase(2)}.", True),  # fora da forma na primeira vez
                      (f"{frase(1)} {S[2]} {frase(1)} {S[3]}.", 2),  # as duas de uma linha
                      (f"{SECAO.strip()}{frase(2)} {S[4]}", False),  # numa linha de fora, nao conta
                      (f"{frase(2)} {S[5]}", True),  # no fim da linha
                      (f"{frase(1)} {TRECHO} {frase(2)}.", False),  # dentro do trecho de fora, nao se le
                      (f"{TRECHO} {frase(1)} {na_forma(S[6])}.", False)]},  # na forma, depois do trecho de fora
        2: {"corpo": [(f"{frase(2)} {S[0]} {frase(2)}.", False),  # a segunda vez, fora da forma
                      (f"{frase(2)} {na_forma(S[1])}.", False),  # a segunda vez, na forma
                      (f"{frase(2)} {S[4]} {frase(2)}.", True),  # a primeira vez fora das linhas de fora
                      (f"{frase(2)} {NO_TRECHO} {frase(1)}.", True),  # a primeira vez fora do trecho de fora
                      (f"{explicacao()} {palavra()} {ABRE_SIGLA}{S[7]}{FECHA_SIGLA}.", True),  # a explicacao longe
                      (f"{explicacao()} {ABRE_SIGLA} {palavra()} {S[8]}{FECHA_SIGLA}.", True),  # o antes longe
                      (f"{explicacao()} {ABRE_SIGLA}{S[9]} {palavra()}{FECHA_SIGLA}.", True)]}}),  # o depois longe
    "siglas de outro texto": documento(secoes={1: {"corpo": [(f"{frase(2)} {S[0]} {frase(2)}.", True),
                                                             (f"{frase(2)} {na_forma(S[1])}.", False)]}}),
    # uma so com o antes e uma so com o depois, nessa ordem
    "siglas de um lado só": documento(secoes={1: {"corpo": [(f"{explicacao()} {ABRE_SIGLA}{S[10]} {frase(1)}.", True),
                                                            (f"{frase(1)} {S[11]}{FECHA_SIGLA} {frase(1)}.", True)]}}),
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

SEM_DIVISORES = grava_esqueleto(ABERTURA_DO_ESQUELETO, TITULOS_DO_ESQUELETO, divisores=False)
confere(roda(CONF, *arquivos.values(), esqueleto=SEM_DIVISORES)[1] == ERROS_DE_TODOS,
        "os divisores do esqueleto não mudam nenhum ERRO")
LITERAL = grava_esqueleto([CASOS["certo"].linhas[0], SUBTITULO], TITULOS)
SEM_LACUNAS = grava_configuracao({k: v for k, v in CONFIGURACAO.items() if k != "lacunas"})
OUTRA = arquivos["título com outra palavra na lacuna"]
TITULO_DA_OUTRA = CASOS["título com outra palavra na lacuna"].linhas.index(SECAO + OUTRO_NA_LACUNA[COM_LACUNA]) + 1
codigo, erros, _, linhas = roda(SEM_LACUNAS, arquivos["certo"], OUTRA, esqueleto=LITERAL)
esperados = sorted([(str(OUTRA), 1), (str(OUTRA), TITULO_DA_OUTRA)])  # a abertura e o titulo, agora sem lacuna
confere(codigo == 1 and sorted(erros) == esperados,
        f"sem lacunas, o esqueleto vale letra por letra: {codigo}, {erros} no lugar de {esperados}")
SO_AS_NOVAS = ("seção que começa fora da forma", "seção só com o fecho", "siglas", "siglas de outro texto",
               "siglas de um lado só")
SEM_AS_NOVAS = grava_configuracao({k: v for k, v in CONFIGURACAO.items() if k not in ("comeco_das_secoes", "siglas")})
codigo, erros, _, linhas = roda(SEM_AS_NOVAS, *(arquivos[nome] for nome in SO_AS_NOVAS))
confere(codigo == 0 and not erros,
        f"sem o começo das seções e sem as siglas, nada deles se confere: {codigo}, {linhas}")

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

ALVO_DO_RODAPE = grava(frase(3), ".txt")
# o rodape, na pasta dos documentos, com o divisor, um padrao proibido e um nome fora do italico
RODAPE = [DIVISOR, "", f"{frase(3)} {PROIBIDO} [{NOME_LONGO}]({ALVO_DO_RODAPE.name}) {frase(2)}."]
MODELO = grava("\n".join(RODAPE) + "\n")


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


def com(*mudancas):
    """Uma copia da configuracao com cada mudanca, um caminho ("a/b") seguido do valor; o valor None tira o campo."""
    dados = json.loads(json.dumps(CONFIGURACAO))
    for caminho, valor in zip(mudancas[::2], mudancas[1::2]):
        alvo, partes = dados, caminho.split("/")
        for parte in partes[:-1]:
            alvo = alvo[parte]
        if valor is None:
            del alvo[partes[-1]]
        else:
            alvo[partes[-1]] = valor
    return grava_configuracao(dados)


SO_O_ANTES_EM, SO_O_DEPOIS_EM = CASOS["siglas de um lado só"].erros  # a linha de cada uma
for tirado, fica_em in (("antes", SO_O_ANTES_EM), ("depois", SO_O_DEPOIS_EM)):
    codigo, erros, _, linhas = roda(com(f"siglas/{tirado}", None), arquivos["siglas de um lado só"])
    confere(codigo == 1 and [linha for _, linha in erros] == [fica_em],
            f"sem o {tirado}, só o outro lado da sigla vale: {codigo}, {linhas}")
TRECHO_E_FECHO = com("siglas/trechos_fora", f"{re.escape(TRECHO)}|{re.escape(FECHA_SIGLA)}")
confere(roda(TRECHO_E_FECHO, arquivos["siglas"])[1] == roda(CONF, arquivos["siglas"])[1],
        "a forma da sigla se confere na linha inteira, também no que é trecho de fora")

LACUNAS = CONFIGURACAO["lacunas"]
ESTRAGADAS = {
    "campo que o molde não conhece": com(palavra(), palavra()),
    "a abertura, que vem do esqueleto": com("abertura", [{"padrao": re.escape(TITULO_DO_DOCUMENTO)}]),
    "os títulos, que vêm do esqueleto": com("titulos", TITULOS),
    "outra versão": com("versao_schema", 1),
    "campo que falta": com("secao", None),
    "seção sem o grupo do título": com("secao", f"^{re.escape(SECAO)}(.+)$"),
    "expressão que não compila": com("divisor", "("),
    "começo das seções que não compila": com("comeco_das_secoes", "("),
    "mínimo maior que o máximo": com("palavras", {"fora_de": FORA, "minimo": 9, "maximo": 1}),
    "mínimo que não é número": com("palavras", {"fora_de": FORA, "minimo": "9", "maximo": 99}),
    "marca vazia": com("italico/marcas", [""]),
    "padrões proibidos, que vão em arquivo próprio": com("proibidos", [REGRA]),
    "lacuna sem marca": com("lacunas", [{"padrao": LACUNAS[0]["padrao"]}] + LACUNAS[1:]),
    "lacuna com marca sem letra": com("lacunas", [dict(LACUNAS[0], marca=" ")] + LACUNAS[1:]),
    "duas lacunas com a mesma marca": com("lacunas", LACUNAS + [dict(LACUNAS[0], padrao=palavra())]),
    "lacuna que não compila": com("lacunas", [dict(LACUNAS[0], padrao="(")] + LACUNAS[1:]),
    "siglas sem um campo": com("siglas/fora_de", None),
    "siglas sem o antes nem o depois": com("siglas/antes", None, "siglas/depois", None),
    "siglas com campo que o molde não conhece": com(f"siglas/{palavra()}", palavra()),
    "padrão das siglas que não compila": com("siglas/padrao", "("),
    "antes das siglas que não compila": com("siglas/antes", "["),
    "depois das siglas que não compila": com("siglas/depois", "["),
    "trechos de fora das siglas que não compilam": com("siglas/trechos_fora", "["),
    "padrão das siglas que casa com o vazio": com("siglas/padrao", f"[{MAIUSCULAS}]*"),
    "antes das siglas que casa com o vazio": com("siglas/antes", f"{re.escape(ABRE_SIGLA)}?"),
    "depois das siglas que casa com o vazio": com("siglas/depois", f"{re.escape(FECHA_SIGLA)}?"),
    "trechos de fora das siglas que casam com o vazio": com("siglas/trechos_fora", f"(?:{re.escape(TRECHO)})?"),
}
for nome, caminho in ESTRAGADAS.items():
    codigo, erros, _, linhas = roda(caminho, arquivos["certo"])
    confere(codigo == 2 and not erros, f"configuração com {nome} sai com 2, sem conferir: {codigo}, {linhas}")
LATIN = TRABALHO / f"{palavra()}.md"
LATIN.write_bytes(ESQUELETO.read_text(encoding="utf-8").encode("latin-1", errors="replace") + b"\xe9\xff")
DUAS_VEZES = grava_esqueleto([f"{ABERTURA_DO_ESQUELETO[0]} {LACUNA_DA_ABERTURA}", SUBTITULO], TITULOS_DO_ESQUELETO)
ESQUELETOS_QUE_NAO_SERVEM = {
    "que não existe": (CONF, TRABALHO / f"{palavra()}.md"),
    "que não se lê em UTF-8": (CONF, LATIN),
    "com uma linha que não é da abertura, de seção nem divisor":
        (CONF, grava_esqueleto(ABERTURA_DO_ESQUELETO, TITULOS_DO_ESQUELETO, depois=[frase(3)])),
    "sem uma lacuna da configuração": (com("lacunas", LACUNAS + [{"marca": f"{{{palavra()}}}", "padrao": "x"}]),
                                       ESQUELETO),
    # o grupo de nome da lacuna, duas vezes na mesma linha, nao compila
    "com uma linha que, com as lacunas, não compila": (com("lacunas", [dict(LACUNAS[0], padrao="(?P<g>[a-z]+)")]
                                                           + LACUNAS[1:]), DUAS_VEZES),
}
for nome, (configuracao, esqueleto) in ESQUELETOS_QUE_NAO_SERVEM.items():
    codigo, erros, _, linhas = roda(configuracao, arquivos["certo"], esqueleto=esqueleto)
    confere(codigo == 2 and not erros and str(esqueleto) in "\n".join(linhas),
            f"o esqueleto {nome} sai com 2, sem conferir, e o erro diz o arquivo: {codigo}, {linhas}")
NAO_E_JSON = grava("{" + palavra(), ".json")
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
ILEGIVEL = TRABALHO / f"{palavra()}.md"
ILEGIVEL.write_bytes(arquivos["certo"].read_text(encoding="utf-8").encode("latin-1", errors="replace") + b"\xe9\xff")
codigo, erros, _, _ = roda(CONF, ILEGIVEL)
confere(codigo == 2 and not erros, f"texto que não se lê em UTF-8 sai com 2: {codigo}")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
