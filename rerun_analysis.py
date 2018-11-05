""" Reruns a specified analysis
"""
import os
import sys
import re
import argparse
import logging
import pandas
import numpy as np
import subprocess
from subprocess import Popen

# GETLLM paths
import betabeatsrc
from GetLLM import GetLLM
from GetLLM import GetLLMError
from utils import logging_tools
from utils import tfs_pandas
from model import manager
import pyterminal
import reinterpret_logger

LOGGER = logging_tools.get_logger(__name__, level_console=logging.DEBUG)
#LOGGER.addHandler(logging_tools.stream_handler(max_level=logging.DEBUG))

SEPARATOR = "\33[38;2;128;128;128m | "
DBG_COLR = "\33[38;2;0;200;200m\33[1m"
ERR_COLR = "\33[38;2;200;0;0m\33[1m"
WRN_COLR = "\33[38;2;220;110;0m\33[1m"
NFO_COLR = "\33[38;2;200;0;200m\33[1m"
REP_COLR = "\33[38;2;128;128;128m\33[1m"
DBG_FLAG = DBG_COLR + "DBG\33[22m" + SEPARATOR + "\33[0m\33[1m"
ERR_FLAG = ERR_COLR + "ERR\33[22m" + SEPARATOR + "\33[38;2;255;0;0m"
WRN_FLAG = WRN_COLR + "WRN\33[22m" + SEPARATOR + "\33[38;2;200;100;0m"
NFO_FLAG = NFO_COLR + "NFO\33[22m" + SEPARATOR + "\33[0m\33[1m"
REP_FLAG = REP_COLR + "   \33[22m" + SEPARATOR + "\33[0m\33[1m"
PRINT_LINELEN = 120


# ----- GLOBALS for analysis
folderpairs = None


def main():
    """Main function
    """
    theseargs = parse_arguments()

    LOGGER.info("============================================================")
    LOGGER.info("===== Reanalyzing {}".format(theseargs.source))
    LOGGER.info("============================================================")
    LOGGER.info("new output folder = '{}'".format(theseargs.output))

    if os.path.isfile(os.path.join(theseargs.source, "thecommand.py")):
        LOGGER.info("thecommand.py found. Run it with new output path?")
        LOGGER.info("info: new outputpath = '{}'".format(theseargs.output))
        if raw_input("run thecommand? (y/n)") == "y":
            _run_thecommand(os.path.join(theseargs.source, "thecommand.py"))
    else:
        _rerun(theseargs)

    if theseargs.analyse:
        if os.path.isdir(theseargs.output):
            LOGGER.info(" ".join(["."] *60))
            LOGGER.info("Checking Integrity")
            check_folders(theseargs)
            pterm = init_pyterm()

            cont = True

            while cont:
                command = raw_input(
                    "{}{:>7s} {}| \33[0m"
                    .format(logging_tools.COLOR_LEVEL, "INPUT", logging_tools.COLOR_DIVIDER)
                )
                success = pterm.run_command(command)
                if not success:
                    if command in ["quit", "q"]:
                        LOGGER.info(" Quitting")
                        cont = False

        else:
            LOGGER.warning("no outputfolder")


