# Source-readable v0.2 installer — audit checklist

**Status: DRAFT. Source files have been added, but the installer has NOT passed a real clean-system installation test. Do not publish it as a stable release yet.**

The proposed `install.sh` downloads the existing pinned v0.2 `.run` asset, verifies its SHA-256, treats it only as a transport archive (never executes its wrapper), extracts the nested runner and invokes the recovered source-readable Lutris helper and exact-build Heap Fix.

## Source files now available in this PR

- `install.sh`
- `proton/setup-jinteia.sh`
- `proton/tools/create_lutris_entry.py`
- `heap/heap-test.py`, `heap/heap_core.py`, `heap/binary_patch.py`
- `proton/tests/test_installer.py`, `tests_bootstrap.py`
- Heap tests: `heap/tests/test_heap_fix.py`, `test_terminal.py`, `test_upgrade.py`
- Basic CI: `.github/workflows/installer-checks.yml`

The corresponding Wine source-diff review is in [draft PR #5](https://github.com/DtyPnt71/Jinteia_Nihor2_linux/pull/5). Revised user documentation is in [draft PR #4](https://github.com/DtyPnt71/Jinteia_Nihor2_linux/pull/4).

## Confirmed on a working Linux installation (read-only)

| File | SHA-256 | Meaning |
| --- | --- | --- |
| Patched 64-bit `ntdll.dll` | `7b925e64a014111f80a1be831866f4d38f34c51abc35640ea87a6926716b021f` | Matches recovered `PATCHED_SHA256` |
| Original DLL backup `ntdll.dll.jinteia-heap-test1.original` | `ad0243384afa5fad82331dacfd7e45383b2a0c955fb8f99dd12e1cfd7d558438` | Matches recovered `ORIGINAL_SHA256` |

The maintainer ran the source-readable installer's read-only `--check` and received `[INSTALLED]` plus a verified original backup.

## Tests and limitations

- Recovered original setup regression suite: **16 tests passed locally**.
- New bootstrap unit suite: **5 tests passed locally**.
- Separate isolated test harness using mock download/runner/Heap-Fix: **3 tests passed locally**; its source file is in the local preview but is not part of this GitHub PR yet.
- Basic syntax and Python compilation checks passed.
- The CI workflow runs the original setup and bootstrap unit suites in GitHub Actions. **A green CI result is not proof of a real installation**.
- The exact full `540 MB` release asset extraction, Lutris integration, first-run/second-run behavior on a real system, real DLL patch/restore on a clean runner, and actual game launch are **not yet verified in this PR**.

## Release gates

1. Check the new GitHub Actions status and review each source file.
2. Verify the actual v0.2 `.run` payload and expected original DLL checksum.
3. Test installation on an isolated user/home with no existing `Jinteia-Proton-0.2` runner.
4. Confirm successful Heap-Fix application and verified original backup in that isolated runner, then exercise the restore path.
5. Test native Lutris config and WebView2/official patcher steps, plus actual gameplay.
6. Improve public transparency further by releasing the runner archive separately, not only embedding it in `.run`.
7. Only then merge PRs and publish a new release.

**Preserve the existing v0.2 installation:** the installer intentionally refuses to overwrite a runner with the same name. No published v0.2 assets were changed by this PR.
