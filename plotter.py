import os
import sys
import contextlib
import argparse
import stat

import betabeatsrc

from pyterminal import *
from getllm_result_plots import *
from utils import tfs_pandas as tfs
import numpy as np
from subprocess import Popen
from shutil import copyfile
from time import sleep

from utils.ADDbpmerror import convert_files
from utils import logging_tools
from math import sqrt
import re
import logging
from matplotlib import rc
from collections import OrderedDict

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib
import pandas as pd

BW = False
LEN = 20

LOG = logging_tools.get_logger(__name__, level_console=logging.DEBUG)
print "path:"
for pathstring in sys.path:
    print pathstring

# =============================================================================
# ======== function definitions ===============================================
# =============================================================================


OMC_LOGO = """
     ######    ##L          ##      ######
   d##   ##b   ###L        ###    ####   ##
  ###     ###  ####L      ####  ###
  ##       ##  ## ##L    ## ##  ##
  ###     ###  ##  ##L  ##  ##  ###
   T##_  ##P   ##   ##L##   ##    ###
     #####     ##    ###    ##      ######
"""

# --------------------------------------------------------------------------------------------------
# ---------- parameters for the program ------------------------------------------------------------
# --------------------------------------------------------------------------------------------------

parameters = {
    "width": "8",
    "accel": "LHC",
    "style": "OMC",
    "ofile": "plot_temp.pdf",
    "ylim": "100",
    "absolut": "0",
    "lines": "1",
    "zoom": "all",
    "omctitle": "",
    "plot_x": "1",
    "plot_y": "1",
    "ipbars": "0",
    "IPticks": "1",
    "lhcbeam": "1",
    "loc": "1",
    "legend": "1",
    "tightlayout_height": 1.0,
    "tl_loc": 0.0,
    "tl_title": 0.0
}

results = OrderedDict()
model = None
colors = [
    ['#5060F0', '#000090'],
    ['#E05020', '#A00A00'],
    ['#10A010', '#108010'],
    ['#E09000', '#805010'],
    ['#10B0E0', '#0050E0'],
    ['#B010F0', '#5000E0'],
    ['#A0F010', '#508010'],
]

RESDIR = os.path.abspath(".")

plt.rc('text', usetex=True)
parameters["tightlayout_height"] = 1.0
if parameters["style"] == "OMC":
    plt.rc('font', family='sans-serif')
    plt.rc('xtick.major', pad=6)

else:
    plt.rc('font', family='serif')
plt.rc('axes', labelsize=16)
plt.rc('xtick', labelsize=16)
plt.rc('ytick', labelsize=16)
plt.rc('legend', fontsize=16)
#    plt.rc("text.latex", preamble=[
#                                   r'\usepackage{siunitx}',
#                                   r'\usepackage{helvetica}',
#                                   r'\usepackage{sansmath}',
#                                   r'\sansmath'
#                               ])

def show_resdirlist(command=""):
    print "RESDIR = '{}'".format(RESDIR)
    dirlist = sorted(os.listdir(RESDIR))
    if command != "noprint":
        for i,f in enumerate(dirlist):
            if os.path.isdir(os.path.join(RESDIR, f)):
                print "  [{:3d}] {}".format(i,f)
    return dirlist
# --------------------------------------------------------------------------------------------------
# ---------- terminal commands ---------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------

def set_param(command):
    global parameters
    words = command.split("=", 1)
    if len(words) == 2:
        parameters[words[0]] = words[1]
    elif len(words) == 1:
        words = words[0].split(' ', 1)
        if len(words) == 2:
            parameters[words[0]] = words[1]
    else:
        print "----- didn't understand the command. please try again --------"

def set_legend_fontsize(command):
    """Sets the fontsize of the legend."""
    try:
        plt.rc('legend', fontsize=int(command))
    except ValueError:
        print "couldn't convert {} to int.".format(command)

def set_resdir(command):
    """changes the root result path"""
    global RESDIR
    RESDIR = os.path.abspath(command)

