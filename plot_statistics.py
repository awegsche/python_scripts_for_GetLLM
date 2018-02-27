import sys
import os

sys.path.append("/afs/cern.ch/work/a/awegsche/public/workspace/GetLLMHelpers")
sys.path.append("/afs/cern.ch/work/a/awegsche/public/workspace/Beta-Beat.src")

#from Python_Classes4MAD import metaclass
import numpy as np
from subprocess import Popen
from shutil import copyfile, rmtree
import random


import matplotlib.pyplot as plt

import time

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from hlclasses import *
import matplotlib
from matplotlib import rc
from matplotlib import colors
from matplotlib.colors import LogNorm
from scipy.optimize import curve_fit
from numpy import exp


import argparse

import h5py
import pandas



def read_ascii():

    measurements = []
    measurementsArc = []
    measurementsIR = []
    measurementssmall = []
    
    
    tablefile = open(args.statisticsfilename, "r")
    for line_ in tablefile:
        m_ = BetXDataSingle()
        m_.read_from_file(line_)
        if m_.valid:
            if m_.region == "all":
                measurements.append(m_)
            if m_.region == "IR":
                measurementsIR.append(m_)
            if m_.region == "Arc":
                measurementsArc.append(m_)
            if m_.region == "small":
                measurementssmall.append(m_)
    tablefile.close()
    
    if args.oneplot:
        f_, ax_ = plt.subplots(nrows=1, ncols=1, squeeze=True, figsize=(args.width,args.width*.6))
    
        rc('font', **{'family': 'serif', 'serif': ['Times']})
        params = {'backend': 'pdf',
                  'axes.labelsize': 16,
                  'font.size': 16,
                  'axes.titlesize': 16,
                  'axes.labelsize': 16,
                  'legend.fontsize': 12,
                  'xtick.labelsize': 12,
                  'ytick.labelsize': 12,
                  'text.usetex': True,
                  'axes.unicode_minus': True,
                  'xtick.major.pad': 12,
                  'ytick.major.pad': 12,
                  'xtick.minor.pad': 12,
                  'ytick.minor.pad': 12
                  }
        matplotlib.rcParams.update(params)
    else:
        
        
        rc('font', **{'family': 'sans-serif', 'serif': ['Times']})
        params = {'backend': 'pdf',
                  'axes.labelsize': 16,
                  'font.size': 16,
                  'axes.titlesize': 16,
                  'axes.labelsize': 16,
                  'legend.fontsize': 14,
                  'xtick.labelsize': 14,
                  'ytick.labelsize': 14,
                  'text.usetex': True,
                  'axes.unicode_minus': True,
                  'xtick.major.pad': 4,
                  'ytick.major.pad': 4,
                  'xtick.minor.pad': 4,
                  'ytick.minor.pad': 4
                  }
        matplotlib.rcParams.update(params)
        

        if args.withandy:
            NROWS = 3
            height= .8
        else:
            NROWS = 2
            height= .6
        f_, ax_ = plt.subplots(nrows=NROWS, ncols=1, squeeze=True, figsize=(args.width,args.width * height))
    
        
       # rc('lines', dashed_pattern=(1,1))
        if args.logscale:
            for i in range(NROWS):
                ax_[i].set_yscale('log', nonposy='clip')
                ax_[i].set_ylim(0.7,5000)
    
        for i in range(NROWS-1):
            ax_[i].set_xticklabels([])
            
            tlabels = ax_[i].yaxis.get_ticklabels()
            for li in range(len(tlabels)):
             if li not in [3,4,5]:
                 tlabels[li].set_visible(False)
        
        tlabels = ax_[NROWS-1].yaxis.get_ticklabels()
        for li in range(len(tlabels)):
             if li not in [3,4,5]:
                 tlabels[li].set_visible(False)
    #    ax_.set_yscale('log', nonposy='clip')
    if args.withandy:
        
        plot_methods(measurements, "compare_NBPM_to_3BPM_{0:s}.pdf".format(args.title), label1="A. N-BPM all", label2="3-BPM all", label3="N-BPM all",
                                color1='#1020FF', color2='#FF2010', color3='#20FF10', lwidth=0.,
                                histmax=args.histmax, optics=args.optics, kick=args.kick*1.0e-4,
                                ax=ax_, f=f_, histtype='stepfilled', alfa=.5)
    
        plot_methods(measurementsIR, "compare_NBPM_to_3BPM_{0:s}_ir.pdf".format(args.title), figs=(args.width,args.width*.6), label1="A. N-BPM IR", label2="3-BPM IR", label3="N-BPM IR",
                                color1='#0000FF', color2='#FF0000', color3='#00A000', lwidth=1.5, histmax=args.histmax, optics=args.optics, kick=args.kick*1.0e-4,
                                ax=ax_, f=f_, linetype='-')
    
        plot_methods(measurementsArc, "compare_NBPM_to_3BPM_{0:s}_arc.pdf".format(args.title), figs=(args.width,args.width*.6), label1="A. N-BPM Arc", label2="3-BPM Arc", label3="N-BPM Arc",
                                color1='#0000FF', color2='#FF0000', color3='#00A000', lwidth=1.5, histmax=args.histmax, optics=args.optics, kick=args.kick*1.0e-4,
                                ax=ax_, f=f_, linetype=(0,(3,2)))
       
    else:
        plot_nbpm_vs_3bpm(measurements, "compare_NBPM_to_3BPM_{0:s}.pdf".format(args.title), label1="A. N-BPM all", label2="3-BPM all",
                                color1='b', edgecolor1="#9090BF", color2='r', edgecolor2="#BF0090", lwidth=0.,
                                histmax=args.histmax, optics=args.optics, kick=args.kick*1.0e-4,
                                ax=ax_, f=f_, histtype='stepfilled', alfa=.5)
    
        plot_nbpm_vs_3bpm(measurementsIR, "compare_NBPM_to_3BPM_{0:s}_ir.pdf".format(args.title), figs=(args.width,args.width*.6), label1="A. N-BPM IR", label2="3-BPM IR",
                                color1='#0000FF', color2='#FF0000', lwidth=1.5, histmax=args.histmax, optics=args.optics, kick=args.kick*1.0e-4,
                                ax=ax_, f=f_, linetype='-')
    
        plot_nbpm_vs_3bpm(measurementsArc, "compare_NBPM_to_3BPM_{0:s}_arc.pdf".format(args.title), figs=(args.width,args.width*.6), label1="A. N-BPM Arc", label2="3-BPM Arc",
                                color1='#0000FF', color2='#FF0000', lwidth=1.5, histmax=args.histmax, optics=args.optics, kick=args.kick*1.0e-4,
                                ax=ax_, f=f_, linetype=(0,(3,2)))
    f_.tight_layout(h_pad=.0)
    
        
    
    f_.savefig("comparison_statistics_{0:s}.pdf".format(args.title))
    
    
def read_hd5_v1():
    
    threebpm_diff_arc = []
    threebpm_diff_IR = []
    a_nbpm_diff_arc = []
    a_nbpm_diff_IR = []
    mc_nbpm_diff_IR = []
    mc_nbpm_diff_arc = []
        
    tablefile = h5py.File(args.statisticsfilename, "r")
    
    for (name,sim) in tablefile["simulations"].iteritems():
        a_nbpm_diff_arc = np.append(a_nbpm_diff_arc, np.absolute(sim["nbpm/Arc/diff"]))
        a_nbpm_diff_IR = np.append(a_nbpm_diff_IR, np.absolute(sim["nbpm/IR/diff"]))
        threebpm_diff_arc = np.append(threebpm_diff_arc, np.absolute(sim["3bpm/Arc/diff"]))
        threebpm_diff_IR = np.append(threebpm_diff_IR, np.absolute(sim["3bpm/IR/diff"]))

        
    tablefile.close()
    
#    if args.oneplot:
#        f_, ax_ = plt.subplots(nrows=1, ncols=1, squeeze=True, figsize=(args.width,args.width*.6))
#    
#        rc('font', **{'family': 'sans-serif', 'serif': ['Computer Modern']})
#        params = {'backend': 'pdf',
#                  'axes.labelsize': 16,
#                  'font.size': 16,
#                  'axes.titlesize': 16,
#                  'legend.fontsize': 12,
#                  'xtick.labelsize': 16,
#                  'ytick.labelsize': 16,
#                  'text.usetex': False,
#                  'axes.unicode_minus': True,
#                  'xtick.major.pad': 12,
#                  'ytick.major.pad': 12,
#                  'xtick.minor.pad': 12,
#                  'ytick.minor.pad': 12
#                  }
#        matplotlib.rcParams.update(params)
#    else:
        
    rc('font', **{'family': 'sans', 'serif': ['Times']})
    params = {'backend': 'pdf',
              'axes.labelsize': 16,
              'font.size': 16,
              'axes.titlesize': 16,
              'legend.fontsize': 12,
              'xtick.labelsize': 12,
              'ytick.labelsize': 14,
              'text.usetex': True,
              'axes.unicode_minus': True,
              'xtick.major.pad': 6,
              'ytick.major.pad': 2,
              'xtick.minor.pad': 6,
              'ytick.minor.pad': 2
              }
    matplotlib.rcParams.update(params)
    
    if args.withandy:
        NROWS = 3
    else:
        NROWS = 2
    f, ax= plt.subplots(nrows=NROWS, ncols=1, squeeze=True, figsize=(args.width,args.width*.6))

    
   # rc('lines', dashed_pattern=(1,1))
    if args.logscale:
        for i in range(NROWS):
            ax[i].set_yscale('log', nonposy='clip')
            ax[i].set_ylim(0.7,5000)


    
    title= "compare_NBPM_to_3BPM_{0:s}.pdf".format(args.title)
    label1="3-BPM"
    label2="N-BPM",
    label3="A. N-BPM"
    color1='#FF2010'
    color2='#20FF10'
    color3='#1020FF'
