"""Offline smoke tests for the source-readable installer. No real installation."""
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class BootstrapTests(unittest.TestCase):
    def test_shell_syntax(self):
        for script in [ROOT / 'install.sh', ROOT / 'proton/setup-jinteia.sh']:
            with self.subTest(script=script):
                subprocess.run(['bash', '-n', str(script)], check=True)

    def test_help(self):
        p = subprocess.run(['bash', str(ROOT / 'install.sh'), '--help'], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn('--heap-only', p.stdout)
        self.assertIn('--check', p.stdout)

    def test_dry_run_is_explicitly_non_destructive(self):
        p = subprocess.run(['bash', str(ROOT / 'install.sh'), '--dry-run'], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn('No files downloaded or changed.', p.stdout)

    def test_check_is_readonly_and_rejects_missing_runner(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = subprocess.run(['bash', str(ROOT / 'install.sh'), '--check', '--runner', d], capture_output=True, text=True)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn('No unique 64-bit ntdll.dll', p.stderr)
            self.assertEqual(list(Path(d).iterdir()), [])

    def test_invalid_flag(self):
        p = subprocess.run(['bash', str(ROOT / 'install.sh'), '--not-a-flag'], capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)


if __name__ == '__main__':
    unittest.main()