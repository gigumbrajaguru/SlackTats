from slackclient import SlackClient
import pymongo
from ProjectAnalyzer import SlackCommunication,Project,Task
import UserManager
connection=pymongo.MongoClient("mongodb://localhost:27017/")
db=connection.get_database("SlackTats")
slack_token = "xoxb-402757429986-412087740598-8bGVF1HoEKEdfQws9aNDTeUM"
sc = SlackClient(slack_token)



def dateValidation(manager,projectid,starttime,endtime):
    document=db.get_collection("project")
    try:
        setstartdate=document.find({"projectid":projectid}, {"startdate": 1,"enddate":1}).distinct("startdate")[0]
        setenddate = document.find({"projectid":projectid}, {"startdate": 1, "enddate": 1}).distinct("enddate")[0]
        strt=setstartdate.split("/")
        strtyr=int(strt[0])
        strtmon = int(strt[1])
        strtdt = int(strt[2])
        end = setenddate.split("/")
        endyr = int(end[0])
        endmon = int(end[1])
        endtdt = int(end[2])

        taskstarttime=starttime.split("/")
        taskendtime=endtime.split("/")
        taskstrtyr = int(taskstarttime[0])
        taskstrtmon = int(taskstarttime[1])
        taskstrtdt = int(taskstarttime[2])

        taskendyr = int(taskendtime[0])
        taskendmon = int(taskendtime[1])
        taskendtdt = int(taskendtime[2])

        if strtyr<taskstrtyr and taskendyr<endyr:
            return True
        if strtyr<taskstrtyr and taskendyr==endyr and taskendmon<endmon:
            return True
        if strtyr<taskstrtyr and taskendyr==endyr and taskendmon==endmon  and taskendtdt<endtdt :
            return True
        if strtyr==taskstrtyr and strtmon < taskstrtmon and taskendyr<endyr:
            return True
        if strtyr == taskstrtyr and strtmon == taskstrtmon and strtdt<taskstrtdt  and taskendyr < endyr:
            return True
        if strtyr == taskstrtyr and strtmon == taskstrtmon and strtdt==taskstrtdt  and taskendyr < endyr:
            return True

        elif strtyr==taskstrtyr and endyr==taskendyr and strtmon<taskstrtmon and taskendmon<endmon:
            return True
        elif strtyr==taskstrtyr and endyr==taskendyr and strtmon==taskstrtmon and strtdt<taskstrtdt and taskendmon<endmon:
            return True
        elif strtyr==taskstrtyr and endyr==taskendyr and strtmon==taskstrtmon and strtdt==taskstrtdt and taskendmon<endmon:
            return True
        elif strtyr == taskstrtyr and endyr == taskendyr and strtmon < taskstrtmon and taskendmon == endmon and taskendtdt<endtdt :
            return True
        elif strtyr == taskstrtyr and endyr == taskendyr and strtmon < taskstrtmon and taskendmon == endmon and taskendtdt == endtdt:
            return True

        elif strtyr==taskstrtyr and endyr==taskendyr and strtmon==taskstrtmon and taskendmon==endmon and strtdt<taskstrtdt and taskendtdt<endtdt:
            return True
        elif strtyr==taskstrtyr and endyr==taskendyr and strtmon==taskstrtmon and taskendmon==endmon and strtdt==taskstrtdt and taskendtdt<endtdt:
            return True
        elif strtyr==taskstrtyr and endyr==taskendyr and strtmon==taskstrtmon and taskendmon==endmon and strtdt==taskstrtdt and taskendtdt==endtdt:
            return True
        elif strtyr == taskstrtyr and endyr == taskendyr and strtmon == taskstrtmon and taskendmon == endmon and strtdt < taskstrtdt and taskendtdt == endtdt:
            return True
        else:
            return False
    except:
        return False

def periodValidation(startdate,enddate,channel):
    if startdate!=None and enddate!=None:
        strt = startdate.split("/")
        end = enddate.split("/")
        if len(end) == 3 and len(strt) == 3:
            strtyr = int(strt[0])
            strtmon = int(strt[1])
            strtdt = int(strt[2])
            endyr = int(end[0])
            endmon = int(end[1])
            endtdt = int(end[2])
            if strtyr < endyr:
                return True
            elif strtyr == endyr and strtmon < endmon:
                return True
            elif strtyr == endyr and strtmon == endmon and strtdt < endtdt:
                return True
            else:
                return False
        else:
            text = "Please check input again"
            SlackCommunication.postMessege(channel, text)
            return False

    else:
        text = "Please check input commands again"
        SlackCommunication.postMessege(channel, text)
