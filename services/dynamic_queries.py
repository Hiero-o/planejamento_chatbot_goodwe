from services.monitoramento import get_charger, get_total_power, get_available_chargers, get_active_chargers, get_total_energy

def get_charger_context(charger_id):
    charger = get_charger(charger_id)

    if not charger:
        return None


    return f"""
    Dados atuais do carregador:
    Usuário: {charger["usuario"]}
    Status: {charger["status"]}
    Potência: {charger["potencia_kw"]} KW
    Corrente: {charger["corrente_a"]} A
    Tensão: {charger["tensao_v"]} V
    Energia: {charger["energia_kwh"]} KWH
    Tempo Restante: {charger["tempo_restante_min"]} Min
    Horário: {charger["horario"]}
    Tarifa: {charger["tarifa_kwh"]} KWH
    """

def get_total_power_context():
    total = get_total_power()

    print("TOTAL POWER: ", total)

    return f"""
    Potência total da planta: {total} KW
    """

def get_available_charger_context():
    diponiveis = get_available_chargers()
    return f"""
    Carregadores diponíveis: {diponiveis}"""

def get_active_charger_context():
    ativos = get_active_chargers()

    return f"""
    Carregadores em uso: {ativos}"""

def get_total_energy_context():
    energia = get_total_energy()

    return f"""
    Energia total utilizada {energia}"""