import shutil

from slackclient import SlackClient
import pymongo
import os
from git import Repo
from ProjectAnalyzer import SlackCommunication
from difflib import SequenceMatcher
from textblob import TextBlob
import nltk
from textblob.wordnet import Synset


nltk.download('wordnet')
nltk.download("punkt")
connection=pymongo.MongoClient("mongodb://localhost:27017/")
db=connection.get_database("SlackTats")
slack_token = "xoxb-402757429986-412087740598-8bGVF1HoEKEdfQws9aNDTeUM"
sc = SlackClient(slack_token)
completioncases={"completed":"completed","finished":"finished","fixed":"fixed","percentage":"percentage","removed":"removed"}

def checkUserRole(manger):
    collection=db.get_collection("user")
    documentcount=collection.count_documents({"userid":manger})
    if documentcount==1:
        if collection.count_documents({"roleid":"2"}):
            return True
        else:
            return False
    else:
        return False


def projectmongoupdate(channels,key,point,updates,dicts):
    record=None
    records = db.get_collection("project")
    if checkUserRole(dicts.get("user")):
        record = records.find_one_and_update({"projectid": key}, {'$set': {point: updates}})
        if record!=None:
            text = "Data Updated"
            channel = channels
            SlackCommunication.postMessege(channel, text)
        else:
            text = "Data Updates fail"
            channel = channels
            SlackCommunication.postMessege(channel, text)
    else:
        text = "You don't have permission"
        channel = channels
        SlackCommunication.postMessege(channel, text)


def updateproject(dicts):
    documents = db.get_collection("project")
    channels = dicts.get("channel")
    msg = dicts.get("text")
    count=0
    if checkUserRole(dicts.get("user")):
        array = msg.split(" ")
        for z in array:
            if z[0] == "-":
                if z == "-projectid":
                    projectid = array[count + 1]
                if z == "-projectname":
                    projectname = array[count + 1]
                    projectmongoupdate(channels, projectid, "projectname", projectname,dicts)
                if z == "-projectid":
                    projectid = array[count + 1]
                    projectmongoupdate(channels, projectid, "projectid", projectid,dicts)
                if z == "-totalslack":
                    totalslack = array[count + 1]
                    projectmongoupdate(channels, projectid, "totalslack", totalslack,dicts)
                if z == "-startdate":
                    startdate = array[count + 1]
                    projectmongoupdate(channels, projectid, "startdate", startdate,dicts)
                if z == "-enddate":
                    enddate = array[count + 1]
                    projectmongoupdate(channels, projectid, "enddate", enddate,dicts)
                if z == "-managerid":
                    managerid = array[count + 1]
                    projectmongoupdate(channels, projectid, "managerid", managerid,dicts)
                if z == "-githublink":
                    githublink = array[count + 1]
                    projectmongoupdate(channels, projectid, "githublink", githublink,dicts)

            count = count + 1
        text = "System updated!"
        SlackCommunication.postMessege(channels, text)


    else:
        text = "Only managers can perform this"
        SlackCommunication.postMessege(channels, text)

def connectGithub(channels,managerid):

        documents = db.get_collection("project")
        gitlink=documents.find({"managerid": managerid}).distinct("githublink")[0]
        if gitlink != None:
            if gitlink.split("//")[0]=="https:":
                if os.path.exists("../Projects/rep"):
                    shutil.rmtree("../Projects/rep")
                Repo.clone_from(gitlink,"../Projects/rep")
                repo = Repo("../Projects/rep")
                if not repo.bare:
                    commits = list(repo.iter_commits('master'))[:10000]
                    for commit in commits:
                        checkcommit(channels,commit,repo)
                        pass
                else:
                    text = 'Repo description: Server problem'
                    SlackCommunication.postMessege(channels, text)



def printrepo(channels,repo):
    text = 'Repo description: {}'.format(repo.description)
    print(text)
    #SlackCommunication.postMessege(channels, text)

    text = 'Repo active branch is {}'.format(repo.active_branch)
    print(text)
   # SlackCommunication.postMessege(channels, text)
    for remote in repo.remotes:
        text = 'Remote named "{}" with URL "{}"'.format(remote, remote.url)
        print(text)
      #  SlackCommunication.postMessege(channels, text)

    text = 'Last commit for repo is {}.'.format(str(repo.head.commit.hexsha))
    print(text)
    #SlackCommunication.postMessege(channels, text)



def checkcommit(channels,commit,repo):
    count,istest=0,0
    commitstatus=0
    commitcontent=""
    projectid,taskid,taskname=None,None,None
    taskcontentarray,checkedcommits=None,None
    commitarray = commit.message
    commitarray = TextBlob(commitarray)
    commitarray = commitarray.words
    documents = db.get_collection("task")
    if len(commitarray) > 3:
        for word in commitarray:
            if word == "projectid":
                projectid = commitarray[count + 1]
            if word == "taskid":
                taskid = commitarray[count + 1]
            if word == "taskname":
                taskname = commitarray[count + 1]
            count = count + 1
    if projectid != None and taskid != None and taskname != None:
        taskcontentarray = \
        documents.find({"taskname": taskname, "taskid": taskid, "projectid": projectid}).distinct("taskobjectives")[
            0].split(" #")
        checkedcommits = documents.find({"projectid": projectid}).distinct("checkedcommits")
    else:
        text = "Skip one commit message : Not according to structure"
    if checkedcommits != [] and checkedcommits != None:
        for checkedcommit in checkedcommits:
            if str(commit.hexsha) == checkedcommit:
                commitstatus = 1
                break
    else:
        if commitstatus == 0:
            if taskcontentarray != [] and taskcontentarray != None:
                maxneeds = len(taskcontentarray)
                for y in range(7, len(commitarray)):
                    if commitarray[y] != None and commitarray[y] != " " and commitarray[y] != "":
                        commitcontent = commitcontent+" "+commitarray[y]
                commitcontentarray=commitcontent.split("#")
                print(commitcontent)
            #   for x in range(0, len(taskcontentarray)):
            # if taskcontentarray[x] != None and taskcontentarray[x] != " " and taskcontentarray[x] != "":
            # ratio = SequenceMatcher(None, correcteddataline, correctedcommitline).ratio()
            # comparisonphaseone = Synset(correcteddataline)
            # comparisonphasetwo = Synset(correctedcommitline)
            # rationtwo = comparisonphasetwo.path_similarity(comparisonphaseone)

            # if commitarray[x].words.count('completed') > 1 or commitarray[x].words.count('finished') > 1:
            #      if rationtwo > 0.7 and ratio > 0.7:
            #          completedsubtasks = completedsubtasks + 1
            #  if commitarray[x].words.count('tested') > 1 or commitarray[x].words.count('verified') > 1:
            #      if rationtwo > 0.7 and ratio > 0.7:
            #          istest = 10
            # commitcompletion = ((completedsubtasks / maxneeds) * 100) - 10 + istest
            # documents.find_one_and_update({"taskid": taskid}, {'$set': {"taskprogress": commitcompletion}})
            #  checkedcommits.append(str(commit.hexsha))
            # projectdocuments = db.get_collection("project")
            #  projectdocuments.find_one_and_update({"projectid": commitarray[2]},
            #                 {'$set': {"checkedcommits": checkedcommits}})

