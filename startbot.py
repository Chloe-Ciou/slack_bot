import re
import os
from time import sleep
import random
import slack
import schedule
from threading import Thread
from shared.constants import messages, photo_Type
from shared.datasources import get_photo_unsplash
from feature.feature import send_jobs, send_messages_regularly, get_joke

from rbc_security import enable_certs
# logging.basicConfig(level=logging.DEBUG)


slack_token = os.environ['SLACK_BOT_TOKEN']
proxy = os.environ['HTTP_PROXY']
starterbot_id = None

# constants
EXAMPLE_COMMAND = "do"
CHANNEL = "slack-bot"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM


def parse_commands(client):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    user_id = None
    message = ''
    for event in client:
        if event == "text" and "subtype" not in client:
            user_id, message = parse_mention(client["text"])
    return user_id, message.lower().strip()


def parse_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned.
    """
    matches = re.search(MENTION_REGEX, message_text)
    if matches:
        return matches.group(1), matches.group(2).strip()
    elif 'late' in message_text:
        return None, 'fired'
    elif 'Thank you' in message_text or 'Thanks' in message_text:
        return None, 'thank_you'
    else:
        return None, ''

def handle_command(message, payload, mentioned):
    """
        Executes bot command if the command is known
    """
    data = payload['data']
    web_client = payload['web_client']
    rtm_client = payload['rtm_client']

    # Finds and executes the given command, filling in response
    response = None

    if mentioned:
        if message.startswith('hi'):
            response = f"Hello <@{data['user']}>! How can I help you?"
        elif message.startswith(EXAMPLE_COMMAND):
            message = (message.replace('do', '', 1)).strip()
            # do with a task
            if message == 'checkin':
                response = f"checkin"
            # do without a task
            else:
                response = f"Sure...please write the task then I can do that!"

        # mentioned without unknown message
        else:
            response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    else:
        # handle specific cases
        if message == 'fired' or message == 'thank_you':
            response = f"<@{data['user']}> {messages[message]}"

    if response:
        # Sends the response back to the channel
        web_client.chat_postMessage(
            channel=data['channel'],
            text=response,
            thread_ts=data['ts'] if mentioned else ''
        )


@slack.RTMClient.run_on(event='hello')
def say_hello(**payload):
    """
       Bot is connected and started running!
    """
    global starterbot_id
    web_client = payload['web_client']
    starterbot_id = web_client.api_call("auth.test")["user_id"]

    """
        Schedule bot jobs 
    """
    schedule.every().day.at("10:00").do(send_messages_regularly, web_client, get_joke(), 'Time For a Joke!  >>>>>  \n')
    schedule.every().day.at("16:00").do(send_messages_regularly, web_client, get_joke(), 'Time For a Joke!  >>>>>  \n')
    # schedule.every().day.at("08:55").do(send_messages_regularly, web_client, '', '',[{'image_url': get_photo_unsplash('travel')}])
    thread = Thread(target=send_jobs)
    thread.start()


@slack.RTMClient.run_on(event='message')
def response_message(**payload):
    user_id, message = parse_commands(payload['data'])

    if message is not '':
        handle_command(message, payload, True if user_id else False)
        sleep(RTM_READ_DELAY)


if __name__ == "__main__":
    # Make the client trust RBC's certificates
    enable_certs()
    rtm_client = slack.RTMClient(token=slack_token, proxy=proxy)
    rtm_client.start()

