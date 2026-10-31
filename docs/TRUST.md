# Trust, downloads and source transparency

[Overview](../README.md) · [Install](INSTALLATION.md) · [Technical verification](DEVELOPMENT.md)

## What is readable

This repository contains the **human-readable `install.sh` coordinator**, terminal interface, native Lutris setup helpers, exact-version Heap Fix Python code and automated tests.

The installer:
- Downloads only the **published v0.2 release asset** from the project's GitHub release.
- Verifies the downloaded bytes against this expected SHA-256:
  `e2d73e4c36266c4c07323bd73a318f9e52e5a805f4774ae1cab8c994df9b59e7`.
- Extracts the embedded runner archive **without executing** the opaque `.run` wrapper.
- Applies Heap Fix 1+2 only to the known matching 64-bit `ntdll.dll`; preserves an original backup and checks patched output.
- Uses the current user's Lutris files rather than replacing system Wine.
- Refuses to overwrite an existing `Jinteia-Proton-0.2` runner.

Read the sources in [install.sh](../install.sh), [scripts](../scripts), [heap](../heap) and [proton](../proton).

## What is *not* proven

The Wine/Proton binary is still the **existing prebuilt v0.2 distribution**. The script's source readability does **not** make that binary reproducible or independently verified. The recovered [Wine patch files](../patches) and their [provenance notes](RECOVERED_PATCHES.md) are published for review, but have **not been independently proven byte-for-byte equivalent** to the distributed runner.

A hash check establishes integrity against the recorded expected bytes, **not** absence of malicious code. The checksum is distributed by the same maintainer as the binary and is not an independent audit.

### Existing published release assets

| File | SHA-256 |
| --- | --- |
| `Jinteia-Proton-0.2-installer.run` | `e2d73e4c36266c4c07323bd73a318f9e52e5a805f4774ae1cab8c994df9b59e7` |
| `Jinteia-HeapFix1+2.zip` (legacy manual release asset) | `4347f539a4d69d80a2c7499d8b5985a85c6a2eb9e3915a78e9ce1e8bf252b3a6` |

The repository installer applies its included Heap Fix code; **you do not need to run the legacy Heap Fix ZIP separately** after a successful source-installer setup.

Maintainer verification commands and reproducibility notes are documented in [Development and validation](DEVELOPMENT.md).

## Manual downloads and limitations

The official `Nihor2-Patcher.exe` must be obtained separately from the game provider; this repository neither redistributes it nor bypasses anti-cheat or game account restrictions. Microsoft WebView2 Evergreen x64 can be **optionally downloaded** over HTTPS from Microsoft; the changing executable has **no pinned static SHA-256** in this project and is **never executed automatically**.

Native Lutris integration was verified on CachyOS; Flatpak is unsupported **by this installer**. We have not tested a fresh-prefix game launch through the new UI or full rollback of an interrupted initial installation. See [the audit log](INSTALLER_AUDIT.md).

**Latest published binary release: v0.2.** The merged source installer does not by itself publish a v0.3 release.
