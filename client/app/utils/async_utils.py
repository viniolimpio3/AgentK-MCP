"""
Utilitários para lidar com operações assíncronas no Streamlit.
"""

import asyncio
import nest_asyncio

def run_task(coroutine):
    """
    Executa uma corotina de forma segura no Streamlit, que não suporta
    execução assíncrona diretamente.
    
    Args:
        coroutine: A corotina a ser executada.
        
    Returns:
        O resultado da execução da corotina.
    """
    try:
        # Tenta aplicar o nest_asyncio se ainda não foi aplicado
        nest_asyncio.apply()
    except Exception:
        pass
    
    # Executa a corotina e retorna o resultado
    return asyncio.run(coroutine)
