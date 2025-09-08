import streamlit as st
from typing import Optional

class ChatInterface:
    """
    Componente de interface do chat.
    """
    
    @staticmethod
    def render_message(role: str, content: str, avatar: Optional[str] = None) -> None:
        """
        Renderiza uma mensagem no chat.
        
        Args:
            role: Papel do remetente (user, assistant, tool)
            content: Conteúdo da mensagem
            avatar: Avatar opcional para a mensagem
        """
        with st.chat_message(role, avatar=avatar):
            st.markdown(content)
    
    @staticmethod
    def render_tool_call(name: str, arguments: str) -> None:
        """
        Renderiza uma chamada de ferramenta.
        
        Args:
            name: Nome da ferramenta
            arguments: Argumentos da chamada
        """
        with st.chat_message(name="tool", avatar=":material/build:"):
            st.markdown(f'LLM chamando tool {name}')
            with st.expander("Visualizar argumentos"):
                st.code(arguments)
    
    @staticmethod
    def render_tool_response(content: str) -> None:
        """
        Renderiza a resposta de uma ferramenta.
        
        Args:
            content: Conteúdo da resposta
        """
        with st.chat_message(name="tool", avatar=":material/data_object:"):
            with st.expander("Visualizar resposta"):
                st.code(content)
    
    @staticmethod
    def get_user_input(placeholder: str = "Digite sua pergunta...", disabled: bool = False) -> Optional[str]:
        """
        Obtém entrada do usuário.
        
        Args:
            placeholder: Texto placeholder para o input
            disabled: Se True, o input ficará desabilitado
            
        Returns:
            Texto digitado pelo usuário ou None
        """
        return st.chat_input(placeholder, disabled=disabled)
