import re

from unidecode import unidecode


TERMOS_FORA_DO_ESCOPO = [
    "politica",
    "eleicao",
    "futebol",
    "filme",
    "musica",
    "receita",
    "jogo",
    "programacao",
    "codigo",
    "clima",
    "previsao do tempo",
    "capital do brasil",
    "ronaldinho",
]

TERMOS_JURIDICOS = [
    "processo judicial",
    "processada",
    "processado",
    "advogado",
    "acao judicial",
    "lei",
    "contrato",
    "responsabilidade juridica",
    "responsabilidade legal",
]

TERMOS_FINANCEIROS = [
    "investimento",
    "investir",
    "bolsa de valores",
    "financiamento",
    "emprestimo",
    "imposto de renda",
    "imposto",
    "declaracao de renda",
]

TERMOS_SEGURANCA_ELETRICA = [
    "ligar fio",
    "ligacao eletrica",
    "instalacao eletrica",
    "instalar cabo",
    "mexer na fiação",
    "mexer na fiacao",
    "choque eletrico",
]


def normalizar(texto: str) -> str:
    """Normaliza acentos, caixa e pontuação."""
    texto = unidecode(texto.lower())
    texto = re.sub(r"[^\w\s]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def _contem_termo(texto: str, termo: str) -> bool:
    """
    Verifica a ocorrência de um termo ou expressão completa.

    Exemplo:
        'processado' não deve corresponder a 'processador'.
    """
    termo_normalizado = normalizar(termo)
    padrao = rf"\b{re.escape(termo_normalizado)}\b"

    return re.search(padrao, texto) is not None


def validar_escopo(question: str):
    texto = normalizar(question)

    # Perguntas sobre códigos de exceção MODBUS pertencem
    # ao domínio técnico do GurAI e devem poder chegar ao RAG.
    possui_codigo_modbus = (
        "modbus" in texto
        and re.search(r"\b0x[0-9a-f]{4}\b", texto) is not None
    )

    pergunta_tecnica_modbus = (
        possui_codigo_modbus
        and any(
            _contem_termo(texto, termo)
            for termo in [
                "codigo",
                "erro",
                "excecao",
                "exception",
                "nome",
                "name",
                "significa",
                "significado",
            ]
        )
    )

    if pergunta_tecnica_modbus:
        return {
            "permitido": True,
            "motivo": None,
        }

    # Preserva a exceção anterior para perguntas sobre códigos
    # de erro, inclusive quando não mencionam MODBUS explicitamente.
    pergunta_sobre_codigo_de_erro = re.search(
        r"\b(o que significa|qual o significado|"
        r"significado de|como interpretar|"
        r"explique|explica)\b.*\bcodigo de erro\b",
        texto,
    )

    if pergunta_sobre_codigo_de_erro:
        return {
            "permitido": True,
            "motivo": None,
        }

    grupos_de_termos = [
        (TERMOS_JURIDICOS, "juridico"),
        (TERMOS_FINANCEIROS, "financeiro"),
        (TERMOS_SEGURANCA_ELETRICA, "seguranca_eletrica"),
        (TERMOS_FORA_DO_ESCOPO, "fora_do_escopo"),
    ]

    for termos, motivo in grupos_de_termos:
        for termo in termos:
            if _contem_termo(texto, termo):
                return {
                    "permitido": False,
                    "motivo": motivo,
                }

    return {
        "permitido": True,
        "motivo": None,
    }