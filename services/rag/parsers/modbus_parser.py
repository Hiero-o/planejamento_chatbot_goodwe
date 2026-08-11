import re 


SINGLE_ADDRESS_PATTERN = re.compile(r"^\s*(\d{5,6})\b") #Objeto de expressão regular, procura numeros de 5 a 6 digitos
# ^ - indica o inicio da linha.

RANGE_ADDRESS_PATTERN = re.compile(r"^\s*(\d{5,6})\s*-\s*(\d{5,6})\b") # Para aceitar valores após o hífem(-) tipo 12345 - 123456
#
#\s* - procura por espaços em branco. o * significa zero ou mais vezes. aceita se tiver espaços antes dos numeros, mas funciona se nao tiver nenhum tbm
#(\d{5,6}) - grupo de captura, busca por numeros.
#\d - qualquer numero de 0 a 9
#{5,6} : quantidade de numeros. sequencias de no minimo 5 r no maximo 6 digitos seguidos (12345 ou 123456).
#(?!\b) - Negative Lookahead (Olhar para frente negativo). valida uma condição sem "consumir texto"
#\b - fronteira de palavra, limite onde terminam letras/numeros e começam espaços e pontuações.
#?! - nega isso, exigindo que o numero de 5 ou 6 digitos NÃO termine em uma fronteira de palavra.


# text: - o nome da variável que afunção vai receber
# str - tipo (string). esperado um texto
# -> seta para indicar o tipo de dado que a função vai receber, no caso, dict ou None se não encontrar nada
# bool: tipo de dado booleano (true, false)
#.match() - Comando que testa se a regra de busca encaixa logo no inicio do texto

#if range_match: se encontrou padrão, executa
#range_match.group(1) - pega o primeiro numero encontrado
#range_match.group(2) - pega o segundo numero encontrado
#o int antes serve para transformar a string em numero inteiros
#"address": f"{start} - {end}" - reconstroi o texto formatado, guarda os numeros inteiros separados (star e end) e categoriza eles como "range"



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


# lines = page["texto"].splitlines() : Acessa o texto bruto da página e usa o .splitlines() para quebrar esse textão em uma lista de linhas individuais, separando onde quer que haja uma quebra de linha (\n).

#for line in lines : Um laço que lê linha por linha da lista lines criada.

#line = line.strip() retira espaços em branco inuteis do começo e do final, mantendo espaços internos.

#if not in line: continue : se a linha estiver vazia após o strip(), o comando continue faz pular o código e ir para a próxima linha.

# if current_record is not None : antes de criar o novo bloco, o python olha para trás, se o current_record não estiver vazio, significa que estávamos preenchendo um bloco anterior.

#records.append(current_record) : salva o bloco anterior que acabou de terminar, colocando-o dentro da lista final records.

# current_record = {} : Reinicia a variável criando um dincionario novinho em folha para oo atual endereço, preenchendo os dados da página, extraindo o numero do endereço com extract_address(line) e guardando a linha inteira em "texto".

#elif current_record is not None: se a linha atual nao começa com um endereço MODBUS, o python para. Ele verifica se já existe um bloco aberto (current_record is not None)
# current_record["texto"] += "\n" + line: se hpouver bloco aberto, significa que essa linha é a continuação do registro anterior (por exemplo, a descrição do registrador MODBUS que quebrou em duas ou mais linhas). o operador += junta a nova linha ao texto que já estava guardado, separando por um \n.

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

        if address is not None:

            if current_record is not None:
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

    if current_record is not None:
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

