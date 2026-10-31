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


    def test_temporary_install_simulation_uses_only_isolated_core(self):
        """Mock the existing real-binary test-heap backend; never touch actual Lutris."""
        for lang, answer, expected in [('de', 'j\n', 'Installationstest erfolgreich'),
                                       ('en', 'y\n', 'test passed')]:
            with self.subTest(lang=lang), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                (root / 'scripts').mkdir()
                (root / 'scripts/installer-ui.sh').write_bytes(UI.read_bytes())
                fake = root / 'install.sh'
                fake.write_text("""#!/usr/bin/env bash
[[ "$1" == "--test-heap" ]] || exit 99
echo '==> Downloading v0.2 release package'
echo '==> Verifying published SHA-256'
echo '==> Extracting verified runner payload'
echo '==> Extracting released runner into private temporary test area'
echo '==> Applying real Heap-Fix1+2 to the isolated test DLL'
echo '==> Heap Fix installed with expected patch and backup hashes; testing restore'
echo '==> ISOLATED HEAP TEST PASSED'
""")
                # An installed runner must not prevent this test or be modified.
                runner = root / 'home/.local/share/lutris/runners/wine/Jinteia-Proton-0.2'
                runner.mkdir(parents=True)
                (runner / 'proton').write_text('UNTOUCHED')
                env = {**os.environ, 'HOME': str(root / 'home'),
                       'XDG_STATE_HOME': str(root / 'home/state'),
                       'NO_COLOR': '1', 'TERM': 'xterm'}
                master, slave = pty.openpty()
                p = subprocess.Popen(
                    ['bash', str(root / 'scripts/installer-ui.sh'),
                     '--simulate-install', '--lang', lang],
                    env=env, stdin=slave, stdout=slave, stderr=slave,
                    start_new_session=True)
                os.close(slave)
                output = bytearray()
                try:
                    deadline = time.monotonic() + 12
                    sent = False
                    while time.monotonic() < deadline:
                        ready, _, _ = select.select([master], [], [], 0.2)
                        if ready:
                            try:
                                output.extend(os.read(master, 65536))
                            except OSError:
                                pass
                        if not sent and (b'[j/N]' in output or b'[y/N]' in output):
                            os.write(master, answer.encode())
                            sent = True
                        if p.poll() is not None:
                            break
                    self.assertIsNotNone(p.poll(), output.decode(errors='replace'))
                    self.assertEqual(p.returncode, 0, output.decode(errors='replace'))
                    self.assertIn(expected, output.decode(errors='replace'))
                    self.assertEqual((runner / 'proton').read_text(), 'UNTOUCHED')
                    logs = list((root / 'home/state/jinteia-proton').glob('simulation-*.log'))
                    self.assertEqual(len(logs), 1)
                    self.assertIn('ISOLATED HEAP TEST PASSED', logs[0].read_text())
                finally:
                    if p.poll() is None:
                        p.kill()
                    p.wait(timeout=5)
                    os.close(master)

    def test_temporary_install_simulation_reports_backend_failure(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'scripts').mkdir()
            (root / 'scripts/installer-ui.sh').write_bytes(UI.read_bytes())
            (root / 'install.sh').write_text(
                '#!/usr/bin/env bash\n[[ "$1" == "--test-heap" ]] || exit 98\n'
                'echo "TEST BACKEND ERROR" >&2\nexit 41\n')
            env = {**os.environ, 'HOME': str(root), 'XDG_STATE_HOME': str(root / 'state'),
                   'NO_COLOR': '1', 'TERM': 'xterm'}
            master, slave = pty.openpty()
            p = subprocess.Popen(
                ['bash', str(root / 'scripts/installer-ui.sh'),
                 '--simulate-install', '--lang', 'en'],
                env=env, stdin=slave, stdout=slave, stderr=slave,
                start_new_session=True)
            os.close(slave)
            output = bytearray()
            try:
                deadline = time.monotonic() + 12
                sent = False
                while time.monotonic() < deadline:
                    ready, _, _ = select.select([master], [], [], 0.2)
                    if ready:
                        try:
                            output.extend(os.read(master, 65536))
                        except OSError:
                            pass
                    if not sent and b'[y/N]' in output:
                        os.write(master, b'y\n')
                        sent = True
                    if p.poll() is not None:
                        break
                self.assertIsNotNone(p.poll())
                self.assertNotEqual(p.returncode, 0)
                decoded = output.decode(errors='replace')
                self.assertIn('Temporary installation test failed', decoded)
                self.assertIn('TEST BACKEND ERROR', decoded)
            finally:
                if p.poll() is None:
                    p.kill()
                p.wait(timeout=5)
                os.close(master)


if __name__ == '__main__':
    unittest.main()