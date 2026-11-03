"""Testes do rodape_comum.py, com modelos, documentos e textos inventados aqui, sorteados e com
letras de fora do ASCII. Conferem regras, nunca uma frase pronta: sem arquivo, nao ha modelo;
no rodape de um documento, o alvo de cada link para um arquivo (tambem o da imagem, o com
ancora e o com espaco no nome, escrito entre < e > ou codificado) e o caminho do arquivo a
partir da pasta do documento, entre < e > quando tem espaco ou parenteses, com a ancora, e o
resto do modelo, o link externo e o so de ancora ficam como estao, sem os espacos e as quebras
das pontas do arquivo; o texto com o rodape e o texto sem os espacos e as quebras do fim, uma
linha em branco, o rodape e uma quebra, so o rodape sem texto, e o texto como vem sem modelo;
o rodape no fim de um texto se acha tambem com outro alvo nos links, com outros espacos e
quebras onde o modelo tem um e com espacos e quebras depois dele, e o corpo e o texto de antes
dele, sem os espacos e as quebras do fim, com uma quebra, e a linha e a do comeco dele; nao se
acha o rodape que nao esta no fim, o de outro texto, o colado a uma linha nem o de outro
modelo; o texto com o rodape volta a ele mesmo; o modelo que falta, que nao se le em UTF-8,
vazio, com codigo na linha ou em bloco, ou com link para um arquivo que nao existe e erro
(ErroDeDados) que diz o arquivo; duas leituras dao o mesmo; a opcao --rodape da o caminho do
modelo, nenhum sem ela, e a ajuda dada aparece na ajuda do script. Uso:
    python3 -I teste_rodape_comum.py <pasta do rodape_comum.py> <pasta de trabalho nova>
Precisa do extrator_comum.py e do markdown_comum.py, nas pastas irmas "extrator" e
"documentos" da peca.
"""
import argparse
import os
import random
import string
import sys
from pathlib import Path
from urllib.parse import quote

PECA, TRABALHO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
sys.path.insert(0, str(PECA))
from rodape_comum import com_rodape, le_modelo, opcao_rodape, rodape, separa  # noqa: E402
from extrator_comum import ErroDeDados  # noqa: E402  (achado na pasta irma pelo rodape_comum)

FALHAS = []
SORTEIO = random.Random(5)
LETRAS = string.ascii_letters + "áçõüéñ"


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


def palavra():
    return "".join(SORTEIO.choice(LETRAS) for _ in range(SORTEIO.randint(3, 7)))


def frase(n=None):
    return " ".join(palavra() for _ in range(n or SORTEIO.randint(2, 5)))


def erro(funcao, *argumentos):
    """A mensagem do ErroDeDados que a funcao da, ou None quando ela nao da erro."""
    try:
        funcao(*argumentos)
    except ErroDeDados as e:
        return str(e)
    return None


def relativo(arquivo, documento):
    """O caminho do arquivo a partir da pasta do documento, como o teste o calcula."""
    return Path(os.path.relpath(arquivo, Path(documento).parent)).as_posix()


TRABALHO.mkdir(parents=True)
DADOS = TRABALHO / palavra() / palavra()
DADOS.mkdir(parents=True)
LICENCA, IMAGEM = TRABALHO / f"{palavra()}.txt", DADOS / f"{palavra()}.png"
COM_ESPACO = TRABALHO / f"{palavra()} {palavra()}" / f"{palavra()}.md"
COM_ESPACO.parent.mkdir()
for arquivo in (LICENCA, IMAGEM, COM_ESPACO):
    arquivo.write_text(frase(), encoding="utf-8")
ANCORA, EXTERNO, PROPRIA = palavra().lower(), f"https://{palavra()}.org/{palavra()}", f"#{palavra().lower()}"
ALVOS_DO_MODELO = [os.path.relpath(LICENCA, DADOS), IMAGEM.name,
                   f"<{os.path.relpath(COM_ESPACO, DADOS)}#{ANCORA}>", quote(os.path.relpath(COM_ESPACO, DADOS))]
