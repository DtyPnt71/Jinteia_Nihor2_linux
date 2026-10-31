"""Isolated fixture tests of the bootstrap coordinator, not of real game binaries."""
import hashlib
import io
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent


def archive_bytes(files):
    out = io.BytesIO()
    with tarfile.open(fileobj=out, mode='w:gz') as t:
        for name, data in files.items():
            b = data.encode() if isinstance(data, str) else data
            info = tarfile.TarInfo(name)
            info.size = len(b)
            t.addfile(info, io.BytesIO(b))
    return out.getvalue()


class BootstrapIntegration(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.project = self.base / 'project'
        (self.project / 'proton/tools').mkdir(parents=True)
        (self.project / 'heap').mkdir(parents=True)
        self.home = self.base / 'home'
        self.home.mkdir()
        self.bin = self.base / 'bin'
        self.bin.mkdir()

        # The .run file has executable commands in its header. They must never run.
        self.fake_dll = b'Fake DLL for offline verification only\n'
        tar = archive_bytes({'payload/Jinteia-Proton-0.2.tar.gz': archive_bytes({
            'Jinteia-Proton-0.2/proton': '#!/usr/bin/env bash\nexit 0\n',
            'Jinteia-Proton-0.2/files/lib/wine/x86_64-windows/ntdll.dll': self.fake_dll,
        })})
        self.fake_run = self.base / 'installer.run'
        self.fake_run.write_bytes(b'#!/usr/bin/env bash\ntouch "$HOME/OPAQUE_WRAPPER_RAN"\n__JINTEIA_PAYLOAD_BELOW__\n' + tar)
        digest = hashlib.sha256(self.fake_run.read_bytes()).hexdigest()
        self.fake_patched_dll = b'Patched fake DLL for simulated test only\n'
        install = (ROOT / 'install.sh').read_text().replace(
            'e2d73e4c36266c4c07323bd73a318f9e52e5a805f4774ae1cab8c994df9b59e7', digest).replace(
            'ad0243384afa5fad82331dacfd7e45383b2a0c955fb8f99dd12e1cfd7d558438', hashlib.sha256(self.fake_dll).hexdigest()).replace(
            '7b925e64a014111f80a1be831866f4d38f34c51abc35640ea87a6926716b021f', hashlib.sha256(self.fake_patched_dll).hexdigest())
        (self.project / 'install.sh').write_text(install)
        (self.project / 'proton/tools/create_lutris_entry.py').write_text('')
        (self.project / 'heap/heap_core.py').write_text('')
        (self.project / 'heap/binary_patch.py').write_text('')
        (self.project / 'proton/setup-jinteia.sh').write_text('''#!/usr/bin/env bash
set -euo pipefail
[[ "$1" == '--runner-archive' ]] || exit 15
archive="$2"
[[ -s "$archive" ]] || exit 16
root="$XDG_DATA_HOME/lutris/runners/wine/Jinteia-Proton-0.2"
mkdir -p "$root" "$XDG_CACHE_HOME/jinteia-proton"
tar -xzf "$archive" -C "$(dirname "$root")"
printf 'Installed Proton runner: %s\\n' "$root" > "$XDG_CACHE_HOME/jinteia-proton/setup-v0.2.log"
''')
        (self.project / 'heap/heap-test.py').write_text('''#!/usr/bin/env python3
import sys
from pathlib import Path
assert sys.argv[1] in ('apply', 'restore')
assert sys.argv[2] == '--runner'
r = Path(sys.argv[3])
assert (r / 'proton').exists()
dll = r / 'files/lib/wine/x86_64-windows/ntdll.dll'
backup = dll.with_name('ntdll.dll.jinteia-heap-test1.original')
if sys.argv[1] == 'apply':
    backup.write_bytes(dll.read_bytes())
    dll.write_bytes(b'Patched fake DLL for simulated test only\\n')
    (r / 'HEAP_SIMULATED').write_text('fake fixture, not real ntdll')
else:
    dll.write_bytes(backup.read_bytes())
''')
        # Mock curl; download from the local test fixture only.
        (self.bin / 'curl').write_text('''#!/usr/bin/env bash
set -euo pipefail
while [[ $# -gt 0 ]]; do
  if [[ "$1" == '--output' ]]; then cp "$FIXTURE_RUN" "$2"; exit 0; fi
  shift
done
exit 17
''')
        (self.bin / 'curl').chmod(0o755)
        self.env = dict(os.environ,
            HOME=str(self.home), XDG_DATA_HOME=str(self.home / '.local/share'),
            XDG_CACHE_HOME=str(self.home / '.cache'),
            PATH=str(self.bin) + os.pathsep + os.environ['PATH'], FIXTURE_RUN=str(self.fake_run))

    def call(self, *args, confirm='y\n'):
        return subprocess.run(['bash', str(self.project / 'install.sh'), *args],
                              input=confirm, text=True, capture_output=True, env=self.env)

    def test_download_extract_and_heap_order(self):
        p = self.call()
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        runner = self.home / '.local/share/lutris/runners/wine/Jinteia-Proton-0.2'
        self.assertTrue((runner / 'proton').exists())
        self.assertTrue((runner / 'HEAP_SIMULATED').exists())
        self.assertFalse((self.home / 'OPAQUE_WRAPPER_RAN').exists())
        # An existing runner must not be overwritten on a second attempt.
        p2 = self.call()
        self.assertNotEqual(p2.returncode, 0)
        self.assertIn('Existing Jinteia-Proton-0.2 detected', p2.stderr)
        self.assertTrue((runner / 'HEAP_SIMULATED').exists())

    def test_verify_release_only_reads_archive_and_dll(self):
        p = self.call('--verify-release')
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertIn('RELEASE VERIFIED', p.stdout)
        self.assertFalse((self.home / 'OPAQUE_WRAPPER_RAN').exists())
        self.assertFalse((self.home / '.local/share/lutris/runners/wine/Jinteia-Proton-0.2').exists())
        self.assertFalse((self.home / '.cache').exists())

    def test_isolated_heap_apply_and_restore_without_touching_lutris(self):
        p = self.call('--test-heap')
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertIn('ISOLATED HEAP TEST PASSED', p.stdout)
        self.assertFalse((self.home / 'OPAQUE_WRAPPER_RAN').exists())
        self.assertFalse((self.home / '.local').exists())
        self.assertFalse((self.home / '.cache').exists())

    def test_invalid_checksum_stops_before_extract(self):
        self.fake_run.write_bytes(self.fake_run.read_bytes() + b'x')
        p = self.call()
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('Checksum mismatch', p.stderr)
        self.assertFalse((self.home / '.local/share/lutris/runners/wine/Jinteia-Proton-0.2').exists())
        self.assertFalse((self.home / 'OPAQUE_WRAPPER_RAN').exists())

    def test_cancel_stops_before_download(self):
        p = self.call(confirm='n\n')
        self.assertEqual(p.returncode, 0)
        self.assertIn('Cancelled', p.stdout)
        self.assertFalse((self.home / '.cache').exists())

if __name__ == '__main__':
    unittest.main()