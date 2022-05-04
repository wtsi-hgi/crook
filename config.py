import os

_root    = os.environ['CROOK_ROOT'] 
logs     = f"{_root}/run"
archiver = os.environ['CROOK_ARCHIVER']
db       = f"{_root}/jobs.db"
CAPACITY_THRESHOLD = 10
