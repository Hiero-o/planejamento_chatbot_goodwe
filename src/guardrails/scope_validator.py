import re
from unidecode import unidecode


TERMOS_FORA_DO_ESCOPO = [
    "politica",
    "eleicao",
    "futebol",
    "filme",
    "musica",
    "receita",
    "jogo",
    "programacao",
    "codigo",
    "clima",
    "previsao do tempo",
    "capital do brasil",
    "ronaldinho",
]

TERMOS_JURIDICOS = [
    "processo judicial",
    "processada",
    "processado",
    "advogado",
    "acao judicial",
    "lei",
    "contrato",
    "responsabilidade juridica",
    "responsabilidade legal",
]

TERMOS_FINANCEIROS = [
    "investimento",
    "investir",
    "bolsa de valores",
    "financiamento",
    "emprestimo",
    "imposto de renda",
    "imposto",
    "declaracao de renda",
]

TERMOS_SEGURANCA_ELETRICA = [
    "ligar fio",
    "ligacao eletrica",
    "instalacao eletrica",
    "instalar cabo",
    "mexer na fiação",
    "mexer na fiacao",
    "choque eletrico",
]


def normalizar(texto):
    texto = unidecode(texto.lower())
    texto = re.sub(r"[^\w\s]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def validar_escopo(question):
    texto = normalizar(question)

    for termo in TERMOS_JURIDICOS:
        if termo in texto:
            return {
                "permitido": False,
                "motivo": "juridico"
            }

    for termo in TERMOS_FINANCEIROS:
        if termo in texto:
            return {
                "permitido": False,
                "motivo": "financeiro"
            }

    for termo in TERMOS_SEGURANCA_ELETRICA:
        if termo in texto:
            return {
                "permitido": False,
                "motivo": "seguranca_eletrica"
            }

    for termo in TERMOS_FORA_DO_ESCOPO:
        if termo in texto:
            return {
                "permitido": False,
                "motivo": "fora_do_escopo"
            }

    return {
        "permitido": True,
        "motivo": None
    }