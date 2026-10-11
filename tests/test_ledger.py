import os
import tempfile
import unittest
from toolgate.ledger import record_evidence, list_evidence


class TestToolGateLedger(unittest.TestCase):
    def test_record_evidence_successful_proof(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            passed, code, stdout, stderr = record_evidence(
                task_name="Unit Test Verification",
                claim="All mathematical assertions hold true",
                proof_command="python3 -c 'assert 2 + 2 == 4'",
                ledger_dir=tmp_dir,
            )
            self.assertTrue(passed)
            self.assertEqual(code, 0)

            records = list_evidence(ledger_dir=tmp_dir)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["task_name"], "Unit Test Verification")
            self.assertTrue(records[0]["verified"])
            self.assertEqual(records[0]["return_code"], 0)

    def test_record_evidence_rejected_failing_proof(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            passed, code, stdout, stderr = record_evidence(
                task_name="Lint Check",
                claim="No syntax errors exist",
                proof_command="python3 -c 'raise SystemExit(42)'",
                ledger_dir=tmp_dir,
            )
            self.assertFalse(passed)
            self.assertEqual(code, 42)

            records = list_evidence(ledger_dir=tmp_dir)
            self.assertEqual(len(records), 1)
            self.assertFalse(records[0]["verified"])
            self.assertEqual(records[0]["return_code"], 42)

    def test_list_evidence_ordering(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Record two separate proofs
            record_evidence("Task 1", "Claim 1", "echo 1", ledger_dir=tmp_dir)
            record_evidence("Task 2", "Claim 2", "echo 2", ledger_dir=tmp_dir)

            records = list_evidence(ledger_dir=tmp_dir)
            self.assertEqual(len(records), 2)
            self.assertTrue(all("timestamp" in r for r in records))


if __name__ == "__main__":
    unittest.main()
