"""
Confere o CSV do baralho antes do pacote do Anki: cada linha contra a tabela (o id, o assunto,
a coluna, as palavras-chave e a fonte que a tabela da, e a ordem dela), os cartoes (nenhum
faltando, nenhum que a tabela nao da, nenhum id repetido), os campos vazios (tambem a pergunta,
a resposta e o trecho, que se escrevem pelo texto da fonte), o trecho de cada linha no
texto da fonte dela, achado nas pastas dadas, em ordem (letra por letra, comparados os dois na
forma NFC, com os espacos juntados e sem as marcas de enfase da configuracao), e cada campo
contra os padroes proibidos dos arquivos dados, como as marcas de IA.

Mostra uma linha "ERRO arquivo:linha: motivo" por problema, em ordem de linha, e um resumo; sai
com 0 sem erro, 1 com erro e 2 quando a configuracao, a tabela, o CSV, um texto, um arquivo de
padroes proibidos ou um argumento nao servem. Usa so a biblioteca padrao, o baralho_comum,
desta pasta, e o proibidos_comum.py, da peca confere-forma, na pasta irma "confere-forma" ou
na mesma pasta.

Uso:
    python3 -I confere_baralho.py <configuracao.json> <tabela.md> <baralho.csv> --pasta <pasta das fontes>...
        [--proibidos <arquivo.json>]...
"""
import argparse
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "confere-forma", PASTA):  # na prateleira, a peca confere-forma fica na pasta irma
    sys.path.insert(0, str(pasta))
import baralho_comum as comum  # noqa: E402
from proibidos_comum import achados, regras_proibidas  # noqa: E402


class Textos:
    """O texto de cada fonte, achado nas pastas, na ordem delas, e lido uma vez so, ja na forma
    em que os trechos se comparam."""

    def __init__(self, pastas, marcas):
        self.pastas, self.marcas, self.lidos = pastas, marcas, {}

    def normaliza(self, texto):
        return comum.normaliza(texto, self.marcas)

    def de(self, fonte):
        """O texto da fonte na forma de comparar; None quando nenhuma pasta a tem."""
        if fonte not in self.lidos:
            caminho = comum.acha(fonte, self.pastas)
            self.lidos[fonte] = self.normaliza(comum.le_texto(caminho)) if caminho else None
        return self.lidos[fonte]


def erros_da_linha(linha, esperada, textos, regras):
    """[motivo] de cada problema de uma linha do CSV; esperada e a linha que a tabela da para o
    id dela (None quando a tabela nao da esse id)."""
    erros = [f"campo vazio: {c}" for c in comum.COLUNAS if not linha[c].strip()]
    if esperada is None:
        erros.append(f"id que a tabela não dá: {linha['id']}")
    else:
        erros += [f"{c} diferente do que a tabela dá: {linha[c]!r}, e não {esperada[c]!r}"
                  for c in comum.DA_TABELA if linha[c] != esperada[c]]
    if linha["trecho"].strip():
        texto = textos.de(linha["fonte"])
        if texto is None:
            erros.append(f"fonte que nenhuma pasta tem: {linha['fonte']}")
        elif textos.normaliza(linha["trecho"]) not in texto:
            erros.append(f"trecho que não está no texto de {linha['fonte']}: {linha['trecho']}")
    erros += [f"padrão proibido em {c}: {nome}" for c in comum.COLUNAS for nome in achados(linha[c], regras)]
    return erros


def erros_do_csv(linhas, esperadas, textos, regras):
    """[(numero da linha, motivo)] de cada problema do CSV, em ordem de linha: os de cada linha,
    os ids repetidos, os cartoes que faltam (na ultima linha) e, quando os ids sao os da
    tabela, a primeira linha fora da ordem dela."""
    por_id, primeira, erros = {e["id"]: e for e in esperadas}, {}, []
    for numero, linha in linhas:
        erros += [(numero, motivo) for motivo in erros_da_linha(linha, por_id.get(linha["id"]), textos, regras)]
        if linha["id"] in primeira:
            erros.append((numero, f"id repetido (também na linha {primeira[linha['id']]}): {linha['id']}"))
        primeira.setdefault(linha["id"], numero)
    fim = linhas[-1][0] if linhas else 1
    erros += [(fim, f"falta o cartão: {e['id']}") for e in esperadas if e["id"] not in primeira]
    ids, da_tabela = [linha["id"] for _, linha in linhas], [e["id"] for e in esperadas]
    if sorted(ids) == sorted(da_tabela) and ids != da_tabela:
        k = next(k for k, (i, j) in enumerate(zip(ids, da_tabela)) if i != j)
        erros.append((linhas[k][0], f"linha fora da ordem da tabela: {ids[k]}; no lugar dela vem {da_tabela[k]}"))
    return sorted(erros)


def confere(a):
    conf = comum.le_configuracao(a.configuracao)
    esperadas = comum.linhas_esperadas(a.tabela, conf)
    linhas = comum.le_csv(a.csv)
    regras = regras_proibidas(a.proibidos)
    textos = Textos(a.pasta, [e["marca"] for e in conf["enfases"]])
    erros = erros_do_csv(linhas, esperadas, textos, regras)
    for numero, motivo in erros:
        print(f"ERRO {a.csv}:{numero}: {motivo}")
    assuntos = len({linha["assunto"] for _, linha in linhas})
    print(f"{len(linhas)} linha(s), {assuntos} assunto(s), {len(erros)} erro(s)")
    return 1 if erros else 0


def main():
    p = argparse.ArgumentParser(description="Confere o CSV do baralho antes do pacote do Anki.")
    p.add_argument("configuracao", help="a configuração do baralho")
    p.add_argument("tabela", help="a tabela Markdown")
    p.add_argument("csv", help="o CSV a conferir")
    p.add_argument("--pasta", action="append", required=True,
                   help="uma pasta das fontes; pode se repetir, e a primeira que tem a fonte vale")
    p.add_argument("--proibidos", action="append", default=[], help="um arquivo de padrões proibidos; pode se repetir")
    return comum.roda(confere, p.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
