# Recovered Wine patches — review status

These four text patches were recovered from the maintainer's original Jinteia-Proton/Heap-Fix development archives. They are **review artifacts**, not proof of a reproducible build.

## Identified changes

| File | What it does | Origin/status |
| --- | --- | --- |
| `0001-ntdll-wx-import-stubs.patch` | Changes generated import stub permissions from permanent RWX to RW during writing, then RX | Extracted from the saved Jinteia Wine v0.2 diff; exact released-binary correspondence not yet independently verified |
| `0002-ole32-revokedragdrop-owner-process.patch` | Guards a raw COM pointer release by the window-owning process | Original v0.2 project patch |
| `0003-ntdll-earlier-lfh-up-to-2k.patch` | Increases the eligible heap bin range for earlier LFH activation | Original Heap-Fix development patch; released Heap-Fix binary add-on may implement the same behavior through byte patching |
| `0004-ntdll-align-small-lfh-groups.patch` | Rounds a specific LFH group allocation request from `0x5f0` to `0x600` on 64-bit builds | Recovered Heap-Test2 source-level patch; equivalent binary add-on must be version checked |

**Not a validated patch series:** The patches have **not** been freshly applied and built against a clean GE-Proton 11-7 source checkout. The local source diff used for extraction also included unrelated upstream changes, which are intentionally excluded here.

A GitHub visitor can now **read the actual proposed code changes**, but that does **not** yet prove that the downloadable 540 MB `.run` was produced from precisely these source patches.

## Verified installed Heap-Fix2 status (2026-10-31)

A local Jinteia-Proton-0.2 installation reported these SHA-256 values:

- 64-bit `files/lib/wine/x86_64-windows/ntdll.dll`:
  `7b925e64a014111f80a1be831866f4d38f34c51abc35640ea87a6926716b021f`
- 32-bit `files/lib/wine/i386-windows/ntdll.dll`:
  `5239134a15e04f6052304042a857e929891cd0d1a392dfefa82b104ded3c8ab2`

A subsequent **read-only hash check** of the installed backup file `ntdll.dll.jinteia-heap-test1.original` returned `ad0243384afa5fad82331dacfd7e45383b2a0c955fb8f99dd12e1cfd7d558438`, matching the recovered `ORIGINAL_SHA256`. This verifies the backup **bytes** for this installation. A successful restore operation has not been performed or tested here.

The **64-bit** value exactly matches the recovered `heap/binary_patch.py` constant `PATCHED_SHA256`. Thus the on-disk 64-bit file matches the expected **Heap-Fix1+2 output**. This is a byte-level consistency check, **not** proof of performance, backup validity, or build reproducibility.

The recovered heap patcher targets the **64-bit DLL only**. The 32-bit hash was recorded for reference; no positive inference about patch state is possible from this source.

### Exact-build hashes in the recovered patcher

| State | SHA-256 |
| --- | --- |
| Original 64-bit ntdll.dll | `ad0243384afa5fad82331dacfd7e45383b2a0c955fb8f99dd12e1cfd7d558438` |
| Heap-Test1 | `4eda8ac60454c496487643d4b96ecb0f4668c2fcb9f7b3e35c46cf5785eab106` |
| Heap-Fix1+2 | `7b925e64a014111f80a1be831866f4d38f34c51abc35640ea87a6926716b021f` |

## Remaining verification before installation changes

1. Compare the recovered scripts and the exact 64-bit DLL from the published v0.2 release, not just a local machine.
2. Reproduce and test the patch application on a clean matching GE-Proton source snapshot.
3. Audit the original heap installer's backup, already-patched and restoration behaviors.
4. Publish source-readable installer `install.sh` and run integration tests using a **separate runner name** or isolated test account.
5. Keep existing Jinteia prefixes and released v0.2 assets unchanged until validated.

This branch intentionally changes **no installer or release artifact**. Avoid instructing users to apply these source patches to random Wine versions.
