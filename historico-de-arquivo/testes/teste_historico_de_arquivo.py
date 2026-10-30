"""Testes de historico_de_arquivo.py e do transcricoes.py, que le as transcricoes para ele.

Tudo e inventado aqui, sorteado com uma semente (--semente para outra): o padrao do nome e a codificacao das
transcricoes, os nomes dos campos dos eventos e das ferramentas, as sessoes, os caminhos, as horas e os textos e, da
saida, os nomes dos arquivos, os rotulos, as marcas e a codificacao; nada e de um projeto real nem de um programa de
verdade. Os testes conferem o que o script faz, nunca uma frase pronta:
  - acha cada uso de uma ferramenta da configuracao no arquivo pedido, e so eles: nem o uso em outro arquivo, nem o de
    uma ferramenta que a configuracao nao tem, nem o bloco de outro tipo com os mesmos campos; nas transcricoes da
    pasta e das subpastas cujo nome segue o padrao, e nao no arquivo de outro nome; a pasta cujo nome segue o padrao
    nao e lida como transcricao;
  - pelo nome, acha os usos de um arquivo com esse nome em qualquer pasta, e nao os de outro nome;
  - le as transcricoes na codificacao da configuracao e grava a saida na dela;
  - poe os achados na ordem do tempo, que as transcricoes trazem embaralhada;
  - cada achado traz a sessao, a hora, a ferramenta, o caminho, a transcricao e a linha, cada um depois do rotulo e do
    separador da configuracao; os campos da entrada que a configuracao diz, sob o titulo entre as marcas dela, o que
    nao e texto em JSON, e nenhum outro; e, so na ferramenta que pede, o texto do resultado, dado em texto ou em lista
    de blocos, um bloco por linha, ou a marca de sem resultado, quando ele nao vem;
  - os arquivos dos achados tem a extensao da configuracao, e a lista dos achados e a das linhas que nao se leram, os
    nomes e os rotulos dela; nada mais e gravado;
  - lista as linhas que nao se leem (fora da codificacao ou que nao sao objeto JSON), e nao a linha em branco; o evento
    sem mensagem, a mensagem que nao e objeto, o conteudo que nao e lista (texto ou numero) e o bloco que nao e objeto
    nao quebram nada;
  - a configuracao com campo desconhecido, sem um dos campos que o script le, com uma codificacao que nao existe (a das
    transcricoes, numa pasta sem transcricao nenhuma) ou com dois arquivos da saida de mesmo nome, e a pasta das
    transcricoes que nao existe dao erro e nao criam a pasta de saida; a pasta de saida que ja existe da erro e fica
    como estava;
  - duas rodadas dao o mesmo.
Uso:
    python3 -I teste_historico_de_arquivo.py <pasta de historico_de_arquivo.py> <pasta de trabalho nova> [--semente N]
Precisa do extrator_comum.py, do extrator, na pasta irma da peca.
"""
import argparse
import csv
import json
import random
import subprocess
import sys
from pathlib import Path

leitor = argparse.ArgumentParser()
leitor.add_argument("peca", type=Path)
leitor.add_argument("trabalho", type=Path)
leitor.add_argument("--semente", type=int, default=1)
ARGS = leitor.parse_args()
PECA, TRABALHO = ARGS.peca.resolve(), ARGS.trabalho.resolve()
PROGRAMA = PECA / "historico_de_arquivo.py"
SORTE = random.Random(ARGS.semente)
ACENTUADAS = "çéáíóú"  # um byte so em cada codificacao sorteada, que o UTF-8 nao le assim
LETRAS = "abcdefghijklmnopqrstuvwxyz" + ACENTUADAS
SINAIS = "=#*~+>|"
FORA = b"\x81"  # um byte que nenhuma das codificacoes sorteadas para as transcricoes tem
FALHAS = []
CONTADOR = iter(range(1, 10 ** 9))
USADAS = set()


