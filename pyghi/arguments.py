#!/usr/bin/env python3

import argparse

def add_arguments(master):
  master.parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=20))
  subparsers = master.parser.add_subparsers()

  parser_list = subparsers.add_parser("list", formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50), description="List issues for the repo")
  parser_list_state = parser_list.add_mutually_exclusive_group()
  parser_list_state.add_argument("-s", "--state", type=str, choices=["open", "closed", "all"], metavar="STATE", default="open", help="show issues of this state")
  parser_list_state.add_argument("--closed", dest="state", action="store_const", const="closed", help="show closed issues")
  parser_list_state.add_argument("--all", dest="state", action="store_const", const="all", help="show both closed and open issues")
  parser_list.add_argument("-m", "--milestone", type=int, help="show issues with this milestone ID")
  parser_list.add_argument("-l", "--labels", type=str, help="show issues with these labels (comma-seperated list)")
  parser_list_labels = parser_list.add_mutually_exclusive_group()
  parser_list_labels.add_argument("-a", "--assignee", type=str, help="show issues assigned to this user")
  if "username" in master.config:
    parser_list_labels.add_argument("--mine", dest="assignee", action="store_const", const=master.config["username"], help="show issues assigned to you")
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
  parser_list.set_defaults(func=master.list)

  parser_show = subparsers.add_parser("show", description="Show a specific issue")
  parser_show.add_argument("issueid", type=int)
  parser_show.add_argument("-b", "--browser", action="store_true", default=False)
  parser_show.set_defaults(func=master.show)

  parser_edit = subparsers.add_parser("edit", description="Edit an issue")
  parser_edit.add_argument("issueid", type=int)
  parser_edit.add_argument("-t", "--title", type=str)
  parser_edit.add_argument("-b", "--body", type=str)
  parser_edit.add_argument("-a", "--assignee", type=str)
  parser_edit.add_argument("-s", "--state", type=str, choices=["open", "closed"], metavar="STATE")
  parser_edit.add_argument("-m", "--milestone", type=int)
  parser_edit.add_argument("-l", "--labels", type=str)
  parser_edit.set_defaults(func=master.edit)

  parser_open = subparsers.add_parser("open", description="(Re)Open an issue")
  parser_open.add_argument("issueid", type=int)
  parser_open.set_defaults(func=master.open)

  parser_close = subparsers.add_parser("close", description="Close an issue")
  parser_close.add_argument("issueid", type=int)
  parser_close.set_defaults(func=master.close)

  parser_assign = subparsers.add_parser("assign", description="(Re)Assign an issue")
  parser_assign.add_argument("issueid", type=int)
  parser_assign.add_argument("assignee", nargs="?", type=str, default="")
  parser_assign_assignee = parser_assign.add_mutually_exclusive_group()
  parser_assign_assignee.add_argument("--none", dest="assignee", action="store_const", const="")
  if "username" in master.config:
    parser_assign_assignee.add_argument("--me", dest="assignee", action="store_const", const=master.config["username"])
  parser_assign.set_defaults(func=master.assign)

  parser_create = subparsers.add_parser("create", description="Create an issue")
  parser_create.add_argument("title", type=str)
  parser_create.add_argument("body", type=str, nargs="?", default="")
  parser_create.set_defaults(func=master.create)

  parser_comment = subparsers.add_parser("comment", description="Comment on an issue")
  parser_comment.add_argument("issueid", type=int)
  parser_comment.add_argument("comment", type=str)
  parser_comment.set_defaults(func=master.comment)

  parser_milestone = subparsers.add_parser("milestone", description="List milestones for the repo")
  parser_milestone_state = parser_milestone.add_mutually_exclusive_group()
  parser_milestone_state.add_argument("-s", "--state", type=str, choices=["open", "closed", "all"], metavar="STATE", default="open")
  parser_milestone_state.add_argument("--closed", dest="state", action="store_const", const="closed")
  parser_milestone_state.add_argument("--all", dest="state", action="store_const", const="all")
  parser_milestone.set_defaults(func=master.milestone)

  parser_label = subparsers.add_parser("label", description="List labels for the repo")
  parser_label.set_defaults(func=master.label)
