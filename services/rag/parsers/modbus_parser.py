import re 

ADDRESS_PATTERN = re.compile(r"^\s*(\d{4,6})\b") #Objeto de expressão regular, procura numeros de 4 a 6 digitos, no inicio da string, permitindo espaços antes do numero

#re.compile : prepara e traduz a regra de texto para um formato rapido de usar no python
#r".." : usa uma string crua "raw string" para evitar problemas com barras invertidas
#^ : exige que a regra comece bem no inicio da linha do texto
#\s* : aceita zero ou mais espaços vazios no começo
#(\d{4,6}) : Um grupo que captura apenas numeros (\d), contando de 4 a 6 vezes o tamanho
#\b : marca o fim da palavra (fronteira de palavra),  garantindo que o numero não continue colado a outros digitos ou letras

# def - definir funções
# is_address_start - nome da função
# text: - o nome da variável que afunção vai receber
# str - tipo (string). esperado um texto
# -> seta para indicar o tipo de dado que a função vai receber, no caso, bool
# bool: tipo de dado booleano (true, false)
#.match() - Comando que testa se a regra de busca encaixa logo no inicio do texto
#is not none - Se não encontrar nada, devolve None, como None is not None é falso, a expressão se torna falsa
def is_address_start(text: str) -> bool:
    """
    Verifica se uma linha inicia um novo registro MODBUS.
    
    Exemplos: 
        10020 Reservation Status...
        10021 Reservation Start Time...
    """

# -> | None : indica que a função devolve int ou None
# match.group(1) - Quando a expressão encontra o padrão, o group(1) pega especificamente o numero que vai ficar dentro do primeiro par de parenteses 
# da regra (\d{4,6}). Ignora os espaços do começo (\s*) e isola apenas o texto dos digitos.
# como o group(1) devolve o numero em str (string), o int() transforma o texto em um numero inteiro real.

    return ADDRESS_PATTERN.match(text) is not None

def extract_address(text: str) -> int | None:
    """
    Extrai o endereço MODBUS do início da linha.
    """

    match = ADDRESS_PATTERN.match(text)

    if not match:
        return None

    return int(match.group(1))


# lines = page["texto"].splitlines() : Acessa o texto bruto da página e usa o .splitlines() para quebrar esse textão em uma lista de linhas individuais, separando onde quer que haja uma quebra de linha (\n).

#for line in lines : Um laço que lê linha por linha da lista lines criada.

#line = line.strip() retira espaços em branco inuteis do começo e do final, mantendo espaços internos.

#if not in line: continue : se a linha estiver vazia após o strip(), o comando continue faz pular o código e ir para a próxima linha.

# if current_record is not None : antes de criar o novo bloco, o python olha para trás, se o current_record não estiver vazio, significa que estávamos preenchendo um bloco anterior.

#records.append(current_record) : salva o bloco anterior que acabou de terminar, colocando-o dentro da lista final records.

# current_record = {} : Reinicia a variável criando um dincionario novinho em folha para oo atual endereço, preenchendo os dados da página, extraindo o numero do endereço com extract_address(line) e guardando a linha inteira em "texto".

#elif current_record is not None: se a linha atual nao começa com um endereço MODBUS, o python para. Ele verifica se já existe um bloco aberto (current_record is not None)
# current_record["texto"] += "\n" + line: se hpouver bloco aberto, significa que essa linha é a continuação do registro anterior (por exemplo, a descrição do registrador MODBUS que quebrou em duas ou mais linhas). o operador += junta a nova linha ao texto que já estava guardado, separando por um \n.

def parse_modbus_page(page: dict) -> list[dict]:
    """
    Agrupa o conteúdo de uma página MODBUS em registros.
    
    Um novo registro começa quando encontramos um novo endereço MODBUS no início de uma linha.
    
    Neste primeiro estágio, não interpretamos as colunas. Apenas preservamos o texto original.
    """

    lines = page["texto"].splitlines()

    records = []
    current_record = None
    for line in lines:
        line = line.strip()

        if not line:
            continue

        if is_address_start(line):
            if current_record is not None:
                records.append(current_record)

            current_record = {
                "tipo": "modbus_register",
                "documento": page["documento"],
                "pagina": page["pagina"],
                "address": extract_address(line),
                "texto": line,
                }
            
        elif current_record is not None:
            current_record["texto"] += "\n" + line

    if current_record is not None:
        records.append(current_record)

    return records
