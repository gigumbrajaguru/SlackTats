from slackclient import SlackClient
import pymongo
import math

from ProjectAnalyzer import SlackCommunication,Project

connection=pymongo.MongoClient("mongodb://localhost:27017/")
db=connection.get_database("SlackTats")
slack_token = "xoxb-402757429986-412087740598-8bGVF1HoEKEdfQws9aNDTeUM"
sc = SlackClient(slack_token)
datadictinary={}

def taskmongoupdate(channels,key,point,updates):
    record=None
    records = db.get_collection("task")
    record = records.find_one_and_update({"taskid": key}, {'$set': {point: updates}})
    if record!=None:
        text = "Data Updated"
        channel = channels
        SlackCommunication.postMessege(channel, text)

def checkAlltaskdetails(dicts):
    documents = db.get_collection("task")
    channels = dicts.get("channel")
    manager=dicts.get("user")
    msg = dicts.get("text")
    if Project.checkUserRole(manager):
        count=0
        array = msg.split(" ")
        for z in array:
            if z[0] == "-":
                if z == "-projectid":
                    projectid = array[count + 1]
                    taskname=documents.find({"projectid": projectid}).distinct("taskname")
                    taskid = documents.find({"projectid": projectid}).distinct("taskid")
                    strtdate = documents.find({"projectid": projectid}).distinct("starttime")
                    enddate = documents.find({"projectid": projectid}).distinct("endtime")
                    totalslack = documents.find({"projectid": projectid}).distinct("freeslack")
                    type=documents.find({"projectid": projectid}).distinct("type")
                    status=documents.find({"projectid": projectid}).distinct("status")
                    enddepends=documents.find({"projectid": projectid}).distinct("enddepends")
                    strtsdepends = documents.find({"projectid": projectid}).distinct("startdepends")
            count=count+1
        for x in range(len(taskid)):
            text=">Task name : "+taskname[x]+" Task ID : "+taskid[x]+" Start date : "+strtdate[x]+\
                 " End date : "+enddate[x]+" \n "+" Total Slack : "+totalslack[x]+" Type : "+type[x]+\
                 " Status : "+status[x]+"  Depends : "+enddepends[x]+" Start depends :" + strtsdepends[x]
            SlackCommunication.postMessege(channels,text)
    else:
        text = "Only manager can perform this command"
        SlackCommunication.postMessege(channels, text)
def updatetask(dicts):
    count=0
    documents = db.get_collection("task")
    channels = dicts.get("channel")
    msg = dicts.get("text")
    array = msg.split(" ")
    try:
        for z in array:
            if z[0] == "-":
                if z == "-taskid":
                    taskid = array[count + 1]
                if z == "-taskname":
                    taskname = array[count + 1]
                    taskmongoupdate(channels, taskid, "taskname", taskname)
                if z == "-projectid":
                    projectid = array[count + 1]
                    taskmongoupdate(channels, taskid, "projectid", projectid)
                if z == "-freeslack":
                    freeslack = array[count + 1]
                    taskmongoupdate(channels, taskid, "freeslack", freeslack)
                if z == "-startdate":
                    starttime = array[count + 1]
                    taskmongoupdate(channels, taskid, "starttime", starttime)
                if z == "-enddate":
                    endtime = array[count + 1]
                    taskmongoupdate(channels, taskid, "endtime", endtime)
                if z == "-taskcontent":
                    taskcontent = array[count + 1]
                    taskmongoupdate(channels, taskid, "taskcontent", taskcontent)
                if z == "-type":
                    if array[count + 1] == "important" or array[count + 1] == "normal" or array[
                        count + 1] == "critical" or array[count + 1] == "finished":
                        type = array[count + 1]
                        taskmongoupdate(channels, taskid, "type", type)
                if z == "-removedepend":
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
                    arraylist=",".join(arraydepends)
                    taskmongoupdate(channels, taskid, type, arraylist)
                if z == "-addepend":
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
                        arraydepends=adddepends
                    elif adddepends == None:
                        adddepends = ""
                        arraydepends=dependslist
                    else:
                        arraydepends = dependslist + "," + adddepends
                    taskmongoupdate(channels, taskid, type, arraydepends)
            count = count + 1
        text = "System updated!"
        SlackCommunication.postMessege(channels, text)
    except:
        text = "Process terminated. check input again"
        SlackCommunication.postMessege(channels, text)

