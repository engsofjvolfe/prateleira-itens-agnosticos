"""
Confere as citacoes de textos Markdown contra as transcricoes das fontes: cada trecho
citado precisa estar, letra por letra, na fonte que a referencia nomeia, e nas paginas que
ela da.

Uma citacao e uma linha de referencia (com a fonte e as paginas), reconhecida por uma
expressao da configuracao, seguida da linha do trecho, reconhecida por outra. O trecho e
partido na marca de supressao; cada pedaco, sem as pontas dadas, precisa aparecer na
fonte, e pelo menos uma das vezes em que aparece precisa cair so nas paginas citadas. Os
pedacos precisam aparecer na ordem do trecho, cada um depois do fim do anterior, e entre
um e o seguinte a fonte precisa ter alguma coisa alem das pontas e dos espacos: a
supressao marca o que foi omitido, e nao pode estar onde nada foi. A
fonte e o arquivo que o modelo da configuracao nomeia, na pasta das fontes; as paginas
dela vem do modelo do titulo de pagina (o mesmo do extrator), e as linhas dos blocos que a
configuracao manda ignorar (como as imagens) nao contam. Na comparacao, o texto vai para
NFC, cada caractere de um grupo de equivalentes vira o primeiro do grupo e cada trecho de
espacos vira um espaco so; maiusculas contam.

Mostra uma linha "ERRO arquivo:linha: motivo" por problema e um resumo; sai com 0 sem
erro, 1 com erro e 2 quando a configuracao ou um argumento nao serve. Usa so a biblioteca
padrao, o extrator_comum.py e o texto_comum.py, da peca extrator, na pasta irma "extrator"
ou na mesma pasta.

Uso:
    python3 -I confere_citacoes.py <configuracao.json> <pasta das fontes> <texto.md>...
"""

import argparse
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "extrator", PASTA):  # na prateleira, a peca extrator fica na pasta irma
    sys.path.insert(0, str(pasta))
from extrator_comum import ErroDeDados, expressao, le_conferido, paginas_da_transcricao, preenche  # noqa: E402
from texto_comum import espacos_juntos, nfc  # noqa: E402

MOLDE = PASTA / "esquemas" / "confere-citacoes.schema.json"
GRUPOS = {"referencia": ("fonte", "paginas"), "citacao": ("trecho",)}  # os grupos que cada expressao tem de ter
CODIFICACAO = "utf-8"
MOSTRA = 80  # quantas letras do pedaco a mensagem mostra


def le_configuracao(caminho):
    """A configuracao, conferida contra o molde, com as expressoes compiladas; os grupos delas e
    o modelo do arquivo, que o molde nao ve, conferidos aqui."""
    dados = le_conferido(caminho, MOLDE)
    conf = {nome: expressao(dados, nome) for nome in GRUPOS}
    for nome, grupos in GRUPOS.items():
        faltam = [g for g in grupos if g not in conf[nome].groupindex]
        if faltam:
            raise ErroDeDados(f"a expressão {nome} não tem o(s) grupo(s) {faltam}")
    conf.update(separador=dados["paginas"]["separador"], intervalo=dados["paginas"]["intervalo"],
                arquivo=dados["fontes"]["arquivo"], titulo_pagina=dados["fontes"]["titulo_pagina"],
                supressao=dados["supressao"], pontas=dados["pontas"])
    preenche(conf["arquivo"], fonte="")  # um campo que nao seja {fonte} e erro agora, nao no meio da conferencia
    conf["ignorar"] = [(expressao(b, "abre"), expressao(b, "fecha")) for b in dados["fontes"]["ignorar"]]
    conf["equivalentes"] = {c: g[0] for g in dados["equivalentes"] for c in g}
    return conf


def letras(texto, equivalentes):
    """O texto em NFC, com cada caractere de um grupo de equivalentes trocado pelo primeiro do grupo."""
    return "".join(equivalentes.get(c, c) for c in nfc(texto))


def comparavel(texto, conf):
    """O texto como se compara: equivalentes iguais e cada trecho de espacos um espaco so, sem espaco nas pontas."""
    return espacos_juntos(letras(texto, conf["equivalentes"]))


