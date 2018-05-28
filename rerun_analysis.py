""" Reruns a specified analysis
"""
import os
import sys
import re
import argparse
import logging
import pandas
import numpy as np

# GETLLM paths
import betabeatsrc
from GetLLM import GetLLM
from GetLLM import GetLLMError
from utils import logging_tools
from utils import tfs_pandas
from model import manager
import pyterminal

LOGGER = logging_tools.get_logger(__name__, level_console=logging.INFO)
LOGGER.addHandler(logging_tools.stream_handler(max_level=logging.DEBUG))

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

    if os.path.isfile(os.path.join(theseargs.source, "getbetax_free.out")):
        getbetax_path = os.path.join(theseargs.source, "getbetax_free.out")
    elif os.path.isfile(os.path.join(theseargs.source, "getbetax.out")):
        getbetax_path = os.path.join(theseargs.source, "getbetax.out")
    else:
        LOGGER.error("Source could not be found")
        sys.exit(1)



    getb = tfs_pandas.read_tfs(getbetax_path)

    command = getb.headers["Command"].split("' '")
    command[-1] = command[-1].strip("'")
    #LOGGER.debug(command)
    command_accel = "lhc"
    command_beam = 1
    LOGGER.debug("Commands:")
    for com in command[1:]:
        # analyse command
        words = com.split('=')
        if len(words) == 2:
            LOGGER.debug("{}: {}".format(words[0], words[1]))
            if words[0] == "--accel" or words[0] == "-a":
                if words[1] == "LHCB1":
                    command_accel = "lhc"
                    command_beam = 1
                elif words[1] == "LHCB2":
                    command_accel = "lhc"
                    command_beam = 2


    options, accelerator = GetLLM._parse_args(command[1:])

    LOGGER.debug("--------------------------------------------------")
    LOGGER.debug("---- GetLLM options: -----------------------------")

    for key, value in options.__dict__.iteritems():
        if key == "files":
            files = value.split(',')
            LOGGER.debug("- {:12s} :".format(files[0]))
            for fname in files:
                LOGGER.debug("-- {}".format(fname))
        else:
            LOGGER.debug("- {:12s} = {}".format(key, value))

    LOGGER.debug("--------------------------------------------------")

    options.output = theseargs.output
    if theseargs.serial:
        options.nprocesses = 0
    if theseargs.model is not None:
        options.model_dir = theseargs.model
        accelerator = manager.get_accel_instance(
            accel=command_accel, beam=command_beam, model_dir=theseargs.model)
    if theseargs.no_union:
        options.union = 0

    LOGGER.warning("If you proceed, GetLLM will be launched. It will write to {}"
                   .format(options.output))
    LOGGER.warning("and might overwrite an existing directory.")
    LOGGER.warning("Proceed? (y/n)")
    proceed = raw_input(">")

    if proceed == "y":
        LOGGER.info("--------------------------------------------------")
        LOGGER.info("  Starting GetLLM")


        if options.errordefspath is not None:
            accelerator.set_errordefspath(options.errordefspath)

        GetLLM.main(
            accelerator,
            accelerator.model_dir,
            outputpath=options.output,
            files_to_analyse=options.files,
            lhcphase=options.lhcphase,
            bpmu=options.BPMUNIT,
            cocut=float(options.COcut),
            nbcpl=int(options.NBcpl),
            nonlinear=options.nonlinear,
            bbthreshold=options.bbthreshold,
            errthreshold=options.errthreshold,
            use_only_three_bpms_for_beta_from_phase=options.use_only_three_bpms_for_beta_from_phase,
            number_of_bpms=options.number_of_bpms,
            range_of_bpms=options.range_of_bpms,
            use_average=options.use_average,
            calibration_dir_path=options.calibration_dir_path,
            nprocesses=options.nprocesses,
            union=options.union)

        with open(os.path.join(options.output, "themodel"), "w") as themodel:
            themodel.write(accelerator.model_dir)

    elif proceed == "n":
        LOGGER.info("Cancelling")

        LOGGER.info("Exit program")
    else:
        LOGGER.error(
            "Couldn't understand '{}'. Will exit because I am confused and don't know what to do."
            .format(proceed))
        LOGGER.error("Exiting program")
        sys.exit(1)

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


if __name__ == "__main__":
    main()
