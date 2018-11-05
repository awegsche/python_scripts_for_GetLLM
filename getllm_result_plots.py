import sys
import os

import betabeatsrc

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from utils import tfs_pandas

OFILELIST = [
    "getbetax.out",
    "getphasex.out",
    "getphasex_free.out",
    "getbetay.out",
    "getbetay_free.out",
    "getphasey_free.out",
    "getphasey.out"]

class GetLLMResult:
    def __init__(self, p):
        self.betax = None
        self.betay = None
        self.phasex = None
        self.phasey = None
        self.lobster = None
        self.path = p

def setup_plot_area(params, ax1, tfsmodel, ylabel, xlabel, plot_omctitle = True):

    params["plfmt"] = " o"
    if params["lines"] == "1":
        params["plfmt"] = "-o"

    ylim = float(params["ylim"])
    absolut = (params["absolut"] == "1")
    if ylim != -1:
        if not absolut:
            ax1.set_ylim(-ylim, ylim)
        else:
            ax1.set_ylim(0, ylim)
    else:
        ylim = 100000

    if params["accel"] == "LHC":
        IPtickslabels = [
            "\\textbf{{\\sffamily IP2}}", "\\textbf{{\\sffamily IP3}}", "\\textbf{{\\sffamily IP4}}",
            "\\textbf{{\\sffamily IP5}}", "\\textbf{{\\sffamily IP6}}", "\\textbf{{\\sffamily IP7}}",
            "\\textbf{{\\sffamily IP8}}", "\\textbf{{\\sffamily IP1}}"
        ]
        IPticknames = [
            "IP2", "IP3", "IP4", "IP5", "IP6", "IP7", "IP8", "IP1"
        ]
        if params["beam"] == "1":
            IPticks = [192.923, 3523.267, 6857.49, 10189.78, 13522.212, 16854.649, 20185.865, 23519.37]
        else:
            print " W A R N I N G: Beam2 fallback IPs have to be looked up"
            IPticks = [192.923, 3523.267, 6857.49, 10189.78, 13522.212, 16854.649, 20185.865, 23519.37]
        # try to find the positions of the IPs
        ticktup = []
        print " reading IP positions from model ..."
        for i in range(len( IPtickslabels)):
            ticktup.append([
                IPtickslabels[i],
                tfsmodel["S"].get(IPticknames[i], IPticks[i])
            ])


        ticktup.sort(key=lambda tup: tup[1])
        IPtickslabels = zip(*ticktup)[0]
        IPticks = zip(*ticktup)[1]

    if params["accel"] == "JPARC":
        ax1.set_xlim(0, 1600)
    elif params["accel"] == "PETRA":
        ax1.set_xlim(0, 2350)
    elif params["accel"] == "CPS":
        ax1.set_xlim(0, 630)
    elif params["accel"] == "SuperKEKB":
        ax1.set_xlim(0, 3020)
    else:
        ax1.set_xlim(0,27000)
        if params["IPticks"] == "1" and plot_omctitle:
                ax1.set_xticks(IPticks)
                ax1.set_xticklabels(IPtickslabels)
                ax1.xaxis.set_ticks_position('none')
                print "setting font weight"
                for label in ax1.xaxis.get_majorticklabels():
                    label.set_size(int(params["ip_fontsize"]))
                    label.set_weight("bold")
                    label.set_family("sans-serif")

        if params["ipbars"] == "1" and not params["style"] == "OMC":
            for x in IPticks:
                ax1.plot((x, x), (-ylim, ylim), "-", color="#D0D0D0")
    if params['omctitle'] != "" and plot_omctitle:
        ax1.text(1.0, 1.02, params['omctitle'], verticalalignment='bottom', horizontalalignment='right', transform=ax1.transAxes, fontsize=14)

    if params['zoom'] != "all":
        zoom = params['zoom'].split(",")
        ax1.set_xlim(float(zoom[0]), float(zoom[1]))

    ax1.set_ylabel(ylabel)
    ax1.set_xlabel(xlabel)


def find_model(outputfolder):

    tfsmodel = None

    if os.path.isfile(os.path.join(outputfolder, "themodel")):
        with open(os.path.join(outputfolder, "themodel")) as themodel:
            line = themodel.readline()
            print "model found in 'themodel' file"
            print "path = {}".format(line)
            tfsmodel = tfs_pandas.read_tfs(os.path.join(line, "twiss_elements.dat"), index="NAME")
        return tfsmodel

    output_filepath = os.path.join(outputfolder, "getbetax_free.out")
    i = 0
    while not os.path.isfile(output_filepath) and i < len(OFILELIST):
        output_filepath = os.path.join(outputfolder, OFILELIST[i])
        i = i + 1

    output_file = tfs_pandas.read_tfs(output_filepath)

    print ". . . . . . . . . ."
    print ". . . . .command: ."
    print output_file.headers["Command"]
    print ". . . . . . . . . ."

    commandargs = output_file.headers["Command"].split("' '")
    for i, comm in enumerate(commandargs):
        words = comm.split("=")
        if words[0] == "--model":
            if len(words) >= 2:
                words1 = words[1]
            else:
                words1 = commandargs[i+1]
            modelpath = os.path.dirname(words1) + "/twiss_elements.dat"
            print "looking for model in ", modelpath
            if os.path.isfile(modelpath):
                tfsmodel = tfs_pandas.read_tfs(modelpath, index="NAME")
                print "model found in input file 1. "
                return tfsmodel
    return None

def _load_beta_plane(path, plane):
    if os.path.isfile(os.path.join(path, 'getbeta{}_free.out'.format(plane))):
        xfilename = os.path.join(path, 'getbeta{}_free.out'.format(plane))
    elif os.path.isfile(os.path.join(path, 'getbeta{}.out'.format(plane))):
        xfilename = os.path.join(path, 'getbeta{}.out'.format(plane))
    else:
        return None
    bbx = tfs_pandas.read_tfs(xfilename, index="NAME")
    plane_ = plane.upper()

    dfx = bbx.loc[:, ["S", "BET{}MDL".format(plane_), "BET" + plane_]]
    dfx.loc[:, "BBEAT"] = (bbx.loc[:, "BET" + plane_] / bbx.loc[:, "BET{}MDL".format(plane_)] - 1) * 100.0
    #dfx.loc[:, "BBEAT"] = (bbx.loc[:, "BBEAT"] ) * 100.0
    dfx.loc[:, "ERR"] = (bbx.loc[:, "ERRBET" + plane_] / bbx.loc[:, "BET{}MDL".format(plane_)]) * 100.0
    return dfx

def load_result(path):
    getllm_result = GetLLMResult(path)
    getllm_result.betax = _load_beta_plane(path, "x")
    getllm_result.betay = _load_beta_plane(path, "y")
    if os.path.isfile(os.path.join(path, 'getlobster.out')):
        getllm_result.lobster = tfs_pandas.read_tfs(os.path.join(path, 'getlobster.out'), index="NAME")

    return getllm_result

def plot_errorbar(ax, df, color, label, fmt):
    ax.errorbar(df["S"], df["BBEAT"], df["ERR"], label=label, c=color[0], markeredgecolor=color[1], fmt=fmt, markersize=3.0)