def le_fonte(caminho, conf):
    """(texto comparavel da fonte, rotulo da pagina de cada letra dele). As linhas fora de
    pagina e as dos blocos ignorados ficam de fora; bloco que nao fecha e erro."""
    try:
        texto = Path(caminho).read_text(encoding=CODIFICACAO)
    except (OSError, UnicodeDecodeError) as e:
        raise ErroDeDados(f"a fonte {caminho} não se lê em {CODIFICACAO} ({e})")
    saida, rotulos, fecha, aberto = [], [], None, None
    for rotulo, _, linhas in paginas_da_transcricao(texto, conf["titulo_pagina"]):
        for n, linha in linhas:
            if fecha is not None:
                if fecha.search(linha):
                    fecha = None
                continue
            fecha = next((f for a, f in conf["ignorar"] if a.search(linha)), None)
            if fecha is not None:
                aberto = n
                continue
            for c in letras(linha, conf["equivalentes"]) + " ":
                if c.isspace():
                    if not saida or saida[-1] == " ":
                        continue
                    c = " "
                saida.append(c)
                rotulos.append(rotulo)
    if fecha is not None:
        raise ErroDeDados(f"{caminho}:{aberto}: bloco ignorado que não fecha")
    return "".join(saida), rotulos


def fonte_lida(nome, conf, pasta, lidas):
    """A fonte de nome dado, lida uma vez so entre os textos; o texto do erro quando ela nao
    existe ou nao se le."""
    if nome not in lidas:
        caminho = Path(pasta) / preenche(conf["arquivo"], fonte=nome)
        if not caminho.is_file():
            lidas[nome] = f"a fonte {caminho} não existe"
        else:
            try:
                lidas[nome] = le_fonte(caminho, conf)
            except ErroDeDados as e:
                lidas[nome] = str(e)
    return lidas[nome]


def chave_de_pagina(rotulo):
    """Ordem dos rotulos: os numeros pelo valor, antes dos outros, que vao por ordem de texto."""
    return (0, int(rotulo), "") if rotulo.isdigit() else (1, 0, rotulo)


def paginas_citadas(texto, separador, intervalo):
    """Os rotulos das paginas citadas: cada parte entre separadores e um rotulo, ou um
    intervalo entre dois numeros, os dois incluidos; None quando uma parte nao se le."""
    citadas = set()
    for parte in texto.split(separador):
        de, sep, ate = (s.strip() for s in parte.partition(intervalo))
        if not de:
            return None
        if not sep:
            citadas.add(de)
            continue
        if not (de.isdigit() and ate.isdigit()) or int(de) > int(ate):
            return None
        citadas.update(str(n) for n in range(int(de), int(ate) + 1))
    return citadas


def pedacos_do_trecho(trecho, conf):
    """Os pedacos do trecho, partido na marca de supressao, comparaveis e sem as pontas; os vazios saem."""
    pedacos = (comparavel(parte, conf).strip(conf["pontas"]) for parte in trecho.split(conf["supressao"]))
    return [p for p in pedacos if p]


def ocorrencias(texto, pedaco):
    """A posicao de cada vez que o pedaco aparece no texto, em ordem."""
    i = texto.find(pedaco)
    while i >= 0:
        yield i
        i = texto.find(pedaco, i + 1)


def confere_pedaco(pedaco, fonte, citadas):
    """(posicoes, motivo): as posicoes, em ordem, das vezes em que o pedaco aparece na fonte
    so nas paginas citadas, e None; ou nenhuma posicao e o motivo, quando nao ha nenhuma."""
    texto, rotulos = fonte
    paginas = {i: set(rotulos[i:i + len(pedaco)]) for i in ocorrencias(texto, pedaco)}
    if not paginas:
        dica = " (difere só em maiúsculas)" if pedaco.lower() in texto.lower() else ""
        return [], f"trecho que não está na fonte{dica}: {pedaco[:MOSTRA]}"
    posicoes = [i for i, p in paginas.items() if p <= citadas]
    if posicoes:
        return posicoes, None
    achadas = ", ".join(sorted(set().union(*paginas.values()), key=chave_de_pagina))
    return [], f"trecho que está na(s) p. {achadas}, fora das citadas: {pedaco[:MOSTRA]}"


def omite_algo(entre, pontas):
    """Se o que a fonte tem entre dois pedacos tem alguma letra alem das pontas e dos espacos."""
    return any(c not in pontas and not c.isspace() for c in entre)


