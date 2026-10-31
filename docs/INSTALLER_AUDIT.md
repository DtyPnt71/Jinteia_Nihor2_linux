# Source-readable v0.2 installer — audit checklist

**Status: DRAFT / INCOMPLETE. Not ready for installation or release.**

The proposed `install.sh` is a transparent coordinator for the existing v0.2 release. It currently downloads the SHA-256-pinned 540 MB `.run`, treats it **only as an archive**, extracts the inner runner tarball, invokes the original readable Lutris setup helper, then calls the recovered exact-build Heap Fix.

**The dependency files listed below are not yet committed on this branch.** As a result, the GitHub copy of `install.sh` deliberately fails its initial prerequisite check. Do not instruct end users to run it from `main` or from this branch yet.

## Files to add from the recovered source archive

- `proton/setup-jinteia.sh`
- `proton/tools/create_lutris_entry.py`
- `heap/heap-test.py`
- `heap/heap_core.py`
- `heap/binary_patch.py`
- Offline tests: `tests_bootstrap.py`, `tests_bootstrap_integration.py`, and `proton/tests/test_installer.py`.
- Relevant original build/heap tests and reproducibility instructions, after confirming provenance and avoiding third-party binary redistribution.

The Wine source diffs are in **draft PR #5**: https://github.com/DtyPnt71/Jinteia_Nihor2_linux/pull/5. The proposed simplified docs are in **draft PR #4**.

## Verified hashes on a working Linux installation (read-only)

| File state | SHA-256 | Status |
| --- | --- | --- |
| Installed 64-bit patched `ntdll.dll` | `7b925e64a014111f80a1be831866f4d38f34c51abc35640ea87a6926716b021f` | Exact match to recovered `PATCHED_SHA256` |
| Original DLL backup `ntdll.dll.jinteia-heap-test1.original` | `ad0243384afa5fad82331dacfd7e45383b2a0c955fb8f99dd12e1cfd7d558438` | Exact match to recovered `ORIGINAL_SHA256` |

The user additionally ran `bash install.sh --check --runner <existing runner>`; it reported `[INSTALLED]`, verified original backup, and Heap-Fix2 + Heap-Fix1 verified on disk. The command made no changes.

## Tests from the recovered local preview

- 16 original setup regression tests passed.
- 5 bootstrap tests passed.
- 3 *simulated* end-to-end flow tests passed (local fake `.run` archive, mock download, mock Lutris installer and Heap Fix; covers checksum mismatch, user cancellation, extraction without executing the .run wrapper, and refusal to overwrite an existing runner).
- Shell syntax passed.
- Original heap fixture tests have **not** been run in this environment because the matching original binary is not available here.

**Not yet tested:** the actual 540 MB asset download and extraction, full install on isolated native/Flatpak Lutris, real binary Heap-Fix application, restore, and clean/repeated installation.

## Safety gates

1. Add the recovered source dependencies to this branch and review them.
2. Add source-level test fixtures and CI checks.
3. Verify `install.sh` against the exact existing release payload SHA-256.
4. Use an isolated home/runner location (or separate test account), *never* overwrite a working `Jinteia-Proton-0.2`.
5. Exercise install, already installed, failed download, failed checksum, backup/restore, and failure after install but before heap patch.
6. Test in Lutris and Jinteia before public release.
7. Prefer a separately published, hashed runner archive in the future; a readable launcher alone does not prove reproducibility of the opaque binary payload.

Do not merge or label this as a completed one-command installer until these gates pass.
