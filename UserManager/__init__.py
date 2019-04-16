import re

from slackclient import SlackClient
import pymongo
from ProjectAnalyzer import SlackCommunication,Project,Task
connection=pymongo.MongoClient("mongodb://localhost:27017/")
db=connection.get_database("SlackTats")
slack_token = "xoxb-402757429986-412087740598-8bGVF1HoEKEdfQws9aNDTeUM"
sc = SlackClient(slack_token)

def registration(dict):
    user = dict.get("user")
    channel = dict.get("channel")
    count = 0
    location, email, fullname = None, None, None
    msg = dict.get("text")
    array = msg.split(" ")
    for z in array:
        if z[0] == "-":
            if z == "-location":
                location = array[count + 1]
            if z == "-email":
                email = array[count + 1]
            if z == "-fullname":
                fullname = array[count + 1]
        count = count + 1
    records = db.get_collection("user")
    if(user!=None and fullname!=None and email!=None and location!= None):
        if rightEmail(email):
            mydict = {"userid":user,"fullname": fullname, "email": email, "location": location}
            id = records.insert_one(mydict)
            if id != None:
                text = "<@" + user + "> registered to system."
                channel = channel
                SlackCommunication.postMessege(channel, text)
            else:
                text = "Registration failed"
                channel = channel
                SlackCommunication.postMessege(channel, text)
        else:
            text = "Please check email again"
            channel = channel
            SlackCommunication.postMessege(channel, text)

def rightEmail(email):
    email=email.split("|")[1].split(">")[0]
    checkemaillevelone=email.split("@")
    if (len(checkemaillevelone)==2):
        checkemailleveltwo=checkemaillevelone[1].split(".")
        if(len(checkemailleveltwo)==2):
            regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
            if (regex.search(checkemaillevelone[0]) == None and regex.search(checkemailleveltwo[0]) == None and regex.search(checkemailleveltwo[1])==None):
                return True
            else:
                return False
        else:
            return False
    else:
        return False
