"""
Grava um documento gerado a partir de dados, ou confere que o documento gravado esta em dia.

Um script que gera um documento (um glossario, uma lista, um indice, a copia de um
arquivo) poe no leitor de argumentos dele a opcao --conferir (opcao_conferir), que liga
"conferir" nos argumentos lidos, e, no fim, chama grava_ou_confere com o arquivo, o texto
gerado agora, se e para conferir e as tres mensagens dele:

- sem conferir, grava o texto no arquivo, em UTF-8, criando as pastas que faltam, mostra a
  mensagem de gravado e devolve 0;
- conferindo, nada e gravado: com o arquivo igual ao texto, mostra a mensagem de em dia e
  devolve 0; com o arquivo diferente, ou sem ele, mostra a de falta e devolve 1.

O que grava_ou_confere devolve e o codigo de saida do script. Nao se roda: e importado. So
biblioteca padrao.
"""

from pathlib import Path

CODIFICACAO = "utf-8"
OPCAO = "--conferir"  # a opcao que confere sem gravar


def opcao_conferir(leitor, ajuda):
    """Poe no leitor de argumentos (argparse) a opcao que confere sem gravar, com a ajuda dada."""
    leitor.add_argument(OPCAO, action="store_true", help=ajuda)


def grava_ou_confere(arquivo, texto, conferir, falta, em_dia, gravado):
    """Grava o texto no arquivo ou, conferindo, diz se o arquivo e o texto, sem gravar nada;
    mostra a mensagem do caso e devolve o codigo de saida: 1 so na falta."""
    arquivo = Path(arquivo)
    if conferir:
        igual = arquivo.is_file() and arquivo.read_text(encoding=CODIFICACAO) == texto
        print(em_dia if igual else falta)
        return 0 if igual else 1
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(texto, encoding=CODIFICACAO)
    print(gravado)
    return 0
