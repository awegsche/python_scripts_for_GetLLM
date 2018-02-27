import os
import sys
import argparse
import logging

sys.path.append("/home/awegsche/Beta-Beat.src/")
sys.path.append("/home/awegsche/Beta-Beat.src/GetLLM")

from GetLLM import GetLLM
from GetLLM import GetLLMError
from utils import logging_tools
from utils import tfs_pandas

LOGGER = logging_tools.get_logger(__name__, level_console=logging.DEBUG)


parser = argparse.ArgumentParser()

parser.add_argument("-s", "--source", dest="source", type=str, help="the output folder of the original analysis")
parser.add_argument("-o", "--output", dest="output", type=str, help="the NEW output folder")
parser.add_argument("--loglevel", dest="loglevel", type=str, default="DEBUG", metavar="LEVEL",
                    help="the log level (DEBUG, INFO, WARN). Default=DEBUG")
parser.add_argument("-m", "--model", dest="model", type=str, help="change the model folder", default=None)
theseargs = parser.parse_args()

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
#LOGGER.debug(command[1:])

options, accelerator = GetLLM._parse_args(command[1:])

LOGGER.debug("--------------------------------------------------")
LOGGER.debug("---- GetLLM options: -----------------------------")

for key, value in options.__dict__.iteritems():
    if key == "files":
        files = value.split(',')
        LOGGER.debug("- {:12s} :".format("files", files[0]))
        for fname in files:
            LOGGER.debug("-- {}".format(fname))
    else:
        LOGGER.debug("- {:12s} = {}".format(key, value))

LOGGER.debug("--------------------------------------------------")

options.output = theseargs.output
if theseargs.model is not None:
    options.model_dir = theseargs.model

LOGGER.warning("If you procedd, GetLLM will be launched. It will write to {}".format(options.output))
LOGGER.warning("and might overwrite an existing directory.")
LOGGER.warning("Proceed? (y/n)")
proceed = raw_input(">")

if proceed == "y":
    LOGGER.info("--------------------------------------------------")
    LOGGER.info("  Starting GetLLM")

    if options.errordefspath is not None:
        accelerator.set_errordefspath(options.errordefspath)

    GetLLM.main(accelerator,
         options.model_dir,
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


elif proceed == "n":
    LOGGER.info("Cancelling")
    LOGGER.error("Exiting program")
    sys.exit(1)
else:
    LOGGER.error("Couldn't understand '{}'. Will exit because I am confused and don't know what to do.".format(proceed))
    LOGGER.error("Exiting program")
    sys.exit(1)
