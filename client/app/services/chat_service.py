from typing import Optional, Dict, Any
import os
from app.classes.llm_client import LLmClient
from app.classes.mcp_client import McpClient
from app.ui.components.chat_interface import ChatInterface
from app.core.async_utils import run_task
from app.config import settings
from app.services.export_service import ExportService
import streamlit as st
import json
import datetime

class ChatService:
    """
    Service for managing chat interactions, with support for tool execution.
    """
    
    def __init__(self, llm_client: LLmClient):
        self.llm_client = llm_client
        self.chat_interface = ChatInterface()
        # Usa um serviço de exportação compartilhado na sessão
        if 'export_service' not in st.session_state:
            st.session_state.export_service = ExportService()
        self.export_service = st.session_state.export_service

    def process_single_tool_call(self, call) -> None:
        try:
            # Registra o início da chamada da ferramenta
            tool_start_time = self.export_service.record_request_start()
            
            async def do_call():
                client = McpClient()
                
                # Verificar se deve usar HTTP/SSE ou stdio
                mcp_server_url = os.getenv("MCP_SERVER_URL")
                
                if mcp_server_url:
                    # Modo container/HTTP - conectar via SSE
                    await client.initialize_with_http(mcp_server_url)
                else:
                    # Modo local/desenvolvimento - usar stdio
                    await client.initialize_with_stdio("mcp", ["run", settings.TOOL_PATH])

                tool_result = await client.call_tool(
                    call.function.name,
                    json.loads(call.function.arguments)
                )

                await client.cleanup()
                return tool_result

            call_result = run_task(do_call())
            
            # Registra o fim da chamada da ferramenta
            self.export_service.record_request_end(tool_start_time)

            return ''.join(item.text for item in call_result.content if item.type == 'text')
        except Exception as e:
            return f"Error calling tool: {str(e)}"  
    
    def resolve_chat(self, response):
        llm_client = st.session_state.llm_client
        tools = st.session_state.tools

        if response.choices[0].finish_reason == 'tool_calls':
            tool_reply = response.choices[0].message.content 

            # Só exibe a mensagem do assistente se houver conteúdo não-vazio
            if tool_reply is not None and tool_reply.strip():
                with st.chat_message("assistant"):
                    st.markdown(tool_reply)

            calls = response.choices[0].message.tool_calls  

            llm_client.add_assistant_message({
                "content": tool_reply,
                "tool_calls": calls,
                "role": "assistant"
            })

            for call in calls:
                with st.chat_message(name="tool", avatar=":material/build:"):
                    st.markdown(f'LLM chamando tool {call.function.name}')
                    with st.expander("Visualizar argumentos"):
                        st.code(call.function.arguments)

                with st.spinner(f"Processando chamada para {call.function.name}..."):
                    result = self.process_single_tool_call(call)

                with st.chat_message(name="tool", avatar=":material/data_object:"):
                    with st.expander("Visualizar resposta"):
                        st.code(result)

                llm_client.add_tool_message({
                    "tool_call_id": call.id,
                    "content": result,
                    "role": "tool"
                })

            with st.spinner("Gerando resposta final..."):
                next_response = llm_client.complete_chat(tools)

            self.resolve_chat(next_response)

        else:
            assistant_reply = response.choices[0].message.content

            with st.chat_message("assistant"):
                st.markdown(assistant_reply)

            llm_client.add_assistant_message({
                "content": assistant_reply,
                "role": "assistant"
            })
            
            # Incrementa contador de mensagens
            if 'message_count' not in st.session_state:
                st.session_state.message_count = 0
            st.session_state.message_count += 1
            
            # Registra timestamp da mensagem do assistente
            self.export_service.record_message_timestamp(st.session_state.message_count)
    def render_chat_history(self) -> None:
        """Render the complete chat history."""
        for message in st.session_state.llm_client.history:
            if message["role"] != "tool":
                # Só renderiza a mensagem se houver conteúdo válido
                content = message.get("content", "")
                if content and content.strip():
                    with st.chat_message(message["role"]):
                        st.markdown(content)

                if message["role"] == 'assistant' and "tool_calls" in message and message["tool_calls"]:
                    for call in message["tool_calls"]:
                        with st.chat_message(name="tool", avatar=":material/build:"):
                            st.markdown(f'LLM chamando tool {call.function.name}')
                            with st.expander("Visualizar resultado"):
                                st.code(call.function.arguments)
            else:
                with st.chat_message(name="tool", avatar=":material/data_object:"):
                    with st.expander("Visualizar resposta"):
                        st.code(message["content"])
    
    def process_llm_request(self, tools=[]):
        """
        Processa uma requisição para o LLM com rastreamento de tempo e tokens.
        
        Args:
            tools: Lista de ferramentas disponíveis para o LLM
            
        Returns:
            Resposta do LLM
        """
        request_start = self.export_service.record_request_start()
        response = self.llm_client.complete_chat(tools)
        self.export_service.record_request_end(request_start, response)
        return response
    
    def export_conversation_history(self, include_tools: bool = True) -> tuple[str, str]:
        """
        Exporta o histórico da conversa em formato Markdown.
        
        Args:
            include_tools: Se deve incluir as chamadas de ferramentas no export
            
        Returns:
            Tuple contendo (conteúdo_markdown, nome_do_arquivo)
        """
        markdown_content = self.export_service.generate_markdown_export(
            self.llm_client.history, 
            include_tools
        )
        filename = self.export_service.get_filename()
        return markdown_content, filename