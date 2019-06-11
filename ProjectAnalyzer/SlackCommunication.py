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
