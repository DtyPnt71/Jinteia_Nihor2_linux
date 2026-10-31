"""Non-network smoke tests for the public terminal UI and Microsoft download helper."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent


class UITests(unittest.TestCase):
    def run_cmd(self, *args, env=None, data=''):
        merged = os.environ.copy()
        merged['NO_COLOR'] = '1'
        if env:
            merged.update(env)
        return subprocess.run(list(args), input=data, capture_output=True, text=True,
                              timeout=20, env=merged)

    def test_demo_is_safe_without_terminal_or_network(self):
        with tempfile.TemporaryDirectory() as root:
            r = self.run_cmd('bash', str(ROOT / 'install.sh'), '--demo',
                             env={'HOME': root, 'XDG_STATE_HOME': root + '/state'})
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn('J I N T E I A   P R O T O N', r.stdout)
            self.assertIn('by DtyPnt71 / Burarion', r.stdout)
            self.assertIn('keine Downloads', r.stdout)
            self.assertEqual(list(Path(root).iterdir()), [])

    def test_ui_rejects_flatpak(self):
        r = self.run_cmd('bash', str(ROOT / 'install.sh'), '--demo', '--mode', 'flatpak')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('natives Lutris', r.stdout)

    def test_webview_only_no_auto_download(self):
        with tempfile.TemporaryDirectory() as root:
            r = self.run_cmd('bash', str(ROOT / 'install.sh'), '--webview2-only',
                             env={'HOME': root})
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertFalse((Path(root) / 'Downloads').exists())

    def test_webview_download_uses_official_url_and_does_not_execute(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            bindir = root / 'bin'
            bindir.mkdir()
            fake_curl = bindir / 'curl'
            fake_curl.write_text('''#!/bin/bash
out=''
while [ "$#" -gt 0 ]; do
  if [ "$1" = '--output' ]; then out="$2"; shift 2; continue; fi
  shift
done
printf 'MZ' > "$out"
head -c 150000 /dev/zero >> "$out"
''')
            fake_curl.chmod(0o755)
            r = self.run_cmd('bash', str(ROOT / 'scripts/webview2-download.sh'), '--yes',
                             env={'HOME': str(root), 'PATH': str(bindir) + os.pathsep + os.environ['PATH']})
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            dest = root / 'Downloads/Jinteia-Proton/MicrosoftEdgeWebView2RuntimeInstallerX64.exe'
            self.assertTrue(dest.exists())
            self.assertEqual(dest.read_bytes()[:2], b'MZ')
            self.assertIn('NICHT gestartet', r.stdout)
            r2 = self.run_cmd('bash', str(ROOT / 'scripts/webview2-download.sh'), '--yes',
                              env={'HOME': str(root), 'PATH': str(bindir) + os.pathsep + os.environ['PATH']})
            self.assertEqual(r2.returncode, 0)
            self.assertIn('überschrieben', r2.stdout.lower())

    def test_webview_rejects_html_download(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            bindir = root / 'bin'
            bindir.mkdir()
            fake_curl = bindir / 'curl'
            fake_curl.write_text('''#!/bin/bash
out=''
while [ "$#" -gt 0 ]; do
  if [ "$1" = '--output' ]; then out="$2"; shift 2; continue; fi
  shift
done
printf '<html>not available</html>' > "$out"
''')
            fake_curl.chmod(0o755)
            r = self.run_cmd('bash', str(ROOT / 'scripts/webview2-download.sh'), '--yes',
                             env={'HOME': str(root), 'PATH': str(bindir) + os.pathsep + os.environ['PATH']})
            self.assertNotEqual(r.returncode, 0)
            dest = root / 'Downloads/Jinteia-Proton/MicrosoftEdgeWebView2RuntimeInstallerX64.exe'
            self.assertFalse(dest.exists())
            self.assertFalse(list(dest.parent.glob('.webview2.*')))


if __name__ == '__main__':
    unittest.main()