"""
Watches the system clipboard and mirrors any change into Diodon's
Clipboard list — this is what makes "select text, press Ctrl+C" work
without us ever touching the Ctrl+C key ourselves.

How it works: every 700ms, read the current clipboard content and compare
to what we last saw. If it changed, someone (you, in any app) just copied
something — add it to the Clipboard list.

Why polling instead of a native "clipboard changed" event: cross-desktop
clipboard-change notifications are inconsistent across X11/Wayland/DE
combinations. Polling is unglamorous but reliably works everywhere
pyperclip works, which is the more valuable property here.
"""

import threading
import time

import pyperclip

from diodon import storage

POLL_INTERVAL_SECONDS = 0.7


class ClipboardWatcher:
    def __init__(self):
        self._last_seen: str | None = None
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        # Seed with whatever's currently in the clipboard so we don't
        # immediately re-add pre-existing clipboard content on startup.
        try:
            self._last_seen = pyperclip.paste()
        except Exception:
            self._last_seen = None

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                current = pyperclip.paste()
            except Exception:
                # Clipboard briefly unreadable (some apps lock it momentarily) — skip this cycle
                current = self._last_seen

            if current and current != self._last_seen and current.strip():
                storage.add_item("clipboard", current)
                self._last_seen = current

            time.sleep(POLL_INTERVAL_SECONDS)
