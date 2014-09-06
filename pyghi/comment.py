#!/usr/bin/env python3

from .user import User
from .helpers import *

class Comment:
  def __init__(self, master, data):
    self.master = master
    for key in data.keys():
      setattr(self, key, data[key])

    self.user = User(self.master, self.user)

  def print_detail(self):
    output = stylize("\n%s wrote %s:" % (self.user.print_name(), relative_time(self.created_at)), bold=True) + "\n"
    output += padding(self.body) + "\n"
    return output
