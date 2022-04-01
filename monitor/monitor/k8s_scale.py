from collections.abc import Iterator
from kubernetes import client, config
import os

NAMESPACE_FILE = "/var/run/secrets/kubernetes.io/serviceaccount/namespace"


def scale_deployments(deployment_scales):
    if not os.path.isfile(NAMESPACE_FILE):
        raise Exception(
            "Namespace file not found. Is this running in a kubernetes pod?"
        )

    namespace = open(NAMESPACE_FILE, "r").read()
    config.load_incluster_config()
    apps_api = client.AppsV1Api()

    def get_scale(deployment):
        raw = apps_api.read_namespaced_deployment_scale(deployment, namespace)
        return raw.spec.replicas

    def set_scale(deployment, count):
        body = {"spec": {"replicas": count}}
        raw = apps_api.patch_namespaced_deployment_scale(deployment, namespace, body)
        return raw.spec.replicas

    def scale_one(deployment, scale):
        prev = get_scale(deployment)
        cur = set_scale(deployment, scale)
        return (deployment, scale, prev, cur)

    return [scale_one(*a) for a in deployment_scales.items()]
