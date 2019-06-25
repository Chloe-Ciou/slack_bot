import time
import schedule
import requests
import pyjokes

def get_attachments(attachs):
    attach_list = []
    for attach in attachs:
        attach_list.append({
            'text': 'Take a break!',
            'image_url': attach['image_url'] if attach['image_url'] else ''
        })
    return attach_list

def get_joke():
    '''
    :return: only programming relative joke so far
    '''
    return pyjokes.get_joke()

def send_messages_regularly(web_client, text = '', type_message = '', attachs = None):
    channel_list = web_client.api_call("conversations.list")
    is_member = []
    for channel in channel_list['channels']:
        if channel['is_member'] is True:
            is_member.append(channel['id'])

    for channel in is_member:
        try:
            web_client.chat_postMessage(
                channel=channel,
                text=f"{type_message}{text}",
                attachments=get_attachments(attachs) if attachs else []
            )
        except:
            continue

def send_jobs():
    while True:
        schedule.run_pending()
        time.sleep(1)