#    edgecolor1='#9F2010'
#    edgecolor2='#209F10'
#    edgecolor3='#10209F'
    edgecolor1='#FF2010'
    edgecolor2='#20FF10'
    edgecolor3='#1020FF'
    linetype="-"
    lwidth=0.
    histmax=args.histmax
    optics=args.optics
    kick=args.kick*1.0e-4
    histtype='bar'
    alfa=.5
    histbarwidth=.5
    
    
        
        

    # ==================================================================================
    # ========== PLOT ==================================================================
    # ==================================================================================
    
    print "====== plotting ========="
    print "nbpm:    {0:4d} simulations".format(len(a_nbpm_diff_arc) + len(a_nbpm_diff_IR))
    print "mc-nbpm: {0:4d} simulations".format(len(mc_nbpm_diff_arc) + len(mc_nbpm_diff_IR))
    print "3bpm:    {0:4d} simulations\n".format(len(threebpm_diff_arc) + len(threebpm_diff_IR))
    
    #print deviation3bpm
    

    
    #ax[NROWS-1].set_xlabel(r"Deviation of measured $\beta$ [\%]")

    ax[0].set_yticks(np.arange(1e4, 1e5, 1e4)) 
    ax[1].set_yticks(np.arange(2e4, 2e5, 2e4))
    ax[0].set_ylim(0, 5.5e4)
    ax[1].set_ylim(0, 8.5e4)

    ax[1].set_xlabel(r"Deviation of measured $\beta$ [\%]")

   # ax1.set_ylabel("count")
    ax[0].set_ylabel("count")
    ax[1].set_ylabel("count")

    ax[0].set_xticklabels([])

    mybins = np.arange(0, histmax, histmax / 60.0)
    
    ax_3bpm = ax[0]
    if args.withandy:
        ax_mcnbpm = ax[1]
        ax_anbpm = ax[2]
    else:
        ax_anbpm = ax[1]

    ax_3bpm.hist(threebpm_diff_arc, bins=mybins,
             normed=False, label=label1 + " arc, $\sigma = {:.2f}$".format(np.std(threebpm_diff_arc)),
             color=color1, edgecolor=edgecolor1, histtype=histtype,
             linestyle=linetype, alpha=alfa)
    ax_anbpm.hist(a_nbpm_diff_arc, bins=mybins,
             normed=False, label=label3 + " arc, $\sigma = {:.2f}$".format(np.std(a_nbpm_diff_arc)), 
            color=color3, edgecolor=edgecolor3, histtype=histtype,
            linestyle=linetype, alpha=alfa)
    if args.withandy:
        ax_mcnbpm.hist(mc_nbpm_diff_arc,bins=mybins,
                 normed=False, label=label2 + " arc, $\sigma = {:.2f}$".format(np.std(mc_nbpm_diff_arc)), 
                color=color2, edgecolor=edgecolor2, histtype=histtype,
                linestyle=linetype, alpha=alfa)

    color1='#9F2010'
    color2='#209F10'
    color3='#10209F'
    edgecolor1='#9F2010'
    edgecolor2='#209F10'
    edgecolor3='#10209F'


    ax_3bpm.hist(threebpm_diff_IR, bins=mybins + (histmax/120.0*histbarwidth), width=(histmax/60.0*histbarwidth), 
            normed=False, label=label1 + " IR, $\sigma = {:.2f}$".format(np.std(threebpm_diff_IR)), 
            color=color1, edgecolor=edgecolor1, histtype=histtype,
            linestyle=linetype, alpha=alfa)
    ax_anbpm.hist(a_nbpm_diff_IR, bins=mybins + (histmax/120.0*histbarwidth), width=(histmax/60.0*histbarwidth),
             normed=False, label=label3 + " IR, $\sigma = {:.2f}$".format(np.std(a_nbpm_diff_IR)), 
            color=color3, edgecolor=edgecolor3, histtype=histtype,
            linestyle=linetype, alpha=alfa)
    if args.withandy:
        ax_mcnbpm.hist(mc_nbpm_diff_IR,bins=mybins + (histmax/120.0*histbarwidth), width=(histmax/60.0*histbarwidth),
                 normed=False, label=label2 + " IR, $\sigma = {:.2f}$".format(np.std(mc_nbpm_diff_IR)), 
                color=color2, edgecolor=edgecolor2, histtype=histtype,
                linestyle=linetype, alpha=alfa)


   
    for a_ in range(NROWS):
        ax[a_].legend()
       
  
    f.tight_layout(h_pad=.0)
    
        
    
    f.savefig("comparison_statistics_{0:s}.pdf".format(args.title))
    
    
def moving_average(x, n, x_new):
    return (x * (n - 1) + x_new) / n
    
    
def read_hd5_v2():
    
    threebpm_diff_arc = []
    threebpm_diff_IR = []
    a_nbpm_diff_arc = []
    a_nbpm_diff_IR = []
    mc_nbpm_diff_IR = []
    mc_nbpm_diff_arc = []

    a_nbpm_ncomb = {}
    mc_nbpm_ncomb = {}


    for i in range(3, 46):
        a_nbpm_ncomb[i] = {}
        mc_nbpm_ncomb[i] = {}

        
    tablefile = h5py.File(args.statisticsfilename, "r")
    
    for (name,sim) in tablefile["simulations"].iteritems():
        #print "open", name
        a_nbpm_diff_arc = np.append(a_nbpm_diff_arc, sim["nbpm/Arc/diff"])
        a_nbpm_diff_IR = np.append(a_nbpm_diff_IR, sim["nbpm/IR/diff"])
        threebpm_diff_arc = np.append(threebpm_diff_arc, sim["3bpm/Arc/diff"])
        threebpm_diff_IR = np.append(threebpm_diff_IR, sim["3bpm/IR/diff"])
        
        ncombnode = "nbpm/Arc/ncomb"
        if ncombnode in sim:
            _n = sim[ncombnode]
            for i in range(len(_n)):
                a_nbpm_ncomb[_n[i]].append(sim["nbpm/Arc/diff"][i])
            

        
    tablefile.close()
    
#    if args.oneplot:
#        f_, ax_ = plt.subplots(nrows=1, ncols=1, squeeze=True, figsize=(args.width,args.width*.6))
#    
#        rc('font', **{'family': 'sans-serif', 'serif': ['Computer Modern']})
#        params = {'backend': 'pdf',
#                  'axes.labelsize': 16,
#                  'font.size': 16,
#                  'axes.titlesize': 16,
#                  'legend.fontsize': 12,
#                  'xtick.labelsize': 16,
#                  'ytick.labelsize': 16,
#                  'text.usetex': False,
#                  'axes.unicode_minus': True,
#                  'xtick.major.pad': 12,
#                  'ytick.major.pad': 12,
#                  'xtick.minor.pad': 12,
#                  'ytick.minor.pad': 12
#                  }
#        matplotlib.rcParams.update(params)
#    else:
        
    rc('font', **{'family': 'serif', 'serif': ['Times']})
    params = {'backend': 'pdf',
              'axes.labelsize': 16,
              'font.size': 16,
              'axes.titlesize': 16,
              'legend.fontsize': 12,
              'xtick.labelsize': 12,
              'ytick.labelsize': 14,
              'text.usetex': True,
              'axes.unicode_minus': True,
              'xtick.major.pad': 6,
              'ytick.major.pad': 2,
              'xtick.minor.pad': 6,
              'ytick.minor.pad': 2
              }
    matplotlib.rcParams.update(params)
    
    
    f, ax= plt.subplots(nrows=2, ncols=1, squeeze=True, figsize=(args.width,args.width*.6))

  

    
    title= "compare_NBPM_to_3BPM_{0:s}.pdf".format(args.title)
    label1="3-BPM"
    label2="N-BPM",
    label3="A. N-BPM"
    color1='#FF2010'
    color2='#20FF10'
    color3='#1020FF'
#    edgecolor1='#9F2010'
#    edgecolor2='#209F10'
#    edgecolor3='#10209F'
    edgecolor1='#FF2010'
    edgecolor2='#20FF10'
    edgecolor3='#1020FF'
    linetype="-"
    lwidth=0.
    histmax=args.histmax
    optics=args.optics
    kick=args.kick*1.0e-4
    histtype='bar'
    alfa=.75
    histbarwidth=.5
    
    
        
        

    # ==================================================================================
    # ========== PLOT ==================================================================
    # ==================================================================================
    
    print "====== plotting ========="
    print "nbpm:    {0:6d} simulations,\n    arc: std = {1:f}\n     IR: std = {2:f}".format(len(a_nbpm_diff_arc) + len(a_nbpm_diff_IR), np.std(a_nbpm_diff_arc), np.std(a_nbpm_diff_IR))
    if args.withandy:
        print "mc-nbpm: {0:6d} simulations\n    arc: std = {1:f}\n     IR: std = {2:f}".format(len(mc_nbpm_diff_arc) + len(mc_nbpm_diff_IR), np.std(mc_nbpm_diff_arc), np.std(mc_nbpm_diff_IR))
    print "3bpm:    {0:6d} simulations\n    arc: std = {1:f}\n     IR: std = {2:f}\n".format(len(threebpm_diff_arc) + len(threebpm_diff_IR), np.std(threebpm_diff_arc), np.std(threebpm_diff_IR))
    
    #print deviation3bpm
    

    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
   
    #ax[0].set_yticks(np.arange(0, 1e5, 2e4)) 
    #ax[1].set_yticks(np.arange(0, 1e5, 1e4))
    #ax[0].set_ylim(0, 10e4)
    #ax[1].set_ylim(0, 5e4) 
    ax[1].set_xlabel(r"Deviation of measured $\beta$ [\%]")

   # ax1.set_ylabel("count")
