import sys
import os
sys.path.append("/home/awegsche/Beta-Beat.src/")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils import tfs_pandas

def setup_plot_area(params, ax1, tfsmodel, ylabel, xlabel):

    plt.rc('text', usetex=True)
    params["tightlayout_height"] = 1.0
    if params["style"] == "OMC":
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
    IPtickslabels = ["IP2","IP3","IP4","IP5","IP6","IP7","IP8","IP1"]
    if params["lhcbeam"] == "LHCB1":
        IPticks = [192.923, 3523.267, 6857.49, 10189.78, 13522.212, 16854.649, 20185.865, 23519.37]
    else:
        IPticks = [192.923, 3523.267, 6857.49, 10189.78, 13522.212, 16854.649, 20185.865, 23519.37]
    # try to find the positions of the IPs
    if params["accel"] == "LHC":
        for i in range(len( IPtickslabels)):
            IPticks[i] = tfsmodel.loc[IPtickslabels[i]]["S"]

    tightlayout_height = .98

    if params["accel"] == "JPARC":
        ax1.set_xlim(0, 1600)
    elif params["accel"] == "PETRA":
        ax1.set_xlim(0, 2350)
    elif params["accel"] == "CPS":
        ax1.set_xlim(0, 630)
    else:
        ax1.set_xlim(0,27000)
        if params["style"] == "OMC":
            #betabeating_.set_index("NAME").loc["IP1"]["S"]
            ax1.set_xticks(IPticks)
            ax1.set_xticklabels(IPtickslabels)

            ax1.xaxis.set_ticks_position('none') 
            if params["ipbars"] == "1":
                for x in IPticks:
                    ax1.plot((x, x), (-args.ylim, args.ylim), "-", color="#D0D0D0")
    if params['omctitle'] != "":
        ax1.text(1.0, 1.02, params['omctitle'], verticalalignment='bottom', horizontalalignment='right', transform=ax1.transAxes, fontsize=14)
        params["tightlayout_height"] -= 0.05

    if params['zoom'] != "all":
        zoom = params['zoom'].split(",")
        ax1.set_xlim(float(zoom[0]), float(zoom[1]))

    ax1.set_ylabel(ylabel)
    ax1.set_xlabel(xlabel)


def find_model(output_file):

    print ". . . . . . . . . ."
    print ". . . . .command: ."
    print output_file.headers["Command"]
    print ". . . . . . . . . ."
    tfsmodel = None
    
    commandargs = output_file.headers["Command"].split("' '")
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
                tfsmodel = tfs_pandas.read_tfs(modelpath, index="NAME")
                print "model found in input file 1. "
                return tfsmodel
    return None

def load_result(path):
    bbx = tfs_pandas.read_tfs(os.path.join(path, 'getbetax_free.out'), index="NAME")
    bby = tfs_pandas.read_tfs(os.path.join(path, 'getbetay_free.out'), index="NAME")

    dfx = bbx.loc[:, ["S", "BETXMDL"]]
    dfx.loc[:, "BBEAT"] = (bbx.loc[:, "BETX"] / bbx.loc[:, "BETXMDL"] - 1) * 100.0
    dfx.loc[:, "ERR"] = (bbx.loc[:, "ERRBETX"] / bbx.loc[:, "BETXMDL"]) * 100.0

    dfy = bby.loc[:, ["S", "BETYMDL"]]
    dfy.loc[:, "BBEAT"] = (bby.loc[:, "BETY"] / bby.loc[:, "BETYMDL"] - 1) * 100.0
    dfy.loc[:, "ERR"] = (bby.loc[:, "ERRBETY"] / bby.loc[:, "BETYMDL"]) * 100.0

    return bbx, bby, dfx, dfy

def plot_errorbar(ax, df, color, label, fmt):
    ax.errorbar(df["S"], df["BBEAT"], df["ERR"], label=label, c=color, fmt=fmt, markersize=3.0)

