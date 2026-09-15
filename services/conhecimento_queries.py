from services.conhecimento_loader import load_all_documents
from services.conhecimento_search import search_conhecimento as search_conhecimento_original

conhecimento = load_all_documents()


def search_conhecimento_context(question):
    return search_conhecimento_original(question, conhecimento)