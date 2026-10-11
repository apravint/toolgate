import subprocess
import sys
import unittest


class TestToolGateCLI(unittest.TestCase):
    def test_cli_help(self):
        res = subprocess.run(
            [sys.executable, "-m", "toolgate.cli", "--help"],
            capture_output=True,
            text=True
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("ToolGate", res.stdout)
        self.assertIn("check", res.stdout)
        self.assertIn("verify", res.stdout)
        self.assertIn("ledger", res.stdout)

    def test_cli_check_safe_command(self):
        res = subprocess.run(
            [sys.executable, "-m", "toolgate.cli", "check", "git status"],
            capture_output=True,
            text=True
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("TOOLGATE: ALLOWED", res.stdout)

    def test_cli_check_denied_command(self):
        res = subprocess.run(
            [sys.executable, "-m", "toolgate.cli", "check", "rm -rf /"],
            capture_output=True,
            text=True
        )
        self.assertEqual(res.returncode, 1)
        self.assertIn("TOOLGATE: DENIED", res.stdout)

    def test_cli_verify_success(self):
        res = subprocess.run(
            [
                sys.executable,
                "-m",
                "toolgate.cli",
                "verify",
                "Feature Build",
                "Build finished with 0 warnings",
                "echo 'Compiled OK'",
            ],
            capture_output=True,
            text=True
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Proof Verified", res.stdout)

    def test_cli_verify_failure(self):
        res = subprocess.run(
            [
                sys.executable,
                "-m",
                "toolgate.cli",
                "verify",
                "Failing Task",
                "Claiming done anyway",
                "false",
            ],
            capture_output=True,
            text=True
        )
        self.assertEqual(res.returncode, 1)
        self.assertIn("Proof Failed", res.stdout)

    def test_cli_ledger_view(self):
        res = subprocess.run(
            [sys.executable, "-m", "toolgate.cli", "ledger"],
            capture_output=True,
            text=True
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Evidence Ledger Records", res.stdout)


if __name__ == "__main__":
    unittest.main()
