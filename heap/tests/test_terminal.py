"""Terminal flow regression tests. Pass the verified original ntdll.dll."""
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
ORIGINAL = Path(sys.argv.pop(1)).read_bytes()
spec = importlib.util.spec_from_file_location('heap_terminal', ROOT / 'heap-test.py')
ui = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ui)


class TerminalTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = Path(tmp.name)
        self.dll = self.home / 'Jinteia-Proton-0.2' / ui.DLL_RELATIVE
        self.dll.parent.mkdir(parents=True)
        self.dll.write_bytes(ORIGINAL)
        self.output = io.StringIO()
        self.addCleanup(patch.stopall)
        patch.dict(os.environ, {'HOME': str(self.home), 'XDG_STATE_HOME': str(self.home / 'state')}).start()
        patch('os.geteuid', return_value=1000).start()
        patch.object(ui, 'COLOR_MODE', 'always').start()

    def test_unique_compatible_runner_skips_selection(self):
        with patch.object(ui, 'discover', return_value=([ui.inspect(self.dll), {'path': '/other', 'state': 'unknown'}], [])), \
             patch('builtins.input', side_effect=AssertionError('Selection should not be requested')), \
             contextlib.redirect_stdout(self.output):
            self.assertEqual(ui.choose(), self.dll)
        self.assertIn('automatically', self.output.getvalue())

    def test_multiple_compatible_runners_require_a_choice(self):
        other = dict(ui.inspect(self.dll), path='/second/ntdll.dll')
        with patch.object(ui, 'discover', return_value=([ui.inspect(self.dll), other], [])), \
             patch('builtins.input', return_value='2'), contextlib.redirect_stdout(self.output):
            self.assertEqual(ui.choose(), Path('/second/ntdll.dll'))

    def test_missing_match_explains_dependency(self):
        with patch.object(ui, 'discover', return_value=([{'path': '/unknown', 'state': 'unknown'}], [])), \
             patch('builtins.input', return_value='q'), contextlib.redirect_stdout(self.output):
            self.assertIsNone(ui.choose())
        self.assertIn('requires the matching', self.output.getvalue())
        self.assertIn('Jinteia-Proton fix first', self.output.getvalue())

    def test_install_restore_flow_updates_menu_and_colors(self):
        with patch('heap_core.check_readable_mappings', return_value=set()), \
             patch('builtins.input', side_effect=['1', 'yes', '', '2', 'yes', '', 'q']), \
             contextlib.redirect_stdout(self.output):
            self.assertEqual(ui.terminal(str(self.dll)), 0)
        self.assertEqual(self.dll.read_bytes(), ORIGINAL)
        output = self.output.getvalue()
        self.assertIn('\033[1;32m[INSTALLED]', output)
        self.assertIn('\033[90m1  Heap Fix installed', output)
        self.assertIn('\033[1;33m2  RESTORE ORIGINAL\033[0m', output)
        self.assertIn('[SUCCESS] ORIGINAL RESTORED', output)
        self.assertIn('nothing to install', output)

    def test_unsupported_menu_cannot_call_patch(self):
        self.dll.write_bytes(b'unknown')
        with patch.object(ui, 'change') as change, \
             patch('builtins.input', side_effect=['1', '', 'q']), contextlib.redirect_stdout(self.output):
            ui.terminal(str(self.dll))
        change.assert_not_called()
        self.assertIn('UNSUPPORTED BUILD', self.output.getvalue())
        self.assertIn('[unavailable]', self.output.getvalue())
        self.assertEqual(self.dll.read_bytes(), b'unknown')

    def test_missing_backup_disables_restore_even_when_installed(self):
        self.dll.write_bytes(ui.patched_bytes(ORIGINAL))
        info = ui.inspect(self.dll)
        self.assertEqual(ui.permissions(info), (False, False))
        with contextlib.redirect_stdout(self.output):
            ui.status(self.dll)
        self.assertIn('valid original backup is missing', self.output.getvalue())

    def test_no_color_keeps_textual_states(self):
        with patch.object(ui, 'COLOR_MODE', 'never'), contextlib.redirect_stdout(self.output):
            ui.status(self.dll)
            ui.menu(ui.inspect(self.dll))
        self.assertNotIn('\033', self.output.getvalue())
        self.assertIn('[READY TO INSTALL]', self.output.getvalue())

    def test_manual_invalid_folder_returns_without_crashing(self):
        with patch('builtins.input', return_value=str(self.home / 'missing')), contextlib.redirect_stdout(self.output):
            self.assertIsNone(ui.manual_path())
        self.assertIn('runner folder', self.output.getvalue())

    def test_upgrade_and_revert_menu_flow(self):
        self.dll.write_bytes(ui.legacy_bytes(ORIGINAL))
        with patch('heap_core.check_readable_mappings', return_value=set()), \
             patch('builtins.input', side_effect=['1', 'yes', '', '6', 'yes', '', 'q']), \
             contextlib.redirect_stdout(self.output):
            self.assertEqual(ui.terminal(str(self.dll)), 0)
        self.assertEqual(self.dll.read_bytes(), ui.legacy_bytes(ORIGINAL))
        text = self.output.getvalue()
        self.assertIn('HEAP-TEST1 / UPDATE AVAILABLE', text)
        self.assertIn('Upgrade to Heap-Test2', text)
        self.assertIn('[SUCCESS] HEAP-TEST1 RESTORED', text)

    def test_revert_cannot_install_first_fix_on_original(self):
        with patch.object(ui, 'change') as change, \
             patch('builtins.input', side_effect=['6', '', 'q']), \
             contextlib.redirect_stdout(self.output):
            ui.terminal(str(self.dll))
        change.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)