def check_folders(args):
    LOGGER.info("Checking outputfolders")
    global folderpairs
    folderpairs = {}
    sourcefolder = sorted(os.listdir(args.source))
    outputfolder = os.listdir(args.output)
    nfiles = 0
    npresent = 0
    nnotimportant = 0
    matching = 0.0

    match = re.compile("get.*\.out$")
    for filep in sourcefolder:
        if match.match(filep):
            nfiles += 1
            if filep in outputfolder:
                matching_file = check_tfs(
                    os.path.join(args.source, filep),
                    os.path.join(args.output, filep))
                matching += matching_file
                LOGGER.info("\33[38;2;100;200;100m{:6.2f}% -- {}\33[0m"
                            .format(matching_file * 100.0, filep))
                folderpairs[filep] = [os.path.join(args.source, filep), os.path.join(args.output, filep)]
                if matching_file > 0:
                    npresent += 1
            elif "_free2" in filep:
                nnotimportant += 1
                LOGGER.info("\33[38;2;200;200;100m{}\33[0m".format(filep))
            else:
                LOGGER.info("\33[38;2;200;100;100m{}\33[0m".format(filep))
    LOGGER.info("")

    LOGGER.info("Number of matching files:  {:3d} ({:5.2f}%)"
                .format(npresent, float(npresent)/nfiles * 100.))
    LOGGER.info("Number of discarded files: {:3d} ({:5.2f}%)"
                .format(nnotimportant, float(nnotimportant)/nfiles * 100.))
    critical_fails = nfiles - npresent - nnotimportant
    critical_diff = float(nfiles) - matching - nnotimportant
    if critical_fails > 0:
        color = "\33[38;2;210;20;20m"
    else:
        color = "\33[38;2;20;200;20m"
    LOGGER.info("{}Number of critical fails:  {:3d} ({:5.2f}%)"
                .format(color, critical_fails, float(critical_fails)/nfiles * 100.))
    LOGGER.info("{}Critical diff:                  {:5.2f}%"
                .format(color, critical_diff / nfiles * 100.))

    LOGGER.info(" ".join(["."] *60))


def check_tfs(path1, path2, show=False):
    try:
        tfs1 = tfs_pandas.read_tfs(path1)
        tfs2 = tfs_pandas.read_tfs(path2)
    except ValueError:
        LOGGER.debug("Value error occured in loading, will return 0% match")
        return .0
    matching = .0

    if len(tfs1.index) != len(tfs2.index):
        if show:
            LOGGER.info("!!!! indices not equal")
            for key in tfs1.index:
                if key not in tfs2.index:
                    LOGGER.warning("'{}' not in new output".format(tfs1.loc[key, "NAME"]))
        return 0.0

    for column in tfs1.columns:
        if column not in tfs2.columns:
            if show:
                LOGGER.info("!!!! column {} in file1 but not in file2".format(column))
        else:
            if tfs1.dtypes[column] is np.dtype('float64'):
                equalindex = abs(tfs1[column]/tfs2[column] - 1.0) > 1.0e-2
            else:
                equalindex = tfs1[column] != tfs2[column]
            diff = pandas.concat(
                [tfs1.loc[equalindex, column], tfs2.loc[equalindex, column]], axis=1)
            if diff.empty:
                if show:
                    LOGGER.info("column \33[38;2;128;128;128m{:16s}\33[0m\33[1m \33[38;2;200;255;200mmatch\33[0m".format(column))
                matching += 1.0
            else:
                if show:
                    LOGGER.info(
                        "column \33[38;2;128;128;128m{:16s}\33[0m\33[1m\33[38;2;255;200;200m"
                        .format(column) +
                        " diff\33[0m\n{}"
                        .format(diff))
                matching += 1.0 - float(len(diff)) / float(len(tfs1.index))

    if show:
        LOGGER.info("{} columns  out of {} matched".format(matching, len(tfs1.columns)))
    return matching / len(tfs1.columns)



def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--source", dest="source", type=str,
                        help="the output folder of the original analysis")
    parser.add_argument("-o", "--output", dest="output", type=str, help="the NEW output folder")
    parser.add_argument("--loglevel", dest="loglevel", type=str, default="DEBUG", metavar="LEVEL",
                        help="the log level (DEBUG, INFO, WARN). Default=DEBUG")
    parser.add_argument("-m", "--model", dest="model", type=str,
                        help="change the model folder", default=None)
    parser.add_argument("--serial", dest="serial", action="store_true",
                        help="should GetLLM run serially?")
    parser.add_argument("--no_union", dest="no_union", action="store_true",
                        help="force UNION=FALSE")
    parser.add_argument("--analyse", dest="analyse", action="store_true",
                        help="analyse the differences between the old and new code afterwards")
    parser.add_argument("--orig", dest="original", action="store_true",
                        help="rerun the original code and save to ouput")
    return parser.parse_args()

