import asyncio
import os
import streamlit as st
from dotenv import load_dotenv

from app.config import settings
from app.classes.mcp_handler import MCPHandler
from app.classes.llm_client import LLmClient
from app.utils.async_utils import run_task
from app.classes.mcp_client import McpClient
import traceback

def initialize_page():
    """
    Inicializa a configuração da página e estilos.
    """
    # Configuração da página
    st.set_page_config(
        page_title=settings.PAGE_TITLE,
        page_icon=settings.PAGE_ICON,
        layout=settings.PAGE_LAYOUT,
        initial_sidebar_state=settings.INITIAL_SIDEBAR_STATE
    )
    
    # Aplica os estilos CSS
    st.markdown(f"<style>{settings.MAIN_CSS}</style>", unsafe_allow_html=True)

def initialize_services():
    """
    Inicializa os serviços necessários para a aplicação.
    """
    try:
        # Configura evento loop do Windows
        if os.name == 'nt':  # Se estiver no Windows
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        initialize_page()
        load_dotenv()

        if "llm_client" not in st.session_state:
            st.session_state.llm_client = LLmClient(settings.DEFAULT_MODEL)
            st.session_state.llm_client.history.append({
                "role": "system",
                "content": settings.SYSTEM_INSTRUCTIONS
            })

        if "mcp_client" not in st.session_state:
            with st.spinner("Inicializando serviços..."): 
                async def init_mcp():
                    try:
                        st.write("1. Criando cliente MCP...")
                        st.session_state.mcp_client = McpClient()

                        st.write(f"2. Verificando caminho do servidor: {settings.TOOL_PATH}")
                        if not os.path.exists(settings.TOOL_PATH):
                            raise FileNotFoundError(f"Arquivo do servidor não encontrado: {settings.TOOL_PATH}")

                        st.write("3. Iniciando servidor MCP...")
                        await st.session_state.mcp_client.initialize_with_stdio("mcp", ["run", settings.TOOL_PATH])
                        st.write("4. Servidor MCP iniciado com sucesso")

                        st.write("5. Obtendo lista de ferramentas...")
                        tools_list = await st.session_state.mcp_client.get_tools()
                        st.write(f"6. Encontradas {len(tools_list)} ferramentas")

                        st.write("7. Formatando ferramentas...")
                        st.session_state.tools = st.session_state.mcp_client.format_tools_llm(tools_list)
                        st.write("8. Ferramentas formatadas com sucesso")

                        st.write("9. Limpando recursos...")
                        await st.session_state.mcp_client.cleanup()
                        st.write("10. Recursos limpos com sucesso")

                        st.success("Inicialização concluída com sucesso!")
                        
                    except Exception as e:
                        st.error(f"Erro durante a inicialização: {str(e)}")
                        st.error(f"Stack trace:\n{traceback.format_exc()}")
                        raise e

                # Cria um novo loop para a execução
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(init_mcp())
                finally:
                    loop.close()
                    asyncio.set_event_loop(None)

    except Exception as e:
        st.error(f"Error in initialize_services: {str(e)}")
        raise e