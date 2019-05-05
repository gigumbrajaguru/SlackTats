import os
from slackclient import SlackClient

slack_token = "xoxb-402757429986-412087740598-8bGVF1HoEKEdfQws9aNDTeUM"
sc = SlackClient(slack_token)


def postMessege(channels,text):
    if text!=None:
        sc.api_call(
            "chat.postMessage",
            channel=channels,
            text=text
            )

def deleteMessege(channels,ts):
    sc.api_call(
        "chat.delete",
        channel=channels,
        ts=ts
        )

def usercount():
    count=0
    request=sc.api_call("users.list")
    if request['ok']:
        for item in request['members']:
            if item["is_bot"]==False and item["is_app_user"]==False:
                count=count+1
    return count
