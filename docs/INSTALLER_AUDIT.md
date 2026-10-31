# Source-readable v0.2 installer — audit checklist

**Status: DRAFT. First-time native Lutris installation and integrated Heap-Fix application passed on a separate CachyOS test account. Game configuration, WebView2, actual patcher/game launch, and failure recovery remain unverified; do not publish as a stable release yet.**

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
- The original v0.2 release asset SHA-256, nested runner archive and unpatched 64-bit DLL were checked successfully on CachyOS. Lutris integration, first-run/second-run behavior on a clean system, and actual game launch are **not yet verified in this PR**. A separate real-DLL patch+restore cycle has now passed in the isolated test runner.

## Release verification completed on CachyOS (2026-10-31)

The maintainer ran `bash install.sh --verify-release` on the actual public GitHub v0.2 release. The downloaded 515.4 MiB file was verified against the pinned release SHA-256. The nested Proton runner was extracted without executing its `.run` wrapper, and its original 64-bit `ntdll.dll` exactly matched `ORIGINAL_SHA256`.

Observed success marker: `RELEASE VERIFIED: asset checksum, nested runner archive, and original 64-bit DLL match.`

This result validates the release archive and original DLL **only**; it does not by itself verify the patch application, recovery, real Lutris installation, WebView2 or game launch.

## Next safe test: real Heap-Fix apply/restore in a temporary directory

The draft `bash install.sh --test-heap` mode verifies the release again, extracts the original runner to a private temporary directory, runs the recovered real Heap-Fix installer against that temporary DLL, verifies both patched DLL and original backup hashes, restores the original DLL byte-for-byte, then removes the temporary runner and download. It never invokes the Lutris setup helper and never targets the user's working runner or prefix. It requires at least **4 GiB free** in the temporary filesystem, such as `/tmp` or an alternative set by `TMPDIR`. It does write a temporary runner and patch that temporary copy; unlike `--verify-release`, it is **not read-only**.

### Real isolated Heap-Fix test — PASSED on CachyOS, 2026-10-31

The maintainer ran `bash install.sh --test-heap` after `git pull --ff-only` from this branch. The public v0.2 asset checksum and original 64-bit DLL checksum matched. The test extracted the full runner into a private directory under `/tmp/jinteia-source-installer.*/isolated-runner/`, ran the *actual* recovered Heap-Fix 3.0.0 application and original-DLL restoration against **that temporary runner**, and checked the expected patched DLL and original-backup SHA-256 values.

Observed success markers:
- `[SUCCESS] HEAP FIX INSTALLED`
- `[SUCCESS] ORIGINAL RESTORED — HEAP FIX REMOVED`
- `ISOLATED HEAP TEST PASSED: real original DLL patched, backup verified, then restored byte-for-byte.`

The original helper warned that **four protected processes could not be inspected**. This does **not** undermine the byte-level output validation of the isolated test, but it means that the process-running check was not exhaustive. The test never invoked the Lutris setup helper or targeted the maintainer's working runner. The temporary runner is removed by the shell trap when the command exits.

**Validated now:** release asset, original DLL, real Heap-Fix1+2 application on matching temporary DLL, original-backup checksum and restoration. **Not yet validated:** full Lutris entry creation, clean new-user installation, original Jinteia patcher/WebView2 first run, gameplay, or end-to-end install failure recovery.

## First integrated installation on an isolated CachyOS user — PASSED (2026-10-31)

The maintainer used the source-readable installer in a separate non-admin Linux account (`/home/test`) with **CachyOS, KDE Wayland, Linux 7.3.0-5-cachyos, native Lutris 0.5.22, and an NVIDIA GeForce RTX 4070 SUPER**.

All six installer setup sections completed:
- System preflight and native Lutris Python configuration API passed; both 64-bit and 32-bit Vulkan loaders and Vulkan information were detected.
- The released Proton runner was installed under the test account's own Lutris runner directory.
- Jinteia game/prefix directories were created within the test account.
- Lutris reported `Lutris entry created: Jinteia Patcher 0.2` and `Lutris entry prepared`; the configuration helper sets Wine runner version `Jinteia-Proton-0.2`. **The maintainer subsequently confirmed that the Lutris GUI entry exists and its runner/prefix settings match the expected values.**
- After the Lutris entry was created, the real Heap-Fix program reported `[SUCCESS] HEAP FIX INSTALLED` and `Original backup saved and verified.`
- The coordinator finished with `Runner and Heap Fix ready.`

**Nonfatal warnings observed:** two `PyGIWarning` messages when loading Lutris GTK/Gdk; the entry was created despite those warnings. The Heap-Fix process scan also warned that **four protected processes could not be inspected**; the fix continued, verified the original backup and reported success. This limits confidence that no other process could be using the target DLL; it is **not** evidence of a binary checksum mismatch.

**Verified after the installer run:** the maintainer checked the Lutris GUI and confirmed that the created entry and settings are correct. **Not tested (by deliberate choice):** game/patcher login or game launch in this test account, because the maintainer reports a game rule prohibiting two different accounts on one PC. No bypass or second-account game test is planned. WebView2 installation in the fresh prefix and interrupted-install recovery remain unverified. Re-running the installer on the existing test runner was subsequently rejected before download, as expected.

The existing main user's working runner and prefixes remained out of scope because this was a separate account. The public release and `main` branch remain unchanged.

## Release gates

1. Check the new GitHub Actions status and review each source file.
2. [Done] Verify the actual v0.2 `.run` payload and expected original DLL checksum.
3. [Done for native Lutris on CachyOS] Test initial installation on a separate Linux user/home with no existing runner.
4. [Done for the isolated runner] Confirm successful real-binary Heap-Fix application, verified original backup and restore. Still test the installation's integrated handoff.
5. [Lutris GUI verified] Game/patcher launch in a second account is explicitly out of scope due to the reported game rule. Do not claim the new-user game launch was tested; validate remaining setup via documentation and independent first-account user feedback when available.
6. Improve public transparency further by releasing the runner archive separately, not only embedding it in `.run`.
7. Only then merge PRs and publish a new release.

**Preserve the existing v0.2 installation:** the installer intentionally refuses to overwrite a runner with the same name. No published v0.2 assets were changed by this PR.
