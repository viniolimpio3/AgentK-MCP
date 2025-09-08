from kubernetes import client, config
from kubernetes.client.rest import ApiException
from typing import Dict, List, Any
import yaml
import os
import json


class K8sExtractor:
    def __init__(self, config_file: str = None, resources: List[str] = None, resource_config_path: str = None):
        """Inicializa o cliente Kubernetes"""
        self._setup_k8s_client(config_file)
        self._load_config(resource_config_path)
        self._validate_resources(resources)

    def _setup_k8s_client(self, config_file: str = None):
        """Configura cliente Kubernetes"""
        if config_file:
            config.load_kube_config(config_file=config_file)
        else:
            try:
                config.load_incluster_config()
            except:
                config.load_kube_config()
        
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.networking_v1 = client.NetworkingV1Api()
        self.batch_v1 = client.BatchV1Api()

    def _load_config(self, config_path: str = None):
        """Carrega configuração de recursos"""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'resource_config.yaml')
        
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config_data = yaml.safe_load(file)
                self.resource_mapping = config_data.get('resources', {})
                self.ignored_namespaces = config_data.get('ignored_namespaces', [])
        except (FileNotFoundError, yaml.YAMLError) as e:
            raise ValueError(f"Erro ao carregar configuração: {e}")

    def _validate_resources(self, resources: List[str]):
        """Valida recursos solicitados"""
        if resources:
            valid = self.get_valid_resources()
            invalid = [r for r in resources if r not in valid]
            if invalid:
                raise ValueError(f"Recursos inválidos: {', '.join(invalid)}")

    def get_valid_resources(self) -> List[str]:
        """Retorna recursos suportados"""
        return list(self.resource_mapping.keys())

    def _get_api_client(self, resource_type: str):
        """Retorna cliente API correto"""
        api = self.resource_mapping.get(resource_type, {}).get('api', 'v1')
        
        if api.startswith('apps/'):
            return self.apps_v1
        elif api.startswith('networking'):
            return self.networking_v1
        elif api.startswith('batch/'):
            return self.batch_v1
        return self.v1

    def _get_resources(self, resource_type: str) -> Dict[str, List]:
        """Obtém recursos de um tipo específico"""
        if resource_type not in self.resource_mapping:
            raise ValueError(f"Recurso inválido: {resource_type}")

        info = self.resource_mapping[resource_type]
        client = self._get_api_client(resource_type)
        method = getattr(client, info['list_method'])

        try:
            response = method()
            
            if info.get('cluster_wide'):
                return {'cluster-wide': [item.to_dict() for item in response.items]}
            
            result = {}
            for item in response.items:
                ns = item.metadata.namespace
                if ns not in self.ignored_namespaces:
                    if ns not in result:
                        result[ns] = []
                    item_dict = item.to_dict()
                    if resource_type == 'secrets' and 'data' in item_dict:
                        item_dict['data'] = {'<REDACTED>': '<REDACTED>'}
                    result[ns].append(item_dict)
            
            return result
        except ApiException as e:
            print(f"Erro ao listar {resource_type}: {e}")
            return {} if not info.get('cluster_wide') else {'cluster-wide': []}

    def get_resource_by_name(self, resource_type: str, name: str, namespace: str = 'default') -> str:
        """Obtém um recurso específico por nome"""
        if resource_type not in self.resource_mapping:
            raise ValueError(f"Recurso inválido: {resource_type}")

        info = self.resource_mapping[resource_type]
        client = self._get_api_client(resource_type)
        method = getattr(client, info['get_method'])

        try:
            if info.get('cluster_wide'):
                resource = method(name=name)
            else:
                resource = method(name=name, namespace=namespace)

            return self._format_yaml(resource.to_dict(), resource_type)
        except ApiException as e:
            if e.status == 404:
                raise KeyError(f"Recurso {resource_type}/{name} não encontrado")
            raise

    def _format_yaml(self, resource: Dict, resource_type: str) -> str:
        """Formata recurso para YAML"""
        resource = self._clean_resource(resource.copy())
        info = self.resource_mapping[resource_type]
        resource['apiVersion'] = info['api']
        resource['kind'] = info['kind']
        return yaml.dump(resource, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def _clean_resource(self, resource: Dict) -> Dict:
        """Limpa campos desnecessários, priorizando last-applied-configuration"""
        
        # Tentar usar last-applied-configuration se disponível
        if ('metadata' in resource and 
            'annotations' in resource['metadata'] and 
            resource['metadata']['annotations'] and
            'kubectl.kubernetes.io/last-applied-configuration' in resource['metadata']['annotations']):
            
            try:
                
                last_applied = resource['metadata']['annotations']['kubectl.kubernetes.io/last-applied-configuration']
                clean_resource = json.loads(last_applied)
                
                # Garantir que temos os campos básicos obrigatórios
                if 'metadata' not in clean_resource:
                    clean_resource['metadata'] = {}
                if 'name' not in clean_resource['metadata']:
                    clean_resource['metadata']['name'] = resource.get('metadata', {}).get('name')
                if 'namespace' not in clean_resource['metadata'] and 'namespace' in resource.get('metadata', {}):
                    clean_resource['metadata']['namespace'] = resource['metadata']['namespace']
                
                # Remover annotations completamente do resultado final
                if 'annotations' in clean_resource.get('metadata', {}):
                    clean_resource['metadata'].pop('annotations', None)
                
                return clean_resource
                
            except (json.JSONDecodeError, KeyError):
                # Se falhar, usar limpeza manual
                pass
        
        # Limpeza manual como fallback
        remove_fields = ['uid', 'resourceVersion', 'generation', 'creationTimestamp',
                        'managedFields', 'deletionTimestamp', 'deletionGracePeriodSeconds',
                        'ownerReferences', 'finalizers', 'selfLink']

        if 'metadata' in resource:
            metadata = resource['metadata']
            for field in remove_fields:
                metadata.pop(field, None)
            
            # Remover annotations completamente
            metadata.pop('annotations', None)

        resource.pop('status', None)
        return {k: v for k, v in resource.items() if v is not None}

    def list_resources_cluster(self, resource_types: List[str] = None) -> Dict[str, List[str]]:
        """Lista nomes dos recursos por tipo"""
        if not resource_types:
            resource_types = list(self.resource_mapping.keys())

        result = {}
        for rt in resource_types:
            if rt not in self.resource_mapping:
                continue
            resources = self._get_resources(rt)
            names = [item.get('metadata', {}).get('name') 
                    for items in resources.values() for item in items 
                    if item.get('metadata', {}).get('name')]
            if names:
                result[rt] = names
        return result

    def export_to_yaml(self, resources: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
        """Exporta recursos para YAML"""
        result = {}
        for rt, namespaces in resources.items():
            if rt not in self.resource_mapping:
                continue
            resource_list = []
            for ns, items in namespaces.items():
                if not items or ns in self.ignored_namespaces:
                    continue
                for item in items:
                    name = item.get('metadata', {}).get('name', 'unnamed')
                    content = self._format_yaml(item, rt)
                    resource_list.append({"name": name, "content": content})
            if resource_list:
                result[rt] = resource_list
        return result

    def get_all_cluster_resources(self, resource_types: List[str] = None) -> Dict[str, Any]:
        """Obtém todos os recursos do cluster"""
        if not resource_types:
            resource_types = list(self.resource_mapping.keys())
        return {rt: self._get_resources(rt) for rt in resource_types if rt in self.resource_mapping}
