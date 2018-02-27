
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
parser.add_argument('linx', metavar='N', 
                    help='aspecifies path to BPM. Mandatory input.')           
args = parser.parse_args()

bpmdata = metaclass.twiss(args.linx)

plt.scatter(bpmdata.S, bpmdata.TUNEX, color='#A0A0FF',edgecolor="b")
plt.xlabel("s [m]")
plt.ylabel("Tune x")
plt.title("Estimated tune from FFT analysis")
plt.legend()

plt.show()