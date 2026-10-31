#!/usr/bin/env python3
"""Run with: python3 tests/test_heap_fix.py /path/to/original/ntdll.dll"""
import importlib.util
import mmap
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
ORIGINAL = Path(sys.argv.pop(1)).read_bytes()
spec = importlib.util.spec_from_file_location('heap_test', ROOT / 'heap-test.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class HeapFixTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='jinteia-heap-test-')
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.runner = self.home / 'data directory/lutris/runners/wine/Jinteia-Proton-0.2'
        self.dll = self.runner / module.DLL_RELATIVE
        self.dll.parent.mkdir(parents=True)
        self.dll.write_bytes(ORIGINAL)
        self.dll.chmod(0o755)
        self.backup = self.dll.with_name(self.dll.name + module.BACKUP_SUFFIX)
        self.process_pids = []
        self.env = dict(os.environ, HOME=str(self.home), XDG_DATA_HOME=str(self.home / 'data directory'))

    def run_action(self, action, explicit=True):
        argv = [sys.executable, str(ROOT / 'heap-test.py'), action]
        if os.geteuid() == 0:
            # CI cannot setuid and has protected root services in /proc.
            # Mock the no-sudo guard and enumerate only our real test processes.
            # Real maps, ownership, hashes and filesystem writes remain active.
            bootstrap = ('import os,runpy,sys; from pathlib import Path; os.geteuid=lambda: 1000; '
                         'saved_iterdir=Path.iterdir; '
                         'pids=[int(Path("/proc/self").resolve().name)]+' + repr(self.process_pids) + '; '
                         'Path.iterdir=lambda p: iter([Path("/proc")/str(i) for i in pids]) '
                         'if str(p)=="/proc" else saved_iterdir(p); '
                         'sys.argv=sys.argv[1:]; sys.path.insert(0,str(Path(sys.argv[0]).parent)); runpy.run_path(sys.argv[0],run_name="__main__")')
            argv = [sys.executable, '-c', bootstrap, str(ROOT / 'heap-test.py'), action]
        if explicit:
            argv += ['--runner', str(self.runner)]
        return subprocess.run(argv, text=True, capture_output=True, env=self.env)

    def test_apply_repeat_restore_and_checksum(self):
        self.assertEqual(self.run_action('check').returncode, 0)
        for _ in range(2):
            result = self.run_action('apply')
            self.assertEqual(result.returncode, 0, result.stderr)
        changed = self.dll.read_bytes()
        self.assertEqual(module.digest(changed), module.PATCHED_SHA256)
        self.assertEqual(self.backup.read_bytes(), ORIGINAL)
        self.assertEqual(self.dll.stat().st_mode & 0o777, 0o755)
        # Only reviewed patch regions and the PE checksum may differ.
        changes = {i for i, (a, b) in enumerate(zip(ORIGINAL, changed)) if a != b}
        allowed = {module.PATCH_OFFSET} | set(range(0xd8, 0xdc)) | set(range(0x190, 0x194)) | set(range(0x1bcea, 0x1bcf6)) | set(range(0x77aa0, 0x77abb))
        self.assertTrue(changes <= allowed)
        self.assertEqual(len(changed), len(ORIGINAL))
        for _ in range(2):
            result = self.run_action('restore')
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.dll.read_bytes(), ORIGINAL)

    def test_unknown_dll_is_not_modified(self):
        altered = bytearray(ORIGINAL)
        altered[-1] ^= 1
        self.dll.write_bytes(altered)
        self.assertNotEqual(self.run_action('apply').returncode, 0)
        self.assertEqual(self.dll.read_bytes(), altered)
        self.assertFalse(self.backup.exists())

    def test_foreign_backup_is_not_overwritten(self):
        self.backup.write_bytes(b'foreign backup')
        self.assertNotEqual(self.run_action('apply').returncode, 0)
        self.assertEqual(self.dll.read_bytes(), ORIGINAL)
        self.assertEqual(self.backup.read_bytes(), b'foreign backup')

    def test_broken_restore_backup_leaves_patched_dll(self):
        self.assertEqual(self.run_action('apply').returncode, 0)
        self.backup.write_bytes(b'broken')
        self.assertNotEqual(self.run_action('restore').returncode, 0)
        self.assertEqual(module.digest(self.dll.read_bytes()), module.PATCHED_SHA256)

    def test_symlink_dll_is_not_modified(self):
        original = self.home / 'real.dll'
        self.dll.rename(original)
        self.dll.symlink_to(original)
        self.assertNotEqual(self.run_action('apply').returncode, 0)
        self.assertEqual(original.read_bytes(), ORIGINAL)

    def test_auto_xdg_and_ambiguous_detection(self):
        result = self.run_action('apply', explicit=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        other = self.home / '.var/app/net.lutris.Lutris/data/lutris/runners/wine/Jinteia-Proton-0.2' / module.DLL_RELATIVE
        other.parent.mkdir(parents=True)
        other.write_bytes(ORIGINAL)
        self.assertNotEqual(self.run_action('apply', explicit=False).returncode, 0)
        self.assertEqual(other.read_bytes(), ORIGINAL)

    def test_loaded_dll_and_prefix_hardlink_are_detected(self):
        link = self.home / 'prefix-ntdll.dll'
        os.link(self.dll, link)
        program = ('import mmap,sys; from pathlib import Path; f=open(sys.argv[1],"rb"); '
                   'm=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ); '
                   'print(Path("/proc/self").resolve().name,flush=True); sys.stdin.read()')
        child = subprocess.Popen([sys.executable, '-c', program, str(link)],
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        try:
            self.process_pids.append(int(child.stdout.readline().strip()))
            result = self.run_action('apply')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('used by process', result.stderr)
            self.assertEqual(self.dll.read_bytes(), ORIGINAL)
        finally:
            child.communicate(timeout=5)

    def fake_proc_scan(self, entries):
        """entries maps PIDs to readable map text or PermissionError."""
        paths = []
        for pid in entries:
            entry = self.home / str(pid)
            entry.mkdir(exist_ok=True)
            paths.append(entry)
        real_read = Path.read_text

        def read_text(path, *args, **kwargs):
            if path.name == 'maps' and path.parent in paths:
                value = entries[int(path.parent.name)]
                if value is None:
                    raise PermissionError('protected process maps')
                return value
            return real_read(path, *args, **kwargs)

        return patch.object(Path, 'iterdir', return_value=paths), patch.object(Path, 'read_text', read_text)

    def own_maps_line(self):
        info = self.dll.stat()
        return (f'1000-2000 r--p 00000000 {os.major(info.st_dev):x}:{os.minor(info.st_dev):x} '
                f'{info.st_ino} {self.dll}\n')

    def test_inaccessible_processes_are_reported_without_blocking(self):
        listing, reading = self.fake_proc_scan({1056: None, 1058: None, 1164: None})
        with listing, reading:
            self.assertEqual(module.check_readable_mappings(self.dll), {'1056', '1058', '1164'})

    def test_scan_continues_after_inaccessible_process(self):
        listing, reading = self.fake_proc_scan({1164: None, 2000: self.own_maps_line()})
        with listing, reading, self.assertRaisesRegex(RuntimeError, 'used by process'):
            module.check_readable_mappings(self.dll)

    def test_unrelated_readable_mapping_is_not_a_blocker(self):
        listing, reading = self.fake_proc_scan({2000: '1000-2000 r--p 00000000 00:00 0 [heap]\n'})
        with listing, reading:
            self.assertEqual(module.check_readable_mappings(self.dll), set())

    def test_apply_and_restore_with_protected_processes(self):
        listing, reading = self.fake_proc_scan({1056: None, 1058: None, 1164: None})
        with listing, reading:
            module.change(self.dll, 'apply')
            self.assertEqual(module.digest(self.dll.read_bytes()), module.PATCHED_SHA256)
            self.assertEqual(self.backup.read_bytes(), ORIGINAL)
            module.change(self.dll, 'restore')
            self.assertEqual(self.dll.read_bytes(), ORIGINAL)

    def test_atomic_replacement_preserves_existing_mapping_and_hardlink(self):
        link = self.home / 'prefix-ntdll.dll'
        os.link(self.dll, link)
        original_inode = self.dll.stat().st_ino
        with self.dll.open('rb') as handle, mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ) as mapped:
            module.atomic_write(self.dll, module.patched_bytes(ORIGINAL), self.dll.stat().st_mode)
            self.assertEqual(mapped[:], ORIGINAL)
            self.assertEqual(handle.read(), ORIGINAL)
            self.assertEqual(link.read_bytes(), ORIGINAL)
            self.assertEqual(module.digest(self.dll.read_bytes()), module.PATCHED_SHA256)
            self.assertNotEqual(self.dll.stat().st_ino, original_inode)


    def discover_local(self, **extra):
        env = dict(self.env, XDG_CONFIG_HOME=str(self.home / 'config'),
                   XDG_STATE_HOME=str(self.home / 'state'), PROTONPATH='', WINE='')
        env.update(extra)
        with patch.dict(os.environ, env, clear=True):
            return module.discover()

    def put_runner(self, root, layout=None):
        dll = root / (layout or module.DLL_RELATIVE)
        dll.parent.mkdir(parents=True, exist_ok=True)
        dll.write_bytes(ORIGINAL)
        return dll

    def test_renamed_runner_and_duplicate_base_aliases(self):
        renamed = self.runner.with_name('Mein Runner mit Leerzeichen')
        self.runner.rename(renamed)
        alias = self.home / '.local/share/lutris/runners/wine'
        alias.parent.mkdir(parents=True)
        alias.symlink_to(renamed.parent, target_is_directory=True)
        found, warnings = self.discover_local()
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]['path'], str(renamed / module.DLL_RELATIVE))
        self.assertEqual(warnings, [])

    def test_lutris_custom_absolute_path_from_config(self):
        custom = self.home / 'extern/Proton Custom'
        self.put_runner(custom)
        config = self.home / 'config/lutris/games/game.yml'
        config.parent.mkdir(parents=True)
        config.write_text('wine:\n  version: "' + str(custom) + '"\ngame:\n  prefix: /ignored\n')
        found, _ = self.discover_local()
        self.assertEqual(len(found), 2)
        self.assertTrue(any(item['path'] == str(custom / module.DLL_RELATIVE) for item in found))

    def test_steam_external_library_discovery(self):
        library = self.home / 'external disk/SteamLibrary'
        dll = self.put_runner(library / 'compatibilitytools.d/Jinteia-Proton-0.2')
        vdf = self.home / 'data directory/Steam/steamapps/libraryfolders.vdf'
        vdf.parent.mkdir(parents=True)
        vdf.write_text('"libraryfolders" { "0" { "path" "' + str(library) + '" } }')
        found, _ = self.discover_local()
        self.assertTrue(any(item['path'] == str(dll) for item in found))

    def test_environment_wine_and_proton_roots(self):
        custom = self.home / 'custom/runner'
        dll = self.put_runner(custom)
        for env in ({'PROTONPATH': str(custom)}, {'WINE': str(custom / 'files/bin/wine')}):
            found, _ = self.discover_local(**env)
            self.assertTrue(any(item['path'] == str(dll) for item in found))

    def test_dist_and_lib_layouts(self):
        for rel in module.DLL_LAYOUTS[1:]:
            root = self.home / rel.parts[0]
            dll = self.put_runner(root, rel)
            self.assertEqual(module.locate(str(root)), dll)

    def test_missing_backup_of_installed_test_is_visible(self):
        self.dll.write_bytes(module.patched_bytes(ORIGINAL))
        info = module.inspect(self.dll)
        self.assertEqual((info['state'], info['backup']), ('patched', 'missing'))
        result = self.run_action('restore')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(module.digest(self.dll.read_bytes()), module.PATCHED_SHA256)

    def test_old_13_backup_is_recognized(self):
        self.dll.write_bytes(module.patched_bytes(ORIGINAL))
        self.backup.write_bytes(ORIGINAL)
        info = module.inspect(self.dll)
        self.assertEqual((info['state'], info['backup']), ('patched', 'valid'))
        self.assertEqual(self.run_action('restore').returncode, 0)
        self.assertEqual(self.dll.read_bytes(), ORIGINAL)

    def test_no_space_failure_preserves_original_and_backup(self):
        import errno
        with patch('heap_core.check_readable_mappings', return_value=set()), \
             patch('heap_core.atomic_write', side_effect=OSError(errno.ENOSPC, 'disk full')):
            with self.assertRaises(OSError):
                module.change(self.dll, 'apply', lambda message: None)
        self.assertEqual(self.dll.read_bytes(), ORIGINAL)
        self.assertEqual(self.backup.read_bytes(), ORIGINAL)

    def test_concurrent_installer_is_blocked(self):
        import fcntl
        lock_path = self.dll.with_name('.jinteia-heap-test1.lock')
        with lock_path.open('w') as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            result = self.run_action('apply')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Another installer', result.stderr)
        self.assertEqual(self.dll.read_bytes(), ORIGINAL)

    def test_backup_symlink_is_rejected(self):
        other = self.home / 'unrelated'
        other.write_bytes(ORIGINAL)
        self.backup.symlink_to(other)
        self.assertEqual(module.inspect(self.dll)['backup'], 'invalid')
        self.assertNotEqual(self.run_action('apply').returncode, 0)
        self.assertEqual(self.dll.read_bytes(), ORIGINAL)
        self.assertEqual(other.read_bytes(), ORIGINAL)

    def test_relative_xdg_is_ignored(self):
        default = self.home / '.local/share/lutris/runners/wine/Jinteia-Proton-0.2'
        dll = self.put_runner(default)
        found, _ = self.discover_local(XDG_DATA_HOME='relative/path')
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]['path'], str(dll))

    def test_diagnostic_redacts_home_and_never_changes_dll(self):
        with patch.dict(os.environ, self.env):
            data = module.diagnostic(self.dll, ['Fehler bei ' + str(self.dll)])
        self.assertNotIn(str(self.home), str(data))
        self.assertEqual(data['author'], 'DtyPnt71')
        self.assertEqual(self.dll.read_bytes(), ORIGINAL)

    def test_unknown_runner_is_visible_but_not_automatically_chosen(self):
        self.dll.write_bytes(b'unknown')
        found, _ = self.discover_local()
        self.assertEqual(found[0]['state'], 'unknown')
        with patch.dict(os.environ, self.env), self.assertRaises(RuntimeError):
            module.locate(None)


if __name__ == '__main__':
    unittest.main(verbosity=2)