#    ax[0].set_ylabel("count [normalized]")
#    ax[1].set_ylabel("count [normalized]")
    f.text(-.0, .5, "count [normalized]", va="center", rotation="vertical")

    #ax3.set_ylabel("count")
    
    mybins = np.arange(-histmax, histmax, histmax / 40.0)
   

   
    ax[0].hist(threebpm_diff_arc, bins=mybins,
             normed=True, label=label1 + " arc, $\sigma = {:.2f}$".format(np.std(threebpm_diff_arc)), 
             color=color1, edgecolor=edgecolor1, histtype=histtype,
             linestyle=linetype, alpha=alfa)
    ax[0].hist(a_nbpm_diff_arc, bins=mybins+ (histmax/120.0*histbarwidth), width=(histmax/60.0*histbarwidth),
             normed=True, label=label3 + " arc, $\sigma= {:.2f}$".format(np.std(a_nbpm_diff_arc)), 
            color=color3, edgecolor=edgecolor3, histtype=histtype,
            linestyle=linetype, alpha=alfa)
    if args.withandy:
        ax[0].hist(mc_nbpm_diff_arc,bins=mybins,
                 normed=True, label=label2 + " arc, $\sigma= {:.2f}$".format(np.std(mc_nbpm_diff_arc)), 
                color=color2, edgecolor=edgecolor2, histtype=histtype,
                linestyle=linetype, alpha=alfa)
    ax[0].get_xaxis().set_visible(False)

    

#    ax[0].plot(mybins, matplotlib.mlab.normpdf(mybins, 0, np.std(threebpm_diff_arc)), color=color1, label="fit 3-BPM")  
#    ax[0].plot(mybins, matplotlib.mlab.normpdf(mybins, 0, np.std(a_nbpm_diff_arc)), color=color3, label="fit 3-BPM")  
#    ax[1].plot(mybins, matplotlib.mlab.normpdf(mybins, 0, np.std(threebpm_diff_IR)), color=color1, label="fit N-BPM")  
#    ax[1].plot(mybins, matplotlib.mlab.normpdf(mybins, 0, np.std(a_nbpm_diff_IR)), color=color3, label="fit N-BPM")  

#    color1='#9F2010'
#    color2='#209F10'
#    color3='#10209F'
#    edgecolor1='#9F2010'
#    edgecolor2='#209F10'
#    edgecolor3='#10209F'


    ax[1].hist(threebpm_diff_IR, bins=mybins, 
            normed=True, label=label1 + " IR, $\sigma= {:.2f}$".format(np.std(threebpm_diff_IR)), 
            color=color1, edgecolor=edgecolor1, histtype=histtype,
            linestyle=linetype, alpha=alfa)
    ax[1].hist(a_nbpm_diff_IR, bins=mybins + (histmax/120.0*histbarwidth), width=(histmax/60.0*histbarwidth),
             normed=True, label=label3 + " IR, $\sigma= {:.2f}$".format(np.std(a_nbpm_diff_IR)), 
            color=color3, edgecolor=edgecolor3, histtype=histtype,
            linestyle=linetype, alpha=alfa)
    if args.withandy:
        ax[1].hist(mc_nbpm_diff_IR,bins=mybins + (histmax/120.0*histbarwidth), width=(histmax/60.0*histbarwidth),
                 normed=True, label=label2 + " IR, $\sigma= {:.2f}$".format(np.std(mc_nbpm_diff_IR)), 
                color=color2, edgecolor=edgecolor2, histtype=histtype,
                linestyle=linetype, alpha=alfa)


   
    for a_ in range(2):
        ax[a_].legend()
       
  
    f.tight_layout(h_pad=.0)
    
        
    
    f.savefig("comparison_statistics_{0:s}.pdf".format(args.title))
    
    
    # =============== plot BPM combinations:
        
        
docut = True  


def remove_nan_onedim(diff3):
    onedim = np.ravel(diff3.astype(np.dtype(np.float)))
    return onedim[np.logical_not(np.isnan(onedim))]      
    

def get_arc(diff, diffbool, err=None, CUT=1e10):
    if docut:
        diff1 = diff.where(diffbool == "arc")
        diff2 = diff1.where(diff1 > -CUT)
        diff3 = diff2.where(diff2 < CUT)
#        diff3 = diff3.dropna()
       
        
#        err = np.ravel(err.where(diff3.notnull()).astype(np.dtype(np.float)))
        onedim = np.ravel(diff3.astype(np.dtype(np.float)))
        return onedim[np.logical_not(np.isnan(onedim))]
    else:
        return np.ravel(diff.where(diffbool == "arc")).dropna()
    
    
def get_ir(diff, diffbool, err=None, CUT=1e10):
    if docut:
        diff1 = diff.where(diffbool == "IR")
        diff2 = diff1.where(diff1 > -CUT)
        diff3 = diff2.where(diff2 < CUT)
        
#        diff3 = diff3.dropna()
#        err = np.ravel(err.where(diff3.notnull()).astype(np.dtype(np.float)))
        onedim = np.ravel(diff3.astype(np.dtype(np.float)))
        return onedim[np.logical_not(np.isnan(onedim))]
        
    else:
        return np.ravel(diff.where(diffbool == "IR").dropna())
        
def rms(array):
    return np.sqrt(np.mean(array * array))
    
    
def plot_hist_err(X1, X2, X3, Y1, Y2, Y3, histmax, width):
    
     
    title= "compare_NBPM_to_3BPM_{0:s}.pdf".format(args.title)
    label1="3-BPM"
    label2="N-BPM"
    label3="A. N-BPM"
    color1='#FF2010'
    color2='#20AF10'
    color3='#1020FF'
#    edgecolor1='#9F2010'
#    edgecolor2='#209F10'
#    edgecolor3='#10209F'
    edgecolor1=color1
    edgecolor2=color2
    edgecolor3=color3
    linetype="-"
    histtype='step'
    alfa=1
    lwidth=2
    histbarwidth=.2
    histbarwidthMC=.6

    
    
    f, ax= plt.subplots(nrows=2, ncols=1, squeeze=True, figsize=(args.width,args.width*.6))  
    ax[1].set_xlabel(r"Deviation of measured $\beta$ [\%]")
    f.text(-.0, .5, "count [normalized]", va="center", rotation="vertical")

    
    mybins = np.arange(0, histmax*1.5, width)
   
    _normed = False
   
   
    ax[0].hist(X1, bins=mybins,
             normed=_normed, label=label1 + " arc", 
             color=color1, edgecolor=edgecolor1, histtype=histtype,
             linestyle=linetype, alpha=alfa, linewidth=lwidth)
    if args.withandy:
        ax[0].hist(X2,bins=mybins + (width*(0.5 - 0.5 * histbarwidthMC)), #width=(width*histbarwidthMC),
                 normed=_normed, label=label2 + " arc", 
                color=color2, edgecolor=edgecolor2, histtype=histtype,
                linestyle=linetype, alpha=alfa, linewidth=lwidth)
#        ax[0].hist(a_nbpmtight_diff_arc,bins=mybins + (width*(0.5 - 0.5 * histbarwidthMC)), #width=(width*histbarwidthMC),
#                 normed=True, label="N-BPM () arc",
#                color=color2, edgecolor="#105050", histtype=histtype,
#                linestyle=linetype, alpha=alfa, linewidth=lwidth)
    ax[0].hist(X3, bins=mybins + (width*(0.5 - 0.5 * histbarwidth)),# width=(width*histbarwidth),
             normed=_normed, label=label3 + " arc", 
            color=color3, edgecolor=edgecolor3, histtype=histtype,
            linestyle=linetype, alpha=alfa, linewidth=lwidth)
    ax[0].get_xaxis().set_visible(False)

    ax[1].hist(Y1, bins=mybins, 
            normed=_normed, label=label1 + " IR", 
            color=color1, edgecolor=edgecolor1, histtype=histtype,
            linestyle=linetype, alpha=alfa, linewidth=lwidth)
    if args.withandy:
        ax[1].hist(Y2,bins=mybins + (width*(0.5 - 0.5 * histbarwidthMC)), #width=(width*histbarwidthMC),
                 normed=_normed, label=label2 + " IR", 
                color=color2, edgecolor=edgecolor2, histtype=histtype,
                linestyle=linetype, alpha=alfa, linewidth=lwidth)
#        ax[1].hist(a_nbpmtight_diff_IR, bins=mybins + (width*(0.5 - 0.5 * histbarwidth)), #width=(width*histbarwidth),
#                 normed=True, label="N-BPM () IR", 
#                color=color3, edgecolor="#105050", histtype=histtype,
#                linestyle=linetype, alpha=alfa, linewidth=lwidth)

    ax[1].hist(Y3, bins=mybins + (width*(0.5 - 0.5 * histbarwidth)), #width=(width*histbarwidth),
             normed=_normed, label=label3 + " IR", 
            color=color3, edgecolor=edgecolor3, histtype=histtype,
            linestyle=linetype, alpha=alfa, linewidth=lwidth)

    f.show()
    raw_input()
    
