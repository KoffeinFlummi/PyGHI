import os
import sys
import subprocess
import string
import random

def randomstring(size=6, chars=string.ascii_uppercase + string.digits):
    # SOURCE: http://stackoverflow.com/a/2257449/3497501
    return ''.join(random.choice(chars) for _ in range(size))

writeaccess = True
testargs = [
    ["pyghi", "list"],
    ["pyghi", "list", "-a", "KoffeinFlummi", "-m", "1"],
    ["pyghi", "list", "-c", "KoffeinFlummi", "--shortlabels"],
    ["pyghi", "list", "--nocomments", "--nolabels"],
    ["pyghi", "show", "1"],
    ["pyghi", "milestone"],
    ["pyghi", "milestone", "--closed"],
    ["pyghi", "label"]
]
if writeaccess:
    testargs.append(["pyghi", "edit", "1", "-t", "Testing Issue %s" % (randomstring())])
    testargs.append(["pyghi", "edit", "1", "-b", randomstring()])
    testargs.append(["pyghi", "open", "1"])
    testargs.append(["pyghi", "close", "1"])
    testargs.append(["pyghi", "assign", "--none"])
    testargs.append(["pyghi", "assign", "--me"])
    testargs.append(["pyghi", "comment", "1", randomstring()])

total = len(testargs) - 1
for i in range(len(testargs)):
    testarg = testargs[i]
    name = " ".join(testarg)
    print("Testing %i/%i: %s ..." % (i, total, name), end=" ")

    try:
        assert(subprocess.call(testarg, stdout=subprocess.PIPE) == 0)
    except:
        raise
        print("FAILED.")
        sys.exit(1)
    else:
        print("done.")

print("\nAll %i tests successfully completed." % (total))
