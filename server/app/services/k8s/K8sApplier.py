from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.utils import create_from_yaml
import yaml
import tempfile
import os
from typing import Dict, List, Any
from .K8sExtractor import K8sExtractor


class K8sApplier:
    def __init__(self, config_file: str = None):
        """Inicializa o cliente Kubernetes para aplicação de recursos"""
        self._setup_k8s_client(config_file)
        self.k8s_extractor = K8sExtractor(config_file)

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

    def apply_yaml_content(self, yaml_content: str, namespace: str = 'default', skip_dry_run: bool = False) -> Dict[str, Any]:
        """
        Aplica conteúdo YAML ao cluster Kubernetes
        Verifica se os recursos já existem e usa create/patch conforme necessário
        """
        try:
            # 1. Validação dry-run opcional
            if not skip_dry_run:
                dry_run_result = self.dry_run_yaml(yaml_content, namespace)
                if not dry_run_result["success"]:
                    return {
                        "success": False,
                        "error": "Falha na validação dry-run",
                        "dry_run_errors": dry_run_result.get("errors", [])
                    }

            # 2. Parse dos recursos YAML
            resources = self._parse_yaml(yaml_content)
            if not resources:
                return {"success": False, "error": "YAML inválido ou vazio"}

            # 3. Aplicar cada recurso individualmente
            applied_resources = []
            errors = []

            for resource in resources:
                kind = resource.get('kind', '')
                name = resource.get('metadata', {}).get('name', '')
                res_namespace = resource.get('metadata', {}).get('namespace', namespace)
                
                if not kind or not name:
                    errors.append(f"Recurso inválido: kind='{kind}', name='{name}'")
                    continue

                # Verificar se existe e aplicar
                resource_type = self._kind_to_resource_type(kind)
                if not resource_type:
                    errors.append(f"Tipo de recurso '{kind}' não suportado")
                    continue

                exists = self._resource_exists(resource_type, name, res_namespace)
                action = "updated" if exists else "created"
                
                # Aplicar usando create_from_yaml (vai decidir create/update internamente)
                self._apply_resource(resource, res_namespace)
                
                applied_resources.append({
                    "kind": kind,
                    "name": name,
                    "namespace": res_namespace,
                    "action": action
                })
                print(f"{action.capitalize()}: {kind}/{name}")

            # 4. Resultado
            if applied_resources:
                return {
                    "success": True,
                    "applied_resources": applied_resources,
                    "errors": errors if errors else None,
                    "message": f"{len(applied_resources)} recursos aplicados"
                }
            else:
                return {"success": False, "errors": errors}

        except Exception as e:
            return {"success": False, "error": f"Erro na aplicação: {str(e)}"}

    def dry_run_yaml(self, yaml_content: str, namespace: str = 'default') -> Dict[str, Any]:
        """Validação básica do YAML"""
        try:
            resources = self._parse_yaml(yaml_content)
            if not resources:
                return {"success": False, "error": "YAML inválido ou vazio"}

            validated_resources = []
            errors = []

            for resource in resources:
                kind = resource.get('kind', '')
                name = resource.get('metadata', {}).get('name', '')
                
                if not kind or not name:
                    errors.append(f"Recurso inválido: kind='{kind}', name='{name}'")
                    continue
                
                # Validações específicas básicas
                validation_errors = self._validate_resource_fields(resource, kind)
                if validation_errors:
                    errors.extend([f"{kind}/{name}: {err}" for err in validation_errors])
                    continue

                validated_resources.append({
                    "kind": kind,
                    "name": name,
                    "validation": "passed"
                })

            return {
                "success": len(validated_resources) > 0,
                "validated_resources": validated_resources,
                "errors": errors,
                "message": f"Validados {len(validated_resources)} recursos"
            }

        except Exception as e:
            return {"success": False, "error": f"Erro no dry-run: {str(e)}"}

    def _parse_yaml(self, yaml_content: str) -> List[Dict[str, Any]]:
        """Parse do conteúdo YAML"""
        documents = yaml.safe_load_all(yaml_content)
        return [doc for doc in documents if doc and isinstance(doc, dict)]

    def _validate_resource_fields(self, resource: Dict[str, Any], kind: str) -> List[str]:
        """Validações básicas por tipo de recurso"""
        errors = []
        
        if kind == 'Pod' and 'spec' not in resource:
            errors.append("campo 'spec' é obrigatório")
        elif kind == 'Deployment':
            spec = resource.get('spec', {})
            if 'selector' not in spec:
                errors.append("campo 'spec.selector' é obrigatório")
        elif kind == 'Service':
            spec = resource.get('spec', {})
            if 'selector' not in spec and spec.get('type') != 'ExternalName':
                errors.append("campo 'spec.selector' é obrigatório para este tipo de Service")

        return errors

    def _resource_exists(self, resource_type: str, name: str, namespace: str) -> bool:
        """Verifica se recurso existe no cluster"""
        try:
            self.k8s_extractor.get_resource_by_name(resource_type, name, namespace)
            return True
        except KeyError:
            return False
        except:
            return False

    def _kind_to_resource_type(self, kind: str) -> str:
        """Converte kind para resource_type usando configuração do extractor"""
        for resource_name, config in self.k8s_extractor.resource_mapping.items():
            if config.get('kind') == kind:
                return resource_name
        return None

    def _apply_resource(self, resource: Dict[str, Any], namespace: str):
        """Aplica recurso usando create_from_yaml (lida com create/update automaticamente)"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as temp_file:
            yaml.dump(resource, temp_file, default_flow_style=False)
            temp_file_path = temp_file.name

        try:
            create_from_yaml(
                self.api_client, 
                temp_file_path, 
                namespace=namespace,
                apply=True
            )
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def delete_resource(self, resource_type: str, name: str, namespace: str = 'default') -> Dict[str, Any]:
        """
        Remove um recurso específico do cluster Kubernetes
        
        Args:
            resource_type (str): Tipo do recurso (pods, services, deployments, etc.)
            name (str): Nome do recurso
            namespace (str): Namespace do recurso (padrão: 'default')
            
        Returns:
            dict: Resultado da operação
        """
        try:
            # Verificar se o resource_type é suportado
            if resource_type not in self.k8s_extractor.resource_mapping:
                return {
                    "success": False,
                    "error": f"Tipo de recurso '{resource_type}' não suportado"
                }

            # Verificar se existe antes de tentar deletar
            if not self._resource_exists(resource_type, name, namespace):
                kind = self.k8s_extractor.resource_mapping[resource_type].get('kind', resource_type)
                return {
                    "success": False,
                    "error": f"Recurso '{kind}/{name}' não encontrado no namespace '{namespace}'"
                }

            # Obter configuração do recurso
            resource_config = self.k8s_extractor.resource_mapping[resource_type]
            kind = resource_config.get('kind', resource_type)

            # Executar delete
            self._delete_resource(name, resource_config, namespace)
            
            return {
                "success": True,
                "message": f"Recurso '{kind}/{name}' removido com sucesso",
                "deleted_resource": {
                    "kind": kind,
                    "name": name,
                    "namespace": namespace if not resource_config.get('cluster_wide') else 'cluster-wide'
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao deletar recurso: {str(e)}"
            }

    def _get_api_client(self, api_version: str):
        """Obtém cliente API baseado na versão"""
        if api_version == 'v1':
            return client.CoreV1Api()
        elif api_version == 'apps/v1':
            return client.AppsV1Api()
        elif api_version == 'networking.k8s.io/v1':
            return client.NetworkingV1Api()
        elif api_version == 'batch/v1':
            return client.BatchV1Api()
        else:
            return client.CoreV1Api()

    def _delete_resource(self, name: str, resource_config: Dict[str, Any], namespace: str):
        """Executa delete do recurso"""
        api_client = self._get_api_client(resource_config.get('api', 'v1'))
        delete_method_name = resource_config.get('delete_method')
        
        if not delete_method_name:
            raise ValueError(f"Método delete não configurado para {resource_config.get('kind')}")

        delete_method = getattr(api_client, delete_method_name)
        
        if resource_config.get('cluster_wide'):
            # Recurso cluster-wide
            delete_method(name=name)
        else:
            # Recurso namespaced
            delete_method(name=name, namespace=namespace)
