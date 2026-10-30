"""Gancho para as regras de código.

Um só programa para os eventos ligados a ele; o evento vem no JSON que o programa que roda o
gancho manda pela entrada padrão.

- Antes de uma chamada de ferramenta que escreve arquivo: anota o arquivo; no
  primeiro arquivo da tarefa, entrega as regras antes da escrita. O arquivo de
  um formato da lista sem_conferencia (a extensao, sem contar maiusculas), como
  um texto ou uma planilha, fica de fora; os outros, sem extensao ou de
  extensao que a lista nao traz, entram.
- Antes de uma chamada do terminal: bloqueia o comando que escreve em arquivo,
  roda código escrito dentro dele ou não pode ser lido.
- No fim de uma resposta: com arquivos anotados, trava o encerramento e pede a
  conferência; na volta da conferência, libera. Nos dois casos a anotação é
  apagada.

As listas e a pasta da anotação vêm da configuração (--config), conferida contra
o molde dela; os textos, dos arquivos dados no comando: as regras (--regras), a
ordem de conferir (--fim) e o aviso do bloqueio (--bloqueio). O evento, as
ferramentas e as respostas vêm do protocolo do programa (--protocolo), lido pelo
protocolo.py, da pasta irmã protocolo. O comando de terminal é lido pelo
leitura_do_terminal.py, da pasta irmã leitura-do-terminal. Só biblioteca padrão.
"""
import argparse
import json
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "leitura-do-terminal", PASTA.parent / "protocolo"):  # as pastas irmas
    sys.path.insert(0, str(pasta))
from leitura_do_terminal import (DUPLICACAO, ESCRITA, FECHA_DESCRITOR, OPCAO, TEXTO_EMBUTIDO,  # noqa: E402
                                 ComandoIlegivel, eh_redirecionamento, lidos, opcao_bate, posicoes_de_comando)
import protocolo  # noqa: E402

MOLDE = PASTA / "esquemas" / "regras-de-codigo.schema.json"
CODIFICACAO = "utf-8"

# Partes do JSON Schema que a conferência entende.
TIPOS = {"object": dict, "array": list, "string": str, "integer": int}
REFERENCIA = "$ref"
REFERENCIA_LOCAL = "#/"
SEPARADOR_DE_CAMINHO = "/"

# Textos.
QUEBRA = "\n"
ITEM_DE_LISTA = "- "
SEPARADOR_DE_TEXTOS = QUEBRA * 2


class ForaDoMolde(ValueError):
    """Dado que o molde não aceita; a mensagem diz onde e o quê."""


def resolver(molde, raiz):
    while REFERENCIA in molde:
        alvo = raiz
        for parte in molde[REFERENCIA][len(REFERENCIA_LOCAL):].split(SEPARADOR_DE_CAMINHO):
            alvo = alvo[parte]
        molde = alvo
    return molde


def conferir_forma(dados, molde, raiz, onde=SEPARADOR_DE_CAMINHO):
    """Erro no primeiro dado fora do molde: tipo, valor fixo, tamanho mínimo, campo que falta
    ou que o molde não conhece."""
    molde = resolver(molde, raiz)
    tipo = molde.get("type")
    if tipo is not None and not isinstance(dados, TIPOS[tipo]):
        raise ForaDoMolde(f"{onde}: {tipo}")
    if "const" in molde and dados != molde["const"]:
        raise ForaDoMolde(f"{onde}: {molde['const']!r}")
    minimo = molde.get("minLength", molde.get("minItems", 0))
    if isinstance(dados, (str, list)) and len(dados) < minimo:
        raise ForaDoMolde(f"{onde}: vazio")
    if isinstance(dados, list):
        for numero, item in enumerate(dados):
            conferir_forma(item, molde.get("items", {}), raiz, f"{onde}{numero}{SEPARADOR_DE_CAMINHO}")
    if isinstance(dados, dict):
        faltam = [campo for campo in molde.get("required", []) if campo not in dados]
        if faltam:
            raise ForaDoMolde(f"{onde}: faltam {faltam}")
        campos, outros = molde.get("properties", {}), molde.get("additionalProperties", True)
        for chave, valor in dados.items():
            dentro = f"{onde}{chave}{SEPARADOR_DE_CAMINHO}"
            if chave in campos:
                conferir_forma(valor, campos[chave], raiz, dentro)
            elif outros is False:
                raise ForaDoMolde(f"{onde}{chave}: campo desconhecido")
            elif isinstance(outros, dict):
                conferir_forma(valor, outros, raiz, dentro)


def ler_json(caminho):
    return json.loads(Path(caminho).read_text(encoding=CODIFICACAO))


def ler_configuracao(caminho):
    arquivo = Path(caminho).resolve()
    dados = ler_json(arquivo)
    molde = ler_json(MOLDE)
    conferir_forma(dados, molde, molde)
    terminal = dados["terminal"]
    return {
        "estado": arquivo.parent / dados["estado"],
        "sem_conferencia": {formato.casefold() for formato in dados["sem_conferencia"]},
        "terminal": {
            "destinos_livres": set(terminal["destinos_livres"]),
            "prefixos": set(terminal["prefixos"]),
            "sempre_escrevem": set(terminal["sempre_escrevem"]),
            "escrevem_com_opcao": {
                nome: list(opcoes) for nome, opcoes in terminal["escrevem_com_opcao"].items()
            },
            "leem_codigo_sem_arquivo": set(terminal["leem_codigo_sem_arquivo"]),
        },
    }


