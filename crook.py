import argparse
import fileinput
from logging import log


import crook_jobs.py


def is_ready(capacity):
    if is_shepherd_busy():
        exit 1
    if is_capacity_full(capacity):
        exit 2
    exit 0  


def is_shepherd_busy:
    are_jobs_completed = crook_jobs.update_jobs_status()
    return !are_jobs_completed

# TOIMPLEMENT
def is_capacity_full(capacity):
    return False
    '''When crook is given a "ready challenge", it must check that the available capacity of the archival location (i.e., the Humgen iRODS zone) exceeds that which is requested, plus a 10% threshold. For example, if a capacity of 1000 bytes is requested, crook must only respond positively if at least 1100 bytes are available.'''

    # It is not straightforward to determine the remaining space available in an iRODS zone with icommands. It can be done with iquest and a suitable query, but there is no df-equivalent; fortunately, ISG run such a script and use it to populate Graphite -- the backend used by the metrics dashboards -- which provides a RESTful interface. crook can use this interface. TODO Interface details from ISG/Graphite documentation: URL, request and response.


def main(capacity):
    if capacity:
        is_ready(capacity)
    else:
        # read from stdin \0 delimited filenames. From the docs: "Note that if you want to send data to the process’s stdin, you need to create the Popen object with stdin=PIPE. Similarly, to get anything other than None in the result tuple, you need to give stdout=PIPE and/or stderr=PIPE too."
        subprocess.run(['../shepherd.sh', 'submit'], input = sys.stdin)
        #Shepherd accepts a file of filenames as input to its submit subcommand. However, this file is assumed to be n-delimited in the current release. However, the code exists to specify an arbitrary delimiter (see shepherd:cli.dummy.prepare, which calls shepherd:common.models.filesystems.posix._identify_by_fofn).

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hand off files to archive to Shepherd)
    parser.add_argument('ready', type = int, nargs = '?', help = 'check if shepherd is ready to take a new job of input capacity ')
    args = parser.parse_args()
    capacity = args.ready
    main(capacity)
