import re
import os
import sqlite3
import subprocess

def parse_output_for_jobId(log_file_path):
    """ parse output of log when submitting a job to Stepherd to get jobid"""
    regex_for_jobId = re.compile(r"Created new job with ID \d+")
    with open(log_file_path, "r") as file:
        for line in file:
            # print(line)
            match_text = regex_for_jobId.search(line)
            if match_text:
                print("Matched:", match_text.group())
                id = re.compile(r'\d+').search(match_text.group())
                if id:
                    id = id.group()
                    print("Job ID:", id)
                


def save_job_in_db(id):
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute('''INSERT INTO jobs VALUES (id,"busy")''')

def update_job_in_db(jobid, status):
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute('''UPDATE jobs VALUES (jobid,status)''')

def update_job_staus:
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    all_jobs = c.execute('''select * from jobs''')
    for jobid, status in all_jobs:
        status = find_status(jobid)
        update_status_in_db(jobid, status)

def find_status(jobid):
    '''parse output of shephered status jobid to get status '''
    output = subprocess.run(["shepherd" , "status", jobid], capture_output=True)
    regex_for_job_status = re.compile(r"Failed: [01]")
    for line in output.stderr:
            # print(line)
        match_text = regex_for_job_status.search(line)
        if match_text:
            print("Matched:", match_text.group())
            id = re.compile(r'\d').search(match_text.group())
            if id:
                id = id.group()
                print("Job Status (0 means Completed):", id)
                return id




# def create_jobs_db:
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE jobs
             (jobid int, status text)''')

if __name__ == "__main__":
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    log_rel_path = "../run/submit.log"
    log_file_path = os.path.join(script_dir, log_rel_path)
    parse_output_for_jobId(log_file_path)

