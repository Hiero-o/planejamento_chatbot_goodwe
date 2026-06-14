from pypdf import PdfReader


def load_pdf(path):
    reader = PdfReader(path)
    texto = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            texto += page_text + "\n"
    return texto

def load_all_documents():

    documents = [
        "conhecimento/manuais/GW_HCA-G2_Datasheet-PT.pdf",
        "conhecimento/manuais/Mapa MODBUS_HCA G2.pdf",
        "conhecimento/manuais/GW_HCA-G2_User-Manual-PT.pdf"
    ]
    conhecimento = ""

    for doc in documents:
        conhecimento += load_pdf(doc)
        conhecimento += "\n\n"
    return conhecimento