LINHAS_DO_MODELO = ["---", "", f"*{frase()} [{frase()}]({ALVOS_DO_MODELO[0]}).*",
                    f"{frase()} ![{palavra()}]({ALVOS_DO_MODELO[1]}) {frase()} [{palavra()}]({EXTERNO})",
                    f"[{palavra()}]({ALVOS_DO_MODELO[2]}) {frase()} [{palavra()}]({PROPRIA}) e "
                    f"[{palavra()}]({ALVOS_DO_MODELO[3]} \"{palavra()}\")"]
TEXTO_DO_MODELO = "\n".join(LINHAS_DO_MODELO)
CAMINHO_DO_MODELO = DADOS / f"{palavra()}.md"
CAMINHO_DO_MODELO.write_text(f"\n  \n{TEXTO_DO_MODELO}  \n\n\n", encoding="utf-8")
MODELO = le_modelo(CAMINHO_DO_MODELO)
confere(le_modelo(None) is None, "sem arquivo, não há modelo")


def esperado(documento):
    """O rodape do documento, como o teste o calcula: cada alvo de arquivo a partir da pasta do documento."""
    certos = [relativo(LICENCA, documento), relativo(IMAGEM, documento),
              f"<{relativo(COM_ESPACO, documento)}#{ANCORA}>" if " " in relativo(COM_ESPACO, documento)
              else f"{relativo(COM_ESPACO, documento)}#{ANCORA}", None]
    certos[3] = certos[2].replace(f"#{ANCORA}", "")
    texto = TEXTO_DO_MODELO
    for antes, depois in zip(ALVOS_DO_MODELO, certos):
        texto = texto.replace(f"({antes}", f"({depois}", 1)
    return texto


DOCUMENTOS = [TRABALHO / f"{palavra()}.md", DADOS / f"{palavra()}.md", COM_ESPACO.parent / f"{palavra()}.md",
              TRABALHO / palavra() / palavra() / palavra() / f"{palavra()}.md"]
for documento in DOCUMENTOS:
    achado = rodape(MODELO, documento)
    confere(achado == esperado(documento), f"o rodapé de {documento}: cada link para um arquivo a partir da pasta do "
                                           f"documento, e o resto como vem: {achado!r} no lugar de "
                                           f"{esperado(documento)!r}")
confere(EXTERNO in rodape(MODELO, DOCUMENTOS[0]) and f"({PROPRIA})" in rodape(MODELO, DOCUMENTOS[0]),
        "o link externo e o só de âncora ficam como estão")

CORPO = "\n".join(frase() for _ in range(SORTEIO.randint(3, 6)))
DOCUMENTO = DOCUMENTOS[3]
RODAPE = rodape(MODELO, DOCUMENTO)
COM = com_rodape(f"{CORPO} \t\n\n\n", MODELO, DOCUMENTO)
confere(COM == f"{CORPO}\n\n{RODAPE}\n", f"o texto com o rodapé: o texto sem os espaços e as quebras do fim, uma "
                                         f"linha em branco, o rodapé e uma quebra: {COM!r}")
confere(com_rodape(" \n\n", MODELO, DOCUMENTO) == f"{RODAPE}\n", "sem texto, só o rodapé e a quebra")
confere(com_rodape(f"{CORPO} \n", None, DOCUMENTO) == f"{CORPO} \n", "sem modelo, o texto como vem")
LINHA_DO_RODAPE = CORPO.count("\n") + 3
confere(separa(COM, MODELO) == (f"{CORPO}\n", LINHA_DO_RODAPE),
        f"o rodapé no fim: o corpo, com uma quebra, e a linha do começo dele: {separa(COM, MODELO)!r}")
confere(com_rodape(separa(COM, MODELO)[0], MODELO, DOCUMENTO) == COM, "o texto com o rodapé volta a ele mesmo")

