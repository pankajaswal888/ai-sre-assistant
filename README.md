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


**Event Processing Flow**

**Repository Structure**

**Component Breakdown**
**main.py**

Application entry point.

Responsibilities:

1. Start Kubernetes event watcher

2. Handle incident lifecycle

3. Coordinate collector → analyzer → notifier pipeline

Flow:


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


**Author**

Pankaj Aswal
DevOps / Site Reliability Engineer
