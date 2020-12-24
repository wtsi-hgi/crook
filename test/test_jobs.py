from unittest import TestCase

import jobs

from datetime import datetime
time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
import logging



class Test_Job_Database(TestCase):


    def test_save(self):
     
        jobs.save(1)
        all_jobs = jobs.findAllBusy()
        self.assertEqual(all_jobs, [(1, "busy", time)])

 
    def test_update(self):
        jobs.update(1, "completed")
        all_jobs = jobs.findAllBusy()
        self.assertEqual(all_jobs, [])

    