import time
import ProjectAnalyzer
import UserManager

from slackclient import SlackClient

# Developer : Gigum Bandara Rajaguru
# Project Name : SlackTats- SlackBot

slack_token = "xoxb-402757429986-412087740598-8bGVF1HoEKEdfQws9aNDTeUM"
sc = SlackClient(slack_token)

if sc.rtm_connect(with_team_state=False):
    while sc.server.connected is True:
        data=sc.rtm_read()
        if len(data) == 1:
            dict=data.pop(0)
##########################################################################
            # Commented by Gigum Bandara Rajaguru
            # replace yourcommand
            # if array[0] == "-youcommand":
            #     Yourpackage.initialmethod(dict)
            # dict is python disctionary so use .get() to get output.
            # example for dictionary file in folder:Test_Outputs(Tested outputs for understand purpose)
##########################################################################
            if dict.get('type')=="message" and dict.get('text')!=None:
                array=dict.get('text').split(" ")
                if array[0]=="-registerproject":
                    ProjectAnalyzer.register_Project(dict)
                if array[0]=="-registergithub":
                    ProjectAnalyzer.register_github(dict)
                if array[0] == "-registerprojectmanager":
                    ProjectAnalyzer.register_ProjectManager(dict)
                if array[0]== "-createtasks":
                    ProjectAnalyzer.create_Task(dict)
                if array[0]== "-setdepends":
                    ProjectAnalyzer.settaskdepends(dict)
                if array[0]== "-checktasks":
                    ProjectAnalyzer.Task.checkAlltaskdetails(dict)
                if array[0]== "-updatetask":
                    ProjectAnalyzer.Task.updatetask(dict)
                if array[0]== "-updateproject":
                    ProjectAnalyzer.Project.updateproject(dict)
                if array[0]== "-register":
                    UserManager.registration(dict)
                if array[0]== "-forecast":
                    ProjectAnalyzer.taskHold(dict)
                if array[0]== "-taskcontent":
                    ProjectAnalyzer.taskContent(dict)
                if array[0] == "-viewrepo":
                    ProjectAnalyzer.Project.printrepo(dict)

            if dict.get('type') == "user_typing":
                ProjectAnalyzer.Project.connectGithub(dict.get('channel'), dict.get('user'))
        time.sleep(1)
else:
    print ("Connection Failed")


