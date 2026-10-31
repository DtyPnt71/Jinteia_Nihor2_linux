# Troubleshooting — Jinteia-Proton v0.2

[Back to overview](../README.md) · [Installation guide](INSTALLATION.md)

Work through these checks **without deleting the Wine prefix**.

## The new runner is missing in Lutris

1. Quit **all** Lutris processes and start Lutris again.
2. Open **Jinteia Patcher 0.2 → Configure → Runner options**.
3. Check the Wine version selector for **Jinteia-Proton-0.2**.
4. If it is still missing, inspect the installer log (below) for errors.

The existing release describes a native Lutris install; Flatpak Lutris may need additional attention and has not been fully verified.

## The patcher does not start

Verify the game entry's **Executable** points to the real **Nihor2-Patcher.exe** and the **Working directory** is the folder containing it.

Then confirm:
- The Wine version is **Jinteia-Proton-0.2**.
- WebView2 **Evergreen x64** is installed **in this entry's prefix**, not in a different one.
- The existing v0.2 Heap Fix steps were completed successfully, where applicable to your setup.

Do not create a fresh Wine prefix just to troubleshoot a launch problem. Jinteia's Discord verification may treat it as a new session.

## The installer reports missing dependencies or Vulkan support

The installer checks host-side requirements, including 64-bit and 32-bit Vulkan. Follow its output to fix missing packages using **your distribution's package manager**. Do not blindly run package-management commands intended for a different distribution.

## WebView2 installer was run, but the patcher still complains

Check that you selected **Run EXE inside Wine prefix** for the **Jinteia Patcher 0.2** Lutris entry. Installing WebView2 in another prefix will not make it available to this entry. Confirm that you used the **x64 Evergreen Runtime**, not a developer SDK.

## Heap Fix did not report success

Close Lutris and Jinteia, extract the release ZIP, then open a terminal in the directory that actually contains **START.sh**. Run **sh START.sh** and read its output.

Do not blindly retry patches against a different runner version or modify system Wine files. Include the failure message when asking for help. There is no confirmed automatic rollback procedure documented for this asset, so make a backup before experimenting.

## Where to find the installation log

~~~text
~/.cache/jinteia-proton/setup-v0.2.log
~~~

To display it in your terminal:

~~~bash
cat ~/.cache/jinteia-proton/setup-v0.2.log
~~~

## When reporting a problem

Please include:

- Linux distribution and version
- Native or Flatpak Lutris
- Jinteia-Proton version
- The installation step that failed
- The relevant error text and installer log

**Review logs before posting them publicly.** Remove usernames, private paths, access tokens, session IDs or other secrets. Do not share your game account password.

Please report **which step fails**, not just "it doesn't work". This helps others reproduce and fix the issue.
