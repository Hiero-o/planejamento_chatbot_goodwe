import re 


SINGLE_ADDRESS_PATTERN = re.compile(r"^\s*(\d{5,6})\b") #Objeto de expressão regular, procura numeros de 5 a 6 digitos
# ^ - indica o inicio da linha.

RANGE_ADDRESS_PATTERN = re.compile(r"^\s*(\d{5,6})\s*-\s*(\d{5,6})\b") # Para aceitar valores após o hífem(-) tipo 12345 - 123456

#\s* - procura por espaços em branco. o * significa zero ou mais vezes. aceita se tiver espaços antes dos numeros, mas funciona se nao tiver nenhum tbm
#(\d{5,6}) - grupo de captura, busca por numeros.
#\d - qualquer numero de 0 a 9
#{5,6} : quantidade de numeros. sequencias de no minimo 5 r no maximo 6 digitos seguidos (12345 ou 123456).
#(?!\b) - Negative Lookahead (Olhar para frente negativo). valida uma condição sem "consumir texto"
#\b - fronteira de palavra, limite onde terminam letras/numeros e começam espaços e pontuações.
#?! - nega isso, exigindo que o numero de 5 ou 6 digitos NÃO termine em uma fronteira de palavra. # *Desativada*

MODBUS_ACCESS_TYPES = {"RO", "WO", "RW"} # procuraremos padrões com essas silabas

MODBUS_DATA_TYPES = {
    "STR",
    "S16",
    "U16",
    "S32",
    "U32",
} #Mesma coisa para esses valores.



def detect_address(text: str) -> dict | None:
    """
    Detecta um endereço MODBUS no inicio de uma linha.
    
    Suporta: 
        10020
        10021
        300005
        10109 - 10112
    """
    range_match = RANGE_ADDRESS_PATTERN.match(text)

    if range_match:
        start = int(range_match.group(1))
        end = int(range_match.group(2))


        return {
            "address": f"{start} - {end}",
            "address_start": start,
            "address_end": end,
            "address_type": "range",
        }

    single_match = SINGLE_ADDRESS_PATTERN.match(text)

    if single_match:
        address = int(single_match.group(1))

        return{
            "address": str(address),
            "address_start": address,
            "address_end": address,
            "address_type": "single"
        }
    return None

def parse_register_metadata(text: str) -> dict:
    """
    Extrai os metadados estruturais de um registro MODBUS.

    O parser procura o campo RW/RO/WO para identificar onde começam os metadados técnicos.

    Isso permite lidar com nomes que foram quebrados em várias linhas durante a extração do PDF.
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

    lines = [line.strip() 
             for line in text.splitlines() 
             if line.strip()
        ]

    if not lines:
        return result

    
    # Encontrar a linha onde começam os metadados
    

    access_index = None
    access_line_index = None

    for line_index, line in enumerate(lines):
        tokens = line.split()

        for token_index, token in enumerate(tokens):
            if token in MODBUS_ACCESS_TYPES:
                access_index = token_index
                access_line_index = line_index
                break

        if access_index is not None:
            break

    if access_index is None:
        return result

    tokens = lines[access_line_index].split()

    # Access

    result["access"] = tokens[access_index]

    tokens = tokens[access_index + 1:]
    
    # Data type
    

    if tokens:
        token = tokens.pop(0)

        if re.fullmatch(r"[SU]\d+", token) or token == "STR":
            result["data_type"] = token
        else:
            return None

    
    # Size
    

    if tokens:
        result["size"] = tokens.pop(0)

    
    # Scale Factor
  

    if tokens:
        result["scale_factor"] = tokens.pop(0)

   
    # Unit
   

    if tokens:
        result["unit"] = tokens.pop(0)

    
    # Range
   

    if tokens and re.fullmatch(
        r"\[[^\]]+\]",
        tokens[0]
    ):
        result["range"] = tokens.pop(0)

    
    # Flash Save
   

    if tokens and tokens[0] in {"Y", "N"}:
        result["flash_save"] = tokens.pop(0)

    return result


def parse_register_page(page: dict) -> list[dict]:
    """
    Agrupa o conteúdo de uma página MODBUS em registros.
    
    Um novo registro começa quando encontramos um novo endereço MODBUS no início de uma linha com um endereço modbus válido.
    """

    lines = page["texto"].splitlines()

    records = []
    current_record = None
    for line in lines:
        line = line.strip()

        if not line:
            continue
        address = detect_address(line)


##
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
##
        elif current_record is not None:
            current_record["texto"] += "\n" + line

    if current_record is not None:
        current_record.update(
            parse_register_metadata(
                current_record["texto"]
            )
        )
        records.append(current_record)

        

    return records


def parse_modbus_page(page:dict) -> dict:
    """
    Classifica uma página do documento MODBUS.
    
    Página 1:
        Histórico de versões.
    
    Página 2:
        Referência do protocolo e informações sobre erros.
        
    Página 3 em diante:
        Registro MODBUS.
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


