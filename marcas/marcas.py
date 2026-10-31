"""
Le as marcas escondidas num texto Markdown -- os comentarios HTML <!-- <nivel> <codigo> -->,
que a visualizacao nao mostra -- e confere se cada codigo esta no lugar em que e esperado.

O programa que o importa da os niveis (Niveis): os que abrem uma regiao, do de fora para o
de dentro (o primeiro abre a unidade; abrir um nivel fecha os de dentro dele), e o das
marcas de dentro, que nao abrem regiao: cada uma diz um codigo que esta na regiao aberta.
Comentario cujo texto nao comeca por um nivel nao e marca. Ele da tambem as linhas de cada
arquivo que ficam fora do codigo (dos blocos e de dentro da linha), cada uma com o numero
dela: a regra do que e codigo fica so no leitor de Markdown dele. Niveis, codigos e texto
se comparam em NFC.

O caminho de um lugar do texto tem um codigo por nivel que abre regiao, com None nos que
nao estao abertos; cada arquivo comeca sem nada aberto.

O esperado de cada unidade (Esperado): as regioes em ordem, cada uma com o caminho, os
codigos que ela recebe e se recebe codigos (Regiao); e os codigos que valem em qualquer
regiao da unidade que recebe codigos. Junto, todos os codigos que existem. As regioes que um
texto abre so para chegar as do esperado (a da unidade antes da primeira regiao de dentro
dela, a de um nivel do meio antes da primeira regiao de dentro dele) podem ser abertas e nao
recebem codigos.

Os avisos (Aviso) saem em ordem de arquivo e linha; CASOS da o tipo de cada caso, FALTA ou
ERRO. Niveis ou esperado que nao servem dao ErroDeMarcas, que diz o que esta errado. O nivel
e o codigo repetidos sao achados pelo extrator_comum.py, do extrator, na pasta irma
"extrator" ou na mesma pasta.
"""
import bisect
import collections
import sys
import unicodedata
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "extrator", PASTA):  # na prateleira, o extrator fica na pasta irma
    sys.path.insert(0, str(pasta))
from extrator_comum import repetidos  # noqa: E402

ABRE, FECHA = "<!--", "-->"  # o comeco e o fim de um comentario HTML
INICIO_DO_FIM = ABRE.index(FECHA[:2])  # o fim pode usar os hifens do comeco: <!--> e <!---> sao comentarios vazios
NAO_SE_ESCREVE = "que não se escreve numa marca (um texto sem espaço)"  # o que e_codigo recusa
FALTA, ERRO = "FALTA", "ERRO"
CASOS = {  # cada caso de aviso, com o tipo dele
    "falta": FALTA,
    "fora-da-forma": ERRO,
    "comentario-sem-fim": ERRO,
    "fora-de-unidade": ERRO,
    "regiao-desconhecida": ERRO,
    "regiao-repetida": ERRO,
    "fora-de-ordem": ERRO,
    "unidade-em-dois-lugares": ERRO,
    "nao-existe": ERRO,
    "outra-unidade": ERRO,
    "regiao-que-nao-recebe": ERRO,
    "outra-regiao": ERRO,
}

Niveis = collections.namedtuple("Niveis", "abrem dentro")
Marca = collections.namedtuple("Marca", "arquivo linha nivel codigo")
Regiao = collections.namedtuple("Regiao", "caminho codigos recebe")
Esperado = collections.namedtuple("Esperado", "regioes livres")
Aviso = collections.namedtuple("Aviso", "tipo caso arquivo linha unidade codigo texto")
Indice = collections.namedtuple("Indice", "ordem listadas lugares livres codigos")  # o esperado pronto para conferir


class ErroDeMarcas(ValueError):
    """Niveis ou esperado que nao servem; a mensagem diz o que e onde."""


def nfc(texto):
    return unicodedata.normalize("NFC", texto)


def e_codigo(valor):
    """Se o valor se escreve numa marca: um texto nao vazio, sem espaco e sem o fim do
    comentario."""
    return isinstance(valor, str) and bool(valor) and not any(c.isspace() for c in valor) and FECHA not in valor


