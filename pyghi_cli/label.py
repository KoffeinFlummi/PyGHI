#!/usr/bin/env python3

from .helpers import stylize

class Label:
    """ A class holding various methods for formatting GH Label information. """
    def __init__(self, master, data):
        self.master = master
        for key in data.keys():
            setattr(self, key, data[key])

    def print_line(self):
        """ Prints a line summary of the label. """
        name = stylize(self.name, bold=True).ljust(30)
        colour = stylize(
            " #%s " % (self.color.upper()),
            bg=int(self.color, 16)
        )

        return "%s%s\n" % (name, colour)

    def print_name(self):
        """ Prints the coloured name of the label. """
        return stylize(" %s " % (self.name), bg=int(self.color, 16))
