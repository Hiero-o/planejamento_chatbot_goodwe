import json
from pathlib import Path

DATA_PATH = Path("data/simulacao-data.json")

def load_data():
    with open(DATA_PATH, 
              "r",
              encoding="utf-8",
              ) as file:
        return json.load(file)
    
    

def get_charger(charger_id):
    data = load_data()

    

    return data.get(charger_id)

def get_all_chargers():
    return load_data()


def get_status(charger_id):
    charger = get_charger(charger_id)

    if not charger:
        return None
    
    return charger["status"]

# Futuramente

def get_field(charger_id, field):
    charger = get_charger(charger_id)

    if not charger:
        return None
    return charger.get(field)

# --------------

def get_available_chargers():
    data = load_data()

    available = []
    for charger_id, charger in data.items():

        if charger["status"] == "Disponível":
            available.append(charger_id)

    return available


def get_active_chargers():
    data = load_data()

    active = []

    for charger_id, charger in data.items():

        if charger["status"] == "Carregando":
            active.append(charger_id)
    return active

def get_total_power():
    data = load_data()

    total = 0

    for charger in data.values():

        total += charger["potencia_kw"]
    return total


def total_energy():
    data = load_data()

    total = 0

    for charger in data.values():
        total += charger["energia_kwh"]
    return total