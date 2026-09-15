import tiktoken

def contar_tokens(texto):
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(texto))

def medir_prompt(caminho):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        texto = arquivo.read()

    return contar_tokens(texto)



if __name__ == "__main__":
    v1 = medir_prompt("prompts/system_prompt_v1.md")
    v2 = medir_prompt("prompts/system_prompt_v2.md")

    print(f"System Prompt v1: {v1} tokens")
    print(f"System Prompt v2: {v2} tokens")
    print(f"Diferença: {v2 - v1} tokens")