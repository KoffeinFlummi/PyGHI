#!/usr/bin/env python3

import os
import sys
import platform
from setuptools import setup, find_packages

def read(fname):
  return open(os.path.join(os.path.dirname(__file__), fname)).read()

requirements = ["requests>=2.4.0"]
if platform.system() == "Windows":
  requirements.append("colorama>=0.3.2")
else:
  requirements.append("xtermcolor>=1.2.1")

setup(
  name = "PyGHI",
  version = "1.0",
  packages = ["pyghi_cli"],
  scripts = ["scripts/pyghi"],
  install_requires = requirements,

  author = "Felix \"KoffeinFlummi\" Wiegand",
  author_email = "koffeinflummi@gmail.com",
  description = "A CLI for GitHub Issues.",
  long_description = read("README.md"),
  license = "MIT",
  keywords = "git github issues cli",
  url = "https://github.com/KoffeinFlummi/PyGHI",
  classifiers=[
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Natural Language :: English",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.0",
    "Programming Language :: Python :: 3.1",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Topic :: Terminals :: Terminal Emulators/X Terminals",
    "Topic :: Utilities"
  ]
)
