#!/usr/bin/env python3
"""Jinteia Heap Fix — DtyPnt71. English terminal setup."""
import argparse
import os
import shlex
import shutil
import sys
import textwrap
from pathlib import Path

if sys.version_info < (3, 8):
    sys.exit('Jinteia Heap Fix requires Python 3.8 or newer.')
if sys.platform != 'linux':
    sys.exit('Jinteia Heap Fix requires Linux.')

from heap_core import *

COLOR_MODE = 'auto'
COLORS = {'green': '1;32', 'cyan': '1;36', 'blue': '1;34', 'yellow': '1;33',
          'red': '1;31', 'muted': '90', 'bold': '1', 'white': '37'}
STATE_LABELS = {'original': 'READY TO INSTALL', 'patched': 'INSTALLED', 'legacy': 'HEAP-TEST1 / UPDATE AVAILABLE',
                'unknown': 'UNSUPPORTED BUILD', 'error': 'FILE ERROR'}


def colored():
    if COLOR_MODE != 'auto':
        return COLOR_MODE == 'always'
    return sys.stdout.isatty() and os.environ.get('TERM', '') != 'dumb' and 'NO_COLOR' not in os.environ


def safe_text(value):
    # Filenames or external errors must not inject terminal control sequences.
    return ''.join(c if c == '\n' or ord(c) >= 32 and ord(c) != 127 else '?' for c in str(value))


def paint(text, color):
    text = safe_text(text)
    return '\033[' + COLORS[color] + 'm' + text + '\033[0m' if colored() else text


def line(text='', color=None):
    text = safe_text(text)
    print('  ' + (paint(text, color) if color else text), flush=True)


def paragraph(text, color=None):
    width = max(40, min(88, shutil.get_terminal_size((88, 24)).columns - 4))
    for part in textwrap.wrap(safe_text(text), width=width, break_long_words=True, break_on_hyphens=False):
        line(part, color)


def section(title):
    line()
    line('## ' + title, 'blue')
    line('---------------------------------------------------------------------------------', 'muted')


def banner(clear=False):
    if clear and sys.stdout.isatty() and colored():
        print('\033[2J\033[H', end='')
    line()
    line('# JINTEIA HEAP FIX', 'bold')
    line('created by DtyPnt71 / Burarion')
    line('Setup version: ' + INSTALLER_VERSION, 'green')
    line()
    paragraph('REQUIRES THE JINTEIA-PROTON FIX (matching Jinteia-Proton-0.2 build).', 'yellow')
    paragraph('This is an add-on, not a standalone Proton fix. Standard Wine, stock GE-Proton and other DLL builds are not supported.', 'muted')
    line()
    line('---------------------------------------------------------------------------------', 'red')
    line('!!! [ IMPORTANT ] !!!', 'red')
    line()
    paragraph('THIS FIX DOES NOT MODIFY ANY JINTEIA GAME FILES.', 'yellow')
    paragraph('THIS FIX ONLY MODIFIES THE PROTON RUNNER’S MEMORY MANAGEMENT.', 'yellow')
    line('---------------------------------------------------------------------------------', 'red')


def permissions(info):
    if os.geteuid() == 0:
        return False, False
    install = info['state'] in ('original', 'legacy') and info['backup'] in ('missing', 'valid')
    restore = info['state'] in ('legacy', 'patched') and info['backup'] == 'valid'
    return install, restore


def status(path, detailed=False):
    info = inspect(path)
    color = {'original': 'cyan', 'legacy': 'yellow', 'patched': 'green', 'unknown': 'red', 'error': 'red'}[info['state']]
    section('Installation status')
    line('[' + STATE_LABELS[info['state']] + ']', color)
    paragraph('Runner DLL: ' + display_path(path), 'muted')
    backup = {'valid': 'Verified original backup.', 'missing': 'No original backup saved yet.',
              'invalid': 'INVALID — restore is blocked.', 'unreadable': 'UNREADABLE — restore is blocked.'}[info['backup']]
    line('Backup: ' + backup, 'green' if info['backup'] == 'valid' else 'yellow' if info['backup'] in ('invalid', 'unreadable') else 'muted')
    if info['state'] == 'patched':
        line('Heap-Fix2 + Heap-Fix1 are verified on disk. Restart the game to load them.', 'green')
        if info['backup'] != 'valid':
            paragraph('WARNING: The fix is installed, but a valid original backup is missing. Reinstall the matching original runner to undo it.', 'yellow')
    elif info['state'] == 'legacy':
        paragraph('Heap-Fix1 is installed. Choose [1] to add the group-allocation fix.', 'yellow')
    elif info['state'] == 'unknown':
        paragraph('Install the matching Jinteia-Proton fix first, then select that RUNNER FOLDER. Choosing a DLL manually does not make an unsupported build compatible.', 'yellow')
    if info['error']:
        paragraph(info['error'], 'red')
    if os.geteuid() == 0:
        paragraph('READ-ONLY: Run as your normal user without sudo to install or restore.', 'yellow')
    if detailed and info['sha256']:
        paragraph('SHA256: ' + info['sha256'], 'muted')
    return info


