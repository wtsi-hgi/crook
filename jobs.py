import sys
import sqlite3
import logging

import config

_DB = config.db


def create_connection(db):
    """create a database connection to the SQLite database specified  by db"""
    conn = None
    try:
        # When you connect to an SQLite database file that does not exist, SQLite automatically creates the new database for you.
        conn = sqlite3.connect(db)
        # This will be called on every transaction
        conn.set_trace_callback(logging.debug)
    except Exception as e:
        print(f"{e}: {db}")
        sys.exit(1)

    return conn


def create_table():
    conn = create_connection(_DB)
    query = '''CREATE TABLE IF NOT EXISTS jobs
             (id int PRIMARY KEY, status text, job_time text)'''
    try:
        with conn:
            conn.execute(query)
    except Exception as e:
        logging.error(f"Could not create table: {e}")

    conn.close()


def findAllBusy():
    """Return list of all crook jobs"""
    print(f"DB: {_DB}")
    conn = create_connection(_DB)
    query = '''SELECT * from jobs WHERE status = "busy"'''
    all_jobs = []
    try:
        with conn:
            all_jobs = conn.execute(query)
            all_jobs = all_jobs.fetchall()
    except Exception as e:
        logging.error(f"Could not exeute find all busy jobs query: {e}")
        raise e

    conn.close()
    logging.info(f"Output of finding all busy jobs: {all_jobs}")
    return all_jobs


# Might be userful later: https://stackoverflow.com/questions/418898/sqlite-upsert-not-insert-or-replace

def save(id):
    conn = create_connection(_DB)
    query = f"INSERT OR REPLACE INTO jobs(id, status, job_time) VALUES (?, ?, strftime('%Y-%m-%d %H:%M:%S')) "
    
    try:
        with conn:
            conn.execute(query, (id, 'busy'))
    except Exception as e:
        logging.error(f"Could save job: {e}")
    conn.close()


def update(job_id, job_status):
    conn = sqlite3.connect(_DB)
    query = f'''UPDATE jobs SET status = ? WHERE id = ?'''
    try:
        with conn:
            conn.execute(query, (job_status, job_id))
    except Exception as e:
        logging.error(f"Could save job: {e}")
    conn.close()

logging.info("Checking if local jobs database exists")
create_table()

