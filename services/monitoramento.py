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