import argparse
import fileinput
import os
import sys
import logging
logging.basicConfig(level=logging.NOTSET)
import subprocess
import json
from datetime import datetime
from pathlib import Path

import crook_jobs
import jobs as Jobs
import config


time = datetime.now().strftime('%H-%M-%d-%m-%Y')
# Location for logs and the source of data(fofn, metadata etc.) for shepherd.
_LOG_PATH = Path(config.logs) / f"crook-{time}"
_ARCHIVER_PATH = Path(config.archiver)


def fileLineIter(inputFile,
                 inputNewline="\x00",
                 outputNewline=None,
                 readSize=8192):
   """Like the normal file iter but you can set what string indicates newline.
   
   The newline string can be arbitrarily long; it need not be restricted to a
   single character. You can also set the read size and control whether or not
   the newline string is left on the end of the iterated lines.  Setting
   newline to '\x00' is particularly good for use with an input file created with
   something like "os.popen('find -print0')".
   """
   if outputNewline is None: 
        outputNewline = inputNewline
        partialLine = ''
   while True:
       charsJustRead = inputFile.read(readSize)
       if not charsJustRead: break
       partialLine += charsJustRead
       lines = partialLine.split(inputNewline)
       partialLine = lines.pop()
       for line in lines: yield line + outputNewline
   if partialLine: yield partialLine

def is_ready(capacity):
    if is_shepherd_busy():
        sys.exit(1)
    if is_capacity_full(capacity):
        sys.exit(2)
    sys.exit(0)  


def is_shepherd_busy():
    are_jobs_completed = crook_jobs.update_jobs_status()
    return not are_jobs_completed

# TOIMPLEMENT
def is_capacity_full(capacity):
    return False
    '''When crook is given a "ready challenge", it must check that the available capacity of the archival location (i.e., the Humgen iRODS zone) exceeds that which is requested, plus a 10% threshold. For example, if a capacity of 1000 bytes is requested, crook must only respond positively if at least 1100 bytes are available.'''

    # It is not straightforward to determine the remaining space available in an iRODS zone with icommands. It can be done with iquest and a suitable query, but there is no df-equivalent; fortunately, ISG run such a script and use it to populate Graphite -- the backend used by the metrics dashboards -- which provides a RESTful interface. crook can use this interface. TODO Interface details from ISG/Graphite documentation: URL, request and response.


def add_metadata():
    metadata = {
            "archive-date": str(time),
            "archived-by": "crook"
        }

    logging.info(f"Writing metadata at: {_LOG_PATH}/metadata.json")
    with open(_LOG_PATH  / "metadata.json", 'w') as f:
        json.dump(metadata, f)


def main(capacity = None):
     # if capacity argument is passed, then just return boolean as to ready or not.
    if capacity:
        is_ready(capacity)
    else:
    # if capacity argument is not passed, then read input files from stdin and pass them to shepherd submit.
        logging.info(f"Crook logging at: {_LOG_PATH}")
        os.makedirs(_LOG_PATH , exist_ok = True) 
         # FIXME: Instead of loading the entire in memory at once, have \0 as line separator in shepherd and pass it line by line
        
        files = sys.stdin.read()
        logging.info(f"Reading file paths from stdin: {files}")
        logging.info(f"Inserting new line characters")
        files = files.replace('\x00', '\n')
        logging.info(f"Writing temporary fofn at: {_LOG_PATH}/fofn")
        with open(_LOG_PATH  / "fofn", 'w') as f:
            f.write(files)

        # Write metadata submitted to shepherd. This is optional
        add_metadata()

      
        try:
            completed_process = subprocess.run([_ARCHIVER_PATH, 'submit', f"crook-{time}"], capture_output=True)
        except Exception as e:
            raise e
        # Use Logging instead of print. 
        #logging.debug(f"Stderr of `./shepherd.sh submit crook: {completed_process.stderr.decode('utf-8')}")

        stderr = completed_process.stderr
        job_id = crook_jobs.parse_output_for_jobId(stderr)
        if job_id is None:
            logging.critical(f"JobID not found in the stderr of shepherd submit:\n {stderr.decode('utf-8')}")
            raise Exception("JobID not found")
        Jobs.save(job_id)
       

        # Write fofn submitted to shepherd with job id for logging and debugging
        logging.info(f"Saving fofn with job id at: {_LOG_PATH}/fofn-{job_id}")  
        with open(_LOG_PATH  / f"fofn-{job_id}", 'w') as f:
            f.write(files)
      
        #Shepherd accepts a file of filenames as input to its submit subcommand. However, this file is assumed to be n-delimited in the current release. However, the code exists to specify an arbitrary delimiter (see shepherd:cli.dummy.prepare, which calls shepherd:common.models.filesystems.posix._identify_by_fofn).


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hand off files to archive to Shepherd")
    parser.add_argument('ready', nargs = '?', help = 'check if shepherd is ready')
    parser.add_argument('capacity', nargs = '?', type = int, help = 'check if shepherd has the requisite capacity')
    args = parser.parse_args()
    capacity = args.capacity
    main(capacity)