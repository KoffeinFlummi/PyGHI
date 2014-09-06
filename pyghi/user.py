#!/usr/bin/env python3

from .helpers import *

class User:
  def __init__(self, master, data):
    self.master = master
    for key in data.keys():
      setattr(self, key, data[key])

  def print_name(self):
    return stylize(self.login, fg=0xFFFF00, bold=True)
