#!/usr/bin/env python3
"""Offline regression tests. No real Lutris installation or user prefix is changed."""
import ast
import io
import os
from pathlib import Path
import runpy
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SETUP = (ROOT / 'setup-jinteia.sh').read_text()


def function(name, next_name):
    return SETUP[SETUP.index(name + '()'):SETUP.index('\n' + next_name + '()')]


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='jinteia-tests-')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.runners = self.base / 'runner directory'
        self.runner = self.runners / 'Jinteia-Proton-0.2'
        self.runner.mkdir(parents=True)
        (self.runner / 'proton').write_text('old runner')

    def archive(self, name='Jinteia-Proton-0.2/proton', data=b'new runner', symlink=False):
        archive = self.base / 'runner.tar.gz'
        with tarfile.open(archive, 'w:gz') as tf:
            entry = tarfile.TarInfo(name)
            if symlink:
                entry.type = tarfile.SYMTYPE
                entry.linkname = '/bin/sh'
                tf.addfile(entry)
            else:
                entry.size = len(data)
                tf.addfile(entry, io.BytesIO(data))
        return archive

    def install(self, archive, fail_activation=False):
        shell = 'set -euo pipefail\n'
        shell += 'RUNNER_NAME=Jinteia-Proton-0.2\n'
        shell += 'RUNNER_ARCHIVE=' + shlex.quote(str(archive)) + '\n'
        shell += 'runner_root_for_mode() { printf "%s" ' + shlex.quote(str(self.runners)) + '; }\n'
        shell += 'have() { command -v "$1" >/dev/null; }\n'
        shell += 'fatal() { echo "$*"; exit 1; }\n'
        shell += 'warn() { echo "$*"; }; fail() { echo "$*"; }; ok() { echo "$*"; }; info() { echo "$*"; }\n'
        if fail_activation:
            shell += 'mv() { if [[ "$2" == */extracted/* ]]; then return 1; fi; command mv "$@"; }\n'
        shell += function('install_runner', 'create_directories') + '\ninstall_runner\n'
        return subprocess.run(['bash', '-c', shell], capture_output=True, text=True)

    def assert_preserved(self, result):
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertEqual((self.runner / 'proton').read_text(), 'old runner')
        self.assertEqual(list(self.runners.glob('.jinteia-*')), [])

    def test_valid_replacement(self):
        result = self.install(self.archive())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.runner / 'proton').read_text(), 'new runner')
        self.assertTrue(os.access(self.runner / 'proton', os.X_OK))
        self.assertEqual(list(self.runners.glob('.jinteia-*')), [])

    def test_first_install(self):
        shutil.rmtree(self.runner)
        result = self.install(self.archive())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.runner / 'proton').read_text(), 'new runner')

    def test_dot_prefixed_archive(self):
        result = self.install(self.archive('./Jinteia-Proton-0.2/proton'))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_incomplete_archive_preserves_runner(self):
        self.assert_preserved(self.install(self.archive('Jinteia-Proton-0.2/README')))

    def test_empty_launcher_preserves_runner(self):
        self.assert_preserved(self.install(self.archive(data=b'')))

    def test_invalid_archive_preserves_runner(self):
        archive = self.base / 'invalid.tar.gz'
        archive.write_bytes(b'not an archive')
        self.assert_preserved(self.install(archive))

    def test_unexpected_folder_preserves_runner(self):
        self.assert_preserved(self.install(self.archive('other/proton')))

    def test_parent_path_preserves_runner(self):
        self.assert_preserved(self.install(self.archive('Jinteia-Proton-0.2/../../outside')))
        self.assertFalse((self.base / 'outside').exists())

    def test_symlink_launcher_preserves_runner(self):
        self.assert_preserved(self.install(self.archive(symlink=True)))

    def test_activation_failure_restores_runner(self):
        self.assert_preserved(self.install(self.archive(), fail_activation=True))

    def test_webview2_locations(self):
        for folder in [None, 'Program Files', 'Program Files (x86)']:
            with self.subTest(folder=folder):
                prefix = self.base / ('prefix-' + str(folder))
                if folder:
                    exe = prefix / 'drive_c' / folder / 'Microsoft/EdgeWebView/Application/1/msedgewebview2.exe'
                    exe.parent.mkdir(parents=True)
                    exe.touch()
                script = 'set -euo pipefail\nPREFIX_DIR=' + shlex.quote(str(prefix)) + '\n'
                script += function('webview2_installed', 'final_dialog') + '\nwebview2_installed'
                result = subprocess.run(['bash', '-c', script], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0 if folder else 1)

    def test_lutris_runner_path_old_and_new(self):
        for modern in [False, True]:
            with self.subTest(modern=modern):
                modules = self.base / ('modern' if modern else 'old')
                package = modules / 'lutris'
                package.mkdir(parents=True)
                (package / '__init__.py').touch()
                expected = str(self.runners if modern else self.base / 'custom-runners/wine')
                (package / 'settings.py').write_text(
                    'RUNNER_DIR=' + repr(str(self.base / 'custom-runners')) + '\n' +
                    ('WINE_DIR=' + repr(expected) + '\n' if modern else ''))
                env = dict(os.environ, PYTHONPATH=str(modules))
                script = 'set -euo pipefail\nDETECTED_MODE=native\nhave() { command -v "$1" >/dev/null; }\n'
                script += function('runner_root_for_mode', 'vulkan_64_present') + '\nrunner_root_for_mode'
                result = subprocess.run(['bash', '-c', script], env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, expected)

    def test_entry_helper_old_and_new_lutris_api(self):
        for modern in [False, True]:
            for existing in [False, True]:
                with self.subTest(modern=modern, existing=existing):
                    names = ['lutris', 'lutris.settings', 'lutris.config', 'lutris.database',
                             'lutris.database.schema', 'lutris.database.games', 'lutris.util', 'lutris.util.strings']
                    modules = {name: types.ModuleType(name) for name in names}
                    settings = modules['lutris.settings']
                    settings.DB_PATH = str(self.base / 'db/pga.db')
                    settings.GAME_CONFIG_DIR = str(self.base / 'config/games')
                    settings.RUNNERS_CONFIG_DIR = str(self.base / 'config/runners')
                    settings.RUNNER_DIR = str(self.runners.parent)
                    # Old Lutris stores wine runners below RUNNER_DIR/wine.
                    old_runner = Path(settings.RUNNER_DIR) / 'wine/Jinteia-Proton-0.2'
                    old_runner.mkdir(parents=True, exist_ok=True)
                    (old_runner / 'proton').write_text('runner')
                    if modern:
                        settings.WINE_DIR = str(self.runners)
                    modules['lutris.database.schema'].syncdb = lambda: None
                    calls = []
                    cfg = types.SimpleNamespace(raw_game_config={'exe': '/existing/patcher.exe', 'working_dir': '/existing'},
                                                raw_runner_config={}, save=lambda: calls.append('saved'))
                    modules['lutris.config'].LutrisConfig = lambda **kw: cfg
                    modules['lutris.config'].write_game_config = lambda slug, config: calls.append(config) or 'config-id'
                    db = modules['lutris.database.games']
                    db.add_game = lambda **kw: calls.append(kw)
                    db.update_existing = lambda **kw: calls.append(kw)
                    db.get_game_by_field = lambda *a, **kw: {'id': 1, 'configpath': 'existing-id'} if existing else None
                    db.get_games_by_slug = lambda slug: []
                    modules['lutris.util.strings'].slugify = lambda value: value.lower().replace(' ', '-')
                    argv = ['create_lutris_entry.py', 'Jinteia Patcher 0.2', 'Jinteia-Proton-0.2', '/test/prefix', '/test/game']
                    with patch.dict(sys.modules, modules), patch.object(sys, 'argv', argv):
                        runpy.run_path(str(ROOT / 'tools/create_lutris_entry.py'), run_name='__main__')
                    self.assertTrue(calls)
                    if existing:
                        self.assertEqual(cfg.raw_game_config['exe'], '/existing/patcher.exe')
                        self.assertEqual(cfg.raw_game_config['working_dir'], '/existing')
                    else:
                        self.assertEqual(calls[0]['wine']['version'], 'Jinteia-Proton-0.2')

    def test_onefile_payload_and_portable_checksum(self):
        archive = self.archive()
        output = self.base / 'output with spaces/installer.run'
        output.parent.mkdir()
        result = subprocess.run(['bash', str(ROOT / 'make-onefile-installer.sh'), str(archive), str(output)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = output.read_bytes()
        stub, payload = data.split(b'\n__JINTEIA_PAYLOAD_BELOW__\n', 1)
        with tarfile.open(fileobj=io.BytesIO(payload), mode='r:gz') as tf:
            self.assertEqual(tf.extractfile('payload/setup-jinteia.sh').read(), (ROOT / 'setup-jinteia.sh').read_bytes())
            self.assertEqual(tf.extractfile('payload/tools/create_lutris_entry.py').read(), (ROOT / 'tools/create_lutris_entry.py').read_bytes())
            self.assertEqual(tf.extractfile('payload/Jinteia-Proton-0.2.tar.gz').read(), archive.read_bytes())
        destination = self.base / 'download'
        destination.mkdir()
        shutil.move(str(output), destination / output.name)
        shutil.move(str(output) + '.sha256', destination / (output.name + '.sha256'))
        result = subprocess.run(['sha256sum', '-c', output.name + '.sha256'], cwd=destination, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_build_checksum_portability(self):
        output = self.base / 'build output'
        output.mkdir()
        filename = 'Jinteia-Proton-0.2.tar.gz'
        (output / filename).write_bytes(b'release contents')
        source = (ROOT / 'build-and-install.sh').read_text()
        command = next(line for line in source.splitlines() if line.startswith('(cd "$OUTPUT_DIR" && sha256sum'))
        script = 'set -euo pipefail\nOUTPUT_DIR=' + shlex.quote(str(output)) + '\nBUILD_NAME=Jinteia-Proton-0.2\n' + command
        subprocess.run(['bash', '-c', script], check=True)
        destination = self.base / 'download'
        shutil.move(str(output), destination)
        result = subprocess.run(['sha256sum', '-c', filename + '.sha256'], cwd=destination, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_syntax(self):
        for script in ROOT.glob('*.sh'):
            subprocess.run(['bash', '-n', str(script)], check=True)
        for script in (ROOT / 'tools').glob('*.py'):
            ast.parse(script.read_text())


if __name__ == '__main__':
    unittest.main(verbosity=2)