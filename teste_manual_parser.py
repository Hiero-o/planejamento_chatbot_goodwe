from services.rag.document_loader import load_documents
from services.rag.parsers.modbus_parser import parse_modbus_page
from services.rag.parsers.modbus_parser import detect_address
from services.rag.parsers.modbus_parser import SINGLE_ADDRESS_PATTERN
from services.rag.parsers.modbus_parser import parse_register_metadata
from services.rag.parsers.manual_parser import parse_manual_toc_page

documentos = load_documents()

modbus_pages = [
    documento
    for documento in documentos
    if documento["documento"] == "Mapa-MODBUS_HCA-G2.pdf"
]

enderecos_teste = {
    "10000",
    "10020",
    "10021",
    "10109 - 10112",
    "20000 - 20095",
    "20096",
    "20097",
    "30000",
    "300005",
}


total_registros = 0


#for page in modbus_pages:

    #resultado = parse_modbus_page(page)


   # registros = resultado["registros"]

  #  for registro in registros:

      #  if registro in registros:
        

manual_pages = [
    page
    for page in documentos
    if page["documento"] == "GW_HCA-G2_User-Manual-PT.pdf"
]

toc_page = next(
    page
    for page in manual_pages
    if page["pagina"] == 3
)

toc_entries = parse_manual_toc_page(toc_page)

print(f"Página {toc_page['pagina']}: {len(toc_entries)} entradas")

for item in toc_entries:
    print(item)

