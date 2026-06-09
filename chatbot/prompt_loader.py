from pathlib import Path

def load_prompt():
    prompt_path = Path(
        "prompts/system_prompt.md"
    )
    
    return prompt_path.read_text(
        encoding="utf-8"
    )
    
