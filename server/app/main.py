import logging
import sys
from mcp.server.fastmcp import FastMCP
from services.k8s.K8sExtractor import K8sExtractor
from services.k8s.K8sApplier import K8sApplier
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
    def listar_nomes_recursos_k8s(resources: list) -> dict:
        """
        Lista os nomes dos recursos Kubernetes disponíveis no cluster por tipo.

        Esta função retorna apenas os nomes dos recursos organizados por tipo.
        Por exemplo: {"pods": ["pod-1", "pod-2"], "services": ["service-1"]}

        Args:
            resources (list): Array de tipos de recursos Kubernetes a serem listados. 
                            Valores aceitos EXATAMENTE: ['pods', 'services', 'deployments', 'configmaps', 'secrets', 'ingresses', 'persistent_volume_claims', 'replicasets', 'statefulsets', 'nodes', 'persistent_volumes', 'namespaces', 'cronjobs', 'jobs']

        Returns:
            dict: Dicionário com estrutura:
                - success (bool): Status da operação
                - data (dict): Dicionário com tipos de recursos como chaves e arrays de nomes como valores
                - error (str): Mensagem de erro caso ocorra algum problema
        """
        try:
            extractor = K8sExtractor(resources=resources)

            resource_names = extractor.list_resources_cluster(resources)
            if not resource_names:
                return {
                    "success": False,
                    "error": f"Nenhum recurso encontrado para os tipos especificados."
                }
            return {
                "success": True,
                "data": resource_names
            }
        except Exception as e:
            error_msg = f"Erro ao listar recursos: {str(e)}"
            return {
                "success": False,
                "error": error_msg
            }

    @mcp.tool()
    def extrair_yamls_recursos_k8s(resources: list) -> dict:
        """
        Extrai e exporta recursos Kubernetes do cluster atual em formato YAML.

        Esta função permite exportar múltiplos recursos Kubernetes em formato YAML.
        A saída é limpa e otimizada para melhor legibilidade e reutilização.
        
        Args:
            resources (list): Array de tipos de recursos a serem exportados.
                            Valores aceitos EXATAMENTE: ['pods', 'services', 'deployments', 'configmaps', 'secrets', 'ingresses', 'persistent_volume_claims', 'replicasets', 'statefulsets', 'nodes', 'persistent_volumes', 'namespaces', 'cronjobs', 'jobs']
        
        Returns:
            dict: Objeto de resposta contendo:
                - success (bool): Status de sucesso da operação
                - data (dict): Contém o conteúdo YAML exportado se bem-sucedido
                    - resources (dict): Recursos organizados por tipo, cada um contendo array de objetos com 'name' e 'content' (YAML)
                    - resource_count (int): Número de tipos de recursos solicitados
                    - timestamp (str): Timestamp da operação
                - error (str): Mensagem de erro se a operação falhar
        
        Exemplo de retorno:
            {
                'success': True,
                'data': {
                    'resources': {
                        'pods': [
                            {'name': 'pod-1', 'content': 'apiVersion: v1\nkind: Pod...'},
                            {'name': 'pod-2', 'content': 'apiVersion: v1\nkind: Pod...'}
                        ]
                    },
                    'resource_count': 1,
                    'timestamp': '2025-09-08T10:30:00'
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
    def obter_yaml_objeto_especifico(resource_type: str, name: str, namespace: str = 'default') -> dict:
        """
        Obtém a configuração YAML de um recurso específico do Kubernetes por tipo e nome.

        Esta função permite extrair a definição completa em YAML de um recurso específico
        do cluster Kubernetes, útil para análise, backup ou replicação de configurações.

        Args:
            resource_type (str): Tipo do recurso Kubernetes. 
                               Valores aceitos EXATAMENTE: ['pods', 'services', 'deployments', 'configmaps', 'secrets', 'ingresses', 'persistent_volume_claims', 'replicasets', 'statefulsets', 'nodes', 'persistent_volumes', 'namespaces', 'cronjobs', 'jobs']
            name (str): Nome exato do recurso no cluster
            namespace (str, optional): Namespace do recurso. Padrão é 'default'. 
                                     Não aplicável para recursos cluster-wide como 'nodes', 'persistent_volumes' e 'namespaces'

        Returns:
            dict: Dicionário contendo:
                - success (bool): Status da operação
                - data (str): Configuração YAML do recurso se encontrado
                - error (str): Mensagem de erro caso o recurso não seja encontrado ou ocorra erro

        Exemplo de uso:
            - obter_yaml_objeto_especifico('pods', 'nginx-pod', 'production')
            - obter_yaml_objeto_especifico('nodes', 'worker-node-1')  # namespace não necessário
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

    @mcp.tool()
    def implementar_yaml_no_cluster(yaml_content: str, namespace: str = 'default', skip_dry_run: bool = False) -> dict:
        """
        Implementa um recurso Kubernetes no cluster a partir de um conteúdo YAML fornecido.

        Esta função permite criar ou atualizar recursos no cluster Kubernetes utilizando
        definições em formato YAML. Suporta múltiplos recursos separados por '---'.

        Args:
            yaml_content (str): Conteúdo YAML do recurso a ser implementado. Pode conter múltiplos recursos separados por '---'.
            namespace (str, optional): Namespace onde recursos namespacados serão criados. 
                Padrão é 'default'. Não aplicável para recursos cluster-wide como 'nodes', 'persistent_volumes' e 'namespaces'.
            skip_dry_run (bool, optional): Se True, pula a validação client dry-run prévia.
                Padrão é False.

        Returns:
            dict: Dicionário contendo:
                - success (bool): Status da operação (true se todos ou parcialmente aplicados)
                - message (str): Mensagem informativa sobre o resultado
                - applied_resources (list): Lista de recursos aplicados com sucesso
                - errors (list, opcional): Lista de erros se houver falhas parciais
                - error (str, opcional): Mensagem de erro se falha completa

        Exemplo de uso:
            - implementar_yaml_no_cluster(yaml_content, 'production')
            - implementar_yaml_no_cluster(multi_resource_yaml)  # Múltiplos recursos
        """
        try:
            applier = K8sApplier()
            
            result = applier.apply_yaml_content(yaml_content, namespace, skip_dry_run=skip_dry_run)
            
            # Padronizar formato de resposta
            response = {
                "success": result["success"],
                "message": result.get("message", "")
            }
            
            # Adicionar recursos aplicados se existirem
            if "applied_resources" in result:
                response["applied_resources"] = result["applied_resources"]
            
            # Adicionar erros se existirem
            if "errors" in result:
                response["errors"] = result["errors"]
            
            # Adicionar erro principal se falha completa
            if "error" in result:
                response["error"] = result["error"]
            
            return response
            
        except Exception as e:
            error_msg = f"Erro ao implementar recursos: {str(e)}"
            return {
                "success": False,
                "error": error_msg
            }

    @mcp.tool()
    def validar_yaml_k8s_dry_run(yaml_content: str, namespace: str = 'default') -> dict:
        """
        Validação básica do conteúdo YAML sem aplicá-lo ao cluster (client dry-run).

        Esta função permite validar a sintaxe e estrutura de recursos Kubernetes
        antes de aplicá-los efetivamente ao cluster.

        Args:
            yaml_content (str): Conteúdo YAML a ser validado
            namespace (str, optional): Namespace de contexto para validação. Padrão é 'default'

        Returns:
            dict: Dicionário contendo:
                - success (bool): Status da validação
                - message (str): Mensagem informativa
                - resources (list): Lista de recursos validados se sucesso
                - error (str): Mensagem de erro se falha na validação

        Exemplo de uso:
            - validar_yaml_k8s(yaml_content, 'production')
            - validar_yaml_k8s(yaml_content)
        """
        try:
            applier = K8sApplier()
            result = applier.dry_run_yaml(yaml_content, namespace)
            return result
            
        except Exception as e:
            error_msg = f"Erro na validação: {str(e)}"
            return {
                "success": False,
                "error": error_msg
            }

    @mcp.tool()
    def deletar_recurso_k8s(resource_type: str, name: str, namespace: str = 'default') -> dict:
        """
        Remove um recurso específico do cluster Kubernetes.

        Esta função permite deletar um recurso individual do cluster por tipo, nome e namespace.
        CUIDADO: Esta operação é irreversível.

        Args:
            resource_type (str): Tipo do recurso Kubernetes.
                Valores aceitos EXATAMENTE: ['pods', 'services', 'deployments', 'configmaps', 'secrets', 'ingresses', 'persistent_volume_claims', 'replicasets', 'statefulsets', 'nodes', 'persistent_volumes', 'namespaces', 'cronjobs', 'jobs']
            name (str): Nome exato do recurso no cluster
            namespace (str, optional): Namespace do recurso. Padrão é 'default'.
                Não aplicável para recursos cluster-wide como 'nodes', 'persistent_volumes' e 'namespaces'

        Returns:
            dict: Dicionário contendo:
                - success (bool): Status da operação
                - message (str): Mensagem informativa sobre o resultado
                - deleted_resource (dict): Informações do recurso deletado se sucesso
                - error (str): Mensagem de erro caso falhe
        """
        try:
            applier = K8sApplier()
            result = applier.delete_resource(resource_type, name, namespace)
            return result
            return result
            
        except Exception as e:
            error_msg = f"Erro ao deletar recurso: {str(e)}"
            return {
                "success": False,
                "error": error_msg
            }

    if __name__ == "__main__":
        mcp.run()
except Exception as e:
    logger.error(f"Erro fatal no servidor: {str(e)}")
    raise
