import logging
import sys
import locale
from mcp.server.fastmcp import FastMCP
from services.k8s.k8s import get_objects, get_object_definition

# Forçar UTF-8 para entrada/saída
sys.stdout.reconfigure(encoding='utf-8')
sys.stdin.reconfigure(encoding='utf-8')

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ])

logger = logging.getLogger(__name__)

try:
    logger.info("Iniciando servidor MCP...")
    mcp = FastMCP("AgentK-Server", dependencies=["requests", "python-dotenv"])
    logger.info("Servidor MCP criado com sucesso")

    @mcp.tool()
    def list_object(object_type: str):
        """Lista um determinado objeto do cluster Kubernetes. 
            Valores aceitos: ['pods', 'nodes', 'services', 'deployments', 'replicasets', 'namespaces', 'cronjobs']
        """
        try:
            logger.info("Chamada para list_pods")
            return get_objects(object_type)
        except Exception as e:
            logger.error(f"Erro em list_pods: {str(e)}")
            return {"error": str(e)}
        
    @mcp.tool()
    def get_specific_object(namespace: str, object_type: str, object_name: str):
        """Obtém um objeto específico do cluster Kubernetes. 
            Valores de tipo aceito: ['pods', 'nodes', 'services', 'deployments', 'replicasets', 'namespaces', 'cronjobs']
        """
        try:
            logger.info(f"Chamada para get_object com tipo: {object_type}")
            return get_object_definition(namespace, object_type, object_name)
        except Exception as e:
            logger.error(f"Erro em get_object: {str(e)}")
            return {"error": str(e)}

    if __name__ == "__main__":
        mcp.run()
            
except Exception as e:
    logger.error(f"Erro fatal no servidor: {str(e)}")
    raise