def print_quantile(ir):
    print "    within 1 sigma (68%): {:6.3f}".format(ir[int(0.682689492137*len(ir))])
    print "    within 2 sigma (84%): {:6.3f}".format(ir[int(0.8427*len(ir))])
    print "    within          90% : {:6.3f}".format(ir[int(0.9*len(ir))])
    print "    within 3 sigma (92%): {:6.3f}".format(ir[int(0.9167*len(ir))])
    print "    within          95% : {:6.3f}".format(ir[int(0.95*len(ir))])
    print "    within 4 sigma (95%): {:6.3f}".format(ir[int(0.9545*len(ir))])
    print "    within 5 sigma (97%): {:6.3f}".format(ir[int(0.9747*len(ir))])
    print "    within          99% :  {:6.3f}".format(ir[int(0.99*len(ir))])


    
def print_quantiles(ir, arc):
    print "  IR:"
    print_quantile(ir)
    print "  arc:"
    print_quantile(arc)

    
    
def bar_plot(ax,
             ARC_Bar1, ARC_Bar2, ARC_Bar3,
             IR_Bar1, IR_Bar2, IR_Bar3,
             barwidth, margin, lwidth, legend,
             color1, edgecolor1, color2, edgecolor2, color3, edgecolor3):
    
    ax.bar(np.arange(2) + 0.5 - barwidth * 1.5 - margin,
            [ARC_Bar1,
            IR_Bar1],
            width=barwidth,
            label="3-BPM",
            color=color1, edgecolor=edgecolor1, linewidth=lwidth)
    ax.bar(np.arange(2) + 0.5-barwidth*.5,
            [ARC_Bar2,
            IR_Bar2],
            width=barwidth,
            label="N-BPM",
            color=color2, edgecolor=edgecolor2, linewidth=lwidth)
#    ax.bar(np.arange(2) + 0.5-barwidth*.5,
#            [stda_nbpmtight_diff_arc,
#            stda_nbpmtight_diff_IR],
#            width=barwidth-margin*.5,
#            label="N-BPM with 10000 sims",
#            color="#00D0D0", edgecolor="#105050", linewidth=lwidth)
    ax.bar(np.arange(2) + 0.5 + barwidth * .5 + margin,
            [ARC_Bar3,
            IR_Bar3],
            width=barwidth,
            label="A. N-BPM",
            color=color3, edgecolor=edgecolor3, linewidth=lwidth)
    ax.set_xticks([.5, 1.5])
    ax.set_xticklabels(("Arc", "IR"))
    
    ax.set_ylabel(r"$\sigma$ [\%]")
    
    maxheight = max(IR_Bar1, IR_Bar2)
    
    ax.set_yticks(np.arange(1, 20, 1))
    if maxheight > 2:
        ax.set_yticks(np.arange(1.0001, 20., 2.))
        
    
    
    ax.set_ylim(0, maxheight * 1.05)
    
    if legend:
        ax.legend(bbox_to_anchor=(.55, 1))
       # ax.get_xaxis().set_visible(False)
       
def accuracy_bar_plot(ax,
             ARC_Bar1, ARC_Bar2, ARC_Bar3,
             IR_Bar1, IR_Bar2, IR_Bar3,
             barwidth, margin, lwidth, legend,
             color1, edgecolor1, color2, edgecolor2, color3, edgecolor3):
    
    ax.bar(np.arange(2) + 0.5 - barwidth * 1.5 - margin,
            [abs(ARC_Bar1),
            abs(IR_Bar1)],
            width=barwidth,
            label="3-BPM",
            color=color1, edgecolor=edgecolor1, linewidth=lwidth)
    ax.bar(np.arange(2) + 0.5-barwidth*.5,
            [abs(ARC_Bar2),
            abs(IR_Bar2)],
            width=barwidth,
            label="N-BPM",
            color=color2, edgecolor=edgecolor2, linewidth=lwidth)
#    ax.bar(np.arange(2) + 0.5-barwidth*.5,
#            [stda_nbpmtight_diff_arc,
#            stda_nbpmtight_diff_IR],
#            width=barwidth-margin*.5,
#            label="N-BPM with 10000 sims",
#            color="#00D0D0", edgecolor="#105050", linewidth=lwidth)
    ax.bar(np.arange(2) + 0.5 + barwidth * .5 + margin,
            [abs(ARC_Bar3),
            abs(IR_Bar3)],
            width=barwidth,
            label="A. N-BPM",
            color=color3, edgecolor=edgecolor3, linewidth=lwidth)
    ax.set_xticks([.5, 1.5])
    ax.set_xticklabels(("Arc", "IR"))
    
    ax.set_ylabel(r"accuracy [\%]")
    
    maxheight = max(IR_Bar1, IR_Bar2)
    
#    ax.set_yticks(np.arange(1, 20, 1))
#    if maxheight > 2:
#        ax.set_yticks(np.arange(1.0001, 20., 2.))
#      
    if legend:
        ax.legend(bbox_to_anchor=(.55, 1))
       # ax.get_xaxis().set_visible(False)
       
COLOR_3BPM          = '#FF2010'
COLOR_MC_NBPM       = '#20AF10'
COLOR_A_NBPM        = '#1020FF'

EDGECOLOR_3BPM      = '#802010'
EDGECOLOR_MC_NBPM   = '#205010'
EDGECOLOR_A_NBPM    = '#102050'

COLOR_3BPM_QUANT        = '#FFA010'
COLOR_MC_NBPM_QUANT     = '#A0AF10'
COLOR_A_NBPM_QUANT      = '#10A0FF'

EDGECOLOR_3BPM_QUANT    = '#805010'
EDGECOLOR_MC_NBPM_QUANT = '#405010'
EDGECOLOR_A_NBPM_QUANT  = '#104050'


       
def sixbar_plot(ax,
             ARC_Bar1, ARC_Bar2, ARC_Bar3,
             ARC_Bar1qu, ARC_Bar2qu, ARC_Bar3qu,
             IR_Bar1, IR_Bar2, IR_Bar3,
             IR_Bar1qu, IR_Bar2qu, IR_Bar3qu,
             barwidth, margin, lwidth, legend):
    
    sep = barwidth / 2
    ax.bar([-1.25 - sep - margin, .25 - sep + margin],
            [ARC_Bar1,
            IR_Bar1],
            width=barwidth,
            label="3-BPM error bar",
            color=COLOR_3BPM, edgecolor=EDGECOLOR_3BPM, linewidth=lwidth)
    
    ax.bar([-.75 - sep- margin, .75 - sep+ margin],
            [ARC_Bar2,
            IR_Bar2],
            width=barwidth,
            label="N-BPM error bar",
            color=COLOR_MC_NBPM, edgecolor=EDGECOLOR_MC_NBPM, linewidth=lwidth)
#    ax.bar(np.arange(2) + 0.5-barwidth*.5,
#            [stda_nbpmtight_diff_arc,
#            stda_nbpmtight_diff_IR],
#            width=barwidth-margin*.5,
#            label="N-BPM with 10000 sims",
#            color="#00D0D0", edgecolor="#105050", linewidth=lwidth)
    ax.bar([-.25 - sep- margin, 1.25 - sep+ margin],
            [ARC_Bar3,
            IR_Bar3],
            width=barwidth,
            label="A. N-BPM error bar",
            color=COLOR_A_NBPM, edgecolor=EDGECOLOR_A_NBPM, linewidth=lwidth)
    ax.bar([-1.25 + sep- margin, .25 + sep+ margin],
            [ARC_Bar1qu,
            IR_Bar1qu],
            width=barwidth,
            label="3-BPM accuracy spread",
            color=COLOR_3BPM_QUANT, edgecolor=EDGECOLOR_3BPM_QUANT, linewidth=lwidth)
    ax.bar([-.75 + sep- margin, .75 + sep+ margin],
            [ARC_Bar2qu,
            IR_Bar2qu],
            width=barwidth,     
            label="N-BPM accuracy spread",
            color=COLOR_MC_NBPM_QUANT, edgecolor=EDGECOLOR_MC_NBPM_QUANT, linewidth=lwidth)
    ax.bar([-.25 + sep- margin, 1.25 + sep+ margin],
            [ARC_Bar3qu,
            IR_Bar3qu],
            width=barwidth,
            label="A. N-BPM accuracy spread",
            color=COLOR_A_NBPM_QUANT, edgecolor=EDGECOLOR_A_NBPM_QUANT, linewidth=lwidth)
    ax.set_xticks([-.75- margin, .75+margin])
    ax.set_xticklabels(("Arc", "IR"))
    ax.set_xlim(-1.6- margin, 1.9 + margin)
    
    ax.set_ylabel(r"$\sigma$ [\%]")
    
    
    
    #ax.set_yticks(np.arange(1, 20, 1))
#    if maxheight > 2:
#        ax.set_yticks(np.arange(1.0001, 20., 2.))
#        
    
    
    
    
   
       # ax.get_xaxis().set_visible(False)
            
def twobar_plot(ax,
             ARC_Bar1, ARC_Bar2, 
             IR_Bar1, IR_Bar2, 
             barwidth, margin, lwidth, legend,
             color1, edgecolor1, color2, edgecolor2, ):
    
    ax.bar(np.arange(2) + 0.5 - barwidth * 1 - margin,
            [ARC_Bar1,
            IR_Bar1],
            width=barwidth,
            label="3-BPM",
            color=color1, edgecolor=edgecolor1, linewidth=lwidth)
    ax.bar(np.arange(2) + 0.5 + margin,
            [ARC_Bar2,
            IR_Bar2],
            width=barwidth,
            label="A. N-BPM",
            color=color2, edgecolor=edgecolor2, linewidth=lwidth)
