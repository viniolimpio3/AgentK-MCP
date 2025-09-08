from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.utils import create_from_yaml
import yaml
import tempfile
import os
from typing import Dict, List, Any
from io import StringIO


class K8sApplier:
    def __init__(self, config_file: str = None):
        """Inicializa o cliente Kubernetes para aplicação de recursos"""
        self._setup_k8s_client(config_file)

    def _setup_k8s_client(self, config_file: str = None):
        """Configura cliente Kubernetes"""
        if config_file:
            config.load_kube_config(config_file=config_file)
        else:
            try:
                config.load_incluster_config()
            except:
                config.load_kube_config()
        
        self.api_client = client.ApiClient()
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.networking_v1 = client.NetworkingV1Api()
        self.batch_v1 = client.BatchV1Api()

    def apply_yaml_content(self, yaml_content: str, namespace: str = 'default') -> Dict[str, Any]:
        """
        Aplica conteúdo YAML ao cluster Kubernetes
        
        Args:
            yaml_content (str): Conteúdo YAML do recurso
            namespace (str): Namespace de destino (usado apenas se não especificado no YAML)
            
        Returns:
            dict: Resultado da operação
        """
        try:
            # Validar YAML
            resources = self._parse_yaml(yaml_content)
            if not resources:
                return {
                    "success": False,
                    "error": "YAML inválido ou vazio"
                }

            applied_resources = []
            errors = []

            for resource in resources:
                try:
                    result = self._apply_single_resource(resource, namespace)
                    if result["success"]:
                        applied_resources.append(result["resource_info"])
                    else:
                        errors.append(result["error"])
                except Exception as e:
                    errors.append(f"Erro ao aplicar recurso: {str(e)}")

            if errors:
                return {
                    "success": False if not applied_resources else True,  # Sucesso parcial se alguns recursos foram aplicados
                    "applied_resources": applied_resources,
                    "errors": errors,
                    "message": f"Aplicados {len(applied_resources)} recursos com {len(errors)} erros"
                }
            else:
                return {
                    "success": True,
                    "applied_resources": applied_resources,
                    "message": f"Todos os {len(applied_resources)} recursos aplicados com sucesso"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Erro geral na aplicação: {str(e)}"
            }

    def _parse_yaml(self, yaml_content: str) -> List[Dict[str, Any]]:
        """Parse do conteúdo YAML em recursos individuais"""
        try:
            # Suporte para múltiplos documentos YAML (separados por ---)
            documents = yaml.safe_load_all(yaml_content)
            resources = []
            
            for doc in documents:
                if doc and isinstance(doc, dict):
                    resources.append(doc)
            
            return resources
        except yaml.YAMLError as e:
            raise ValueError(f"YAML inválido: {str(e)}")

    def _apply_single_resource(self, resource: Dict[str, Any], default_namespace: str) -> Dict[str, Any]:
        """Aplica um único recurso ao cluster"""
        try:
            # Extrair informações do recurso
            kind = resource.get('kind', '')
            api_version = resource.get('apiVersion', '')
            metadata = resource.get('metadata', {})
            name = metadata.get('name', 'unnamed')
            namespace = metadata.get('namespace', default_namespace)

            # Determinar se é recurso cluster-wide
            cluster_wide_resources = ['Node', 'PersistentVolume', 'Namespace', 'ClusterRole', 'ClusterRoleBinding']
            is_cluster_wide = kind in cluster_wide_resources

            # Usar kubernetes.utils.create_from_yaml para aplicar o recurso
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as temp_file:
                yaml.dump(resource, temp_file, default_flow_style=False)
                temp_file_path = temp_file.name

            try:
                # Aplicar o recurso usando create_from_yaml
                created_resources = create_from_yaml(
                    self.api_client,
                    temp_file_path,
                    namespace=namespace if not is_cluster_wide else None
                )

                resource_info = {
                    "kind": kind,
                    "name": name,
                    "namespace": namespace if not is_cluster_wide else "cluster-wide",
                    "api_version": api_version,
                    "action": "applied"
                }

                return {
                    "success": True,
                    "resource_info": resource_info
                }

            finally:
                # Limpar arquivo temporário
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except ApiException as e:
            error_msg = f"API Error para {kind}/{name}: {e.reason}"
            if e.status == 409:  # Conflict - recurso já existe
                error_msg += " (recurso já existe - considere usar 'kubectl apply' para atualizar)"
            return {
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao aplicar {kind}/{name}: {str(e)}"
            }

    def apply_yaml_file(self, file_path: str, namespace: str = 'default') -> Dict[str, Any]:
        """
        Aplica um arquivo YAML ao cluster
        
        Args:
            file_path (str): Caminho para o arquivo YAML
            namespace (str): Namespace de destino
            
        Returns:
            dict: Resultado da operação
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                yaml_content = file.read()
            return self.apply_yaml_content(yaml_content, namespace)
        except FileNotFoundError:
            return {
                "success": False,
                "error": f"Arquivo não encontrado: {file_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao ler arquivo: {str(e)}"
            }

    def dry_run_yaml(self, yaml_content: str, namespace: str = 'default') -> Dict[str, Any]:
        """
        Executa dry-run do YAML usando create_from_yaml com dry_run
        
        Args:
            yaml_content (str): Conteúdo YAML do recurso
            namespace (str): Namespace de destino
            
        Returns:
            dict: Resultado da validação
        """
        try:
            # Validar parse do YAML
            resources = self._parse_yaml(yaml_content)
            if not resources:
                return {
                    "success": False,
                    "error": "YAML inválido ou vazio"
                }

            validated_resources = []
            errors = []

            # Para cada recurso, tentar dry-run usando a mesma abordagem do apply
            for resource in resources:
                try:
                    kind = resource.get('kind', '')
                    name = resource.get('metadata', {}).get('name', 'unnamed')
                    api_version = resource.get('apiVersion', '')
                    
                    # Validação básica
                    if not kind or not api_version:
                        errors.append(f"Recurso {name}: 'kind' e 'apiVersion' são obrigatórios")
                        continue

                    # Usar arquivo temporário igual ao apply, mas com dry-run
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as temp_file:
                        yaml.dump(resource, temp_file, default_flow_style=False)
                        temp_file_path = temp_file.name

                    try:
                        # Tentar dry-run usando create_from_yaml
                        cluster_wide_resources = ['Node', 'PersistentVolume', 'Namespace', 'ClusterRole', 'ClusterRoleBinding']
                        is_cluster_wide = kind in cluster_wide_resources
                        
                        create_from_yaml(
                            self.api_client,
                            temp_file_path,
                            namespace=namespace if not is_cluster_wide else None,
                            dry_run='All'  # Server-side dry-run
                        )
                        
                        # Se chegou aqui, validação passou
                        validated_resources.append({
                            "kind": kind,
                            "name": name,
                            "api_version": api_version,
                            "namespace": namespace if not is_cluster_wide else "cluster-wide",
                            "validation": "passed"
                        })

                    except ApiException as e:
                        if e.status == 409:  # Recurso já existe
                            validated_resources.append({
                                "kind": kind,
                                "name": name,
                                "api_version": api_version,
                                "namespace": namespace if not is_cluster_wide else "cluster-wide",
                                "validation": "passed",
                                "note": "recurso já existe"
                            })
                        else:
                            errors.append(f"{kind}/{name}: {e.reason}")
                    
                    finally:
                        # Limpar arquivo temporário
                        if os.path.exists(temp_file_path):
                            os.unlink(temp_file_path)

                except Exception as e:
                    errors.append(f"Erro na validação: {str(e)}")

            # Resultado final
            if errors and not validated_resources:
                return {
                    "success": False,
                    "errors": errors
                }
            elif errors:
                return {
                    "success": True,
                    "validated_resources": validated_resources,
                    "errors": errors,
                    "message": f"Validados {len(validated_resources)} recursos com {len(errors)} avisos/erros"
                }
            else:
                return {
                    "success": True,
                    "validated_resources": validated_resources,
                    "message": f"Todos os {len(validated_resources)} recursos validados com sucesso"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Erro no dry-run: {str(e)}"
            }
