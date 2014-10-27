#!/usr/bin/env python3

"""
Module containing the classes needed for the PyGHI CLI
"""

import os
import sys
import time
import platform
import re
import json
import webbrowser
import threading
import argparse

import requests
if platform.system() == "Windows":
    import colorama

from .issue import Issue
from .label import Label
from .milestone import Milestone

from .helpers import stylize, pager, get_terminal_size
from .arguments import add_arguments
from .stopwords import stopwords

class PyGHI:
    """ Main PyGHI CLI class """
    def __init__(self, wd):
        if platform.system() == "Windows":
            colorama.init()

        self.cwd = wd
        self.basedir = os.path.dirname(os.path.realpath(__file__))
        self.stopwords = stopwords()

        # Load config
        configpath = os.path.join(os.path.expanduser("~"), ".pyghiconf")

        self.config = {}
        if os.path.exists(configpath):
            try:
                self.config = json.load(open(configpath, "r"))
            except:
                self.log(1, "Couldn't parse config file.")

        # Check for git repo
        gitpath = None
        try:
            curpath = self.cwd
            for i in range(20): # maximum depth
                if os.path.isdir(os.path.join(curpath, ".git")):
                    gitpath = os.path.join(curpath, ".git")
                    break
                if curpath == os.path.dirname(curpath): # reached root
                    break
                curpath = os.path.dirname(curpath)
            assert(curpath != None)
        except:
            self.log(2, "Current directory is no git repo.")

        # Get repository data
        try:
            gitconfigpath = os.path.join(gitpath, "config")
            gitconfig = open(gitconfigpath, "r").read()

            origin = re.match(
                r".*?\[remote \"origin\"\].*?url = (.*?)\n",
                gitconfig,
                re.DOTALL
            ).group(1)

            match = re.match(
                r".*?github\.com\/([a-zA-Z0-9-_]+)\/([a-zA-Z0-9-_]+)",
                origin
            )

            self.owner = match.group(1)
            self.repo = match.group(2)
        except:
            self.log(2, "Couldn't extract GitHub URL.")

        # Parse Arguments
        self.parser = None
        add_arguments(self)

    def parse_args(self, args=sys.argv[1:]):
        """ Parses given arguments. Default is sys.argv[1:] """
        if len(args) == 0:
            args = ["list"]
        args = self.parser.parse_args(args)
        args.func(args)

    def get_json(self, url, params={}):
        url = "https://api.github.com/" + url
        try:
            if "username" in self.config and "password" in self.config:
                auth = (self.config["username"], self.config["password"])
                r = requests.get(url, params=params, auth=auth)
            else:
                r = requests.get(url, params=params)

            if r.status_code != 200:
                self.log(2, "Couldn't connect to GitHub. Status Code: %i" % (
                    r.status_code
                ))

            return r.json()
        except:
            self.log(2, "Couldn't connect to GitHub.")

    def patch_json(self, url, payload={}):
        url = "https://api.github.com/" + url

        if not "username" in self.config or not "password" in self.config:
            self.log(2, "You are not authorized to do that.")

        auth = (self.config["username"], self.config["password"])
        r = requests.patch(url, auth=auth, data=json.dumps(payload))

        if r.status_code != 200:
            self.log(2, "Couldn't connect to GitHub. Status Code: %i" % (
                r.status_code
            ))

    def post_json(self, url, payload={}):
        url = "https://api.github.com/" + url

        if not "username" in self.config or not "password" in self.config:
            self.log(2, "You are not authorized to do that.")

        auth = (self.config["username"], self.config["password"])
        r = requests.post(url, auth=auth, data=json.dumps(payload))

        if r.status_code != 201:
            self.log(2, "Couldn't connect to GitHub. Status Code: %i" % (
                r.status_code
            ))

        return r.json()

    def log(self, level, message):
        """
        Outputs a log message and quits on error.
        Levels: 0: Info, 1: Warning, 2: Error (quit)
        """
        prefixes = [
            stylize("INFO:", fg=0x00FF00, bold=True),
            stylize("WARNING:", fg=0xFFFF00, bold=True),
            stylize("ERROR:", fg=0xFF0000, bold=True)
        ]
        print(prefixes[level], message)

        if level == 2:
            try:
                self.stop_event.set()
            except:
                pass
            sys.exit(1)

    def spinner(self):
        i = 0
        while not self.stop_event.is_set():
            output = [
                stylize("[", bold=True),
                stylize(":", fg=0xFFFF00),
                stylize(":", fg=0xFFFF00),
                stylize(":", fg=0xFFFF00),
                stylize(":", fg=0xFFFF00),
                stylize(":", fg=0xFFFF00),
                stylize("]", bold=True)
            ]
            output[i+1] = stylize("|", fg=0x00FF00, bold=True)
            print("".join(output), end="\r")
            i = (i+1) % 5
            time.sleep(0.1)

        # Clear line
        cols, rows = get_terminal_size()
        print(" "*cols, end="\r")

    def start_spinner(self):
        self.stop_event = threading.Event()
        thread = threading.Thread(target=self.spinner)
        thread.start()

    def stop_spinner(self):
        self.stop_event.set()

    def list(self, args):
        params = {
            "state": args.state,
            "milestone": args.milestone,
            "labels": args.labels,
            "assignee": args.assignee,
            "creator": args.creator,
            "per_page": 100
        }
        params = {k: v for k, v in params.items() if v != None}

        statestr = args.state[0].upper() + args.state[1:]
        heading = "%s Issues for %s/%s" % (
            statestr,
            self.owner,
            self.repo
        )

        if args.milestone:
            heading += ", with milestone #%i" % (params["milestone"])
        if args.labels:
            heading += ", labeled %s" % (params["labels"])
        if args.assignee:
            heading += ", assigned to %s" % (params["assignee"])
        if args.creator:
            heading += ", created by %s" % (params["creator"])

        print(stylize(heading + ":", fg=0x00FF00, bold=True))

        self.start_spinner()

        url = "repos/%s/%s/issues" % (self.owner, self.repo)
        issues = []
        for i in range(1, 20):
            params["page"] = i
            last = self.get_json(url, params)
            if len(last) == 0:
                break
            issues += last

        self.stop_spinner()

        issues = list(map(lambda x: Issue(self, x), issues))
        if args.type == "issues":
            issues = list(filter(lambda x: not x.is_pr, issues))
        if args.type == "prs":
            issues = list(filter(lambda x: x.is_pr, issues))

        output = "No results." if len(issues) == 0 else ""
        for issue in issues:
            output += issue.print_line(
                args.shortlabels,
                args.nolabels,
                args.nocomments
            )

        pager(output)

    def show(self, args):
        if args.browser:
            savout = os.dup(1)
            os.close(1)
            os.open(os.devnull, os.O_RDWR)
            try:
                webbrowser.open("https://github.com/%s/%s/issues/%i" % (
                    self.owner,
                    self.repo,
                    args.issueid
                ), 2, True)
            finally:
                os.dup2(savout, 1)
                sys.exit()

        heading = "Issue #%i in %s/%s:" % (args.issueid, self.owner, self.repo)
        print(stylize(heading, fg=0x00FF00, bold=True))

        self.start_spinner()

        url = "repos/%s/%s/issues/%i" % (self.owner, self.repo, args.issueid)
        issue = self.get_json(url, {})
        url += "/comments"
        comments = self.get_json(url, {})

        self.stop_spinner()

        issue = Issue(self, issue, comments)

        pager(issue.print_detail())

    def edit(self, args):
        payload = {
            "title": args.title,
            "body": args.body,
            "assignee": args.assignee if args.assignee != "none" else "",
            "state": args.state,
            "milestone": args.milestone,
            "labels": args.labels
        }
        payload = {k: v for k, v in payload.items() if v != None}

        if len(payload) == 0:
            nargs = self.parser.parse_args(["edit", "-h"])
            return nargs.func(nargs)

        self.start_spinner()

        url = "repos/%s/%s/issues/%i" % (self.owner, self.repo, args.issueid)
        self.patch_json(url, payload)

        self.stop_spinner()

        nargs = self.parser.parse_args(["show", str(args.issueid)])
        return nargs.func(nargs)

    def open(self, args):
        args = ["edit", str(args.issueid), "-s", "open"]
        nargs = self.parser.parse_args(args)
        return nargs.func(nargs)

    def close(self, args):
        args = ["edit", str(args.issueid), "-s", "closed"]
        nargs = self.parser.parse_args(args)
        return nargs.func(nargs)

    def assign(self, args):
        assignee = args.assignee
        if assignee == "":
            assignee = "none"
        args = ["edit", str(args.issueid), "-a", assignee]
        nargs = self.parser.parse_args(args)
        return nargs.func(nargs)

    def create(self, args):
        params = {
            "title": args.title,
            "body": args.body
        }

        self.start_spinner()

        url = "repos/%s/%s/issues" % (self.owner, self.repo)
        result = Issue(self, self.post_json(url, params))

        self.stop_spinner()

        nargs = self.parser.parse_args(["show", str(result.number)])
        return nargs.func(nargs)

    def comment(self, args):
        self.start_spinner()

        url = "repos/%s/%s/issues/%i/comments" % (
            self.owner,
            self.repo,
            args.issueid
        )
        self.post_json(url, {"body": args.comment})

        self.stop_spinner()

        nargs = self.parser.parse_args(["show", str(args.issueid)])
        return nargs.func(nargs)

    def milestone(self, args):
        statstr = args.state[0].upper() + args.state[1:]
        heading = "%s Milestones for %s/%s:" % (statstr, self.owner, self.repo)
        print(stylize(heading, fg=0x00FF00, bold=True))

        self.start_spinner()

        url = "repos/%s/%s/milestones" % (self.owner, self.repo)
        milestones = self.get_json(url, {"state": args.state, "per_page": 100})
        milestones = list(map(lambda x: Milestone(self, x), milestones))

        self.stop_spinner()

        output = ""
        if len(milestones) == 0:
            output = "No results."
        for milestone in milestones:
            output += milestone.print_line()

        pager(output)

    def label(self, args):
        heading = "Labels for %s/%s:" % (self.owner, self.repo)
        print(stylize(heading, fg=0x00FF00, bold=True))

        self.stop_event = threading.Event()
        thread = threading.Thread(target=self.spinner)
        thread.start()

        url = "repos/%s/%s/labels" % (self.owner, self.repo)
        labels = self.get_json(url, {})
        labels = list(map(lambda x: Label(self, x), labels))
        self.stop_event.set()

        output = ""
        if len(labels) == 0:
            output = "No results."
        for label in labels:
            output += label.print_line()

        pager(output)