def create_Task(dict):
    manager = dict.get("user")
    channel = dict.get("channel")
    count = 0
    if UserManager.checkUserRole(manager):
        taskname=None
        taskid=None
        projectid=None
        starttime=None
        endtime=None
        type=None
        taskcontent=None
        msg = dict.get("text")
        array = msg.split(" ")

        for split in array:
            if split!=None and split!=" ":
                if split[0] == "-":
                    if split == "-taskname":
                        taskname = array[count+1]
                    if split == "-taskid":
                        taskid = array[count + 1]
                    if split == "-projectid":
                        projectid = array[count + 1]
                    if split == "-freeslack":
                        freeslack = array[count + 1]
                    if split == "-startdate":
                        starttime = array[count + 1]
                    if split == "-enddate":
                        endtime = array[count + 1]
                    if split == "-taskcontent":
                        taskcontent = array[count + 1]
                    if split == "-type":
                        if array[count + 1]=="important" or array[count + 1]=="normal" or array[count + 1]=="critical":
                            type = array[count + 1]
            count = count + 1
        if dateValidation(manager,projectid,starttime,endtime) and periodValidation(starttime,endtime,channel) and Task.duplicateChecker("taskid", taskid,"task"):
            records = db.get_collection("task")
            mydict = {"taskname": taskname , "taskid": taskid, "projectid": projectid, "taskprogress": "0",
                      "freeslack": freeslack, "starttime": starttime, "endtime": endtime, "type": type, "status": "fine","taskcontent":taskcontent}
            ischeck = records.insert_one(mydict).acknowledged
            if ischeck:
                text = "Task created"
                SlackCommunication.postMessege(channel,text)
        else:
            text = "Process terminated. Check input again"
            SlackCommunication.postMessege(channel, text)
    else:
        text = "Only project manager can perform this project"
        SlackCommunication.postMessege(channel, text)

def register_Project(dict):
    count=0
    user=dict.get("user")
    msg = dict.get("text")
    channels = dict.get("channel")
    if UserManager.checkUserRole(user):
        projectid,projectname,startdate,enddate,totalslack=None,None,None,None,None
        array = msg.split(" ")
        for split in array:
            if split[0] != None and split[0] != " ":
                if split[0] == "-":
                    if split=="-projectid":
                        projectid=array[count+1]
                    if split=="-projectname":
                        projectname=array[count+1]
                    if split == "-startdate":
                        startdate=array[count+1]
                    if split == "-enddate":
                        enddate=array[count+1]
                    if split == "-totalslack":
                        totalslack=array[count+1]
            count=count+1
        records = db.get_collection("project")
        if periodValidation(startdate,enddate,channels) and  projectid!=None and projectname!=None and startdate!=None and enddate!=None and totalslack!=None and Task.duplicateChecker("projectid",projectid,"project"):
            mydict = {"projectid": projectid, "projectname": projectname, "startdate": startdate, "enddate": enddate,"totalslack": totalslack,"managerid": user}
            ischecked = records.insert_one(mydict).acknowledged
            if ischecked:
                text = "Project  " + projectname + " is connected"
                SlackCommunication.postMessege(channels, text)
            else:
                text = "Process terminated. Try again"
                SlackCommunication.postMessege(channels, text)
        else:
            text = "Check input again"
            SlackCommunication.postMessege(channels, text)
    else:
        text = "Only project manager can perform this project"
        SlackCommunication.postMessege(channels, text)



def settaskdepends(dict):
    count=0
    msg = dict.get("text")
    channels = dict.get("channel")
    user=dict.get("user")
    if UserManager.checkUserRole(user):
        main,startdepends,enddepends=None,None,None
        array = msg.split(" ")
        for split in array:
            if split != None and split != "":
                if split[0] == "-":
                    if split == "-maintask":
                        main = array[count + 1]
                    if split == "-startdepends":
                        startdepends = array[count + 1]
                    if split == "-endepends":
                        enddepends = array[count + 1]
            count = count + 1
        records = db.get_collection("task")
        startdep = records.find({"taskid": main}, {"taskid": 1}).distinct("startdepends")
        enddep = records.find({"taskid": main}, {"taskid": 1}).distinct("enddepends")

        if listCheck(startdepends,startdep) and listCheck(enddepends,enddep):

            if startdep!=None and startdep!=[] and startdep!=[None] and startdepends!=None:
                startdepends=startdepends+","+str(startdep[0])
            elif startdep!=None and startdep!=[] and startdep!=[None] and startdepends==None:
                startdepends =  str(startdep[0])

            if enddep!= None and enddep != [] and enddep!=[None] and enddepends!=None:
                enddepends = enddepends + "," + str(enddep[0])
            elif enddep != None and enddep != [] and enddep != [None] and enddepends == None:
                enddepends = str(enddep[0])

            startlen,endlen=0,0
            if main!=None:
                if startdepends!=None and startdepends!=[]:
                    startdependset = startdepends.split(",")
                    startlen=len(startdependset)
                else:
                    startdependset=None
                if enddepends != None and enddepends!=[]:
                    enddependset = enddepends.split(",")
                    endlen=len(enddependset)
                else:
                    enddependset=None
                if checktaskdepend(startdependset,channels) and  checktaskdepend(enddependset,channels):
                    countdepend = startlen+endlen
                    record=records.find_one_and_update({"taskid":main},{'$set':{"startdepends":startdepends,"enddepends":enddepends}})
                    if record:
                        text = str(countdepend)+" tasks depend on "+main+" task"
                        SlackCommunication.postMessege(channels, text)
                    else:
                        text = "Process terminated. Check input again"
                        SlackCommunication.postMessege(channels, text)
        else:
            text = "Some depends already submitted"
            SlackCommunication.postMessege(channels, text)
    else:
        text = "Only project manager can perform this project"
        SlackCommunication.postMessege(channels, text)

