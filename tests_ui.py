"""Offline regression tests for Jinteia-Proton's bilingual Bash front end."""
import os
from pathlib import Path
import pty
import select
import subprocess
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parent
UI = ROOT / "scripts" / "installer-ui.sh"
WEBVIEW = ROOT / "scripts" / "webview2-download.sh"


class BilingualUITests(unittest.TestCase):
    def run_cmd(self, *args, env=None, data=""):
        merged = {**os.environ, "NO_COLOR": "1", "LC_ALL": "C", "LANG": "C"}
        if env:
            merged.update(env)
        return subprocess.run(list(map(str, args)), input=data, text=True,
                              capture_output=True, timeout=30, env=merged)

    def test_de_demo_safely_displays_full_flow(self):
        with tempfile.TemporaryDirectory() as root:
            p = self.run_cmd('bash', UI, '--lang', 'de', '--demo',
                             env={'HOME': root, 'XDG_STATE_HOME': root + '/state'})
            self.assertEqual(p.returncode, 0, p.stderr)
            for s in ('JINTEIA', 'by DtyPnt71 / Burarion', 'VORBEREITUNG',
                      'Proton herunterladen', 'NÄCHSTE SCHRITTE', 'Keine Spieldateien'):
                self.assertIn(s, p.stdout)
            self.assertEqual(list(Path(root).iterdir()), [])

    def test_en_demo_safely_displays_full_flow(self):
        with tempfile.TemporaryDirectory() as root:
            p = self.run_cmd('bash', UI, '--lang', 'en', '--demo',
                             env={'HOME': root, 'XDG_STATE_HOME': root + '/state'})
            self.assertEqual(p.returncode, 0, p.stderr)
            for s in ('JINTEIA', 'PREPARATION', 'Download Proton',
                      'NEXT STEPS', 'No game files changed', '7 / 7'):
                self.assertIn(s, p.stdout)
            self.assertNotIn('VORBEREITUNG', p.stdout)
            self.assertEqual(list(Path(root).iterdir()), [])

    def test_language_selection_in_real_pseudo_terminal(self):
        # Only the demo is invoked; pty checks the actual 1/2 language menu.
        for choice, marker in [('1\n', 'VORBEREITUNG'), ('2\n', 'PREPARATION')]:
            with self.subTest(choice=choice):
                master, slave = pty.openpty()
                env = {**os.environ, 'TERM': 'xterm', 'NO_COLOR': '1'}
                p = subprocess.Popen(['bash', str(UI), '--demo'], stdin=slave,
                                     stdout=slave, stderr=slave, env=env,
                                     start_new_session=True)
                os.close(slave)
                data = bytearray()
                try:
                    deadline = time.monotonic() + 10
                    sent = False
                    while time.monotonic() < deadline:
                        readable, _, _ = select.select([master], [], [], 0.15)
                        if readable:
                            try:
                                chunk = os.read(master, 65536)
                            except OSError:
                                chunk = b''
                            data.extend(chunk)
                        if not sent and b'Auswahl / Choice' in data:
                            os.write(master, choice.encode())
                            sent = True
                        if p.poll() is not None:
                            break
                    self.assertIsNotNone(p.poll(), 'Language prompt hung')
                    self.assertEqual(p.returncode, 0, data.decode(errors='replace'))
                    output = data.decode(errors='replace')
                    self.assertIn('LANGUAGE / SPRACHE', output)
                    self.assertIn(marker, output)
                finally:
                    if p.poll() is None:
                        p.kill()
                    p.wait(timeout=5)
                    os.close(master)

    def test_install_sh_dispatches_explicit_language_to_ui(self):
        for lang, expected in [('de', 'VORBEREITUNG'), ('en', 'PREPARATION')]:
            with self.subTest(lang=lang):
                with tempfile.TemporaryDirectory() as root:
                    p = self.run_cmd('bash', ROOT / 'install.sh', '--lang', lang, '--demo',
                                     env={'HOME': root})
                    self.assertEqual(p.returncode, 0, p.stderr)
                    self.assertIn(expected, p.stdout)
                    self.assertEqual(list(Path(root).iterdir()), [])

    def test_invalid_language_or_flatpak_rejected(self):
        bad = self.run_cmd('bash', UI, '--lang', 'fr', '--demo')
        self.assertEqual(bad.returncode, 2)
        self.assertIn('de | en', bad.stderr)
        for lang, msg in [('de', 'Nur natives Lutris'), ('en', 'Only native Lutris')]:
            r = self.run_cmd('bash', UI, '--demo', '--lang', lang, '--mode', 'flatpak')
            self.assertNotEqual(r.returncode, 0)
            self.assertIn(msg, r.stderr)

    def test_webview_noninteractive_does_not_download(self):
        with tempfile.TemporaryDirectory() as root:
            for lang in ['de', 'en']:
                p = self.run_cmd('bash', WEBVIEW, '--lang', lang, env={'HOME': root})
                self.assertEqual(p.returncode, 0, p.stderr)
            self.assertFalse((Path(root) / 'Downloads').exists())

    def make_fake_curl(self, bindir, valid=True):
        bindir.mkdir(exist_ok=True)
        f = bindir / 'curl'
        prefix = 'MZ' if valid else '<html>'
        script = '''#!/usr/bin/env bash
out=''
while (( $# )); do
    if [[ "$1" == '--output' ]]; then out="$2"; shift 2; continue; fi
    shift
done
printf '%s' > "$out"
head -c 150000 /dev/zero >> "$out"
'''.replace("printf '%s' >", f"printf '{prefix}' >")
        f.write_text(script)
        f.chmod(0o755)

    def test_webview_en_download_and_existing_guard(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            self.make_fake_curl(root / 'bin')
            env = {'HOME': str(root), 'PATH': str(root / 'bin') + os.pathsep + os.environ['PATH']}
            args = ('bash', WEBVIEW, '--lang', 'en', '--yes')
            p = self.run_cmd(*args, env=env)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn('Download complete', p.stdout)
            self.assertIn('NOT executed', p.stdout)
            dest = root / 'Downloads/Jinteia-Proton/MicrosoftEdgeWebView2RuntimeInstallerX64.exe'
            self.assertEqual(dest.read_bytes()[:2], b'MZ')
            again = self.run_cmd(*args, env=env)
            self.assertEqual(again.returncode, 0)
            self.assertIn('will not be overwritten', again.stdout)

    def test_webview_de_download_and_guide(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            self.make_fake_curl(root / 'bin')
            p = self.run_cmd('bash', WEBVIEW, '--lang', 'de', '--yes',
                             env={'HOME': str(root), 'PATH': str(root / 'bin') + os.pathsep + os.environ['PATH']})
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn('Download abgeschlossen', p.stdout)
            self.assertIn('WebView2 in Lutris installieren', p.stdout)
            self.assertIn('NICHT ausgeführt', p.stdout)

    def test_webview_rejects_html_in_both_languages(self):
        for lang in ['de', 'en']:
            with tempfile.TemporaryDirectory() as root:
                root = Path(root)
                self.make_fake_curl(root / 'bin', valid=False)
                p = self.run_cmd('bash', WEBVIEW, '--lang', lang, '--yes',
                                 env={'HOME': str(root), 'PATH': str(root / 'bin') + os.pathsep + os.environ['PATH']})
                self.assertNotEqual(p.returncode, 0)
                dest = root / 'Downloads/Jinteia-Proton/MicrosoftEdgeWebView2RuntimeInstallerX64.exe'
                self.assertFalse(dest.exists())

    def test_direct_webview_language_dispatch_is_safe(self):
        with tempfile.TemporaryDirectory() as root:
            r = self.run_cmd('bash', UI, '--lang', 'en', '--webview2-only', env={'HOME': root})
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn('Skipped', r.stdout)
            self.assertFalse((Path(root) / 'Downloads').exists())


if __name__ == '__main__':
    unittest.main()