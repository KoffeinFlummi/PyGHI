#!/usr/bin/env python3

import sys

from .label import Label
from .milestone import Milestone
from .user import User
from .comment import Comment
from .helpers import *

class Issue:
  def __init__(self, master, data, comments=[]):
    self.master = master
    for key in data.keys():
      setattr(self, key, data[key])

    self.user = User(self.master, self.user)
    if self.assignee != None:
      self.assignee = User(self.master, self.assignee)

    if not "pull_request" in data:
      self.pull_request = None
      self.is_pr = False
    else:
      self.is_pr = True

    self.comments = []
    for comment in comments:
      self.comments.append(Comment(self.master, comment))

    if self.milestone != None:
      self.milestone = Milestone(self.master, self.milestone)

    self.labels = []
    for label in data["labels"]:
      self.labels.append(Label(self.master, label))

  def print_line(self, shortlabels=False, nolabels=False, nocomments=False):
    number = stylize(("#" + str(self.number)).rjust(6), bold=True) + " "

    if self.state == "open":
      state = stylize(" O ", bg=0x00AA00) + " "
    else:
      state = stylize(" C ", bg=0xDD0000) + " "

    if self.pull_request != None:
      issuetype = stylize(" P ", bg=0xCC00CC) + " "
    else:
      issuetype = ""
    
    name = self.title + " "
    
    if not nolabels:
      if shortlabels:
        labels = " ".join(list(map(lambda x: stylize(" ", bg=int(x.color, 16)), self.labels))) + " "
      else:
        labels = " ".join(list(map(lambda x: x.print_name(), self.labels))) + " "
    else:
      labels = ""

    if nocomments:
      comments = ""
    else:
      comments = "[%i %s]" % (len(self.comments), stylize("@", fg=0xFFFF00))

    return "%s%s%s%s%s%s\n" % (number, state, issuetype, name, labels, comments)

  def print_detail(self):
    output = stylize(self.title, bold=True) + "\n"
    if self.state == "open":
      output += stylize(" Open ", bg=0x00AA00, bold=True) + " "
    else:
      output += stylize(" Closed ", bg=0xAA0000, bold=True) + " "
    output += "%s created this %s\n" % (self.user.print_name(), relative_time(self.created_at))

    if self.milestone != None:
      milestone = self.milestone.progress_bar()
    else:
      milestone = "No milestone"

    if self.assignee != None:
      assignee = "Assigned to %s" % (self.assignee.print_name())
    else:
      assignee = "No assignee"

    output += "%s - %s\n" % (milestone, assignee)

    if len(self.labels) > 0:
      labels = " ".join(list(map(lambda x: x.print_name(), self.labels)))
    else:
      labels = "No labels"
    output += labels + "\n\n"

    if self.body == None:
      self.body = ""
    if len(self.body) > 0:
      output += padding(self.body) + "\n"
    else:
      output += padding("No description provided.") + "\n"

    output += "\n" + stylize("%i %s" % (len(self.comments), "COMMENT" if len(self.comments) == 1 else "COMMENTS"), bold=True) + "\n"

    for comment in self.comments:
      output += comment.print_detail()

    return output
