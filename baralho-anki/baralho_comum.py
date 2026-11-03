"""
O que os scripts do baralho-anki fazem do mesmo jeito, num lugar so: ler a configuracao pelo
molde dela, ler a primeira tabela Markdown de um arquivo, achar o arquivo de uma fonte nas
pastas dadas, em ordem, passar um texto para a forma em que os trechos se comparam, dar o
identificador de um nome, montar as linhas do CSV que a tabela da, ler e gravar o CSV e rodar
o trabalho de um script, com o erro numa linha so e o codigo 2.

Nao se roda: os scripts desta pasta o importam. Usa so a biblioteca padrao, o
extrator_comum.py e o texto_comum.py, da peca extrator, e o markdown_comum.py, da peca
documentos, nas pastas irmas ou na mesma pasta.
"""
import csv
import io
import re
import sys
import unicodedata
from pathlib import Path, PurePath

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "extrator", PASTA.parent / "documentos", PASTA):  # na prateleira, as pastas irmas
    sys.path.insert(0, str(pasta))
from extrator_comum import ErroDeDados, le_conferido, le_texto, repetidos  # noqa: E402
from markdown_comum import linhas_fora_de_codigo  # noqa: E402
from texto_comum import espacos_juntos, nfc  # noqa: E402

MOLDE = PASTA / "esquemas" / "baralho-anki.schema.json"  # o molde da configuracao
# as colunas do CSV, na ordem
COLUNAS = ("id", "assunto", "coluna", "pergunta", "resposta", "palavras_chave", "trecho", "fonte")
DA_FONTE = ("pergunta", "resposta", "trecho")  # as que se escrevem pelo texto da fonte
DA_TABELA = tuple(c for c in COLUNAS if c not in DA_FONTE)  # as que saem da tabela
FIM_DE_LINHA = "\n"  # o fim de cada linha do CSV
JUNTA = "-"  # entre as partes de um identificador
CELULA = "|"  # o comeco de uma linha de tabela Markdown e o divisor das celulas dela
PARTE = re.compile(r"[a-z0-9]+")  # as partes de um identificador


def roda(trabalho, argumentos):
    """O codigo de saida do trabalho, chamado com os argumentos; o erro de dados, de leitura, de
    gravacao ou de forma sai numa linha "ERRO: motivo", com o codigo 2."""
    try:
        return trabalho(argumentos)
    except (ErroDeDados, OSError, ValueError, csv.Error) as e:
        print(f"ERRO: {e}")
        return 2


def identificador(texto):
    """O texto em minusculas, sem acento, com as partes de letras e numeros ligadas pela junta:
    "Onde / Status" da "onde-status"."""
    sem_acento = "".join(c for c in unicodedata.normalize("NFD", texto) if not unicodedata.combining(c))
    return JUNTA.join(PARTE.findall(sem_acento.lower()))


def le_configuracao(caminho):
    """A configuracao, conferida contra o molde dela; o que o molde nao ve (a coluna de cada
    campo, os nomes de campo repetidos, as colunas de cartao que dao o mesmo identificador e as
    marcas de enfase repetidas) se confere aqui, e o erro diz o arquivo."""
    conf = le_conferido(caminho, MOLDE)
    campos = conf["nota"]["campos"]
    fora = [c["coluna"] for c in campos if c["coluna"] not in COLUNAS]
    problemas = [f"coluna(s) de campo que o CSV não tem: {fora}"] if fora else []
    cartoes = [identificador(c) for c in conf["tabela"]["cartoes"]]
    for o_que, valores in (("nome(s) de campo", [c["nome"] for c in campos]),
                           ("identificador(es) de coluna de cartão", cartoes),
                           ("marca(s) de ênfase", [e["marca"] for e in conf["enfases"]])):
        mesmos = repetidos(valores)
        if mesmos:
            problemas.append(f"{o_que} repetido(s): {mesmos}")
    if problemas:
        raise ErroDeDados(f"{caminho}: {'; '.join(problemas)}")
    return conf


def celulas(linha):
    """As celulas de uma linha de tabela Markdown, sem os espacos das pontas."""
    return [c.strip() for c in linha.strip().strip(CELULA).split(CELULA)]


