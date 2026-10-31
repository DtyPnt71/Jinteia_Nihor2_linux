#!/usr/bin/env python3
"""Jinteia Heap Fix — DtyPnt71. Version-bound, reversible LFH adjustment."""
import argparse
import fcntl
import hashlib
import os
from pathlib import Path
import stat
import struct
import sys
import tempfile
import json
import platform
import re
from datetime import datetime, timezone

from binary_patch import (ORIGINAL_SHA256, LEGACY_SHA256, PATCHED_SHA256, PATCH_OFFSET,
                          digest, checksum, patched_bytes, original_bytes, legacy_bytes)
BACKUP_SUFFIX = '.jinteia-heap-test1.original'
DLL_RELATIVE = Path('files/lib/wine/x86_64-windows/ntdll.dll')
INSTALLER_VERSION = '3.0.0'
AUTHOR = 'DtyPnt71'
DLL_LAYOUTS = (DLL_RELATIVE, Path('dist/lib/wine/x86_64-windows/ntdll.dll'),
               Path('lib/wine/x86_64-windows/ntdll.dll'))


def xdg(name, fallback):
    value = os.environ.get(name, '')
    return Path(value) if value and Path(value).is_absolute() else Path.home() / fallback


def inspect(path):
    """Read-only state. A matching hash verifies disk bytes, not FPS or a live game."""
    result = {'path': str(path), 'state': 'error', 'backup': 'missing', 'sha256': '', 'error': ''}
    try:
        info = regular_file(path)
        if info.st_size > 16 * 1024 * 1024:
            fail('DLL exceeds the expected size. This build is not supported.')
        sha = digest(path.read_bytes())
        result.update(sha256=sha, state={ORIGINAL_SHA256: 'original', LEGACY_SHA256: 'legacy', PATCHED_SHA256: 'patched'}.get(sha, 'unknown'))
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists() or backup.is_symlink():
            try:
                binfo = regular_file(backup)
                result['backup'] = 'valid' if binfo.st_size <= 16 * 1024 * 1024 and digest(backup.read_bytes()) == ORIGINAL_SHA256 else 'invalid'
            except OSError:
                result['backup'] = 'unreadable'
            except RuntimeError:
                result['backup'] = 'invalid'
    except (OSError, RuntimeError) as error:
        result['error'] = friendly_error(error)
    return result


def candidates_at(folder):
    if folder.name == 'ntdll.dll':
        return [folder] if folder.exists() or folder.is_symlink() else []
    return [folder / rel for rel in DLL_LAYOUTS if (folder / rel).exists() or (folder / rel).is_symlink()]


def discover():
    """Bounded local discovery; never execute configuration or walk entire disks."""
    home = Path.home()
    data = xdg('XDG_DATA_HOME', '.local/share')
    config = xdg('XDG_CONFIG_HOME', '.config')
    bases = [data / 'lutris/runners/wine', home / '.local/share/lutris/runners/wine',
             home / '.var/app/net.lutris.Lutris/data/lutris/runners/wine']
    steam = [data / 'Steam', home / '.local/share/Steam', home / '.steam/root', home / '.steam/steam',
             home / '.var/app/com.valvesoftware.Steam/data/Steam',
             home / '.var/app/com.valvesoftware.Steam/.local/share/Steam']
    roots, warnings = [], []
    for root in steam[:]:
        try:
            vdf = root / 'steamapps/libraryfolders.vdf'
            if vdf.is_file() and vdf.stat().st_size < 1024 * 1024:
                for value in re.findall(r'"path"\s+"([^"\n]+)"', vdf.read_text(errors='replace')):
                    path = Path(value.replace('\\\\', '\\'))
                    if path.is_absolute():
                        steam.append(path)
        except OSError:
            warnings.append('A Steam library could not be read.')
    bases.extend(p / 'compatibilitytools.d' for p in steam)
    for base in dict.fromkeys(bases):
        try:
            if base.is_dir():
                children = sorted(base.iterdir())
                if len(children) > 512:
                    warnings.append('Runner discovery is limited to 512 entries per directory.')
                roots.extend(p for p in children[:512] if p.is_dir())
        except OSError:
            warnings.append('A runner directory could not be read. You can enter its path manually.')
    for key in ('PROTONPATH', 'WINE'):
        value = os.environ.get(key, '')
        if value and Path(value).is_absolute():
            p = Path(value)
            roots.append(p if key == 'PROTONPATH' else p.parent.parent)
    # Only simple wine.version scalar values are interpreted. Full YAML isn't evaluated.
    configs = [config / 'lutris/games', home / '.config/lutris/games',
               home / '.var/app/net.lutris.Lutris/config/lutris/games']
    for folder in dict.fromkeys(configs):
        try:
            files = sorted(folder.glob('*.y*ml'))[:1000]
            for file in files:
                if file.stat().st_size > 1024 * 1024:
                    continue
                in_wine = False
                for line in file.read_text(errors='replace').splitlines():
                    if line and not line[0].isspace() and not line.startswith('#'):
                        in_wine = line.strip() == 'wine:'
                    if not in_wine:
                        continue
                    match = re.match(r'^\s+version:\s*(.+?)\s*$', line)
                    if not match:
                        continue
                    value = match.group(1)
                    if value[:1] in ('"', "'") and value[-1:] == value[:1]:
                        value = value[1:-1]
                    else:
                        value = value.split(' #', 1)[0].strip()
                    p = Path(value).expanduser()
                    if p.is_absolute():
                        roots.extend((p, p.parent.parent))
                    elif '/' not in value and value not in ('.', '..'):
                        roots.extend(base / value for base in bases)
        except OSError:
            warnings.append('A Lutris configuration could not be read.')
    found = {}
    for root in dict.fromkeys(roots):
        try:
            for path in candidates_at(root):
                # Preserve DLL symlinks for an explicit error; deduplicate parent aliases.
                canonical = path.parent.resolve() / path.name
                found[str(canonical)] = inspect(canonical)
        except (OSError, RuntimeError):
            warnings.append('A runner path could not be resolved.')
    return sorted(found.values(), key=lambda item: (item['state'] not in ('original', 'legacy', 'patched'), item['path'])), list(dict.fromkeys(warnings))