def diff_cmd(command):
    """prints out the difference between the given file in the source and output directory.
    """
    global folderpairs
    key = command
    if key in folderpairs.keys():
        [src, dst] = folderpairs[key]
        check_tfs(src, dst, True)
    else:
        LOGGER.info("'{}' not in the source output folder".format(key))


def init_pyterm():
    term = pyterminal.ATerm()
    term.add_command(["diff"], diff_cmd)

    return term

def _shorten_filename(fname):
    paths = fname.split(os.sep)

    spaths = [paths[0]]

    for p in paths[1:-1]:
        spaths.append(p[0])
    spaths.append(paths[-1])
    return os.sep.join(spaths)

def _run_thecommand(thecommand):
    p = Popen(["python", thecommand])

    p.wait()



def _rerun(theseargs):
    if os.path.isfile(os.path.join(theseargs.source, "getbetax_free.out")):
        getbetax_path = os.path.join(theseargs.source, "getbetax_free.out")
    elif os.path.isfile(os.path.join(theseargs.source, "getbetax.out")):
        getbetax_path = os.path.join(theseargs.source, "getbetax.out")
    else:
        LOGGER.error("Source could not be found")
        sys.exit(1)

    pyscript = "import os\nimport sys\n"
    pyscript += "BETABEATPATH = '{}'\n\nsys.path.append(BETABEATPATH)\n".format(betabeatsrc.BETABEATPATH)
    pyscript += "NEW_OUTPUT = '{}'\n\n".format(theseargs.output)
    pyscript += (
        "from GetLLM import GetLLM\n"
        "from GetLLM import GetLLMError\n\n"
        "from utils import logging_tools\n"
        "LOG = logging_tools.get_logger(__name__)\n\n"
    )
    pyscript += "command = []\n"

    getb = tfs_pandas.read_tfs(getbetax_path)

    command = getb.headers["Command"].split("' '")
    command[-1] = command[-1].strip("'")
    #LOGGER.debug(command)
    command_accel = "lhc"
    command_beam = 1
    files = ""
    LOGGER.debug("Commands:")
    for i, com in enumerate(command[1:]):
        # analyse command
        words = com.split('=')
        if len(words) == 2:
            if words[0] == "--accel" or words[0] == "-a":
                pyscript += "command.append('{}')\n".format(com)
                old_accel_command = words[1]
                if words[1] == "LHCB1":
                    command_accel = "lhc"
                    command_beam = 1
                elif words[1] == "LHCB2":
                    command_accel = "lhc"
                    command_beam = 2
                LOGGER.info("-- accel: " + words[1])

            elif (words[0] == '--model' or words[0] == '-m'):
                if theseargs.model is not None:
                    LOGGER.info("... redirecting model")
                    LOGGER.info("model: " + theseargs.model)
                    command[i+1] = '--model=' + os.path.join(os.getcwd(), theseargs.model)
                    pyscript += "command.append(\"--model={}\")\n".format(theseargs.model)
                else:
                    if words[1].endswith(".dat"):
                        theseargs.model = os.path.dirname(words[1])
                    else:
                        theseargs.model = words[1]
                    LOGGER.info("-- model: " + theseargs.model)

            elif words[0] == '--files' or words[0] == "-f":
                LOGGER.info("-- files:")

                files = words[1].split(',')
                for fname in files:
                    LOGGER.debug(" - {}".format(_shorten_filename(fname)))
            else:
                pyscript += "command.append('{}')\n".format(com)
                LOGGER.info("{}: {}".format(words[0], words[1]))

    pyscript += "options, accelerator = GetLLM._parse_args(command)\n"



    LOGGER.warning("If you proceed, GetLLM will be launched. It will write to \33[1m{}\33[22m"
                   .format(theseargs.output))
    LOGGER.warning("and might overwrite an existing directory.")
    LOGGER.warning("Proceed? (y/n)")
    proceed = raw_input(">")

    print files

    if proceed == "y":
        if os.path.exists(os.path.join(theseargs.output, "measure_optics.log")):
            LOGGER.info("remove old logfile")
            os.remove(os.path.join(theseargs.output, "measure_optics.log"))
        LOGGER.info("--------------------------------------------------")
        LOGGER.info("  Starting GetLLM")
        LOGGER.info("starting measure_optics via command line . . .")

        if theseargs.original:
            p = Popen([
                "/afs/cern.ch/work/o/omc/anaconda/bin/python",
                "/media/awegsche/HDD/CernBox/MyBeta-Beat.src/Beta-Beat.src/GetLLM/GetLLM.py",
                "--accel={}".format(old_accel_command),
                "--nbcpl=1",
                "--model={}".format(os.path.join(os.getcwd(), theseargs.model, "twiss.dat")),
                "--files={}".format(",".join(files)),
                "--output={}".format(theseargs.output),
           ])

        else:
            p = Popen([
                "python",
                "/media/awegsche/HDD/CernBox/MyBeta-Beat.src/Beta-Beat.src/measure_optics.py",
                "--accel={}".format(command_accel),
                "--coupling_method=1",
                "--lhcmode=lhc_runII_2018",
                "--beam={}".format(command_beam),
                "--model_dir={}".format(os.path.join(os.getcwd(), theseargs.model)),
                "--files={}".format(",".join(files)),
                "--outputdir={}".format(theseargs.output),
                "--calibrationdir=/afs/cern.ch/eng/sl/lintrack/LHC_commissioning2017/Calibration_factors_2017/Calibration_factors_2017_beam1"
            ])
        p.wait()
        LOGGER.info("collecting debug output . . . ")
        logmessages = reinterpret_logger.read_logfile(os.path.join(theseargs.output, "measure_optics.log"))
        LOGGER.info("{} lines in log".format(len(logmessages)))

        print "\n\33[38;2;128;128;128m" + "".join(["|"] * PRINT_LINELEN) + "\33[0m"
        for logm in logmessages:
            messline = ""
            if logm.Level == "DEBUG":
                messline = DBG_FLAG + logm.Message + DBG_COLR
            elif logm.Level == "WARNING":
                messline = WRN_FLAG + logm.Message + WRN_COLR
            elif logm.Level == "ERROR":
                messline = ERR_FLAG + logm.Message + ERR_COLR
            elif logm.Level == "INFO":
                messline = NFO_FLAG + logm.Message + NFO_COLR
            else: messline = REP_FLAG + logm.Message + REP_COLR

            messline += _print_endofline(logm.Message)
            print messline + "\33[0m"

        print "\33[38;2;128;128;128m" + "".join(["|"] * PRINT_LINELEN) + "\33[0m\n"

        with open(os.path.join(theseargs.output, "thecommand.py"), "w") as thecommand:
            thecommand.write(pyscript)

        with open(os.path.join(theseargs.output, "themodel"), "w") as themodel:
            themodel.write(theseargs.model)

    elif proceed == "n":
        LOGGER.info("Cancelling")

        LOGGER.info("Exit program")
    else:
        LOGGER.error(
            "Couldn't understand '{}'. Will exit because I am confused and don't know what to do."
            .format(proceed))
        LOGGER.error("Exiting program")
        sys.exit(1)

def _print_endofline(mess):
    return "".join([" "] * min(4, PRINT_LINELEN - 11 - len(mess))) +\
            "".join(["."] * max(0, PRINT_LINELEN - 15 - len(mess))) +\
            "".join(["|"] * min(5, PRINT_LINELEN - 6 - len(mess)))


if __name__ == "__main__":
    main()
