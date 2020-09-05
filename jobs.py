

import sqlite3


_DB_NAME = 'jobs.db'


def create_connection(db):
    """create a database connection to the SQLite database specified  by db"""
    conn = None
    try:
        # When you connect to an SQLite database file that does not exist, SQLite automatically creates the new database for you.
        conn = sqlite3.connect(db)
        conn.set_trace_callback(print)
    except Error as e:
        print(e)

    return conn


def create_table():
    conn = create_connection(_DB_NAME )
    query = '''CREATE TABLE IF NOT EXISTS jobs
             (id int PRIMARY KEY, status text)'''
    conn.execute(query)
    conn.commit()
    conn.close()


def findAll():
    conn = create_connection(_DB_NAME)
    c = conn.cursor()
    query = '''SELECT * from jobs'''
    all_jobs = conn.execute(query)
    all_jobs = all_jobs.fetchall()
    conn.commit()
    conn.close()
    print("All Jobs: ", all_jobs)
    return all_jobs


# Might be userful later: https://stackoverflow.com/questions/418898/sqlite-upsert-not-insert-or-replace

def save(id):
    conn = create_connection(_DB_NAME )
    # Instead of print, you may want to use a function from the logging module.
    # c = conn.cursor()
    query = f"INSERT OR REPLACE INTO jobs(id, status) VALUES (?, ?) "
    x = conn.execute(query, (id, 'busy'))
    conn.commit()
    conn.close()


def update(job_id, job_status):
    conn = sqlite3.connect(_DB_NAME)
    query = f'''UPDATE jobs SET status = ? WHERE id = ?'''
    print(f"Excuting update on {job_id} with {job_status}")
    conn.execute(query, (job_status, job_id))
    conn.commit()
    conn.close()





create_table()


if __name__ == "__main__":
   save(1)
   findAll()
   update(1, "completed")
   findAll()

