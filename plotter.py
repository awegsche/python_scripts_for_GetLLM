import os
import sys
import contextlib
import argparse
import stat

from pyterminal import *
from getllm_result_plots import *

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
import logging
from matplotlib import rc

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib
import pandas as pd

BW = False
LEN = 20

LOG = logging_tools.get_logger(__name__, level_console=logging.DEBUG)

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
    "lhcbeam": "1",
    "loc": "1",
    "legend": "1",
    "tightlayout_height": 1.0
}

results = {}
model = None
colors = [
    "orangered",
    "deepskyblue",
    "limegreen",
    "goldenrod",
    "mediumpurple",
    "fuchsia",
    "chocolate",
    "y",
    "palegreen",
    "turquoise",
    "slategray"
]

RESDIR = os.path.abspath(".")
# --------------------------------------------------------------------------------------------------
# ---------- terminal commands ---------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------

def set_param(command):
    global parameters
    words = command.split("=")
    parameters[words[0]] = words[1]

def add_beta(command):
    global model
    words = command.split(" ")
    path = os.path.join(RESDIR, words[1])
    bbx, bby, dfx, dfy = load_result(path)
    results[words[0]] = [dfx, dfy]
    if model is None:
        model = find_model(bbx)

def add_betas(command):
    dirlist = os.listdir(RESDIR)
    for i,f in enumerate(dirlist):
        print "  [{:3d}] {}".format(i,f)
    select = raw_input("[select:] ")
    print "Need label"
    label = raw_input("[label: ] ")

    add_beta(label + " " + os.path.join(RESDIR, dirlist[int(select)]))

def plot_betabeating(command):
    # do the plotting
    global parameters
    print "plotting"
    width = float(parameters["width"])
    height = width * .8

    px = parameters["plot_x"]
    py = parameters["plot_y"]

    if parameters["absolut"]:
        y_label = r"$\beta_x \; [m]$"
        y_label2 = r"$\beta_y \; [m]$"
    else:
        y_label = r"$\Delta \beta_x/ \beta_x\; [\%]$"
        y_label2 = r"$\Delta \beta_y/ \beta_y\; [\%]$"
    x_label = "$ s\;[m]$"

    if px and py:
        f, [ax1,ax2] = plt.subplots(nrows=2, figsize=(width, height))
        setup_plot_area(parameters, ax2, model, y_label2, x_label)
        x_label = ""
    else:
        f, ax1 = plt.subplots(nrows=1, figsize=(width, height * .6))

    setup_plot_area(parameters, ax1, model, y_label, x_label)


    i = 0
    for label, [dfx, dfy] in results.iteritems():
        if px and py:
            plot_errorbar(ax1, dfx, colors[i], label, parameters["plfmt"])
            plot_errorbar(ax2, dfy, colors[i], label, parameters["plfmt"])
        i = i + 1

    if parameters["legend"] == "1":
        if parameters["style"] == "OMC":
            print "\n"
            print OMC_LOGO
            print "\n"
            if parameters["loc"] == "1":
                ax1.legend(bbox_to_anchor=(.98, .98), loc="upper right",ncol=2)
            elif params["loc"] == "2":
                ax2.legend(bbox_to_anchor=(.98, .98), loc="upper right",ncol=2)
            elif params["loc"] == "0":
                ax1.legend(bbox_to_anchor=(1.02, 1), loc="lower right",ncol=2)
                tightlayout_height -= 0.1
        else:
            ax1.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                       ncol=2, mode="expand", borderaxespad=0.)
            ax2.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                       ncol=2, mode="expand", borderaxespad=0.)

    plt.tight_layout(rect=(.02,.02,.98, parameters["tightlayout_height"]), pad=0.5)

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

terminal.add_command(aliases = ["bet", "add_beta"],
                     action = add_beta)

terminal.add_command(aliases = ["add"],
                     action = add_betas)

terminal.add_command(aliases=["plotbb"],
                     action=plot_betabeating,
                     thehelp="Does the plotting.")

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