def statusUpdate(key,channels,update):
    record = None
    records = db.get_collection("task")
    record = records.find_one_and_update({"taskid": key}, {'$set': {"status": update}})
    return record


def taskstatus(taskid):
    documents = db.get_collection("task")
    try:
        status = documents.find({"taskid": taskid}).distinct("status")[0]
        return status
    except:
        return "Wrong task id"


def taskforecast(taskid,startdate,days,channels):
    endepend,startdepend,remaindays=None,None,None
    try:
        documents = db.get_collection("task")
        taskprogress = documents.find({"taskid": taskid}).distinct("taskprogress")[0]
        taskfree = documents.find({"taskid": taskid}).distinct("freeslack")[0]
        starttime = documents.find({"taskid": taskid}).distinct("starttime")[0]
        endtime = documents.find({"taskid": taskid}).distinct("endtime")[0]
        type= documents.find({"taskid": taskid}).distinct("type")[0]
        status = documents.find({"taskid": taskid}).distinct("status")[0]
        endepends=documents.find({"taskid": taskid}).distinct("enddepends")[0]
        startdepends = documents.find({"taskid": taskid}).distinct("startdepends")[0]
        if endepends!=None:
            endepend=endepends[0]
        if startdepends!=None:
            startdepend=startdepends[0]
    except:
        text = "Problem in task forecast"
        SlackCommunication.postMessege(channels, text)
    if (days>taskfree):
        remaindays=days-taskfree

    holdtarttime = startdate.split("/")
    holdstrtyr = holdtarttime[0]
    holdstrtmon = holdtarttime[1]
    holdstrtdt = holdtarttime[2]

    taskstarttime = starttime.split("/")
    taskstrtyr = taskstarttime[0]
    taskstrtmon = taskstarttime[1]
    taskstrtdt = taskstarttime[2]

    taskendtime = endtime.split("/")
    taskendyr = taskendtime[0]
    taskendmon = taskendtime[1]
    taskenddt = taskendtime[2]

    if (holdstrtdt+days)>30 and days<30:
        holdenddate=days-(30-holdstrtdt)
        if((holdstrtmon+1)<12):
            holdendmonth=holdstrtmon+1
        else:
            holdendyr=holdstrtyr+1
            holdendmonth=1
    elif (holdstrtdt+days)<30:
        holdenddate = holdstrtdt+days
    elif (holdstrtdt+days)>30 and days>30:
        months=math.floor(days/30)
        xdays = days - months * 30
        if months>12:
            years=math.floor(months/12)
            xmonths=months-years*12
            holdendyr=holdstrtyr+years
            holdendmonth=holdstrtmon+xmonths
            holdenddate=holdstrtdt+xdays
            if holdendmonth>12:
                holdendyr=holdendyr+1
                holdendmonth=xmonths-(12-holdstrtmon)
            if holdenddate>30:
                holdendmonth=holdendmonth+1
                holdenddate=xdays-(30-holdstrtdt)

    blockedTasks(taskid,holdstrtyr,holdstrtmon,holdstrtdt,holdendyr,holdendmonth,holdenddate,taskstrtyr,
                 taskstrtmon,taskstrtdt,taskendyr,taskendmon,taskenddt,channels,days,remaindays)


