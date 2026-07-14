# Diodon (Desktop)

A background Linux tray app: Clipboard (yellow) and Tasksheet (blue), with
items movable between the two.

## How capture works

- **Ctrl+C anywhere** → automatically mirrored into the Clipboard tab.
  No setup needed — this works the moment Diodon is running, because it
  just watches the system clipboard for changes. We deliberately do NOT
  intercept the Ctrl+C key itself, so your normal copy-paste is never at risk.
- **Ctrl+Y anywhere** → sends your current text selection to the Tasksheet
  tab. This DOES need a one-time setup step (below), because it's a real
  global hotkey, and the correct/robust way to bind one on Linux is
  through your desktop environment's own shortcut settings — not by
  having this app hook the keyboard itself (which only reliably works on
  X11, not Wayland).

## Install

```bash
chmod +x install.sh
./install.sh
```

This installs system packages (needs your sudo password once), sets up a
Python virtual environment, creates the `diodon-capture-tasksheet` command,
and registers Diodon to autostart on login.

## One manual step: the Ctrl+Y shortcut

The installer prints this at the end, but to spell it out:

1. Settings → Keyboard → View and Customize Shortcuts
2. Scroll down to **Custom Shortcuts** → click **+**
3. Name: `Diodon Capture`
4. Command: `~/.local/bin/diodon-capture-tasksheet`
5. Click the new row, press **Ctrl+Y**, confirm

This works the same way regardless of whether you're on X11 or Wayland,
since GNOME (not our app) is the one actually grabbing the key combo.

## Running it right now (without logging out)

```bash
venv/bin/python -m diodon.main &
```

Look for the tray icon (top-right of your screen, yellow/blue split
square). On most Linux desktops, a single click shows a small menu
("Open Diodon" / "Quit") rather than opening the window directly —
that's a standard Linux tray-icon convention, not a bug.

## Where your data lives

`~/.local/share/diodon/clipboard.json` and `tasksheet.json` — plain JSON,
easy to inspect, back up, or clear by hand if you ever want to.

## Troubleshooting

**Tray icon doesn't appear at all:** on stock GNOME (no extensions), tray
icons need the "AppIndicator and KStatusNotifierItem Support" GNOME Shell
extension — install it from extensions.gnome.org, since GNOME removed
built-in tray support years ago. KDE/XFCE/MATE don't need this.

**Ctrl+Y does nothing:** check the shortcut is bound to the exact path
`~/.local/bin/diodon-capture-tasksheet`, and that the file is executable
(`ls -l ~/.local/bin/diodon-capture-tasksheet` should show an `x` in the
permissions). Also confirm Diodon is actually running — the capture
command writes to the same JSON files the tray app reads, but the window
only reflects new data when you reopen/refresh it.

**Ctrl+C doesn't show up in Clipboard tab:** give it ~1 second — the
watcher polls every 700ms rather than reacting instantly, to avoid
hammering the clipboard. If it never appears, confirm Diodon is actually
running (`ps aux | grep diodon`).

## Uninstall

```bash
rm ~/.config/autostart/diodon.desktop
rm ~/.local/bin/diodon-capture-tasksheet
rm -rf ~/.local/share/diodon   # deletes your saved items too
```
(Remove the extracted project folder itself separately, whenever you like.)
