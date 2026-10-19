from pathlib import Path

import pymupdf

DOCUMENTS_DIR = Path("conhecimento/manuais")

def load_pdf(path: Path) -> list[dict]:
    
    pages = []

    with pymupdf.open(str(path)) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text") or ""
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