def blockedTasks(taskid,holdstrtyr,holdstrtmon,holdstrtdt,holdendyr,holdendmonth,holdenddate,taskstrtyr,taskstrtmon,
                 taskstrtdt,taskendyr,taskendmon,taskenddt,channels,days,remaindays):
    if taskstrtyr == holdstrtyr and taskstrtmon==holdstrtmon and taskstrtdt==holdstrtdt:
        depends.startdependtask(channels,taskid, days,remaindays)
    if taskendyr==holdendyr and taskendmon==holdendmonth and taskenddt==holdenddate:
        depends.enddependtask(channels,taskid, days,remaindays)


    if taskstrtyr<holdstrtyr and taskendyr<holdendyr:
        depends.enddependtask(channels,taskid, days,remaindays)
    if taskstrtyr==holdstrtyr and taskendyr<holdendyr:
        depends.enddependtask(channels,taskid, days,remaindays)
        if taskstrtmon == holdstrtmon and taskstrtmon > holdstrtmon :
            if taskstrtdt > holdstrtdt and taskstrtdt == holdstrtdt:
                depends.startdependtask(channels,taskid, days,remaindays)
    if taskstrtyr==holdstrtyr and taskendyr>holdendyr:
        if taskstrtmon == holdstrtmon and taskstrtmon > holdstrtmon:
            if taskstrtdt > holdstrtdt and taskstrtdt == holdstrtdt:
                depends.startdependtask(channels,taskid, days,remaindays)


    if taskstrtyr == holdstrtyr and taskendyr == holdendyr:
        if taskstrtmon < holdstrtmon and taskendmon < holdendmonth:
            depends.enddependtask(channels,taskid, days,remaindays)
        if taskstrtmon == holdstrtmon and taskendmon < holdendmonth:
            depends.enddependtask(channels,taskid, days,remaindays)
            if taskstrtdt > holdstrtdt and taskstrtdt == holdstrtdt:
                depends.startdependtask(channels,taskid, days,remaindays)
        if taskstrtmon < holdstrtmon and taskendmon == holdendmonth:
            if taskenddt < holdenddate and taskenddt == holdenddate:
                depends.enddependtask(channels,taskid, days,remaindays)
        if taskstrtmon == holdstrtmon and taskendmon == holdendmonth:
            if taskstrtdt < holdstrtdt and taskenddt < holdenddate:
                depends.enddependtask(channels,taskid, days,remaindays)
            if taskstrtdt == holdstrtdt and taskenddt < holdenddate:
                depends.startdependtask(channels,taskid, days,remaindays)
                depends.enddependtask(channels,taskid, days,remaindays)
            if taskstrtdt == holdstrtdt and taskenddt > holdenddate:
                depends.startdependtask(channels,taskid, days,remaindays)
                if remaindays!=None:
                    depends.enddependtask(channels,taskid, days,remaindays)
            if taskstrtdt < holdstrtdt and taskenddt > holdenddate:
                if remaindays!=None:
                    depends.enddependtask(channels,taskid, days,remaindays)
            if taskstrtdt < holdstrtdt and taskenddt == holdenddate:
                depends.enddependtask(channels,taskid, days,remaindays)
            if taskstrtdt == holdstrtdt and taskenddt == holdenddate:
                depends.startdependtask(channels,taskid, days,remaindays)
                depends.enddependtask(channels,taskid, days,remaindays)