def nova():
    """Uma palavra sorteada que nao saiu antes, sempre com uma letra acentuada."""
    while True:
        letras = [SORTE.choice(LETRAS) for _ in range(SORTE.randint(3, 8))]
        letras.insert(SORTE.randrange(len(letras) + 1), SORTE.choice(ACENTUADAS))
        palavra = "".join(letras)
        if palavra not in USADAS:
            USADAS.add(palavra)
            return palavra


def texto_unico():
    """Um texto sorteado que nenhum outro contem: termina num numero entre sinais, unico na rodada."""
    return f"{nova()} {nova()} <{next(CONTADOR)}>"


def marca():
    """Uma marca sorteada, de sinais."""
    return "".join(SORTE.choice(SINAIS) for _ in range(SORTE.randint(1, 3)))


CHAVES = ("hora", "sessao", "mensagem", "conteudo", "tipo", "texto", "tipo_uso", "id_uso", "nome_uso", "entrada",
          "caminho", "tipo_resultado", "id_resultado", "conteudo_resultado", "le", "poe", "troca", "estranha", "desde",
          "tudo", "velho", "novo", "varios", "escondido", "isca", "tipo_texto")
N = {chave: nova() for chave in CHAVES}  # cada nome inventado, todos diferentes
CAMPOS = {N["le"]: [N["desde"]], N["poe"]: [N["tudo"]], N["troca"]: [N["velho"], N["novo"], N["varios"]]}
COM_RESULTADO = {N["le"]}
EXTENSAO = nova()  # a das transcricoes
ROTULOS = ("numero", "arquivo", "sessao", "hora", "ferramenta", "caminho", "transcricao", "linha", "resultado")
CONFIG = {
    "versao_schema": 1,
    "transcricoes": {"padrao": f"*.{EXTENSAO}", "codificacao": SORTE.choice(["cp1252", "cp1250"])},
    "eventos": {chave: N[chave] for chave in ("hora", "sessao", "mensagem", "conteudo", "tipo", "texto")},
    "uso": {"tipo": N["tipo_uso"], "id": N["id_uso"], "nome": N["nome_uso"], "entrada": N["entrada"],
            "caminho": N["caminho"]},
    "resultado": {"tipo": N["tipo_resultado"], "id": N["id_resultado"], "conteudo": N["conteudo_resultado"]},
    "ferramentas": [{"nome": nome, "campos": campos, "resultado": nome in COM_RESULTADO}
                    for nome, campos in CAMPOS.items()],
    "saida": {"codificacao": SORTE.choice(["utf-16", "cp1252", "cp1250"]), "extensao": f".{nova()}",
              "lista": f"{nova()}.{nova()}", "ilegiveis": f"{nova()}.{nova()}",
              "rotulos": {chave: nova() for chave in ROTULOS}, "separador": f"{marca()} ",
              "secao": {"antes": f"{marca()} ", "depois": f" {marca()}"}, "sem_resultado": f"{nova()} {nova()}"},
}
SAIDA, ROT = CONFIG["saida"], CONFIG["saida"]["rotulos"]
CODIFICACAO = CONFIG["transcricoes"]["codificacao"]
NOME = f"{nova()}.{nova()}"
PEDIDO = f"/{nova()}/{nova()}/{NOME}"
MESMO_NOME = f"/{nova()}/{NOME}"  # outra pasta, o mesmo nome
OUTRO = f"{PEDIDO.rsplit('/', 1)[0]}/{nova()}{NOME}"  # a mesma pasta, outro nome
# a terceira fica numa pasta cujo nome segue o padrao das transcricoes
TRANSCRICOES = [f"{nova()}.{EXTENSAO}", f"{nova()}.{EXTENSAO}", f"{nova()}/{nova()}.{EXTENSAO}/{nova()}.{EXTENSAO}"]


def valor_de(campo):
    """Um valor sorteado para um campo da entrada; o campo de varios valores nunca e texto, nem numero, que o JSON e o
    Python escrevem igual."""
    if campo == N["varios"]:
        return SORTE.choice([True, [texto_unico(), texto_unico()], {nova(): texto_unico()}])
    return texto_unico()


