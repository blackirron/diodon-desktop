"""
Storage layer for Diodon desktop.

Design choice: plain JSON files in ~/.local/share/diodon/, not sqlite.
Why: this app never has more than a few hundred items, no queries beyond
"list everything" — a database is unjustified complexity here. JSON files
are trivial to inspect/debug/back up by hand too.

This file has ZERO GUI dependencies on purpose, so it can be tested
headlessly (no display server needed) and reused identically by:
- the tray app's popup window (ui.py)
- the background clipboard watcher (clipboard_watch.py)
- the CLI capture command triggered by the Ctrl+Y shortcut (capture_cli.py)
"""

import json
import time
import uuid
from pathlib import Path
from typing import Literal

DATA_DIR = Path.home() / ".local" / "share" / "diodon"
CLIPBOARD_FILE = DATA_DIR / "clipboard.json"
TASKSHEET_FILE = DATA_DIR / "tasksheet.json"

ListName = Literal["clipboard", "tasksheet"]


def _file_for(list_name: ListName) -> Path:
    return CLIPBOARD_FILE if list_name == "clipboard" else TASKSHEET_FILE


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_items(list_name: ListName) -> list[dict]:
    _ensure_data_dir()
    path = _file_for(list_name)
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        # Corrupted or unreadable file — fail safe to empty rather than crash
        return []


def save_items(list_name: ListName, items: list[dict]) -> None:
    _ensure_data_dir()
    path = _file_for(list_name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


def add_item(list_name: ListName, text: str) -> dict:
    text = text.strip()
    item = {
        "id": str(uuid.uuid4()),
        "text": text,
        "created_at": time.time(),
        "done": False,
    }
    items = load_items(list_name)
    items.insert(0, item)
    save_items(list_name, items)
    return item


def remove_item(list_name: ListName, item_id: str) -> None:
    items = load_items(list_name)
    items = [i for i in items if i["id"] != item_id]
    save_items(list_name, items)


def move_item(from_list: ListName, item_id: str) -> dict | None:
    to_list: ListName = "tasksheet" if from_list == "clipboard" else "clipboard"
    items = load_items(from_list)
    match = next((i for i in items if i["id"] == item_id), None)
    if not match:
        return None
    save_items(from_list, [i for i in items if i["id"] != item_id])
    new_item = {**match, "id": str(uuid.uuid4())}
    dest_items = load_items(to_list)
    dest_items.insert(0, new_item)
    save_items(to_list, dest_items)
    return new_item


def toggle_done(list_name: ListName, item_id: str) -> None:
    items = load_items(list_name)
    for i in items:
        if i["id"] == item_id:
            i["done"] = not i.get("done", False)
    save_items(list_name, items)