def conferidos(niveis):
    """Os niveis em NFC. ErroDeMarcas sem nivel que abre regiao, com nivel que nao se
    escreve numa marca ou com nivel repetido."""
    abrem, dentro = niveis
    if not isinstance(abrem, (list, tuple)) or not abrem:
        raise ErroDeMarcas(f"os níveis que abrem região precisam ser uma lista com pelo menos um: {abrem!r}")
    todos = list(abrem) + [dentro]
    ruins = [n for n in todos if not e_codigo(n)]
    if ruins:
        raise ErroDeMarcas(f"nível {NAO_SE_ESCREVE}: {ruins!r}")
    todos = [nfc(n) for n in todos]
    mesmos = repetidos(todos)
    if mesmos:
        raise ErroDeMarcas(f"nível repetido: {mesmos!r}")
    return Niveis(todos[:-1], todos[-1])


def marcas_das_linhas(linhas, arquivo, niveis):
    """As marcas de um arquivo, na ordem, das linhas dele fora do codigo, [(numero, texto)]:
    cada comentario cujo texto comeca por um nivel, com o arquivo e o numero da linha em que
    ele abre (um comentario pode ocupar mais de uma linha). A marca cujo texto nao e o nivel e
    um codigo sai com o codigo None. O comentario que nao fecha sai com o nivel e o codigo
    None, e o que vem depois dele nao se le."""
    niveis = conferidos(niveis)
    conhecidos = set(niveis.abrem) | {niveis.dentro}
    numeros, inicios, partes, tamanho = [], [], [], 0
    for numero, texto in linhas:
        numeros.append(numero)
        inicios.append(tamanho)
        partes.append(nfc(texto))
        tamanho += len(partes[-1]) + 1
    corrido = "\n".join(partes)
    marcas, i = [], 0
    while True:
        abre = corrido.find(ABRE, i)
        if abre < 0:
            return marcas
        linha = numeros[bisect.bisect_right(inicios, abre) - 1]
        fecha = corrido.find(FECHA, abre + INICIO_DO_FIM)
        if fecha < 0:
            marcas.append(Marca(arquivo, linha, None, None))
            return marcas
        palavras = corrido[abre + len(ABRE):fecha].split()
        if palavras and palavras[0] in conhecidos:
            marcas.append(Marca(arquivo, linha, palavras[0], palavras[1] if len(palavras) == 2 else None))
        i = fecha + len(FECHA)


def com_caminho(marcas, niveis):
    """[(marca, caminho)]: o caminho que a marca de regiao abre, ou o da regiao aberta onde
    esta a outra marca. Abrir um nivel fecha os de dentro dele; a marca sem codigo nao abre
    nada; cada arquivo comeca sem nada aberto."""
    niveis = conferidos(niveis)
    saida, abertos, arquivo = [], None, None
    for marca in marcas:
        if abertos is None or marca.arquivo != arquivo:
            arquivo, abertos = marca.arquivo, [None] * len(niveis.abrem)
        if marca.codigo is not None and marca.nivel in niveis.abrem:
            k = niveis.abrem.index(marca.nivel)
            abertos[k:] = [marca.codigo] + [None] * (len(abertos) - k - 1)
        saida.append((marca, tuple(abertos)))
    return saida


def mostra(caminho, niveis):
    """O caminho em texto: cada nivel aberto, com o codigo dele."""
    return ", ".join(f"{nivel} {codigo}" for nivel, codigo in zip(niveis.abrem, caminho) if codigo is not None)


def ordem_de_escrita(unidade, caminhos, niveis):
    """{caminho: posicao} de cada regiao que um texto certo abre, na ordem, a partir da
    unidade, para chegar as regioes dadas. ErroDeMarcas quando elas, nessa ordem, nao se
    escrevem: uma pede fechado um nivel que outra antes dela abriu, e so abrir de novo um
    nivel de fora o fecharia; ou uma pede aberta outra vez uma regiao."""
    n = len(niveis.abrem)
    abertos = [unidade] + [None] * (n - 1)
    ordem = {tuple(abertos): 0}
    for caminho in caminhos:
        for k in range(1, n):
            if caminho[k] == abertos[k]:
                continue
            if caminho[k] is None:
                raise ErroDeMarcas(f"o esperado da unidade {unidade}: a região {mostra(caminho, niveis)} vem depois de "
                                   f"{mostra(tuple(abertos), niveis)} e pede fechado o nível {niveis.abrem[k]}, que só "
                                   f"se fecha abrindo de novo um nível de fora")
            abertos[k:] = [caminho[k]] + [None] * (n - k - 1)
            if tuple(abertos) in ordem:
                raise ErroDeMarcas(f"o esperado da unidade {unidade}: a região {mostra(tuple(abertos), niveis)} teria "
                                   f"de ser aberta outra vez")
            ordem[tuple(abertos)] = len(ordem)
    return ordem