def uso(ferramenta, caminho, todos=False):
    """(evento sem hora, dados do uso) de um uso sorteado: com um bloco de texto antes, as vezes, e cada campo da
    ferramenta (os da que le, na ferramenta estranha), cada um com chance de faltar, menos com todos."""
    campos = CAMPOS.get(ferramenta, CAMPOS[N["le"]])
    entrada = {N["caminho"]: caminho, N["escondido"]: texto_unico()}
    entrada.update({c: valor_de(c) for c in campos if todos or SORTE.random() < 0.8})
    ident = f"{nova()}{next(CONTADOR)}"
    blocos = [{N["tipo"]: N["tipo_texto"], N["texto"]: texto_unico()}] if SORTE.random() < 0.5 else []
    blocos.append({N["tipo"]: N["tipo_uso"], N["id_uso"]: ident, N["nome_uso"]: ferramenta, N["entrada"]: entrada})
    evento = {N["mensagem"]: {N["conteudo"]: blocos}}
    return evento, {"ferramenta": ferramenta, "caminho": caminho, "entrada": entrada, "id": ident, "resultado": None,
                    "evento": evento}


def resultado(dados, em_lista):
    """O evento do resultado do uso, em texto ou em lista de dois blocos de texto; guarda nos dados o texto esperado."""
    partes = [texto_unico(), texto_unico()]
    conteudo = [{N["tipo"]: N["tipo_texto"], N["texto"]: p} for p in partes] if em_lista else partes[0]
    dados["resultado"] = "\n".join(partes) if em_lista else partes[0]
    return {N["mensagem"]: {N["conteudo"]: [{N["tipo"]: N["tipo_resultado"], N["id_resultado"]: dados["id"],
                                             N["conteudo_resultado"]: conteudo}]}}


def obrigatorios():
    """Os usos que toda rodada tem, para cada caso aparecer: cada ferramenta no arquivo pedido, com todos os campos; a
    que le com resultado em lista, com resultado em texto e sem resultado; a que poe com resultado; um uso no mesmo
    nome, um em outro nome e um da ferramenta estranha no arquivo pedido. (ferramenta, caminho, resultado: None,
    'texto' ou 'lista')."""
    return [(N["le"], PEDIDO, "lista"), (N["le"], PEDIDO, "texto"), (N["le"], PEDIDO, None),
            (N["poe"], PEDIDO, "texto"), (N["troca"], PEDIDO, "texto"), (N["le"], MESMO_NOME, "texto"),
            (N["poe"], OUTRO, "texto"), (N["estranha"], PEDIDO, "texto")]


RUINS = [b"isto nao e json {", b"[1, 2, 3]", FORA + b" fora da codificacao", b"\"so um texto\""]  # nao se leem
BRANCAS = [b"", b"   ", b"\t"]  # linhas em branco, que nao contam


def ruido(sessao):
    """Eventos sem uso nem resultado: sem mensagem, com a mensagem em texto, com o conteudo em texto e em numero, com
    blocos que nao sao objetos e com um bloco de outro tipo que tem os campos de um uso no arquivo pedido."""
    isca = {N["tipo"]: N["isca"], N["id_uso"]: nova(), N["nome_uso"]: N["le"],
            N["entrada"]: {N["caminho"]: PEDIDO, N["desde"]: texto_unico()}}
    conteudos = [texto_unico(), next(CONTADOR), [texto_unico(), next(CONTADOR)], [isca]]
    return ([{N["sessao"]: sessao}, {N["sessao"]: sessao, N["mensagem"]: texto_unico()}]
            + [{N["sessao"]: sessao, N["mensagem"]: {N["conteudo"]: c}} for c in conteudos])


