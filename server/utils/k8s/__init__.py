import os
import pathlib
from kubernetes import client, config


def load_config(config_file):
    config.load_kube_config(config_file=config_file)


def null(**kwargs):
    print("warning: not support")


class ApiResource:
    """
    k8sUtils api resource 资源method
    """

    def get(self, **kwargs): null()

    def create(self, **kwargs): null()

    def delete(self, **kwargs): null()

    def patch(self, **kwargs): null()

    def replace(self, **kwargs): null()

    def list_all(self, **kwargs): null()

    def list(self, **kwargs): null()


class CustomRegister(ApiResource):
    """
    k8sUtils 第三方资源注册
    """

    def __init__(self,
                 group: str = None, version: str = None,
                 plural: str = None):
        super(CustomRegister, self).__init__()
        self.api = client.CustomObjectsApi()
        self.group = group
        self.version = version
        self.plural = plural

    def get(self, namespace, name):
        return self.api.get_namespaced_custom_object(
            group=self.group,
            version=self.version, namespace=namespace,
            plural=self.plural, name=name)

    def create(self, namespace, body):
        return self.api.create_namespaced_custom_object(
            namespace=namespace, body=body,
            group=self.group, version=self.version, plural=self.plural)

    def delete(self, name, namespace):
        return self.api.delete_namespaced_custom_object(
            name=name, namespace=namespace,
            group=self.group, version=self.version, plural=self.plural)

    def list(self, namespace):
        return self.api.list_namespaced_custom_object(
            namespace=namespace,
            group=self.group, version=self.version, plural=self.plural)

    def list_all(self):
        return self.api.list_cluster_custom_object(group=self.group, version=self.version, plural=self.plural)

    def read(self):
        return

    def patch(self, name, namespace, body):
        return self.api.patch_namespaced_custom_object(
            name=name, namespace=namespace, body=body,
            group=self.group, version=self.version, plural=self.plural)

    def replace(self, name, namespace, body):
        return self.api.replace_namespaced_custom_object(
            name=name, namespace=namespace, body=body,
            group=self.group, version=self.version, plural=self.plural)


# ---------------------------------------- k8s.io
class Deployment(ApiResource):
    def __init__(self):
        super(Deployment, self).__init__()
        self.api = client.AppsV1Api()
        self.get = self.api.read_namespaced_deployment
        self.create = self.api.create_namespaced_deployment
        self.delete = self.api.delete_namespaced_deployment
        self.patch = self.api.patch_namespaced_deployment
        self.replace = self.api.replace_namespaced_deployment
        self.list_all = self.api.list_deployment_for_all_namespaces
        self.list = self.api.list_namespaced_deployment


class Service(ApiResource):
    def __init__(self):
        super(Service, self).__init__()
        self.api = client.CoreV1Api()
        self.get = self.api.read_namespaced_service
        self.create = self.api.create_namespaced_service
        self.delete = self.api.delete_namespaced_service
        self.patch = self.api.patch_namespaced_service
        self.replace = self.api.read_namespaced_service
        self.list_all = self.api.list_service_for_all_namespaces
        self.list = self.api.list_namespaced_service


class Ingress(ApiResource):
    def __init__(self):
        super(Ingress, self).__init__()
        self.api = client.ExtensionsV1beta1Api()
        self.get = self.api.read_namespaced_ingress
        self.create = self.api.create_namespaced_ingress
        self.delete = self.api.delete_namespaced_ingress
        self.patch = self.api.patch_namespaced_ingress
        self.replace = self.api.replace_namespaced_ingress
        self.list_all = self.api.list_deployment_for_all_namespaces
        self.list = self.api.list_namespaced_ingress


class AutoScaler(ApiResource):
    def __init__(self):
        super(AutoScaler, self).__init__()
        self.api = client.AutoscalingV1Api()
        self.get = self.api.read_namespaced_horizontal_pod_autoscaler
        self.create = self.api.create_namespaced_horizontal_pod_autoscaler
        self.delete = self.api.delete_namespaced_horizontal_pod_autoscaler
        self.patch = self.api.patch_namespaced_horizontal_pod_autoscaler
        self.replace = self.api.replace_namespaced_horizontal_pod_autoscaler
        self.list_all = self.api.list_horizontal_pod_autoscaler_for_all_namespaces
        self.list = self.api.list_namespaced_horizontal_pod_autoscaler


class Pod(ApiResource):

    def __init__(self):
        super(Pod, self).__init__()
        self.api = client.CoreV1Api()
        self.get = self.api.read_namespaced_pod
        self.create = self.api.create_namespaced_pod
        self.delete = self.api.delete_namespaced_pod
        self.patch = self.api.patch_namespaced_pod
        self.replace = self.api.replace_namespaced_pod
        self.list_all = self.api.list_pod_for_all_namespaces
        self.list = self.api.list_namespaced_pod


class Node(ApiResource):
    def __init__(self):
        super(Node, self).__init__()
        self.api = client.CoreV1Api()
        self.get = self.api.read_node
        self.create = self.api.create_node
        self.delete = self.api.delete_node
        self.patch = self.api.patch_node
        self.replace = self.api.replace_namespace
        self.list_all = self.api.list_node
        self.list = self.api.list_node


class Job(ApiResource):
    def __init__(self):
        super(Job, self).__init__()
        self.api = client.BatchV1Api()
        self.get = self.api.read_namespaced_job
        self.create = self.api.create_namespaced_job
        self.delete = self.api.delete_namespaced_job
        self.patch = self.api.patch_namespaced_job
        self.replace = self.api.replace_namespaced_job
        self.list_all = self.api.list_job_for_all_namespaces
        self.list = self.api.list_namespaced_job


# ---------------------------
class K8s:
    @property
    def deployment(self):
        return Deployment()

    @property
    def service(self): return Service()

    @property
    def ingress(self): return Ingress()

    @property
    def hpa(self): return AutoScaler()

    @property
    def pod(self): return Pod()

    @property
    def node(self): return Node()

    @property
    def job(self): return Job()


if __name__ == '__main__':
    load_config("../../.kube/kubeconfig.yaml")
    k8s_job = K8s().job
    k8s_service = K8s().service
    print(k8s_job.list_all())
    print(k8s_service.list_all())
    
