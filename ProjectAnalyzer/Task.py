from slackclient import SlackClient
import pymongo
import math
import UserManager
from ProjectAnalyzer import SlackCommunication,Project

connection=pymongo.MongoClient("mongodb://localhost:27017/")
db=connection.get_database("SlackTats")
slack_token = "xoxb-402757429986-412087740598-8bGVF1HoEKEdfQws9aNDTeUM"
sc = SlackClient(slack_token)
datadictinary={}
arrays=[]
count,start=0,0

def taskmongoupdate(channels,key,point,updates):
    record=None
    records = db.get_collection("task")
    record = records.find_one_and_update({"taskid": key}, {'$set': {point: updates}})
    if record!=None:
        text = "Data Updated"
        SlackCommunication.postMessege(channels, text)

def checkAlltaskdetails(dicts):
    taskids,taskname,strtdate,enddate,totalslack,type,status,enddepends,strtsdepends=None,None,None,None,None,None,None,None,None
    documents = db.get_collection("task")
    channels = dicts.get("channel")
    manager=dicts.get("user")
    msg = dicts.get("text")
    if UserManager.checkUserRole(manager):
        count=0
        array = msg.split(" ")
        for split in array:
            if split!=None:
                if split[0] == "-":
                    if split == "-projectid":
                        projectid = array[count + 1]
                        taskids = documents.find({"projectid": projectid}).distinct("taskid")

            count=count+1
        for taskid in taskids:
            taskname = documents.find({"taskid": taskid}).distinct("taskname")[0]
            strtdate = documents.find({"taskid": taskid}).distinct("starttime")[0]
            enddate = documents.find({"taskid": taskid}).distinct("endtime")[0]
            totalslack = documents.find({"taskid": taskid}).distinct("freeslack")[0]
            progress=documents.find({"taskid": taskid}).distinct("taskprogress")[0]
            type = documents.find({"taskid": taskid}).distinct("type")[0]
            status = documents.find({"taskid": taskid}).distinct("status")[0]
            enddepends = documents.find({"taskid": taskid}).distinct("enddepends")
            strtsdepends = documents.find({"taskid": taskid}).distinct("startdepends")
            if enddepends!=None and enddepends!=[] and enddepends!=[None]:
                enddepends=enddepends[0]
            else:
                enddepends="no depends"
            if strtsdepends!=None and strtsdepends!=[] and strtsdepends!=[None]:
                strtsdepends=strtsdepends[0]
            else:
                strtsdepends="no depends"
            text="\n Task name : "+taskname+" Task ID : "+taskid+"\n Start date : "+strtdate+\
                 " End date : "+enddate+" \n Task progress "+progress+" \n"+" Total Slack : "+totalslack+"\n Type : "+type+\
                 " Status : "+status+"\n  Depends : "+enddepends+" Start depends :" + strtsdepends
            SlackCommunication.postMessege(channels,text)
    else:
        text = "Only manager can perform this command"
        SlackCommunication.postMessege(channels, text)
