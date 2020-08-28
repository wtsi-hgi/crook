#!/usr/bin/env bash





# Script for Crook which satisfies the interface expected by Vault. It will be an executable that provides the following interface: /path/to/executable [ready]. 
# If the ready argument is provided, the handler will exit with a zero exit code if it is ready to consume the queue, otherwise it will exit with 1.f no arguments are provided, then the handler will read \0-delimited filenames from standard input. These will be the files to archive and delete.

# Function: Take files from /.vault/.staged  and (1) archive them (2) move to iRODS (3) delete original file (Note: it is the handler's responsibility to delete staged files from vaults, once they are dealt with. Failing to delete staged files will cause the vault to increase in size in perpetuity)


# Steps:

# 1. Assign fd 123 as input to a file named ".lock" 2. Obtain a write lock on file descriptor 123.  3. Saved lock status in variable locked
# Open connection to the SQLite database to track Shepherd Job IDs

# 4. If ready option is passed:
     # shepherd ready && exit 1 (Exit Code 1: Shepherd is busy with a previous job.)
     # check shephord capacity (Exit Code 2: The requested capacity is not available.
       # exit with the status of locked (If locked successfully, exit with 0, else with 1
    
    # When a "ready challenge" is received, crook must:
        # Update the status of all incomplete Shepherd jobs in its tracking database.
    # Return positively if all jobs have completed; otherwise return negatively.

# 5. If ready option is not passed, then if locked successfully do nothing. If locked unsuccessfully, exit with 1. 
# 6. xargs  # submit_to_shepherd -0  "name formating..." --remove-files 


exec 123>.lock
flock -nx 123
locked=$?


# This toy handler uses flock to provide filesystem-based locking, to facilitate the ready interface (described above), otherwise it slurps in standard input (the incoming list of filenames) and sends it to tar to create an archive file. Clearly this is not production ready (e.g., it is not defensive against failure), but illustrates how a downstream handler should operate.

# Note that the stream of filenames provided from the drain phase will be the vault files, with their obfuscated names. It is up to the downstream handler to decode these, if necessary.




case $1 in
  ready)  
     for jobid in jobids
        # shepherd status jobid && exit 1;; # (Exit Code 1: Shepherd is busy with a previous job.)
    # check_shephord_capacity $2 && exit 2;; #(Exit Code 2: The requested capacity is not available.)
     exit ${locked};;
  *)      (( locked )) && exit 1;;
esac


xargs tar czf "$(date +%F).tar.gz"

# xargs -0 submit_to_shepherd "name formating..." --remove-files (Exit Code 0: The input data was fully consumed and passed to Shepherd successfully.)
    # Processing of the stream could not be concluded before handling to Shepherd.
    


# crook must only exit with a successful exit code if the process was fully successful, as this will instruct HGI Vault to irrecoverably clear its staging queue. Ensure that any unexpected exit will result in a failure exit code.

# crook will only ever be run serially, by a single user, so its tracking database can be file-based (e.g., SQLite). Shepherd maintains the files it needs to process internally, so these will not also need to be maintained by crook.


