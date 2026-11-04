"""
Junta entradas ao fim de listas de arquivos JSON e troca campos de linhas de tabelas CSV, pelas
mudancas de um arquivo de dados, e grava cada arquivo na forma que ele ja tem: o que muda nele e
so o que se juntou ou se trocou.

A configuracao, do projeto, se le pelo configuracao.py, desta pasta: as "listas", cada uma pelo
nome, com o "arquivo" JSON, o caminho da "lista" dentro dele, com "/" entre as chaves, e,
opcionais, o campo "unico" das entradas e os campos "montados", cada um com o nome do modelo
dele; os "modelos", cada um pelo nome, com o arquivo do "item" e, opcional, o do texto "entre"
dois itens; e as "tabelas", cada uma pelo nome, com o "arquivo" CSV e a coluna "chave", que acha
a linha. Os arquivos valem a partir da pasta da configuracao.

As mudancas sao um JSON com o molde esquemas/mudancas.schema.json: para cada lista, pelo nome,
as entradas que se juntam ao fim dela, na ordem; para cada tabela, pelo nome, as trocas, cada
uma com o valor da chave da linha e o valor novo de cada coluna que muda.

A forma de cada arquivo sai dele, pelo forma_do_arquivo.py, desta pasta, e cada arquivo tem de
voltar igual, letra por letra, lido e gravado de novo nessa forma. Cada campo montado, em
qualquer nivel da entrada, vira o texto do modelo dele, pelo campos_montados.py, desta pasta.

Sao problema, e nada se grava: o arquivo que nao volta igual; o campo montado que nao serve; a
entrada sem o campo unico, ou com o valor dele igual, na forma Unicode NFC, ao de outra entrada
da lista ou das mudancas; sem campo unico, a entrada igual a outra; e a troca sem a chave, com
uma chave que nenhuma linha tem ou que mais de uma tem, com uma coluna que a tabela nao tem, que
nao muda nada ou que troca de novo a mesma coluna da mesma linha.

Mostra uma linha por lista e por tabela mudadas e um resumo, ou uma linha ERRO por problema, com
o arquivo e a linha, ou as mudancas e o caminho do valor nelas, e um resumo. Sai com codigo 0
com os arquivos gravados; 1 com problema; e 2, sem nada gravado, quando a configuracao, as
mudancas, um modelo ou um arquivo de lista ou de tabela nao servem (o README diz quando).
Precisa do extrator_comum.py e do texto_comum.py, do extrator, e do documento_gerado.py, do
grava-ou-confere, nas pastas irmas ou na mesma pasta.

Uso:
    python3 -I listas_e_tabelas.py <configuracao.json> <mudancas.json>
"""

import argparse
import collections
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "grava-ou-confere", PASTA.parent / "extrator", PASTA):
    sys.path.insert(0, str(pasta))  # na prateleira, as pastas irmas; e esta, a dos modulos da peca
from campos_montados import montada  # noqa: E402
from configuracao import LISTAS, TABELAS, Lista, le_configuracao  # noqa: E402
from documento_gerado import confere_destino  # noqa: E402
from extrator_comum import ErroDeDados, campo, igual, le_conferido  # noqa: E402
from forma_do_arquivo import grava, le_csv_na_forma, le_json_na_forma, linha_que_nao_volta  # noqa: E402
from texto_comum import nfc  # noqa: E402

MUDANCAS = PASTA / "esquemas" / "mudancas.schema.json"  # o molde das mudancas
FALTA = object()  # o valor unico da entrada que nao tem o campo unico


def le_mudancas(caminho, listas, tabelas):
    """As mudancas, conferidas pelo molde; ErroDeDados quando nao servem ou nomeiam uma lista ou uma tabela que a
    configuracao nao tem."""
    mudancas = le_conferido(caminho, MUDANCAS)
    for grupo, conhecidos in ((LISTAS, listas), (TABELAS, tabelas)):
        faltam = [nome for nome in mudancas.get(grupo, {}) if nome not in conhecidos]
        if faltam:
            raise ErroDeDados(f"{caminho}: {grupo} que a configuração não tem: {faltam}")
    return mudancas


