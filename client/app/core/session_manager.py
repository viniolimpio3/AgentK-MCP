import streamlit as st
from typing import Any, Optional

class SessionManager:
    """
    Gerencia o estado da sessão do Streamlit e recursos associados.
    """
    
    @staticmethod
    def get_state(key: str, default: Any = None) -> Any:
        """
        Obtém um valor do estado da sessão.
        
        Args:
            key: Chave do estado
            default: Valor padrão se a chave não existir
        """
        return st.session_state.get(key, default)
    
    @staticmethod
    def set_state(key: str, value: Any) -> None:
        """
        Define um valor no estado da sessão.
        
        Args:
            key: Chave do estado
            value: Valor a ser armazenado
        """
        st.session_state[key] = value
    
    @staticmethod
    def increment_counter(key: str) -> int:
        """
        Incrementa um contador no estado da sessão.
        
        Args:
            key: Chave do contador
        
        Returns:
            Novo valor do contador
        """
        if key not in st.session_state:
            st.session_state[key] = 0
        st.session_state[key] += 1
        return st.session_state[key]
    
    @staticmethod
    def register_cleanup(cleanup_func: callable) -> None:
        """
        Registra uma função para ser chamada na limpeza da sessão.
        
        Args:
            cleanup_func: Função de limpeza a ser registrada
        """
        st.session_state["_cleanup_handler"] = cleanup_func
