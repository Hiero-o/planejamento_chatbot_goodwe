from services.conhecimento_loader import load_all_documents
from services.conhecimento_search import search_conhecimento

conhecimento = load_all_documents()


def search_conhecimento(question):
    return search_conhecimento(question, conhecimento)