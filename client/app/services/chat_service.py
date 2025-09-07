from typing import Optional, Dict, Any
from app.classes.llm_client import LLmClient
from app.classes.mcp_client import McpClient
from app.ui.components.chat_interface import ChatInterface
from app.core.async_utils import run_task
from app.config import settings
import streamlit as st
import json

class ChatService:
    """
    Service for managing chat interactions, with support for tool execution.
    """
    
    def __init__(self, llm_client: LLmClient):
        self.llm_client = llm_client
        self.chat_interface = ChatInterface()
    
    # def render_chat_history(self) -> None:
    #     """Render the complete chat history."""
    #     for message in self.llm_client.history:
    #         if message["role"] == "tool":
    #             self.chat_interface.render_tool_response(message["content"])
    #             continue
                
    #         self.chat_interface.render_message(message["role"], message["content"])
            
    #         if message.get("tool_calls"):
    #             for call in message["tool_calls"]:
    #                 self.chat_interface.render_tool_call(
    #                     call.function.name,
    #                     call.function.arguments
    #                 )

    def process_single_tool_call(self, call) -> None:
        try:
            async def do_call():
                client = McpClient()  
                await client.initialize_with_stdio("mcp", ["run", settings.TOOL_PATH])  

                tool_result = await client.call_tool(
                    call.function.name,
                    json.loads(call.function.arguments)
                )

                await client.cleanup()
                return tool_result

            call_result = run_task(do_call())

            return ''.join(item.text for item in call_result.content if item.type == 'text')
        except Exception as e:
            return f"Error calling tool: {str(e)}"  
    
    def resolve_chat(self, response):
        llm_client = st.session_state.llm_client
        tools = st.session_state.tools

        if response.choices[0].finish_reason == 'tool_calls':
            tool_reply = response.choices[0].message.content 

            if tool_reply is not None:
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
    def render_chat_history(self) -> None:
        """Render the complete chat history."""
        for message in st.session_state.llm_client.history:
            if message["role"] != "tool":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

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