def updatetask(dicts):
    count,depends,taskid=0,"",""
    documents = db.get_collection("task")
    channels = dicts.get("channel")
    msg = dicts.get("text")
    array = msg.split(" ")
    for split in array:
        if split != None:
            if split[0] == "-":
                if split == "-taskid":
                    taskid = array[count + 1]
                if split == "-taskname":
                    taskname = array[count + 1]
                    taskmongoupdate(channels, taskid, "taskname", taskname)
                if split == "-freeslack":
                    freeslack = array[count + 1]
                    taskmongoupdate(channels, taskid, "freeslack", freeslack)
                if split == "-startdate":
                    starttime = array[count + 1]
                    taskmongoupdate(channels, taskid, "starttime", starttime)
                if split == "-enddate":
                    endtime = array[count + 1]
                    taskmongoupdate(channels, taskid, "endtime", endtime)
                if split == "-taskcontent":
                    taskcontent = array[count + 1]
                    taskmongoupdate(channels, taskid, "taskcontent", taskcontent)
                if split == "-type":
                    if array[count + 1] == "important" or array[count + 1] == "normal" or array[count + 1] == "critical":
                        type = array[count + 1]
                        taskmongoupdate(channels, taskid, "type", type)
                if split == "-removedepend":
                    if taskid!=None and taskid!="":
                        removedepnd = array[count + 2]
                        dependtype = array[count + 1]
                        if dependtype == "-startdepend":
                            depends = documents.find({"taskid": taskid}).distinct("startdepends")[0]
                            type = "startdepends"
                        elif dependtype == "-enddepend":
                            depends = documents.find({"taskid": taskid}).distinct("enddepends")[0]
                            type = "enddepends"
                        removearray = removedepnd.split(",")
                        arraydepends = depends.split(",")
                        for removes in removearray:
                            for check in arraydepends:
                                arraydepends.remove(removes)
                        arraylist = ",".join(arraydepends)
                        taskmongoupdate(channels, taskid, type, arraylist)
                if split == "-addepend":
                    if taskid != None and taskid != "":
                        dependslist = ""
                        adddepends = array[count + 2]
                        dependtype = array[count + 1]
                        if dependtype == "-startdepend":
                            dependslist = documents.find({"taskid": taskid}).distinct("startdepends")[0]
                            type = "startdepends"
                        elif dependtype == "-enddepend":
                            dependslist = documents.find({"taskid": taskid}).distinct("enddepends")[0]
                            type = "enddepends"
                        if dependslist == None:
                            dependslist = ""
                            arraydepends = adddepends
                        elif adddepends == None:
                            adddepends = ""
                            arraydepends = dependslist
                        else:
                            arraydepends = dependslist + "," + adddepends
                        taskmongoupdate(channels, taskid, type, arraydepends)
        count = count + 1


def checkTaskdetails(dicts):
    taskid,text,progress,taskname,strtdate,enddate,totalslack,type,status,enddepends,strtsdepends=None,None,None,None,None,None,None,None,None,None,None
    documents = db.get_collection("task")
    channels = dicts.get("channel")
    manager=dicts.get("user")
    msg = dicts.get("text")
    if UserManager.checkUserRole(manager):
        count=0
        array = msg.split(" ")
        for split in array:
            if split!=None:
                if split[0] == "-":
                    if split == "-taskid":
                        taskid = array[count + 1]
                        taskname = documents.find({"taskid": taskid}).distinct("taskname")[0]
                        strtdate = documents.find({"taskid": taskid}).distinct("starttime")[0]
                        enddate = documents.find({"taskid": taskid}).distinct("endtime")[0]
                        totalslack = documents.find({"taskid": taskid}).distinct("freeslack")[0]
                        progress = documents.find({"taskid": taskid}).distinct("taskprogress")[0]
                        type = documents.find({"taskid": taskid}).distinct("type")[0]
                        status = documents.find({"taskid": taskid}).distinct("status")[0]
                        enddepends = documents.find({"taskid": taskid}).distinct("enddepends")
                        strtsdepends = documents.find({"taskid": taskid}).distinct("startdepends")

            count=count+1
            if enddepends!=None and enddepends!=[] and enddepends!=[None]:
                enddepends=enddepends[0]
            else:
                enddepends="No depends"

            if strtsdepends!=None and strtsdepends!=[] and strtsdepends!=[None]:
                strtsdepends=strtsdepends[0]
            else:
                strtsdepends="No depends"
            if taskid!=None:
                text="\n Task name : "+taskname+" Task ID : "+taskid+"\n Start date : "+strtdate+\
                     " End date : "+enddate+" \n Task progress "+progress+" \n"+" Total Slack : "+totalslack+"\n Type : "+type+\
                     " Status : "+status
        SlackCommunication.postMessege(channels,text)
    else:
        text = "Only manager can perform this command"
        SlackCommunication.postMessege(channels, text)


