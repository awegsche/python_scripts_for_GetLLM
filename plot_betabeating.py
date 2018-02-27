

''

import os
import sys
import contextlib
import argparse

sys.path.append("/home/awegsche/afspublic/workspace/Beta-Beat.src")
sys.path.append("/media/awegsche/HDD/workspace/GetLLMTest")

from Python_Classes4MAD import metaclass
from Utilities import tfs_file_writer
from Utilities import tfs_pandas
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

    
def write_Boolean(name, value):
    line = name
    for i in range(len(name), LEN):
        line += " "
    if value:
        print line + "\33[38;2;0;255;0mYES\33[0m"
    else:
        print line + "\33[38;2;255;0;0mNO\33[0m"

def write_String(name, value):
    line = name
    for i in range(len(name), LEN):
        line += " "
    print line + value
    
def plot_bb(getbetaxpath, label, ax1, mcolor, fcolor, linest):
        
    bb_file = metaclass.twiss(getbetaxpath)
    
    betabeating = []
    s = []
    err = []
    if args.use_yplane:
        for i in range(len(bb_file.BETY)):
            bb = (bb_file.BETY[i] / bb_file.BETYMDL[i] - 1.0) * 100.0
        
            if abs(bb) < args.cut:
                betabeating.append(bb)
                err.append(bb_file.ERRBETY[i] / bb_file.BETYMDL[i] * 100.0)
                s.append(bb_file.S[i])
          
    else:
        for i in range(len(bb_file.BETX)):
            bb = (bb_file.BETX[i] / bb_file.BETXMDL[i] - 1.0) * 100.0
        
            if abs(bb) < args.cut:
                betabeating.append(bb)
                err.append(bb_file.ERRBETX[i] / bb_file.BETXMDL[i] * 100.0)
                s.append(bb_file.S[i])
        
    
    # betabeating = (bb_file.BETX-bb_file.BETXMDL) / bb_file.BETXMDL * 100.0
    # err = (bb_file.ERRBETX) / bb_file.BETXMDL * 100.0
    rms = np.sqrt(np.mean(np.square(betabeating)))
    
    label1 = "{1:s}, rms = {0:7.3f}%".format(rms, label)
    label2 = "ncombinations"

    if plotmode == 0:
        ax2 = ax1.twinx()
        b = ax2.plot(bb_file.S, bb_file.NCOMBINATIONS, label=label2, c='g', alpha=.3)
        ax2.fill_between(bb_file.S, 0, bb_file.NCOMBINATIONS, facecolor='g', alpha=.15)
        ax2.set_ylim(0,150)
        ax2.set_ylabel("# combinations")
        ax2.yaxis.label.set_color('green')
        ax2.tick_params(axis='y', colors='green')
        
        
    a = ax1.errorbar(s, betabeating, err, label=label1, c=fcolor, markeredgecolor=mcolor, marker='o', markersize=3.0, fmt=linest)




# ----------------------------------------------------------------------------------------------




parser = argparse.ArgumentParser(description='Plots the betabeating from GetLLM.')
#
#parser.add_argument('-m', dest="create_the_model", action='store_true',
#                    help='the path to the input file')
#parser.add_argument('-g', dest="de_GetLLM", action='store_true',
#                    help='run GetLLM')
#                    
#parser.add_argument('-c', dest="use_centre", action='store_true',
#                    help='use center')
#
#parser.add_argument('-e', dest='errordefs', action='store_true',
#                    help='create errordefs')
parser.add_argument('-b', dest='getbetax', metavar='GETBETAX.out', help='specifies path to getbetax.out. Default is "getbetax.out"', default="getbetax.out")
parser.add_argument('--b2', dest='getbetax2', metavar='GETBETAX.out', help='specifies path to getbetax.out. Default is "getbetax.out"', default=None)
#parser.add_argument('-m', dest='model', metavar='MODEL.DAT', help='specifies path to the model twiss file. Default is "twiss.dat"', default="twiss.dat")
parser.add_argument('-p', dest='plot', metavar='MODE', help='specifies the plot mode.\n-1   Only beta beating\n 0   Betabeating with number of used combinations', default=-1,type=int)
parser.add_argument('--print', dest='printplt', metavar='FILENAME', help='should the plot be saved as jpg?', default="")
parser.add_argument('--ylim', dest='ylim', metavar='FLOAT', type=float, default=-1, help="limits of y axis in percent")
parser.add_argument('--label', dest='label', metavar='LABLE', default='N-BPM', help="label for the data, default=N-BPM")
parser.add_argument('--width', dest='width', metavar='WIDTH', default=20.0, type=float, help="the design width of the printed plot")
parser.add_argument('--cut', dest='cut', metavar='CUT', default=100.0, type=float, help="the maximal beta beating to be included in the calculation of the average, rms etc. Default = 100")
parser.add_argument('--accel', dest='accel', metavar='ACC', default="LHCB1", help="the maximal beta beating to be included in the calculation of the average, rms etc. Default = 100")
parser.add_argument('-Y', dest='use_yplane', action="store_true", help="plot vertical beta function")
parser.add_argument('-l', dest='linestyle', help="linestyle")
parser.add_argument('--label2', dest='label2', help="Label for the second plot")
parser.add_argument('--histogram', dest="histogram", action='store_true', help="prints an additional histogram of the errorbars")