#    ax.bar(np.arange(2) + 0.5-barwidth*.5,
#            [stda_nbpmtight_diff_arc,
#            stda_nbpmtight_diff_IR],
#            width=barwidth-margin*.5,
#            label="N-BPM with 10000 sims",
#
    ax.set_xticks([.5, 1.5])
    ax.set_xticklabels(("Arc", "IR"))
    
    ax.set_ylabel(r"$\sigma$ [\%]")
    
    maxheight = max(IR_Bar1, IR_Bar2)
    
    ax.set_yticks(np.arange(1, 20, 1))
    if maxheight > 2:
        ax.set_yticks(np.arange(1.0001, 20., 2.))
        
    
    
    ax.set_ylim(0, maxheight * 1.05)
    
    if legend:
        ax.legend(loc=9)
       # ax.get_xaxis().set_visible(False)
       
def gaus(x,a,x0,sigma):
    return a*exp(-(x-x0)**2/(2*sigma**2))
    
def fit(bins, n, cut_bins=0):
    mean = 0.0
    sigma = 1.0
    return curve_fit(gaus, 0.5 * (
            bins[1 + cut_bins:len(bins) - cut_bins] + bins[cut_bins:len(n)-cut_bins]),
            n[cut_bins:len(n) - cut_bins],
            p0 = [1, mean, sigma])
    

        
    
def read_pandas():
    print "pandas filename = ", args.pandas
    tablefile = pandas.read_pickle(args.pandas)
    
    KEY = "DIFF"
    KEY_ERR = "ERR"
    
    noise = "0\\.1"
    mqx_field = "4\\.0"
    
    if args.modern:
        A_NBPM = "a_nbpm"
        MC_NBPM = "mc_nbpm"
    else:
        A_NBPM = "nbpm"
        MC_NBPM = "mc_precise_nbpm"
    
    print "readin pandas file"
    print "nbpm pattern =","[0-9]+/3bpm/{}/{}/[0-9]+/{}/pc/{}/{}" \
                             .format(args.optics, args.kick, args.betabeatversion, args.noise, args.mqx_field)
    print tablefile.axes[0]
    print tablefile.keys()[0]
    
    threebpm_re = re.compile("[0-9]+/3bpm/{}/{}/[0-9]+/{}/pc/{}/{}"
                             .format(args.optics, args.kick, args.betabeatversion, args.noise, args.mqx_field))
    a_nbpm_re = re.compile("[0-9]+/{}/{}/{}/[0-9]+/{}/pc/{}/{}"
                           .format(A_NBPM, args.optics, args.kick, args.betabeatversion, args.noise, args.mqx_field))
    
    
    
    olda_nbpm_re = re.compile("[0-9]+/a_nbpm/{}/{}/[0-9]+/{}/pc/{}/{}"
                           .format(args.optics, args.kick, "2017\\.3\\.2", args.noise, args.mqx_field))
    #    a_nbpmtight_re = re.compile("[0-9]+/mc_nbpm/{}/{}/[0-9]+/2017\\.3\\.2/pc/{}/{}"
#                                .format(args.optics, args.kick, args.noise, args.mqx_field))
    mc_nbpm_re = re.compile("[0-9]+/{}/{}/{}/[0-9]+/{}/pc/{}/{}"
                            .format(MC_NBPM, args.optics, args.kick, args.betabeatversion, args.noise, args.mqx_field))
    
    
    
#    x_ =np.ravel(tablefile.select(a_nbpm_re.match).loc[:,:,"DIFF"].astype(np.dtype(np.float)))
#    y_ =np.ravel(tablefile.select(a_nbpm_re.match).loc[:,:,"ERR"].astype(np.dtype(np.float)))
#    h,axh = plt.subplots()
#    axh.hist2d(x=x_, y=y_, bins=[np.arange(-30,30,.05),np.arange(-0, 6, .01)])
#    h.show()
#    raw_input()
#    return

    

    
  
    threebpmdiff = tablefile.select(threebpm_re.match).loc[:,:,KEY]
    threebpmerr = tablefile.select(threebpm_re.match).loc[:,:,KEY_ERR]
    threebpmdiff_bool = tablefile.select(threebpm_re.match).loc[:,:,"REGION"]
  

    
    mc_nbpmdiff = tablefile.select(mc_nbpm_re.match).loc[:,:,KEY]
    mc_nbpmerr = tablefile.select(mc_nbpm_re.match).loc[:,:,KEY_ERR]
    mc_nbpmdiff_bool = tablefile.select(mc_nbpm_re.match).loc[:,:,"REGION"]
    
    a_nbpmdiff = tablefile.select(a_nbpm_re.match).loc[:,:,KEY]
    a_nbpmerr = tablefile.select(a_nbpm_re.match).loc[:,:,KEY_ERR]
    a_nbpmdiff_bool = tablefile.select(a_nbpm_re.match).loc[:,:,"REGION"]
    
    
    olda_nbpmdiff = tablefile.select(olda_nbpm_re.match).loc[:,:,KEY]
    olda_nbpmerr = tablefile.select(olda_nbpm_re.match).loc[:,:,KEY_ERR]
    olda_nbpmdiff_bool = tablefile.select(olda_nbpm_re.match).loc[:,:,"REGION"]
  
    ERR_FACTOR = 1

    threebpm_diff_arc = get_arc(threebpmdiff, threebpmdiff_bool, threebpmerr, CUT=args.cut)
    threebpm_diff_IR = get_ir(threebpmdiff, threebpmdiff_bool, threebpmerr, CUT=args.cut)
    threebpm_err_arc = get_arc(threebpmerr, threebpmdiff_bool, CUT=args.cut * ERR_FACTOR)
    threebpm_err_IR = get_ir(threebpmerr, threebpmdiff_bool, CUT=args.cut * ERR_FACTOR)
    
    a_nbpm_diff_arc = get_arc(a_nbpmdiff, a_nbpmdiff_bool, a_nbpmerr, CUT=args.cut)
    a_nbpm_diff_IR = get_ir(a_nbpmdiff, a_nbpmdiff_bool, a_nbpmerr, CUT=args.cut)
    a_nbpm_err_arc = get_arc(a_nbpmerr, a_nbpmdiff_bool, CUT=args.cut * ERR_FACTOR)
    a_nbpm_err_IR = get_ir(a_nbpmerr, a_nbpmdiff_bool, CUT=args.cut * ERR_FACTOR)
    
    olda_nbpm_diff_arc = get_arc(olda_nbpmdiff, olda_nbpmdiff_bool, a_nbpmerr, CUT=args.cut)
    olda_nbpm_diff_IR = get_ir(olda_nbpmdiff, olda_nbpmdiff_bool, a_nbpmerr, CUT=args.cut)
    olda_nbpm_err_arc = get_arc(olda_nbpmerr, olda_nbpmdiff_bool, CUT=args.cut * ERR_FACTOR)
    olda_nbpm_err_IR = get_ir(olda_nbpmerr, olda_nbpmdiff_bool, CUT=args.cut * ERR_FACTOR)

    
    
    mc_nbpm_diff_arc = get_arc(mc_nbpmdiff, mc_nbpmdiff_bool, mc_nbpmerr, CUT=args.cut)
    mc_nbpm_diff_IR = get_ir(mc_nbpmdiff, mc_nbpmdiff_bool, mc_nbpmerr, CUT=args.cut)
    mc_nbpm_err_arc = get_arc(mc_nbpmerr, mc_nbpmdiff_bool, CUT=args.cut * ERR_FACTOR)
    mc_nbpm_err_IR = get_ir(mc_nbpmerr, mc_nbpmdiff_bool, CUT=args.cut * ERR_FACTOR)
    
    
    
    

    print "done"
    a_nbpm_ncomb = {}
    mc_nbpm_ncomb = {}


    for i in range(3, 46):
        a_nbpm_ncomb[i] = {}
        mc_nbpm_ncomb[i] = {}

        
#    lastsim = 319
#    
#    for sim in xrange(lastsim):
#        #print "open", name
#        a_nbpm_diff_arc = np.append(a_nbpm_diff_arc, sim["{}_a_nbpmArc".format(sim)])
#        a_nbpm_diff_IR = np.append(a_nbpm_diff_IR, sim["{}_a_npmIR".format(sim)])
#        threebpm_diff_arc = np.append(threebpm_diff_arc, sim["{}_3bpmArc".format(sim)])
#        threebpm_diff_IR = np.append(threebpm_diff_IR, sim["{}_3bpmIR".format(sim)])
#        
#        ncombnode = "nbpm/Arc/ncomb"
#        if ncombnode in sim:
#            _n = sim[ncombnode]
#            for i in range(len(_n)):
#                a_nbpm_ncomb[_n[i]].append(sim["nbpm/Arc/diff"][i])
#            

        
    #tablefile.close()
    
#    if args.oneplot:
#        f_, ax_ = plt.subplots(nrows=1, ncols=1, squeeze=True, figsize=(args.width,args.width*.6))
#    
#        rc('font', **{'family': 'sans-serif', 'serif': ['Computer Modern']})
#        params = {'backend': 'pdf',
#                  'axes.labelsize': 16,
#                  'font.size': 16,
#                  'axes.titlesize': 16,
#                  'legend.fontsize': 12,
#                  'xtick.labelsize': 16,
#                  'ytick.labelsize': 16,
#                  'text.usetex': False,
#                  'axes.unicode_minus': True,
#                  'xtick.major.pad': 12,
#                  'ytick.major.pad': 12,
#                  'xtick.minor.pad': 12,
#                  'ytick.minor.pad': 12
#                  }
#        matplotlib.rcParams.update(params)
#    else:
        
    rc('font', **{'family': 'serif', 'serif': ['Times']})
    params = {'backend': 'pdf',
              'axes.labelsize': 18,
              'font.size': 16,
              'axes.titlesize': 10,
              'legend.fontsize': 16,
              'xtick.labelsize': 16,
              'ytick.labelsize': 16,
              'text.usetex': True,
              'axes.unicode_minus': True,
              'xtick.major.pad': 10,
              'ytick.major.pad': 4,
              'xtick.minor.pad': 6,
              'ytick.minor.pad': 2
              }
    matplotlib.rcParams.update(params)
    

    
    title= "compare_NBPM_to_3BPM_{0:s}.pdf".format(args.title)
    label1="3-BPM"
    label2="N-BPM"
    label3="A. N-BPM"
    color1='#FF2010'
    color2='#20AF10'
    color3='#1020FF'
