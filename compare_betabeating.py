import os
import sys
import contextlib
import argparse
import stat


sys.path.append("/home/awegsche/Beta-Beat.src/")

from utils import tfs_pandas as tfs
import numpy as np
from subprocess import Popen
from shutil import copyfile
from time import sleep

from utils.ADDbpmerror import convert_files
from utils import logging_tools
from math import sqrt
import re
from matplotlib import rc

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib
import pandas as pd

BW = False
LEN = 20

LOG = logging_tools.get_logger(__name__, level_console=DEBUG)

# =============================================================================
# ======== function definitions ===============================================
# =============================================================================

def write_Boolean(name, value):
    line = name
    for i in range(len(name), LEN):
        line += " "
    if value:
        LOG.info( line + "\33[38;2;0;255;0mYES\33[0m")
    else:
        LOG.info(line + "\33[38;2;255;0;0mNO\33[0m")

def write_String(name, value):
    line = name
    for i in range(len(name), LEN):
        line += " "
    LOG.info(line + value)

def make_cmdline_argument(argument):
    if " " in argument:
        return "'" + argument + "'"
    return argument

def make_bar(value, maxvalue=100):
    return "".join(["#"] * int(value/maxvalue*300))

OMC_LOGO = """
     ######    ##L          ##      ######
   d##   ##b   ###L        ###    ####   ##
  ###     ###  ####L      ####  ###
  ##       ##  ## ##L    ## ##  ##
  ###     ###  ##  ##L  ##  ##  ###
   T##_  ##P   ##   ##L##   ##    ###
     #####     ##    ###    ##      ######
"""


# =============================================================================
# ======== argparse initialization ============================================
# =============================================================================

# retrieve the command line for reuse
cmdline = " ".join([make_cmdline_argument(x) for x in sys.argv])

parser = argparse.ArgumentParser(description='Plots the betabeating from GetLLM.')
subparsers = parser.add_subparsers(help='sub-command help', title="submodules")

