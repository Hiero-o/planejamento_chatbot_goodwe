INTENTS = {
    "TOTAL_POWER": [
        "potencia total",
        "consumo total",
        "potencia da planta"
    ],

    "AVAILABLE_CHARGERS": [
        "disponiveis",
        "livres",
        "desocupados"
    ],

    "ACTIVE_CHARGERS": [
        "em uso",
        "ativos",
        "carregando"
    ],

    "TOTAL_ENERGY": [
        "energia total utilizada",
        "energia total",
        "consumo de energia",
        "energia total da planta"
    ],

    "HELP": [
        "ajuda",
        "me ajuda",
        "help",
        "quais perguntas posso fazer",
        "o que voce faz",
        "o que voce pode fazer"
    ]
}


CAMPOS_OPERACIONAIS = [
    "potencia",
    "corrente",
    "tensao",
    "energia",
    "status",
    "tempo",
    "tarifa",
    "usuario",
    "horario"
]


EXPRESSOES_ESTADO = [
    "como esta",
    "funcionando",
    "situacao",
    "estado"
]


TERMOS_TECNICOS = [
    "nominal",
    "capacidade",
    "temperatura",
    "especificacao"
]


def detect_intent(texto):

    for intent, exemplos in INTENTS.items():
        for exemplo in exemplos:
            if exemplo in texto:
                return intent

    if "charger" in texto:

        if any(termo in texto for termo in TERMOS_TECNICOS):
            return None

        if any(campo in texto for campo in CAMPOS_OPERACIONAIS):
            return "CHARGER_INFO"

        if any(expressao in texto for expressao in EXPRESSOES_ESTADO):
            return "CHARGER_INFO"

    return None