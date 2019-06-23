import re
import os
import time
import slack
from feature import feature

rtm_client = slack.RTMClient(token=os.environ["SLACK_BOT_TOKEN"])
starterbot_id = None

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
    for event in client:
        if event == "text" and not "subtype" in client:
            user_id, message = parse_mention(client["text"])
            if user_id == starterbot_id:
                return message.lower().strip()
    return None


def parse_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_command(command, payload):
    """
        Executes bot command if the command is known
    """
    data = payload['data']
    web_client = payload['web_client']
    rtm_client = payload['rtm_client']

    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None

    if command.startswith('hi'):
        response = f"Hello <@{data['user']}>! How can I help you?"

    if command.startswith(EXAMPLE_COMMAND):
        command = (command.replace('do', '', 1)).strip()
        if command == 'checkin':
            response = f"checkin"
        else:
            response = f"Sure...please write the task then I can do that!"
    if command.startswith('weather'):
        feature.get_weather()

    # Sends the response back to the channel
    web_client.chat_postMessage(
        channel=data['channel'],
        text=response,
        thread_ts=data['ts']
    )


@slack.RTMClient.run_on(event='hello')
def say_hello(**payload):
    """
       Bot is connected and started running!
    """
    global starterbot_id
    web_client = payload['web_client']
    starterbot_id = web_client.api_call("auth.test")["user_id"]

@slack.RTMClient.run_on(event='message')
def response_message(**payload):
    command = parse_commands(payload['data'])

    if command:
        handle_command(command, payload)
        time.sleep(RTM_READ_DELAY)

if __name__ == "__main__":
    rtm_client.start()
