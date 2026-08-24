from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

CENT = Decimal("0.01")


def money(value: Decimal | int | float | str) -> Decimal:
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Charger:
    charger_id: str
    status: str
    potencia_kw: Decimal
    corrente_a: Decimal
    tensao_v: Decimal
    estabelecimento_id: str


@dataclass(frozen=True)
class Establishment:
    estabelecimento_id: str
    nome: str
    endereco: str
    tarifa_kwh: Decimal
    margem_percentual: Decimal = Decimal("10")
    carregadores: tuple[Charger, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ChargingSession:
    estabelecimento_id: str
    charger_id: str
    inicio: datetime
    duracao_minutos: int
    potencia_kw: Decimal
    energia_kwh: Decimal | None = None
    bandeira: str = "verde"
    usuario_id: str = "anonimo"
    veiculo_id: str = "nao informado"
    session_id: str | None = None

    def __post_init__(self) -> None:
        if self.duracao_minutos <= 0:
            raise ValueError("duracao_minutos deve ser maior que zero")
        if self.potencia_kw < 0:
            raise ValueError("potencia_kw nao pode ser negativa")
        if self.energia_kwh is not None and self.energia_kwh < 0:
            raise ValueError("energia_kwh nao pode ser negativa")


@dataclass(frozen=True)
class PriceBreakdown:
    estabelecimento_id: str
    charger_id: str
    horario_inicio: str
    energia_kwh: Decimal
    potencia_kw: Decimal
    duracao_minutos: int
    periodo: str
    bandeira: str
    tarifa_base_kwh: Decimal
    adicional_horario_percentual: Decimal
    adicional_bandeira_kwh: Decimal
    subtotal_energia: Decimal
    impostos: dict[str, Decimal]
    total_impostos: Decimal
    margem_estabelecimento: Decimal
    custo_total: Decimal
    usuario_id: str = "anonimo"
    veiculo_id: str = "nao informado"
    session_id: str | None = None

    def as_dict(self) -> dict[str, Any]:
        result = self.__dict__.copy()
        for key, value in list(result.items()):
            if isinstance(value, Decimal):
                result[key] = float(value)
            elif isinstance(value, dict):
                result[key] = {name: float(amount) for name, amount in value.items()}
        return result
