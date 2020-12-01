import re
import os
import subprocess
import logging
logging.basicConfig(level=logging.NOTSET)

import jobs as Jobs
import config


_SHEPHERD_SUBMIT_JOBID_REGEX = r"Created new job with ID \d+"
_SHEPHERD_STATUS_JOBID_REGEX = r"Transfer phase: In progress"


                
def update_jobs_status():
    """ update statys of all jobs in db to latest"""
    all_jobs = Jobs.findAll()
    are_jobs_completed = True
    for row in all_jobs:
        job_id = row[0]
        old_status = row[1]
        new_status = find_job_status(job_id)
        Jobs.update(job_id, new_status)
        if new_status == "Busy":
            are_jobs_completed = False
    return are_jobs_completed


def find_job_status(jobid):
    """parse output of shephered status jobid to get status"""
    output = subprocess.run([config.archiver , "status", str(jobid)], capture_output=True)
    output = output.stderr
    status = parse_output_for_job_status(output)
    logging.info(f"Status for jobid {jobid}: {status}")
    return status


def parse_output_for_job_status(log_output):
    # regex_for_job_status = re.compile(r"Failed: [01]")
    regex_for_job_status = re.compile(_SHEPHERD_STATUS_JOBID_REGEX)
    for line in log_output.decode('utf-8').split('\n'):
        match_text = regex_for_job_status.search(line)
        if match_text:
            logging.info(f"Matched: {match_text.group()}. Shepherd is busy")
            return "Busy"
    return "Completed"

def parse_output_for_jobId(log_output): 
    """ parse output of log when submitting a job to Stepherd to get jobid"""
    regex_for_jobId = re.compile(_SHEPHERD_SUBMIT_JOBID_REGEX)
    for line in log_output.decode('utf-8').split('\n'):
        match_text = regex_for_jobId.search(line)
        if match_text:
            logging.info(f"Matched: {match_text.group()}")
            id = re.compile(r'\d+').search(match_text.group())
            if id:
                id = id.group()
                logging.info(f"Returning Job ID: {id}")
                return int(id)