class depends:
    documents = db.get_collection("task")
    arrays=[]
    def startdependtask(self,channels,taskid,days,remaindays):
        endepends,startdepends=None,None
        dependslist = self.documents.find({"taskid": taskid}).distinct("startdepends")[0]
        dependstartarray = dependslist.split(",")
        for taskids in dependstartarray:
            taskprogress = self.documents.find({"taskid": taskid}).distinct("taskprogress")[0]
            taskfree = self.documents.find({"taskid": taskid}).distinct("freeslack")[0]
            starttime = self.documents.find({"taskid": taskid}).distinct("starttime")[0]
            endtime = self.documents.find({"taskid": taskid}).distinct("endtime")[0]
            type = self.documents.find({"taskid": taskid}).distinct("type")[0]
            status = self.documents.find({"taskid": taskid}).distinct("status")[0]
            endepends = self.documents.find({"taskid": taskid}).distinct("enddepends")[0]
            startdepends = self.documents.find({"taskid": taskid}).distinct("startdepends")[0]
            if remaindays!=None and remaindays!=0:
                if remaindays>taskfree:
                    remaindays=remaindays-taskfree
                    if status!="fine" and status!="finished":
                        text = "task "+taskid+" is not in good status. So its risk to hold task for "+remaindays+" days."
                        SlackCommunication.postMessege(channels, text)
                        if type=="important":
                            text = "Also task " + taskid + " is important tasks "
                            SlackCommunication.postMessege(channels, text)

            dicarray={
                "taskids":taskids,
                "parenttask":taskid,
                "taskprogress":taskprogress,
                "type": type,
                "taskfree": taskfree,
                "starttime": starttime,
                "endtime": endtime,
                "status": status,
                "endepends": endepends,
                "startdepends": startdepends,
                "remaindays": remaindays
                }
            self.arrays[self.count]=dicarray
            if startdepends!=None:
                dependstartarray = startdepends.split(",")
                for starttaskids in dependstartarray:
                    depends.startdependtask(self, starttaskids, days, remaindays)
            if endepends!=None and remaindays>depends.periodCalculator(self,starttime,endtime):
                dependendarray = endepends.split(",")
                for endtaskids in dependendarray:
                    depends.startdependtask(self, endtaskids, days, remaindays)
            self.count=self.count+1

        return self.arrays

    def enddependtask(self,channels,taskid,days,remaindays):
        dependslist = self.documents.find({"taskid": taskid}).distinct("enddepends")[0]
        dependendarray = dependslist.split(",")
        dependstartarray = dependslist.split(",")
        for taskids in dependstartarray:
            taskprogress = self.documents.find({"taskid": taskid}).distinct("taskprogress")[0]
            taskfree = self.documents.find({"taskid": taskid}).distinct("freeslack")[0]
            starttime = self.documents.find({"taskid": taskid}).distinct("starttime")[0]
            endtime = self.documents.find({"taskid": taskid}).distinct("endtime")[0]
            type = self.documents.find({"taskid": taskid}).distinct("type")[0]
            status = self.documents.find({"taskid": taskid}).distinct("status")[0]
            endepends = self.documents.find({"taskid": taskid}).distinct("enddepends")[0]
            startdepends = self.documents.find({"taskid": taskid}).distinct("startdepends")[0]
            if remaindays != None and remaindays!=0:
                if remaindays > taskfree:
                    remaindays = remaindays - taskfree
                    if status != "fine":
                        text = "task "+taskid+" is not in good status. So its risk to hold task for "+remaindays+" days."
                        SlackCommunication.postMessege(channels, text)
                        if type == "important":
                            text = "Also task " + taskid + " is important tasks "
                            SlackCommunication.postMessege(channels, text)

            dicarray = {"taskids": taskids,
                        "taskprogress": taskprogress,
                        "type": type,
                        "taskfree": taskfree,
                        "starttime": starttime,
                        "endtime": endtime,
                        "status": status,
                        "endepends": endepends,
                        "startdepends": startdepends,
                        "remaindays": remaindays
                        }
            self.arrays[self.count] = dicarray
            if startdepends != None:
                dependstartarray = startdepends.split(",")
                for starttaskids in dependstartarray:
                    depends.startdependtask(self, starttaskids, days, remaindays)
            if endepends != None:
                dependendarray = endepends.split(",")
                for endtaskids in dependendarray:

                    depends.startdependtask(self, endtaskids, days, remaindays)
            self.count = self.count + 1
        return self.arrays

    def periodCalculator(self,starttimes,endtimes):
        strt = starttimes.split("/")
        end = endtimes.split("/")
        if len(end) == 3 and len(strt) == 3:
            strtyr = strt[0]
            strtmon  = strt[1]
            strtdt = strt[2]
            endyr = end[0]
            endmon = end[1]
            endtdt = end[2]
            yrs=endyr-strtyr
            if endyr!=strtyr:
                months=12-strtmon+endmon
            else:
                months=endmon-strtmon
            if strtmon!=endmon:
                days=30-strtdt+endtdt
            else:
                days=endtdt-strtdt

            totaldays=yrs*365+months*30+days
            return totaldays