def juntar(caminhos):
    return SEPARADOR_DE_TEXTOS.join(Path(c).read_text(encoding=CODIFICACAO).strip() for c in caminhos)


def arquivo_da_anotacao(config, sessao):
    if not isinstance(sessao, str) or not sessao or Path(sessao).name != sessao or sessao.startswith("."):
        raise ValueError(sessao)
    return config["estado"] / sessao


# ---- análise do comando de terminal ----

def destino_livre(terminal, operador, destino):
    if destino is None or destino[1]:
        return False
    alvo = destino[0]
    if operador.endswith(DUPLICACAO) and (alvo.isdigit() or alvo == FECHA_DESCRITOR):
        return True
    return alvo in terminal["destinos_livres"]


def redirecionamento_que_escreve(terminal, partes):
    for numero, (texto, operador) in enumerate(partes):
        if not operador:
            continue
        if TEXTO_EMBUTIDO in texto:
            return texto
        if ESCRITA in texto and eh_redirecionamento(texto):
            destino = partes[numero + 1] if numero + 1 < len(partes) else None
            if not destino_livre(terminal, texto, destino):
                return " ".join([texto] + ([destino[0]] if destino else []))
    return None


def comando_que_escreve(terminal, palavras):
    for posicao in posicoes_de_comando(palavras, terminal["prefixos"]):
        nome = Path(palavras[posicao]).name
        seguintes = palavras[posicao + 1:]
        if nome in terminal["sempre_escrevem"]:
            return nome
        for opcao in terminal["escrevem_com_opcao"].get(nome, []):
            for palavra in seguintes:
                if opcao_bate(opcao, palavra):
                    return f"{nome} {palavra}"
        sem_arquivo = all(palavra.startswith(OPCAO) for palavra in seguintes)
        if nome in terminal["leem_codigo_sem_arquivo"] and sem_arquivo:
            return nome
    return None


def parte_que_escreve(terminal, comando):
    """Primeira parte do comando, ou de um comando de dentro dele, que escreve em arquivo ou roda código escrito
    nele; None se não há."""
    for partes, simples in lidos(comando):
        achado = redirecionamento_que_escreve(terminal, partes)
        for palavras in simples:
            achado = achado or comando_que_escreve(terminal, palavras)
        if achado:
            return achado
    return None


# ---- eventos ----

def antes_do_terminal(config, proto, entrada):
    try:
        parte = parte_que_escreve(config["terminal"], entrada[proto["terminal"]["campo_comando"]])
    except ComandoIlegivel as erro:
        parte = str(erro)
    if parte is None:
        return None
    motivo = juntar([config["bloqueio"]]) + QUEBRA + parte
    return protocolo.resposta(proto, "nega", motivo)


def antes_da_escrita(config, proto, entrada, anotacao):
    campos = [campo for campo in proto["escritas"]["campos_caminho"] if campo in entrada]
    if not campos:
        raise KeyError(proto["escritas"]["campos_caminho"])
    if Path(entrada[campos[0]]).suffix.casefold() in config["sem_conferencia"]:
        return None
    primeira = not anotacao.exists()
    anotacao.parent.mkdir(parents=True, exist_ok=True)
    with anotacao.open("a", encoding=CODIFICACAO) as arquivo:
        arquivo.write(entrada[campos[0]] + QUEBRA)
    if not primeira:
        return None
    return protocolo.resposta(proto, "contexto", juntar(config["regras"]))


def antes(config, proto, partes, anotacao):
    if partes["ferramenta"] == proto["terminal"]["ferramenta"]:
        return antes_do_terminal(config, proto, partes["entrada"])
    return antes_da_escrita(config, proto, partes["entrada"], anotacao)


def no_fim(config, proto, partes, anotacao):
    if not anotacao.exists():
        return None
    caminhos = list(dict.fromkeys(anotacao.read_text(encoding=CODIFICACAO).splitlines()))
    anotacao.unlink()
    if partes.get("fim_repetido"):
        return None
    lista = QUEBRA.join(ITEM_DE_LISTA + caminho for caminho in caminhos)
    motivo = juntar(config["regras"] + [config["fim"]]) + QUEBRA + lista
    return protocolo.resposta(proto, "trava", motivo)


TRATADORES = {"antes": antes, "fim": no_fim}  # pelo nome que o protocolo.py dá a cada evento


def main(argumentos=None):
    leitor = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    leitor.add_argument("--config", required=True, type=Path, help="JSON com as listas e a pasta da anotação")
    leitor.add_argument("--protocolo", required=True, type=Path,
                        help="JSON com o protocolo do programa que roda o gancho")
    leitor.add_argument("--regras", action="append", required=True, type=Path,
                        help="texto de regras, na ordem em que são entregues (pode repetir)")
    leitor.add_argument("--fim", required=True, type=Path, help="texto da ordem de conferir")
    leitor.add_argument("--bloqueio", required=True, type=Path, help="texto do bloqueio no terminal")
    args = leitor.parse_args(argumentos)
    config = dict(ler_configuracao(args.config), regras=list(args.regras), fim=args.fim, bloqueio=args.bloqueio)
    proto = protocolo.ler(args.protocolo)
    partes = protocolo.le_evento(proto, sys.stdin.read())
    anotacao = arquivo_da_anotacao(config, partes["sessao"])
    saida = TRATADORES[partes["evento"]](config, proto, partes, anotacao)
    if saida is not None:
        print(json.dumps(saida, ensure_ascii=False))


if __name__ == "__main__":
    main()
