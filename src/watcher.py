from kubernetes import client, config, watch


def build_payload(v1, namespace, pod_name, reason, message):
    """
    Build enriched payload for AI analysis
    """

    try:
        pod = v1.read_namespaced_pod(pod_name, namespace)
    except Exception as e:
        print(f"Failed to read pod {pod_name}: {e}")
        return None

    container = pod.spec.containers[0]
    container_name = container.name
    image = container.image

    restart_count = 0
    last_state = None
    exit_code = None
    termination_message = None
    oom_killed = False

    liveness_probe = None
    readiness_probe = None
    resource_limits = None

    if container.resources and container.resources.limits:
        resource_limits = container.resources.limits

    if container.liveness_probe:
        liveness_probe = "configured"

    if container.readiness_probe:
        readiness_probe = "configured"

    if pod.status.container_statuses:
        status = pod.status.container_statuses[0]

        restart_count = status.restart_count

        if status.last_state and status.last_state.terminated:
            last_state = status.last_state.terminated.reason
            exit_code = status.last_state.terminated.exit_code
            termination_message = status.last_state.terminated.message

            if status.last_state.terminated.reason == "OOMKilled":
                oom_killed = True

    # Resolve deployment owner
    deployment = None
    owners = pod.metadata.owner_references

    if owners:
        owner = owners[0]

        if owner.kind == "ReplicaSet":
            deployment = owner.name
        elif owner.kind == "Deployment":
            deployment = owner.name

    # Fetch container logs (prefer previous container)
    logs = None

    try:
        logs = v1.read_namespaced_pod_log(
            name=pod_name,
            namespace=namespace,
            tail_lines=50,
            timestamps=True,
            previous=True
        )

        if not logs:
            logs = v1.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                tail_lines=50,
                timestamps=True
            )

    except Exception:
        logs = "unable to fetch logs"

    payload = {
        "pod": pod.metadata.name,
        "deployment": deployment,
        "container": container_name,
        "image": image,
        "namespace": namespace,
        "restart_count": restart_count,
        "last_state": last_state,
        "exit_code": exit_code,
        "termination_message": termination_message,
        "oom_killed": oom_killed,
        "liveness_probe": liveness_probe,
        "readiness_probe": readiness_probe,
        "resource_limits": str(resource_limits),
        "node": pod.spec.node_name,
        "reason": reason,
        "message": message,
        "recent_logs": logs
    }

    return payload


def watch_events(callback):
    """
    Watch Kubernetes events and trigger callback
    """

    print("Starting Kubernetes event stream...")

    config.load_incluster_config()

    v1 = client.CoreV1Api()
    w = watch.Watch()

    for event in w.stream(v1.list_namespaced_event, namespace="ai-sre"):

        obj = event["object"]

        reason = obj.reason
        message = obj.message
        namespace = obj.metadata.namespace

        if reason in ["BackOff", "CrashLoopBackOff", "FailedScheduling"]:

            pod_name = obj.involved_object.name

            # Avoid analyzing the assistant itself
            if pod_name.startswith("ai-sre-assistant"):
                continue

            print(
                f"Event received: pod={pod_name} "
                f"namespace={namespace} reason={reason}"
            )

            payload = build_payload(v1, namespace, pod_name, reason, message)

            if payload is None:
                continue

            callback(payload)