def fail(message):
    raise RuntimeError(message)


def regular_file(path):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode):
        fail(f'Not a regular file (DLL symlinks are not modified): {path}')
    return info


def locate(explicit):
    if explicit:
        supplied = Path(explicit).expanduser().absolute()
        paths = candidates_at(supplied)
        if len(paths) != 1:
            fail('No unique 64-bit ntdll.dll found. Select the Jinteia-Proton runner folder, not the game or prefix folder.')
        regular_file(paths[0])
        return paths[0].resolve()
    items, _ = discover()
    supported = [Path(item['path']) for item in items if item['state'] in ('original', 'legacy', 'patched')]
    if len(supported) != 1:
        fail('No unique compatible runner found. Requires the matching Jinteia-Proton fix; use --runner "/path/to/runner".')
    return supported[0]


def check_readable_mappings(path):
    """Best-effort check; report inaccessible processes without probing around permissions.

    The caller must close the game and patcher. Atomic replacement writes a
    new inode: it never modifies bytes behind an existing file mapping.
    """
    info = path.stat()
    device = (os.major(info.st_dev), os.minor(info.st_dev))
    proc = Path('/proc')
    if not proc.is_dir():
        fail('Process inspection requires Linux /proc.')
    unchecked = set()
    for entry in proc.iterdir():
        if not entry.name.isdigit():
            continue
        try:
            if entry.stat().st_uid != os.getuid():
                continue
            maps = (entry / 'maps').read_text(errors='replace')
        except (FileNotFoundError, ProcessLookupError):
            continue
        except PermissionError:
            unchecked.add(entry.name)
            continue
        for line in maps.splitlines():
            fields = line.split(None, 5)
            if len(fields) < 5:
                continue
            dev = tuple(int(x, 16) for x in fields[3].split(':'))
            if dev == device and int(fields[4]) == info.st_ino:
                fail(f'The DLL is used by process {entry.name}. Fully close the game and patcher.')
    return unchecked


