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
- Separate isolated test harness using mock download/runner/Heap-Fix: **5 tests passed locally**, including both `--verify-release` and `--test-heap` modes; the integration test source is now checked into this PR.
- Basic syntax and Python compilation checks passed.
- The CI workflow runs the original setup and bootstrap unit suites in GitHub Actions. **A green CI result is not proof of a real installation**.
- The original v0.2 release asset SHA-256, nested runner archive and unpatched 64-bit DLL were checked successfully on CachyOS. Lutris integration, first-run/second-run behavior on a real system, real DLL patch/restore on a clean runner, and actual game launch are **not yet verified in this PR**.

## Release verification completed on CachyOS (2026-10-31)

The maintainer ran `bash install.sh --verify-release` on the actual public GitHub v0.2 release. The downloaded 515.4 MiB file was verified against the pinned release SHA-256. The nested Proton runner was extracted without executing its `.run` wrapper, and its original 64-bit `ntdll.dll` exactly matched `ORIGINAL_SHA256`.

Observed success marker: `RELEASE VERIFIED: asset checksum, nested runner archive, and original 64-bit DLL match.`

This result validates the release archive and original DLL **only**; it does not by itself verify the patch application, recovery, real Lutris installation, WebView2 or game launch.

## Next safe test: real Heap-Fix apply/restore in a temporary directory

The draft `bash install.sh --test-heap` mode verifies the release again, extracts the original runner to a private temporary directory, runs the recovered real Heap-Fix installer against that temporary DLL, verifies both patched DLL and original backup hashes, restores the original DLL byte-for-byte, then removes the temporary runner and download. It never invokes the Lutris setup helper and never targets the user's working runner or prefix. It requires at least **4 GiB free** in the temporary filesystem, such as `/tmp` or an alternative set by `TMPDIR`. It does write a temporary runner and patch that temporary copy; unlike `--verify-release`, it is **not read-only**.

The `--test-heap` path has passed **simulated offline integration tests**, but **has not yet been performed against the real release DLL**.

## Release gates

1. Check the new GitHub Actions status and review each source file.
2. Verify the actual v0.2 `.run` payload and expected original DLL checksum.
3. Test installation on an isolated user/home with no existing `Jinteia-Proton-0.2` runner.
4. Confirm successful Heap-Fix application and verified original backup in that isolated runner, then exercise the restore path.
5. Test native Lutris config and WebView2/official patcher steps, plus actual gameplay.
6. Improve public transparency further by releasing the runner archive separately, not only embedding it in `.run`.
7. Only then merge PRs and publish a new release.

**Preserve the existing v0.2 installation:** the installer intentionally refuses to overwrite a runner with the same name. No published v0.2 assets were changed by this PR.