parser_omc = subparsers.add_parser(
    'omc',
    help=('OMC style plots? LHC interaction regions will be labelled between the x and y plots.'
          'They share the same x-axis and the legend is placed within one of them.')

parser_histo = subparsers.add_parser('histo', help='Histogram of error bars.')
parser_reveal = subparsers.add_parser('reveal', help='Create data points for reveal.js slides')


parser.add_argument('--bet1', dest='getbetax', default=None, metavar='OUTPUTDIR',
                    help='specifies the folder that contains getbetax.out. "')

parser.add_argument('--bet2', dest='getbetax2', default=None, metavar='OUTPUTDIR',
                    help='specifies the folder that contains getbetax.out. "')

parser.add_argument('--label1', dest='label1', metavar='LABLE', default='N-BPM',
                    help="label for the data, default=N-BPM")

parser.add_argument('--label2', dest='label2', metavar='LABLE', default='N-BPM',
                    help="label for the data, default=N-BPM")

parser.add_argument('-p', dest='plot', metavar='MODE',
                    help='specifies the plot mode.\n-1   Only beta beating\n 0   Betabeating with number of used combinations', default=-1,type=int)

parser.add_argument('--print', dest='printplt', metavar='FILENAME',
                    help='should the plot be saved as jpg?', default="")

parser.add_argument('--ylim', dest='ylim', metavar='FLOAT', type=float, default=-1,
                    help="limits of y axis in percent")

parser.add_argument('--absolut', dest='absolut', action="store_true",
                    help="instead of beta beating, print the absolute beta")

parser.add_argument('--width', dest='width', metavar='WIDTH', default=20.0, type=float,
                    help="the design width of the printed plot")

parser.add_argument('--height', dest='height', metavar='HEIGHT', default=None, type=float,
                    help="the design height of the printed plot")

parser.add_argument('--nolegend', dest='legend', action="store_false", help="if set, no legend will be printed")
parser.add_argument('--cut', dest='cut', metavar='CUT', default=100.0, type=float, help="the maximal beta beating to be included in the calculation of the average, rms etc. Default = 100")
parser.add_argument('--zoom', dest='zoom', metavar='MIN,MAX', default=None, help="zooms to a certain xrange.")
parser.add_argument('--accel', dest='accel', metavar='ACC', default="LHCB1", help="the maximal beta beating to be included in the calculation of the average, rms etc. Default = 100")
parser.add_argument('--noY', dest='use_yplane', action="store_false", help="plot vertical beta function")
parser.add_argument('-m', dest='model', default=None, help="path to the model")
parser.add_argument('-b', dest='lhcbeam', default="LHCB1", type=str, help="which beam (LHCB1/LHCB2)")
parser.add_argument('--withoutcomp', dest='without_compensation', action='store_true', help="use the uncompensated files")
parser.add_argument('--tex', dest='use_advanced_tex', action='store_true', help="use advanced LaTeX")
parser.add_argument('-l', dest='lines', action='store_true', help='draw lines between plot points')
parser.set_defaults(omcstyle=False)
parser.set_defaults(errhisto=False)
parser.set_defaults(bb_plot=True)

parser_omc.set_defaults(omcstyle=True)
parser_omc.set_defaults(bb_plot=True)
parser_omc.set_defaults(output_pickle=False)
parser_omc.add_argument('--loc', dest='loc', default=1, type=int, help="Location of the legend. 1=plot 1, 2=plot2")
parser_omc.add_argument('--title', dest='omctitle', default=None, type=str, help="optional title in the top right corner of the plot")
parser_omc.add_argument('--noIPbars', dest='ipbars', action='store_false', help="suppress drawing of the IP vertical bars")

parser_histo.set_defaults(errhisto=False)
parser_histo.set_defaults(bb_plot=False)
parser_histo.set_defaults(output_pickle=False)
parser_histo.add_argument('--xlim', dest='xlim', metavar='FLOAT', type=float, default=4, help="limits of x axis in percent")
parser_histo.add_argument('--title', dest='omctitle', default=None, type=str, help="optional title in the top right corner of the plot")

parser_reveal.set_defaults(errhisto=False)
parser_reveal.set_defaults(bb_plot=False)
parser_reveal.set_defaults(output_pickle=True)
parser_reveal.add_argument('--output', dest='outputpath', metavar='PATH', type=str, default=None, help="sets the output path for the pickle dictionary")




parser_histo.add_argument('--histmax', dest='histmax', type=float, default=None, help="xrange for histogram")
args = parser.parse_args()

if args.getbetax == None:
    print "No betabeating [1] given. Please do so with the flag --bet1 PATH"
    sys.exit(1)

#modelpath = args.model
getbetaxpath = args.getbetax
plotmode = args.plot
printplot = (args.printplt != "")

print "\33[38;2;0;255;200m- - - INFO: - - -\33[0m"

#write_String("model", modelpath)
write_String("getbetax.out", getbetaxpath)
write_Boolean("print to pdf", printplot)

print "\33[38;2;0;255;200m- - - - - - - - -\33[0m"

plt.rc('text', usetex=True)
if args.omcstyle:
    plt.rc('font', family='sans-serif')
    plt.rc('xtick.major', pad=6)

else:
    plt.rc('font', family='serif')
plt.rc('axes', labelsize=16)
plt.rc('xtick', labelsize=16)
plt.rc('ytick', labelsize=16)
plt.rc('legend', fontsize=16)
if args.use_advanced_tex:
    plt.rc("text.latex", preamble=[
                                   r'\usepackage{siunitx}',
#                                   r'\usepackage{helvetica}',
#                                   r'\usepackage{sansmath}',
#                                   r'\sansmath'
                                   ])

width = args.width
if args.height is not None:
    height = args.height
else:
    height = width * .8


if args.use_yplane:
    f, [ax1,ax2] = plt.subplots(nrows=2, figsize=(width, height))
else:
    f, ax1 = plt.subplots(nrows=1, figsize=(width, height * .6))

# =============================================================================
# ======== setting up getllm output paths and loading files ===================
# =============================================================================

# check the paths. is getbetax_free.out there? 
termination = "_free.out"
if args.without_compensation:
    termination = ".out"
if os.path.isdir(args.getbetax):
    bet1xpath = args.getbetax + "/getbetax" + termination
    bet1ypath = args.getbetax + "/getbetay" + termination
else:
    bet1xpath = args.getbetax
    bet1ypath = args.getbetax.replace("betax", "betay")

if args.getbetax2 is not None:    
    if os.path.isdir(args.getbetax2):
        bet2xpath = args.getbetax2 + "/getbetax" + termination
        bet2ypath = args.getbetax2 + "/getbetay" + termination
    else:
        bet2xpath = args.getbetax2
        bet2ypath = args.getbetax2.replace("betax", "betay")
    bb_file_x2 = tfs.read_tfs(bet2xpath)
    
    if args.use_yplane:
        bb_file_y2 = tfs.read_tfs(bet2ypath)
    else:
        bb_file_y2 = pd.DataFrame(columns=["NAME","S", "BETY", "ERRBETY", "BETYMDL"], data=[["BPM0", 0, 100, 0, 100], ["BPM1", 1, 100, 0, 100]] )

bb_file_x1 = tfs.read_tfs(bet1xpath)
if args.use_yplane:
    bb_file_y1 = tfs.read_tfs(bet1ypath)
else:
    bb_file_y1 = pd.DataFrame(columns=["NAME", "S", "BETY", "ERRBETY", "BETYMDL"], data=[["BPM0", 0, 100, 0, 100], ["BPM1", 1, 100, 0, 100]])
if args.model is not None:
    bmodel = tfs.read_tfs(args.model)
    bmodel = bmodel.rename(columns={"BETX": "BETXMDL", "BETY": "BETYMDL"})
    
bb_file_x1 = bb_file_x1.rename(columns={"BETX": "BETX1", "ERRBETX": "ERRBETX1", "BETXMDL": "BETXMDL1"})
bb_file_y1 = bb_file_y1.rename(columns={"BETY": "BETY1", "ERRBETY": "ERRBETY1", "BETYMDL": "BETYMDL1"})

if args.getbetax2 is not None:
    bb_file_x2 = bb_file_x2.rename(columns={"BETX": "BETX2", "ERRBETX": "ERRBETX2", "BETXMDL": "BETXMDL2"})
    bb_file_y2 = bb_file_y2.rename(columns={"BETY": "BETY2", "ERRBETY": "ERRBETY2", "BETYMDL": "BETYMDL2"})


betabeating_ = pd.merge(bb_file_x1, bb_file_y1[["NAME", "BETY1", "ERRBETY1", "BETYMDL1"]], on="NAME", how="outer")
if args.getbetax2 is not None:
    betabeating_ = pd.merge(betabeating_, bb_file_x2[["NAME", "BETX2", "ERRBETX2", "BETXMDL2"]], on="NAME", how="outer")
    betabeating_ = pd.merge(betabeating_, bb_file_y2[["NAME", "BETY2", "ERRBETY2", "BETYMDL2"]], on="NAME", how="outer")


# =============================================================================
# ======== calculating beta beating and error bars ============================
# =============================================================================


betabeating = betabeating_["BETX1"]/betabeating_["BETXMDL1"]*100.0 - 100.0
err = betabeating_["ERRBETX1"]/betabeating_["BETXMDL1"]*100.0
rms = np.sqrt(np.mean(np.square([x for x in betabeating if abs(x) < args.cut])))

if args.getbetax2 is not None:
    betabeating_old = betabeating_["BETX2"]/betabeating_["BETXMDL2"] *100.0- 100.0
    err_old = betabeating_["ERRBETX2"]/betabeating_["BETXMDL2"]*100.0
    rms_old = np.sqrt(np.mean(np.square([x for x in betabeating_old if abs(x) < args.cut])))

betabeatingy = betabeating_["BETY1"]/betabeating_["BETYMDL1"]*100.0 - 100.0
erry = betabeating_["ERRBETY1"]/betabeating_["BETYMDL1"]*100.0
rmsy = np.sqrt(np.mean(np.square([x for x in betabeatingy if abs(x) < args.cut])))

if args.getbetax2 is not None:
    betabeatingy_old = betabeating_["BETY2"]/betabeating_["BETYMDL2"] *100.0- 100.0
    erry_old = betabeating_["ERRBETY2"]/betabeating_["BETYMDL2"]*100.0
    rmsy_old = np.sqrt(np.mean(np.square([x for x in betabeatingy_old if abs(x) < args.cut])))


#if args.omcstyle:
x_label1 = "{1:s}".format(rms, args.label1)
y_label1 = "{1:s}".format(rmsy, args.label1)
if args.getbetax2 is not None:
    x_label2 = "{1:s}".format(rms, args.label2)
    y_label2 = "{1:s}".format(rmsy, args.label2)


#else:
#    x_label1 = "{1:s}, rms = ${0:7.3f}\,\%$".format(rms, args.label1)
#    y_label1 = "{1:s}, rms = ${0:7.3f}\,\%$".format(rmsy, args.label1)
#    if args.getbetax2 is not None:
#        x_label2 = "{1:s}, rms = ${0:7.3f}\,\%$".format(rms_old, args.label2)
#        y_label2 = "{1:s}, rms = ${0:7.3f}\,\%$".format(rmsy_old, args.label2)

# =============================================================================
# ======== printing informatiions about performance ===========================
# =============================================================================


print "{:12s} x, rms = {:10.3f} | \33[38;2;100;100;255m{:s}\33[0m".format(args.label1, rms, make_bar(rms))
print "{:12s} y, rms = {:10.3f} | \33[38;2;100;100;255m{:s}\33[0m".format(args.label1, rmsy, make_bar(rmsy))
if args.getbetax2 is not None:
    print "{:12s} x, rms = {:10.3f} | \33[38;2;255;50;50m{:s}\33[0m".format(args.label2, rms_old, make_bar(rms_old))
    print "{:12s} y, rms = {:10.3f} | \33[38;2;255;50;50m{:s}\33[0m".format(args.label2, rmsy_old, make_bar(rmsy_old))


# =============================================================================
# ======== plotting ===========================================================
# =============================================================================

plfmt = " o"
if args.lines:
    plfmt = "-o"

if args.bb_plot:
    if args.ylim != -1:
        if not args.absolut:
            ax1.set_ylim(-args.ylim, args.ylim)
            if args.use_yplane:
                ax2.set_ylim(-args.ylim, args.ylim)
        else:
            ax1.set_ylim(0, args.ylim)
            if args.use_yplane:
                ax2.set_ylim(0, args.ylim)
            
    else:
        args.ylim = 100000
        
        
    IPtickslabels = ["IP2","IP3","IP4","IP5","IP6","IP7","IP8","IP1"]
    if args.lhcbeam == "LHCB1":
        IPticks = [192.923, 3523.267, 6857.49, 10189.78, 13522.212, 16854.649, 20185.865, 23519.37]
    else:
        IPticks = [192.923, 3523.267, 6857.49, 10189.78, 13522.212, 16854.649, 20185.865, 23519.37]
    # try to find the positions of the IPs
    
    print ". . . . . . . . . ."
    print ". . bet1 command: ."
    print bb_file_x1.headers["Command"]
    print ". . . . . . . . . ."
    
    if args.getbetax2 is not None:
        print ". . bet2 command: ."
        print bb_file_x2.headers["Command"]
        print ". . . . . . . . . ."

    print args.accel
    
    tfsmodel = None
    
    commandargs = bb_file_x1.headers["Command"].split("' '")
    for i, comm in enumerate(commandargs):
        words = comm.split("=")
        if words[0] == "--model":
            if len(words) >= 2:
                words1 =  words[1]
            else:
                words1 = commandargs[i+1]
            modelpath = os.path.dirname( words1) + "/twiss_elements.dat"
            print "looking for model in ", modelpath
            if os.path.isfile(modelpath):
                tfsmodel = tfs.read_tfs(modelpath)
                print "model found in input file 1. "
                if args.accel.startswith("LHC"):
                    for i in range(len( IPtickslabels)):
                        IPticks[i] = tfsmodel.set_index("NAME").loc[IPtickslabels[i]]["S"]

    tightlayout_height = .98
    
    if args.accel == "JPARC":
        ax1.set_xlim(0, 1600)
    elif args.accel == "PETRA":
        ax1.set_xlim(0, 2350)
    elif args.accel == "CPS":
        ax1.set_xlim(0, 630)
    else:
        ax1.set_xlim(0,27000)
        if args.use_yplane:
            ax2.set_xlim(0,27000)
        if args.omcstyle:
            #betabeating_.set_index("NAME").loc["IP1"]["S"]
            ax1.set_xticks(IPticks)
            ax1.set_xticklabels(IPtickslabels)
            
            ax1.xaxis.set_ticks_position('none') 
            if args.ipbars:
                for x in IPticks:
                    ax1.plot((x, x), (-args.ylim, args.ylim), "-", color="#D0D0D0")
                    if args.use_yplane:
                        ax2.plot((x, x), (-args.ylim, args.ylim), "-", color="#D0D0D0")
    if args.omctitle is not None:
        ax1.text(1.0, 1.02, args.omctitle, verticalalignment='bottom', horizontalalignment='right', transform=ax1.transAxes, fontsize=14)
        tightlayout_height -= 0.05
            
    if args.zoom is not None:
        args.zoom = args.zoom.split(",")
        ax1.set_xlim(float(args.zoom[0]), float(args.zoom[1]))
        if args.use_yplane:
            ax2.set_xlim(float(args.zoom[0]), float(args.zoom[1]))
     
    if args.absolut:
        if tfsmodel is not None:
            b = ax1.errorbar(tfsmodel["S"], tfsmodel["BETX"], label="model", c="deepskyblue", markeredgecolor="#D00000", marker=None, markersize=3.0, fmt='-', linewidth=1, zorder=-32)
        else:
            b = ax1.errorbar(betabeating_["S"], betabeating_["BETXMDL1"], label="model", c="deepskyblue", markeredgecolor="#D00000", marker=None, markersize=3.0, fmt='-', linewidth=1, zorder=-32)
        a = ax1.errorbar(betabeating_["S"], betabeating_["BETX1"], betabeating_["ERRBETX1"], label=x_label1, c="r",
                         markeredgecolor="r", marker="o", markersize=2.0, fmt=" 0", linewidth=1)
        
        #ax2.plot(bb_file["BETX"]/ bb_file_old["BETX"]*100.0 -100.0, label="Difference", c="black")
        if args.use_yplane:
            if tfsmodel is not None:
                a = ax2.errorbar(tfsmodel["S"], tfsmodel["BETY"], label="model", c="deepskyblue", markeredgecolor="#0000D0", marker=None, markersize=3.0, fmt='-', linewidth=1)
            else:
                a = ax2.errorbar(betabeating_["S"], betabeating_["BETYMDL1"], label="model", c="deepskyblue", markeredgecolor="#0000D0", marker=None, markersize=3.0, fmt='-', linewidth=1)
            b = ax2.errorbar(betabeating_["S"], betabeating_["BETY1"], betabeating_["ERRBETY1"], label=y_label1, c="r", markeredgecolor="r", marker="o", markersize=2.0, fmt=' o')
    
        
    else:
        a = ax1.errorbar(betabeating_["S"], betabeating, err, label=x_label1, c="#9090FF", markeredgecolor="#0000D0",
                         marker='o', markersize=3.0, fmt=plfmt)
        if args.getbetax2 is not None:
            b = ax1.errorbar(betabeating_["S"], betabeating_old, err_old, label=x_label2, c="#FF9090",
                             markeredgecolor="#D00000", marker='o', markersize=3.0, fmt=plfmt)
        
        #ax2.plot(bb_file["BETX"]/ bb_file_old["BETX"]*100.0 -100.0, label="Difference", c="black")
        if args.use_yplane:
            a = ax2.errorbar(betabeating_["S"], betabeatingy, erry, label=y_label1, c="#9090FF",
                             markeredgecolor="#0000D0", marker='o', markersize=3.0, fmt=plfmt)
            if args.getbetax2 is not None:
                b = ax2.errorbar(betabeating_["S"], betabeatingy_old, erry_old, label=y_label2, c="#FF9090",
                                 markeredgecolor="#D00000", marker='o', markersize=3.0, fmt=plfmt)
    
    #ax2.legend()
    if args.absolut:
        ax1.set_ylabel(r"$\beta_x \; [m]$")
        if args.use_yplane:
            ax2.set_ylabel(r"$\beta_y \; [m]$")
    else:
        ax1.set_ylabel(r"$\Delta \beta_x/ \beta_x\; [\%]$")
        if args.use_yplane:
            ax2.set_ylabel(r"$\Delta \beta_y/ \beta_y\; [\%]$")
    
    
    
    #plt.title("BetaBeating")
    if args.use_yplane:
        ax2.set_xlabel("$ s\;[m]$")
    else:
        ax1.set_xlabel("$ s\;[m]$")
    
    if args.legend:
        if args.omcstyle:
            print "\n"
            print OMC_LOGO
            print "\n"
            if args.loc == 1:
                ax1.legend(bbox_to_anchor=(.98, .98), loc="upper right",ncol=2)
            elif args.loc == 2:
                ax2.legend(bbox_to_anchor=(.98, .98), loc="upper right",ncol=2)
            elif args.loc == 0:
                ax1.legend(bbox_to_anchor=(1.02, 1), loc="lower right",ncol=2)
                tightlayout_height -= 0.1
        else:
            ax1.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                       ncol=2, mode="expand", borderaxespad=0.)
            ax2.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                       ncol=2, mode="expand", borderaxespad=0.)
            
        
        
    plt.tight_layout(rect=(.02,.02,.98, tightlayout_height), pad=0.5)
    
    
    print "\n- - - - - - - - - - - - - - - - - -"
    print "- - - - Plotting Beta Beating - - -"
    print "- \33[38;2;200;200;200msummary\33[0m:"
    print "- "
    #print "- rms ich BetaBeating = {0:9.5f}".format(rms)
    print "- "

 
