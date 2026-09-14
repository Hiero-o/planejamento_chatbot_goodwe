from ollama import Client
from dotenv import load_dotenv
import os



load_dotenv()



client = Client(
    host="https://ollama.com",
    headers={
        "Authorization": f"Bearer {os.getenv('OLLAMA_API_KEY')}"
    }
)

def ask_model(messages, retornar_metricas=False):

    response = client.chat(
        model="gemma4:31b-cloud",
        messages=messages,
        options={
            "temperature": 0.3,
            "num_predict": 1200
        }
    )

    resposta = response["message"]["content"]

    if not retornar_metricas:
        return resposta
    return {
        "resposta": resposta,
        "input_tokens": response.get("prompt_eval_count", 0),
        "output_tokens": response.get("eval_count", 0)
    }

