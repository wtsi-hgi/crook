import argparse
import fileinput
import os
import sys
from pathlib import Path
import subprocess

import crook_jobs
import jobs as Jobs


_RUN_PATH = Path('../run/crook')


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


def main(capacity):
    if capacity:
        is_ready(capacity)
    else:
        os.makedirs(_RUN_PATH , exist_ok = True)        
        with open(_RUN_PATH  / "crook.fofn", 'w') as f:
            files = sys.stdin.read()
            files.replace(r'\0', r'\n')
            f.write(files)
        wd = os.getcwd()
        os.chdir("..")
        output = subprocess.run(['./shepherd.sh', 'submit', 'crook'], capture_output=True)
        os.chdir(wd)
        print("Output:" , output)
        job_id = crook_jobs.parse_output_for_jobId(output.stderr)
        Jobs.save(job_id)
        #Shepherd accepts a file of filenames as input to its submit subcommand. However, this file is assumed to be n-delimited in the current release. However, the code exists to specify an arbitrary delimiter (see shepherd:cli.dummy.prepare, which calls shepherd:common.models.filesystems.posix._identify_by_fofn).

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hand off files to archive to Shepherd")
    parser.add_argument('ready', nargs = '?', help = 'check if shepherd is ready')
    parser.add_argument('capacity', nargs = '?', type = int, help = 'check if shepherd has the requisite capacity')
    args = parser.parse_args()
    capacity = args.ready
    main(capacity)
