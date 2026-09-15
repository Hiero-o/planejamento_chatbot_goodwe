from pydantic import BaseModel, Field, field_validator, ConfigDict


class ConsultaRecarga(BaseModel):
    carregador: str
    usuario: str | None = None
    status: str | None = None
    potencia_kw: float | None = None
    corrente_a: float | None = None
    tensao_v: float | None = None
    energia_kwh: float | None = None
    tempo_restante_min: int | None = None
    horario: str | None = None
    tarifa_kwh: float | None = None

    @field_validator("carregador")
    @classmethod
    def validar_carregador(cls, valor):
        if valor.isdigit():
            valor = f"charger_{valor.zfill(2)}"

        if not valor.startswith("charger_"):
            raise ValueError(
                "O carregador deve seguir o formato charger_XX"
            )

        return valor

    @field_validator(
        "potencia_kw",
        "corrente_a",
        "tensao_v",
        "energia_kwh",
        "tarifa_kwh"
    )
    @classmethod
    def validar_valores(cls, valor):
        if valor is not None and valor < 0:
            raise ValueError("O valor não pode ser negativo")
        return valor

    @field_validator("tempo_restante_min")
    @classmethod
    def validar_tempo(cls, valor):
        if valor is not None and valor < 0:
            raise ValueError(
                "O tempo restante não pode ser negativo"
            )
        return valor


class ConsultaPotenciaTotal(BaseModel):
    potencia_total_kw: float = Field(
        description="Potência total atual da planta em quilowatts (kW)."
    )

    @field_validator("potencia_total_kw")
    @classmethod
    def validar_potencia(cls, valor):
        if valor < 0:
            raise ValueError(
                "A potência total não pode ser negativa"
            )
        return valor


class ConsultaCarregadoresDisponiveis(BaseModel):
    carregadores_disponiveis: list[str] = Field(
        description="Lista dos carregadores atualmente disponíveis."
    )

    @field_validator("carregadores_disponiveis")
    @classmethod
    def validar_carregadores(cls, valor):
        for carregador in valor:
            if not carregador.startswith("charger_"):
                raise ValueError(
                    "Todos os carregadores devem seguir o formato charger_XX"
                )

        return valor


class ConsultaCarregadoresAtivos(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    carregadores_ativos: list[str] = Field(
        alias="chargers_in_use",
        description="Lista dos identificadores dos carregadores atualmente em uso."
    )

    @field_validator("carregadores_ativos")
    @classmethod
    def validar_carregadores(cls, valor):
        for carregador in valor:
            if not carregador.startswith("charger_"):
                raise ValueError(
                    "Todos os carregadores devem seguir o formato charger_XX"
                )

        return valor


class ConsultaEnergiaTotal(BaseModel):
    energia_total_kwh: float = Field(
        description="Energia total utilizada pela planta em quilowatt-hora (kWh)."
    )

    @field_validator("energia_total_kwh")
    @classmethod
    def validar_energia(cls, valor):
        if valor < 0:
            raise ValueError(
                "A energia total não pode ser negativa"
            )

        return valor