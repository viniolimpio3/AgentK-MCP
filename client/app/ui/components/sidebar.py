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
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Perfil do agente
            st.markdown("#### Perfil do Agente")
            st.info("Especialista em Kubernetes, conectado ao MCP, pronto para analisar e manipular configurações do Kubernetes.")
            
            st.markdown("---")
            
            # Recursos Suportados
            st.markdown("### Recursos Suportados")
            
            with st.expander("Namespaced", expanded=False):
                st.markdown("""
                `pods`, `services`, `deployments`, `configmaps`, `secrets`, 
                `ingresses`, `persistent_volume_claims`, `replicasets`, 
                `statefulsets`, `cronjobs`, `jobs`, `horizontal_pod_autoscalers`, 
                `replication_controllers`, `daemon_sets`
                """)
            
            with st.expander("Cluster-wide", expanded=False):
                st.markdown("`nodes`, `persistent_volumes`, `namespaces`")
            
            st.markdown("---")
            # Informações do modelo
            st.markdown("### Configurações")
            st.markdown(f"**Modelo:** gpt-4.1")
            st.markdown(f"**Versão:** latest")
            
            # Contador de mensagens
            message_count = st.session_state.get("message_count", 0)
            st.markdown(f"**Mensagens trocadas:** {message_count}")
            
            st.markdown("---")
            
            # Seção de Exportação
            st.markdown("### 📄 Exportar Conversa")
            
            # Opções de exportação
            include_tools = st.checkbox("Incluir chamadas de ferramentas", value=True, 
                                      help="Incluir detalhes das chamadas MCP no relatório")
            
            # Verifica se há histórico para exportar
            has_history = (
                "llm_client" in st.session_state and 
                hasattr(st.session_state.llm_client, 'history') and
                len(st.session_state.llm_client.history) > 1
            )
            
            if st.button("📥 Exportar Histórico", 
                        disabled=not has_history,
                        help="Exporta o histórico da sessão atual em formato Markdown"):
                if has_history:
                    # Importa aqui para evitar dependência circular
                    from app.services.chat_service import ChatService
                    
                    # Cria uma instância temporária do chat service para exportação
                    temp_chat_service = ChatService(st.session_state.llm_client)
                    
                    try:
                        markdown_content, filename = temp_chat_service.export_conversation_history(include_tools)
                        
                        # Oferece o download do arquivo
                        st.download_button(
                            label="💾 Baixar Relatório",
                            data=markdown_content,
                            file_name=filename,
                            mime="text/markdown",
                            help="Clique para baixar o relatório da sessão"
                        )
                        
                        st.success("✅ Relatório gerado com sucesso!")
                        
                        # Mostra preview das estatísticas
                        stats = temp_chat_service.export_service.session_stats
                        st.markdown("**📊 Resumo da Sessão:**")
                        st.markdown(f"- Requisições: {stats['total_requests']}")
                        st.markdown(f"- Tokens: {stats['total_input_tokens'] + stats['total_output_tokens']}")
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar relatório: {str(e)}")
                else:
                    st.warning("⚠️ Nenhuma conversa para exportar")
            
            if not has_history:
                st.info("💡 Inicie uma conversa para habilitar a exportação")
            
            # Botão para limpar histórico
            if st.button("🗑️ Limpar Histórico", 
                        disabled=not has_history,
                        help="Remove todas as mensagens e reseta as estatísticas"):
                if has_history:
                    # Limpa o histórico mantendo apenas a mensagem do sistema
                    system_message = None
                    for msg in st.session_state.llm_client.history:
                        if isinstance(msg, dict) and msg.get("role") == "system":
                            system_message = msg
                            break
                    
                    st.session_state.llm_client.history.clear()
                    if system_message:
                        st.session_state.llm_client.history.append(system_message)
                    
                    # Reseta contadores e estatísticas
                    st.session_state.message_count = 0
                    if 'export_service' in st.session_state:
                        st.session_state.export_service.reset_session_stats()
                    
                    st.success("✅ Histórico limpo com sucesso!")
                    st.rerun()
            
            st.markdown("---")
            
            # Área de configurações extras
            with st.expander("ℹ️ Sobre"):
                st.markdown("""
                **Agent K** é um assistente inteligente baseado no modelo LLM gpt-4.1,
                que utiliza ferramentas específicas para ajudar em suas tarefas.
                """)
