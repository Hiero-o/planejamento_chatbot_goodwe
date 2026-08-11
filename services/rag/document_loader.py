from pathlib import Path

from pypdf import PdfReader

DOCUMENTS_DIR = Path("conhecimento/manuais")

#load_pdf(path: Path) - Abre e lê o pdf do caminho Path (um unico arquivo pdf) e extrai os valores da pagina
#reader = PdfReader(str(path)) - cria um objeto leitor do pdf. transforma o caminho do arquivo em texto (string) para que a biblioteca consiga ler o documento
#pages = [] - Cria uma lista vazia
#for page_number, page in... - inicia o loop para percorrer todas as paginas do pdf
#enumerate(reader.pages, start=1) - conta as paginas começando do 1 em vez do zero. o numero atual fica na var page_number
#text = page.extract_text() or "" - tenta extrair a pagina atual.
# o comando or "" - Segurança extra, se a pagina for imahgem ou nao tiver texto extraivel, define a var text como um texto vazio para evitar cagadas(erros) no codigo
#text.strp() - remove espaços brancos inuteis e quebras de linha do inicio e fim do texto.
# if note text. continue - verifrica se está vazio, se estiver, o continue pula o resto do codigo e vai para a proxima pagina.
# #pages.append({...}) - caso a página tiver texto, ela é salva na lista pages como um dicionario(dict) contendo os parametros: documento(nome do arquivo),
# caminho(onde está salvo no computador), pagina(numero da pagina), texto(conteudo extraido da pagina.) 
def load_pdf(path: Path) -> list[dict]:
    reader = PdfReader (str(path))


    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        text = text.strip()

        if not text:
            continue

        pages.append(
            {
                "documento": path.name,
                "caminho": str(path),
                "pagina": page_number,
                "texto": text,
            }
        )

    return pages


#documents = [] - lista vazia
# for path in sorted... -
#DOCUMENTS_DIR.glob("*.pdf") - busca por todos os arquivos q terminam em .pdf dentro da pasta configurada.
# sorted(...) organiza os arquivos em ordem alfabetica para serem lidos na ordem correta.
#documents.extend(load_pdf(path)) - chama a função load_pdf para o pdf atual.
#.extend - pega a lista de páginas retornada e adiciona(ou funde) esses itens dentro da lista documents = []


def load_documents() -> list[dict]:
    documents= []

    for path in sorted(DOCUMENTS_DIR.glob("*.pdf")):
        documents.extend(load_pdf(path))

    return documents
