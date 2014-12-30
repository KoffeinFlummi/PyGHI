#!/usr/bin/env python3

import os
import sys
import time
import datetime
import pydoc
import shlex
import struct
import platform
import functools

if platform.system() != "Windows":
    import xtermcolor

def pager(text):
    """ Outputs large text via pager if terminal isn't high enough. """
    cols, rows = get_terminal_size()

    while text[-1] == "\n":
        text = text[:-1]

    try:
      import pymoji
      text = pymoji.replaceAliases(text, 1)
    except ImportError:
      pass

    if len(text.split("\n")) > rows - 1:
        try:
            pydoc.pipepager(text, cmd="less -R")
        except:
            print(text)
    else:
        print(text)

def stylize(text, fg=None, bg=None, bold=False):
    """ Stylizes given text and, if necessary, calculates proper FG colour. """
    if bold:
        text = "\033[1m" + text + "\033[0m"

    # No foreground colour defined, guess one from BG
    if fg == None and bg != None:
        hexstring = str(hex(bg))[2:].rjust(6, "0")
        r = int(hexstring[0:2], 16)
        g = int(hexstring[2:4], 16)
        b = int(hexstring[4:6], 16)
        # Credit: http://alienryderflex.com/hsp.html
        brightness = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        fg = 0x000000 if brightness > 0.5 else 0xFFFFFF

    if platform.system() == "Windows":
        return _stylize_windows(text, fg, bg)
    else:
        return _stylize_unix(text, fg, bg)

def _stylize_windows(text, fg, bg):
    if fg != None:
        fg_ansi, fg_reset = _rgb_to_ansi(fg)
        if bg != None:
            bg_ansi, bg_reset = _rgb_to_ansi(bg, True)
            return bg_ansi + fg_ansi + text + fg_reset + bg_reset
        return fg_ansi + text + fg_reset

    return text

def _stylize_unix(text, fg, bg):
    if bg != None:
        return xtermcolor.colorize(text, rgb=fg, bg=bg)
    if fg != None:
        return xtermcolor.colorize(text, rgb=fg)
    return text

# SOURCE:
# https://mail.python.org/pipermail/python-list/2008-December/482381.html
def _rgb_to_ansi(rgb, bg=False):
    """ For shitty Windows systems we have to manually convert things. """
    if bg:
        ansi_colours = {
            0x000000: "\33[40m",
            0xFF0000: "\33[41m",
            0x00FF00: "\33[42m",
            0xFFFF00: "\33[43m",
            0x0000FF: "\33[44m",
            0xFF00FF: "\33[45m",
            0x00FFFF: "\33[46m",
            0xFFFFFF: "\33[47m",
        }
        reset = "\33[49m"
    else:
        ansi_colours = {
            0x000000: "\33[30m",
            0xFF0000: "\33[31m",
            0x00FF00: "\33[32m",
            0xFFFF00: "\33[33m",
            0x0000FF: "\33[34m",
            0xFF00FF: "\33[35m",
            0x00FFFF: "\33[36m",
            0xFFFFFF: "\33[37m",
        }
        reset = "\33[39m"

    closest_match = min(ansi_colours, key=functools.partial(_euclidian, rgb))
    return ansi_colours[closest_match], reset

def _to_rgb(color):
    return (color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF

def _euclidian(c1, c2):
    r, g, b = _to_rgb(c1)
    s, h, c = _to_rgb(c2)
    r -= s
    g -= h
    b -= c
    return r*r+g*g+b*b

def padding(text, width=2):
    """ Pads a text. (duh) """
    cols, rows = get_terminal_size()
    result = ""
    lines = text.split("\n")

    for line in lines:
        if len(line) < cols - width*2:
            result += " "*width + line + "\n"
        else:
            words = line.split(" ")
            printwords = []
            for word in words:
                nextlen = len(" ".join(printwords)) + len(word) + 1
                if len(printwords) > 0 and nextlen > cols - width*2:
                    result += " "*width + " ".join(printwords) + "\n"
                    printwords = [word]
                else:
                    printwords.append(word)
            if len(printwords) > 0:
                result += " "*width + " ".join(printwords) + "\n"

    return result[:-1]

def relative_time(timestring):
    """ Converts a timestring to a relative time. """

    timeob = datetime.datetime.strptime(timestring, "%Y-%m-%dT%H:%M:%SZ")
    diff = datetime.datetime.utcnow() - timeob

    seconds = diff.seconds
    minutes = int(seconds / 60)
    hours = int(minutes / 60)
    days = diff.days

    if days > 30:
        return timeob.strftime("on %Y-%m-%d")
    if days > 0:
        return "%i %s ago" % (days, "day" if days == 1 else "days")
    if hours > 0:
        return "%i %s ago" % (hours, "hour" if hours == 1 else "hours")
    if minutes > 0:
        return "%i %s ago" % (minutes, "minute" if minutes == 1 else "minutes")
    if seconds > 10:
        return "%i %s ago" % (seconds, "second" if seconds == 1 else "seconds")

    return "just now"


# SOURCE OF THE FOLLOWING 4 FUNCTIONS:
# https://gist.github.com/jtriley/1108174
# Edited by KoffeinFlummi

def get_terminal_size():
    """ getTerminalSize()
     - get width and height of console
     - works on linux,os x,windows,cygwin(windows)
     originally retrieved from:
     http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
    """
    current_os = platform.system()
    tuple_xy = None
    if current_os == 'Windows':
        tuple_xy = _get_terminal_size_windows()
        return tuple_xy if tuple_xy != None else _get_terminal_size_tput()
    if current_os in ['Linux', 'Darwin'] or current_os.startswith('CYGWIN'):
        return _get_terminal_size_linux()
    return (80, 25)

def _get_terminal_size_windows():
    try:
        from ctypes import windll, create_string_buffer
        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
            (bufx, bufy, curx, cury, wattr,
             left, top, right, bottom,
             maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            sizex = right - left + 1
            sizey = bottom - top + 1
            return sizex, sizey
    except:
        pass

def _get_terminal_size_tput():
    # get terminal width
    # src: http://stackoverflow.com/questions/263890/how-do-i-find-the-width-height-of-a-terminal-window
    try:
        cols = int(subprocess.check_call(shlex.split('tput cols')))
        rows = int(subprocess.check_call(shlex.split('tput lines')))
        return (cols, rows)
    except:
        pass

def _get_terminal_size_linux():
    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            cr = struct.unpack(
                'hh',
                fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234')
            )
            return cr
        except:
            pass
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (os.environ['LINES'], os.environ['COLUMNS'])
        except:
            return None
    return int(cr[1]), int(cr[0])
