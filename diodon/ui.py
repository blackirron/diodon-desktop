"""
The popup window shown when you click the tray icon.

Built in plain Tkinter (ships with Python, zero extra install weight)
rather than a heavier GUI framework — this window's job is simple
(two lists, a few buttons per row) and doesn't need more than that.
"""

import tkinter as tk
from tkinter import font as tkfont

from diodon import storage

YELLOW = "#EAB308"
YELLOW_TINT = "#FEF9E7"
BLUE = "#2563EB"
BLUE_TINT = "#EFF6FF"
BG = "#F7F7F5"
BORDER = "#E5E7EB"
TEXT = "#111827"
MUTED = "#6B7280"


class DiodonWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.active_tab: storage.ListName = "clipboard"

        self.win = tk.Toplevel(root)
        self.win.title("Diodon")
        self.win.geometry("380x540")
        self.win.configure(bg=BG)
        # Closing the window just hides it — the app keeps running in the tray
        self.win.protocol("WM_DELETE_WINDOW", self.hide)
        self.win.withdraw()

        self.body_font = tkfont.Font(family="Helvetica", size=11)
        self.bold_font = tkfont.Font(family="Helvetica", size=11, weight="bold")
        self.small_font = tkfont.Font(family="Helvetica", size=9)

        self._build_tabs()
        self._build_quick_add()
        self._build_list_area()
        self.refresh()

    # --- window visibility (called from tray thread via root.after) ---
    def show(self):
        self.refresh()
        self.win.deiconify()
        self.win.lift()
        self.win.focus_force()

    def hide(self):
        self.win.withdraw()

    # --- layout ---
    def _build_tabs(self):
        tab_frame = tk.Frame(self.win, bg=BG)
        tab_frame.pack(fill="x", padx=14, pady=(14, 8))

        self.clip_tab_btn = tk.Button(
            tab_frame, text="Clipboard", font=self.bold_font, bd=0,
            command=lambda: self.switch_tab("clipboard"),
        )
        self.clip_tab_btn.pack(side="left", expand=True, fill="x", padx=(0, 4), ipady=6)

        self.task_tab_btn = tk.Button(
            tab_frame, text="Tasksheet", font=self.bold_font, bd=0,
            command=lambda: self.switch_tab("tasksheet"),
        )
        self.task_tab_btn.pack(side="left", expand=True, fill="x", padx=(4, 0), ipady=6)

    def _build_quick_add(self):
        add_frame = tk.Frame(self.win, bg=BG)
        add_frame.pack(fill="x", padx=14, pady=(0, 8))

        self.quick_add_entry = tk.Entry(add_frame, font=self.body_font, relief="solid", bd=1)
        self.quick_add_entry.pack(side="left", fill="x", expand=True, ipady=5)
        self.quick_add_entry.bind("<Return>", lambda e: self._quick_add())

        add_btn = tk.Button(add_frame, text="+", font=self.bold_font, width=3, command=self._quick_add)
        add_btn.pack(side="left", padx=(6, 0))

    def _quick_add(self):
        text = self.quick_add_entry.get().strip()
        if text:
            storage.add_item(self.active_tab, text)
            self.quick_add_entry.delete(0, tk.END)
            self.refresh()

    def _build_list_area(self):
        container = tk.Frame(self.win, bg=BG)
        container.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.list_frame = tk.Frame(canvas, bg=BG)

        self.list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.list_frame, anchor="nw", width=340)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas = canvas

    # --- state ---
    def switch_tab(self, tab: storage.ListName):
        self.active_tab = tab
        self.refresh()

    def refresh(self):
        accent = YELLOW if self.active_tab == "clipboard" else BLUE
        accent_tint = YELLOW_TINT if self.active_tab == "clipboard" else BLUE_TINT

        self.clip_tab_btn.configure(
            bg=YELLOW_TINT if self.active_tab == "clipboard" else BG,
            fg="#92660A" if self.active_tab == "clipboard" else MUTED,
        )
        self.task_tab_btn.configure(
            bg=BLUE_TINT if self.active_tab == "tasksheet" else BG,
            fg="#1E40AF" if self.active_tab == "tasksheet" else MUTED,
        )

        for widget in self.list_frame.winfo_children():
            widget.destroy()

        items = storage.load_items(self.active_tab)

        if not items:
            empty_label = tk.Label(
                self.list_frame,
                text="Nothing here yet." if self.active_tab == "clipboard" else "No tasks yet.",
                font=self.body_font, bg=BG, fg=MUTED, pady=30,
            )
            empty_label.pack(fill="x")
            return

        for item in items:
            self._render_item_row(item, accent)

    def _render_item_row(self, item: dict, accent: str):
        row = tk.Frame(self.list_frame, bg="white", highlightbackground=BORDER, highlightthickness=1)
        row.pack(fill="x", pady=4)

        accent_bar = tk.Frame(row, bg=accent, width=3)
        accent_bar.pack(side="left", fill="y")

        content = tk.Frame(row, bg="white")
        content.pack(side="left", fill="both", expand=True, padx=8, pady=6)

        if self.active_tab == "tasksheet":
            done = item.get("done", False)
            check_var = tk.BooleanVar(value=done)
            check = tk.Checkbutton(
                content, variable=check_var, bg="white",
                command=lambda: (storage.toggle_done("tasksheet", item["id"]), self.refresh()),
            )
            check.pack(side="left")

        text_label = tk.Label(
            content, text=item["text"], font=self.body_font, bg="white", fg=TEXT,
            wraplength=220, justify="left", anchor="w",
        )
        if self.active_tab == "tasksheet" and item.get("done"):
            text_label.configure(fg=MUTED)
        text_label.pack(side="left", fill="x", expand=True, padx=(4, 4))

        actions = tk.Frame(row, bg="white")
        actions.pack(side="right", padx=4)

        if self.active_tab == "clipboard":
            copy_btn = tk.Button(
                actions, text="⧉", bd=0, bg="white", font=self.small_font,
                command=lambda: self._copy(item["text"]),
            )
            copy_btn.pack(side="left", padx=2)

        move_btn = tk.Button(
            actions, text="⇄", bd=0, bg="white", font=self.small_font,
            command=lambda: (storage.move_item(self.active_tab, item["id"]), self.refresh()),
        )
        move_btn.pack(side="left", padx=2)

        delete_btn = tk.Button(
            actions, text="✕", bd=0, bg="white", font=self.small_font,
            command=lambda: (storage.remove_item(self.active_tab, item["id"]), self.refresh()),
        )
        delete_btn.pack(side="left", padx=2)

    def _copy(self, text: str):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
