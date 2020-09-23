import re
import os
import subprocess
import logging
logging.basicConfig(level=logging.NOTSET)
import jobs as Jobs



def parse_output_for_jobId(log_output):
    """ parse output of log when submitting a job to Stepherd to get jobid"""
    regex_for_jobId = re.compile(r"Created new job with ID \d+")
    for line in log_output.decode('utf-8').split('\n'):
        match_text = regex_for_jobId.search(line)
        if match_text:
            logging.info(f"Matched: {match_text.group()}")
            id = re.compile(r'\d+').search(match_text.group())
            if id:
                id = id.group()
                logging.info(f"Returning Job ID: {id}")
                return id


def find_job_status(jobid):
    '''parse output of shephered status jobid to get status '''
    wd = os.getcwd()
    os.chdir("..")
    output = subprocess.run(["./shepherd.sh" , "status", str(jobid)], capture_output=True)
    output = output.stderr
    os.chdir(wd)
    #logging.debug(f"Output of shepherd status for jobid {jobid}: {output}")
    status = parse_output_for_job_status(output)
    logging.info(f"Status for jobid {jobid}: {status}")
    return status


def parse_output_for_job_status(log_output):
    # regex_for_job_status = re.compile(r"Failed: [01]")
    regex_for_job_status = re.compile(r"Transfer phase: In progress")
    for line in log_output.decode('utf-8').split('\n'):
        match_text = regex_for_job_status.search(line)
        if match_text:
            logging.info(f"Matched: {match_text.group()}. Shepherd is busy")
            return "Busy"
            # id = re.compile(r'\d').search(match_text.group())
            # if id:
            #     id = id.group()
            #     logging.debug(f"Job Status (0 means Completed): {id}")
            #     return id
    return "Completed"

def update_jobs_status():
    """ update statys of all jobs in db to latest"""
    all_jobs = Jobs.findAll()
    are_jobs_completed = True
    for row in all_jobs:
        job_id = row[0]
        job_status = row[1]
        status = find_job_status(job_id)
        Jobs.update(job_id, job_status)
        if status == "Busy":
            are_jobs_completed = False
    return are_jobs_completed


def get_status_from_file():
    script_dir = os.path.dirname(__file__)
    log_rel_path = "../run/crook/status.txt"
    log_file_path = os.path.join(script_dir, log_rel_path)
    with open(log_file_path, 'r') as f:
        return f.read()

if __name__ == "__main__":
    # script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    # log_rel_path = "../run/crook/submit.log"
    # log_file_path = os.path.join(script_dir, log_rel_path)
    # with open(log_file_path, 'r') as f:
    #     parse_output_for_jobId(f)
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    log_rel_path = "../status-in-progress.txt"
    log_file_path = os.path.join(script_dir, log_rel_path)
    with open(log_file_path, 'br') as f:
        parse_output_for_job_status(f.read())