def get_param(command):
    if command == "all":
        for key, value in parameters.iteritems():
            print "{:20s}: {}".format(key, value)
    elif command == "":
        print ("you have to specify which parameter should be printed or 'all' if you want to see "
               "the values of all the parameters")
    elif command in parameters.keys():
        print "{:20s}: {}".format(command, parameters[command])
    else:
        print "{} not in the parameters".format(command)

def add_beta(command):
    global model
    words = command.split("#")
    path = os.path.join(RESDIR, words[1])
    bbx, bby, dfx, dfy = load_result(path)
    results[words[0]] = [dfx, dfy]
    if model is None:
        model = find_model(path)

def add_betas(command=""):
    if command == "":
        dirlist = show_resdirlist()
        select = raw_input("[select:] ")
    else:
        dirlist = show_resdirlist("noprint")
        select = command

    splitselect = select.split('#')
    if len(splitselect) == 2:
        add_beta(splitselect[1] + '#' + os.path.join(RESDIR, dirlist[int(splitselect[0])]))
    else:
        print "Need label"
        label = raw_input("[label: ] ")
        add_beta(label + "#" + os.path.join(RESDIR, dirlist[int(select)]))

def del_beta(command=""):
    global results
    if command == "all":
        results = OrderedDict()
        model = None
        print "resetting results data..."
        return

    for i,b in enumerate(results.keys()):
        print"  [{:3d}] {}".format(i, b)
    print "delete desired index (e.g. 3) or desired label, preceeded by ':' (e.g. :label1)."
    inp = raw_input("[in:] ")
    if inp[0] == ':':
        del results[inp[1:]]
    else:
        del results[results.keys()[int(inp)]]
    for i,b in enumerate(results.keys()):
        print"  [{:3d}] {}".format(i, b)

def reset(command):
    """Resets results and model"""
    global results
    global model
    global parameters
    results = OrderedDict()
    model = None
    parameters["ofile"] = "ofile.pdf"
    print ""
    print " ` ` ` ` ` ` ` ` ` resetting results and model ` ` ` ` ` ` ` ` ` ` "
    print ""

def status(command):
    """Prints out status messages.
    - the selected model (note that a model is needed for the plotting to work)
    - a list of selected results folders
    - some important parameters (accelerator, filename)"""
    print "\n` ` ` ` ` STATUS  ` ` ` ` ` ` "
    if model is None:
        print " model: NONE"
    else:
        print " model: [OK]"
    print " Selected results:"
    for beta in results.keys():
        print "  -", beta
    print " accel:", parameters["accel"]
    print " ofile:", parameters["ofile"]
    print "` ` ` ` ` ` ` ` ` ` ` ` ` ` ` \n"

