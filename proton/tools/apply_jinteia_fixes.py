#!/usr/bin/env python3
from pathlib import Path
import sys

MARKER_WX = "Keep generated import stubs W^X"
MARKER_OLE = "The raw pointer in prop_oledroptarget is only valid"


def die(msg: str):
    raise SystemExit(f"ERROR: {msg}")


def patch_loader(path: Path):
    src = path.read_text(encoding="utf-8")

    alloc_old = '''        if (NtAllocateVirtualMemory( NtCurrentProcess(), (void **)&stubs, 0, &size,
                                     MEM_COMMIT, PAGE_EXECUTE_READWRITE ) != STATUS_SUCCESS)
            return 0xdeadbeef;
'''
    alloc_new = '''        if (NtAllocateVirtualMemory( NtCurrentProcess(), (void **)&stubs, 0, &size,
                                     MEM_COMMIT, PAGE_READWRITE ) != STATUS_SUCCESS)
            return 0xdeadbeef;
'''

    if alloc_new not in src:
        if src.count(alloc_old) != 1:
            die("loader.c: expected allocate_stub RWX allocation was not found exactly once")
        src = src.replace(alloc_old, alloc_new, 1)

    stub_anchor = '''    stub = &stubs[nb_stubs++];
'''
    pre_write = '''    stub = &stubs[nb_stubs++];

    /* Keep generated import stubs W^X.  NtProtectVirtualMemory rounds this
     * small range to the containing page.  Existing stubs on that page are
     * briefly non-executable while the loader writes the next stub, then the
     * page is restored to PAGE_EXECUTE_READ below. */
    {
        void *protect_addr = stub;
        SIZE_T protect_size = sizeof(*stub);
        ULONG old_protect;

        if (NtProtectVirtualMemory( NtCurrentProcess(), &protect_addr, &protect_size,
                                    PAGE_READWRITE, &old_protect ) != STATUS_SUCCESS)
            return 0xdeadbeef;
    }
'''

    if MARKER_WX not in src:
        if src.count(stub_anchor) != 1:
            die("loader.c: stub assignment anchor was not found exactly once")
        src = src.replace(stub_anchor, pre_write, 1)

    ret_anchor = '''    return (ULONG_PTR)stub;
}

#else  /* __i386__ */
'''
    post_write = '''    {
        void *protect_addr = stub;
        SIZE_T protect_size = sizeof(*stub);
        ULONG old_protect;

        NtFlushInstructionCache( NtCurrentProcess(), stub, sizeof(*stub) );
        if (NtProtectVirtualMemory( NtCurrentProcess(), &protect_addr, &protect_size,
                                    PAGE_EXECUTE_READ, &old_protect ) != STATUS_SUCCESS)
            return 0xdeadbeef;
    }

    return (ULONG_PTR)stub;
}

#else  /* __i386__ */
'''

    if "NtFlushInstructionCache( NtCurrentProcess(), stub, sizeof(*stub) )" not in src:
        if src.count(ret_anchor) != 1:
            die("loader.c: allocate_stub return anchor was not found exactly once")
        src = src.replace(ret_anchor, post_write, 1)

    path.write_text(src, encoding="utf-8")


def patch_ole32(path: Path):
    src = path.read_text(encoding="utf-8")

    if MARKER_OLE in src:
        return

    decl_old = '''  IDropTarget *drop_target;
  HRESULT hr;
'''
    decl_new = '''  IDropTarget *drop_target;
  HRESULT hr;
  DWORD pid = 0;
'''

    if src.count(decl_old) != 1:
        die("ole2.c: RevokeDragDrop declaration anchor was not found exactly once")
    src = src.replace(decl_old, decl_new, 1)

    release_old = '''  drop_target = GetPropW(hwnd, prop_oledroptarget);
  if(drop_target) IDropTarget_Release(drop_target);

  RemovePropW(hwnd, prop_oledroptarget);
'''
    release_new = '''  /* The raw pointer in prop_oledroptarget is only valid in the process that
   * called RegisterDragDrop, which is always the process owning the window.
   * Releasing it from any other process dereferences a foreign address. */
  GetWindowThreadProcessId(hwnd, &pid);
  if (pid == GetCurrentProcessId())
  {
    drop_target = GetPropW(hwnd, prop_oledroptarget);
    if(drop_target) IDropTarget_Release(drop_target);
  }

  RemovePropW(hwnd, prop_oledroptarget);
'''

    if src.count(release_old) != 1:
        die("ole2.c: RevokeDragDrop release block was not found exactly once")
    src = src.replace(release_old, release_new, 1)

    path.write_text(src, encoding="utf-8")


def verify(wine_root: Path):
    loader = (wine_root / "dlls/ntdll/loader.c").read_text(encoding="utf-8")
    ole2 = (wine_root / "dlls/ole32/ole2.c").read_text(encoding="utf-8")

    start = loader.find("static ULONG_PTR allocate_stub")
    end = loader.find("#else  /* __i386__ */", start)
    if start < 0 or end < 0:
        die("verify: could not isolate allocate_stub")
    fn = loader[start:end]

    checks = [
        ("PAGE_EXECUTE_READWRITE" not in fn, "allocate_stub still contains PAGE_EXECUTE_READWRITE"),
        ("MEM_COMMIT, PAGE_READWRITE" in fn, "allocate_stub is not allocated PAGE_READWRITE"),
        ("PAGE_EXECUTE_READ" in fn, "allocate_stub is not restored to PAGE_EXECUTE_READ"),
        ("NtFlushInstructionCache" in fn, "instruction cache flush is missing"),
        (MARKER_OLE in ole2, "ole32 RevokeDragDrop process-owner check is missing"),
        ("GetWindowThreadProcessId(hwnd, &pid);" in ole2, "ole32 process-owner lookup is missing"),
        ("if (pid == GetCurrentProcessId())" in ole2, "ole32 owner comparison is missing"),
    ]

    failed = [msg for ok, msg in checks if not ok]
    if failed:
        die("verify failed: " + "; ".join(failed))

    print("Jinteia fixes verified:")
    print("  [OK] import stubs use W^X instead of persistent RWX")
    print("  [OK] RevokeDragDrop only releases the raw drop-target pointer in its owner process")


def main():
    if len(sys.argv) not in (2, 3):
        die("usage: apply_jinteia_fixes.py /path/to/wine [--verify-only]")

    wine_root = Path(sys.argv[1]).resolve()
    if not wine_root.is_dir():
        die(f"Wine source directory not found: {wine_root}")

    if len(sys.argv) == 2:
        patch_loader(wine_root / "dlls/ntdll/loader.c")
        patch_ole32(wine_root / "dlls/ole32/ole2.c")

    verify(wine_root)


if __name__ == "__main__":
    main()