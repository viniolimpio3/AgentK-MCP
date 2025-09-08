from kubernetes import client, config
from kubernetes.client.rest import ApiException
import yaml
from typing import Dict, List, Any


class K8sExtractor:
    # Mapeamento unificado de recursos
    RESOURCE_MAPPING = {
        'pods': {
            'api': 'v1', 
            'kind': 'Pod', 
            'list_method': 'list_pod_for_all_namespaces', 
            'get_method': 'read_namespaced_pod'
        },
        'services': {
            'api': 'v1',
            'kind': 'Service',
            'list_method': 'list_service_for_all_namespaces',
            'get_method': 'read_namespaced_service'
        },
        'configmaps': {
            'api': 'v1',
            'kind': 'ConfigMap',
            'list_method': 'list_config_map_for_all_namespaces',
            'get_method': 'read_namespaced_config_map'
        },
        'secrets': {
            'api': 'v1',
            'kind': 'Secret',
            'list_method': 'list_secret_for_all_namespaces',
            'get_method': 'read_namespaced_secret'
        },
        'persistent_volume_claims': {
            'api': 'v1',
            'kind': 'PersistentVolumeClaim',
            'list_method': 'list_persistent_volume_claim_for_all_namespaces',
            'get_method': 'read_namespaced_persistent_volume_claim'
        },
        'nodes': {
            'api': 'v1',
            'kind': 'Node',
            'list_method': 'list_node',
            'get_method': 'read_node',
            'cluster_wide': True
        },
        'persistent_volumes': {
            'api': 'v1',
            'kind': 'PersistentVolume',
            'list_method': 'list_persistent_volume',
            'get_method': 'read_persistent_volume',
            'cluster_wide': True
        },
        'namespaces': {
            'api': 'v1',
            'kind': 'Namespace',
            'list_method': 'list_namespace',
            'get_method': 'read_namespace',
            'cluster_wide': True
        },
        'deployments': {
            'api': 'apps/v1',
            'kind': 'Deployment',
            'list_method': 'list_deployment_for_all_namespaces',
            'get_method': 'read_namespaced_deployment'
        },
        'replicasets': {
            'api': 'apps/v1',
            'kind': 'ReplicaSet',
            'list_method': 'list_replica_set_for_all_namespaces',
            'get_method': 'read_namespaced_replica_set'
        },
        'statefulsets': {
            'api': 'apps/v1',
            'kind': 'StatefulSet',
            'list_method': 'list_stateful_set_for_all_namespaces',
            'get_method': 'read_namespaced_stateful_set'
        },
        'ingresses': {
            'api': 'networking.k8s.io/v1',
            'kind': 'Ingress',
            'list_method': 'list_ingress_for_all_namespaces',
            'get_method': 'read_namespaced_ingress'
        },
        'cronjobs': {
            'api': 'batch/v1',
            'kind': 'CronJob',
            'list_method': 'list_cron_job_for_all_namespaces',
            'get_method': 'read_namespaced_cron_job'
        },
        'jobs': {
            'api': 'batch/v1',
            'kind': 'Job',
            'list_method': 'list_job_for_all_namespaces',
            'get_method': 'read_namespaced_job'
        }
    }

    def __init__(self, config_file: str = None, resources: List[str] = None):
        """Inicializa o cliente Kubernetes"""
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
        self.ignored_namespaces = ['kube-system', 'kube-public', 'kube-node-lease']
        valid_resources = self.get_valid_resources()
        if not all(res in valid_resources for res in resources):
            invalid = [res for res in resources if res not in valid_resources]
            raise ValueError(f"Invalid resources: {', '.join(invalid)}. Valid values are: {', '.join(valid_resources)}")

    def get_valid_resources(self) -> List[str]:
        """Retorna a lista de recursos Kubernetes suportados"""
        return list(self.RESOURCE_MAPPING.keys())

    def _get_api_client(self, resource_type: str):
        """Retorna o cliente API correto para o tipo de recurso"""
        if resource_type in ['deployments', 'replicasets', 'statefulsets']:
            return self.apps_v1
        elif resource_type == 'ingresses':
            return self.networking_v1
        return self.v1

    def _get_resources(self, resource_type: str) -> Dict[str, List]:
        """Obtém recursos de um tipo específico"""
        if resource_type not in self.RESOURCE_MAPPING:
            raise ValueError(f"Tipo de recurso inválido: {resource_type}")

        resource_info = self.RESOURCE_MAPPING[resource_type]
        api_client = self._get_api_client(resource_type)
        list_method = getattr(api_client, resource_info['list_method'])

        try:
            response = list_method()
            
            # Para recursos cluster-wide
            if resource_info.get('cluster_wide'):
                return {'cluster-wide': [item.to_dict() for item in response.items]}
            
            # Para recursos namespacados
            result = {}
            for item in response.items:
                namespace = item.metadata.namespace
                if namespace not in self.ignored_namespaces:
                    if namespace not in result:
                        result[namespace] = []
                    item_dict = item.to_dict()
                    if resource_type == 'secrets' and 'data' in item_dict:
                        item_dict['data'] = {'<REDACTED>': '<REDACTED>'}
                    result[namespace].append(item_dict)
            
            return result
        except ApiException as e:
            print(f"Erro ao listar {resource_type}: {e}")
            return {} if not resource_info.get('cluster_wide') else {'cluster-wide': []}

    def get_resource_by_name(self, resource_type: str, name: str, namespace: str = 'default') -> str:
        """Obtém um recurso específico por nome"""
        if resource_type not in self.RESOURCE_MAPPING:
            raise ValueError(f"Tipo de recurso inválido: {resource_type}")

        resource_info = self.RESOURCE_MAPPING[resource_type]
        api_client = self._get_api_client(resource_type)
        get_method = getattr(api_client, resource_info['get_method'])

        try:
            if resource_info.get('cluster_wide'):
                resource = get_method(name=name)
            else:
                resource = get_method(name=name, namespace=namespace)

            return self._format_resource_yaml(resource.to_dict(), resource_type)
        except ApiException as e:
            if e.status == 404:
                raise KeyError(f"Recurso {resource_type}/{name} não encontrado")
            raise

    def _format_resource_yaml(self, resource: Dict, resource_type: str) -> str:
        """Formata um recurso para YAML"""
        resource = self._clean_resource(resource.copy())
        
        # Garantir apiVersion e kind corretos
        info = self.RESOURCE_MAPPING[resource_type]
        resource['apiVersion'] = info['api']
        resource['kind'] = info['kind']

        return yaml.dump(resource, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def _clean_resource(self, resource: Dict) -> Dict:
        """Limpa campos desnecessários do recurso"""
        metadata_fields_to_remove = [
            'uid', 'resourceVersion', 'generation', 'creationTimestamp',
            'managedFields', 'deletionTimestamp', 'deletionGracePeriodSeconds',
            'ownerReferences', 'finalizers', 'selfLink'
        ]

        if 'metadata' in resource:
            metadata = resource['metadata']
            for field in metadata_fields_to_remove:
                metadata.pop(field, None)
            
            if 'annotations' in metadata and not metadata['annotations']:
                metadata.pop('annotations', None)

        # Remover status e campos vazios
        resource.pop('status', None)
        return {k: v for k, v in resource.items() if v is not None}

    def list_resources_cluster(self, resource_types: List[str] = None) -> Dict[str, List[str]]:
        """Lista apenas os nomes dos recursos por tipo"""
        if not resource_types:
            resource_types = list(self.RESOURCE_MAPPING.keys())

        result = {}
        for resource_type in resource_types:
            if resource_type not in self.RESOURCE_MAPPING:
                continue

            resources = self._get_resources(resource_type)
            names = []
            
            for items in resources.values():
                for item in items:
                    name = item.get('metadata', {}).get('name')
                    if name:
                        names.append(name)
            
            if names:
                result[resource_type] = names

        return result

    def export_to_yaml(self, resources: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
        """Exporta recursos para formato YAML"""
        result = {}
        
        for resource_type, namespaces in resources.items():
            if resource_type not in self.RESOURCE_MAPPING:
                continue

            resource_list = []
            for namespace, items in namespaces.items():
                if not items or namespace in self.ignored_namespaces:
                    continue
                
                for item in items:
                    name = item.get('metadata', {}).get('name', 'unnamed')
                    yaml_content = self._format_resource_yaml(item, resource_type)
                    
                    resource_list.append({
                        "name": name,
                        "content": yaml_content
                    })
            
            if resource_list:
                result[resource_type] = resource_list

        return result

    def get_all_cluster_resources(self, resource_types: List[str] = None) -> Dict[str, Any]:
        """Obtém todos os recursos do cluster dos tipos especificados"""
        if not resource_types:
            resource_types = list(self.RESOURCE_MAPPING.keys())

        resources = {}
        for resource_type in resource_types:
            if resource_type in self.RESOURCE_MAPPING:
                resources[resource_type] = self._get_resources(resource_type)

        return resources
