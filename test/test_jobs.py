from unittest import TestCase

import jobs


class Test_Job_Database(TestCase):


    def test_save(self):
        jobs.save(1)
        all_jobs = jobs.findAll()
        self.assertEqual(all_jobs, [(1, "busy")])

    def test_update(self):
        jobs.update(1, "completed")
        all_jobs = jobs.findAll()
        self.assertEqual(all_jobs, [(1, "completed")])

    