def monta_transcricao(sessao, fixos):
    """(itens, usos) de uma transcricao: itens sao eventos (dict) ou linhas prontas (bytes), na ordem; cada uso vem
    antes do resultado dele, e o ruido, as linhas que nao se leem e as em branco, cada uma ao menos uma vez, ficam no
    meio."""
    sorteados = [(SORTE.choice(list(CAMPOS) + [N["estranha"]]), SORTE.choice([PEDIDO, PEDIDO, MESMO_NOME, OUTRO]),
                  SORTE.choice([None, "texto", "lista"])) for _ in range(SORTE.randint(3, 8))]
    pedidos = list(fixos) + sorteados
    SORTE.shuffle(pedidos)
    itens, usos, pendentes = [], [], []
    for ferramenta, caminho, forma in pedidos:
        evento, dados = uso(ferramenta, caminho, todos=(ferramenta, caminho, forma) in fixos)
        evento[N["sessao"]] = sessao
        itens.append(evento)
        usos.append(dados)
        if forma:
            pendentes.append((dados, forma == "lista"))
        while pendentes and SORTE.random() < 0.5:
            itens.append(resultado(*pendentes.pop(SORTE.randrange(len(pendentes)))))
    itens += [resultado(*p) for p in pendentes]
    extras = ruido(sessao) + RUINS + BRANCAS + [SORTE.choice(RUINS + BRANCAS) for _ in range(SORTE.randint(0, 4))]
    for extra in extras:
        itens.insert(SORTE.randrange(len(itens) + 1), extra)
    return itens, usos


def grava_transcricoes(pasta):
    """Grava as transcricoes inventadas na pasta, na codificacao da configuracao, e um arquivo de outro nome com um uso
    no arquivo pedido; devolve (usos, linhas que nao se leem): cada uso com a hora, a sessao, a transcricao e a linha;
    as horas, unicas, sao sorteadas fora da ordem das linhas."""
    todos, ruins = [], []
    fixos = obrigatorios()
    por_transcricao = [fixos[k::len(TRANSCRICOES)] for k in range(len(TRANSCRICOES))]
    montadas = []
    for nome, seus in zip(TRANSCRICOES, por_transcricao):
        sessao = nova()
        itens, usos = monta_transcricao(sessao, seus)
        montadas.append((nome, sessao, itens, usos))
    eventos = [i for _, _, itens, _ in montadas for i in itens if isinstance(i, dict)]
    horas = set()
    while len(horas) < len(eventos):
        horas.add(f"2031-{SORTE.randint(1, 12):02d}-{SORTE.randint(1, 28):02d}T{SORTE.randint(0, 23):02d}:"
                  f"{SORTE.randint(0, 59):02d}:{SORTE.randint(0, 59):02d}.{SORTE.randint(0, 999):03d}Z")
    horas = sorted(horas)
    SORTE.shuffle(horas)
    for evento, hora in zip(eventos, horas):
        evento[N["hora"]] = hora
    for nome, sessao, itens, usos in montadas:
        arquivo = pasta / nome
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        linhas, por_evento = [], {id(d["evento"]): d for d in usos}
        for numero, item in enumerate(itens, 1):
            if isinstance(item, dict):
                linhas.append(json.dumps(item, ensure_ascii=False).encode(CODIFICACAO))
                if id(item) in por_evento:
                    por_evento[id(item)]["linha"] = numero
            else:
                linhas.append(item)
                if item.strip():
                    ruins.append((nome, numero))
        arquivo.write_bytes(b"\n".join(linhas) + b"\n")
        todos += [dict(d, sessao=sessao, transcricao=nome, hora=d["evento"][N["hora"]]) for d in usos]
    evento, _ = uso(N["le"], PEDIDO, todos=True)
    (pasta / f"{nova()}.{nova()}").write_bytes(json.dumps(evento, ensure_ascii=False).encode(CODIFICACAO) + b"\n")
    return todos, ruins


def rodar(*argumentos):
    return subprocess.run([sys.executable, "-I", "-B", str(PROGRAMA), *map(str, argumentos)], capture_output=True,
                          text=True)


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


def tabela(caminho):
    """As linhas de uma tabela da saida, pelos rotulos; nenhuma, quando o arquivo nao existe."""
    if not caminho.is_file():
        return []
    with caminho.open(encoding=SAIDA["codificacao"], newline="") as arquivo:
        return list(csv.DictReader(arquivo, delimiter="\t"))


