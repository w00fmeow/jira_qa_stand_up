#!/usr/bin/env python3
import requests, json, sys
from datetime import datetime, timedelta

class Jira():
    def __init__(self, path_to_config):
        self.headers = self.get_headers()
        self.load_config(path_to_config)

        self.now = datetime.now()
        self.load_time_range()

    def load_config(self, path_to_config):
        config = json.loads(open(path_to_config).read())
        try:
            assert config
            assert "server" in config
            assert "api_path" in config
            assert "auth" in config
            assert "email" in config["auth"]
            assert config["auth"]["email"]
            assert "password" in config["auth"]
            assert config["auth"]["password"]
            assert "project" in config
            assert config["project"]
            assert "boardId" in config
            assert config["boardId"]

            self.server = config["server"]
            self.auth = (config["auth"]["email"], config["auth"]["password"], )
            self.project = config["project"]
            self.api_path = config["api_path"]
            self.active_sprint = self.get_active_sprint(board_id=config["boardId"])

        except Exception as e:
            print("Error loading configuration. Please, check your config file")
            sys.exit(1)
    
    def load_time_range(self):
        start = self.now - timedelta(days=1)
        if self.now.weekday() in [6, 5, 4]:
            while start.weekday() != 3:
                start -= timedelta(days=1)

        self.time_range = (start.strftime('%Y-%m-%d'), self.now.strftime('%Y-%m-%d'), )

    def get_active_sprint(self, board_id):
        res_agile_path = "/rest/agile/1.0"
        path = "/board/{}/sprint?state=active".format(board_id)
        try:
            r = requests.get(self.server + res_agile_path + path, headers=self.headers, auth=self.auth)
            return r.json()['values'][0]['id']
        except Exception as e:
            print("There was an error loading active sprint")
            print(e)
            sys.exit(1)

    def load_issues(self):
        self.load_opened_bugs()
        self.load_done_tickets()
        self.load_ready_for_testing()
        self.load_testing()
            
    def load_opened_bugs(self):
        self.opened_bugs = self.search(created=True, sprint=False, reporter="currentUser()", issue_type='Bug').json()["issues"]

    def load_done_tickets(self):
        self.done_tickets = self.search(status="Done", status_changed=True).json()["issues"]
    
    def load_ready_for_testing(self):
        self.ready_for_testing = self.search(status='"Ready For Testing"').json()["issues"]
        
    def load_testing(self):
        self.testing = self.search(status='"Testing in QA"').json()["issues"]

    def projects(self):
        self.projects = self.jira.projects()
        return self.projects

    def get_headers(self):
        return {
            "accept": "application/json",
            "content-Type" : "application/json"
            }

    def fetch(self, path):
        try:
            r = requests.get(self.server + self.api_path + path, headers=self.headers, auth=self.auth)
            return r
        except Exception as e:
            print(e)

    def search(self, text=None, project=None, issue_type=None, created=False,
                        reporter=None, status=None, status_changed=False,
                        sprint=True, max_results=10000):
        if not project:
            project = self.project
        path = "/search?jql=project = {}".format(project)
        if issue_type:
            path += " AND issuetype = {}".format(issue_type)
        if created:
            path += " AND created >= {} AND created <= {}".format(*self.time_range)
        if reporter:
            path += " AND reporter in ({})".format(reporter)
        if status:
            path += " AND status = {}".format(status)
        if status_changed:
            path += " AND statusCategoryChangedDate >= {} AND statusCategoryChangedDate <= {}".format(*self.time_range)
        if sprint:
            path += " AND Sprint = {}".format(self.active_sprint)

        if max_results:
            path += "&maxResults={}".format(max_results)
        if text:
            path += "&text={}".format(text)
        # print(path)
        return self.fetch(path=path)
