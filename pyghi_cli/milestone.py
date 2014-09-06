#!/usr/bin/env python3

from .helpers import stylize

class Milestone:
    """ Class holding various methods to format GH milestone information. """
    def __init__(self, master, data):
        self.master = master
        for key in data.keys():
            setattr(self, key, data[key])

    def progress_bar(self):
        """ Returns a string containing a progress bar for the milestone. """
        completed = self.closed_issues
        total = self.closed_issues + self.open_issues
        progressbar = stylize("[", bold=True)
        percentage = int(round((completed / total) * 100)) if total != 0 else 0

        stringleft = self.title
        stringright = "%i%s (%i/%i)" % (percentage, "%", completed, total)
        stringleft = stringleft.ljust(int(14))
        stringright = stringright.rjust(int(14))
        string = " %s%s " % (stringleft, stringright)

        pointer = int(30 * completed/total) if total != 0 else 0
        filled = stylize(string[:pointer], bg=0x00DD00)
        unfilled = string[pointer:]

        return progressbar + filled + unfilled + stylize("]", bold=True)

    def print_line(self):
        """ Returns a one-line summary of the milestone. """
        number = stylize(("#" + str(self.number)).rjust(4), bold=True) + " "

        if self.state == "open":
            state = stylize(" O ", fg=0xFFFFFF, bg=0x00AA00) + " "
        else:
            state = stylize(" C ", fg=0xFFFFFF, bg=0xDD0000) + " "

        progress = self.progress_bar()

        return "%s%s%s\n" % (number, state, progress)
