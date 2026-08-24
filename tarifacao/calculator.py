from __future__ import annotations

from datetime import datetime, time
from decimal import Decimal

from .models import ChargingSession, PriceBreakdown, money
from .repository import EstablishmentRepository


class PricingCalculator:
    def __init__(self, repository: EstablishmentRepository | None = None) -> None:
        self.repository = repository or EstablishmentRepository()
        self.rules = self.repository.get_rules()

    @staticmethod
    def _as_time(value: str) -> time:
        if value == "24:00":
            return time.max
        return datetime.strptime(value, "%H:%M").time()

    def _period(self, start: time) -> tuple[str, Decimal]:
        for period in self.rules.get("periodos", []):
            period_start = self._as_time(period["inicio"])
            period_end = self._as_time(period["fim"])
            matches = period_start <= start < period_end if period_start < period_end else start >= period_start or start < period_end
            if matches:
                return period["nome"], Decimal(str(period.get("adicional_percentual", 0)))
        return "fora_ponta", Decimal("0")

    def calculate(self, session: ChargingSession) -> PriceBreakdown:
        establishment = self.repository.get_establishment(session.estabelecimento_id)
        charger_ids = {charger.charger_id for charger in establishment.carregadores}
        if session.charger_id not in charger_ids:
            raise ValueError("O carregador nao pertence ao estabelecimento informado")

        energy = session.energia_kwh if session.energia_kwh is not None else (
            session.potencia_kw * Decimal(session.duracao_minutos) / Decimal(60)
        )
        energy = energy.quantize(Decimal("0.001"))
        period_name, time_addition = self._period(session.inicio.time())
        flags = self.rules.get("bandeiras", {})
        flag = session.bandeira.lower().replace(" ", "_").replace("-", "_")
        aliases = {"amarela": "amarela", "vermelha": "vermelha_1", "vermelha_1": "vermelha_1", "vermelha_2": "vermelha_2", "verde": "verde"}
        flag = aliases.get(flag, flag)
        if flag not in flags:
            raise ValueError(f"Bandeira invalida: {session.bandeira}")

        base_cost = energy * establishment.tarifa_kwh
        time_cost = base_cost * time_addition / Decimal(100)
        flag_cost = energy * Decimal(str(flags[flag]))
        subtotal = money(base_cost + time_cost + flag_cost)

        taxes: dict[str, Decimal] = {}
        tax_total = Decimal("0")
        for tax_name, rate in self.rules.get("impostos", {}).items():
            tax = money(subtotal * Decimal(str(rate)) / Decimal(100))
            taxes[tax_name] = tax
            tax_total += tax

        taxable_total = subtotal + tax_total
        margin = money(taxable_total * establishment.margem_percentual / Decimal(100))
        total = money(taxable_total + margin)
        return PriceBreakdown(
            estabelecimento_id=establishment.estabelecimento_id,
            charger_id=session.charger_id,
            horario_inicio=session.inicio.isoformat(),
            energia_kwh=energy,
            potencia_kw=session.potencia_kw,
            duracao_minutos=session.duracao_minutos,
            periodo=period_name,
            bandeira=flag,
            tarifa_base_kwh=establishment.tarifa_kwh,
            adicional_horario_percentual=time_addition,
            adicional_bandeira_kwh=Decimal(str(flags[flag])),
            subtotal_energia=subtotal,
            impostos=taxes,
            total_impostos=money(tax_total),
            margem_estabelecimento=margin,
            custo_total=total,
            usuario_id=session.usuario_id,
            veiculo_id=session.veiculo_id,
            session_id=session.session_id,
        )

    def simulate(self, establishment_id: str, charger_id: str, start: datetime, duration_minutes: int, power_kw: Decimal | float, bandeira: str = "verde", usuario_id: str = "anonimo", veiculo_id: str = "nao informado", session_id: str | None = None) -> PriceBreakdown:
        return self.calculate(ChargingSession(
            estabelecimento_id=establishment_id,
            charger_id=charger_id,
            inicio=start,
            duracao_minutos=duration_minutes,
            potencia_kw=Decimal(str(power_kw)),
            bandeira=bandeira,
            usuario_id=usuario_id,
            veiculo_id=veiculo_id,
            session_id=session_id,
        ))
