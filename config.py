import os

_root    = os.environ['CROOK_ROOT'] 
logs     = f"{_root}/run"
archiver = f"{_root}/shepherd.sh"
db       = f"{_root}/crook/jobs.db"
CAPACITY_THRESHOLD = 10