def indice(unidade, esperado, existem, niveis):
    """O esperado de uma unidade, conferido (Indice): a ordem de cada regiao que um texto
    certo abre; as regioes do esperado, pelo caminho; os caminhos que esperam cada codigo; os
    codigos que valem em qualquer regiao; e todos os codigos da unidade. ErroDeMarcas quando o
    esperado nao serve."""
    def erro(problema):
        return ErroDeMarcas(f"o esperado da unidade {unidade}: {problema}")

    regioes, livres = esperado
    listadas, lugares = {}, collections.defaultdict(list)
    for regiao in map(Regiao._make, regioes):
        bruto = tuple(regiao.caminho)
        if len(bruto) != len(niveis.abrem) or not all(c is None or e_codigo(c) for c in bruto):
            raise erro(f"o caminho {bruto!r} precisa de um código por nível que abre região, com None nos fechados")
        caminho = tuple(c if c is None else nfc(c) for c in bruto)
        if caminho[0] != unidade:
            raise erro(f"o caminho {caminho!r} não começa pela unidade")
        if caminho in listadas:
            raise erro(f"a região {mostra(caminho, niveis)} aparece mais de uma vez")
        if not isinstance(regiao.recebe, bool):
            raise erro(f"a região {mostra(caminho, niveis)} precisa dizer com True ou False se recebe códigos")
        codigos = conferidos_os_codigos(regiao.codigos, f"a região {mostra(caminho, niveis)}", erro)
        if codigos and not regiao.recebe:
            raise erro(f"a região {mostra(caminho, niveis)} não recebe códigos e tem {codigos!r}")
        listadas[caminho] = Regiao(caminho, codigos, regiao.recebe)
        for c in codigos:
            lugares[c].append(caminho)
    livres = conferidos_os_codigos(livres, "os códigos que valem em qualquer região", erro)
    if livres and not any(r.recebe for r in listadas.values()):
        raise erro("tem códigos que valem em qualquer região e nenhuma região que recebe códigos")
    codigos = set(lugares) | set(livres)
    fora = sorted(codigos - existem)
    if fora:
        raise erro(f"código(s) que não estão entre os que existem: {fora!r}")
    return Indice(ordem_de_escrita(unidade, list(listadas), niveis), listadas, dict(lugares), livres, codigos)


def conferidos_os_codigos(codigos, onde, erro):
    """Os codigos em NFC, na ordem; o erro de erro() quando eles nao vem numa lista, ou
    quando um nao se escreve numa marca ou se repete."""
    if not isinstance(codigos, (list, tuple)):
        raise erro(f"{onde}: os códigos precisam vir numa lista: {codigos!r}")
    ruins = [c for c in codigos if not e_codigo(c)]
    if ruins:
        raise erro(f"{onde}: código {NAO_SE_ESCREVE}: {ruins!r}")
    codigos = [nfc(c) for c in codigos]
    mesmos = repetidos(codigos)
    if mesmos:
        raise erro(f"{onde}: código repetido: {mesmos!r}")
    return codigos