def statusUpdate(key,update):
    records = db.get_collection("task")
    if records.find_one_and_update({"taskid": key}, {'$set': {"status": update}}):
        return True
    else:
        return False

def taskstatus(taskid):
    documents = db.get_collection("task")
    try:
        status = documents.find({"taskid": taskid}).distinct("status")[0]
        return status
    except:
        return "Wrong task id"

def rightTask(taskid):
    records = db.get_collection("task")
    if records.find({"taskid": taskid}).distinct("taskid"):
        return True
    else:
        return False

def taskforecast(taskid,startdate,days,channels):
    try:
        global start
        start=0
        arrays.clear()
        holdendyr, holdendmonth, holdenddate,remaindays=0,0,0,0
        documents = db.get_collection("task")
        taskfree = int(documents.find({"taskid": taskid}).distinct("freeslack")[0])
        starttime = documents.find({"taskid": taskid}).distinct("starttime")[0]
        endtime = documents.find({"taskid": taskid}).distinct("endtime")[0]
        if (days > taskfree):
            remaindays = days - taskfree

        holdtarttime = startdate.split("/")
        holdstrtyr = int(holdtarttime[0])
        holdstrtmon = int(holdtarttime[1])
        holdstrtdt = int(holdtarttime[2])

        taskstarttime = starttime.split("/")
        taskstrtyr = int(taskstarttime[0])
        taskstrtmon = int(taskstarttime[1])
        taskstrtdt = int(taskstarttime[2])

        taskendtime = endtime.split("/")
        taskendyr = int(taskendtime[0])
        taskendmon = int(taskendtime[1])
        taskenddt = int(taskendtime[2])
        holdendyr = holdstrtyr
        holdendmonth = holdstrtmon
        holdenddate = holdstrtdt
        if (holdstrtdt + days) > 30 and days < 30:
            holdenddate = days - (30 - holdstrtdt)
            if ((holdstrtmon + 1) < 12):
                holdendmonth = holdstrtmon + 1
            else:
                holdendyr = holdstrtyr + 1
                holdendmonth = 1
        elif (holdstrtdt + days) < 30:
            holdenddate = holdstrtdt + days
        elif (holdstrtdt + days) > 30 and days > 30:
            months = math.floor(days / 30)
            xdays = days - months * 30
            if months > 12:
                years = math.floor(months / 12)
                xmonths = months - years * 12
                holdendyr = holdstrtyr + years
                holdendmonth = holdstrtmon + xmonths
                holdenddate = holdstrtdt + xdays
                if holdendmonth > 12:
                    holdendyr = holdendyr + 1
                    holdendmonth = xmonths - (12 - holdstrtmon)
                if holdenddate > 30:
                    holdendmonth = holdendmonth + 1
                    holdenddate = xdays - (30 - holdstrtdt)

        blockedTasks(taskid, holdstrtyr, holdstrtmon, holdstrtdt, holdendyr, holdendmonth, holdenddate, taskstrtyr,
                     taskstrtmon, taskstrtdt, taskendyr, taskendmon, taskenddt, channels, days, remaindays)

    except:
        text = "System crashed."
        SlackCommunication.postMessege(channels, text)

