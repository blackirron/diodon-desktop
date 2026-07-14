"""
Generates the tray icon image. Split out from tray_app.py deliberately:
this file has zero dependency on pystray/GTK, so it can be tested and
regenerated on any machine (including headless CI) without a display
server — only the actual tray-icon *display* (tray_app.py) needs that.
"""

from pathlib import Path

from PIL import Image, ImageDraw

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
ICON_PATH = ASSETS_DIR / "icon.png"

YELLOW = (234, 179, 8)
BLUE = (37, 99, 235)


def generate_icon(force: bool = False) -> Path:
    """
    Draws a simple split-color icon (yellow top-left / blue bottom-right)
    hinting at "clipboard + tasksheet" without needing an external
    design asset. Skips regeneration if the file already exists,
    unless force=True.
    """
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    if ICON_PATH.exists() and not force:
        return ICON_PATH

    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=14, fill=(255, 255, 255, 255))
    draw.polygon([(0, 0), (size, 0), (0, size)], fill=YELLOW)
    draw.polygon([(size, 0), (size, size), (0, size)], fill=BLUE)
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=14, outline=(255, 255, 255, 255), width=2)

    img.save(ICON_PATH)
    return ICON_PATH