def atomic_write(path, data, mode):
    fd, tmp = tempfile.mkstemp(prefix='.jinteia-heap-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as output:
            output.write(data)
            os.fchmod(output.fileno(), stat.S_IMODE(mode))
            output.flush()
            os.fsync(output.fileno())
        os.replace(tmp, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def save_backup(path, data, mode):
    if path.exists() or path.is_symlink():
        regular_file(path)
        if digest(path.read_bytes()) != ORIGINAL_SHA256:
            fail(f'Existing backup does not match: {path}')
        return
    # Publish a complete backup without overwriting an existing backup.
    fd, tmp = tempfile.mkstemp(prefix='.jinteia-backup-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as output:
            output.write(data)
            os.fchmod(output.fileno(), stat.S_IMODE(mode))
            output.flush()
            os.fsync(output.fileno())
        os.link(tmp, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        os.unlink(tmp)


def change(path, action, emit=print):
    if action not in ("apply", "restore", "revert"):
        fail("Unknown action.")
    if sys.platform != "linux":
        fail("This installer requires Linux.")
    lock_path = path.with_name('.jinteia-heap-test1.lock')
    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'r+') as lock:
        lock_info = os.fstat(lock.fileno())
        if not stat.S_ISREG(lock_info.st_mode) or lock_info.st_uid != os.getuid():
            fail('Invalid lock file. Installation stopped.')
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        info = regular_file(path)
        if info.st_uid != os.getuid():
            fail('The DLL is not owned by your user. Do not run with sudo.')
        if info.st_size > 16 * 1024 * 1024:
            fail('Unsupported DLL size. No changes made.')
        current = path.read_bytes()
        current_hash = digest(current)
        if current_hash not in (ORIGINAL_SHA256, LEGACY_SHA256, PATCHED_SHA256):
            fail('Unsupported DLL build. Requires the matching Jinteia-Proton fix. No patch applied. SHA256: ' + current_hash)
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if action == 'apply' and current_hash == PATCHED_SHA256:
            emit('Heap Fix is already installed. No further patch is needed.')
            return
        if action == 'revert' and current_hash == LEGACY_SHA256:
            emit('Heap-Test1 is already in place.')
            return
        if action == 'revert' and current_hash == ORIGINAL_SHA256:
            fail('Heap-Test2 is not installed; there is no second fix to revert.')
        if action == 'restore' and current_hash == ORIGINAL_SHA256:
            emit('The original DLL is already in place.')
            return
        unchecked = check_readable_mappings(path)
        emit('Process scan complete. Checking the original backup and target file...')
        if action == 'apply':
            new_data = patched_bytes(current)
            save_backup(backup, original_bytes(current), info.st_mode)
            if digest(backup.read_bytes()) != ORIGINAL_SHA256:
                fail('Original backup verification failed. The DLL has not been changed.')
            emit('Original backup saved and verified.')
        else:
            regular_file(backup)
            new_data = backup.read_bytes()
            if digest(new_data) != ORIGINAL_SHA256:
                fail('The backup is damaged or belongs to another build.')
            if action == 'revert':
                new_data = legacy_bytes(new_data)
        # Recheck immediately before replacement; do not launch a game during this script.
        unchecked.update(check_readable_mappings(path))
        if path.read_bytes() != current:
            fail('The DLL changed during this operation. Stopping.')
        if unchecked:
            emit(f'Warning: {len(unchecked)} protected processes could not be inspected. '
                  'The game and patcher must be closed.')
        regular_file(path)
        emit('Replacing the DLL atomically, then verifying SHA256...')
        atomic_write(path, new_data, info.st_mode)
        if digest(path.read_bytes()) != digest(new_data):
            fail('Post-write verification failed. Original backup: ' + str(backup))
        emit({'apply': 'Heap-Test2 installed successfully (includes Heap-Test1).',
              'restore': 'Original DLL restored byte for byte.',
              'revert': 'Heap-Test2 removed. Verified Heap-Test1 restored.'}[action])
        emit('Backup: ' + display_path(backup))
        emit('Fully restart the game. No additional Lutris variables are required.')


def display_path(path):
    return str(path).replace(str(Path.home()), '~')


def friendly_error(error):
    if isinstance(error, BlockingIOError):
        return 'Another installer is working on this runner. Close it and try again.'
    if isinstance(error, PermissionError):
        return 'Permission denied. Choose a runner owned by your user; do not use sudo.'
    if isinstance(error, FileNotFoundError):
        return 'A required file is missing. Check the runner path and original backup.'
    if isinstance(error, OSError) and error.errno == 28:
        return 'Disk full. Free some space and check the DLL status again.'
    if isinstance(error, OSError) and error.errno in (38, 95):
        return 'The filesystem does not support a required file operation. Use a runner on a Linux filesystem.'
    if isinstance(error, OSError) and error.errno == 30:
        return 'The filesystem is read-only. Choose a writable runner.'
    return display_path(str(error)) or type(error).__name__


def diagnostic(path=None, events=()):
    state = inspect(path) if path else None
    if state:
        state['path'] = display_path(state['path'])
        state['error'] = display_path(state['error'])
    return {'application': 'Jinteia Heap Fix', 'author': AUTHOR, 'installer_version': INSTALLER_VERSION,
            'patch': 'Heap-Test2 + Heap-Test1; internal group alignment',
            'platform': sys.platform, 'architecture': platform.machine(),
            'python': platform.python_version(), 'time_utc': datetime.now(timezone.utc).isoformat(),
            'disk_state': state, 'events': [display_path(str(x)) for x in events],
            'note': 'Disk status does not prove FPS improvement. Home directory is shortened to ~.'}


def save_diagnostic(path=None, events=()):
    folder = xdg('XDG_STATE_HOME', '.local/state') / 'dtypnt71/jinteia-heap-fix'
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, name = tempfile.mkstemp(prefix='diagnose-', suffix='.json', dir=folder)
    with os.fdopen(fd, 'w', encoding='utf-8') as output:
        json.dump(diagnostic(path, events), output, ensure_ascii=False, indent=2)
        output.write('\n')
    return Path(name)