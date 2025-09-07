import logging
import sys
from mcp.server.fastmcp import FastMCP
from services.k8s.k8s import get_objects, get_object_definition
from typing import List, Any
from services.k8s.K8sExtractor import K8sExtractor
from datetime import datetime

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
    def get_cluster_resources_yaml(resources):
        """
            Extracts and exports Kubernetes resources from the current cluster as YAML.

            This MCP tool allows you to export multiple Kubernetes resources into a single YAML format.
            The output is cleaned and optimized for better readability and reusability.
            
            Args:
                resources (List[str]): Array of resource types to export
                                    Example: ['pods', 'deployments']
            
            Supported Resources:
                - pods              - services
                - deployments       - configmaps
                - secrets          - ingresses
                - persistent_volume_claims
                - replicasets      - statefulsets
                - nodes            - persistent_volumes
            
            Returns:
                dict: Response object containing:
                    - success (bool): Operation success status
                    - data (dict): Contains exported YAML content if successful
                    - error (str): Error message if operation failed
            
            Example:
                >>> get_cluster_resources_yaml(['pods', 'deployments'])
                {
                    'success': True,
                    'data': {
                        'yaml_content': '# Kubernetes Resources Export...',
                        'resource_count': 2
                    }
                }
        """

        logger.info(f"Resources requested for export: {resources}")  # ← Comentar temporariamente
        valid_resources = K8sExtractor.get_valid_resources()

        if not all(res in valid_resources for res in resources):
            invalid = [res for res in resources if res not in valid_resources]
            error_msg = f"Invalid resources: {', '.join(invalid)}. Valid values are: {', '.join(valid_resources)}"
            logger.error(error_msg)  # ← Comentar temporariamente
            return {
                "success": False,
                "error": error_msg
            }

        try:
            logger.info(f"Exporting resources: {', '.join(resources)}")  # ← Comentar
            extractor = K8sExtractor()
            
            cluster_resources = extractor.get_all_cluster_resources(resources)
            print(cluster_resources)  
            yaml_content = extractor.export_to_yaml(
                resources=cluster_resources,
                clean_export=True,
                minimal_export=True
            )

            return {
                "success": True,
                "data": {
                    "yaml_content": yaml_content,
                    "resource_count": len(resources),
                    "timestamp": datetime.now().isoformat()
                }
            }

        except Exception as e:
            error_msg = f"Failed to export resources: {str(e)}"
            logger.error(error_msg)  # ← Comentar
            return {
                "success": False,
                "error": error_msg
            }
    
    # @mcp.tool()
    # def list_object(object_type: str):
    #     """Lista um determinado objeto do cluster Kubernetes. 
    #         Valores aceitos: ['pods', 'nodes', 'services', 'deployments', 'replicasets', 'namespaces', 'cronjobs']
    #     """
    #     try:
    #         logger.info("Chamada para list_pods")
    #         return get_objects(object_type)
    #     except Exception as e:
    #         logger.error(f"Erro em list_pods: {str(e)}")
    #         return {"error": str(e)}
        
    # @mcp.tool()
    # def get_specific_object(namespace: str, object_type: str, object_name: str):
    #     """Obtém um objeto específico do cluster Kubernetes. 
    #         Valores de tipo aceito: ['pods', 'nodes', 'services', 'deployments', 'replicasets', 'namespaces', 'cronjobs']
    #     """
    #     try:
    #         logger.info(f"Chamada para get_object com tipo: {object_type}")
    #         return get_object_definition(namespace, object_type, object_name)
    #     except Exception as e:
    #         logger.error(f"Erro em get_object: {str(e)}")
    #         return {"error": str(e)}



    if __name__ == "__main__":
        mcp.run()
except Exception as e:
    logger.error(f"Erro fatal no servidor: {str(e)}")
    raise
