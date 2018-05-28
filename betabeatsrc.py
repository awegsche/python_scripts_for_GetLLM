import os
import sys

P_MYGETLLM = "/media/awegsche/HDD/CernBox/MyBeta-Beat.src/Beta-Beat.src"

BETABEATPATH = P_MYGETLLM

print "SYS IMPORT '{}'".format(BETABEATPATH)
if not BETABEATPATH in sys.path:
    sys.path.append(BETABEATPATH)