def blockedTasks(taskid,holdstrtyr,holdstrtmon,holdstrtdt,holdendyr,holdendmonth,holdenddate,taskstrtyr,taskstrtmon,
                 taskstrtdt,taskendyr,taskendmon,taskenddt,channels,days,remaindays):
    #############################################################################
    if taskstrtyr == holdstrtyr and taskstrtmon==holdstrtmon and taskstrtdt==holdstrtdt:
        startdependtask(channels,taskid,remaindays)
    elif taskendyr==holdendyr and taskendmon==holdendmonth and taskenddt==holdenddate:
        enddependtask(channels,taskid,remaindays)
    #############################################################################
    elif taskstrtyr>holdstrtyr and taskendyr<holdendyr:
        enddependtask(channels,taskid,remaindays)
        startdependtask(channels, taskid, remaindays)
    elif taskstrtyr < holdstrtyr and taskendyr < holdendyr:
        enddependtask(channels, taskid, remaindays)
    elif taskstrtyr > holdstrtyr and taskendyr > holdendyr:
        startdependtask(channels, taskid, remaindays)
     ############################################################################
    elif taskstrtyr==holdstrtyr and taskendyr<holdendyr:
        enddependtask(channels,taskid,remaindays)
        if  taskstrtmon > holdstrtmon :
            startdependtask(channels, taskid, remaindays)
        if taskstrtmon == holdstrtmon:
            if taskstrtdt > holdstrtdt or taskstrtdt == holdstrtdt:
                startdependtask(channels,taskid,remaindays)
    elif taskstrtyr==holdstrtyr and taskendyr>holdendyr:
        if  taskstrtmon > holdstrtmon :
            startdependtask(channels, taskid, remaindays)
        if taskstrtmon == holdstrtmon:
            if taskstrtdt > holdstrtdt or taskstrtdt == holdstrtdt:
                startdependtask(channels,taskid,remaindays)
    elif taskstrtyr>holdstrtyr and taskendyr==holdendyr:
        startdependtask(channels,taskid,remaindays)
        if  taskendmon < holdendmonth :
            enddependtask(channels, taskid, remaindays)
        if taskendmon == holdendmonth:
            if taskenddt < holdenddate or taskenddt == holdenddate:
                enddependtask(channels,taskid,remaindays)
    elif taskstrtyr<holdstrtyr and taskendyr==holdendyr:
        if  taskendmon < holdendmonth :
            enddependtask(channels, taskid, remaindays)
        if taskendmon == holdendmonth:
            if taskenddt < holdenddate or taskenddt == holdenddate:
                enddependtask(channels,taskid,remaindays)
    #############################################################################
    elif taskstrtyr == holdstrtyr and taskendyr == holdendyr:
        if taskstrtmon < holdstrtmon and taskendmon < holdendmonth:
            enddependtask(channels,taskid,remaindays)
        elif taskstrtmon == holdstrtmon and taskendmon < holdendmonth:
            enddependtask(channels,taskid,remaindays)
            if taskstrtdt > holdstrtdt or taskstrtdt == holdstrtdt:
                startdependtask(channels,taskid,remaindays)
        elif taskstrtmon == holdstrtmon and taskendmon > holdendmonth:
            if taskstrtdt > holdstrtdt or taskstrtdt == holdstrtdt:
                startdependtask(channels,taskid,remaindays)

        elif taskstrtmon < holdstrtmon and taskendmon == holdendmonth:
            if taskenddt < holdenddate or taskenddt == holdenddate:
                enddependtask(channels,taskid,remaindays)
        elif taskstrtmon == holdstrtmon and taskendmon == holdendmonth:
            if taskstrtdt < holdstrtdt and taskenddt < holdenddate:
                enddependtask(channels,taskid,remaindays)
            elif taskstrtdt == holdstrtdt and taskenddt < holdenddate:
                startdependtask(channels,taskid,remaindays)
                enddependtask(channels,taskid,remaindays)
            elif taskstrtdt == holdstrtdt and taskenddt > holdenddate:
                startdependtask(channels,taskid,remaindays)
            elif taskstrtdt < holdstrtdt and taskenddt > holdenddate:
                if remaindays!=0:
                    enddependtask(channels,taskid,remaindays)
            elif taskstrtdt < holdstrtdt and taskenddt == holdenddate:
                enddependtask(channels,taskid,remaindays)
            elif taskstrtdt > holdstrtdt and taskenddt == holdenddate:
                startdependtask(channels, taskid, remaindays)
                enddependtask(channels,taskid,remaindays)
            elif taskstrtdt == holdstrtdt and taskenddt == holdenddate:
                startdependtask(channels,taskid,remaindays)
                enddependtask(channels,taskid,remaindays)
        else:
            text = "Please check your input again"
            SlackCommunication.postMessege(channels, text)
    else:
        text = "Please check your input again"
        SlackCommunication.postMessege(channels, text)