def le_arquivos(listas, tabelas, mudancas, entradas):
    """{arquivo: Json ou Csv} dos arquivos que as mudancas tocam, cada um lido uma vez; ErroDeDados quando um deles
    e uma das entradas ou nao serve, quando o caminho de uma lista nao leva a uma lista ou quando a tabela nao tem a
    chave."""
    lidos = {}
    for grupo, alvos, le in ((LISTAS, listas, le_json_na_forma), (TABELAS, tabelas, le_csv_na_forma)):
        for nome in mudancas.get(grupo, {}):
            alvo = alvos[nome]
            if alvo.arquivo not in lidos:
                confere_destino(alvo.arquivo, entradas)
                lidos[alvo.arquivo] = le(alvo.arquivo)
            if isinstance(alvo, Lista):
                try:
                    campo(lidos[alvo.arquivo].dados, alvo.lista, list)
                except ErroDeDados as e:
                    raise ErroDeDados(f"{alvo.arquivo}: a lista {nome}: {e}")
            elif alvo.chave not in lidos[alvo.arquivo].registros[0][1]:
                raise ErroDeDados(f"{alvo.arquivo}: a tabela {nome} não tem a coluna {alvo.chave}")
    return lidos


def comparavel(valor):
    """O valor JSON com cada texto, tambem as chaves, na forma Unicode NFC, para comparar com outro."""
    if isinstance(valor, str):
        return nfc(valor)
    if isinstance(valor, list):
        return [comparavel(v) for v in valor]
    if isinstance(valor, dict):
        return {nfc(k): comparavel(v) for k, v in valor.items()}
    return valor


def valor_unico(entrada, unico):
    """O valor que nao pode se repetir na entrada: o do campo unico, ou FALTA sem ele; sem campo unico, a entrada."""
    if unico is None:
        return entrada
    return entrada[unico] if isinstance(entrada, dict) and unico in entrada else FALTA


def junta(nome, alvo, entradas, dados):
    """(problemas [(caminho, motivo)], entradas juntadas): junta ao fim da lista dos dados as entradas, montadas, e
    confere o valor unico de cada uma contra o das outras, da lista e das mudancas."""
    lista = campo(dados, alvo.lista, list)
    fim = f"/{alvo.unico}" if alvo.unico is not None else ""
    vistos = []  # [(lugar, valor unico comparavel)] das entradas da lista e das ja juntadas
    for k, entrada in enumerate(lista):
        valor = valor_unico(entrada, alvo.unico)
        if valor is not FALTA:
            vistos.append((f"/{alvo.lista}/{k}{fim} de {alvo.arquivo}", comparavel(valor)))
    problemas, novas = [], []
    for k, entrada in enumerate(entradas):
        onde = f"/{LISTAS}/{nome}/{k}"
        nova, erros = montada(entrada, alvo.modelos, onde)
        problemas += erros
        valor = valor_unico(nova, alvo.unico)
        if valor is FALTA:
            problemas.append((onde, f"falta o campo {alvo.unico}" if isinstance(nova, dict) else
                              f"não é um objeto com o campo {alvo.unico}"))
        else:
            mesmo = next((lugar for lugar, visto in vistos if igual(visto, comparavel(valor))), None)
            if mesmo is not None:
                problemas.append((onde + fim, f"repete {mesmo}"))
            vistos.append((onde + fim, comparavel(valor)))
        novas.append(nova)
    lista.extend(novas)
    return problemas, len(novas)


