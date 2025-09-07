import requests
import json
from utils.util import getEnv
# from app.utils.util import getEnv

def format_pods_json(k8s_data):
    """
    Formata JSON do Kubernetes mapeando colunas com valores
    """
    columns = [col['name'] for col in k8s_data['columnDefinitions']]
    
    result = []
    for row in k8s_data['rows']:
        pod = {}
        pod["namespace"] = row['object']['metadata']['namespace']
        for i, value in enumerate(row['cells']):
            pod[columns[i]] = value
        result.append(pod)
    
    return result

def valid_object_type(object_type: str) -> bool:
    return object_type in ['pods', 'nodes', 'services', 'deployments', 'replicasets', 'namespaces', 'cronjobs']

def get_objects(object_type: str, namespace: str = "default"):
    """
        Lista um determinado objeto do cluster Kubernetes. 
        Valores aceitos: ['pods', 'nodes', 'services', 'deployments', 'replicasets', 'namespaces', 'cronjobs']
        Para 'replicasets' e 'cronjobs', o namespace é obrigatório.
    """
    try:
        if not valid_object_type(object_type):
            raise ValueError(f"Tipo de objeto inválido: {object_type}")
        
        url = f"{getEnv('K8S_BASE_URL')}/api/v1/{object_type}?limit=500"

        if object_type in ['deployments', 'replicasets']:
            url = f"{getEnv('K8S_BASE_URL')}/apis/apps/v1/namespaces/{namespace}/{object_type}?limit=500"

        if object_type == 'cronjobs':
            url = f"{getEnv('K8S_BASE_URL')}/apis/batch/v1/namespaces/{namespace}/{object_type}?limit=500"
        
        # Make a GET request to the API
        headers = {
            'Accept': 'application/json;as=Table;v=v1;g=meta.k8s.io,application/json;as=Table;v=v1beta1;g=meta.k8s.io,application/json',
            'User-Agent': 'kubectl.exe/v1.28.3 (windows/amd64) kubernetes/a8a1abc'
        }
        response = requests.get(
            url=url,
            cert=(
                getEnv("K8S_CERT_PATH"), 
                getEnv("K8S_KEY_CERT_PATH")
            ),
            headers=headers,
            timeout=30,
            verify=getEnv("K8S_CA_PATH")
        )

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            return format_pods_json(data)
        else:
            return f"Failed to retrieve data: {response.status_code} - {response.text}"
    except Exception as e:
        return f"An error occurred: {e}"
    
def get_object_definition(namespace: str, object_type: str, object_name: str):
    """
        Obtém a definição de um objeto específico do cluster Kubernetes. 
    """
    try:
        if not valid_object_type(object_type):
            raise ValueError(f"Tipo de objeto inválido: {object_type}")
        
        url = f"{getEnv('K8S_BASE_URL')}/api/v1/namespaces/{namespace}/{object_type}/{object_name}"
        # Make a GET request to the API
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'kubectl.exe/v1.28.3 (windows/amd64) kubernetes/a8a1abc'
        }
        response = requests.get(
            url=url,
            cert=(
                getEnv("K8S_CERT_PATH"), 
                getEnv("K8S_KEY_CERT_PATH")
            ),
            headers=headers,
            timeout=30,
            verify=getEnv("K8S_CA_PATH")
        )

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return f"Failed to retrieve data: {response.status_code} - {response.text}"
    except Exception as e:
        return f"An error occurred: {e}"
    
def get_pod_logs(namespace: str, object_name: str):
    """
        Obtém os logs de um pod específico do cluster Kubernetes.
        namespace: Namespace do pod;
        object_name: Nome do pod. 
    """
    try:
        
        url = f"{getEnv('K8S_BASE_URL')}/api/v1/namespaces/{namespace}/pods/{object_name}/log"
        # Make a GET request to the API
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'kubectl.exe/v1.28.3 (windows/amd64) kubernetes/a8a1abc'
        }
        response = requests.get(
            url=url,
            cert=(
                getEnv("K8S_CERT_PATH"), 
                getEnv("K8S_KEY_CERT_PATH")
            ),
            headers=headers,
            timeout=30,
            verify=getEnv("K8S_CA_PATH")
        )

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return f"Failed to retrieve data: {response.status_code} - {response.text}"
    except Exception as e:
        return f"An error occurred: {e}"