def startdependtask(channels, taskid, remaindays):
    documents = db.get_collection("task")
    taskprogress = documents.find({"taskid": taskid}).distinct("taskprogress")[0]
    taskfree = int(documents.find({"taskid": taskid}).distinct("freeslack")[0])
    starttime = documents.find({"taskid": taskid}).distinct("starttime")[0]
    endtime = documents.find({"taskid": taskid}).distinct("endtime")[0]
    type = documents.find({"taskid": taskid}).distinct("type")[0]
    status = documents.find({"taskid": taskid}).distinct("status")[0]
    endepends = documents.find({"taskid": taskid}).distinct("enddepends")
    startdepends = documents.find({"taskid": taskid}).distinct("startdepends")

    if remaindays != None and remaindays > 0:
        remaindays = remaindays - taskfree
        if endepends != None and endepends != []:
            endepends = endepends[0]
        if startdepends != None and startdepends != []:
            startdepends = startdepends[0]
        dicarray = {
            "taskids": taskid,
            "taskprogress": taskprogress,
            "type": type,
            "taskfree": taskfree,
            "starttime": starttime,
            "endtime": endtime,
            "status": status,
            "endepends": endepends,
            "startdepends": startdepends,
            "remaindays": remaindays,
        }
        arrays.append(dicarray)
        subTaskcheck(arrays,remaindays,1,channels)

    else:
        text = "Task can hold till requested days."
        SlackCommunication.postMessege(channels, text)

def subTaskcheck(arrays,remaindays,depend,channels):
    global start
    if start==0:
        for count in range(0,100):
            if count<len(arrays):
                startdependtaskid = arrays[count].get("startdepends")
                enddependtaskid = arrays[count].get("endepends")
                if startdependtaskid != None and startdependtaskid != [] and depend!=2:
                    startdependtaskid = startdependtaskid.split(",")
                    for taskid in startdependtaskid:
                        arrays.append(taskinfomation(taskid, remaindays))
                if enddependtaskid != None and enddependtaskid != []:
                    enddependtaskid = enddependtaskid.split(",")
                    for taskid in enddependtaskid:
                        arrays.append(taskinfomation(taskid, remaindays))
        for dict in arrays:
            remaindays = dict.get("remaindays")
            taskid = dict.get("taskids")
            status = dict.get("status")
            taskfree = dict.get("taskfree")
            type = dict.get("type")
            informationsender(remaindays, taskfree, taskid, channels, status, type)
    start=1

def taskinfomation(taskid, remaindays):
    documents = db.get_collection("task")
    taskprogress = documents.find({"taskid": taskid}).distinct("taskprogress")[0]
    taskfree = int(documents.find({"taskid": taskid}).distinct("freeslack")[0])
    starttime = documents.find({"taskid": taskid}).distinct("starttime")[0]
    endtime = documents.find({"taskid": taskid}).distinct("endtime")[0]
    type = documents.find({"taskid": taskid}).distinct("type")[0]
    status = documents.find({"taskid": taskid}).distinct("status")[0]
    endepends = documents.find({"taskid": taskid}).distinct("enddepends")
    startdepends = documents.find({"taskid": taskid}).distinct("startdepends")

    if remaindays != None and remaindays > 0:
        remaindays = remaindays - taskfree
        if remaindays<0:
            remaindays=0
        if endepends != None and endepends != []:
            endepends = endepends[0]
        if startdepends != None and startdepends != []:
            startdepends = startdepends[0]
        dicarray = {
            "taskids": taskid,
            "taskprogress": taskprogress,
            "type": type,
            "taskfree": taskfree,
            "starttime": starttime,
            "endtime": endtime,
            "status": status,
            "endepends": endepends,
            "startdepends": startdepends,
            "remaindays": remaindays,
        }
        return dicarray