args = parser.parse_args()

#modelpath = args.model
getbetaxpath = args.getbetax
plotmode = args.plot
printplot = (args.printplt != "")

print "\33[38;2;0;255;200m- - - INFO: - - -\33[0m"

#write_String("model", modelpath)
write_String("getbetax.out", getbetaxpath)
write_Boolean("print to pdf", printplot)

print "\33[38;2;0;255;200m- - - - - - - - -\33[0m"

#model = metaclass.twiss(modelpath)

    
# rc('font', **{'family': 'sans-serif', 'serif': ['Computer Modern']})
# params = {'backend': 'pdf',
#           'axes.labelsize': 16,
#           'font.size': 16,
#           'axes.titlesize': 16,
#           'legend.fontsize': 16,
#           'xtick.labelsize': 16,
#           'ytick.labelsize': 16,
#           'text.usetex': False,
#           'axes.unicode_minus': True,
#           'xtick.major.pad': 12,
#           'ytick.major.pad': 12,
#           'xtick.minor.pad': 12,
#           'ytick.minor.pad': 12
#
#           }
# matplotlib.rcParams.update(params)

plt.rc('text', usetex=True)
plt.rc('font', family='serif')
plt.rc('legend', fontsize=12)

print "backend =", matplotlib.get_backend()

width = args.width
height = width * 0.5
f, ax1 = plt.subplots(figsize=(width, height))


if args.use_yplane:
    plane = "Y"
else:
    plane = "X"

mcolor = 'b'
fcolor = '#A0A0FF'

if args.label == "3-BPM":
    mcolor='r'
    fcolor='#FFA0A0'

        
if args.getbetax2 is None:
    plot_bb(getbetaxpath, args.label, ax1, mcolor, fcolor, args.linestyle)
else:
    
    plot_bb(args.getbetax2, args.label, ax1, 'b', '#A0A0FF', args.linestyle)
    plot_bb(getbetaxpath, args.label2, ax1, 'r', '#FFA0A0', args.linestyle)

ax1.set_ylabel(r"$\Delta \beta/ \beta$")

if args.accel == "JPARC":
    ax1.set_xlim(0, 1600)
elif args.accel == "PETRA":
    ax1.set_xlim(0, 2350)
else:
    ax1.set_xlim(0,27000)
if args.ylim != -1:
    ax1.set_ylim(-args.ylim, args.ylim)
    


#plt.title("BetaBeating")
ax1.set_xlabel("$s$ [m]")

if plotmode == 0:
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
               ncol=2, mode="expand", borderaxespad=0.,handles=[a,b], labels=[label1, label2])
else:
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
               ncol=2, mode="expand", borderaxespad=0.)
    
    
    
plt.tight_layout(rect=(.02,0,1,.9))


print "\n- - - - - - - - - - - - - - - - - -"
print "- - - - Plotting Beta Beating - - -"
print "- \33[38;2;200;200;200msummary\33[0m:"
print "- "
#print "- rms ich BetaBeating = {0:9.5f}".format(rms)
print "- "
f.show()

if printplot:
    

    
    #plt.title(r"$\beta$ Beating")
    plt.xlabel("$s \; [m]$")
    ax1.set_ylabel(r'$ \Delta \beta/ \beta \; [\%]$')
    #plt.axes().set_aspect(aspect=150)
    #ax1.set_aspect(1.50)
    #ax2.set_aspect(1.50)
    
    plt.savefig(args.printplt)

    
if args.histogram:
    g, ax1 = plt.subplots(figsize=(width*.65, height*.65))
    
    getbetax = tfs_pandas.read_tfs(getbetaxpath)
    
    mybins = np.arange(0, 10, .25)
    
    ax1.hist(getbetax["ERRBET{:s}".format(plane)] / getbetax["BET{:s}MDL".format(plane)] * 100.0, mybins, color='#A0A0FF', edgecolor='#0000FF')
    plt.xlabel(r"size of errorbar$ \; [\%]$")
    ax1.set_ylabel(r'count')
    plt.tight_layout()
    
    plt.savefig(args.printplt.replace(".pdf", "_hist.pdf"))
    
    g.show()
    
raw_input()
#plotScatterX(outputich, output3bpm, twisserr)
