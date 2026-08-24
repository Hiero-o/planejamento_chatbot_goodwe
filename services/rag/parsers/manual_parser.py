import re

MANUAL_TOC_PATTERN = re.compile(
    r"^(\d+(?:\.\d+)*)\s+(.+?)\s*\.{2,}\s*(\d+)\s*$"
)
# essa regex vai entender as seções, EX:
#1
#1.1
#1.2.1
#...
#(.+?) pega o título
#(\d+)\s*$ pega o numero da pagina do indice.

def parse_manual_toc_page(page: dict) -> list[dict]:
    """
    Extrai entradas do índice do User Manual.
    
    Exemplo:
    3.6.1 Descrição das peças ............... 12

    reotrna {
    "secao": "3.6.1",
    "titulo": "descrição das peças",
    "pagina_manual": 12,
    }
    """

    entradas = []

    lines = page["texto"].splitlines()

    pending_line = None

    for line in lines:

        line = line.strip()

        if not line:
            continue
        # se tiver uma linha pendente, junta com a atual
        if pending_line is not None:
            line = pending_line + " " + line
            pending_line = None

        match = MANUAL_TOC_PATTERN.match(line)

        if not match:
            #Veririca se parece ser uma entrada de índice,
            #mas está sem a página no final da linha
            possible_section = re.match(
                r"^(\d+(?:\.\d+)*)\s+",
                line
            )

            if possible_section:
                pending_line = line
            continue
        

        secao =match.group(1)
        titulo = match.group(2).strip()
        pagina_manual = int(match.group(3))

        titulo = re.sub(r"\.{2,}\s*$", "", titulo).strip()

        entradas.append(
            {
            "secao": secao,
            "titulo": titulo,
            "pagina_manual": pagina_manual,
            }
        )
        
    return entradas


