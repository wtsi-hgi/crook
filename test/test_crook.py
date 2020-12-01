from unittest import TestCase, mock
import subprocess
import logging
import os
from pathlib import Path

import crook
import config

import datetime
date = datetime.date.today() 


class Test_Crook(TestCase):

    def setUp(self):
        completed_process = subprocess.run(['test/vault-test.sh'], capture_output=True)
        self.input_files = completed_process.stdout.decode('utf-8') + "\x00"
        logging.debug(f"Test Set Up. File in staging: {self.input_files}")
        # output = "/tmp/tmp.9Q0LiyUGjP/.vault/.staged/08/98-bXlfdGVzdF9maWxl\x00"
        self.jobid_mock = 1
        self.sample_stderr = b"Created new job with ID 1"

    
    @mock.patch('crook.subprocess.run')
    @mock.patch('crook.Jobs.save')
    def test_basic_case(self, jobsdb_save_mock, shepherd_submit_mock):
        """Test if the correct run directory is passed and jobs database is called""" 

        # sys.stdin.read() will return "/tmp/tmp.9Q0LiyUGjP/.vault/.staged/08/98-bXlfdGVzdF9maWxl\x00"
        crook.sys.stdin.read = lambda :self.input_files
        # subprocess.run() will return shepherd_submit_mock instead of completed_process. shepherd_submit_mock.stderr will return sample_stderr instead of actual std err. 
        shepherd_submit_mock.return_value.stderr = self.sample_stderr

        crook.main(None)

        # check correct file names were passed to shepherd run path
        _FOFN = Path(config.logs) / f"crook-{date}" /"fofn"
        with open(_FOFN, 'r') as fofn:
            input_files = self.input_files.split('\x00')
            for input_file, saved_file in zip(input_files, fofn) :
                self.assertEqual(input_file, saved_file.strip())

        # Check if shepherd submit was called with correct run path
        shepherd_submit_mock.assert_called_once_with([Path(config.archiver), "submit", f"crook-{date}"], capture_output=True)

        # Check if local jobs db was called to save the new job
        jobsdb_save_mock.assert_called_once_with(self.jobid_mock)



     



