**AI SRE Assistant**

AI SRE Assistant is an experimental AI Driven Kubernetes incident analysis system that observes cluster failures in real time, collects operational signals, and produces automated root cause diagnostics using a Large Language Model.

The system behaves like a junior SRE assistant that continuously monitors Kubernetes events and performs triage when incidents occur.

**Why This Project Exists**

SRE teams spend a significant amount of time triaging repetitive incidents such as:

CrashLoopBackOff containers

OOMKilled workloads

Failed scheduling events

Misconfigured resource limits

Application startup failures

The goal of this project is to explore whether AI can assist in early incident diagnosis by automatically analyzing operational telemetry.

Instead of manually investigating logs, events, and container state, the assistant gathers evidence and generates an initial diagnosis.

**What This System Does**

When a failure happens in Kubernetes:

1. The assistant detects the event

2. It gathers runtime evidence

3. It sends structured incident context to an LLM

4. The model produces root cause analysis

5. The result is sent to Slack

This reduces the time required to perform initial incident triage.

**System Architecture**

                 Kubernetes Cluster
                         │
                         │
               Kubernetes Events API
                         │
                         ▼
                  Event Watcher
                    (watcher.py)
                         │
                         │ enrich payload
                         ▼
                   Evidence Collector
                    (collector.py)
                         │
                         │ structured incident data
                         ▼
                  AI Analyzer
                   (analyzer.py)
                         │
                         │ AWS Bedrock LLM
                         ▼
                  Root Cause Analysis
                         │
                         ▼
                   Notification
                   (notifier.py)
                         │
                         ▼
                      Slack

**Event Processing Flow**

    Pod Crash
        │
        ▼
    Kubernetes Event
        │
        ▼
    watcher.py detects BackOff / CrashLoopBackOff
        │
        ▼
    collector.py gathers runtime evidence
        │
        ▼
    analyzer.py sends incident payload to LLM
        │
        ▼
    LLM produces diagnosis
        │
        ▼
    notifier.py sends alert to Slack




## Repository Structure

```
ai-sre-assistant
│
├── src
│   ├── main.py
│   ├── watcher.py
│   ├── collector.py
│   ├── analyzer.py
│   ├── notifier.py
│   ├── cooldown.py
│   ├── config.py
│   └── prompts
│       └── sre_prompt.txt
│
├── deployment.yaml
├── Dockerfile
├── requirements.txt
└── README.md
```

**Component Breakdown**
**main.py**

Application entry point.

Responsibilities:

1. Start Kubernetes event watcher

2. Handle incident lifecycle

3. Coordinate collector → analyzer → notifier pipeline

Flow:

watch_events()
     ↓
collect()
     ↓
analyze()
     ↓
notify()

**watcher.py**

Continuously watches Kubernetes events.

Key responsibilities:

1.Subscribe to cluster events

2.Detect failure signals

3.Enrich incident payload with runtime metadata

Signals collected:

container name
container image
restart count
exit code
termination reason
OOMKilled
resource limits
liveness/readiness probes
container logs


**collector.py**

Collects additional context from the cluster.

Responsibilities:

1.Fetch pod metadata

2.Resolve service name

3.Extract container configuration

4.Parse resource requests and limits

Service resolution logic:

1. app label
2. run label
3. Deployment owner
4. fallback → unknown

**analyzer.py**

Responsible for AI diagnosis.

The analyzer sends structured incident data to AWS Bedrock.

Model used:
google.gemma-3-4b-it

The prompt asks the model to generate:

Root cause

Evidence

Immediate remediation

Long-term fix

Confidence score

**notifier.py**

Handles incident notifications.

Currently supports: Slack Incoming Webhooks

**cooldown.py**

Prevents alert storms.

CrashLoopBackOff generates many repeated events.

Cooldown logic ensures:same service not analyzed repeatedly

**Incident Evidence Collected**

Each incident payload includes operational signals such as:

pod
container_name
container_image
image_tag
restart_count
exit_code
termination_reason
OOMKilled
resource_limits
resource_requests
liveness_probe
readiness_probe
termination_message
recent_logs

**Real Failure Scenarios Tested**
*CrashLoopBackOff*

Deployment intentionally exits with code 1.

*OOMKilled*

Container memory usage exceeds configured limit.

*Failed Scheduling*

Pod requests impossible resources.

The assistant was tested with several real-world failure modes.

**Future Improvements**

Several enhancements can make the system more production-ready.

**Prometheus Metrics Integration**

Add metrics context:
container_cpu_usage
container_memory_usage
node_memory_pressure
restart_rate

**Multi-Cluster Support**

Extend the assistant to monitor multiple clusters.

**Auto Remediation**

Enable AI to trigger corrective actions:
kubectl rollout restart
kubectl scale deployment

**Project Goal**

This project explores the intersection of AI and Site Reliability Engineering.

It demonstrates how LLMs can assist with:

1.incident triage

2.root cause analysis

3.operational diagnostics

The assistant does not replace SREs but acts as a decision-support system that accelerates troubleshooting.


**Author**

Pankaj Aswal
DevOps / Site Reliability Engineer
