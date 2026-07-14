"""
This is the command your Ctrl+Y GNOME keyboard shortcut will run.

Why a standalone CLI script rather than a hotkey library inside the tray app:
GNOME (and most DEs) already have a robust, correct way to bind a key
combo to run a shell command — Settings > Keyboard > Custom Shortcuts.
That mechanism is handled by the desktop environment itself and works
identically whether you're on X11 or Wayland. Reimplementing global
hotkey grabbing ourselves (e.g. with pynput) only reliably works on X11
and is one more thing that can silently break — so we let the DE do the
one job it's already good at, and we just do the capture-and-store part.

What "current selection" means here: the text you have highlighted,
even if you never explicitly pressed Ctrl+C. This is the X11 "PRIMARY"
selection. We try that first (most useful — captures what you're
looking at right now), then fall back to whatever's in the regular
clipboard if PRIMARY isn't available (e.g. some Wayland setups).
"""

import subprocess

from diodon import storage


def _try_primary_selection() -> str | None:
    """Try X11 primary selection (xclip), then Wayland primary (wl-paste)."""
    for cmd in (
        ["xclip", "-selection", "primary", "-o"],
        ["wl-paste", "--primary", "--no-newline"],
    ):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return None


def _try_clipboard_fallback() -> str | None:
    try:
        import pyperclip

        value = pyperclip.paste()
        return value if value and value.strip() else None
    except Exception:
        return None


def _notify(message: str) -> None:
    """Best-effort desktop notification. Silently skips if notify-send isn't available."""
    try:
        subprocess.run(["notify-send", "Diodon", message], timeout=2)
    except FileNotFoundError:
        pass


def capture_to_tasksheet() -> None:
    text = _try_primary_selection() or _try_clipboard_fallback()

    if not text or not text.strip():
        _notify("Nothing selected to capture")
        return

    storage.add_item("tasksheet", text)
    preview = text.strip().replace("\n", " ")[:60]
    _notify(f"Added to Tasksheet: {preview}")


if __name__ == "__main__":
    capture_to_tasksheet()