def checktaskdepend(dependset,channels):
    records = db.get_collection("task")
    if dependset!=None and dependset!=[]:
        try:
            for item in dependset:
                check=records.find({"taskid":item},{"taskid":1}).distinct("taskid")[0]
                if check!=None and check==item:
                    return True
                else:
                    text = "No task found,check depends again."
                    SlackCommunication.postMessege(channels, text)
                    return False
        except:
            text = "No task found,check depends again."
            SlackCommunication.postMessege(channels, text)
            return False
    else:
        return True

def update_github(dict):
    count = 0
    msg = dict.get("text")
    manager=dict.get("user")
    channel=dict.get("channel")
    ts=dict.get("ts")
    githublink=None
    array = msg.split(" ")
    if UserManager.checkUserRole(manager):
        for split in array:
            try:
                if split != None and split != "":
                    if split[0] == "-":
                        if split == "-githublink":
                            githublink = array[count + 1]
            except:
                break
            count = count + 1
        SlackCommunication.deleteMessege(channel, ts)
        records = db.get_collection("project")
        if githublink=="" or githublink==None:
            text = "User command is incomplete. Please input right command to proceed"
            SlackCommunication.postMessege(channel, text)
        else:
            if UserManager.checkUserRole(manager) and githublink!=None:
                githublink=githublink[1:]
                githublink=githublink[:-1]
                githublink=githublink.split("|")[0]
                if records.find_one_and_update({"managerid": manager}, {'$set': {"githublink": githublink}}):
                    text = "Github linked"
                    SlackCommunication.postMessege(channel, text)
    else:
        text="Only manager can performe this command and need to configure at the beginning of project"
        SlackCommunication.postMessege(channel, text)

def taskContent(dict):
    msg = dict.get("text")
    records = db.get_collection("task")
    manager = dict.get("user")
    channel = dict.get("channel")
    arraycontent=[]
    array = msg.split(" ")
    if UserManager.checkUserRole(manager):
        taskid, content= None, None
        if array[0]=="-taskcontent" and array[1]=="-taskid" and array[3]=="-projectid":
            for x in range(5,len(array)):
                arraycontent.append(array[x])
                objectives=" ".join(arraycontent)
            if records.find_one_and_update({"taskid": array[2], "projectid": array[4]}, {
                '$set': {"taskcontent": objectives}}):
                text="Data updated"
                SlackCommunication.postMessege(channel,text)
    else:
        text = "Only project manager can perform this command"
        SlackCommunication.postMessege(channel, text)

def checkTaskStatus(taskid):
    return Task.taskstatus(taskid)

def taskHold(dict):
    taskid,days,startdate,count=None,0,None,0
    msg = dict.get("text")
    manager = dict.get("user")
    channel = dict.get("channel")
    array = msg.split(" ")
    if UserManager.checkUserRole(manager):
        for split in array:
            if split != None and split != " ":
                if split[0] == "-":
                    if split == "-taskid":
                        taskid = array[count + 1]
                    if split == "-startdate":
                        startdate = array[count + 1]
                    if split == "-days":
                        days = int(array[count + 1])
            count = count + 1
        Task.taskforecast(taskid,startdate,days,channel)
    else:
        text = "Only project manager can perform this command"
        SlackCommunication.postMessege(channel, text)

def listCheck(idlist,submittedidlist):
    if idlist!=None and idlist!=[] and submittedidlist!=None and submittedidlist!=[]:
        currentlist=idlist.split(",")
        summmited=submittedidlist[0].split(",")
        for checkid in currentlist:
            for checkidlist in summmited:
                if checkid==checkidlist:
                    return False
        return True
    else:
        return True