def confere_sequencia(achados, texto, pontas):
    """None quando os pedacos aparecem na fonte na ordem do trecho, com alguma coisa omitida
    entre cada um e o seguinte; senao, o motivo. achados: [(pedaco, posicoes)], na ordem do
    trecho, cada pedaco com as posicoes em que esta nas paginas citadas. Cada pedaco fica na
    primeira posicao que serve: a mais cedo deixa mais lugar aos seguintes, entao, se ela nao
    leva ate o fim, nenhuma leva."""
    fim = None
    for pedaco, posicoes in achados:
        # texto[fim:i] e vazio quando i <= fim: a mesma conta barra o pedaco fora da ordem
        servem = posicoes if fim is None else [i for i in posicoes if omite_algo(texto[fim:i], pontas)]
        if not servem:
            motivo = ("supressão que não omite nada antes de" if max(posicoes) >= fim
                      else "trecho fora da ordem da fonte")
            return f"{motivo}: {pedaco[:MOSTRA]}"
        fim = servem[0] + len(pedaco)
    return None


def confere_texto(arquivo, conf, pasta, lidas):
    """([(linha, motivo)], citacoes, pedacos) de um texto."""
    try:
        linhas = Path(arquivo).read_text(encoding=CODIFICACAO).split("\n")
    except (OSError, UnicodeDecodeError) as e:
        raise ErroDeDados(f"o texto {arquivo} não se lê em {CODIFICACAO} ({e})")
    erros, citacoes, pedacos, k = [], 0, 0, 0
    while k < len(linhas):
        ref = conf["referencia"].search(linhas[k])
        if ref is None:
            if conf["citacao"].search(linhas[k]):
                erros.append((k + 1, "trecho sem a linha de referência logo antes"))
            k += 1
            continue
        citacoes += 1
        cit = conf["citacao"].search(linhas[k + 1]) if k + 1 < len(linhas) else None
        if cit is None:
            erros.append((k + 1, "referência sem a linha do trecho logo depois"))
            k += 1
            continue
        citadas = paginas_citadas(ref.group("paginas"), conf["separador"], conf["intervalo"])
        fonte = fonte_lida(ref.group("fonte"), conf, pasta, lidas) if citadas is not None else None
        if citadas is None:
            erros.append((k + 1, f"páginas que não se leem: {ref.group('paginas')!r}"))
        elif isinstance(fonte, str):
            erros.append((k + 1, fonte))
        else:
            achados = []
            for pedaco in pedacos_do_trecho(cit.group("trecho"), conf):
                pedacos += 1
                posicoes, motivo = confere_pedaco(pedaco, fonte, citadas)
                if motivo:
                    erros.append((k + 2, motivo))
                achados.append((pedaco, posicoes))
            motivo = confere_sequencia(achados, fonte[0], conf["pontas"]) if all(p for _, p in achados) else None
            if motivo:
                erros.append((k + 2, motivo))
        k += 2
    return erros, citacoes, pedacos


def main(argv=None):
    p = argparse.ArgumentParser(description="Confere as citações de textos Markdown contra as transcrições das fontes.")
    p.add_argument("configuracao", type=Path)
    p.add_argument("fontes", type=Path, help="a pasta das transcrições das fontes")
    p.add_argument("textos", type=Path, nargs="+")
    a = p.parse_args(argv)
    faltam = ([str(a.fontes)] if not a.fontes.is_dir() else []) + [str(t) for t in a.textos if not t.is_file()]
    if faltam:
        print(f"ERRO: não existe(m): {faltam}")
        return 2
    try:
        conf, lidas = le_configuracao(a.configuracao), {}
        resultados = [(t, confere_texto(t, conf, a.fontes, lidas)) for t in a.textos]
    except ErroDeDados as e:
        print(f"ERRO: {e}")
        return 2
    erros = citacoes = pedacos = 0
    for texto, (lista, c, n) in resultados:
        for linha, motivo in lista:
            print(f"ERRO {texto}:{linha}: {motivo}")
        erros, citacoes, pedacos = erros + len(lista), citacoes + c, pedacos + n
    print(f"{len(a.textos)} texto(s), {citacoes} citação(ões), {pedacos} trecho(s), {erros} erro(s)")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