if args.errhisto:
    err_arc = []
    err_IR = []
    err2_arc = []
    err2_IR = []
    
    rebpm = re.compile("BPM[A-Z_]*\.[A-Z]*([0-9]+)[R,L].+")


    if args.accel.startswith("LHC"):
        for i in range(len(err)):
            match = rebpm.match(betabeating_["NAME"][i])
    
            if not np.isnan(err[i]):
                if int(match.group(1)) < 13:
                    err_IR.append(err[i])
                else:
                    err_arc.append(err[i])
            if not np.isnan(err_old[i]):
                if int(match.group(1)) < 13:
                    err2_IR.append(err_old[i])
                else:
                    err2_arc.append(err_old[i])
            
    

            
    print x_label1
    print "mean {} total: {:.4f} %".format(args.label1, np.mean(err[err < args.cut])) 
    if args.accel.startswith("LHC"):
        print "mean {} arc: {:.4f} %".format(args.label1, np.mean(err_arc)) 
        print "mean {} IR: {:.4f} %".format(args.label1, np.mean(err_IR)) 
        
    print ""
    
    print x_label2
    print "mean {} total: {:.4f} %".format(args.label1, np.mean(err_old[err_old < args.cut])) 
    if args.accel.startswith("LHC"):
        print "mean {} arc: {:.4f} %".format(args.label2, np.mean(err2_arc)) 
        print "mean {} IR: {:.4f} %".format(args.label2, np.mean(err2_IR)) 


    bins = np.linspace(0,args.xlim, 50)    
    err = err[~np.isnan(err)]
    err_old = err_old[~np.isnan(err_old)]
    erry = erry[~np.isnan(erry)]
    erry_old = erry_old[~np.isnan(erry_old)]
    
    ax1.hist(err, bins, label=x_label1 + ", mean = {:.1f}".format(np.mean(err[err < args.cut])), color="deepskyblue", alpha=.5, normed=True)
    ax1.hist(err_old, bins, label=x_label2 + ", mean = {:.1f}".format(np.mean(err_old[err_old < args.cut])), color="r", alpha=.5, normed=True)
    print np.mean(err)
    print np.mean(err_old)
    if args.use_yplane:
        ax2.hist(erry, bins, label=y_label1, color="deepskyblue", alpha=.5, normed=True)
        ax2.hist(erry_old, bins, label=y_label2, color="r", alpha=.5, normed=True)
        print np.mean(err)
        print np.mean(err_old)
    ax1.legend()
    
    if args.use_yplane:
        ax2.set_xlabel(r"size of errorbars [\%]")
        ax2.set_ylabel(r"count [normalized]")
    else:
        ax1.set_xlabel(r"size of errorbars [\%]")
    ax1.set_ylabel(r"count [normalized]")
    
    tightlayout_height = 1.0
    if args.omctitle is not None:
        ax1.text(1.0, 1.02, args.omctitle, verticalalignment='bottom', horizontalalignment='right', transform=ax1.transAxes, fontsize=14)
        tightlayout_height -= 0.05

    plt.tight_layout(rect=(.00,.00,1, tightlayout_height), pad=0.5)
    # seperate arc and IR
    
    
#    ax2.hist(erry, label=x_label1, c="deepskyblue")
    
   
    
    #
    
    
f.show()

if printplot:
    plt.savefig(args.printplt)
    commandfile = open(args.printplt + ".command", "w")
    commandfile.write("""#!/bin/bash\n\n""")
    commandfile.write(sys.executable + " " + cmdline)
    commandfile.close()
    os.chmod(args.printplt + ".command", stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE | stat.S_IWOTH | stat.S_IXOTH | stat.S_IROTH | stat.S_IWGRP | stat.S_IXGRP | stat.S_IRGRP)
    

if args.output_pickle:
	tfs.write_tfs(args.outputpath, betabeating_[["S", "BETX1", "ERRBETX1", "BETY1", "ERRBETY1", "BETXMDL1", "BETYMDL1"]])
	
raw_input()

