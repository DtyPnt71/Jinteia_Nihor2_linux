"""Upgrade, rollback, source and PE boundaries. DtyPnt71."""
import importlib.util
import os
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import binary_patch as binary
import heap_core as core
ORIGINAL=Path(sys.argv.pop(1)).read_bytes()
LEGACY=binary.legacy_bytes(ORIGINAL)
PATCHED=binary.patched_bytes(ORIGINAL)
spec=importlib.util.spec_from_file_location('source_patch',ROOT/'source/apply_heap_fix.py')
source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)


class UpgradeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.dll=Path(self.tmp.name)/'ntdll.dll';self.dll.write_bytes(LEGACY)
        self.backup=self.dll.with_name(self.dll.name+core.BACKUP_SUFFIX)
        self.scan=patch.object(core,'check_readable_mappings',return_value=set());self.scan.start();self.addCleanup(self.scan.stop)

    def run_change(self,action):
        core.change(self.dll,action,lambda text:None)

    def test_upgrade_reuses_original_backup(self):
        self.backup.write_bytes(ORIGINAL);inode=self.backup.stat().st_ino
        self.run_change('apply');self.assertEqual(self.dll.read_bytes(),PATCHED)
        self.assertEqual(self.backup.stat().st_ino,inode)
        self.assertEqual(self.backup.read_bytes(),ORIGINAL)

    def test_upgrade_reconstructs_verified_missing_backup(self):
        self.run_change('apply')
        self.assertEqual(self.backup.read_bytes(),ORIGINAL)
        self.assertEqual(self.dll.read_bytes(),PATCHED)

    def test_revert_keeps_first_fix_and_reapply_works(self):
        self.run_change('apply');self.run_change('revert')
        self.assertEqual(self.dll.read_bytes(),LEGACY)
        self.assertEqual(core.inspect(self.dll)['state'],'legacy')
        self.run_change('revert');self.run_change('apply')
        self.assertEqual(self.dll.read_bytes(),PATCHED)
        self.run_change('restore');self.assertEqual(self.dll.read_bytes(),ORIGINAL)

    def test_restore_directly_from_old_fix(self):
        self.backup.write_bytes(ORIGINAL);self.run_change('restore')
        self.assertEqual(self.dll.read_bytes(),ORIGINAL)

    def test_corrupt_backup_blocks_upgrade(self):
        self.backup.write_bytes(b'wrong')
        with self.assertRaises(RuntimeError):self.run_change('apply')
        self.assertEqual(self.dll.read_bytes(),LEGACY)

    def test_revert_missing_backup_does_not_change_dll(self):
        self.dll.write_bytes(PATCHED)
        with self.assertRaises(OSError):self.run_change('revert')
        self.assertEqual(self.dll.read_bytes(),PATCHED)

    def test_modified_new_dll_rejected(self):
        damaged=bytearray(PATCHED);damaged[binary.HELPER]^=1
        self.dll.write_bytes(damaged);self.backup.write_bytes(ORIGINAL)
        for action in ('apply','restore','revert'):
            with self.assertRaises(RuntimeError):self.run_change(action)
        self.assertEqual(self.dll.read_bytes(),damaged)

    def test_roundtrip_known_images(self):
        for data in (ORIGINAL,LEGACY,PATCHED):
            self.assertEqual(binary.original_bytes(data),ORIGINAL)
            self.assertEqual(binary.legacy_bytes(data),LEGACY)
            self.assertEqual(binary.patched_bytes(data),PATCHED)

    def test_pe_mapping_and_unwind_boundaries(self):
        pe=struct.unpack_from('<I',PATCHED,0x3c)[0]
        count=struct.unpack_from('<H',PATCHED,pe+6)[0]
        sh=pe+24+struct.unpack_from('<H',PATCHED,pe+20)[0]
        self.assertEqual(PATCHED[sh:sh+8],b'.text\0\0\0')
        vsize,rva,raw_size,raw_offset=struct.unpack_from('<4I',PATCHED,sh+8)
        self.assertEqual(rva,raw_offset)
        self.assertLessEqual(binary.HELPER+len(binary.HELPER_CODE),rva+vsize)
        self.assertLessEqual(vsize,raw_size)
        self.assertTrue(struct.unpack_from('<I',PATCHED,sh+36)[0]&0x20000000)
        self.assertEqual(binary.HOOK+5+struct.unpack_from('<i',PATCHED,binary.HOOK+1)[0],binary.HELPER)
        # Existing function/unwind metadata is unchanged. Helper is a leaf:
        # only volatile registers/flags are modified; no stack adjustment.
        self.assertEqual(PATCHED[0x9b000:0xab000],ORIGINAL[0x9b000:0xab000])
        for i in range(count):
            off=sh+40*i
            if PATCHED[off:off+8].rstrip(b'\0')==b'.pdata':
                length=struct.unpack_from('<I',PATCHED,off+8)[0]
                data=struct.unpack_from('<I',PATCHED,off+20)[0]
                for a,b,_ in struct.iter_unpack('<III',PATCHED[data:data+length]):
                    self.assertFalse(a<=binary.HELPER<b)
        checksum_offset,value=binary.checksum(PATCHED)
        self.assertEqual(struct.unpack_from('<I',PATCHED,checksum_offset)[0],value)

    def test_source_apply_upgrade_restore_and_unknown(self):
        # Minimal shape isolates the helper's exact two transformations.
        original=('static struct group *group_allocate(\n{\n'+source.GROUP_OLD+'}\n'
                  'static void bin_try_enable(\n{\n'+source.OLD+'}\n')
        p=Path(self.tmp.name)/'heap.c'
        for initial in (original,original.replace(source.OLD,source.NEW)):
            p.write_text(initial);source.patch_heap(p);source.verify_heap(p)
            first=p.read_text();source.patch_heap(p);self.assertEqual(p.read_text(),first)
            source.patch_heap(p,True);self.assertEqual(p.read_text(),original)
        p.write_text(original.replace(source.GROUP_OLD,'unknown\n'))
        before=p.read_bytes()
        with self.assertRaises(ValueError):source.patch_heap(p)
        self.assertEqual(p.read_bytes(),before)

if __name__=='__main__':unittest.main(verbosity=2)