def depois_do_titulo(conteudo, titulo):
    """O que vem no arquivo de um achado depois da linha do titulo de uma secao; None, quando ela nao esta la."""
    linha = f"\n{SAIDA['secao']['antes']}{titulo}{SAIDA['secao']['depois']}\n"
    return conteudo.split(linha, 1)[1] if linha in conteudo else None


def tem_valor(conteudo, campo, valor):
    """Se a secao do campo traz o valor: ele mesmo, quando e texto; senao, o JSON dele."""
    depois = depois_do_titulo(conteudo, campo)
    if depois is None:
        return False
    if isinstance(valor, str):
        return depois.startswith(valor + "\n")
    try:
        return json.JSONDecoder().raw_decode(depois)[0] == valor
    except json.JSONDecodeError:
        return False


def confere_achados(saida, esperados, caso):
    """Confere a lista e o arquivo de cada achado contra os usos esperados, na ordem do tempo, e que a pasta de saida
    nao tem nada mais."""
    lista = tabela(saida / SAIDA["lista"])
    nomes = {SAIDA["lista"], SAIDA["ilegiveis"]} | {str(linha.get(ROT["arquivo"])) for linha in lista}
    confere(sorted(p.name for p in saida.iterdir()) == sorted(nomes), f"{caso}: a pasta de saída tem outros arquivos")
    if not confere(len(lista) == len(esperados), f"{caso}: {len(lista)} achados, esperados {len(esperados)}"):
        return
    for linha, uso_ in zip(lista, esperados):
        onde = f"{caso}: achado {linha.get(ROT['numero'])}"
        dados = {"sessao": uso_["sessao"], "hora": uso_["hora"], "ferramenta": uso_["ferramenta"],
                 "caminho": uso_["caminho"], "transcricao": uso_["transcricao"], "linha": str(uso_["linha"])}
        confere(all(linha.get(ROT[chave]) == valor for chave, valor in dados.items()),
                f"{onde}: dados {linha} != {dados}")
        arquivo = saida / str(linha.get(ROT["arquivo"]))
        confere(arquivo.name.endswith(SAIDA["extensao"]), f"{onde}: o arquivo não tem a extensão da configuração")
        conteudo = arquivo.read_text(encoding=SAIDA["codificacao"]) if arquivo.is_file() else ""
        linhas = conteudo.split("\n")
        confere(all(f"{ROT[chave]}{SAIDA['separador']}{valor}" in linhas for chave, valor in dados.items()),
                f"{onde}: o arquivo não traz os dados do uso com os rótulos da configuração")
        campos = [c for c in CAMPOS[uso_["ferramenta"]] if c in uso_["entrada"]]
        confere(all(tem_valor(conteudo, c, uso_["entrada"][c]) for c in campos), f"{onde}: falta um campo da entrada")
        confere(uso_["entrada"][N["escondido"]] not in conteudo, f"{onde}: traz um campo que a configuração não diz")
        depois = depois_do_titulo(conteudo, ROT["resultado"])
        if uso_["ferramenta"] in COM_RESULTADO:
            esperado = SAIDA["sem_resultado"] if uso_["resultado"] is None else uso_["resultado"]
            confere(depois is not None and depois.startswith(esperado + "\n"),
                    f"{onde}: o resultado não é {esperado!r}")
        else:
            confere(depois is None and (uso_["resultado"] is None or uso_["resultado"] not in conteudo),
                    f"{onde}: o resultado aparece numa ferramenta que não o pede")


def arquivos_de(pasta):
    return {p.relative_to(pasta).as_posix(): p.read_bytes() for p in sorted(pasta.rglob("*")) if p.is_file()}


TRABALHO.mkdir(parents=True)
PASTA = TRABALHO / "transcricoes"
USOS, RUINS_ESPERADAS = grava_transcricoes(PASTA)
CONFIGURACAO = TRABALHO / "cfg.json"
CONFIGURACAO.write_text(json.dumps(CONFIG, ensure_ascii=False), encoding="utf-8")
ACHAVEIS = [u for u in USOS if u["ferramenta"] in CAMPOS]