def plot_betabeating(command):
    """This function will do the plotting of beta beating. How the final plot looks like is defined
    by the following parameters (change them with set PARAM VALUE, see help set for more info):
        - 
        """
    # do the plotting

    # check if everything is alright
    if model is None:
        print "----------------> no model"
        return
    if len(results) == 0:
        print "----------------> no results"
        return
    global parameters
    print "plotting"
    width = float(parameters["width"])
    height = width * .8

    px = parameters["plot_x"] == "1"
    py = parameters["plot_y"] == "1"

    if parameters["absolut"] == "1":
        y_label = r"$\beta_x \; [m]$"
        y_label2 = r"$\beta_y \; [m]$"
    else:
        y_label = r"$\Delta \beta_x/ \beta_x\; [\%]$"
        y_label2 = r"$\Delta \beta_y/ \beta_y\; [\%]$"
    x_label = "$ s\;[m]$"

    if px and py:
        f, [ax1,ax2] = plt.subplots(nrows=2, figsize=(width, height))
        setup_plot_area(parameters, ax2, model, y_label2, x_label, False)
        x_label = ""
    else:
        parameters["IPticks"] = "0"
        f, ax1 = plt.subplots(nrows=1, figsize=(width, height * .6))

    setup_plot_area(parameters, ax1, model, y_label, x_label, True)


    i = 0
    l = len(results) - 1
    for label, [dfx, dfy] in results.iteritems():
        if px and py:
            plot_errorbar(ax1, dfx, colors[l-i], label, parameters["plfmt"])
            plot_errorbar(ax2, dfy, colors[l-i], label, parameters["plfmt"])
        elif px:
            plot_errorbar(ax1, dfx, colors[l-i], label, parameters["plfmt"])
        elif py:
            plot_errorbar(ax1, dfy, colors[l-i], label, parameters["plfmt"])

        i = i + 1

    if parameters["legend"] == "1":
        if parameters["style"] == "OMC":
            print "\n"
            print OMC_LOGO
            print "\n"
            parameters["tl_loc"] = 0.0
            if parameters["loc"] == "1":
                ax1.legend(bbox_to_anchor=(.98, .98), loc="upper right",ncol=2)
                parameters["tl_loc"] = 0.0
            elif parameters["loc"] == "2":
                ax2.legend(bbox_to_anchor=(.98, .98), loc="upper right",ncol=2)
                parameters["tl_loc"] = 0.0
            elif parameters["loc"] == "out":
                ax1.legend(bbox_to_anchor=(1.02, 1), loc="lower right",ncol=2)
                parameters["tl_loc"] = -0.1
            elif parameters["loc"] == "auto":
                ax1.legend()
                parameters["tl_loc"] = 0.0
            elif parameters["loc"].startswith("1:"):
                ax1.legend(loc=parameters["loc"].split(":")[1], ncol=3)
                parameters["tl_loc"] = 0.0
            elif parameters["loc"].startswith("2:"):
                ax2.legend(loc=parameters["loc"].split(":")[1], ncol=3)
                parameters["tl_loc"] = 0.0
        else:
            ax1.legend(bbox_to_anchor=(0., 1.15, 1., .102), loc=3,
                       ncol=2, mode="expand", borderaxespad=0.)
            parameters["tl_loc"] -= .075
    if parameters["omctitle"] != "":
        parameters["tl_title"] -= 0.05

    tightlayout = parameters["tightlayout_height"] + parameters["tl_loc"] + parameters["tl_title"]

    plt.tight_layout(rect=(.02,.02,.98, tightlayout), pad=0.5)

    f.show()

    if command == 'print':
        f.savefig(parameters["ofile"])

# --------------------------------------------------------------------------------------------------
# ---------- terminal initialization ---------------------------------------------------------------
# --------------------------------------------------------------------------------------------------

CONT = True
cmd_nr = 0


terminal = ATerm()

terminal.add_command(aliases=["set", "set_param"],
                     action=set_param,
                     thehelp="KEY=VALUE. Sets the parameter KEY to the value VALUE.")

terminal.add_command(aliases=["get", "get_param"],
                     action=get_param,
                     thehelp=("shows the value of the given parameter. get all will return all the"
                              "parameters"))

terminal.add_command(aliases = ["bet", "add_beta"],
                     action = add_beta)

terminal.add_command(aliases = ["add"],
                     action = add_betas)

terminal.add_command(aliases=["plotbb"],
                     action=plot_betabeating,
                     thehelp="Does the plotting.")

terminal.add_command(aliases=['del_bet', 'del_beta'],
                     action=del_beta,
                     thehelp='Deletes the result at the given index.')

terminal.add_command(aliases=['showres', 'showresdir'],
                     action=show_resdirlist,
                     thehelp='Shows the result directories in the current gui directory.')

terminal.add_command(aliases=['set_legend', 'set_legend_fontsize'],
                     action=set_legend_fontsize,
                     thehelp='Sets the legend fontsize to the given value. Default=16.')

terminal.add_command(aliases=['set_resdir'],
                     action=set_resdir)
terminal.add_command(aliases=['s', 'status'],
                     action=status)
terminal.add_command(aliases=['reset'],
                     action=reset)
# --------------------------------------------------------------------------------------------------
# ---------- main loop -----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------

while CONT:
    command = raw_input("[in {}] ".format(cmd_nr))
    if terminal.run_command(command):
        cmd_nr = cmd_nr + 1
    else:
        if command == "quit" or command == "exit" or command == "q":
            CONT = False



