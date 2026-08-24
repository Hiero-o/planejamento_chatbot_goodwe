from __future__ import annotations

import json
import random
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from .calculator import PricingCalculator
from .models import ChargingSession, PriceBreakdown


class SessionRepository:
    """Persiste sessoes agrupadas por estabelecimento, usuario e veiculo."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else Path(__file__).with_name("sessoes.json")
        self.data: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"estabelecimentos": {}}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self.data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    @staticmethod
    def _serialize(result: PriceBreakdown) -> dict[str, Any]:
        return {
            "session_id": result.session_id or str(uuid.uuid4()),
            "usuario_id": result.usuario_id,
            "veiculo_id": result.veiculo_id,
            "charger_id": result.charger_id,
            "inicio": result.horario_inicio,
            "duracao_minutos": result.duracao_minutos,
            "potencia_kw": float(result.potencia_kw),
            "energia_kwh": float(result.energia_kwh),
            "periodo": result.periodo,
            "bandeira": result.bandeira,
            "tarifa_base_kwh": float(result.tarifa_base_kwh),
            "adicional_horario_percentual": float(result.adicional_horario_percentual),
            "adicional_bandeira_kwh": float(result.adicional_bandeira_kwh),
            "subtotal_energia": float(result.subtotal_energia),
            "impostos": {name: float(value) for name, value in result.impostos.items()},
            "total_impostos": float(result.total_impostos),
            "margem_estabelecimento": float(result.margem_estabelecimento),
            "custo_total": float(result.custo_total),
        }

    def save(self, result: PriceBreakdown) -> dict[str, Any]:
        establishment = self.data.setdefault("estabelecimentos", {}).setdefault(
            result.estabelecimento_id,
            {"usuarios": {}},
        )
        user = establishment.setdefault("usuarios", {}).setdefault(
            result.usuario_id,
            {"veiculos": {}},
        )
        vehicle = user.setdefault("veiculos", {}).setdefault(
            result.veiculo_id,
            {"sessoes": []},
        )
        session = self._serialize(result)
        vehicle["sessoes"].append(session)
        self._save()
        return session

    def find(self, estabelecimento_id: str, usuario_id: str | None = None, veiculo_id: str | None = None) -> list[dict[str, Any]]:
        establishment = self.data.get("estabelecimentos", {}).get(estabelecimento_id, {})
        users = establishment.get("usuarios", {})
        if usuario_id is not None:
            users = {usuario_id: users.get(usuario_id, {})}

        sessions: list[dict[str, Any]] = []
        for user in users.values():
            vehicles = user.get("veiculos", {})
            if veiculo_id is not None:
                vehicles = {veiculo_id: vehicles.get(veiculo_id, {})}
            for vehicle in vehicles.values():
                sessions.extend(vehicle.get("sessoes", []))
        return sessions

    def reload(self) -> None:
        """Atualiza a memoria caso outro processo altere o JSON."""
        self.data = self._load()

    def summary_for_gurai(self, estabelecimento_id: str, usuario_id: str, veiculo_id: str | None = None) -> str:
        sessions = self.find(estabelecimento_id, usuario_id, veiculo_id)
        if not sessions:
            return "Nao encontrei sessoes registradas para os filtros informados."

        total_energy = sum(Decimal(str(item["energia_kwh"])) for item in sessions)
        total_cost = sum(Decimal(str(item["custo_total"])) for item in sessions)
        total_minutes = sum(item["duracao_minutos"] for item in sessions)
        last_session = max(sessions, key=lambda item: item["inicio"])
        vehicle_label = veiculo_id or "todos os veiculos"
        session_lines = "\n".join(
            f"- {item['session_id']}: {item['inicio']}, {item['duracao_minutos']} min, "
            f"{item['energia_kwh']} kWh, R$ {item['custo_total']}, "
            f"carregador {item['charger_id']}"
            for item in sorted(sessions, key=lambda item: item["inicio"], reverse=True)[:20]
        )
        return (
            "Contexto de sessoes de recarga (dados registrados):\n"
            f"- Estabelecimento: {estabelecimento_id}\n"
            f"- Usuario: {usuario_id}\n"
            f"- Veiculo: {vehicle_label}\n"
            f"- Sessoes encontradas: {len(sessions)}\n"
            f"- Energia total: {total_energy.quantize(Decimal('0.001'))} kWh\n"
            f"- Tempo total: {total_minutes} minutos\n"
            f"- Custo total registrado: R$ {total_cost.quantize(Decimal('0.01'))}\n"
            f"- Ultima sessao: {last_session['inicio']} no carregador {last_session['charger_id']}\n"
            "- Sessoes mais recentes:\n"
            f"{session_lines}\n"
            "Use somente esses dados para responder sobre o historico."
        )

    def generate_demo_sessions(self, calculator: PricingCalculator, establishment_id: str, users: list[tuple[str, str]], count: int = 10, seed: int | None = 42) -> list[dict[str, Any]]:
        """Gera dados ficticios; nunca deve ser usado como medicao real."""
        establishment = calculator.repository.get_establishment(establishment_id)
        if not establishment.carregadores:
            raise ValueError("O estabelecimento nao possui carregadores")
        if not users:
            raise ValueError("Informe pelo menos um usuario e veiculo")
        if count < 0:
            raise ValueError("count nao pode ser negativo")
        generator = random.Random(seed)
        base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        hours = (8, 10, 13, 17, 18, 19, 20, 21)
        durations = (30, 40, 45, 60, 75, 90)
        flags = ("verde", "verde", "amarela", "verde", "vermelha_1")
        generated = []
        for index in range(count):
            user_id, vehicle_id = generator.choice(users)
            charger = establishment.carregadores[index % len(establishment.carregadores)]
            start = base_date - timedelta(days=(index + 1) * 2)
            start = start.replace(hour=hours[index % len(hours)], minute=(index % 4) * 15)
            duration = durations[index % len(durations)]
            result = calculator.simulate(
                establishment_id,
                charger.charger_id,
                start,
                duration,
                charger.potencia_kw,
                flags[index % len(flags)],
                user_id,
                vehicle_id,
                f"demo-{index + 1:04d}",
            )
            generated.append(self.save(result))
        return generated