def confere(marcas, niveis, esperados, existem):
    """Os avisos das marcas de um ou mais arquivos (na ordem em que foram lidas) contra o
    esperado de cada unidade, {unidade: Esperado}, e todos os codigos que existem. Cada aviso
    tem o tipo, o caso, o arquivo, a linha, a unidade aberta ali (None fora de unidade), o
    codigo de que trata e o texto; saem em ordem de arquivo e linha. A FALTA fica na linha da
    marca que abre a regiao, ou na da unidade quando a regiao nao foi aberta ou quando o
    codigo vale em qualquer regiao. Numa unidade que nao esta no esperado, so a marca dela e
    as fora da forma dao aviso; a unidade aberta outra vez continua a mesma."""
    niveis = conferidos(niveis)
    if isinstance(existem, str):
        raise ErroDeMarcas(f"os códigos que existem precisam vir numa lista ou num conjunto: {existem!r}")
    existem = list(existem)
    ruins = [c for c in existem if not e_codigo(c)] + [u for u in esperados if not e_codigo(u)]
    if ruins:
        raise ErroDeMarcas(f"unidade ou código que existe {NAO_SE_ESCREVE}: {ruins!r}")
    existem = {nfc(c) for c in existem}
    indices = {nfc(u): indice(nfc(u), e, existem, niveis) for u, e in esperados.items()}
    if len(indices) != len(esperados):
        raise ErroDeMarcas(f"unidade repetida no esperado, escrita de dois jeitos: {sorted(esperados)!r}")
    avisos, arquivos, primeira, anterior = [], {}, {}, {}
    abertas, vistos = collections.defaultdict(dict), collections.defaultdict(set)

    def avisa(caso, marca, unidade, codigo, texto):
        avisos.append(Aviso(CASOS[caso], caso, marca.arquivo, marca.linha, unidade, codigo, texto))

    for marca, caminho in com_caminho(marcas, niveis):
        arquivos.setdefault(marca.arquivo, len(arquivos))
        unidade, codigo = caminho[0], marca.codigo
        idx = indices.get(unidade)
        if marca.nivel is None:
            avisa("comentario-sem-fim", marca, unidade, None,
                  "comentário que não fecha: o que vem depois dele não se lê")
        elif codigo is None:
            avisa("fora-da-forma", marca, unidade, None, f"marca {marca.nivel} fora da forma <!-- nível código -->")
        elif unidade is None:
            avisa("fora-de-unidade", marca, None, codigo, f"marca {marca.nivel} {codigo} fora de unidade: antes da "
                  f"primeira marca {niveis.abrem[0]} do arquivo")
        elif idx is None and marca.nivel != niveis.abrem[0]:
            continue  # dentro de uma unidade que o esperado nao tem, so a forma das marcas se confere
        elif marca.nivel in niveis.abrem and caminho not in (idx.ordem if idx is not None else ()):
            avisa("regiao-desconhecida", marca, unidade, codigo, f"região desconhecida: {mostra(caminho, niveis)}")
        elif marca.nivel == niveis.abrem[0]:
            if unidade in primeira:
                antes = primeira[unidade]
                avisa("unidade-em-dois-lugares", marca, unidade, codigo, f"unidade em dois lugares: {unidade}, aberta "
                      f"antes em {antes.arquivo}:{antes.linha}")
            else:
                primeira[unidade], abertas[unidade][caminho], anterior[unidade] = marca, marca, caminho
        elif marca.nivel in niveis.abrem:
            if caminho in abertas[unidade]:
                antes = abertas[unidade][caminho]
                avisa("regiao-repetida", marca, unidade, codigo, f"região repetida: {mostra(caminho, niveis)}, aberta "
                      f"antes em {antes.arquivo}:{antes.linha}")
            else:
                if idx.ordem[caminho] < idx.ordem[anterior[unidade]]:
                    avisa("fora-de-ordem", marca, unidade, codigo, f"região fora de ordem: {mostra(caminho, niveis)} "
                          f"vem depois de {mostra(anterior[unidade], niveis)}")
                abertas[unidade][caminho], anterior[unidade] = marca, caminho
        elif codigo not in existem:
            avisa("nao-existe", marca, unidade, codigo, f"o código {codigo} não existe")
        elif codigo not in idx.codigos:
            avisa("outra-unidade", marca, unidade, codigo, f"o código {codigo} é de outra unidade")
        elif caminho not in idx.listadas or not idx.listadas[caminho].recebe:
            avisa("regiao-que-nao-recebe", marca, unidade, codigo, f"o código {codigo} está em "
                  f"{mostra(caminho, niveis)}, que não recebe códigos")
        elif caminho in idx.lugares.get(codigo, ()) or codigo in idx.livres:
            vistos[unidade].add((caminho, codigo))
        else:
            avisa("outra-regiao", marca, unidade, codigo, f"o código {codigo} está em {mostra(caminho, niveis)}; o "
                  f"lugar dele: {'; '.join(mostra(c, niveis) for c in idx.lugares[codigo])}")

    for unidade, marca_da_unidade in primeira.items():
        idx = indices[unidade]
        for caminho, regiao in idx.listadas.items():
            onde = abertas[unidade].get(caminho, marca_da_unidade)
            for codigo in regiao.codigos:
                if (caminho, codigo) not in vistos[unidade]:
                    avisa("falta", onde, unidade, codigo, f"falta o código {codigo} em {mostra(caminho, niveis)}")
        achados = {codigo for _, codigo in vistos[unidade]}
        for codigo in idx.livres:
            if codigo not in achados:
                avisa("falta", marca_da_unidade, unidade, codigo, f"falta o código {codigo}, que vale em qualquer "
                      f"região da unidade {unidade} que recebe códigos")
    return sorted(avisos, key=lambda a: (arquivos[a.arquivo], a.linha))
