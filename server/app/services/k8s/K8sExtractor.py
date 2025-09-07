from kubernetes import client, config
from kubernetes.client.rest import ApiException
import yaml
import os
from typing import Dict, List, Any
from datetime import datetime


class K8sExtractor:
    def __init__(self, config_file: str = None):
        """
        Inicializa o cliente Kubernetes
        
        Args:
            config_file: Caminho para o arquivo kubeconfig (opcional)
        """
        if config_file:
            config.load_kube_config(config_file=config_file)
        else:
            # Tenta carregar configuração in-cluster ou do kubeconfig padrão
            try:
                config.load_incluster_config()
            except:
                config.load_kube_config()
        
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.networking_v1 = client.NetworkingV1Api()
        self.rbac_v1 = client.RbacAuthorizationV1Api()
        self.storage_v1 = client.StorageV1Api()

        self.ignored_namespaces = ['kube-system', 'kube-public', 'kube-node-lease']
    
    @staticmethod
    def get_valid_resources() -> List[str]:
        """Retorna a lista de recursos Kubernetes suportados"""
        return [
            'pods', 'services', 'deployments', 'configmaps', 'secrets',
            'ingresses', 'persistent_volume_claims', 
            'replicasets', 'statefulsets', 'nodes', 'persistent_volumes',
            'namespaces'
        ]

    def get_all_namespaces(self) -> List[str]:
        """Obtém todos os namespaces"""
        try:
            namespaces = self.v1.list_namespace()
            return [ns.metadata.name for ns in namespaces.items]
        except ApiException as e:
            print(f"Erro ao obter namespaces: {e}")
            return ['default']
    
    def get_pods_all_namespaces(self) -> Dict[str, List]:
        """Obtém todos os pods de todos os namespaces"""
        try:
            pods = self.v1.list_pod_for_all_namespaces()
            
            pods_by_namespace = {}
            
            for pod in pods.items:
                namespace = pod.metadata.namespace
                if namespace not in pods_by_namespace:
                    pods_by_namespace[namespace] = []
                
                # Converter para dict para serialização
                pod_dict = pod.to_dict()
                pods_by_namespace[namespace].append(pod_dict)
            
            return pods_by_namespace
        except ApiException as e:
            print(f"Erro ao obter pods: {e}")
            return {}
    
    def get_services_all_namespaces(self) -> Dict[str, List]:
        """Obtém todos os services"""
        try:
            services = self.v1.list_service_for_all_namespaces()
            services_by_namespace = {}
            
            for service in services.items:
                namespace = service.metadata.namespace
                if namespace not in services_by_namespace:
                    services_by_namespace[namespace] = []
                
                service_dict = service.to_dict()
                services_by_namespace[namespace].append(service_dict)
            
            return services_by_namespace
        except ApiException as e:
            print(f"Erro ao obter services: {e}")
            return {}
    
    def get_deployments_all_namespaces(self) -> Dict[str, List]:
        """Obtém todos os deployments"""
        try:
            deployments = self.apps_v1.list_deployment_for_all_namespaces()
            deployments_by_namespace = {}
            
            for deployment in deployments.items:
                namespace = deployment.metadata.namespace
                if namespace not in deployments_by_namespace:
                    deployments_by_namespace[namespace] = []
                
                deployment_dict = deployment.to_dict()
                deployments_by_namespace[namespace].append(deployment_dict)
            
            return deployments_by_namespace
        except ApiException as e:
            print(f"Erro ao obter deployments: {e}")
            return {}
    
    def get_configmaps_all_namespaces(self) -> Dict[str, List]:
        """Obtém todos os configmaps"""
        try:
            configmaps = self.v1.list_config_map_for_all_namespaces()
            configmaps_by_namespace = {}
            
            for cm in configmaps.items:
                namespace = cm.metadata.namespace
                if namespace not in configmaps_by_namespace:
                    configmaps_by_namespace[namespace] = []
                
                cm_dict = cm.to_dict()
                configmaps_by_namespace[namespace].append(cm_dict)
            
            return configmaps_by_namespace
        except ApiException as e:
            print(f"Erro ao obter configmaps: {e}")
            return {}
    
    def get_secrets_all_namespaces(self) -> Dict[str, List]:
        """Obtém todos os secrets"""
        try:
            secrets = self.v1.list_secret_for_all_namespaces()
            secrets_by_namespace = {}
            
            for secret in secrets.items:
                namespace = secret.metadata.namespace
                if namespace not in secrets_by_namespace:
                    secrets_by_namespace[namespace] = []
                
                secret_dict = secret.to_dict()
                # Removendo dados sensíveis
                if 'data' in secret_dict:
                    secret_dict['data'] = {'<REDACTED>': '<REDACTED>'}
                
                secrets_by_namespace[namespace].append(secret_dict)
            
            return secrets_by_namespace
        except ApiException as e:
            print(f"Erro ao obter secrets: {e}")
            return {}
    
    def get_ingresses_all_namespaces(self) -> Dict[str, List]:
        """Obtém todos os ingresses"""
        try:
            ingresses = self.networking_v1.list_ingress_for_all_namespaces()
            ingresses_by_namespace = {}
            
            for ingress in ingresses.items:
                namespace = ingress.metadata.namespace
                if namespace not in ingresses_by_namespace:
                    ingresses_by_namespace[namespace] = []
                
                ingress_dict = ingress.to_dict()
                ingresses_by_namespace[namespace].append(ingress_dict)
            
            return ingresses_by_namespace
        except ApiException as e:
            print(f"Erro ao obter ingresses: {e}")
            return {}
    
    def get_persistent_volume_claims_all_namespaces(self) -> Dict[str, List]:
        """Obtém todos os PVCs"""
        try:
            pvcs = self.v1.list_persistent_volume_claim_for_all_namespaces()
            pvcs_by_namespace = {}
            
            for pvc in pvcs.items:
                namespace = pvc.metadata.namespace
                if namespace not in pvcs_by_namespace:
                    pvcs_by_namespace[namespace] = []
                
                pvc_dict = pvc.to_dict()
                pvcs_by_namespace[namespace].append(pvc_dict)
            
            return pvcs_by_namespace
        except ApiException as e:
            print(f"Erro ao obter PVCs: {e}")
            return {}
    
    def get_replicasets_all_namespaces(self) -> Dict[str, List]:
        """Obtém todos os replicasets"""
        try:
            replicasets = self.apps_v1.list_replica_set_for_all_namespaces()
            replicasets_by_namespace = {}
            
            for rs in replicasets.items:
                namespace = rs.metadata.namespace
                if namespace not in replicasets_by_namespace:
                    replicasets_by_namespace[namespace] = []
                
                rs_dict = rs.to_dict()
                replicasets_by_namespace[namespace].append(rs_dict)
            
            return replicasets_by_namespace
        except ApiException as e:
            print(f"Erro ao obter replicasets: {e}")
            return {}
    
    def get_statefulsets_all_namespaces(self) -> Dict[str, List]:
        """Obtém todos os statefulsets"""
        try:
            statefulsets = self.apps_v1.list_stateful_set_for_all_namespaces()
            statefulsets_by_namespace = {}
            
            for sts in statefulsets.items:
                namespace = sts.metadata.namespace
                if namespace not in statefulsets_by_namespace:
                    statefulsets_by_namespace[namespace] = []
                
                sts_dict = sts.to_dict()
                statefulsets_by_namespace[namespace].append(sts_dict)
            
            return statefulsets_by_namespace
        except ApiException as e:
            print(f"Erro ao obter statefulsets: {e}")
            return {}
    
    def get_all_cluster_resources(self, resource_types: List[str] = None) -> Dict[str, Any]:
        """
        Obtém recursos do cluster
        
        Args:
            resource_types: Lista de tipos de recursos para coletar. 
                          Se None, coleta os principais tipos.
        """

        valid_resources = self.get_valid_resources()
        for res in resource_types or []:
            if res not in valid_resources:
                raise ValueError(f"Recurso inválido: {res}. Valores aceitos: {', '.join(valid_resources)}")

        if resource_types is None:
            resource_types = [
                'pods', 'services', 'deployments', 'configmaps', 'secrets',
                'ingresses', 'persistent_volume_claims', 
                'replicasets', 'statefulsets', 'nodes', 'persistent_volumes'
            ]
        
        resources = {}
        
        # Mapeamento dos métodos para cada tipo de recurso
        resource_methods = {
            'pods': self.get_pods_all_namespaces,
            'services': self.get_services_all_namespaces,
            'deployments': self.get_deployments_all_namespaces,
            'configmaps': self.get_configmaps_all_namespaces,
            'secrets': self.get_secrets_all_namespaces,
            'ingresses': self.get_ingresses_all_namespaces,
            'persistent_volume_claims': self.get_persistent_volume_claims_all_namespaces,
            'replicasets': self.get_replicasets_all_namespaces,
            'statefulsets': self.get_statefulsets_all_namespaces,
        }
        
        # Recursos namespacados
        for resource_type in resource_types:
            if resource_type in resource_methods:
                print(f"Coletando {resource_type}...")
                resources[resource_type] = resource_methods[resource_type]()
        
        # Recursos não namespacados (cluster-wide)
        if 'nodes' in resource_types:
            print("Coletando nodes...")
            try:
                nodes = self.v1.list_node()
                resources['nodes'] = {'cluster-wide': [node.to_dict() for node in nodes.items]}
            except ApiException as e:
                print(f"Erro ao obter nodes: {e}")
                resources['nodes'] = {'cluster-wide': []}
        
        if 'persistent_volumes' in resource_types:
            print("Coletando persistent volumes...")
            try:
                pvs = self.v1.list_persistent_volume()
                resources['persistent_volumes'] = {'cluster-wide': [pv.to_dict() for pv in pvs.items]}
            except ApiException as e:
                print(f"Erro ao obter PVs: {e}")
                resources['persistent_volumes'] = {'cluster-wide': []}
        
        if 'namespaces' in resource_types:
            print("Coletando namespaces...")
            try:
                namespaces = self.v1.list_namespace()
                resources['namespaces'] = {'cluster-wide': [ns.to_dict() for ns in namespaces.items]}
            except ApiException as e:
                print(f"Erro ao obter namespaces: {e}")
                resources['namespaces'] = {'cluster-wide': []}
        
        return resources
    
    def clean_resource_for_export(self, resource: Dict, minimal: bool = False) -> Dict:
        """
        Limpa campos desnecessários para export
        
        Args:
            resource: Recurso a ser limpo
            minimal: Se True, remove ainda mais campos para um export mínimo
        """
        # Fazer uma cópia para não modificar o original
        cleaned = resource.copy()
        
        # Limpar metadata
        if 'metadata' in cleaned:
            metadata = cleaned['metadata']
            
            # Campos básicos a serem sempre removidos
            basic_fields_to_remove = [
                'uid', 'self_link', 'resource_version', 'generation',
                'creation_timestamp', 'managed_fields', 'deletion_timestamp',
                'deletion_grace_period_seconds', 'owner_references'
            ]
            
            # Campos adicionais para export mínimo
            if minimal:
                basic_fields_to_remove.extend([
                    'finalizers', 'generate_name'
                ])
            
            for field in basic_fields_to_remove:
                metadata.pop(field, None)
            
            # Limpar annotations vazias ou desnecessárias
            if 'annotations' in metadata:
                annotations = metadata['annotations']
                if not annotations or annotations == {}:
                    metadata.pop('annotations', None)
                elif minimal:
                    # Em modo mínimo, manter apenas annotations essenciais
                    essential_annotations = {}
                    for key, value in annotations.items():
                        if not key.startswith('kubectl.kubernetes.io/'):
                            essential_annotations[key] = value
                    metadata['annotations'] = essential_annotations if essential_annotations else None
                    if not metadata['annotations']:
                        metadata.pop('annotations', None)
        
        # Remover status (sempre, pois é runtime)
        cleaned.pop('status', None)
        
        # Limpar spec baseado no tipo de recurso
        if 'spec' in cleaned and minimal:
            spec = cleaned['spec']
            
            # Para Services, remover campos null/vazios
            if cleaned.get('kind') == 'Service' or 'ports' in spec:
                fields_to_check = [
                    'allocate_load_balancer_node_ports', 'external_i_ps', 'external_name',
                    'external_traffic_policy', 'health_check_node_port', 'load_balancer_class',
                    'load_balancer_ip', 'load_balancer_source_ranges', 'publish_not_ready_addresses',
                    'session_affinity_config', 'traffic_distribution'
                ]
                
                for field in fields_to_check:
                    if spec.get(field) is None:
                        spec.pop(field, None)
                
                # Limpar ports
                if 'ports' in spec:
                    for port in spec['ports']:
                        port_fields_to_check = ['app_protocol', 'node_port']
                        for field in port_fields_to_check:
                            if port.get(field) is None:
                                port.pop(field, None)
        
        # Remover campos null de nível superior
        if minimal:
            cleaned = {k: v for k, v in cleaned.items() if v is not None}
        
        return cleaned
    
    def _remove_none_values(self, obj):
        """Remove recursivamente valores None de dicts e listas"""
        if isinstance(obj, dict):
            return {k: self._remove_none_values(v) for k, v in obj.items() 
                   if v is not None and v != {} and v != []}
        elif isinstance(obj, list):
            return [self._remove_none_values(item) for item in obj 
                   if item is not None and item != {} and item != []]
        else:
            return obj

    def export_to_yaml(self, resources: Dict[str, Any], 
                      clean_export: bool = True,
                      minimal_export: bool = False):
        """
        Exporta todos os recursos para um único arquivo YAML
        
        Args:
            resources: Recursos para exportar
            base_path: Diretório base para export
            clean_export: Se deve limpar campos desnecessários
            minimal_export: Se deve fazer um export mínimo (mais limpo)
        """
        # filename = f"resources_{datetime.now().strftime('%d%m%Y%H%M%S')}.yaml"
        
        yaml_content = "# Kubernetes Resources Export\n"
        yaml_content += f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        yaml_content += "# " + "="*60 + "\n\n"
        
        first_resource = True
        for resource_type, namespaces in resources.items():
            # Add resource type header
            yaml_content += f"# Resource Type: {resource_type.upper()}\n"
            yaml_content += "# " + "-"*60 + "\n\n"
            
            for namespace, items in namespaces.items():
                if not items or namespace in self.ignored_namespaces:
                    continue
                
                # Add namespace header
                yaml_content += f"# Namespace: {namespace}\n"
                yaml_content += f"# Total resources in this namespace: {len(items)}\n\n"
                
                for i, item in enumerate(items):
                    if clean_export:
                        item = self.clean_resource_for_export(item.copy(), minimal=minimal_export)
                    
                    # Add separator between resources, but not before the first one
                    if not first_resource:
                        yaml_content += "\n---\n\n"
                    first_resource = False
                    
                    # Add detailed comment for each resource
                    name = item.get('metadata', {}).get('name', 'unnamed')
                    yaml_content += f"# Resource: {resource_type} - {name}\n"
                    
                    # Adicionar apiVersion e kind se não existirem
                    if 'api_version' not in item or item['api_version'] is None:
                        apiVersionMapping = {
                            'services': 'v1',
                            'pods': 'v1',
                            'deployments': 'apps/v1',
                            'configmaps': 'v1',
                            'secrets': 'v1',
                            'ingresses': 'networking.k8s.io/v1',
                        }
                        kindMapping = {
                            'services': 'Service',
                            'pods': 'Pod',
                            'deployments': 'Deployment',
                            'configmaps': 'ConfigMap',
                            'secrets': 'Secret',
                            'ingresses': 'Ingress',
                        }

                        item["apiVersion"] = apiVersionMapping.get(resource_type, 'v1')
                        item["kind"] = kindMapping.get(resource_type, resource_type.rstrip('s').title())
                    
                    # Remover campos com valor None se minimal_export
                    if minimal_export:
                        item = self._remove_none_values(item)
                    
                    # Reorganizar para manter apiVersion e kind no topo
                    ordered_item = {}
                    if 'apiVersion' in item:
                        ordered_item['apiVersion'] = item['apiVersion']
                    if 'kind' in item:
                        ordered_item['kind'] = item['kind']
                    for key, value in item.items():
                        if key not in ['apiVersion', 'kind']:
                            ordered_item[key] = value
                    item = ordered_item
                    
                    yaml_content += yaml.dump(item, 
                        default_flow_style=False, 
                        allow_unicode=True,
                        sort_keys=False,
                        default_style=None)
            
            # Add a visual separator between different resource types
            yaml_content += "\n# " + "="*60 + "\n\n"
        
        # Write all content to a single file
        # with open(filepath, 'w', encoding='utf-8') as f:
        #     f.write(yaml_content)
        
        # print(f"Todos os recursos exportados para: {filepath}")
        return yaml_content