#    edgecolor1='#9F2010'
#    edgecolor2='#209F10'
#    edgecolor3='#10209F'
    edgecolor1=color1
    edgecolor2=color2
    edgecolor3=color3
    linetype="-"
    lwidth=1.5
    histmax=args.histmax
    optics=args.optics
    kick=float(args.kick)
    histtype='step'
    alfa=1
    histbarwidth=.2
    histbarwidthMC=.6
    
    
        
        

    # ==================================================================================
    # ========== PLOT ==================================================================
    # ==================================================================================
    
   
    meana_nbpm_diff_IR = np.mean(a_nbpm_diff_IR)
    meana_nbpm_diff_arc = np.mean(a_nbpm_diff_arc)
    
    mean_3bpm_diff_arc = np.mean(threebpm_diff_arc)
    mean_3bpm_diff_IR = np.mean(threebpm_diff_IR)
    meanmc_nbpm_diff_arc = np.mean(mc_nbpm_diff_arc)
    meanmc_nbpm_diff_IR = np.mean(mc_nbpm_diff_IR)

    
    
    stda_nbpm_err_arc = np.mean(a_nbpm_err_arc)
    stda_nbpm_err_IR = np.mean(a_nbpm_err_IR)
    
    std_3bpm_err_arc = np.mean(threebpm_err_arc)
    std_3bpm_err_IR = np.mean(threebpm_err_IR)
    stdmc_nbpm_err_arc = np.mean(mc_nbpm_err_arc)
    stdmc_nbpm_err_IR = np.mean(mc_nbpm_err_IR)
    
    mean_anbpm_err = np.mean(np.append(a_nbpm_err_arc, a_nbpm_err_IR))
    mean_mcnbpm_err = np.mean(np.append(mc_nbpm_err_arc, mc_nbpm_err_IR))
    mean_3bpm_err = np.mean(np.append(threebpm_err_arc, threebpm_err_IR))
    
    old_anbpm = False
    if len(olda_nbpm_diff_arc) > 0:
        meanolda_nbpm_diff_IR = np.mean(olda_nbpm_diff_IR)
        meanolda_nbpm_diff_arc = np.mean(olda_nbpm_diff_arc)
    
        stdolda_nbpm_err_arc = np.mean(olda_nbpm_err_arc)
        stdolda_nbpm_err_IR = np.mean(olda_nbpm_err_IR)
        mean_oldanbpm_err = np.mean(np.append(olda_nbpm_err_arc, olda_nbpm_err_IR))
        old_anbpm=True


    
#    sorted_a_npm_diff_IR = np.sort(abs(a_nbpm_diff_IR))
#    sorted_mc_npm_diff_IR = np.sort(abs(mc_nbpm_err_IR))
#    sorted_3bpm_diff_IR = np.sort(abs(threebpm_err_IR))
#    
#    sorted_a_npm_diff_arc = np.sort(abs(a_nbpm_diff_arc))
#    sorted_mc_npm_diff_arc = np.sort(abs(mc_nbpm_err_arc))
#    sorted_3bpm_diff_arc = np.sort(abs(threebpm_err_arc))
#    
    
#    stda_nbpm_diff_arc = rms(a_nbpm_diff_arc)
#    stda_nbpm_diff_IR = rms(a_nbpm_diff_IR)
#    stda_nbpmtight_diff_arc = rms(a_nbpmtight_diff_arc)
#    stda_nbpmtight_diff_IR = rms(a_nbpmtight_diff_IR)
#    stda_3bpm_diff_arc = rms(threebpm_diff_arc)
#    stda_3bpm_diff_IR = rms(threebpm_diff_IR)
#    stdmc_nbpm_diff_arc = rms(mc_nbpm_diff_arc)
#    stdmc_nbpm_diff_IR = rms(mc_nbpm_diff_IR)
#    
   
    print "A. N-BPM mean errorbar: {}".format(mean_anbpm_err)
    print "N-BPM mean errorbar: {}".format(mean_mcnbpm_err)
    print "3-BPM mean errorbar: {}".format(mean_3bpm_err)
    #print deviation3bpm
    

    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
   
    f, ax= plt.subplots(nrows=2, ncols=1, squeeze=True, figsize=(args.width,args.width*.6))  
    ax[1].set_xlabel(r"deviation of measured $\beta$ [\%]")
    f.text(-.0, .5, "count [normalized]", va="center", rotation="vertical", fontsize=18)

    #ax3.set_ylabel("count")
    
    width = histmax / 30.0
    
#    ax[0].set_yscale("log")
#    ax[1].set_yscale("log")
#    ax[0].set_ylim(1e-4, 1)
#    ax[1].set_ylim(1e-4, 1)
#    plot_hist_err(threebpm_err_arc, mc_nbpm_err_arc, a_nbpm_err_arc,
#                  threebpm_err_IR, mc_nbpm_err_IR, a_nbpm_err_IR, histmax, width)
    
    mybins = np.arange(-histmax, histmax, width)
   
    _normed = True
   
    n_3bpm_arc, bins_3bpm_arc, _ = ax[0].hist(threebpm_diff_arc, bins=mybins,
             normed=_normed, label=label1 , 
             color=color1, edgecolor=edgecolor1, histtype=histtype,
             linestyle=linetype, alpha=alfa, linewidth=lwidth)
    
    #ax[0].plot(mybins, matplotlib.mlab.normpdf(mybins, 0, stda_3bpm_diff_arc), color="#A0A000", linewidth=2.0)
    
    if args.withandy:
        n_mc_nbpm_arc, bins_mc_nbpm_arc, _ = ax[0].hist(mc_nbpm_diff_arc,bins=mybins + (width*(0.5 - 0.5 * histbarwidthMC)), #width=(width*histbarwidthMC),
                 normed=_normed, label=label2 , 
                color=color2, edgecolor=edgecolor2, histtype=histtype,
                linestyle=linetype, alpha=alfa, linewidth=lwidth)
#        ax[0].hist(a_nbpmtight_diff_arc,bins=mybins + (width*(0.5 - 0.5 * histbarwidthMC)), #width=(width*histbarwidthMC),
#                 normed=True, label="N-BPM () arc",
#                color=color2, edgecolor="#105050", histtype=histtype,
#                linestyle=linetype, alpha=alfa, linewidth=lwidth)
    n_a_nbpm_arc, bins_a_nbpm_arc, _ = ax[0].hist(a_nbpm_diff_arc, bins=mybins + (width*(0.5 - 0.5 * histbarwidth)),# width=(width*histbarwidth),
             normed=_normed, label=label3 , 
            color=color3, edgecolor=edgecolor3, histtype=histtype,
            linestyle=linetype, alpha=alfa, linewidth=lwidth)

    
    if old_anbpm:
        n_olda_nbpm_arc, bins_olda_nbpm_arc, _ = ax[0].hist(olda_nbpm_diff_arc, bins=mybins + (width*(0.5 - 0.5 * histbarwidth)),# width=(width*histbarwidth),
                 normed=_normed, label=label3 + "old" , 
                color="gold", edgecolor="gold", histtype=histtype,
                linestyle=linetype, alpha=alfa, linewidth=lwidth)
    
    ax[0].get_xaxis().set_visible(False)
    
    

    n_3bpm_ir, bins_3bpm_ir, _ = ax[1].hist(threebpm_diff_IR, bins=mybins, 
            normed=_normed, label=label1 , 
            color=color1, edgecolor=edgecolor1, histtype=histtype,
            linestyle=linetype, alpha=alfa, linewidth=lwidth)
    if args.withandy:
        n_mc_nbpm_ir, bins_mc_nbpm_ir, _ = ax[1].hist(mc_nbpm_diff_IR,bins=mybins + (width*(0.5 - 0.5 * histbarwidthMC)), #width=(width*histbarwidthMC),
                 normed=_normed, label=label2, 
                color=color2, edgecolor=edgecolor2, histtype=histtype,
                linestyle=linetype, alpha=alfa, linewidth=lwidth)
