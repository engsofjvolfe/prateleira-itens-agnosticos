"""Le um comando de terminal como o shell le, para o programa que precisa saber o que ele roda.

Divide o comando em palavras e operadores, respeitando aspas, escapes e comentarios;
separa os comandos simples, sem os alvos de redirecionamento; acha as palavras que o shell
roda como comando (a primeira e as que vem depois de um prefixo, como xargs); confere se
uma opcao de linha de comando aparece numa palavra (a curta tambem junto de outras, a longa
tambem com =valor); e da o comando e cada comando de dentro dele, de $( ) e de crases,
tambem entre aspas, um depois do outro. Comando com aspas, crase ou substituicao sem
fechar e ComandoIlegivel.

Nao se roda: e importado. So biblioteca padrao.
"""
from pathlib import Path

# Gramatica do shell.
PONTUACAO = "();<>|&\n"
ESCRITA = ">"
LEITURA = "<"
TEXTO_EMBUTIDO = "<<"
ABRE = "("
FECHA = ")"
DUPLICACAO = "&"
FECHA_DESCRITOR = "-"
SUBSTITUICAO = "$("
CRASE = "`"
ASPA_SIMPLES = "'"
ASPA_DUPLA = '"'
ESCAPE = "\\"
COMENTARIO = "#"
QUEBRA = "\n"
ATRIBUICAO = "="
OPCAO = "-"
OPCAO_LONGA = "--"


class ComandoIlegivel(ValueError):
    """Aspas, crase ou substituição sem fechar."""


def fim_do_par(comando, inicio, sinal):
    """Posição do sinal que fecha o par aberto logo antes de inicio."""
    fim = comando.find(sinal, inicio)
    if fim < 0:
        raise ComandoIlegivel(sinal)
    return fim


def ler_substituicao(comando, inicio):
    """Lê de inicio (logo depois de '$(') até o ')' que fecha; devolve (posição seguinte, conteúdo)."""
    nivel, i = 1, inicio
    while i < len(comando):
        c = comando[i]
        if c == ESCAPE:
            i += 2
        elif c == ASPA_SIMPLES:
            i = fim_do_par(comando, i + 1, ASPA_SIMPLES) + 1
        elif c == ASPA_DUPLA:
            i, _, _ = ler_aspas_duplas(comando, i + 1)
        elif c == ABRE:
            nivel, i = nivel + 1, i + 1
        elif c == FECHA:
            nivel -= 1
            if nivel == 0:
                return i + 1, comando[inicio:i]
            i += 1
        else:
            i += 1
    raise ComandoIlegivel(SUBSTITUICAO)


def ler_aspas_duplas(comando, inicio):
    """Lê de inicio (logo depois da aspa) até a aspa que fecha; devolve (posição seguinte, texto, comandos internos)."""
    texto, internos, i = [], [], inicio
    while i < len(comando):
        c = comando[i]
        if c == ASPA_DUPLA:
            return i + 1, "".join(texto), internos
        if c == ESCAPE and i + 1 < len(comando):
            texto.append(comando[i + 1])
            i += 2
        elif comando.startswith(SUBSTITUICAO, i):
            i, interno = ler_substituicao(comando, i + len(SUBSTITUICAO))
            internos.append(interno)
        elif c == CRASE:
            fim = fim_do_par(comando, i + 1, CRASE)
            internos.append(comando[i + 1:fim])
            i = fim + 1
        else:
            texto.append(c)
            i += 1
    raise ComandoIlegivel(ASPA_DUPLA)


def separar(comando):
    """Divide o comando como o shell divide.

    Devolve (partes, internos): cada parte é (texto, é_operador), e operador só
    existe fora de aspas; internos são os comandos de substituições e crases
    que ficam dentro de aspas ou de crases.
    """
    partes, internos = [], []
    palavra, i = None, 0

    def fechar():
        nonlocal palavra
        if palavra is not None:
            partes.append(("".join(palavra), False))
            palavra = None

    while i < len(comando):
        c = comando[i]
        if c in PONTUACAO:
            fechar()
            fim = i
            while fim < len(comando) and comando[fim] in PONTUACAO:
                fim += 1
            partes.append((comando[i:fim], True))
            i = fim
        elif c.isspace():
            fechar()
            i += 1
        elif c == ESCAPE and comando.startswith(QUEBRA, i + 1):
            i += 2
        elif c == COMENTARIO and palavra is None:
            fim = comando.find(QUEBRA, i)
            i = len(comando) if fim < 0 else fim
        else:
            if palavra is None:
                palavra = []
            if c == ESCAPE:
                palavra.append(comando[i + 1:i + 2])
                i += 2
            elif c == ASPA_SIMPLES:
                fim = fim_do_par(comando, i + 1, ASPA_SIMPLES)
                palavra.append(comando[i + 1:fim])
                i = fim + 1
            elif c == ASPA_DUPLA:
                i, texto, novos = ler_aspas_duplas(comando, i + 1)
                palavra.append(texto)
                internos.extend(novos)
            elif c == CRASE:
                fim = fim_do_par(comando, i + 1, CRASE)
                internos.append(comando[i + 1:fim])
                i = fim + 1
            else:
                palavra.append(c)
                i += 1
    fechar()
    return partes, internos


def eh_redirecionamento(operador):
    return (ESCRITA in operador or LEITURA in operador) and ABRE not in operador


def comandos_simples(partes):
    """Palavras de cada comando simples, sem operadores e sem alvos de redirecionamento."""
    palavras, pular = [], False
    for texto, operador in partes:
        if operador:
            if eh_redirecionamento(texto):
                pular = True
                continue
            if palavras:
                yield palavras
            palavras, pular = [], False
        elif pular:
            pular = False
        else:
            palavras.append(texto)
    if palavras:
        yield palavras


def lidos(comando):
    """(partes, [palavras de cada comando simples]) do comando e, depois, de cada comando de dentro dele, na ordem,
    cada um seguido dos de dentro dele; ComandoIlegivel quando um deles nao se le."""
    partes, internos = separar(comando)
    yield partes, list(comandos_simples(partes))
    for interno in internos:
        yield from lidos(interno)


def eh_atribuicao(palavra):
    nome, sinal, _ = palavra.partition(ATRIBUICAO)
    return bool(sinal) and nome.isidentifier()


def posicoes_de_comando(palavras, prefixos):
    """Posições das palavras que o shell roda como comando: a primeira e todas depois de um prefixo."""
    posicoes, primeira, depois_de_prefixo = [], True, False
    for numero, palavra in enumerate(palavras):
        if primeira and eh_atribuicao(palavra):
            continue
        if primeira or depois_de_prefixo:
            posicoes.append(numero)
        primeira = False
        depois_de_prefixo = depois_de_prefixo or Path(palavra).name in prefixos
    return posicoes


def letras_iniciais(texto):
    fim = 0
    while fim < len(texto) and texto[fim].isalpha():
        fim += 1
    return texto[:fim]


def opcao_bate(opcao, palavra):
    if palavra == opcao:
        return True
    if opcao.startswith(OPCAO_LONGA):
        return palavra.startswith(opcao + ATRIBUICAO)
    curta = len(opcao) == len(OPCAO) + 1 and opcao.startswith(OPCAO)
    agrupada = palavra.startswith(OPCAO) and not palavra.startswith(OPCAO_LONGA)
    return curta and agrupada and opcao[len(OPCAO):] in letras_iniciais(palavra[len(OPCAO):])
