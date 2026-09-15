import re

def extract_charger_id(question):
    match = re.search(r"\bchargers*[_-]?\s*(\d+)", question.lower())

    if not match:
        return None
    numero = match.group(1)

    return f"charger_{numero.zfill(2)}"