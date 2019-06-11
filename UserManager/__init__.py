import re
from ProjectAnalyzer import checkUserRole
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
                try:
                    email = email.split("|")[1]
                    email = email[:-1]
                except:
                    email=""
                    text = "Please check email domain"
                    SlackCommunication.postMessege(channel, text)
            if z == "-fullname":
                fullname = array[count + 1]
        count = count + 1
    records = db.get_collection("user")
    if user!=None and fullname!=None and email!=None and location!= None :
        if rightEmail(email):
            if Task.duplicateChecker("userid",user,"user"):
                mydict = {"userid":user,"fullname": fullname, "email": email, "location": location}
                ischecked = records.insert_one(mydict).acknowledged
                if ischecked:
                    text = "<@" + user + "> registered to system."
                    SlackCommunication.postMessege(channel, text)
                else:
                    text = "Registration failed."
                    SlackCommunication.postMessege(channel, text)
            else:
                text = "Alreqady registered."
                SlackCommunication.postMessege(channel, text)
        else:
            text = "Please check email again."
            SlackCommunication.postMessege(channel, text)
    else:
        text = "You should set input parameters with values."
        SlackCommunication.postMessege(channel, text)

def rightEmail(email):
    checkemaillevelone=email.split("@")
    if (len(checkemaillevelone)==2):
        checkemailleveltwo=checkemaillevelone[1].split(".")
        if(len(checkemailleveltwo)==2):
            if (bool(re.search('[a-zA-Z]',checkemaillevelone[0])) and bool(re.search('[a-zA-Z]',checkemailleveltwo[0]))  and bool(re.search('[a-zA-Z]',checkemailleveltwo[1]))):
                return True
            else:
                return False
        else:
            return False
    else:
        return False

def workassigner(dict):
    id,userid=None,None
    count=0
    taskids=""
    taskvalidate,isvalidate=False,True
    user = dict.get("user")
    records = db.get_collection("user")
    channel = dict.get("channel")
    msg = dict.get("text")
    array = msg.split(" ")
    for z in array:
        if z == "-userid":
            userid = array[count + 1]
        if z == "-tasksid":
            for countnumber in range(count + 1, len(array)):
                taskids = taskids + " " + str(array[countnumber])
        count = count + 1

    if taskids!="":
        checktaskid = taskids.split(" ")
        for checks in checktaskid:
            if checks!="" and checks!=" " and checks!=None:
                isvalidtask = Task.rightTask(checks)
                if isvalidtask==False:
                    isvalidate=False
                    break
        if isvalidate and checkUserRole(user):
            if records.find_one_and_update({"userid": userid}, {'$set': {"allocatedtasks": taskids}}):
                text = "<@" + user + "> asssigned to do " + taskids + "."
                SlackCommunication.postMessege(channel, text)
        else:
            text = "Assigning failed"
            SlackCommunication.postMessege(channel, text)




def deleteUser(dict):
    user = dict.get("user")
    count=0
    userid=None
    channel = dict.get("channel")
    msg = dict.get("text")
    array = msg.split(" ")
    for z in array:
        if z == "-userid":
            userid = array[count + 1]
        count = count + 1
    records = db.get_collection("user")
    if userid != None and userid!="" and checkUserRole(user):
        userdetail = {"userid": userid }
        check=records.delete_one(userdetail).acknowledged
        if check:
            text = "<@" + user + "> Deleted."
            SlackCommunication.postMessege(channel, text)
        else:
            text = "Check input again."
            SlackCommunication.postMessege(channel, text)