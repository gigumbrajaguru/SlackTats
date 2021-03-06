import datetime
import re
from slackclient import SlackClient
import pymongo
import os
from git import Repo
import UserManager
from ProjectAnalyzer import SlackCommunication
from ProjectAnalyzer import Task
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



def projectmongoupdate(channels,key,point,updates,dicts):
    records = db.get_collection("project")
    if UserManager.checkUserRole(dicts.get("user")):
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
    channels = dicts.get("channel")
    msg = dicts.get("text")
    count=0
    if UserManager.checkUserRole(dicts.get("user")):
        array = msg.split(" ")
        for split in array:
            if split!=None:
                if split[0] == "-":
                    if split == "-projectid":
                        projectid = array[count + 1]
                    if split == "-projectname":
                        projectname = array[count + 1]
                        projectmongoupdate(channels, projectid, "projectname", projectname,dicts)
                    if split == "-totalslack":
                        totalslack = array[count + 1]
                        projectmongoupdate(channels, projectid, "totalslack", totalslack,dicts)
                    if split == "-startdate":
                        startdate = array[count + 1]
                        projectmongoupdate(channels, projectid, "startdate", startdate,dicts)
                    if split == "-enddate":
                        enddate = array[count + 1]
                        projectmongoupdate(channels, projectid, "enddate", enddate,dicts)
                    if split == "-managerid":
                        managerid = array[count + 1]
                        projectmongoupdate(channels, projectid, "managerid", managerid,dicts)
                    if split == "-githublink":
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
        paths="../Projects/rep"
        if UserManager.checkUserRole(managerid):
            try:
                gitlink = documents.find({"managerid": managerid}).distinct("githublink")[0]
                if gitlink != None:
                    if gitlink.split("//")[0] == "https:":
                        if os.path.exists(paths):
                            repo = Repo(paths)
                            repo.remotes.origin.pull()
                        else:
                            Repo.clone_from(gitlink, paths)
                        repo = Repo(paths)
                        if not repo.bare:
                            commits = list(repo.iter_commits('master'))[:10000]
                            for commit in commits:
                                checkcommit(channels, commit, repo)
                                pass
                        else:
                            text = 'Repo description: Server problem'
                            SlackCommunication.postMessege(channels, text)
                else:
                    text = 'Link Github repository.'
                    SlackCommunication.postMessege(channels, text)
            except:
                text = 'Complete github link registration first'
                SlackCommunication.postMessege(channels, text)


def checkcommit(channels,commit,repo):
    count,istest=0,0
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
            if word !=None:
                if word == "projectid":
                    projectid = commitarray[count + 1]
                if word == "taskid":
                    taskid = commitarray[count + 1]
                if word == "taskname":
                    taskname = commitarray[count + 1]
            count = count + 1
        if projectid != [] and projectid != None:
            checkedcommits = projectdocuments.find({"projectid": projectid}).distinct("checkedcommits")
            for checkedcommit in checkedcommits:
                if str(commit.hexsha) == checkedcommit:
                    check = 1
                    break

        if projectid != None and taskid != None and taskname != None:
            taskcontentarray = documents.find({"taskname": taskname, "taskid": taskid, "projectid": projectid}).distinct("taskcontent")
            if taskcontentarray!=[] and taskcontentarray!=None:
                taskcontentarray=taskcontentarray[0].split("#")

        else:
            text = "Skip one commit message : Not according to structure"
            SlackCommunication.postMessege(channels, text)
        if check == 0:

            commitscontent = None
            completedsubtasks, counts = 0, 0
            count, istest = 0, 0
            if taskcontentarray != [] and taskcontentarray != None:
                for y in range(7, len(commitarray)):
                    if commitarray[y] != None and commitarray[y] != " " and commitarray[y] != "":
                        commitcontent = commitcontent + " " + commitarray[y]
                numberarray = re.findall(r'\b\d+\b', commitcontent)
                if len(numberarray)==1:
                    splt = str(numberarray[count]) + "."
                    commitscontent = commitcontent.split(splt)
                for num in range(0, len(numberarray) - 1):
                    splt = str(numberarray[count]) + "."
                    spltl = str(numberarray[count + 1]) + "."
                    contentfilter = commitcontent.split(splt)
                    commitscontent = contentfilter[1].split(spltl)
                    count = count + 1
                if commitscontent != None:
                    for rep in taskcontentarray:
                        if rep != '':
                            counts = counts + 1
                            for turns in commitscontent:
                                if turns != '':
                                    ratio = fuzz.ratio(str(turns), str(rep))
                                    if ratio > 85:
                                        completedsubtasks = completedsubtasks + 1
                                    elif TextBlob(turns).words.count('Completed') > 0 and ratio > 59:
                                        completedsubtasks = completedsubtasks + 1
                                    elif TextBlob(turns).words.count('Finished') > 0 and ratio > 59:
                                        completedsubtasks = completedsubtasks + 1

                                    if TextBlob(turns).words.count('tested') > 1 or TextBlob(
                                            turns).words.count('verified') > 1:
                                        istest = 10

                if completedsubtasks > 0 and counts > 0:
                    commitcompletion = ((completedsubtasks / counts) * 100) - 10 + istest
                    documents.find_one_and_update({"taskid": taskid}, {'$set': {"taskprogress": str(commitcompletion)}})
                    if (commitcompletion == 100):
                        documents.find_one_and_update({"taskid": taskid}, {'$set': {"status": "finished"}})
                    if (commitcompletion > 85):
                        documents.find_one_and_update({"taskid": taskid}, {'$set': {"status": "fine"}})
                    elif (commitcompletion > 50 and commitcompletion < 85):
                        documents.find_one_and_update({"taskid": taskid}, {'$set': {"status": "working"}})
                    elif (commitcompletion < 50):
                        documents.find_one_and_update({"taskid": taskid}, {'$set': {"status": "critical"}})
                text = "Checked commit message and update project progress."
                SlackCommunication.postMessege(channels, text)
        if check == 0:
            projectdocuments.update({"projectid": projectid},
                                    {'$push': {"checkedcommits": str(commit.hexsha)}})