DE_OUTRO = rodape(MODELO, DOCUMENTOS[0])  # com os alvos de outro documento
ESPALHADO = DE_OUTRO.replace(" ", SORTEIO.choice(["  ", " \n", "\t"]), 3).replace("\n\n", "\n \n\n", 1)
for nome, fim in (("com outros alvos", DE_OUTRO), ("com outros espaços e quebras", ESPALHADO),
                  ("com espaços e quebras depois", f"{RODAPE} \n\n \n")):
    texto = f"{CORPO}  \n\n\n{fim}"
    confere(separa(texto, MODELO) == (f"{CORPO}\n", LINHA_DO_RODAPE + 1),
            f"o rodapé {nome} se acha no fim: {separa(texto, MODELO)!r}")
for nome, texto in (("que não está no fim", f"{CORPO}\n\n{RODAPE}\n\n{frase()}\n"),
                    ("de outro texto", f"{CORPO}\n\n{RODAPE.replace(LINHAS_DO_MODELO[3][:4], palavra(), 1)}\n"),
                    ("colado a uma linha", f"{CORPO} {RODAPE}\n"),
                    ("num texto sem ele", CORPO + "\n")):
    confere(separa(texto, MODELO) == (texto, None), f"não se acha o rodapé {nome}: {separa(texto, MODELO)!r}")
confere(separa(COM, None) == (COM, None), "sem modelo, o texto como vem e nenhuma linha")
ENTRE = frase()
DOIS = f"{CORPO}\n\n{RODAPE}\n\n{ENTRE}\n\n{RODAPE}\n"
confere(separa(DOIS, MODELO)[0] == f"{CORPO}\n\n{RODAPE}\n\n{ENTRE}\n", "com dois rodapés, só o do fim sai")
OUTRO_MODELO = DADOS / f"{palavra()}.md"
OUTRO_MODELO.write_text(f"{frase()} [{palavra()}]({ALVOS_DO_MODELO[0]})", encoding="utf-8")
confere(separa(COM, le_modelo(OUTRO_MODELO)) == (COM, None), "não se acha o rodapé de outro modelo")

SUMIDO, LATIN, VAZIO = DADOS / f"{palavra()}.md", DADOS / f"{palavra()}.md", DADOS / f"{palavra()}.md"
LATIN.write_bytes(f"{frase()} ç".encode("latin-1"))
VAZIO.write_text(" \n\t\n", encoding="utf-8")
NA_LINHA, EM_BLOCO, SEM_ARQUIVO = (DADOS / f"{palavra()}.md" for _ in range(3))
NA_LINHA.write_text(f"{frase()} `{palavra()}` {frase()}", encoding="utf-8")
EM_BLOCO.write_text(f"{frase()}\n\n```\n{frase()}\n```\n", encoding="utf-8")
SEM_ARQUIVO.write_text(f"{frase()} [{palavra()}]({palavra()}/{palavra()}.md#{palavra()})", encoding="utf-8")
for nome, caminho in (("que falta", SUMIDO), ("que não se lê em UTF-8", LATIN), ("vazio", VAZIO),
                      ("com código na linha", NA_LINHA), ("com código em bloco", EM_BLOCO),
                      ("com link para um arquivo que não existe", SEM_ARQUIVO)):
    e = erro(le_modelo, caminho)
    confere(e is not None and str(caminho) in e, f"o modelo {nome} é erro que diz o arquivo: {e!r}")
confere(le_modelo(CAMINHO_DO_MODELO) == MODELO and rodape(le_modelo(CAMINHO_DO_MODELO), DOCUMENTO) == RODAPE,
        "duas leituras dão o mesmo")

LEITOR, AJUDA = argparse.ArgumentParser(), frase()
opcao_rodape(LEITOR, AJUDA)
confere(LEITOR.parse_args(["--rodape", str(CAMINHO_DO_MODELO)]).rodape == CAMINHO_DO_MODELO
        and LEITOR.parse_args([]).rodape is None, "a opção do modelo dá o caminho dele, e sem ela não há caminho")
confere(AJUDA in " ".join(LEITOR.format_help().split()), "a ajuda dada aparece na ajuda do script")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
