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
import requests

import crook_jobs
import jobs as Jobs
import config


time = datetime.now().strftime('%H-%M-%d-%m-%Y')
# Location for logs and the source of data(fofn, metadata etc.) for shepherd.
_LOG_PATH = Path(config.logs) / f"crook-{time}"
_ARCHIVER_PATH = Path(config.archiver)


def fileLineIter(inputFile,
                 inputNewline="\x00",
                 outputNewline="\n",
                 readSize=8192):
    last = ""
    while True:
        block = inputFile.read(readSize)
        # print(f"block: {block}")
        if not block: break
        record_chunks = block.split(inputNewline)
        if len(record_chunks) == 1:
            last += record_chunks
        else:
        
            x = last + record_chunks[0] + outputNewline
            yield x
            for record in record_chunks[1:-1]:
                yield record + outputNewline

            last = record_chunks[-1]
    if last:
        yield last + outputNewline

def is_ready(requested_capacity):
    if is_shepherd_busy():
        sys.exit(1)
    if is_capacity_full(requested_capacity, config.CAPACITY_THRESHOLD):
        sys.exit(2)
    sys.exit(0)  


def is_shepherd_busy():
    are_jobs_completed = crook_jobs.update_jobs_status()
    return not are_jobs_completed

def is_capacity_full(requested, threshold):
    '''When crook is given a "ready challenge", it must check that the available capacity of the archival location (i.e., the Humgen iRODS zone) exceeds that which is requested, plus a 10% threshold. For example, if a capacity of 1000 bytes is requested, crook must only respond positively if at least 1100 bytes are available.'''
    green_free = find_free_capacity("green")
    red_free = find_free_capacity("red")
    available = min(green_free, red_free)
    needed = requested*(1+ threshold/100)
    if available < needed:
        print(f" Available capacity {available} is less than needed (requested capacity + {threshold}%): {needed}")
        return True
    else:
        print(f" Available capacity {available} is more than needed (requested capacity + {threshold}%): {needed}")
        return False
    
def find_free_capacity(colour):
    '''Helper method to query Graphite API for irods capacity in the relevant replica. At the moment of writing, the replicas are named "red" and "green"'''

    _URL = f"http://graphite.internal.sanger.ac.uk/render?target=irods.v4capacity.humgen.{colour}.free&format=json&PRETTY=1"
    r = requests.get(_URL)
    data = r.json()
    # Expected data = ['project':.... 'datapoints: [..., [bytes, UNIX timestamp - 1 hour], [bytes, UNIX timestamp]]'].
    # If you do the request on the hour (up to ~15 minutes thereafter), the last tuple's value is (null, <timestamp>); presumably because the datapoint is still being calculated. Your code should return the latest non-null datapoint, rather than assuming the last one is valid.
    free_bytes = None
    while free_bytes == None:
        free_bytes = int(data[0]['datapoints'].pop()[0])
    return free_bytes
   

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
    
        logging.info(f"Writing temporary fofn at: {_LOG_PATH}/fofn")

        with open(_LOG_PATH  / "fofn", 'w') as f:
            for filepath in fileLineIter(inputFile = sys.stdin, inputNewline="\x00",
                 outputNewline="\n", readSize = 1024):
                logging.debug(f"Writing file path to disk after inserting new line character: {filepath}")
                f.write(filepath)

        # logging.info(f"Reading file paths from stdin: {files}")

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hand off files to archive to Shepherd")
    parser.add_argument('ready', nargs = '?', help = 'check if shepherd is ready')
    parser.add_argument('capacity', nargs = '?', type = int, help = 'check if shepherd has the requisite capacity')
    args = parser.parse_args()
    requested_capacity = args.capacity
    main(requested_capacity)