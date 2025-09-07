"""
Configurações globais da aplicação.
"""
import os
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).parent.parent.parent.parent.resolve()
TOOL_PATH = str(ROOT_DIR / "server" / "app" / "main.py")

# Server path validation logging
print("\n=== MCP Server Configuration ===")
print(f"Root directory: {ROOT_DIR}")
print(f"Server path: {TOOL_PATH}")
print(f"Server file exists: {os.path.exists(TOOL_PATH)}")
print("==============================\n")

def load_css(css_file_name: str) -> str:
    """
    Carrega o conteúdo de um arquivo CSS da pasta styles.
    
    Args:
        css_file_name: Nome do arquivo CSS a ser carregado
        
    Returns:
        Conteúdo do arquivo CSS formatado como tag style
    """
    css_path = Path(__file__).parent.parent / "ui" / "styles" / css_file_name
    with open(css_path) as f:
        return f"<style>{f.read()}</style>"

# LLM Settings
DEFAULT_MODEL = "gpt-4"
SYSTEM_INSTRUCTIONS = (
    "Você é um agente especialista em Kubernetes. "
    "Seu papel é ajudar o usuário a entender, analisar e manipular configurações do Kubernetes. "
    "Você está conectado ao servidor MCP e pode obter arquivos de configuração do Kubernetes conforme solicitado. "
    "Utilize as ferramentas disponíveis para buscar, analisar e explicar recursos do Kubernetes."
)

# UI Settings
PAGE_TITLE = "Agent K"
PAGE_ICON = "🤖"
LOGO_PATH = "app/assets/AgentK-white.png"
PAGE_LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"

# CSS Style paths
CSS_FILES = {
    'main': 'main.css'
}

# Get the content of main CSS
MAIN_CSS = load_css(CSS_FILES['main'])