def menu(info):
    install, restore = permissions(info)
    section('Actions')
    if info['state'] == 'patched':
        line('1  Heap Fix installed                 [nothing to install]', 'muted')
    else:
        line(('1  Upgrade to Heap-Test2' if info['state'] == 'legacy' else '1  Install heap fix') + ('' if install else '                  [unavailable]'), 'green' if install else 'muted')
    line('2  RESTORE ORIGINAL' + ('' if restore else '                  [unavailable]'), 'yellow' if restore else 'muted')
    line('3  Check status', 'cyan')
    line('4  Save diagnostics', 'cyan')
    line('5  Choose another runner', 'cyan')
    line('6  REVERT TO HEAP-TEST1' + ('' if info['state'] == 'patched' and restore else '               [unavailable]'), 'yellow' if info['state'] == 'patched' and restore else 'muted')
    line('Q  Quit', 'white')
    line()
    if restore:
        paragraph('UNDO AT ANY TIME: close the game and patcher, then choose [2] RESTORE ORIGINAL.', 'yellow')
    elif install:
        paragraph('UNDO: after installation, use [2] RESTORE ORIGINAL. A verified backup is created first.', 'yellow')
    else:
        paragraph('Only a matching DLL with a verified original backup can be restored.', 'muted')
    return install, restore


def manual_path():
    line()
    paragraph('Enter the Jinteia-Proton RUNNER FOLDER. You do not need to find a DLL. Do not select the game folder or Wine prefix.', 'cyan')
    value = input('  Runner folder (Enter to go back): ').strip().strip('"').strip("'")
    if not value:
        return None
    try:
        return locate(value)
    except (RuntimeError, OSError) as error:
        paragraph(friendly_error(error), 'red')
        return None


def choose(explicit=None, auto=True):
    if explicit:
        return locate(explicit)
    while True:
        section('Runner detection')
        line('Looking for compatible Jinteia-Proton installations...', 'muted')
        items, warnings = discover()
        for warning in warnings:
            paragraph('Warning: ' + warning, 'yellow')
        matches = [item for item in items if item['state'] in ('original', 'legacy', 'patched')]
        skipped = len(items) - len(matches)
        if auto and len(matches) == 1:
            line('[OK] Compatible runner selected automatically.', 'green')
            return Path(matches[0]['path'])
        if not matches:
            paragraph('No compatible Jinteia-Proton runner was found. This add-on requires the matching Jinteia-Proton fix first.', 'yellow')
            paragraph('If it is installed in a custom location, use [P] and select its RUNNER FOLDER.', 'muted')
        for index, item in enumerate(matches, 1):
            line('{}  [{}]'.format(index, STATE_LABELS[item['state']]), 'green' if item['state'] == 'patched' else 'cyan')
            paragraph('   ' + display_path(item['path']), 'muted')
        if skipped:
            paragraph('{} incompatible or unreadable installation(s) excluded from automatic selection.'.format(skipped), 'muted')
        line('P  Enter a runner folder', 'cyan')
        line('R  Scan again', 'cyan')
        line('Q  Cancel', 'white')
        while True:
            value = input('\n  Select: ').strip().lower()
            if value == 'q':
                return None
            if value == 'r':
                break
            if value == 'p':
                path = manual_path()
                if path:
                    return path
                continue
            if value.isdigit() and 1 <= int(value) <= len(matches):
                return Path(matches[int(value) - 1]['path'])
            line('Choose a listed number, P, R or Q.', 'yellow')