def esperados(caminhos):
    return sorted((u for u in ACHAVEIS if u["caminho"] in caminhos), key=lambda u: u["hora"])


for caso, argumentos, caminhos in [("pelo caminho", ["--arquivo", PEDIDO], {PEDIDO}),
                                   ("pelo nome", ["--arquivo", NOME, "--pelo-nome"], {PEDIDO, MESMO_NOME})]:
    saida = TRABALHO / f"saida-{len(caminhos)}"
    rodada = rodar("--config", CONFIGURACAO, "--transcricoes", PASTA, *argumentos, "--saida", saida)
    if confere(rodada.returncode == 0, f"{caso}: saiu com {rodada.returncode}: {rodada.stderr.strip()}"):
        confere_achados(saida, esperados(caminhos), caso)
        ilegiveis = [(linha.get(ROT["transcricao"]), int(linha.get(ROT["linha"]) or 0))
                     for linha in tabela(saida / SAIDA["ilegiveis"])]
        confere(sorted(ilegiveis) == sorted(RUINS_ESPERADAS),
                f"{caso}: linhas que não se leram {sorted(ilegiveis)} != {sorted(RUINS_ESPERADAS)}")

DE_NOVO = TRABALHO / "de-novo"
rodar("--config", CONFIGURACAO, "--transcricoes", PASTA, "--arquivo", PEDIDO, "--saida", DE_NOVO)
confere(DE_NOVO.is_dir() and arquivos_de(DE_NOVO) == arquivos_de(TRABALHO / "saida-1"), "duas rodadas dão o mesmo")


def com(chaves, valor):
    """Uma copia da configuracao com o valor no lugar das chaves dadas."""
    copia = json.loads(json.dumps(CONFIG))
    alvo = copia
    for chave in chaves[:-1]:
        alvo = alvo[chave]
    alvo[chaves[-1]] = valor
    return copia


VAZIA = TRABALHO / "vazia"  # uma pasta sem transcricao nenhuma
VAZIA.mkdir()
SEM = SORTE.choice([c for c in CONFIG if c != "versao_schema"])  # um dos campos que o script le
ERROS = {
    "configuração com campo desconhecido": (dict(CONFIG, **{nova(): 1}), PASTA),
    f"configuração sem o campo {SEM}": ({c: v for c, v in CONFIG.items() if c != SEM}, PASTA),
    "codificação das transcrições que não existe": (com(["transcricoes", "codificacao"], nova()), VAZIA),
    "codificação da saída que não existe": (com(["saida", "codificacao"], nova()), PASTA),
    "dois arquivos da saída com o mesmo nome": (com(["saida", "ilegiveis"], SAIDA["lista"]), PASTA),
}
for numero, (caso, (dados, transcricoes)) in enumerate(ERROS.items()):
    configuracao, saida = TRABALHO / f"cfg-{numero}.json", TRABALHO / f"saida-erro-{numero}"
    configuracao.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    rodada = rodar("--config", configuracao, "--transcricoes", transcricoes, "--arquivo", PEDIDO, "--saida", saida)
    confere(rodada.returncode != 0 and not saida.exists(), f"{caso} dá erro e não cria a pasta de saída")
SEM_PASTA = TRABALHO / "saida-sem-pasta"
confere(rodar("--config", CONFIGURACAO, "--transcricoes", TRABALHO / "nao-existe", "--arquivo", PEDIDO,
              "--saida", SEM_PASTA).returncode != 0 and not SEM_PASTA.exists(),
        "pasta das transcrições que não existe dá erro e não cria a pasta de saída")
ANTES = arquivos_de(DE_NOVO)
confere(rodar("--config", CONFIGURACAO, "--transcricoes", PASTA, "--arquivo", PEDIDO,
              "--saida", DE_NOVO).returncode != 0 and arquivos_de(DE_NOVO) == ANTES,
        "pasta de saída que já existe dá erro e fica como estava")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
