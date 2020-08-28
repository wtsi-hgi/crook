

import sqlite3


_DB_NAME = 'jobs.db'

def create_db:
    conn = sqlite3.connect(_DB_NAME )
    c = conn.cursor()
    query = '''CREATE TABLE jobs
             (id int, status text)'''
    print("Connected to SQLite. Executing: ", query)
    c.execute(query)


def findAll():
    conn = sqlite3.connect(_DB_NAME)
    c = conn.cursor()
    query = '''SELECT * from jobs'''
    print("Connected to SQLite. Executing: ", query)
    all_jobs = c.execute(query)
    all_jobs = all_jobs.fetchAll()
    return all_jobs

def save(id):
    conn = sqlite3.connect(_DB_NAME )
    c = conn.cursor()
    c.execute('''INSERT INTO jobs VALUES (id,"busy")''')

def update(job_id, job_status):
    conn = sqlite3.connect(_DB_NAME)
    c = conn.cursor()
    query = '''UPDATE jobs SET status = job_status WHERE id = job_id'''
    print("Connected to SQLite. Executing: ", query)
    c.execute(query)

