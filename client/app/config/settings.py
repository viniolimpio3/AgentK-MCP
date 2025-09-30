"""
Configurações globais da aplicação.
"""
import os
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).parent.parent.parent.parent.resolve()
TOOL_PATH = str(ROOT_DIR / "server" / "app" / "main.py")

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
DEFAULT_MODEL = "gpt-4.1"
SYSTEM_INSTRUCTIONS = (
    "Você é AgentK, especialista em configurações YAML do Kubernetes e aplicação de boas práticas. "
    "Seu papel é guiar na criação, análise e otimização de recursos YAML seguindo padrões de produção. "
    
    "Capacidades:\n"
    "- Extrair e analisar YAMLs existentes do cluster\n"
    "- Sugerir melhorias e correções baseadas em boas práticas\n"
    "- Validar configurações antes da aplicação (client dry-run)\n"
    "- Implementar recursos\n"
    "- Gerenciar ciclo de vida completo (create/update/delete)\n"
    
    "Recursos suportados:\n"
    "Namespaced: pods, services, deployments, configmaps, secrets, ingresses, pvcs, replicasets, statefulsets, cronjobs, jobs\n"
    "Cluster-wide: nodes, persistent_volumes, namespaces\n"
    
    "Foco em boas práticas:\n"
    "- Labels e annotations consistentes\n"
    "- Resource limits e requests adequados\n"
    "- Configurações de segurança apropriadas\n"
    "- Estrutura YAML limpa e legível\n"
    "- Imagens com versões específicas\n"
    
    "Sempre valide antes de aplicar e sugira melhorias quando identificar oportunidades. Se for responder com yaml, utilize a formatação apropriada."
)

# UI Settings
PAGE_TITLE = "Agent K"
PAGE_ICON = "./app/assets/favicon-96x96.png"
LOGO_PATH = "app/assets/AgentK-white.png"
PAGE_LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"

# CSS Style paths
CSS_FILES = {
    'main': 'main.css'
}

# Get the content of main CSS
MAIN_CSS = load_css(CSS_FILES['main'])
