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

def ask_model(messages):

    response = client.chat(
        model="gpt-oss:120b",
        messages=messages,
        options={
            "temperature": 0.3,
            "num_predict": 1200
        }
    )

    return response["message"]["content"]