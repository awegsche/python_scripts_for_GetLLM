#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  7 11:46:32 2017

@author: awegsche
"""


import os
import sys
import contextlib
import argparse
import stat

sys.path.append("/afs/cern.ch/work/a/awegsche/public/workspace/Beta-Beat.src")

from Utilities import tfs_pandas as tfs
import numpy as np
from subprocess import Popen
from shutil import copyfile
from time import sleep

from Utilities.ADDbpmerror import convert_files
from math import sqrt
import re
from matplotlib import rc

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib
import pandas

BW = False

if BW:
    from Utilities.progressbar import startProgressBW as startProgress, progressBW as progress, endProgressBW as endProgress
else:
    from Utilities.progressbar import startProgress, progress, endProgress, printStep, startTime, stopPrint
    
LEN = 20


# =============================================================================
# ======== function definitions ===============================================
# =============================================================================

resultspath = "/user/slops/data/LHC_DATA/OP_DATA/Betabeat/"

list_dir = os.listdir(resultspath)

logfile = open("/afs/cern.ch/work/a/awegsche/public/CCC_postprocessing/results", "w")

for d in list_dir:
    
    if  d.startswith("2017"):
        print d
        
        walked = os.walk(resultspath + d)
        
        for tripl in walked:
            
            if "getbetax_free.out" in tripl[2]:
                
                getbetax = tfs.read_tfs(tripl[0] + "/getbetax_free.out" )
                
                logfile.write(tripl[0] + "; " + getbetax.headers["Command"] + "; nothng\n")
                
                
                print "\33[38;2;255;0;0m", tripl[0], "\33[0m"
logfile.close()

#print os.walk(resultspath)