def primeira_tabela(texto):
    """As linhas da primeira tabela Markdown do texto, fora dos blocos de codigo: a primeira
    linha que comeca pelo divisor das celulas e as seguidas a ela que tambem comecam por ele."""
    linhas, ultima = [], None
    for numero, linha in linhas_fora_de_codigo(texto):
        if linha.startswith(CELULA) and (ultima is None or numero == ultima + 1):
            linhas.append(linha)
            ultima = numero
    return linhas


def tabela(caminho, conf):
    """[{coluna: celula}] das linhas da primeira tabela Markdown do arquivo: a primeira linha e
    o cabecalho, a segunda e o separador, e as outras sao as linhas. O arquivo sem tabela com
    linhas, a linha com outro numero de celulas e a coluna da configuracao (o assunto, a fonte e
    as colunas de cartao) que o cabecalho nao tem sao erro, que diz o arquivo."""
    linhas = primeira_tabela(le_texto(caminho))
    if len(linhas) < 3:
        raise ErroDeDados(f"{caminho}: o texto não tem tabela com linhas")
    cabecalho, saida = celulas(linhas[0]), []
    for linha in linhas[2:]:
        valores = celulas(linha)
        if len(valores) != len(cabecalho):
            raise ErroDeDados(f"{caminho}: linha da tabela com {len(valores)} célula(s), "
                              f"e não {len(cabecalho)}: {linha}")
        saida.append(dict(zip(cabecalho, valores)))
    t = conf["tabela"]
    faltam = [c for c in (t["assunto"], t["fonte"], *t["cartoes"]) if c not in cabecalho]
    if faltam:
        raise ErroDeDados(f"{caminho}: a tabela não tem a(s) coluna(s): {faltam}")
    return saida


def acha(nome, pastas):
    """O arquivo de nome dado na primeira das pastas que o tem, na ordem delas; None quando
    nenhuma o tem."""
    return next((Path(p) / nome for p in pastas if (Path(p) / nome).is_file()), None)


def normaliza(texto, marcas):
    """O texto na forma em que os trechos se comparam: na forma NFC, sem as marcas dadas (as
    mais longas primeiro) e com os espacos juntados."""
    texto = nfc(texto)
    for marca in sorted(marcas, key=len, reverse=True):
        texto = texto.replace(marca, "")
    return espacos_juntos(texto)


def nome_da_fonte(fonte):
    """O nome do arquivo da fonte, sem a extensao."""
    return PurePath(fonte).stem


def linhas_esperadas(caminho_da_tabela, conf):
    """As linhas do CSV que a tabela do arquivo da: uma por linha da tabela e por coluna de
    cartao, na ordem da tabela e, dentro dela, na das colunas de cartao, com as colunas que se
    escrevem pelo texto da fonte vazias."""
    t = conf["tabela"]
    return [{"id": JUNTA.join((nome_da_fonte(linha[t["fonte"]]), identificador(coluna))),
             "assunto": linha[t["assunto"]], "coluna": coluna, "palavras_chave": linha[coluna],
             "fonte": linha[t["fonte"]], **dict.fromkeys(DA_FONTE, "")}
            for linha in tabela(caminho_da_tabela, conf) for coluna in t["cartoes"]]


def le_csv(caminho):
    """[(numero da linha, {coluna: valor})] de um CSV do baralho, em UTF-8. O cabecalho que nao
    e o das colunas do CSV e a linha com outro numero de campos sao erro, que diz o arquivo e a
    linha."""
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        if next(leitor, None) != list(COLUNAS):
            raise ErroDeDados(f"{caminho}:1: o cabeçalho não é {','.join(COLUNAS)}")
        linhas = []
        for valores in leitor:
            if len(valores) != len(COLUNAS):
                raise ErroDeDados(f"{caminho}:{leitor.line_num}: {len(valores)} campo(s), e não {len(COLUNAS)}")
            linhas.append((leitor.line_num, dict(zip(COLUNAS, valores))))
    return linhas


def grava_csv(caminho, linhas):
    """Grava as linhas no CSV, em UTF-8, com o cabecalho e as aspas do padrao do modulo csv; o
    texto se monta inteiro antes de ir para o arquivo."""
    texto = io.StringIO()
    escritor = csv.DictWriter(texto, fieldnames=COLUNAS, lineterminator=FIM_DE_LINHA)
    escritor.writeheader()
    escritor.writerows(linhas)
    Path(caminho).write_text(texto.getvalue(), encoding="utf-8", newline="")
