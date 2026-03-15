import json
import boto3
import os
from config import BEDROCK_MODEL


def analyze(payload):

    region = os.getenv("AWS_REGION", "eu-west-1")
    bedrock = boto3.client("bedrock-runtime", region_name=region)

    prompt = open("prompts/sre_prompt.txt").read()
    final_prompt = prompt.replace("{incident_payload}", json.dumps(payload))

    body = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": final_prompt
            }
        ],
        "max_tokens": 500,
        "temperature": 0.2
    })

    response = bedrock.invoke_model(
        modelId=BEDROCK_MODEL,
        body=body,
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())

    return result["choices"][0]["message"]["content"]
