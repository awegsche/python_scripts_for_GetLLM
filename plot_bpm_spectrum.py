
import os
import sys
import contextlib
import argparse

sys.path.append("/home/awegsche/afspublic/workspace/Beta-Beat.src")
sys.path.append("/media/awegsche/HDD/workspace/GetLLMTest")

from Python_Classes4MAD import metaclass
from Utilities import tfs_file_writer
import numpy as np
from subprocess import Popen
from shutil import copyfile
from time import sleep

from Utilities.ADDbpmerror import convert_files
from math import sqrt
import re

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab


parser = argparse.ArgumentParser(description='Plots the spectrum of a given BPM from drive.')
#parser.add_argument('-b', dest='bpm', metavar='BPM.XY', help='specifies path to BPM. Mandatory input', default="")
parser.add_argument('bpm', metavar='N', 
                    help='aspecifies path to BPM. Mandatory input.')           
parser.add_argument('--out', dest="out" , metavar='N', type=str,
                    help='aspecifies path to BPM. Mandatory input.')           
args = parser.parse_args()

bpmdata = metaclass.twiss(args.bpm)
f, ax = plt.subplots(figsize=(7,3.5))
ax.set_yscale('log', nonposy='clip')
ax.set_xlim(-.4, .4)
ax.bar(bpmdata.FREQ, bpmdata.AMP, 2.0e-4, color='#A0A0FF',edgecolor="b")

f.savefig(args.out)

#plt.show()