import logging
import sys
from mcp.server.fastmcp import FastMCP
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
    mcp = FastMCP("AgentK-Server", dependencies=["requests", "python-dotenv"])


    @mcp.tool()
    def list_k8s_resources(resources: list) -> dict:
        """
        Lista os recursos Kubernetes disponíveis no cluster.

        Args:
            resources (list): Array de tipos de recursos Kubernetes a serem listados. Valores aceitos: 'pods', 'services', 'deployments', 'configmaps', 'secrets',
            'ingresses', 'persistent_volume_claims', 'replicasets', 'statefulsets', 'nodes', 'persistent_volumes', 'namespaces'.
        Returns:
            dict: Dicionário contendo a lista de recursos ou uma mensagem de erro.
        """
        try:
            extractor = K8sExtractor(resources=resources)

            resources = extractor.list_resources_cluster(resources)
            if not resources:
                return {
                    "success": False,
                    "error": f"Nenhum recurso encontrado para os tipos especificados."
                }
            return {
                "success": True,
                "data": resources
            }
        except Exception as e:
            error_msg = f"Erro ao listar recursos: {str(e)}"
            return {
                "success": False,
                "error": error_msg
            }

    @mcp.tool()
    def get_yaml_cluster_resources(resources: list) -> dict:
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
        try:
            logger.info(f"Exporting resources: {', '.join(resources)}")  # ← Comentar
            extractor = K8sExtractor(resources=resources)
            
            cluster_resources = extractor.get_all_cluster_resources(resources)
            print(cluster_resources)  
            response = extractor.export_to_yaml(
                resources=cluster_resources
            )

            return {
                "success": True,
                "data": {
                    "resources": response,
                    "resource_count": len(resources),
                    "timestamp": datetime.now().isoformat()
                }
            }

        except Exception as e:
            error_msg = f"Failed to export resources: {str(e)}"
            logger.error(error_msg) 
            return {
                "success": False,
                "error": error_msg
            }

    @mcp.tool()
    def get_specific_object(resource_type: str, name: str, namespace: str = 'default') -> dict:
        """
        Obtém a configuração YAML de um recurso específico por tipo e nome.

        Args:
            resource_type (str): Tipo do recurso Kubernetes (Valores aceitos: 'pods', 'services', 'deployments', 'configmaps', 'secrets',
            'ingresses', 'persistent_volume_claims', 
            'replicasets', 'statefulsets', 'nodes', 'persistent_volumes',
            'namespaces').
            name (str): Nome do recurso.
            namespace (str, optional): Namespace do recurso. Padrão é 'default'.

        Returns:
            dict: Dicionário contendo a configuração YAML do recurso ou uma mensagem de erro.
        """
        try:
            extractor = K8sExtractor(resources=[resource_type])

            resource_yaml = extractor.get_resource_by_name(resource_type, name, namespace)
            if not resource_yaml:
                return {
                    "success": False,
                    "error": f"Recurso '{name}' do tipo '{resource_type}' não encontrado no namespace '{namespace}'."
                }
            return {
                "success": True,
                "data": resource_yaml
            }
        except Exception as e:
            error_msg = f"Erro ao obter recurso: {str(e)}"
            return {
                "success": False,
                "error": error_msg
            }

    if __name__ == "__main__":
        mcp.run()
except Exception as e:
    logger.error(f"Erro fatal no servidor: {str(e)}")
    raise
