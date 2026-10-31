"""
Mostra o uso de tokens de cada transcricao de sessao, como as dos agentes de um programa de IA:
quantos turnos trazem o uso, o maior contexto de um turno, o total processado (contexto
mais saida, somados em todos os turnos), o total de saida e o comeco da primeira pergunta.
Um turno e um evento cuja mensagem traz o uso; o contexto dele e a soma dos campos de
entrada do uso, e campo que falta, ou que nao e numero inteiro, vale 0.

Os nomes dos campos, o padrao dos arquivos, a codificacao, o tamanho do comeco e os rotulos
das colunas vem da configuracao, lida pelo molde dela com o extrator_comum.py, da peca
extrator. As transcricoes (os arquivos da pasta e das subpastas que seguem o padrao) sao
lidas pelo transcricoes.py, da peca historico-de-arquivo, que pula a linha que nao e um
objeto JSON. As duas pecas ficam nas pastas irmas "extrator" e "historico-de-arquivo", ou na
mesma pasta.

Escreve na tela uma tabela separada por tabulacao: o cabecalho e uma linha por transcricao
que tem alguma linha, na ordem do caminho; no comeco, cada trecho de espacos (com quebras de
linha e tabulacoes) vira um espaco, pelo texto_comum.py, da peca extrator. Sai com 0, ou com
2 quando a configuracao ou a pasta nao serve.

Uso:
    python3 -I custo.py <configuracao.json> <pasta das transcricoes>
"""

import argparse
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
# as pecas irmas, na prateleira, ou a mesma pasta, numa copia fora da prateleira
for pasta in (PASTA.parent / "extrator", PASTA.parent / "historico-de-arquivo", PASTA):
    sys.path.insert(0, str(pasta))
from extrator_comum import ErroDeDados, codificacao, le_conferido  # noqa: E402
from texto_comum import espacos_juntos  # noqa: E402
from transcricoes import eventos  # noqa: E402

MOLDE = PASTA / "esquemas" / "custo-de-agentes.schema.json"
# a ordem das colunas; os rotulos delas vem da configuracao
COLUNAS = ("transcricao", "turnos", "contexto_maximo", "processado", "saida", "comeco")
SEPARADOR = "\t"


def le_configuracao(caminho):
    """A configuracao, conferida contra o molde; a codificacao que nao existe, que o molde nao
    ve, e erro aqui."""
    dados = le_conferido(caminho, MOLDE)
    eventos_, uso = dados["eventos"], dados["uso"]
    return {"padrao": dados["transcricoes"]["padrao"], "codificacao": codificacao(dados, "transcricoes/codificacao"),
            "tipo": eventos_["tipo"], "pergunta": eventos_["pergunta"], "mensagem": eventos_["mensagem"],
            "conteudo": eventos_["conteudo"], "uso": eventos_["uso"], "entrada": uso["entrada"], "saida": uso["saida"],
            "letras": dados["comeco"]["letras"], "rotulos": [dados["colunas"][c] for c in COLUNAS]}


def numero(uso, nome):
    """O numero inteiro do campo do uso; 0 quando falta ou nao e numero inteiro (um booleano nao conta)."""
    valor = uso.get(nome, 0)
    return valor if isinstance(valor, int) and not isinstance(valor, bool) else 0


def custo(pasta, conf):
    """{transcricao: {coluna: valor}} de cada transcricao com alguma linha, na ordem do caminho."""
    tabela = {}
    for transcricao, _, evento in eventos(pasta, conf["padrao"], conf["codificacao"]):
        linha = tabela.setdefault(transcricao, {"turnos": 0, "contexto_maximo": 0, "processado": 0, "saida": 0,
                                                "comeco": None})
        mensagem = evento.get(conf["mensagem"]) if evento is not None else None
        if not isinstance(mensagem, dict):
            continue
        texto = mensagem.get(conf["conteudo"])
        if linha["comeco"] is None and evento.get(conf["tipo"]) == conf["pergunta"] and isinstance(texto, str):
            linha["comeco"] = espacos_juntos(texto)[:conf["letras"]]
        uso = mensagem.get(conf["uso"])
        if isinstance(uso, dict):
            contexto, saida = sum(numero(uso, c) for c in conf["entrada"]), numero(uso, conf["saida"])
            linha["turnos"] += 1
            linha["contexto_maximo"] = max(linha["contexto_maximo"], contexto)
            linha["processado"] += contexto + saida
            linha["saida"] += saida
    return tabela


def main(argv=None):
    p = argparse.ArgumentParser(description="Mostra o uso de tokens de cada transcrição de sessão.")
    p.add_argument("configuracao", type=Path)
    p.add_argument("pasta", type=Path, help="a pasta das transcrições")
    a = p.parse_args(argv)
    if not a.pasta.is_dir():
        print(f"ERRO: a pasta {a.pasta} não existe")
        return 2
    try:
        conf = le_configuracao(a.configuracao)
    except ErroDeDados as e:
        print(f"ERRO: {e}")
        return 2
    print(SEPARADOR.join(conf["rotulos"]))
    for transcricao, linha in custo(a.pasta, conf).items():
        valores = dict(linha, transcricao=transcricao.relative_to(a.pasta).as_posix(), comeco=linha["comeco"] or "")
        print(SEPARADOR.join(str(valores[c]) for c in COLUNAS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
