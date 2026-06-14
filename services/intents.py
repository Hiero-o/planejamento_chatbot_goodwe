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
        "carregando",
        "estão em uso"
        
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
        "quais perguntas posso fazer"
    ]
}

def detect_intent(texto):

    for intent, exemplos in INTENTS.items():

        for exemplo in exemplos:

            if exemplo in texto:

                return intent

    return None