def troca(nome, alvo, trocas, tabela, feitas):
    """(problemas, linhas mudadas, campos trocados): troca nos registros da tabela o valor de cada coluna das trocas,
    na linha que a chave acha, tambem em outra forma Unicode; feitas, {(registro, coluna): caminho}, guarda o que ja
    se trocou no arquivo."""
    colunas = {c: i for i, c in enumerate(tabela.registros[0][1])}
    por_chave = collections.defaultdict(list)
    for k, (_, valores) in enumerate(tabela.registros[1:], start=1):
        por_chave[nfc(valores[colunas[alvo.chave]])].append(k)
    problemas, mudadas, trocados = [], set(), 0
    for t, mudanca in enumerate(trocas):
        onde = f"/{TABELAS}/{nome}/{t}"
        if alvo.chave not in mudanca:
            problemas.append((onde, f"falta a coluna {alvo.chave}, que acha a linha"))
            continue
        achados = por_chave.get(nfc(mudanca[alvo.chave]), [])
        if len(achados) != 1:
            motivo = (f"as linhas {[tabela.registros[k][0] for k in achados]} de {alvo.arquivo} têm esse valor"
                      if achados else f"nenhuma linha de {alvo.arquivo} tem esse valor")
            problemas.append((f"{onde}/{alvo.chave}", motivo))
            continue
        k = achados[0]
        linha, valores = tabela.registros[k]
        for coluna, valor in mudanca.items():
            if coluna == alvo.chave:
                continue
            lugar = f"{onde}/{coluna}"
            if coluna not in colunas:
                problemas.append((lugar, f"coluna que {alvo.arquivo} não tem"))
            elif (k, coluna) in feitas:
                problemas.append((lugar, f"troca de novo o que {feitas[k, coluna]} troca"))
            elif valores[colunas[coluna]] == valor:
                problemas.append((lugar, f"a linha {linha} de {alvo.arquivo} já tem esse valor"))
            else:
                feitas[k, coluna] = lugar
                valores[colunas[coluna]] = valor
                mudadas.add(k)
                trocados += 1
    return problemas, len(mudadas), trocados


def aplica(listas, tabelas, mudancas, lidos):
    """(problemas [(caminho, motivo)], o que se fez [linha]): junta as entradas e troca os campos nos dados lidos."""
    problemas, feito, feitas = [], [], collections.defaultdict(dict)
    for nome, entradas in mudancas.get(LISTAS, {}).items():
        alvo = listas[nome]
        erros, n = junta(nome, alvo, entradas, lidos[alvo.arquivo].dados)
        problemas += erros
        feito.append(f"{alvo.arquivo}: {n} entrada(s) juntada(s) à lista {alvo.lista}")
    for nome, trocas in mudancas.get(TABELAS, {}).items():
        alvo = tabelas[nome]
        erros, linhas, campos = troca(nome, alvo, trocas, lidos[alvo.arquivo], feitas[alvo.arquivo])
        problemas += erros
        feito.append(f"{alvo.arquivo}: {campos} campo(s) trocado(s) em {linhas} linha(s)")
    return problemas, feito


def main(argv=None):
    p = argparse.ArgumentParser(description="Junta entradas ao fim de listas JSON e troca campos de tabelas CSV.")
    p.add_argument("configuracao", type=Path, help="as listas, os modelos e as tabelas do projeto, em JSON")
    p.add_argument("mudancas", type=Path, help="as entradas e as trocas, em JSON")
    a = p.parse_args(argv)
    try:
        listas, tabelas, modelos = le_configuracao(a.configuracao)
        mudancas = le_mudancas(a.mudancas, listas, tabelas)
        lidos = le_arquivos(listas, tabelas, mudancas, [a.configuracao, a.mudancas, *modelos])
    except ErroDeDados as e:
        print(f"ERRO: {e}")
        return 2
    fora = [(arquivo, linha_que_nao_volta(lido), lido.forma()) for arquivo, lido in lidos.items()]
    erros = [(f"{arquivo}:{n}", f"não volta igual, lido e gravado de novo na forma que se tira dele ({forma})")
             for arquivo, n, forma in fora if n is not None]
    problemas, feito = aplica(listas, tabelas, mudancas, lidos)
    erros += [(f"{a.mudancas}: {onde}", motivo) for onde, motivo in problemas]
    if erros:
        for lugar, motivo in erros:
            print(f"ERRO {lugar}: {motivo}")
        n = sum(len(v) for grupo in (LISTAS, TABELAS) for v in mudancas.get(grupo, {}).values())
        print(f"{n} mudança(s), {len(erros)} erro(s): nada foi gravado.")
        return 1
    try:
        grava({arquivo: lido.refeito() for arquivo, lido in lidos.items()})
    except ErroDeDados as e:
        print(f"ERRO: {e}")
        return 2
    for linha in feito:
        print(linha)
    print(f"{len(lidos)} arquivo(s) gravado(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
