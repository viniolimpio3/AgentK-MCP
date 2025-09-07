import streamlit as st
from typing import Optional

class Sidebar:
    """
    Componente da barra lateral.
    """
    
    def __init__(self, title: str, logo_path: Optional[str] = None):
        self.title = title
        self.logo_path = logo_path
    
    def render(self) -> None:
        """
        Renderiza a barra lateral.
        """
        with st.sidebar:
            # Container fixo para o logo
            st.markdown('<div class="sidebar-image-container">', unsafe_allow_html=True)
            if self.logo_path:
                st.image(self.logo_path, use_container_width=True)
            st.markdown(f"<h1 class='sidebar-title'>{self.title}</h1>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Perfil do agente
            st.markdown("#### Perfil do Agente")
            st.info("Especialista em Kubernetes, conectado ao MCP, pronto para analisar e manipular configurações do Kubernetes.")
            
            st.markdown("---")
            # Informações do modelo
            st.markdown("### Configurações")
            st.markdown(f"**Modelo:** o4-mini")
            st.markdown(f"**Versão:** latest")
            
            # Contador de mensagens
            message_count = st.session_state.get("message_count", 0)
            st.markdown(f"**Mensagens trocadas:** {message_count}")
            
            st.markdown("---")
            # Área de configurações extras
            with st.expander("ℹ️ Sobre"):
                st.markdown("""
                **Agent K** é um assistente inteligente que utiliza 
                o poder do GPT-4 combinado com ferramentas específicas 
                para ajudar em suas tarefas.
                """)
