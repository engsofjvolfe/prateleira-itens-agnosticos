"""Um PDF montado aqui, para os testes: paginas com linhas de texto em fontes padrao do PDF,
na camada de texto e na imagem, ou so na camada de texto (texto invisivel)."""

FONTES = {"F1": ("Helvetica", []), "F2": ("Times-Bold", ["forte"]), "F3": ("Courier-Oblique", ["inclinado"]),
          "F4": ("Helvetica-Bold", ["forte"]), "F5": ("Times-BoldItalic", ["forte", "inclinado"])}
"""Cada fonte: o nome dela no PDF e os destaques que ela tem, com nomes inventados."""


def literal(texto):
    """O texto como literal de uma string do PDF: a barra e os parenteses escapados."""
    return texto.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def pdf_inventado(paginas):
    """Um PDF com as fontes de FONTES: cada pagina e uma lista de (tamanho, x, y, texto,
    invisivel), em que o texto e uma linha so em F1 ou uma lista de (fonte, pedaco); o
    texto invisivel fica so na camada de texto, sem aparecer na imagem."""
    fontes = " ".join(f"/{nome} << /Type /Font /Subtype /Type1 /BaseFont /{base} /Encoding /WinAnsiEncoding >>"
                      for nome, (base, _) in FONTES.items())
    objetos = {1: b"<< /Type /Catalog /Pages 2 0 R >>", 3: f"<< {fontes} >>".encode()}
    filhos = " ".join(f"{4 + 2 * i} 0 R" for i in range(len(paginas)))
    objetos[2] = f"<< /Type /Pages /Kids [{filhos}] /Count {len(paginas)} >>".encode()
    for i, linhas in enumerate(paginas):
        ops = []
        for tamanho, x, y, texto, invisivel in linhas:
            pedacos = [("F1", texto)] if isinstance(texto, str) else texto
            escrito = " ".join(f"/{fonte} {tamanho} Tf ({literal(s)}) Tj" for fonte, s in pedacos)
            ops.append(f"BT {3 if invisivel else 0} Tr {x} {y} Td {escrito} ET")
        fluxo = "\n".join(ops).encode("cp1252")
        objetos[5 + 2 * i] = b"<< /Length %d >>\nstream\n" % len(fluxo) + fluxo + b"\nendstream"
        objetos[4 + 2 * i] = (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font "
                              f"3 0 R >> /Contents {5 + 2 * i} 0 R >>").encode()
    saida, lugares = b"%PDF-1.4\n", {}
    for k in sorted(objetos):
        lugares[k] = len(saida)
        saida += f"{k} 0 obj\n".encode() + objetos[k] + b"\nendobj\n"
    xref, total = len(saida), max(objetos) + 1
    saida += f"xref\n0 {total}\n0000000000 65535 f \n".encode()
    saida += b"".join(f"{lugares[k]:010d} 00000 n \n".encode() for k in range(1, total))
    return saida + f"trailer\n<< /Size {total} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()


def pagina_de_linhas(linhas, tamanho, passo):
    """As linhas uma embaixo da outra, do alto da pagina, a partir da margem."""
    return [(tamanho, 72, 750 - k * passo, l, False) for k, l in enumerate(linhas)]
