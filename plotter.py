import os
import sys
import contextlib
import argparse
import stat

import betabeatsrc

from pyterminal import *
from getllm_result_plots import *
from GetLLM.GetLLM import _tb_
from utils import tfs_pandas as tfs
import numpy as np
from numpy import sqrt, square, mean
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
TWOPI = 2.0 * np.pi

LOG = logging_tools.get_logger(__name__, level_console=logging.INFO)

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
commands = []

parameters = {
    "width": "8",
    "aspect": "1.25",
    "accel": "LHC",
    "beam": "1",
    "style": "OMC",
    "ylim": "100",
    "ofile": "plot_temp.pdf",
    "absolut": "0",
    "lines": "1",
    "zoom": "all",
    "omctitle": "",
    "plot_x": "1",
    "plot_y": "1",
    "ipbars": "0",
    "IPticks": "1",
    "loc": "1:best",
    "legend": "1",
    "ip_fontsize": "14",
    "tightlayout_height": 1.0,
    "tl_loc": 0.0,
    "tl_title": 0.0,

    "y_label": None,
    "y_label2": None
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
    print "command given: " + command
    words = command.split("#")
    path = words[1]
    results[words[0]] = load_result(path)

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
        try:
            index = int(splitselect[0])
            path = os.path.join(RESDIR, dirlist[index])
        except ValueError:
            path = os.path.join(os.getcwd, splitselect[0])
        add_beta(splitselect[1] + '#' + path)
    else:
        print "Need label"
        label = raw_input("[label: ] ")
        try:
            index = int(splitselect[0])
            path = os.path.join(RESDIR, dirlist[index])
        except ValueError:
            path = os.path.join(os.getcwd(), splitselect[0])
        add_beta(label + "#" + path)

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
    height = width / float(parameters["aspect"])

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
    for label, getllm_result in results.iteritems():
        dfx = getllm_result.betax
        dfy = getllm_result.betay
        if px and py:
            plot_errorbar(ax1, dfx, colors[l-i], label, parameters["plfmt"])
            plot_errorbar(ax2, dfy, colors[l-i], label, parameters["plfmt"])
        elif px:
            plot_errorbar(ax1, dfx, colors[l-i], label, parameters["plfmt"])
        elif py:
            plot_errorbar(ax1, dfy, colors[l-i], label, parameters["plfmt"])

        i = i + 1

        print "rms_x of {}: {:10.4f} %".format(
            label,
            sqrt(mean(square(dfx["BBEAT"].loc[abs(dfx)["BBEAT"] < float(parameters["ylim"])].values)))
        )
        print "rms_y of {}: {:10.4f} %".format(
            label,
            sqrt(mean(square(dfy["BBEAT"].loc[abs(dfy)["BBEAT"] < float(parameters["ylim"])].values))))

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
            parameters["tl_loc"] = -.075
    if parameters["omctitle"] != "":
        parameters["tl_title"] = -0.05

    tightlayout = parameters["tightlayout_height"] + parameters["tl_loc"] + parameters["tl_title"]

    plt.tight_layout(rect=(.02,.02,.98, tightlayout), pad=0.5)

    f.show()

    if command == 'print':
        f.savefig(parameters["ofile"])


def plot_disp_over_beta(command):
    """
    Plots the disperion over beta function.

    """

    # do the plotting
    words = command.split(' ')
    global parameters
    x_label = "$ s\;[m]$"
    y_label = r"$\Delta D_x / \beta$"
    y_label2 = r"$\Delta D_y / \beta$"


    # check if everything is alright
    if model is None:
        print "----------------> no model"
        return
    if len(results) == 0:
        print "----------------> no results"
        return
    print "plotting LOBSTER"
    width = float(parameters["width"])
    height = width / float(parameters["aspect"])

    px = parameters["plot_x"] == "1"
    py = parameters["plot_y"] == "1"

    printit = command == "print"


    if px and py:
        f, [ax1,ax2] = plt.subplots(nrows=2, figsize=(width, height))
        setup_plot_area(parameters, ax2, model, y_label2, x_label, False)
        x_label = ""
        #ax2.set_ylim(auto=True)
    else:
        parameters["IPticks"] = "0"
        f, ax1 = plt.subplots(nrows=1, figsize=(width, height * .6))

    setup_plot_area(parameters, ax1, model, y_label, x_label, True)
    #ax1.set_ylim(auto=True)

    i = 0
    l = len(results) - 1
    for label, getllm_result in results.iteritems():
        if px and py:
            datax = _tfs(os.path.join(getllm_result.path, "getDx.out"), index="NAME")
            datay = _tfs(os.path.join(getllm_result.path, "getDy.out"), index="NAME")
            xkeys = getllm_result.betax.index.intersection(datax.index)
            ykeys = getllm_result.betay.index.intersection(datay.index)
            ax1.errorbar(
                datax.loc[xkeys, "S"],
                (datax.loc[xkeys, "DX"] - datax.loc[xkeys, "DXMDL"]) /
                (getllm_result.betax.loc[xkeys, "BETX"]),
                (datax.loc[xkeys, "STDDX"]) /
                (getllm_result.betax.loc[xkeys, "BETX"]),
                fmt=' o', color=colors[l-i][0], markeredgecolor=colors[l-i][1], label=label,
                markersize=4.0)
            ax2.errorbar(
                datay.loc[ykeys, "S"],
                (datay.loc[ykeys, "DY"] - datay.loc[ykeys, "DYMDL"]) /
                (getllm_result.betay.loc[ykeys, "BETY"]),
                (datay.loc[ykeys, "STDDY"]) /
                (getllm_result.betay.loc[ykeys, "BETY"]),
                fmt=' o', color=colors[l-i][0], markeredgecolor=colors[l-i][1], label=label,
                markersize=4.0)
        elif px:
            datax = _tfs(os.path.join(getllm_result.path, "getDx.out"), index="NAME")
            ax1.errorbar(
                datax.loc[xkeys, "S"],
                (datax.loc[xkeys, "DX"] - datax.loc[xkeys, "DXMDL"]) /
                np.sqrt(getllm_result.betax.loc[xkeys, "BETX"]),
                ' o', color=colors[l-i][0], markeredgecolor=colors[l-i][1], label=label,
                markersize=4.0)
        else:
            datay = _tfs(os.path.join(getllm_result.path, "getDy.out"), index="NAME")
            ax1.errorbar(
                datay.loc[ykeys, "S"],
                (datay.loc[ykeys, "DY"] - datay.loc[ykeys, "DYMDL"]) /
                np.sqrt(getllm_result.betay.loc[ykeys, "BETY"]),
                ' o', color=colors[l-i][0], markeredgecolor=colors[l-i][1], label=label,
                markersize=4.0)
        i += 1


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
            parameters["tl_loc"] = -.075
    if parameters["omctitle"] != "":
        parameters["tl_title"] = -0.05

    tightlayout = parameters["tightlayout_height"] + parameters["tl_loc"] + parameters["tl_title"]

    plt.tight_layout(rect=(.02,.02,.98, tightlayout), pad=0.5)

    f.show()

    if printit:
        f.savefig(parameters["ofile"])

def plot_column(command):
    """
    Plots the column of an arbitrary file. Usage:

        plot FILENAME COLUMN
            plots the column COLUMN of file FILENAME against a column S if it finds any. If not, the
            user is prompted to specify another column as x-axis.
            ex.:
                the command
                plot getbetax.out BETX
                plots the horizontal beta function
        plot FILENAME u X_COLUMN:Y_COLUMN
            gnuplot-like command style, plots Y_COLUMN against X_COLUMN.
            ex.:
                plot getphasex.out u S:PHASEX
                plots the measured phaseadvances
    Notes:
        spaces in the column names as well as between the ':' and the column names are not supported
        and will cause this programm to crash.

    More Examples:
        1. plotting normalised dispersion:
            set y_label=$\Delta N D_x\;\left[\sqrt{m}\,\right]$
            plot getNDx.out u S:NDX-NDXMDL:STDNDX print
    """

    # do the plotting
    words = command.split(' ')
    global parameters

    filename2 = None
    if ',' in words[0]:
        filename, filename2 = words[0].split(',')
    else:
        filename = words[0]

    i = 1
    x_column = "S"
    y_column = None
    err_column = None
    printit = False
    x2_column = "S"
    y2_column = None
    err2_column = None


    x_label = "$ s\;[m]$"
    y_label = parameters["y_label"]
    y_label2 = parameters["y_label2"]

    while i < len(words):
        word = words[i]
        if word == "u":
            i += 1
            if ':' in words[i]:
                columns = words[i].split(':')
                if len(columns) == 2:
                    [x_column, y_column] = columns
                else:
                    [x_column, y_column, err_column] = columns
            else:
                y_column = words[i]
        if word == "u2":
            i += 1
            if ':' in words[i]:
                columns = words[i].split(':')
                if len(columns) == 2:
                    [x2_column, y2_column] = columns
                else:
                    [x2_column, y2_column, err2_column] = columns
            else:
                y2_column = words[i]
        elif word == 'print' or word == 'p':
            printit = True

        i += 1

    if y_label is None:
        y_label = y_column
    if y_label2 is None:
        y_label2 = y2_column

    # check if everything is alright
    if model is None:
        print "----------------> no model"
        return
    if len(results) == 0:
        print "----------------> no results"
        return
    print "plotting LOBSTER"
    width = float(parameters["width"])
    height = width * .5

    if filename2 is not None:
        f, [ax1,ax2] = plt.subplots(nrows=2, figsize=(width, height))
        setup_plot_area(parameters, ax2, model, y_label2, x_label, False)
        x_label = ""
    else:
        parameters["IPticks"] = "0"
        f, ax1 = plt.subplots(nrows=1, figsize=(width, height * .6))

    setup_plot_area(parameters, ax1, model, y_label, x_label, True)

    i = 0
    l = len(results) - 1
    for label, getllm_result in results.iteritems():
        data = _tfs(os.path.join(getllm_result.path, filename))
        _plot_ax(x_column, y_column, err_column, l, i, data, label, ax1)
        if filename2 is not None:
            data2 = _tfs(os.path.join(getllm_result.path, filename2))
            _plot_ax(x2_column, y2_column, err2_column, l, i, data2, label, ax2)
        i += 1


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
            parameters["tl_loc"] = -.075
    if parameters["omctitle"] != "":
        parameters["tl_title"] = -0.05

    tightlayout = parameters["tightlayout_height"] + parameters["tl_loc"] + parameters["tl_title"]

    plt.tight_layout(rect=(.02,.02,.98, tightlayout), pad=0.5)

    f.show()

    if printit:
        f.savefig(parameters["ofile"])

def plot_lobster(command):
    """
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
    print "plotting LOBSTER"
    width = float(parameters["width"])
    height = width * .5

    px = parameters["plot_x"] == "1"
    py = parameters["plot_y"] == "1"

    y_label = r"$\Delta \Phi_x $ [mrad]"
    y_label2 = r"$\Delta \Phi_y $ [mrad]"
    x_label = "$ s\;[m]$"

    if px and py:
        f, [ax1,ax2] = plt.subplots(nrows=2, figsize=(width, height))
        setup_plot_area(parameters, ax2, model, y_label2, x_label, False)
        x_label = ""
    else:
        parameters["IPticks"] = "0"
        f, ax1 = plt.subplots(nrows=1, figsize=(width, height * .6))

    setup_plot_area(parameters, ax1, model, y_label, x_label, True)

    ax1.set_ylim(auto=True)

    i = 0
    l = len(results) - 1
    for label, getllm_result in results.iteritems():
        lobster = getllm_result.lobster
        if px and py:
            ax1.errorbar(lobster["S"], 1.0e3 * TWOPI * lobster["DELTAPHI_NEAR"],
                         1.0e3 * TWOPI * lobster["ERRPHI_NEAR"], linestyle='',
                         marker='.', label=label, markeredgecolor=colors[l-i][1],
                         color=colors[l-i][0])
        elif px:
            ax1.errorbar(lobster["S"], 1.0e3 * TWOPI * lobster["DELTAPHI_NEAR"],
                         1.0e3 * TWOPI * lobster["ERRPHI_NEAR"], linestyle='',
                         marker='.', label=label, markeredgecolor=colors[l-i][1],
                         color=colors[l-i][0])
        elif py:
            pass

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
            parameters["tl_loc"] = -.075
    if parameters["omctitle"] != "":
        parameters["tl_title"] = -0.05

    tightlayout = parameters["tightlayout_height"] + parameters["tl_loc"] + parameters["tl_title"]

    plt.tight_layout(rect=(.02,.02,.98, tightlayout), pad=0.5)

    f.show()

    if command == 'print':
        f.savefig(parameters["ofile"])

def save_commands(command):
    """Saves all commands typed in by the user until now. Loading and executing saved commands
should restore a previous session and enable replotting;
Usage:
    save FILE   prints the commands to the file FILE
    save        prints the commands to the file 'cmd'"""

    if command == "":
        path = "cmd"
    else:
        path = command

    with open(path, "w") as ofile:
        for cmd in commands:
            ofile.write(cmd + "\n")
    print "commands saved to {}".format(path)

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
terminal.add_command(aliases=['save'],
                     action=save_commands)
terminal.add_command(aliases=['plotlobster', 'plotl'],
                     action=plot_lobster)
terminal.add_command(aliases=['plot'],
                     action=plot_column)
terminal.add_command(aliases=['plotdisp'],
                     action=plot_disp_over_beta)
# --------------------------------------------------------------------------------------------------
# ---------- private functions ---------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------
def _tfs(path, index=None):
    if os.path.isfile(path):
        return tfs_pandas.read_tfs(path, index=index)
    else:
        print ("The file '{}' doesn't exist.".format(path) +
               " Do you want to chose an alternative? (no/path to file)")
        answer = raw_input("[in ] ")
        if answer == 'no':
            return None
        else:
            return _tfs(answer)

def _plot_ax(x_column, y_column, err_column, l, i, data, label, ax1):
    """Plots on the given axis
    """
    if "-" in y_column:
        cols = y_column.split('-')
        y_values = (data[cols[0]] - data[cols[1]]).values
    else:
        y_values = data[y_column]

    ax1.set_ylim(auto=True)

    if err_column == None:
        print "plotting points"
        print "x-axis = {}".format(x_column)
        print "y-axis = {}".format(y_column)
        ax1.plot(data[x_column], y_values, ' o', color=colors[l-i][0],
                 markeredgecolor=colors[l-i][1], label=label, markersize=4.0)
    else:
        print "plotting points"
        print "x-axis = {}".format(x_column)
        print "y-axis = {}".format(y_column)
        print "errors = {}".format(err_column)
        ax1.errorbar(data[x_column], y_values, data[err_column], fmt=' o', color=colors[l-i][0],
                 markeredgecolor=colors[l-i][1], label=label, markersize=4.0)
# --------------------------------------------------------------------------------------------------
# ---------- main loop -----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------

while CONT:
    try:
        command = raw_input("[in {}] ".format(cmd_nr))
        if terminal.run_command(command):
            cmd_nr = cmd_nr + 1
            commands.append(command)
        else:
            if command == "quit" or command == "exit" or command == "q":
                CONT = False
    except KeyboardInterrupt:
        print " -+-+-+-+-+-+-+-+-+ interrupt"
    except:
        _tb_()



