import logging
import os
import secrets
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal

from src.chain.memoria import set_session_history

from services.question_processor import process_question


load_dotenv()

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="GurAI API",
    description="API de comunicação com o core Python do GurAI",
    version="1.0.0",
)

class ChatHistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)

class UserChargingSession(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str

    charger_name: str = Field(
        default="",
        alias="chargerName",
    )
    vehicle_brand: str = Field(
        default="",
        alias="vehicleBrand",
    )
    vehicle_model: str = Field(
        default="",
        alias="vehicleModel",
    )

    establishment_name: str | None = Field(
        default=None,
        alias="establishmentName",
    )
    establishment_address: str | None = Field(
        default=None,
        alias="establishmentAddress",
    )

    started_at: str = Field(
        default="",
        alias="startedAt",
    )
    started_at_ms: int = Field(
        default=0,
        alias="startedAtMs",
    )

    duration_minutes: float = Field(
        default=0,
        alias="durationMinutes",
    )
    energy_kwh: float = Field(
        default=0,
        alias="energyKwh",
    )


class UserSessionSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total_sessions: int = Field(
        default=0,
        alias="totalSessions",
    )
    total_energy_kwh: float = Field(
        default=0,
        alias="totalEnergyKwh",
    )
    total_duration_minutes: float = Field(
        default=0,
        alias="totalDurationMinutes",
    )

    current_month_key: str = Field(
        default="",
        alias="currentMonthKey",
    )
    current_month_sessions: int = Field(
        default=0,
        alias="currentMonthSessions",
    )
    current_month_energy_kwh: float = Field(
        default=0,
        alias="currentMonthEnergyKwh",
    )
    current_month_duration_minutes: float = Field(
        default=0,
        alias="currentMonthDurationMinutes",
    )


class ChatRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    message: str = Field(
        min_length=1,
        max_length=4000,
    )
    session_id: str = Field(
        min_length=1,
        max_length=200,
        alias="sessionId",
    )
    history: list[ChatHistoryMessage] = Field(
        default_factory=list,
        max_length=20,
    )

    user_sessions: list[UserChargingSession] = Field(
        default_factory=list,
        max_length=20,
        alias="userSessions",
    )
    user_sessions_summary: UserSessionSummary | None = Field(
        default=None,
        alias="userSessionsSummary",
    )

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/chat")
def chat(
    payload: ChatRequest,
    x_gurai_api_key: Optional[str] = Header(default=None),
):
    # A chave é obrigatória para impedir chamadas não autorizadas.
    expected_key = os.getenv("GURAI_API_KEY")

    if not expected_key:
        raise HTTPException(
            status_code=503,
            detail="A chave de comunicação da API não foi configurada.",
        )

    if (
        not x_gurai_api_key
        or not secrets.compare_digest(x_gurai_api_key, expected_key)
    ):
        raise HTTPException(
            status_code=401,
            detail="Não autorizado.",
        )

    question = payload.message.strip()
    session_id = payload.session_id.strip()

    if not question or not session_id:
        raise HTTPException(
            status_code=422,
            detail="A mensagem e o identificador da conversa são obrigatórios.",
        )

    try:
        
        set_session_history(
            session_id,
            [message.model_dump() for message in payload.history],
        )
        
        # Reutiliza o processamento já implementado no GurAI.
        answer = process_question(
            question=question,
            session_id=session_id,
            user_sessions=[
                session.model_dump()
                for session in payload.user_sessions
            ],
            user_sessions_summary=(
                payload.user_sessions_summary.model_dump()
                if payload.user_sessions_summary is not None
                else None
            ),
        )

        return {"response": answer}

    except Exception:
        logging.exception("Erro ao processar pergunta do GurAI")

        raise HTTPException(
            status_code=500,
            detail="Não foi possível processar a mensagem.",
        )