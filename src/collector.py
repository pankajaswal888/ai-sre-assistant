from kubernetes import client, config
from kubernetes.client.exceptions import ApiException

config.load_incluster_config()

v1 = client.CoreV1Api()
apps = client.AppsV1Api()


def collect(namespace, pod_name):

    try:
        pod = v1.read_namespaced_pod(pod_name, namespace)
    except ApiException as e:
        if e.status == 404:
            return None
        raise

    container = pod.spec.containers[0]
    status = pod.status.container_statuses[0]

    # ---- resolve service / deployment ----

    service = pod.metadata.labels.get("app")

    if not service:
        owners = pod.metadata.owner_references

        if owners:
            owner = owners[0]

            if owner.kind == "ReplicaSet":
                try:
                    rs = apps.read_namespaced_replica_set(owner.name, namespace)

                    if rs.metadata.owner_references:
                        service = rs.metadata.owner_references[0].name
                except ApiException:
                    service = None

            elif owner.kind == "Deployment":
                service = owner.name

    if not service:
        service = "unknown"

    # ---- parse image tag ----

    image = container.image
    image_tag = None

    if ":" in image:
        image_tag = image.split(":")[-1]

    # ---- resource requests ----

    resource_requests = None

    if container.resources and container.resources.requests:
        resource_requests = container.resources.requests

    # ---- exit code ----

    exit_code = None

    if status.last_state and status.last_state.terminated:
        exit_code = status.last_state.terminated.exit_code

    # ---- evidence payload ----

    evidence = {
        "service": service,
        "namespace": namespace,

        "pod": {
            "name": pod.metadata.name,
            "node": pod.spec.node_name
        },

        "container": {
            "name": container.name,
            "image": image,
            "image_tag": image_tag
        },

        "resources": {
            "memory_limit":
                container.resources.limits.get("memory")
                if container.resources and container.resources.limits
                else None,

            "requests": resource_requests
        },

        "status": {
            "restart_count": status.restart_count,
            "exit_code": exit_code,
            "termination_reason":
                status.last_state.terminated.reason
                if status.last_state and status.last_state.terminated
                else None
        }
    }

    return evidence
