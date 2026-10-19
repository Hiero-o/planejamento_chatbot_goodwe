import re


MANUAL_TOC_PATTERN = re.compile(
    r"^(\d+(?:\.\d+)*)\s+(.+?)\s*(?:\.|…|·|•|\ufffd){2,}\s*(\d+)\s*$"
)


def parse_manual_toc_page(page: dict) -> list[dict]:
    """
    Extrai as entradas do índice do manual do usuário.

    Retorna uma lista de dicionários com:
    - secao: número da seção
    - titulo: título da seção
    - pagina_manual: número da página indicado no índice
    """

    entradas = []
    lines = page["texto"].splitlines()
    pending_line = None

    for line in lines:
        # Remove caracteres de controle que podem aparecer
        # no texto extraído pelo PyMuPDF.
        line = re.sub(
            r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]",
            " ",
            line,
        ).strip()

        if not line:
            continue

        # Se a entrada anterior foi dividida entre linhas,
        # junta a linha pendente com a linha atual.
        if pending_line is not None:
            line = pending_line + " " + line
            pending_line = None

        match = MANUAL_TOC_PATTERN.match(line)

        if not match:
            # Verifica se a linha parece começar uma seção,
            # mas ainda não contém todos os dados do índice.
            possible_section = re.match(
                r"^(\d+(?:\.\d+)*)\s+",
                line,
            )

            if possible_section:
                pending_line = line

            continue

        secao = match.group(1)
        titulo = match.group(2).strip()
        pagina_manual = int(match.group(3))

        # Remove eventuais separadores que tenham sobrado
        # no final do título.
        titulo = re.sub(
            r"(?:\.|…|·|•|\ufffd){2,}\s*$",
            "",
            titulo,
        ).strip()

        entradas.append(
            {
                "secao": secao,
                "titulo": titulo,
                "pagina_manual": pagina_manual,
            }
        )

    return entradas