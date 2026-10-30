"""Tira das transcricoes das sessoes cada leitura e cada gravacao de um arquivo, na ordem do tempo.

Uma ferramenta que le ou grava arquivos aparece num evento da transcricao como um uso, com o nome dela e a entrada,
onde esta o caminho do arquivo, e, num evento seguinte da mesma transcricao, como o resultado desse uso, ligado a ele
pelo id. Para cada uso de uma ferramenta da configuracao no arquivo pedido -- pelo caminho inteiro, como a sessao o
escreveu, ou so pelo nome --, o script grava um arquivo de texto com a sessao, a hora, a ferramenta, o caminho, a
transcricao e a linha dela, os campos da entrada que a configuracao diz e, quando ela pede, o texto do resultado.
Grava tambem a lista dos achados, na ordem do tempo, e a das linhas que nao se leram. As transcricoes sao lidas pelo
transcricoes.py, desta pasta.

A configuracao (--config), lida pelo molde dela com o extrator_comum.py, do extrator, que fica na pasta irma, da o
padrao do nome e a codificacao das transcricoes, os nomes dos campos dos eventos, as ferramentas e, da saida, os nomes
dos arquivos, os rotulos, as marcas e a codificacao. Tudo e lido e montado antes de a pasta de saida ser criada: com
erro, ela nao e criada. So biblioteca padrao.
"""
import argparse
import codecs
import csv
import io
import json
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for lugar in (PASTA.parent / "extrator", PASTA):  # na prateleira, o extrator fica na pasta irma
    sys.path.insert(0, str(lugar))
from extrator_comum import ErroDeDados, le_conferido  # noqa: E402
from transcricoes import blocos, eventos  # noqa: E402

MOLDE = PASTA / "esquemas" / "historico-de-arquivo.schema.json"
DADOS = ("sessao", "hora", "ferramenta", "caminho", "transcricao", "linha")  # o que se diz de cada achado, nesta ordem
COLUNAS = ("numero", "arquivo")  # as colunas da lista dos achados antes dos dados de cada um
ONDE = ("transcricao", "linha")  # as colunas da lista das linhas que nao se leram
RESULTADO = "resultado"
QUEBRA, TAB = "\n", "\t"


def ler_configuracao(caminho):
    """A configuracao, lida pelo molde dela, com as ferramentas pelo nome; erro quando ela tem um campo que o molde nao
    conhece ou uma codificacao que nao existe."""
    cfg = le_conferido(Path(caminho).resolve(), MOLDE)
    for codificacao in (cfg["transcricoes"]["codificacao"], cfg["saida"]["codificacao"]):
        try:
            codecs.lookup(codificacao)
        except LookupError:
            raise ErroDeDados(f"{caminho}: a codificação {codificacao!r} não existe") from None
    return dict(cfg, ferramentas={f["nome"]: f for f in cfg["ferramentas"]})


def texto(valor, cfg):
    """O texto de um resultado: ele mesmo, quando e texto; quando e lista, os textos dos blocos que tem um, um por
    linha; senao, a marca de sem resultado."""
    if isinstance(valor, list):
        campo = cfg["eventos"]["texto"]
        return QUEBRA.join(b[campo] for b in valor if isinstance(b, dict) and isinstance(b.get(campo), str))
    return valor if isinstance(valor, str) else cfg["saida"]["sem_resultado"]


def bate(caminho, pedido, pelo_nome):
    """Se o caminho de um uso e o do arquivo pedido: o mesmo texto ou, com pelo_nome, so o mesmo nome."""
    return isinstance(caminho, str) and (Path(caminho).name if pelo_nome else caminho) == pedido


def achado_do_uso(bloco, evento, cfg, pedido, pelo_nome):
    """O achado do bloco, quando ele e o uso de uma ferramenta da configuracao no arquivo pedido; None, senao."""
    ev, uso = cfg["eventos"], cfg["uso"]
    nome, entrada = bloco.get(uso["nome"]), bloco.get(uso["entrada"])
    e_uso = bloco.get(ev["tipo"]) == uso["tipo"] and isinstance(nome, str)
    ferramenta = cfg["ferramentas"].get(nome) if e_uso else None
    if ferramenta is None or not isinstance(entrada, dict) or not bate(entrada.get(uso["caminho"]), pedido, pelo_nome):
        return None
    return {"sessao": str(evento.get(ev["sessao"], "")), "hora": str(evento.get(ev["hora"], "")), "ferramenta": nome,
            "caminho": entrada[uso["caminho"]], "campos": {c: entrada[c] for c in ferramenta["campos"] if c in entrada}}


def achados(cfg, pasta, pedido, pelo_nome):
    """(achados na ordem do tempo, [(transcricao, linha)] das linhas que nao se leram), das transcricoes da pasta e das
    subpastas dela."""
    ev, uso, res, lidas = cfg["eventos"], cfg["uso"], cfg["resultado"], cfg["transcricoes"]
    saida, ilegiveis, esperando = [], [], {}  # esperando: {(transcricao, id do uso): achado que espera o resultado}
    for transcricao, numero, evento in eventos(pasta, lidas["padrao"], lidas["codificacao"]):
        if evento is None:
            ilegiveis.append((transcricao, numero))
            continue
        for posicao, bloco in blocos(evento, ev["mensagem"], ev["conteudo"]):
            ligado = (transcricao, bloco.get(res["id"]))
            if bloco.get(ev["tipo"]) == res["tipo"] and isinstance(ligado[1], str) and ligado in esperando:
                esperando.pop(ligado)[RESULTADO] = texto(bloco.get(res["conteudo"]), cfg)
                continue
            achado = achado_do_uso(bloco, evento, cfg, pedido, pelo_nome)
            if achado is None:
                continue
            achado.update(transcricao=transcricao, linha=numero, posicao=posicao)
            saida.append(achado)
            if cfg["ferramentas"][achado["ferramenta"]]["resultado"]:
                achado[RESULTADO] = cfg["saida"]["sem_resultado"]
                if isinstance(bloco.get(uso["id"]), str):
                    esperando[(transcricao, bloco[uso["id"]])] = achado
    return sorted(saida, key=lambda a: (a["hora"], a["transcricao"], a["linha"], a["posicao"])), ilegiveis


