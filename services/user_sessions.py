
import re
from datetime import datetime, timedelta, timezone

from unidecode import unidecode


def is_personal_session_question(question: str) -> bool:
    """Identifica perguntas sobre as sessões do usuário."""

    texto = unidecode(question.lower())
    texto = re.sub(r"[^\w\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()

    palavras = set(texto.split())

    assuntos_sessoes = {
        "sessao",
        "sessoes",
        "recarga",
        "recargas",
        "carregamento",
        "carregamentos",
        "carreguei",
        "carregando",
    }

    assuntos_energia = {
        "energia",
        "consumo",
        "consumi",
    }

    marcadores_pessoais = {
        "meu",
        "minha",
        "meus",
        "minhas",
        "eu",
        "fiz",
        "realizei",
        "consumi",
        "ultimos",
        "ultimas",
        "historico",
        "quantas",
        "quantos",
        "quais",
        "liste",
        "listar",
    }

    tem_assunto = bool(
        palavras & (assuntos_sessoes | assuntos_energia)
    )

    tem_marcador_pessoal = bool(
        palavras & marcadores_pessoais
    )

    return tem_assunto and tem_marcador_pessoal


def _numero(valor, padrao=0.0) -> float:
    try:
        numero = float(valor)
        return numero if numero >= 0 else padrao
    except (TypeError, ValueError):
        return padrao


def _formatar_data(sessao: dict) -> str:
    timestamp = _numero(sessao.get("started_at_ms"))

    try:
        if timestamp > 0:
            data = datetime.fromtimestamp(
                timestamp / 1000,
                tz=timezone.utc,
            )
        else:
            valor = sessao.get("started_at", "")

            if not valor:
                return "Data não informada"

            data = datetime.fromisoformat(
                str(valor).replace("Z", "+00:00")
            )

            if data.tzinfo is None:
                data = data.replace(tzinfo=timezone.utc)

        fuso_sp = timezone(timedelta(hours=-3))

        return data.astimezone(fuso_sp).strftime(
            "%d/%m/%Y às %H:%M"
        )

    except (ValueError, TypeError, OSError, OverflowError):
        return "Data não informada"


def build_user_sessions_context(
    sessions: list[dict],
    summary: dict,
) -> str:
    """Prepara os dados de sessões para o contexto do GurAI."""

    total = int(_numero(summary.get("total_sessions")))
    energia = _numero(summary.get("total_energy_kwh"))
    duracao = int(
        _numero(summary.get("total_duration_minutes"))
    )

    mes_atual = summary.get("current_month_key", "")

    sessoes_mes = int(
        _numero(summary.get("current_month_sessions"))
    )
    

    energia_mes = _numero(
        summary.get("current_month_energy_kwh")
    )

    duracao_mes = int(
        _numero(summary.get("current_month_duration_minutes"))
    )

    linhas = [
        "DADOS DAS SESSÕES DO USUÁRIO AUTENTICADO",
        "",
        "Os dados abaixo foram consultados na plataforma.",
        "Não invente registros, datas ou valores.",
        "Use os totais fornecidos para perguntas agregadas.",
        "",
        f"Total de sessões registradas: {total}",
        f"Energia total registrada: {energia:.2f} kWh",
        f"Duração total registrada: {duracao} minutos",
        "",
        f"Mês atual: {mes_atual or 'não informado'}",
        f"Sessões no mês atual: {sessoes_mes}",
        f"Energia no mês atual: {energia_mes:.2f} kWh",
        f"Duração no mês atual: {duracao_mes} minutos",
        "",
        "SESSÕES MAIS RECENTES:",
    ]

    if not sessions:
        linhas.append(
        "Não há sessões detalhadas disponíveis para listar."
    )

    for indice, sessao in enumerate(sessions, start=1):
        veiculo = " ".join(
            str(valor)
            for valor in (
                sessao.get("vehicle_brand", ""),
                sessao.get("vehicle_model", ""),
            )
            if valor
        ).strip()

        estabelecimento = (
            sessao.get("establishment_name")
            or sessao.get("establishmentName")
        )

        endereco = (
            sessao.get("establishment_address")
            or sessao.get("establishmentAddress")
        )

        linhas.extend(
            [
                "",
                f"Sessão {indice}:",
                f"Identificador: {sessao.get('id', 'não informado')}",
                f"Data: {_formatar_data(sessao)}",
                (
                    "Carregador: "
                    f"{sessao.get('charger_name') or sessao.get('chargerName') or 'não informado'}"
                ),
                f"Veículo: {veiculo or 'não informado'}",
                f"Estabelecimento: {estabelecimento or 'não informado'}",
                f"Endereço: {endereco or 'não informado'}",
                (
                    "Energia: "
                    f"{_numero(sessao.get('energy_kwh')):.2f} kWh"
                ),
                (
                    "Duração: "
                    f"{int(_numero(sessao.get('duration_minutes')))} minutos"
                ),
            ]
        )
    linhas.extend(
        [
            "",
            "REGRAS DE RESPOSTA:",
            "- Responda em português.",
            "- Não confunda sessões pessoais com indicadores da planta.",
            "- Não invente sessões, datas, energia ou duração.",
            "- Para perguntas sobre recargas recentes, use os registros listados.",
            "- Se algum dado estiver ausente, informe a limitação.",
            "- Não calcule valores financeiros a partir apenas da energia.",
        ]
    )

    return "\n".join(linhas)