def enddependtask(channels, taskid, remaindays):
    documents = db.get_collection("task")
    taskprogress = documents.find({"taskid": taskid}).distinct("taskprogress")[0]
    taskfree = int(documents.find({"taskid": taskid}).distinct("freeslack")[0])
    starttime = documents.find({"taskid": taskid}).distinct("starttime")[0]
    endtime = documents.find({"taskid": taskid}).distinct("endtime")[0]
    type = documents.find({"taskid": taskid}).distinct("type")[0]
    status = documents.find({"taskid": taskid}).distinct("status")[0]
    endepends = documents.find({"taskid": taskid}).distinct("enddepends")
    startdepends = documents.find({"taskid": taskid}).distinct("startdepends")

    if remaindays != None and remaindays > 0:
        remaindays = remaindays - taskfree
        if remaindays<0:
            remaindays=0
        if endepends != None and endepends != []:
            endepends = endepends[0]
        if startdepends != None and startdepends != []:
            startdepends = startdepends[0]
        dicarray = {
            "taskids": taskid,
            "taskprogress": taskprogress,
            "type": type,
            "taskfree": taskfree,
            "starttime": starttime,
            "endtime": endtime,
            "status": status,
            "endepends": endepends,
            "startdepends": startdepends,
            "remaindays": remaindays,
        }
        arrays.append(dicarray)
        subTaskcheck(arrays, remaindays,2,channels)
    else:
        text = "Task can hold till requested days."
        SlackCommunication.postMessege(channels, text)

def informationsender(remaindays,taskfree,taskid,channels,status,type):
        if remaindays > taskfree:
            if status == "critical":
                text = "task " + taskid + " is  in critical stage. So its risk to hold task for " + str(
                    remaindays) + " days."
                SlackCommunication.postMessege(channels, text)
            elif status != "fine" and status != "finished":
                text = "task " + taskid + " is in not good stage. So its risk to hold task for " + str(
                    remaindays) + " days."
                SlackCommunication.postMessege(channels, text)
                if type == "important":
                    text = "Also task " + taskid + " is important tasks "
                    SlackCommunication.postMessege(channels, text)
            else:
                text = "Task status is" + status
                SlackCommunication.postMessege(channels, text)
                if remaindays > 0:
                    text = "But holding more than free slack is risk"
                    SlackCommunication.postMessege(channels, text)
        else:
            text = "task " + taskid + " can hold " + str(remaindays) + " days."
            SlackCommunication.postMessege(channels, text)

def periodCalculator(starttimes, endtimes):
    strt = starttimes.split("/")
    end = endtimes.split("/")
    if len(end) == 3 and len(strt) == 3:
        strtyr = int(strt[0])
        strtmon = int(strt[1])
        strtdt = int(strt[2])
        endyr = int(end[0])
        endmon = int(end[1])
        endtdt = int(end[2])
        yrs = endyr - strtyr
        if endyr != strtyr:
            months = 12 - strtmon + endmon
        else:
            months = endmon - strtmon
        if strtmon != endmon:
            days = 30 - strtdt + endtdt
        else:
            days = endtdt - strtdt

        totaldays = yrs * 365 + months * 30 + days
        return totaldays

def duplicateChecker(variable,value,table):
    documents = db.get_collection(table)
    checkpoint=documents.find({variable:value}).count()
    if checkpoint==0:
        return True
    else:
        return False

def deleteTask(dict):
    user = dict.get("user")
    count=0
    taskid=None
    channel = dict.get("channel")
    msg = dict.get("text")
    array = msg.split(" ")
    for split in array:
        if split == "-taskid":
            taskid = array[count + 1]
        count = count + 1
    records = db.get_collection("task")
    if taskid != None and taskid!="" and UserManager.checkUserRole(user):
        taskdetails = {"taskid": taskid }
        check=records.delete_one(taskdetails).acknowledged
        if check:
            text =  taskid + " Task deleted."
            SlackCommunication.postMessege(channel, text)
        else:
            text = "Check input again."
            SlackCommunication.postMessege(channel, text)