#        ax[1].hist(a_nbpmtight_diff_IR, bins=mybins + (width*(0.5 - 0.5 * histbarwidth)), #width=(width*histbarwidth),
#                 normed=True, label="N-BPM () IR", 
#                color=color3, edgecolor="#105050", histtype=histtype,
#                linestyle=linetype, alpha=alfa, linewidth=lwidth)

    n_a_nbpm_ir, bins_a_nbpm_ir, _ = ax[1].hist(a_nbpm_diff_IR, bins=mybins + (width*(0.5 - 0.5 * histbarwidth)), #width=(width*histbarwidth),
             normed=_normed, label=label3 , 
            color=color3, edgecolor=edgecolor3, histtype=histtype,
            linestyle=linetype, alpha=alfa, linewidth=lwidth)
    
    if old_anbpm:
        n_olda_nbpm_ir, bins_olda_nbpm_ir, _ = ax[1].hist(olda_nbpm_diff_IR, bins=mybins + (width*(0.5 - 0.5 * histbarwidth)), #width=(width*histbarwidth),
                 normed=_normed, label=label3 + "old", 
                color="gold", edgecolor="gold", histtype=histtype,
                linestyle=linetype, alpha=alfa, linewidth=lwidth)

    ax[0].set_yticks(np.arange(.2, .8, .2))
    ax[1].set_yticks(np.arange(.2, .8, .2))
    ax[1].set_xticks(np.arange(-histmax,histmax,histmax/4))
    ax[0].text(0.05, 0.9, 'Arc',
        verticalalignment='top', horizontalalignment='left',
        transform=ax[0].transAxes,
        color='black', fontsize=20)
    ax[1].text(0.05, 0.9, 'IR',
        verticalalignment='top', horizontalalignment='left',
        transform=ax[1].transAxes,
        color='black', fontsize=20)
    
    ax[0].set_ylim(0,.9)    
    ax[1].set_ylim(0,.9)  
    if args.logscale:
        ax[0].set_ylim(0.0001,.9)    
        ax[1].set_ylim(0.0001,.9)  
        ax[0].set_yscale("log", nonposy='clip')
        ax[1].set_yscale("log", nonposy='clip')
  
    ax[0].set_xlim(-histmax+.1, histmax-.1)
    ax[1].set_xlim(-histmax+.1, histmax-.1)
   
    fit_x = np.arange(-histmax, histmax, width)

    [a_3bpm_arc, x0_3bpm_arc, sigma_3bpm_arc], pcov = fit(bins_3bpm_arc, n_3bpm_arc)
    [a_mc_nbpm_arc, x0_mc_nbpm_arc, sigma_mc_nbpm_arc],pcov = fit(bins_mc_nbpm_arc, n_mc_nbpm_arc)
    [a_a_nbpm_arc, x0_a_nbpm_arc, sigma_a_nbpm_arc],pcov = fit(bins_a_nbpm_arc, n_a_nbpm_arc)
    
    if old_anbpm:
        [a_olda_nbpm_arc, x0_olda_nbpm_arc, sigma_olda_nbpm_arc],pcov = fit(bins_olda_nbpm_arc, n_olda_nbpm_arc)
        [a_olda_nbpm_ir, x0_olda_nbpm_ir, sigma_olda_nbpm_ir],pcov = fit(bins_olda_nbpm_ir, n_olda_nbpm_ir)

    [a_3bpm_ir, x0_3bpm_ir, sigma_3bpm_ir],pcov = fit(bins_3bpm_ir, n_3bpm_ir)
    [a_mc_nbpm_ir, x0_mc_nbpm_ir, sigma_mc_nbpm_ir],pcov = fit(bins_mc_nbpm_ir, n_mc_nbpm_ir)
    [a_a_nbpm_ir, x0_a_nbpm_ir, sigma_a_nbpm_ir],pcov = fit(bins_a_nbpm_ir, n_a_nbpm_ir)
    
    if args.gaussfit:
        ax[0].plot(fit_x, gaus(fit_x, a_3bpm_arc, x0_3bpm_arc, sigma_3bpm_arc), label="3 BPM gaussian fit", linewidth=1, color=COLOR_3BPM_QUANT)
        ax[0].plot(fit_x, gaus(fit_x, a_mc_nbpm_arc, x0_mc_nbpm_arc, sigma_mc_nbpm_arc), label="N-BPM gaussian fit", linewidth=1, color=COLOR_MC_NBPM_QUANT)
        ax[0].plot(fit_x, gaus(fit_x, a_a_nbpm_arc, x0_a_nbpm_arc, sigma_a_nbpm_arc), label="A. N-BPM gaussian fit", linewidth=1, color=COLOR_A_NBPM_QUANT)
        ax[1].plot(fit_x, gaus(fit_x, a_3bpm_ir, x0_3bpm_ir, sigma_3bpm_ir), label="3 BPM gaussian fit", linewidth=1, color=COLOR_3BPM_QUANT)
        ax[1].plot(fit_x, gaus(fit_x, a_mc_nbpm_ir, x0_mc_nbpm_ir, sigma_mc_nbpm_ir), label="N-BPM gaussian fit", linewidth=1, color=COLOR_MC_NBPM_QUANT)
        ax[1].plot(fit_x, gaus(fit_x, a_a_nbpm_ir, x0_a_nbpm_ir, sigma_a_nbpm_ir), label="A. N-BPM gaussian fit", linewidth=1, color=COLOR_A_NBPM_QUANT)


    print "================ plotting ===================\n"
    print "a-nbpm:    {0:6d} BPMs,\n    arc: std = {1:6.3f} ({3:6.2f}%), mean_err = {5:6.3f}\n     IR: std = {2:6.3f} ({4:6.2f}%), mean_err = {6:6.3f}\n".format(
                                                                                            len(a_nbpm_diff_arc) + len(a_nbpm_diff_IR),
                                                                                            sigma_a_nbpm_arc, sigma_a_nbpm_ir,
                                                                                            (sigma_a_nbpm_arc / sigma_3bpm_arc - 1) * 100,
                                                                                            (sigma_a_nbpm_ir / sigma_3bpm_ir - 1) * 100,
                                                                                            stda_nbpm_err_arc, stda_nbpm_err_IR)
    if old_anbpm:
        print "old a-nbpm:    {0:6d} BPMs,\n    arc: std = {1:6.3f} ({3:6.2f}%), mean_err = {5:6.3f}\n     IR: std = {2:6.3f} ({4:6.2f}%), mean_err = {6:6.3f}\n".format(
                                                                                            len(olda_nbpm_diff_arc) + len(olda_nbpm_diff_IR),
                                                                                            sigma_olda_nbpm_arc, sigma_olda_nbpm_ir,
                                                                                            (sigma_olda_nbpm_arc / sigma_3bpm_arc - 1) * 100,
                                                                                            (sigma_olda_nbpm_ir / sigma_3bpm_ir - 1) * 100,
                                                                                            stdolda_nbpm_err_arc, stdolda_nbpm_err_IR)
    
#    print_quantiles(sorted_a_npm_diff_IR, sorted_a_npm_diff_arc)

    if args.withandy:      
#        print "mc-nbpm (10^4):    {0:6d} BPMs,\n    arc: std = {1:6.3f} ({3:6.2f}%), mean_err = {5:6.3f}\n     IR: std = {2:6.3f} ({4:6.2f}%), mean_err = {6:6.3f}\n".format(
#                                                                                            len(mc_nbpm_diff_arc) + len(mc_nbpm_diff_IR),
#                                                                                            stdmc_nbpm_diff_arc, stdmc_nbpm_diff_IR,
#                                                                                            (stdmc_nbpm_diff_arc / sigma_3bpm_arc - 1) * 100,
#                                                                                            (stdmc_nbpm_diff_IR / sigma_3bpm_ir - 1) * 100,
#                                                                                            stdmc_nbpm_err_arc, stdmc_nbpm_err_IR
#                                                                                            )
##        print_quantiles(sorted_mc_npm_diff_IR, sorted_mc_npm_diff_arc)

   
        print "mc-nbpm:    {0:6d} BPMs,\n    arc: std = {1:6.3f} ({3:6.2f}%), mean_err = {5:6.3f}\n     IR: std = {2:6.3f} ({4:6.2f}%), mean_err = {6:6.3f}\n".format(
                                                                                            len(mc_nbpm_diff_arc) + len(mc_nbpm_diff_IR),
                                                                                            sigma_mc_nbpm_arc, sigma_mc_nbpm_ir,
                                                                                            (sigma_mc_nbpm_arc / sigma_3bpm_arc - 1) * 100,
                                                                                            (sigma_mc_nbpm_ir / sigma_3bpm_ir - 1) * 100,
                                                                                            stdmc_nbpm_err_arc, stdmc_nbpm_err_IR
                                                                                            )
    print "3bpm:    {0:6d} BPMs\n    arc: std = {1:6.3f}, mean_err = {3:6.3f}\n     IR: std = {2:6.3f}, mean_err = {4:6.3f}\n".format(
                                                                                            len(threebpm_diff_arc) + len(threebpm_diff_IR),
                                                                                            sigma_3bpm_arc, sigma_3bpm_ir,
                                                                                            std_3bpm_err_arc, std_3bpm_err_IR)
#    print_quantiles(sorted_3bpm_diff_IR, sorted_3bpm_diff_arc)

    
    
    for a_ in range(2):
        ax[a_].legend()

  
    f.tight_layout(h_pad=.0)
    
        
    
    f.savefig("comparison_statistics_{0:s}.pdf".format(args.title))
    if args.copy:
        f.savefig("/home/awegsche/Dropbox/CERN/NBPM/comparison_2016_{:s}_histo.pdf".format(args.title))

    
    rc('font', **{'family': 'serif', 'serif': ['Times']})
    params = {'backend': 'pdf',
              'axes.labelsize': 16,
              'font.size': 16,
              'axes.titlesize': 16,
              'legend.fontsize': 14,
              'xtick.labelsize': 20,
              'ytick.labelsize': 16,
              'text.usetex': True,
              'axes.unicode_minus': True,
              'xtick.major.pad': 10,
              'ytick.major.pad': 4,
              'xtick.minor.pad': 6,
              'ytick.minor.pad': 2
              }
    matplotlib.rcParams.update(params)
   
    g,ax = plt.subplots(nrows=1, figsize=(args.width,args.width*.35))
    
    if args.split_plot:
        g2,[ax2_top, ax2] = plt.subplots(nrows=2, figsize=(args.width,args.width*.5), sharex=True)
    else:
        g2,ax2 = plt.subplots(nrows=1, figsize=(args.width,args.width*.5), sharex=True)
    
    #["stda_nbpm_diff_arc",
