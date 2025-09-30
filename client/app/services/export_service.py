import json
import datetime
from typing import Dict, Any, List
import streamlit as st
import pytz

class ExportService:
    """
    Serviço responsável por exportar o histórico de conversas em formato Markdown.
    """
    
    def __init__(self):
        # Define o timezone GMT-3 (horário de Brasília)
        self.timezone = pytz.timezone('America/Sao_Paulo')
        self.session_stats = {
            'start_time': datetime.datetime.now(self.timezone),
            'total_requests': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'request_times': [],
            'message_timestamps': {}
        }
    
    def record_request_start(self) -> datetime.datetime:
        """Registra o início de uma requisição e retorna o timestamp."""
        start_time = datetime.datetime.now(self.timezone)
        self.session_stats['total_requests'] += 1
        return start_time
    
    def record_message_timestamp(self, message_index: int):
        """Registra o timestamp de uma mensagem específica."""
        self.session_stats['message_timestamps'][message_index] = datetime.datetime.now(self.timezone)
    
    def record_request_end(self, start_time: datetime.datetime, response_data: Any = None):
        """Registra o fim de uma requisição e calcula o tempo decorrido."""
        end_time = datetime.datetime.now(self.timezone)
        execution_time = (end_time - start_time).total_seconds()
        self.session_stats['request_times'].append({
            'start': start_time,
            'end': end_time,
            'duration': execution_time
        })
        
        # Registra tokens se disponíveis na resposta
        if response_data and hasattr(response_data, 'usage'):
            usage = response_data.usage
            if hasattr(usage, 'prompt_tokens'):
                self.session_stats['total_input_tokens'] += usage.prompt_tokens
            if hasattr(usage, 'completion_tokens'):
                self.session_stats['total_output_tokens'] += usage.completion_tokens
    
    def generate_markdown_export(self, chat_history: List[Dict], include_tools: bool = True) -> str:
        """
        Gera o histórico de conversa em formato Markdown.
        
        Args:
            chat_history: Lista com o histórico de mensagens
            include_tools: Se deve incluir as chamadas de ferramentas
            
        Returns:
            String contendo o markdown formatado
        """
        md_content = []
        
        # Cabeçalho do relatório
        md_content.append("# Relatório de Sessão - Agent K")
        md_content.append("")
        export_time = datetime.datetime.now(self.timezone)
        md_content.append(f"**Data de Exportação:** {export_time.strftime('%d/%m/%Y %H:%M:%S')} (GMT-3)")
        md_content.append(f"**Início da Sessão:** {self.session_stats['start_time'].strftime('%d/%m/%Y %H:%M:%S')} (GMT-3)")
        md_content.append("")
        
        # Estatísticas da sessão
        md_content.append("## 📊 Estatísticas da Sessão")
        md_content.append("")
        md_content.append(f"- **Total de Requisições:** {self.session_stats['total_requests']}")
        md_content.append(f"- **Tokens de Entrada:** {self.session_stats['total_input_tokens']}")
        md_content.append(f"- **Tokens de Saída:** {self.session_stats['total_output_tokens']}")
        md_content.append(f"- **Total de Tokens:** {self.session_stats['total_input_tokens'] + self.session_stats['total_output_tokens']}")
        
        if self.session_stats['request_times']:
            total_time = sum(req['duration'] for req in self.session_stats['request_times'])
            avg_time = total_time / len(self.session_stats['request_times'])
            md_content.append(f"- **Tempo Total de Processamento:** {total_time:.2f}s")
            md_content.append(f"- **Tempo Médio por Requisição:** {avg_time:.2f}s")
        
        md_content.append("")
        
        # Detalhes de timing por requisição
        if self.session_stats['request_times']:
            md_content.append("### ⏱️ Tempo de Execução por Requisição")
            md_content.append("")
            for i, req_time in enumerate(self.session_stats['request_times'], 1):
                start_str = req_time['start'].strftime('%H:%M:%S')
                end_str = req_time['end'].strftime('%H:%M:%S')
                md_content.append(f"**Requisição {i}:** {start_str} - {end_str} ({req_time['duration']:.2f}s)\n")
            md_content.append("")
        
        # Histórico da conversa
        md_content.append("## 💬 Histórico da Conversa")
        md_content.append("")
        
        message_counter = 1
        tool_call_counter = 1
        
        for message in chat_history:
            role = message.get("role", "unknown")
            content = message.get("content", "")
            
            if role == "system":
                continue  # Pula mensagens do sistema
            
            elif role == "user":
                # Usa timestamp real se disponível, senão usa timestamp atual
                msg_timestamp = self.session_stats['message_timestamps'].get(
                    message_counter, datetime.datetime.now(self.timezone)
                )
                timestamp = msg_timestamp.strftime('%H:%M:%S')
                md_content.append(f"### 👤 Usuário - #{message_counter} ({timestamp})")
                md_content.append("")
                md_content.append(content)
                md_content.append("")
                message_counter += 1
                
            elif role == "assistant":
                # Usa timestamp real se disponível, senão usa timestamp atual  
                msg_timestamp = self.session_stats['message_timestamps'].get(
                    message_counter, datetime.datetime.now(self.timezone)
                )
                timestamp = msg_timestamp.strftime('%H:%M:%S')
                md_content.append(f"### 🤖 Assistente - #{message_counter} ({timestamp})")
                md_content.append("")
                if content:
                    md_content.append(content)
                md_content.append("")
                
                # Verifica se há chamadas de ferramentas
                if include_tools and "tool_calls" in message and message["tool_calls"]:
                    md_content.append("#### 🔧 Chamadas de Ferramentas:")
                    md_content.append("")
                    for tool_call in message["tool_calls"]:
                        function_name = tool_call.function.name
                        arguments = tool_call.function.arguments
                        
                        md_content.append(f"**Ferramenta #{tool_call_counter}: {function_name}**")
                        md_content.append("")
                        md_content.append("```json")
                        md_content.append(arguments)
                        md_content.append("```")
                        md_content.append("")
                        tool_call_counter += 1
                
                message_counter += 1
                
            elif role == "tool" and include_tools:
                tool_call_id = message.get("tool_call_id", "unknown")
                md_content.append(f"#### 📋 Resposta da Ferramenta ({tool_call_id}):")
                md_content.append("")
                md_content.append("```")
                md_content.append(content)
                md_content.append("```")
                md_content.append("")
        
        # Rodapé
        md_content.append("---")
        md_content.append("")
        md_content.append("*Relatório gerado automaticamente pelo Agent K*")
        
        return "\n".join(md_content)
    
    def get_filename(self) -> str:
        """Gera um nome de arquivo baseado na data e hora atual."""
        timestamp = datetime.datetime.now(self.timezone).strftime("%Y%m%d_%H%M%S")
        return f"agent_k_session_{timestamp}.md"
    
    def reset_session_stats(self):
        """Reseta as estatísticas da sessão."""
        self.session_stats = {
            'start_time': datetime.datetime.now(self.timezone),
            'total_requests': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'request_times': [],
            'message_timestamps': {}
        }