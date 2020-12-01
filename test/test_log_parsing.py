from unittest import TestCase
from crook_jobs import *


class Test_Log_Parsing(TestCase):

        def test_status_in_progress(self):
            with open("test/status-in-progress.txt", "br") as f:
                logs = f.read()

            status = parse_output_for_job_status(logs)
            self.assertEqual("Busy", status)

        def test_status_completed(self):
            with open("test/status-completed.txt", "br") as f:
                logs = f.read()

            status = parse_output_for_job_status(logs)
            self.assertEqual("Completed", status)

        def test_status_waiting(self):
            with open("test/status-waiting.txt", "br") as f:
                logs = f.read()

            status = parse_output_for_job_status(logs)
            self.assertEqual("Completed", status)



