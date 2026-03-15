import requests
from config import SLACK_WEBHOOK


def notify(message):

    payload = {
        "text": f"""
 *AI SRE INCIDENT DETECTED*

{message}
"""
    }

    try:
        response = requests.post(SLACK_WEBHOOK, json=payload)

        if response.status_code != 200:
            print("Slack notification failed:", response.text)

    except Exception as e:
        print("Slack webhook error:", e)
