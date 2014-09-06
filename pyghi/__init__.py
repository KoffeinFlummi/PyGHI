#!/usr/bin/env python3

import os
import sys
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

from .helpers import *
from .stopwords import stopwords

class PyGHI:
  def __init__(self, wd):
    if platform.system() == "Windows":
      colorama.init()

    self.cwd = wd
    self.basedir = os.path.dirname(os.path.realpath(__file__))
    self.stopwords = stopwords()

    # Load config
    if platform.system() == "Windows":
      configpath = os.path.join(os.environ["HOMEPATH"], ".pyghiconf")
    else:
      configpath = os.path.join(os.environ["HOME"], ".pyghiconf")

    self.config = {}
    if os.path.exists(configpath):
      try:
        self.config = json.load(open(configpath, "r"))
      except:
        self.log(1, "Couldn't parse config file.")

    # Check for git repo
    if not os.path.isdir(os.path.join(self.cwd, ".git")):
      self.log(2, "Current directory is no git repo.")

    # Get repository data
    try:
      gitconfig = open(os.path.join(self.cwd, ".git", "config"), "r").read()
      origin = re.match(r".*?\[remote \"origin\"\].*?url = (.*?)\n", gitconfig, re.DOTALL).group(1)
      match = re.match(r"https.*?github\.com\/([a-zA-Z0-9]+)\/([a-zA-Z0-9]+)", origin)
      self.owner = match.group(1)
      self.repo = match.group(2)
    except:
      self.log(2, "Couldn't extract GitHub URL.")

    # Parse Arguments
    self.parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=20))
    subparsers = self.parser.add_subparsers()

    parser_list = subparsers.add_parser("list", formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50))
    parser_list_state = parser_list.add_mutually_exclusive_group()
    parser_list_state.add_argument("-s", "--state", type=str, choices=["open", "closed", "all"], metavar="STATE", default="open", help="show issues of this state")
    parser_list_state.add_argument("--closed", dest="state", action="store_const", const="closed", help="show closed issues")
    parser_list_state.add_argument("--all", dest="state", action="store_const", const="all", help="show both closed and open issues")
    parser_list.add_argument("-m", "--milestone", type=int, help="show issues with this milestone ID")
    parser_list.add_argument("-l", "--labels", type=str, help="show issues with these labels (comma-seperated list)")
    parser_list_labels = parser_list.add_mutually_exclusive_group()
    parser_list_labels.add_argument("-a", "--assignee", type=str, help="show issues assigned to this user")
    if "username" in self.config:
      parser_list_labels.add_argument("--mine", dest="assignee", action="store_const", const=self.config["username"], help="show issues assigned to you")
    parser_list_labels.add_argument("--noassignee", dest="assignee", action="store_const", const="none", help="show issues assigned to noone")
    parser_list.add_argument("-c", "--creator", type=str, help="show issues created by this user")
    parser_list_type = parser_list.add_mutually_exclusive_group()
    parser_list_type.add_argument("-t", "--type", type=str, help="show issues of this type")
    parser_list_type.add_argument("--issues", dest="type", action="store_const", const="issues", help="show only issues (no PRs)")
    parser_list_type.add_argument("--prs", dest="type", action="store_const", const="prs", help="show only PRs (no issues)")
    parser_list.add_argument("--duplicates", action="store_true", help="detect potential duplicates")
    parser_list_lprint = parser_list.add_mutually_exclusive_group()
    parser_list_lprint.add_argument("--nolabels", action="store_true", help="don't print labels")
    parser_list_lprint.add_argument("--shortlabels", action="store_true", help="print a short version of labels")
    parser_list.add_argument("--nocomments", action="store_true", help="don't print comment count")
    parser_list.set_defaults(func=self.list)

    parser_show = subparsers.add_parser("show")
    parser_show.add_argument("issueid", type=int)
    parser_show.add_argument("-b", "--browser", action="store_true", default=False)
    parser_show.set_defaults(func=self.show)

    parser_edit = subparsers.add_parser("edit")
    parser_edit.add_argument("issueid", type=int)
    parser_edit.add_argument("-t", "--title", type=str)
    parser_edit.add_argument("-b", "--body", type=str)
    parser_edit.add_argument("-a", "--assignee", type=str)
    parser_edit.add_argument("-s", "--state", type=str, choices=["open", "closed"], metavar="STATE")
    parser_edit.add_argument("-m", "--milestone", type=int)
    parser_edit.add_argument("-l", "--labels", type=str)
    parser_edit.set_defaults(func=self.edit)

    parser_open = subparsers.add_parser("open")
    parser_open.add_argument("issueid", type=int)
    parser_open.set_defaults(func=self.open)

    parser_close = subparsers.add_parser("close")
    parser_close.add_argument("issueid", type=int)
    parser_close.set_defaults(func=self.close)

    parser_assign = subparsers.add_parser("assign")
    parser_assign.add_argument("issueid", type=int)
    parser_assign.add_argument("assignee", nargs="?", type=str, default="")
    parser_assign_assignee = parser_assign.add_mutually_exclusive_group()
    parser_assign_assignee.add_argument("--none", dest="assignee", action="store_const", const="")
    if "username" in self.config:
      parser_assign_assignee.add_argument("--me", dest="assignee", action="store_const", const=self.config["username"])
    parser_assign.set_defaults(func=self.assign)

    parser_create = subparsers.add_parser("create")
    parser_create.add_argument("title", type=str)
    parser_create.add_argument("body", type=str, nargs="?", default="")
    parser_create.set_defaults(func=self.create)

    parser_comment = subparsers.add_parser("comment")
    parser_comment.add_argument("issueid", type=int)
    parser_comment.add_argument("comment", type=str)
    parser_comment.set_defaults(func=self.comment)

    parser_milestone = subparsers.add_parser("milestone")
    parser_milestone_state = parser_milestone.add_mutually_exclusive_group()
    parser_milestone_state.add_argument("-s", "--state", type=str, choices=["open", "closed", "all"], metavar="STATE", default="open")
    parser_milestone_state.add_argument("--closed", dest="state", action="store_const", const="closed")
    parser_milestone_state.add_argument("--all", dest="state", action="store_const", const="all")
    parser_milestone.set_defaults(func=self.milestone)

    parser_label = subparsers.add_parser("label")
    parser_label.set_defaults(func=self.label)

  def parse_args(self, args):
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
        self.log(2, "Couldn't connect to GitHub. Status Code: %i" % (r.status_code))

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
      self.log(2, "Couldn't connect to GitHub. Status Code: %i" % (r.status_code))

  def post_json(self, url, payload={}):
    url = "https://api.github.com/" + url

    if not "username" in self.config or not "password" in self.config:
      self.log(2, "You are not authorized to do that.")

    auth = (self.config["username"], self.config["password"])
    r = requests.post(url, auth=auth, data=json.dumps(payload))

    if r.status_code != 201:
      self.log(2, "Couldn't connect to GitHub. Status Code: %i" % (r.status_code))

    return r.json()

  def log(self, level, message):
    """ Outputs a log message. Levels: 0: Info, 1: Warning, 2: Error (quit) """
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

  def list(self, args):
    params = {}
    params["state"] = args.state
    if args.milestone:
      params["milestone"] = args.milestone
    if args.labels:
      params["labels"] = args.labels
    if args.assignee:
      params["assignee"] = args.assignee
    if args.creator:
      params["creator"] = args.creator

    if params["state"] == "all":
      heading = "All Issues for %s/%s" % (self.owner, self.repo)
    elif params["state"] == "open":
      heading = "Open Issues for %s/%s" % (self.owner, self.repo)
    else:
      heading = "Closed Issues for %s/%s" % (self.owner, self.repo)
    if "milestone" in params:
      heading += ", with milestone #%i" % (params["milestone"])
    if "labels" in params:
      heading += ", labeled %s" % (params["labels"])
    if "assignee" in params:
      heading += ", assigned to %s" % (params["assignee"])
    if "creator" in params:
      heading += ", created by %s" % (params["creator"])
    heading += ":"
    print(stylize(heading, fg=0x00FF00, bold=True))

    self.stop_event = threading.Event()
    thread = threading.Thread(target=self.spinner)
    thread.start()

    url = "repos/%s/%s/issues" % (self.owner, self.repo)
    issues = []
    params["per_page"] = 100
    for i in range(1,20):
      params["page"] = i
      last = self.get_json(url, params)
      if len(last) == 0:
        break
      issues += last
    self.stop_event.set()
    issues = list(map(lambda x: Issue(self, x), issues))

    if args.type == "issues":
      issues = list(filter(lambda x: not x.is_pr, issues))
    if args.type == "prs":
      issues = list(filter(lambda x: x.is_pr, issues))

    output = ""
    if len(issues) == 0:
      output = "No results."
    for issue in issues:
      output += issue.print_line(args.shortlabels, args.nolabels, args.nocomments)

    pager(output)

  def show(self, args):
    if args.browser:
      out = os.dup(1)
      os.close(1)
      os.open(os.devnull, os.O_RDWR)
      try:
        webbrowser.open("https://github.com/%s/%s/issues/%i" % (self.owner, self.repo, args.issueid), 2, True)
      finally:
        os.dup2(savout, 1)
        sys.exit()

    heading = "Issue #%i in %s/%s:" % (args.issueid, self.owner, self.repo)
    print(stylize(heading, fg=0x00FF00, bold=True))

    self.stop_event = threading.Event()
    thread = threading.Thread(target=self.spinner)
    thread.start()

    url = "repos/%s/%s/issues/%i" % (self.owner, self.repo, args.issueid)
    issue = self.get_json(url, {})
    url += "/comments"
    comments = self.get_json(url, {})
    self.stop_event.set()

    issue = Issue(self, issue, comments)

    pager(issue.print_detail())

  def edit(self, args):
    payload = {}
    if args.title:
      payload["title"] = args.title
    if args.body:
      payload["body"] = args.body
    if args.assignee:
      payload["assignee"] = args.assignee if args.assignee != "none" else ""
    if args.state:
      payload["state"] = args.state
    if args.milestone:
      payload["milestone"] = args.milestone
    if args.labels:
      payload["labels"] = args.labels
    if len(payload) == 0:
      nargs = self.parser.parse_args(["edit", "-h"])
      return nargs.func(nargs)

    self.stop_event = threading.Event()
    thread = threading.Thread(target=self.spinner)
    thread.start()

    url = "repos/%s/%s/issues/%i" % (self.owner, self.repo, args.issueid)
    self.patch_json(url, payload)
    self.stop_event.set()

    nargs = self.parser.parse_args(["show", str(args.issueid)])
    return nargs.func(nargs)

  def open(self, args):
    nargs = self.parser.parse_args(["edit", str(args.issueid), "-s", "open"])
    return nargs.func(nargs)

  def close(self, args):
    nargs = self.parser.parse_args(["edit", str(args.issueid), "-s", "closed"])
    return nargs.func(nargs)

  def assign(self, args):
    assignee = args.assignee
    if assignee == "":
      assignee = "none"
    nargs = self.parser.parse_args(["edit", str(args.issueid), "-a", assignee])
    return nargs.func(nargs)

  def create(self, args):
    self.stop_event = threading.Event()
    thread = threading.Thread(target=self.spinner)
    thread.start()

    url = "repos/%s/%s/issues" % (self.owner, self.repo)
    result = Issue(self, self.post_json(url, {"title": args.title, "body": args.body}))
    self.stop_event.set()

    nargs = self.parser.parse_args(["show", str(result.number)])
    return nargs.func(nargs)

  def comment(self, args):
    self.stop_event = threading.Event()
    thread = threading.Thread(target=self.spinner)
    thread.start()

    url = "repos/%s/%s/issues/%i/comments" % (self.owner, self.repo, args.issueid)
    self.post_json(url, {"body": args.comment})
    self.stop_event.set()

    nargs = self.parser.parse_args(["show", str(args.issueid)])
    return nargs.func(nargs)

  def milestone(self, args):
    if args.state == "all":
      heading = "All Milestones for %s/%s:" % (self.owner, self.repo)
    elif args.state == "open":
      heading = "Open Milestones for %s/%s:" % (self.owner, self.repo)
    else:
      heading = "Closed Milestones for %s/%s:" % (self.owner, self.repo)
    print(stylize(heading, fg=0x00FF00, bold=True))

    self.stop_event = threading.Event()
    thread = threading.Thread(target=self.spinner)
    thread.start()

    url = "repos/%s/%s/milestones" % (self.owner, self.repo)
    milestones = self.get_json(url, {"state": args.state, "per_page": 100})
    milestones = list(map(lambda x: Milestone(self, x), milestones))
    self.stop_event.set()

    output = ""
    if len(milestones) == 0:
      output = "No results."
    for milestone in milestones:
      output += milestone.print_line()

    pager(output)

  def label(self, args):
    print(stylize("Labels for %s/%s:" % (self.owner, self.repo), fg=0x00FF00, bold=True))

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
