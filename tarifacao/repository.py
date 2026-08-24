from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from .models import Charger, Establishment


class EstablishmentRepository:
    """Le estabelecimentos e regras de preco de um arquivo JSON."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else Path(__file__).with_name("estabelecimentos.json")
        self._data = self._load()

    def _load(self) -> dict[str, Any]:
        with self.path.open("r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def _charger(raw: dict[str, Any]) -> Charger:
        return Charger(
            charger_id=raw["charger_id"],
            status=raw["status"],
            potencia_kw=Decimal(str(raw["potencia_kw"])),
            corrente_a=Decimal(str(raw["corrente_a"])),
            tensao_v=Decimal(str(raw["tensao_v"])),
            estabelecimento_id=raw["estabelecimento_id"],
        )

    def list_establishments(self) -> list[Establishment]:
        return [
            Establishment(
                estabelecimento_id=raw["estabelecimento_id"],
                nome=raw["nome"],
                endereco=raw["endereco"],
                tarifa_kwh=Decimal(str(raw["tarifa_kwh"])),
                margem_percentual=Decimal(str(raw.get("margem_percentual", 10))),
                carregadores=tuple(self._charger(item) for item in raw.get("carregadores", [])),
            )
            for raw in self._data.get("estabelecimentos", [])
        ]

    def get_establishment(self, establishment_id: str) -> Establishment:
        for establishment in self.list_establishments():
            if establishment.estabelecimento_id == establishment_id:
                return establishment
        raise KeyError(f"Estabelecimento nao encontrado: {establishment_id}")

    def get_rules(self) -> dict[str, Any]:
        return self._data.get("configuracao", {})

    def add_establishment(self, establishment: Establishment) -> None:
        establishments = self._data.setdefault("estabelecimentos", [])
        if any(item["estabelecimento_id"] == establishment.estabelecimento_id for item in establishments):
            raise ValueError(f"ID ja cadastrado: {establishment.estabelecimento_id}")
        establishments.append({
            "estabelecimento_id": establishment.estabelecimento_id,
            "nome": establishment.nome,
            "endereco": establishment.endereco,
            "tarifa_kwh": float(establishment.tarifa_kwh),
            "margem_percentual": float(establishment.margem_percentual),
            "carregadores": [charger.__dict__ | {
                "potencia_kw": float(charger.potencia_kw),
                "corrente_a": float(charger.corrente_a),
                "tensao_v": float(charger.tensao_v),
            } for charger in establishment.carregadores],
        })
        self.path.write_text(json.dumps(self._data, indent=2, ensure_ascii=False), encoding="utf-8")