def statusUpdater(dict):
    text=None
    projectdocuments = db.get_collection("project")
    taskdocument=db.get_collection("task")
    managerid = dict.get("user")
    channels=dict.get("channel")
    projectids = projectdocuments.find({"managerid": managerid},{"roleid":"2"}).distinct("projectid")
    if projectids != [] and  projectids!=None:
        projectids = projectids[0]
        taskdetailarray = taskdocument.find({"projectid": projectids}).distinct("taskid")
        if taskdetailarray!=[]:
            for taskids in taskdetailarray:
                tasktime = taskdocument.find({"taskid": taskids}).distinct("endtime")[0]
                taskstarttime = taskdocument.find({"taskid": taskids}).distinct("starttime")[0]
                nows =str(datetime.datetime.now().date())
                checkdate=nows.replace("-","/",2)
                currentremain=Task.periodCalculator(checkdate,tasktime)
                tasktimes=Task.periodCalculator(taskstarttime, tasktime)
                ratio=currentremain/tasktimes
                taskprogress = int(float(taskdocument.find({"taskid": taskids}).distinct("taskprogress")[0]))
                tasktype = taskdocument.find({"taskid": taskids}).distinct("type")[0]
                if (taskprogress > 90 and taskprogress<100):
                    if ratio<1 and ratio>0.5:
                        if tasktype == "critical" or tasktype == "important":
                            text = taskids + "is almost done but keep work on. " + tasktype + " task"
                    elif ratio<0.5:
                        if tasktype=="critical" or tasktype=="important":
                            text=taskids+ "is almost done but keep work on. "+tasktype+" task"
                            taskdocument.find_one_and_update({"taskid": taskids}, {'$set': {"status": "working"}})

                elif (taskprogress > 50 and taskprogress < 90):
                    if ratio < 1 and ratio > 0.5:
                        if tasktype == "critical" or tasktype == "important":
                            text = taskids + "need full attention because " + tasktype + " task"

                    elif ratio < 0.5:
                        if tasktype == "critical" or tasktype == "important":
                            text = taskids + "need full attention because " + tasktype + " task"
                            taskdocument.find_one_and_update({"taskid": taskids}, {'$set': {"status": "critical"}})
                elif (taskprogress < 50):
                    if ratio < 1 and ratio > 0.5:
                        if tasktype == "critical" or tasktype == "important":
                            text = taskids + "is almost done but keep work on. " + tasktype + " task"
                            taskdocument.find_one_and_update({"taskid": taskids}, {'$set': {"status": "working"}})
                    elif ratio < 0.5:
                        text = taskids + "is in reallly bad stage. its " + tasktype + " task"
                        taskdocument.find_one_and_update({"taskid": taskids}, {'$set': {"status": "critical"}})

                SlackCommunication.postMessege(channels,text)
