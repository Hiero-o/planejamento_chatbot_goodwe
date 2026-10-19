import re


# Aceita endereços isolados, sem texto adicional na linha.
SINGLE_ADDRESS_PATTERN = re.compile(
    r"^\s*(\d{5,6})\s*$"
)

# Aceita intervalos isolados, sem texto adicional na linha.
RANGE_ADDRESS_PATTERN = re.compile(
    r"^\s*(\d{5,6})\s*-\s*(\d{5,6})\s*$"
)

MODBUS_ACCESS_TYPES = {"RO", "WO", "RW"}

MODBUS_DATA_TYPES = {
    "STR",
    "S16",
    "U16",
    "S32",
    "U32",
}


def detect_address(text: str) -> dict | None:
    """
    Detecta um endereço MODBUS no início de uma linha.

    Aceita endereços individuais, como 10020,
    e intervalos, como 10109 - 10112.
    A linha deve conter somente o endereço ou intervalo.
    """
    range_match = RANGE_ADDRESS_PATTERN.fullmatch(text)

    if range_match:
        start = int(range_match.group(1))
        end = int(range_match.group(2))

        return {
            "address": f"{start} - {end}",
            "address_start": start,
            "address_end": end,
            "address_type": "range",
        }

    single_match = SINGLE_ADDRESS_PATTERN.fullmatch(text)

    if single_match:
        address = int(single_match.group(1))

        return {
            "address": str(address),
            "address_start": address,
            "address_end": address,
            "address_type": "single",
        }

    return None


def parse_register_metadata(text: str) -> dict:
    """
    Extrai os metadados estruturais de um registro MODBUS.

    Os campos técnicos podem estar na mesma linha ou
    distribuídos em linhas separadas durante a extração
    do PDF.
    """
    result = {
        "access": None,
        "data_type": None,
        "size": None,
        "scale_factor": None,
        "unit": None,
        "range": None,
        "flash_save": None,
    }

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return result

    # Encontra a linha e a posição do campo de acesso.
    access_line_index = None
    access_token_index = None

    for line_index, line in enumerate(lines):
        tokens = line.split()

        for token_index, token in enumerate(tokens):
            if token in MODBUS_ACCESS_TYPES:
                access_line_index = line_index
                access_token_index = token_index
                break

        if access_line_index is not None:
            break

    if access_line_index is None:
        return result

    access_tokens = lines[access_line_index].split()

    result["access"] = access_tokens[access_token_index]

    # Reúne os tokens que aparecem depois do acesso,
    # inclusive os distribuídos pelas linhas seguintes.
    tokens = access_tokens[access_token_index + 1:]

    for line in lines[access_line_index + 1:]:
        tokens.extend(line.split())

    if not tokens:
        return result

    # Tipo de dado.
    data_type = tokens.pop(0)

    if data_type in MODBUS_DATA_TYPES:
        result["data_type"] = data_type
    else:
        # Não inventa metadados se o tipo não for reconhecido.
        return result

    # Tamanho, fator de escala e unidade.
    metadata_fields = [
        "size",
        "scale_factor",
        "unit",
    ]

    for field in metadata_fields:
        if tokens:
            result[field] = tokens.pop(0)

    # Intervalo permitido, quando presente.
    if tokens and re.fullmatch(r"\[[^\]]+\]", tokens[0]):
        result["range"] = tokens.pop(0)

    # Indicação de persistência, quando presente.
    if tokens and tokens[0] in {"Y", "N"}:
        result["flash_save"] = tokens.pop(0)

    return result


def parse_register_page(page: dict) -> list[dict]:
    """
    Agrupa o conteúdo de uma página MODBUS em registros.

    Cada novo endereço detectado inicia um registro.
    O texto posterior é acumulado até o próximo endereço.
    """
    lines = page["texto"].splitlines()

    records = []
    current_record = None

    for line in lines:
        line = line.strip()

        if not line:
            continue

        address = detect_address(line)

        if address is not None:
            if current_record is not None:
                current_record.update(
                    parse_register_metadata(
                        current_record["texto"]
                    )
                )

                records.append(current_record)

            current_record = {
                "tipo": "modbus_register",
                "documento": page["documento"],
                "pagina": page["pagina"],
                "address": address["address"],
                "address_start": address["address_start"],
                "address_end": address["address_end"],
                "address_type": address["address_type"],
                "texto": line,
            }

        elif current_record is not None:
            current_record["texto"] += "\n" + line

    # Processa o último registro da página.
    if current_record is not None:
        current_record.update(
            parse_register_metadata(
                current_record["texto"]
            )
        )

        records.append(current_record)

    return records


def parse_modbus_page(page: dict) -> dict:
    """
    Classifica uma página do documento MODBUS.

    Página 1: histórico de versões.
    Página 2: referência do protocolo.
    Página 3 em diante: tabela de registros.
    """
    page_number = page["pagina"]

    if page_number == 1:
        return {
            "tipo": "modbus_version_history",
            "documento": page["documento"],
            "pagina": page_number,
            "texto": page["texto"],
            "registros": [],
        }

    if page_number == 2:
        return {
            "tipo": "modbus_protocol_reference",
            "documento": page["documento"],
            "pagina": page_number,
            "texto": page["texto"],
            "registros": [],
        }

    records = parse_register_page(page)

    return {
        "tipo": "modbus_register_table",
        "documento": page["documento"],
        "pagina": page_number,
        "texto": page["texto"],
        "registros": records,
    }