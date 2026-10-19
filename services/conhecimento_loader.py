from pathlib import Path

import pymupdf


# Raiz do projeto

PROJECT_ROOT = Path(__file__).resolve().parents[1]


# Caminhos relativos dos documentos da base atual.
DOCUMENTS = (
    "conhecimento/manuais/GW_HCA-G2_Datasheet-PT.pdf",
    "conhecimento/manuais/Mapa-MODBUS_HCA-G2.pdf",
    "conhecimento/manuais/GW_HCA-G2_User-Manual-PT.pdf",
)


def load_pdf(path: str | Path) -> str:
    pdf_path = Path(path).expanduser()

    # Resolve caminhos relativos a partir da raiz do projeto.
    if not pdf_path.is_absolute():
        pdf_path = PROJECT_ROOT / pdf_path

    pdf_path = pdf_path.resolve()

    if not pdf_path.is_file():
        raise FileNotFoundError(
            f"PDF não encontrado: {pdf_path}"
        )

    texto = ""

    with pymupdf.open(str(pdf_path)) as pdf:
        for page in pdf:
            page_text = page.get_text("text")

            if page_text:
                texto += page_text + "\n"

    return texto


def load_all_documents() -> str:
    
    conhecimento = ""

    for doc in DOCUMENTS:
        conhecimento += load_pdf(doc)
        conhecimento += "\n\n"

    return conhecimento