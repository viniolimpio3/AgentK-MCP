import asyncio
import os
from typing import Coroutine, Any, TypeVar

T = TypeVar('T')

def run_task(coro: Coroutine[Any, Any, T]) -> T:
    """
    Executa uma corotina de forma segura em um novo loop de eventos.
    
    Args:
        coro: A corotina a ser executada
        
    Returns:
        O resultado da execução da corotina
        
    Raises:
        Exception: Qualquer exceção que ocorra durante a execução
    """
    try:
        # Configura a política de eventos do Windows se necessário
        if os.name == 'nt':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        # Cria um novo loop para evitar conflitos
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
            # Limpa o loop atual para evitar conflitos
            asyncio.set_event_loop(None)
    except Exception as e:
        # Re-raise a exceção para ser tratada pelo chamador
        raise e