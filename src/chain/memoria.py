from langchain_core.chat_history import InMemoryChatMessageHistory


historicos: dict[str, InMemoryChatMessageHistory] = {}


def get_session_history(
    session_id: str,
) -> InMemoryChatMessageHistory:
    if session_id not in historicos:
        historicos[session_id] = InMemoryChatMessageHistory()

    return historicos[session_id]


def set_session_history(
    session_id: str,
    messages: list[dict[str, str]],
) -> None:
    """
    Sincroniza a memória da conversa com o histórico
    persistido pelo frontend no Firestore.
    """
    history = get_session_history(session_id)
    history.clear()

    # Mantém no máximo as últimas 20 mensagens.
    for message in messages[-20:]:
        role = message.get("role")
        content = message.get("content", "")

        if not isinstance(content, str) or not content.strip():
            continue

        if role == "user":
            history.add_user_message(content)
        elif role == "assistant":
            history.add_ai_message(content)