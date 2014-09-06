PyGHI
=====

[![Build Status](http://img.shields.io/travis/KoffeinFlummi/PyGHI.svg)](https://travis-ci.org/KoffeinFlummi/PyGHI) ![License](http://img.shields.io/badge/license-MIT-red.svg)

Use your console to access GitHub issues!

All credit for the original idea goes to @stephencelis. His repository can be found here:  
https://github.com/stephencelis/ghi

![List View](http://i.imgur.com/7e08yuI.png)
![Show View](http://i.imgur.com/tjwvYux.png)

Works on both Linux and Windows (at least in the git bash), although not nearly as pretty:

![Ugly Windows](http://i.imgur.com/P2VuXDk.png)

### Setup

```
sudo python3 setup.py install
```

**Requirements**:
- [requests](https://github.com/kennethreitz/requests)
- [colorama](https://github.com/tartley/colorama) - *if you're on Windows*
- [xtermcolor](https://github.com/broadinstitute/xtermcolor) - *if you're not*


### Usage

```
pyghi [command] [options]
```

Type `pyghi --help` to get a list of all commands and `pyghi [command] --help` to get help for that command.
