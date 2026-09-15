from pathlib import Path

from pypdf import PdfReader

DOCUMENTS_DIR = Path("conhecimento/manuais")

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

def load_documents() -> list[dict]:
    documents= []

    for path in sorted(DOCUMENTS_DIR.glob("*.pdf")):
        documents.extend(load_pdf(path))

    return documents
