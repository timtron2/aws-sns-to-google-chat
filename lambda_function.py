import json
import logging
import os
import urllib3
from http.client import responses


"""
Set GOOGLE_WEBHOOK_URL in lambda envinroment:
"""



google_chat_url = os.environ['GOOGLE_WEBHOOK_URL']
http = urllib3.PoolManager()


def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))

    try:
        text = get_text(get_message_from_event(event))
        send_to_chat(text, google_chat_url)
        logging.warning(f'message body: {event}')
        return {
            'statusCode': 200,
            'body': str(text)
        }

    except Exception as e:
        logging.error(f'Exception:{e}. Message{event}')
        return {
            'statusCode': 500,
            'body': 'Send ERROR to chat - ' + str(send_to_chat(f'Something went wrong with sns-to-googlechat:\n```{e}\n{event}```', google_chat_url))
        }


def get_message_from_event(event: dict) -> dict:
    return json.loads(event.get('Records')[0].get('Sns').get('Message'))


def get_text(message: dict) -> str:
    alarm_name = message['AlarmName'] if 'AlarmName' in message.keys() else ''
    old_state = message['OldStateValue'] if 'OldStateValue' in message.keys() else ''
    new_state = message['NewStateValue'] if 'NewStateValue' in message.keys() else ''
    new_state_reason = message['NewStateReason'] if 'NewStateReason' in message.keys() else ''

    return f'*{alarm_name}:* {old_state} ⟶ {new_state}\n```{new_state_reason}```'


def send_to_chat(text: str, webhook_url: str):
    message = {'text': text}
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    response = http.request('POST', url=webhook_url, headers=headers, body=json.dumps(message))

    if response.status != 200:
        return False

    return True
