import argparse
from os import environ as env
from slackclient import SlackClient

SLACK_TOKEN = 'SLACK_TOKEN' in env and env['SLACK_TOKEN']
SLACK_CHANNEL = 'SLACK_CHANNEL' in env and env['SLACK_CHANNEL']
SLACK_USERNAME = 'SLACK_USERNAME' in env and env['SLACK_USERNAME']
SLACK_ICON_URL = 'SLACK_ICON_URL' in env and env['SLACK_ICON_URL']

def send_text(text):
    slack_client = SlackClient(SLACK_TOKEN)
    message = slack_client.api_call('chat.postMessage', **{
        'text': text,
        'channel': SLACK_CHANNEL,
        'username': SLACK_USERNAME,
        'icon_url': SLACK_ICON_URL
    })
    print(message)

def error(param):
    print('You need to set parameter {}.'.format(param))
    print ('You can use the argument or set the environment variable.')
    print ('See help: slack-cli -h')
    exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', help='\
        Slack token. Use this or set environment variable SLACK_TOKEN.')
    parser.add_argument('-c', '--channel', help='\
        Slack channel. Use this or set environment variable SLACK_CHANNEL.')
    parser.add_argument('-u', '--username', help='\
        Sender name. Use this or set environment variable SLACK_USERNAME.\
        Default: Slack CLI.')
    parser.add_argument('-i', '--icon', help='\
        Sender icon url. Use this or set environment variable SLACK_ICON_URL.\
        Default: Slack default.')
    parser.add_argument('text', help='Text to be sent')
    args = parser.parse_args()
    
    '''
    params priority: 
    1. argument
    2. environment variable
    '''
    SLACK_TOKEN = args.token or SLACK_TOKEN
    SLACK_CHANNEL = args.channel or SLACK_CHANNEL
    SLACK_USERNAME = args.username or SLACK_USERNAME or 'Slack CLI'
    SLACK_ICON_URL = args.icon or SLACK_ICON_URL or None
    if not SLACK_TOKEN:
        error('TOKEN')
    if not SLACK_CHANNEL:
        error('CHANNEL')
    send_text(args.text.decode('string-escape'))

if __name__ == '__main__':
    main()

