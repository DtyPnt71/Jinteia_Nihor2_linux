# Trust, release integrity and installer transparency

[Back to overview](../README.md) · [Installation guide](INSTALLATION.md)

A user running a Linux installer deserves to know **what it does and what it installs**. We welcome feedback about transparency.

## Current state of v0.2

- The released installer is **Jinteia-Proton-0.2-installer.run**, a roughly **540 MB** self-contained distribution.
- It detects the Linux/Lutris environment and dependencies, sets up the custom runner and creates a Lutris entry, as described in the release.
- The separately distributed **Jinteia-HeapFix1+2.zip** contains a manual patch workflow for the customized Wine runtime.
- The repository currently publishes the documentation and banner, **but not the full source, build instructions, or payload manifest for these release assets**.

The release assets should therefore **not be described as fully source-auditable or reproducible** at this time. This documentation change does not alter or repackage those binaries.

## Verify downloaded v0.2 assets

GitHub's release asset metadata reports these SHA-256 values:

| File | SHA-256 |
| --- | --- |
| **Jinteia-Proton-0.2-installer.run** | **e2d73e4c36266c4c07323bd73a318f9e52e5a805f4774ae1cab8c994df9b59e7** |
| **Jinteia-HeapFix1+2.zip** | **4347f539a4d69d80a2c7499d8b5985a85c6a2eb9e3915a78e9ce1e8bf252b3a6** |

In a terminal, run these commands in the folder containing the downloaded assets:

~~~bash
sha256sum Jinteia-Proton-0.2-installer.run
sha256sum 'Jinteia-HeapFix1+2.zip'
~~~

Compare the entire value with the corresponding row above. If a value differs, **do not execute that file**.

**Limitations:** A SHA-256 match verifies that the bytes match the published digest. It does **not** prove that an installer is safe, open-source or independently reproducible. A checksum posted on the same account as an asset is not an independent security attestation.

## Why not just rename .run to .sh?

Many Linux **.run** installers are executable shell wrappers with compressed or binary data appended. Renaming that file to **.sh** does not make those appended bytes readable.

The sensible long-term design is:

1. Publish a small, **human-readable install.sh** in the repository.
2. Release the custom runner as a **separate versioned archive**.
3. Have the script explain the files and directories it will modify **before** asking to install.
4. Verify the archive against a documented SHA-256 value **before extraction**.
5. Publish the build recipe, source/patch references, and an archive manifest where distribution rights permit.
6. Keep system Wine and existing working Jinteia prefixes untouched; use no elevated privileges by default.
7. Test the new install and uninstall/rollback flows before releasing them.

**That design has not yet been implemented for v0.2.** It requires the original installer sources and a properly packaged runner, not a file-extension change.

## External dependencies

Jinteia / Nihor2, Lutris, Wine/GE-Proton and Microsoft WebView2 are separate projects. The Microsoft WebView2 runtime should be obtained from [Microsoft's official download page](https://developer.microsoft.com/en-us/microsoft-edge/webview2/).

## Reporting concerns

If you find suspicious behavior or have questions about what the installer modifies, open an issue with a **non-sensitive** description. Do not publish private account credentials, tokens or session IDs.
