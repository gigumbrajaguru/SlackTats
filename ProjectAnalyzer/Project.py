import re
import shutil

from slackclient import SlackClient
import pymongo
import os
from git import Repo
from ProjectAnalyzer import SlackCommunication
from textblob import TextBlob
from fuzzywuzzy import fuzz
import nltk


nltk.download('wordnet')
nltk.download("punkt")
connection=pymongo.MongoClient("mongodb://localhost:27017/")
db=connection.get_database("SlackTats")
slack_token = "xoxb-402757429986-412087740598-8bGVF1HoEKEdfQws9aNDTeUM"
sc = SlackClient(slack_token)
completioncases={"completed":"completed","finished":"finished","fixed":"fixed","percentage":"percentage","removed":"removed"}
repo=None
globalprojectid=None

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



def printrepo(dicts):
    managerid=dicts.get("user")
    channels = dicts.get("channel")
    documents = db.get_collection("project")
    gitlink = documents.find({"managerid": managerid}).distinct("githublink")[0]
    if gitlink != None:
        if gitlink.split("//")[0] == "https:":
            if os.path.exists("../Projects/rep"):
                shutil.rmtree("../Projects/rep")
            Repo.clone_from(gitlink, "../Projects/rep")
            repo = Repo("../Projects/rep")
            if not repo.bare:
                text = 'Repo description: {}'.format(repo.description)
                SlackCommunication.postMessege(channels, text)
                text = 'Repo active branch is {}'.format(repo.active_branch)
                SlackCommunication.postMessege(channels, text)
                for remote in repo.remotes:
                    text = 'Remote named "{}" with URL "{}"'.format(remote, remote.url)
                    SlackCommunication.postMessege(channels, text)
                text = 'Last commit for repo is {}.'.format(str(repo.head.commit.hexsha))
                SlackCommunication.postMessege(channels, text)



def checkcommit(channels,commit,repo):
    count,istest=0,0
    commitstatus=0
    commitcontent=""
    check=0
    projectid,taskid,taskname=None,None,None
    taskcontentarray,checkedcommits=None,None
    commitarray = commit.message
    commitarray = TextBlob(commitarray)
    commitarray = commitarray.words
    documents = db.get_collection("task")
    projectdocuments = db.get_collection("project")
    if len(commitarray) > 3:
        for word in commitarray:
            if word == "projectid":
                projectid = commitarray[count + 1]
                if projectid!=None:
                    globalprojectid=projectid
            if word == "taskid":
                taskid = commitarray[count + 1]
            if word == "taskname":
                taskname = commitarray[count + 1]
            count = count + 1
        if globalprojectid != [] and globalprojectid != None:
            checkedcommits = projectdocuments.find({"projectid": globalprojectid}).distinct("checkedcommits")
            for checkedcommit in checkedcommits:
                if str(commit.hexsha) == checkedcommit:
                    check = 1
                    break
            if check==0:
                projectdocuments.update({"projectid": globalprojectid},
                                        {'$push': {"checkedcommits": str(commit.hexsha)}})



        if projectid != None and taskid != None and taskname != None:
            taskcontentarray = \
            documents.find({"taskname": taskname, "taskid": taskid, "projectid": projectid}).distinct("taskobjectives")[
                0].split(" #")
            checkedcommits = projectdocuments.find({"projectid": projectid}).distinct("checkedcommits")

        elif globalprojectid!=None:
            text = "Skip one commit message : Not according to structure"
            SlackCommunication.postMessege(channels, text)


    if checkedcommits != [] and checkedcommits != None:
        for checkedcommit in checkedcommits:
            if str(commit.hexsha) == checkedcommit:
                commitstatus = 1
                break
    else:
        if commitstatus == 0:
            commitscontent=None
            completedsubtasks,counts=0,0
            count,istest=0,0
            if taskcontentarray != [] and taskcontentarray != None:
                for y in range(6, len(commitarray)):
                    if commitarray[y] != None and commitarray[y] != " " and commitarray[y] != "":
                        commitcontent = commitcontent+" "+commitarray[y]
                numberarray=re.findall(r'\b\d+\b',commitcontent)
                for num in range(0,len(numberarray)-1):
                    splt=str(numberarray[count])+"."
                    spltl=str(numberarray[count+1]) + "."
                    contentfilter=commitcontent.split(splt)
                    commitscontent=contentfilter[1].split(spltl)
                    count = count + 1
                if commitscontent!=None:
                    for rep in taskcontentarray:
                        if rep != '':
                            counts = counts + 1
                            for turns in commitscontent:
                                ratio = fuzz.ratio(str(turns),str(rep))
                                if ratio ==100:
                                    completedsubtasks = completedsubtasks + 1
                                elif TextBlob(turns).words.count('Completed') > 0 and ratio>59 :
                                    completedsubtasks = completedsubtasks + 1
                                elif TextBlob(turns).words.count('Finished') > 0 and ratio > 59:
                                    completedsubtasks = completedsubtasks + 1
                                if TextBlob(turns).words.count('tested')> 1 or TextBlob(
                                        turns).words.count('verified') > 1:
                                    istest = 10
                commitcompletion = ((completedsubtasks / counts) * 100) - 10 + istest
                documents.find_one_and_update({"taskid": taskid}, {'$set': {"taskprogress": commitcompletion}})





