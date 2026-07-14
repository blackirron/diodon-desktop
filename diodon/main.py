"""
Entrypoint for Diodon desktop.

Threading model — IMPORTANT, and the source of a real bug in an earlier
version of this file:

On Linux, pystray's tray icon uses GTK/AppIndicator under the hood, and
GTK's main loop MUST run on the actual main thread — this is a hard
requirement, not a preference. An earlier version of this file had that
backwards (Tkinter on the main thread, pystray's icon.run() pushed onto
a worker thread), which caused two main loops to fight over GTK
rendering — visible as the tray icon flickering in and out and the
panel resizing repeatedly.

The fix: pystray's icon.run() owns the main thread. Tkinter runs on a
worker thread instead. Cross-thread communication happens through a
plain thread-safe Queue rather than calling Tkinter methods directly
from the tray thread (Tkinter methods, including `.after()`, are only
safe to call from the thread that's running its mainloop).
"""

import queue
import threading
import tkinter as tk

from diodon.clipboard_watch import ClipboardWatcher
from diodon.tray_app import create_tray_icon
from diodon.ui import DiodonWindow

# Commands the tray thread posts, consumed by the Tkinter thread's poll loop
COMMAND_QUEUE: "queue.Queue[str]" = queue.Queue()


def _run_tkinter():
    root = tk.Tk()
    root.withdraw()
    window = DiodonWindow(root)

    def poll_commands():
        try:
            while True:
                cmd = COMMAND_QUEUE.get_nowait()
                if cmd == "show":
                    window.show()
                elif cmd == "quit":
                    root.destroy()
                    return  # stop polling, window is gone
        except queue.Empty:
            pass
        root.after(100, poll_commands)

    root.after(100, poll_commands)
    root.mainloop()


def main():
    watcher = ClipboardWatcher()
    watcher.start()

    tk_thread = threading.Thread(target=_run_tkinter, daemon=True)
    tk_thread.start()

    def on_open(icon, item):
        COMMAND_QUEUE.put("show")

    def on_quit(icon, item):
        watcher.stop()
        COMMAND_QUEUE.put("quit")
        icon.stop()

    icon = create_tray_icon(on_open=on_open, on_quit=on_quit)
    icon.run()  # blocks the main thread — required for the GTK backend to behave


if __name__ == "__main__":
    main()
