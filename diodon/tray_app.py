"""
The tray icon (top-right of your screen) and its menu.

Note on Linux tray-icon behavior: most Linux desktops (via the
AppIndicator convention pystray uses on Linux) show a menu on click
rather than running a custom action directly — unlike Windows/Mac where
a left-click can open a window immediately. So on Linux, clicking the
icon will show a small menu with "Open Diodon" / "Quit" rather than
popping the window straight away. This is a platform convention, not a
bug — worth knowing before you go looking for why "just clicking" the
icon doesn't instantly open the window.
"""

import pystray
from PIL import Image

from diodon.icon_gen import generate_icon


def create_tray_icon(on_open, on_quit) -> pystray.Icon:
    icon_path = generate_icon()
    image = Image.open(icon_path)
    menu = pystray.Menu(
        pystray.MenuItem("Open Diodon", on_open, default=True),
        pystray.MenuItem("Quit", on_quit),
    )
    return pystray.Icon("diodon", image, "Diodon", menu)
