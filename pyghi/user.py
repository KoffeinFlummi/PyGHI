#!/usr/bin/env python3

from .helpers import stylize

class User:
    """ Class holding methods to format GH user information. """
    def __init__(self, master, data):
        self.master = master
        for key in data.keys():
            setattr(self, key, data[key])

    def print_name(self):
        """ Prints the coloured name of the user. """
        return stylize(self.login, fg=0xFFFF00, bold=True)
