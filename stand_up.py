#!/usr/bin/env python3
from j import Jira

class StandUp():
    HELLO = '''\
     ╔╗            ╔╗            
    ╔╝╚╗           ║║            
╔══╗╚╗╔╝╔══╗ ╔═╗ ╔═╝║    ╔╗╔╗╔══╗
║══╣ ║║ ╚ ╗║ ║╔╗╗║╔╗║    ║║║║║╔╗║
╠══║ ║╚╗║╚╝╚╗║║║║║╚╝║    ║╚╝║║╚╝║
╚══╝ ╚═╝╚═══╝╚╝╚╝╚══╝    ╚══╝║╔═╝
                             ║║  
                             ╚╝  
'''
    SECTION_DELIMITER = "------------"
    ISSUE_DELIMITER = "~~~~"

    def __init__(self):
        self.jira = Jira(path_to_config='./config.json')
        self.welcome()
        self.report()

    def welcome(self):
        print(self.HELLO)
            
    def report(self):
        print("----- {} -----".format("Getting your report ready"))
        print()
        self.jira.load_issues()
        self.show_bugs()
        self.show_done()
        self.show_ready_for_testing()
        self.show_testing()

    def show_bugs(self):
        print("☠️       BUGS OPENED: {}".format(len(self.jira.opened_bugs)))
        for issue in self.jira.opened_bugs:
            print(self.ISSUE_DELIMITER)
            print(self.format_issue(issue))
        print(self.SECTION_DELIMITER)


    def format_issue(self, issue):
        assignee = None
        if issue["fields"]["assignee"]:
            if "displayName" in issue["fields"]["assignee"].keys():
                assignee = issue["fields"]["assignee"]["displayName"]
        return """Name: {name}\nurl: {url} | Type: {type}\nAssignee: {assignee} | Reporter: {reporter} | Status: {status}""".format(
            name=issue["fields"]["summary"].upper(),
            url="{}/browse/{}".format(self.jira.server, issue["key"]),
            type=issue["fields"]["issuetype"]["name"].upper(),
            assignee=assignee,
            reporter=issue["fields"]["reporter"]["displayName"],
            status=issue["fields"]["status"]["name"].upper()
        )

    def show_done(self):
        print("✅       TICKETS DONE: {}".format(len(self.jira.done_tickets)))
        for issue in self.jira.done_tickets:
            print(self.ISSUE_DELIMITER)
            print(self.format_issue(issue))
        print(self.SECTION_DELIMITER)

    def show_ready_for_testing(self):
        print("👾       READY FOR TESTING: {}".format(len(self.jira.ready_for_testing)))
        for issue in self.jira.ready_for_testing:
            print(self.ISSUE_DELIMITER)
            print(self.format_issue(issue))
        print(self.SECTION_DELIMITER)
    
    def show_testing(self):
        print("👷       TESTING IN QA: {}".format(len(self.jira.testing)))
        for issue in self.jira.testing:
            print(self.ISSUE_DELIMITER)
            print(self.format_issue(issue))
        print(self.SECTION_DELIMITER)


s = StandUp()