def em_texto(valor):
    """O valor de um campo da entrada como texto: ele mesmo, quando e texto; senao, o JSON dele."""
    return valor if isinstance(valor, str) else json.dumps(valor, ensure_ascii=False, indent=2)


def da_pasta(transcricao, pasta):
    """O caminho da transcricao a partir da pasta dada, com barras."""
    return transcricao.relative_to(pasta).as_posix()


def dados_do_achado(achado, pasta):
    """Os valores, em texto, do que se diz do achado, na ordem de DADOS, com a transcricao a partir da pasta dada."""
    valores = dict(achado, transcricao=da_pasta(achado["transcricao"], pasta))
    return [str(valores[chave]) for chave in DADOS]


def secao(titulo, valor, saida):
    """As linhas de uma secao do arquivo de um achado: uma em branco, o titulo entre as marcas da configuracao e o
    valor."""
    return ["", f"{saida['secao']['antes']}{titulo}{saida['secao']['depois']}", valor]


def texto_do_achado(achado, dados, saida):
    """O arquivo de um achado: os dados dele, cada um depois do rotulo; uma secao para cada campo da entrada e, quando
    a ferramenta pede, uma para o resultado."""
    rotulos = saida["rotulos"]
    linhas = [f"{rotulos[c]}{saida['separador']}{v}" for c, v in zip(DADOS, dados)]
    for campo, valor in achado["campos"].items():
        linhas += secao(campo, em_texto(valor), saida)
    if RESULTADO in achado:
        linhas += secao(rotulos[RESULTADO], achado[RESULTADO], saida)
    return QUEBRA.join(linhas) + QUEBRA


def tabela(colunas, linhas, rotulos):
    """O texto de uma tabela separada por tabulacao: os rotulos das colunas e uma linha por item."""
    texto_da_tabela = io.StringIO()
    escritor = csv.writer(texto_da_tabela, delimiter=TAB, lineterminator=QUEBRA)
    escritor.writerow([rotulos[c] for c in colunas])
    escritor.writerows(linhas)
    return texto_da_tabela.getvalue()


def arquivos_da_saida(lista, ilegiveis, pasta, saida):
    """{nome: conteudo, na codificacao da saida} de cada arquivo da pasta de saida: um por achado, numerado na ordem do
    tempo, a lista dos achados e a das linhas que nao se leram; erro quando dois teriam o mesmo nome."""
    largura, textos, linhas = len(str(len(lista))), [], []
    for numero, achado in enumerate(lista, 1):
        nome, dados = f"{numero:0{largura}d}{saida['extensao']}", dados_do_achado(achado, pasta)
        textos.append((nome, texto_do_achado(achado, dados, saida)))
        linhas.append([numero, nome] + dados)
    textos.append((saida["lista"], tabela(COLUNAS + DADOS, linhas, saida["rotulos"])))
    textos.append((saida["ilegiveis"], tabela(ONDE, [[da_pasta(t, pasta), n] for t, n in ilegiveis],
                                              saida["rotulos"])))
    nomes = [nome for nome, _ in textos]
    repetidos = sorted({nome for nome in nomes if nomes.count(nome) > 1})
    if repetidos:
        raise ErroDeDados(f"mais de um arquivo da saída teria o nome {', '.join(repetidos)}")
    return {nome: conteudo.encode(saida["codificacao"]) for nome, conteudo in textos}


def main(argumentos=None):
    leitor = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    leitor.add_argument("--config", required=True, type=Path,
                        help="JSON com as transcrições, os campos dos eventos, as ferramentas e a saída")
    leitor.add_argument("--transcricoes", required=True, type=Path,
                        help="pasta das transcrições das sessões, lida com as subpastas")
    leitor.add_argument("--arquivo", required=True,
                        help="o caminho do arquivo, como a sessão o escreveu, ou só o nome, com --pelo-nome")
    leitor.add_argument("--pelo-nome", action="store_true", help="acha o arquivo só pelo nome, em qualquer pasta")
    leitor.add_argument("--saida", required=True, type=Path, help="pasta nova para os achados")
    args = leitor.parse_args(argumentos)
    try:
        cfg = ler_configuracao(args.config)
        if not args.transcricoes.is_dir():
            raise ErroDeDados(f"a pasta das transcrições não existe: {args.transcricoes}")
        pasta = args.transcricoes.resolve()
        lista, ilegiveis = achados(cfg, pasta, args.arquivo, args.pelo_nome)
        arquivos = arquivos_da_saida(lista, ilegiveis, pasta, cfg["saida"])
        args.saida.mkdir(parents=True)
    except ErroDeDados as erro:
        sys.exit(f"ERRO: {erro}")
    except FileExistsError:
        sys.exit(f"ERRO: a pasta de saída já existe: {args.saida}")
    for nome, conteudo in arquivos.items():
        (args.saida / nome).write_bytes(conteudo)
    print(f"{len(lista)} achados e {len(ilegiveis)} linhas que não se leram, em {args.saida}")


if __name__ == "__main__":
    main()
