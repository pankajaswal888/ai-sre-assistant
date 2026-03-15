from watcher import watch_events
from collector import collect
from analyzer import analyze
from notifier import notify
from cooldown import is_in_cooldown, register_incident

print("AI SRE assistant starting...")


def handle_event(payload):

    namespace = payload["namespace"]
    pod = payload["pod"]
    reason = payload["reason"]
    message = payload["message"]

    print(f"Event received: pod={pod} namespace={namespace} reason={reason}")

    incident_type = "pod_failure"

    evidence = collect(namespace, pod)

    if evidence is None:
        print("Pod not found, skipping")
        return

    # Merge enriched watcher payload with collector evidence
    evidence.update(payload)

    service = evidence.get("service", "unknown")

    if is_in_cooldown(service, incident_type):
        print(f"Incident in cooldown for service={service}")
        return

    print(f"Analyzing incident for service={service}")

    try:
        diagnosis = analyze(evidence)
    except Exception as e:
        print(f"Analyzer failed: {e}")
        diagnosis = "analysis skipped"

    print("Diagnosis result:")
    print(diagnosis)

    notify(str(diagnosis))
    register_incident(service, incident_type)


if __name__ == "__main__":
    print("Watching Kubernetes events...")
    watch_events(handle_event)
