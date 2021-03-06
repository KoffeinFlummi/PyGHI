#!/usr/bin/env python3

import sys

from .label import Label
from .milestone import Milestone
from .user import User
from .comment import Comment
from .helpers import padding, stylize, relative_time

class Issue:
    def __init__(self, master, data, comments=[]):
        self.master = master
        for key in data.keys():
            setattr(self, key, data[key])

        if self.body == None:
            self.body = ""
        if self.body == "":
            self.body = "No description provided."

        self.user = User(self.master, self.user)
        if self.assignee != None:
            self.assignee = User(self.master, self.assignee)

        self.is_pr = "pull_request" in data

        if self.milestone != None:
            self.milestone = Milestone(self.master, self.milestone)
        self.comments = list(map(lambda x: Comment(self.master, x), comments))
        self.labels = list(map(lambda x: Label(self.master, x), self.labels))

    def print_line(self, shortlabels=False, nolabels=False, nocomments=False):
        number = stylize(("#" + str(self.number)).rjust(6), bold=True) + " "

        if self.state == "open":
            state = stylize(" O ", bg=0x00AA00) + " "
        else:
            state = stylize(" C ", bg=0xDD0000) + " "

        issuetype = stylize(" P ", bg=0xCC00CC) + " " if self.is_pr else ""
        
        name = self.title + " "
        
        labels = ""
        if shortlabels:
            labels = " ".join(list(map(
                lambda x: stylize(" ", bg=int(x.color, 16)),
                self.labels
            ))) + " "
        elif not nolabels:
            labels = " ".join(list(map(
                lambda x: x.print_name(),
                self.labels
            ))) + " "

        comments = ""
        if not nocomments:
            comments = "[%i %s]" % (
                len(self.comments),
                stylize("@", fg=0xFFFF00)
            )

        return "%s%s%s%s%s%s\n" % (
            number,
            state,
            issuetype,
            name,
            labels,
            comments
        )

    def print_detail(self):
        output = stylize(self.title, bold=True) + "\n"
        if self.state == "open":
            output += stylize(" Open ", bg=0x00AA00, bold=True) + " "
        else:
            output += stylize(" Closed ", bg=0xAA0000, bold=True) + " "
        output += "%s created this %s\n" % (
            self.user.print_name(),
            relative_time(self.created_at)
        )

        if self.milestone != None:
            milestone = self.milestone.progress_bar()
        else:
            milestone = "No milestone"

        if self.assignee != None:
            assignee = "Assigned to %s" % (self.assignee.print_name())
        else:
            assignee = "No assignee"
        
        output += "%s - %s\n" % (milestone, assignee)

        labels = " ".join(list(map(lambda x: x.print_name(), self.labels)))
        if len(self.labels) == 0:
            labels = "No labels"
        output += labels + "\n\n"

        output += padding(self.body) + "\n"

        if len(self.comments) == 1:
            output += "\n" + stylize("1 COMMENT", bold=True) + "\n"
        else:
            output += "\n" + stylize("%i COMMENTS" % (
                len(self.comments)
            ), bold=True) + "\n"

        for comment in self.comments:
            output += comment.print_detail()

        return output
