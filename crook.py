import argparse
import fileinput
import os
import sys
from pathlib import Path
import logging
logging.basicConfig(level=logging.NOTSET)
import subprocess
import datetime 
import json

import crook_jobs
import jobs as Jobs

date = datetime.date.today() 
_RUN_PATH = Path(f"../run/crook-{date}")

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

def get_fofn_index():
    i = 0
    while os.path.exists(_RUN_PATH/ "fofn-%s" % i):
        i = i + 1
    print("Returning fofn index: ", i )
    return i



def main(capacity):
    if capacity:
        is_ready(capacity)
    else:
        os.makedirs(_RUN_PATH , exist_ok = True) 
         # FIXME: Instead of loading the entire in memory at once, have \0 as line separator in shepherd and pass it line by line
        files = sys.stdin.read()
        files = files.replace('\x00', '\n')
        logging.info(f"Writing temporary fofn at: {_RUN_PATH}/fofn")
        with open(_RUN_PATH  / "fofn", 'w') as f:
            f.write(files)

        metadata = {
            "archive-date": str(date),
            "archived-by": "crook"
        }
        logging.info(f"Writing metadata at: {_RUN_PATH}/metadata.json")
        with open(_RUN_PATH  / "metadata.json", 'w') as f:
            json.dump(metadata, f)
        wd = os.getcwd()
        os.chdir("..")
        completed_process = subprocess.run(['./shepherd.sh', 'submit', f'crook-{date}'], capture_output=True)
        os.chdir(wd)
        # Use Logging instead of print. 

        #logging.debug(f"Stderr of `./shepherd.sh submit crook: {completed_process.stderr.decode('utf-8')}")

        stderr = completed_process.stderr
        job_id = crook_jobs.parse_output_for_jobId(stderr)
        if job_id is None:
            logging.critical(f"JobID not found in the stderr of shepherd submit:\n {stderr.decode('utf-8')}")
            raise Exception("JobID not found")
        Jobs.save(job_id)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, _RUN_PATH)
        logging.info(f"Saving fofn with job id at: {_RUN_PATH}/fofn-{job_id}") 
        with open(_RUN_PATH  / f"fofn-{job_id}", 'w') as f:
            f.write(files)
      
        #Shepherd accepts a file of filenames as input to its submit subcommand. However, this file is assumed to be n-delimited in the current release. However, the code exists to specify an arbitrary delimiter (see shepherd:cli.dummy.prepare, which calls shepherd:common.models.filesystems.posix._identify_by_fofn).

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hand off files to archive to Shepherd")
    parser.add_argument('ready', nargs = '?', help = 'check if shepherd is ready')
    parser.add_argument('capacity', nargs = '?', type = int, help = 'check if shepherd has the requisite capacity')
    args = parser.parse_args()
    capacity = args.ready
    main(capacity)
   
   
    
    
    