def run_action(action, path):
    events = []
    def emit(message):
        text = display_path(message)
        events.append(text)
        paragraph(text, 'yellow' if text.startswith('Warning:') else 'muted')
    result = 0
    try:
        if action in ('apply', 'restore', 'revert'):
            section({'apply': 'Install Heap-Fix2', 'restore': 'Restore original DLL', 'revert': 'Revert to Heap-Fix1'}[action])
            if os.geteuid() == 0:
                fail('Run as your normal user without sudo.')
            emit('The game and patcher must remain closed throughout this operation.')
            change(path, action, emit)
            if action == 'apply':
                line('[SUCCESS] HEAP FIX INSTALLED', 'green')
            elif action == 'revert':
                line('[SUCCESS] HEAP-FIX1 RESTORED — SECOND FIX REMOVED', 'green')
            else:
                line('[SUCCESS] ORIGINAL RESTORED — HEAP FIX REMOVED', 'green')
        elif action == 'diagnose':
            events.append('Diagnostics requested; no DLL changes made.')
        else:
            info = status(path, detailed=True)
            return 0 if info['state'] in ('original', 'legacy', 'patched') else 1
    except (RuntimeError, OSError) as error:
        message = 'ERROR: ' + friendly_error(error)
        events.append(message)
        # Keep a readable error on stderr for direct commands and logs.
        print('  ' + paint(message, 'red'), file=sys.stderr, flush=True)
        paragraph('Check the current file status. Any existing original backup is retained.', 'yellow')
        result = 1
    finally:
        if action != 'check':
            try:
                log = save_diagnostic(path, events)
                paragraph('Diagnostics saved: ' + display_path(log), 'muted')
            except OSError as error:
                paragraph('Could not save diagnostics: ' + friendly_error(error), 'yellow')
    return result


def terminal(explicit=None):
    banner()
    path = choose(explicit)
    notice = ''
    while path:
        banner(clear=True)
        if notice:
            line(notice, 'green')
        section('What this fix does')
        paragraph('HEAP-FIX1.', 'yellow')
        paragraph('Enables Wine\'s existing Low Fragmentation Heap earlier for additional small-block size classes.', 'cyan')
        paragraph('HEAP-FIX2.', 'yellow')
        paragraph('Rounds internal 1,520-byte LFH groups to 1,536 bytes to avoid searching undersized free blocks. Adds 16 bytes per affected group.', 'cyan')
        paragraph('Experimental performance fix.', 'muted')
        info = status(path)
        install, restore = menu(info)
        choice = input('\n  Select [1-6 / Q]: ').strip().lower()
        notice = ''
        if choice == 'q':
            line('Done. Thanks for using DtyPnt71\'s Jinteia Heap Fix.', 'muted')
            return 0
        if choice == '5':
            other = choose(auto=False)
            path = other or path
            continue
        action = {'1': 'apply', '2': 'restore', '3': 'check', '4': 'diagnose', '6': 'revert'}.get(choice)
        if not action:
            line('Choose an available action.', 'yellow')
        elif action in ('apply', 'restore', 'revert'):
            if not (install if action == 'apply' else restore and (action != 'revert' or info['state'] == 'patched')):
                paragraph('This action is unavailable for the current DLL / backup state. Review the status above.', 'yellow')
            else:
                paragraph('Close the game and patcher before continuing. Keep them closed until the operation finishes.', 'yellow')
                verb = {'apply': 'Install Heap-Fix2', 'restore': 'Restore the original DLL (remove both fixes)', 'revert': 'Remove only Heap-Fix2 and keep Heap-Fix1'}[action]
                answer = input('  ' + verb + '? [y/N]: ').strip().lower()
                if answer in ('y', 'yes'):
                    code = run_action(action, path)
                    if code == 0:
                        notice = '[SUCCESS] ' + {'apply': 'Heap-Fix2 installed.', 'restore': 'Original restored. Both fixes removed.', 'revert': 'Heap-Fix1 restored. Second fix removed.'}[action]
        else:
            run_action(action, path)
        input('\n  Press Enter to return to the menu...')
    return 0


def main():
    global COLOR_MODE
    parser = argparse.ArgumentParser(description='Jinteia Heap Fix — DtyPnt71. Requires the matching Jinteia-Proton fix.')
    parser.add_argument('action', choices=('check', 'apply', 'restore', 'revert', 'diagnose'), nargs='?')
    parser.add_argument('--runner', help='Jinteia-Proton runner folder (or exact supported 64-bit ntdll.dll)')
    parser.add_argument('--cli', action='store_true', help='Open the interactive terminal setup (default)')
    parser.add_argument('--color', choices=('auto', 'always', 'never'), default='auto', help='Terminal colors (default: auto)')
    args = parser.parse_args()
    COLOR_MODE = args.color
    if args.action:
        banner()
        return run_action(args.action, locate(args.runner))
    if not sys.stdin.isatty():
        print('Open a terminal in the extracted folder and run: bash START.sh', file=sys.stderr)
        return 1
    return terminal(args.runner)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (RuntimeError, OSError) as error:
        print('  ' + paint('ERROR: ' + friendly_error(error), 'red'), file=sys.stderr)
        sys.exit(1)
    except (KeyboardInterrupt, EOFError):
        line('Exited. If an operation was interrupted, check the DLL status before continuing.', 'yellow')
        sys.exit(130)