#            "stda_nbpm_diff_IR",
#            "stda_3bpm_diff_arc",
#            "stda_3bpm_diff_IR",
#            "stdmc_nbpm_diff_arc",
#            "stdmc_nbpm_diff_IR"]
    barwidth=.2
    margin = .1
    lwidth = 2
    edgecolor1='#802010'
    edgecolor2='#205010'
    edgecolor3='#102050'
    
    
    ARC_Bar1 = sigma_3bpm_arc# sorted_3bpm_diff_arc[int(0.6827*len(sorted_3bpm_diff_arc))]
    ARC_Bar2 = sigma_mc_nbpm_arc # sorted_mc_npm_diff_arc[int(0.6827*len(sorted_mc_npm_diff_arc))]
    ARC_Bar3 = sigma_a_nbpm_arc # sorted_a_npm_diff_arc[int(0.6827*len(sorted_a_npm_diff_arc))]
    
    IR_Bar1 = sigma_3bpm_ir # sorted_3bpm_diff_IR[int(0.6827*len(sorted_3bpm_diff_IR))]
    IR_Bar2 = sigma_mc_nbpm_arc #sorted_mc_npm_diff_IR[int(0.6827*len(sorted_mc_npm_diff_IR))]
    IR_Bar3 = sigma_a_nbpm_ir  # sorted_a_npm_diff_IR[int(0.6827*len(sorted_a_npm_diff_IR))]
    
    if args.withandy:
        sixbar_plot(ax2, 
                    std_3bpm_err_arc, stdmc_nbpm_err_arc, stda_nbpm_err_arc,
                    ARC_Bar1, ARC_Bar2, ARC_Bar3,
                    std_3bpm_err_IR, stdmc_nbpm_err_IR, stda_nbpm_err_IR,
                    IR_Bar1, IR_Bar2, IR_Bar3,
                    barwidth, margin, 1.5, True)
        if args.split_plot:      
            sixbar_plot(ax2_top, 
                        std_3bpm_err_arc, stdmc_nbpm_err_arc, stda_nbpm_err_arc,
                        ARC_Bar1, ARC_Bar2, ARC_Bar3,
                        std_3bpm_err_IR, stdmc_nbpm_err_IR, stda_nbpm_err_IR,
                        IR_Bar1, IR_Bar2, IR_Bar3,
                        barwidth, margin, 1.5, True)
            
            
            if args.split_at is None:
                max_bottom = max(ARC_Bar1, ARC_Bar2, ARC_Bar3, IR_Bar1, IR_Bar2, IR_Bar3, stdmc_nbpm_err_IR, stda_nbpm_err_IR, stdmc_nbpm_err_IR, stda_nbpm_err_IR) + 0.1
                min_top = min(std_3bpm_err_arc, std_3bpm_err_IR) - 0.3
                max_top = max(std_3bpm_err_arc, std_3bpm_err_IR) + 0.3
            else:
                max_bottom = args.split_at[0]
                min_top = args.split_at[1]
                max_top = args.split_at[2]
            
            ax2.set_yticks(np.arange(0, max_bottom + 0.5, args.steps[0]))
            ax2_top.set_yticks(np.arange(int((min_top-1) / 0.5) * 0.5, max_top + 1, args.steps[1]))
    
            ax2.set_ylim(0, max_bottom)
            ax2_top.set_ylim(min_top, max_top)
            g2.subplots_adjust(hspace=10)
            
            ax2_top.spines["bottom"].set_visible(False)
            ax2.spines["top"].set_visible(False)
            
            ax2_top.xaxis.tick_top()
            ax2_top.tick_params(labeltop='off')  # don't put tick labels at the top
            ax2.xaxis.tick_bottom()
            
            d = .015  # how big to make the diagonal lines in axes coordinates
            # arguments to pass to plot, just so we don't keep repeating them
            kwargs = dict(transform=ax2_top.transAxes, color='k', clip_on=False)
            ax2_top.plot((-d, +d), (-d, +d), **kwargs)        # top-left diagonal
            ax2_top.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal
            
            kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
            ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
            ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal
            
            handles, labels = ax2.get_legend_handles_labels()
            
            g2.legend(handles[:3], labels[:3], bbox_to_anchor=(.215, .89), loc=2, borderaxespad=0.)
            g2.legend(handles[3:], labels[3:], bbox_to_anchor=(.6, .89), loc=2, borderaxespad=0.)
        else:
            ax2.legend(bbox_to_anchor=(.18, .95), loc=2, borderaxespad=0.)
    
        
    else:
        twobar_plot(ax2, ARC_Bar1, ARC_Bar3, 
             IR_Bar1, IR_Bar3, 
             barwidth, margin, lwidth, True,
             color1, edgecolor1, color3, edgecolor3 )


    if args.withandy:
        accuracy_bar_plot(ax, mean_3bpm_diff_arc, meanmc_nbpm_diff_arc, meana_nbpm_diff_arc,
             mean_3bpm_diff_IR, meanmc_nbpm_diff_IR, meana_nbpm_diff_IR,
             barwidth, margin, lwidth, True,
             color1, edgecolor1, color2, edgecolor2, color3, edgecolor3)
    else:
        twobar_plot(ax, ARC_Bar1, ARC_Bar3, 
             IR_Bar1, IR_Bar3, 
             barwidth, margin, lwidth, True,
             color1, edgecolor1, color3, edgecolor3 )
        
    
    
    g.tight_layout(h_pad=.0)
    
    g.savefig("comparison_statistics_{0:s}_bars.pdf".format(args.title))
    if args.copy:
            g.savefig("/home/awegsche/Dropbox/CERN/NBPM/comparison_2016_{:s}_bar.pdf".format(args.title))

    g2.tight_layout(h_pad=.0)
    
    g2.savefig("comparison_statistics_{0:s}_quantilebars.pdf".format(args.title))
    if args.copy:
            g2.savefig("/home/awegsche/Dropbox/CERN/NBPM/comparison_2016_{:s}_quantilebar.pdf".format(args.title))

    


parser = argparse.ArgumentParser(description='Plotting statistics of simulated GetLLM')
parser.add_argument('--width', type=float, dest="width", default=10,
                    help="The desired final width of the plot in cm. This is needed in order for the fonts to be displayed big enough")
parser.add_argument('--in', type=str, dest="statisticsfilename", default=None,
                    help="The name of the file with the statistics data.")
parser.add_argument('--histmax', type=float, dest="histmax", default=6.0,
                    help="The nx range of the histogram.")
parser.add_argument('--optics', type=str, dest="optics", default="V6503coll",
                    help="The nx range of the histogram.")
parser.add_argument('--kick', type=str, dest="kick", default="0.0001",
                    help="The kick in units of m. Default = 0.0001")
parser.add_argument('--mqx', type=str, dest="mqx_field", default="4.0",
                    help="The MQX field strength in units of 1e-4. Default = 4.0")
parser.add_argument('--noise', type=str, dest="noise", default="0.1",
                    help="The bpm noise in mm. Default=0.1")
parser.add_argument('--title', type=str, dest="title", default="",
                    help="Additional label for filename.")
parser.add_argument('--oneplot', action="store_true", dest="oneplot",
                    help="If set, all the histogramms will be drawn in one plot.")
parser.add_argument('--withAndy', action="store_true", dest="withandy",
                    help="If set, Andy's N-BPM method will also be displayed.")
parser.add_argument('--logscale', action="store_true", dest="logscale",
                    help="If set, the y axis will be scaled logarithmically.")
parser.add_argument('--ascii', action="store_true", dest="ascii",
                    help="Is the input file the old statistics file (in ascii)? If not, HD5 is assumed.")
parser.add_argument('-v', dest="v", type=int, default=1,
                    help="The version of the HD5 plot, 1=similar to before, 2=one plot for arc, one for IR.")
parser.add_argument('--pandas', dest="pandas", type=str, default=None,
                    help="Path to the pandas hd5 file. If None is given, only histogramms will be created")
parser.add_argument('-c', dest="copy", action="store_true",
                    help="if specified, copies the resulting plots to the N-BPM draft directory.")
parser.add_argument('--pfit', dest="gaussfit", action="store_true",
                    help="Should the Gaussian fit be shown in the plot?")
parser.add_argument('--bbv', dest="betabeatversion", default="2017\\.3\\.2",
                    help="Filter for the BetaBeat.src version to use. Default = 2017\\.3\\.2")
parser.add_argument('--obsolete', dest="modern", action="store_false",
                    help="should we use the old version of plot_statistics?")
parser.add_argument('--split_plot', dest="split_plot", action="store_true",
                    help="should we break the vertical axis?")
parser.add_argument('--at', dest="split_at", nargs=3, type=float, metavar=("MAX_lower", "MIN_upper", "MAX_upper"),
                    default=None,
                    help="where should we break at?")
parser.add_argument('--steps', dest="steps", nargs=2, type=float, metavar=("bottom_step", "top_step"),
                    default=(.5, 1.5),
                    help="where should we break at?")


parser.add_argument('--cut', dest="cut", type=float, default=100.0,
                    help="the cut of diff for the std.")


args = parser.parse_args()
oneplot = True
if args.statisticsfilename is not None:
    if args.ascii:
        read_ascii()
    else:
        if args.v == 1:
            read_hd5_v1()
        else:
            read_hd5_v2()

if args.pandas is not None:
    read_pandas()