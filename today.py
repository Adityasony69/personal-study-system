"""
today.py - "Today's Topic": your daily NEW-skill lesson, progress tracker and dashboard.

Views (sidebar, or keys 1 / 2 / 3 / 4)
  Lesson      the day's lesson cards, with Done / Skip / Undo, a focus timer, Teach me and Notes
  Dashboard   streaks, time learned, activity heatmap, progress per track, your own dates
  Roadmap     every day of the roadmap, searchable and filterable; double-click a row to open it
  Notes       built-in study notes (Java, DSA in Java); any .md file you add under notes/ shows up too

Keyboard
  Left / Right  previous / next day        T  jump to today
  D  Done    S  Skip    U  Undo            L  Teach me    N  Notes
  Space  start / pause the focus timer     Ctrl+F or /  search (roadmap, or notes when open)
  1-4    switch view                       ?  show this list

Everything is logged in progress.txt (append-only history). If Notion is connected
(run notion_setup.py once), every Done/Skip/Undo is also synced there.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
import webbrowser
from datetime import date, datetime, timedelta
from pathlib import Path
from tkinter import messagebox, ttk

HERE = Path(__file__).resolve().parent
HUB = HERE.parent
sys.path.insert(0, str(HERE))
import notion_sync as ns  # noqa: E402

ROADMAP = HERE / "roadmap.json"
PROGRESS = HERE / "progress.txt"
LINKS = HERE / "notion_links.json"
SETTINGS = HERE / "settings.json"
EVENTS = HERE / "my-events.txt"
NOTES = HERE / "notes"
NOTE_GROUPS = {"java": "Java", "dsa-java": "DSA in Java"}
APP_NAME = "Today's Topic"

THEMES = {
    "dark": dict(bg="#15171c", side="#0f1115", card="#1f222a", card2="#2a2e39", fg="#eceef4", muted="#9096a5",
                 line="#343947", accent="#5b9dff", ok="#34c27a", warn="#f0a93b", bad="#e5616b", purple="#8468e8",
                 empty="#2a2e39"),
    "light": dict(bg="#f4f5f8", side="#e8eaf0", card="#ffffff", card2="#e9ecf2", fg="#1b1e26", muted="#667085",
                  line="#cfd4de", accent="#2f6fe0", ok="#1f9d5c", warn="#c67d0a", bad="#d14653", purple="#6a4fd1",
                  empty="#e1e5ec"),
}
SCALE = 1.0


def px(n):
    """Scale a pixel size for high-DPI screens."""
    return int(round(n * SCALE))


def mix(a, b, t):
    """Blend colour a towards colour b by fraction t."""
    a, b = a.lstrip("#"), b.lstrip("#")
    return "#%02x%02x%02x" % tuple(round(int(a[i:i + 2], 16) * (1 - t) + int(b[i:i + 2], 16) * t) for i in (0, 2, 4))


# ---------------------------------------------------------------- data
def load_entries():
    return json.loads(ROADMAP.read_text(encoding="utf-8"))["entries"]


def statuses():
    """date -> 'DONE' | 'SKIP' (latest action wins; UNDO clears)."""
    st = {}
    if PROGRESS.exists():
        for line in PROGRESS.read_text(encoding="utf-8").splitlines():
            if line.startswith("#"):
                continue
            p = line.split("\t")
            if len(p) >= 3:
                if p[1] == "UNDO":
                    st.pop(p[2], None)
                elif p[1] in ("DONE", "SKIP"):
                    st[p[2]] = p[1]
    return st


def log(status, entry):
    first = not PROGRESS.exists()
    with PROGRESS.open("a", encoding="utf-8") as f:
        if first:
            f.write("# logged_at\tstatus\tday\ttitle   (append-only history: DONE / SKIP / UNDO)\n")
        f.write(f"{datetime.now():%Y-%m-%d %H:%M}\t{status}\t{entry['date']}\t{entry['title']}\n")


def is_rest(e):
    return e.get("mode") == "rest"


def minutes_of(e):
    return sum(b["minutes"] for b in e["blocks"])


def track_name(e):
    p = e["phase"]
    if p.startswith("Track: "):
        return p[7:]
    return "Mini lessons" if p.startswith("Light season") else p


def load_links():
    """Topic -> Notion page URLs (made with the Notion connector, no API token needed)."""
    try:
        return json.loads(LINKS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def load_settings():
    try:
        return json.loads(SETTINGS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def load_events():
    """Upcoming dates from my-events.txt: lines like '2026-11-20  OS CA test 3'."""
    out = []
    try:
        for line in EVENTS.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\s*(\d{4}-\d{2}-\d{2})\s+(.+)$", line)
            if m:
                try:
                    out.append((date.fromisoformat(m.group(1)), m.group(2).strip()))
                except ValueError:
                    pass
    except OSError:
        pass
    return sorted(e for e in out if e[0] >= date.today())


def load_notes():
    """[(group title, [(note title, path), ...]), ...] from notes/<folder>/*.md"""
    out = []
    if NOTES.is_dir():
        known = list(NOTE_GROUPS)
        folders = [d for d in NOTES.iterdir() if d.is_dir()]
        for folder in sorted(folders, key=lambda d: (known.index(d.name) if d.name in known else 99, d.name)):
            items = []
            for path in sorted(folder.glob("*.md")):
                title = path.stem
                try:
                    first = path.read_text(encoding="utf-8").lstrip().splitlines()[0]
                    if first.startswith("# "):
                        title = first[2:].strip()
                except (OSError, IndexError):
                    pass
                items.append((title, path))
            if items:
                out.append((NOTE_GROUPS.get(folder.name, folder.name.replace("-", " ").title()), items))
    return out


def open_notion(url):
    """Open in the Notion desktop app; fall back to the browser."""
    try:
        os.startfile(ns.desktop_url(url))
    except OSError:
        webbrowser.open(url)


def fmt_minutes(m):
    return f"{m // 60}h {m % 60:02d}m" if m >= 60 else f"{m}m"


# ---------------------------------------------------------------- widgets
def rounded(cv, x1, y1, x2, y2, r, **kw):
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return cv.create_polygon(pts, smooth=True, **kw)


class RButton(tk.Canvas):
    """Rounded button with a hover colour."""

    def __init__(self, parent, text, command, bg, fg="#ffffff", size=10, bold=True, padx=14, pady=7, radius=9):
        font = ("Segoe UI Semibold" if bold else "Segoe UI", size)
        f = tkfont.Font(font=font)
        w, h = f.measure(text) + 2 * px(padx), f.metrics("linespace") + 2 * px(pady)
        super().__init__(parent, width=w, height=h, bg=parent["bg"], highlightthickness=0, bd=0, cursor="hand2")
        hover = mix(bg, fg, 0.16)
        shape = rounded(self, 1, 1, w - 1, h - 1, px(radius), fill=bg, outline="")
        self.create_text(w / 2, h / 2, text=text, fill=fg, font=font)
        self.bind("<Enter>", lambda e: self.itemconfigure(shape, fill=hover))
        self.bind("<Leave>", lambda e: self.itemconfigure(shape, fill=bg))
        self.bind("<ButtonRelease-1>", lambda e: command())


class Card(tk.Canvas):
    """Rounded panel; put content in .body. Height follows the content."""

    def __init__(self, parent, fill, pad=16, radius=14):
        # start tall enough for the body to be on screen, or Tk never maps it and never reports its size
        super().__init__(parent, width=10, height=2 * px(pad) + px(8), bg=parent["bg"], highlightthickness=0, bd=0)
        self.fill, self.pad, self.r = fill, px(pad), px(radius)
        self.body = tk.Frame(self, bg=fill)
        self.win = self.create_window(self.pad, self.pad, window=self.body, anchor="nw")
        self.bind("<Configure>", self._size)
        self.body.bind("<Configure>", self._fit)

    def _size(self, e):
        self.itemconfigure(self.win, width=max(10, e.width - 2 * self.pad))
        self._draw()

    def _fit(self, _e):
        self.configure(height=self.body.winfo_reqheight() + 2 * self.pad)
        self._draw()

    def _draw(self):
        self.delete("bg")
        w, h = self.winfo_width(), self.body.winfo_reqheight() + 2 * self.pad
        if w > 4:
            rounded(self, 0, 0, w, h, self.r, fill=self.fill, outline="", tags="bg")
            self.tag_lower("bg")


class Bar(tk.Canvas):
    """Thin rounded progress bar."""

    def __init__(self, parent, frac, fill, track, height=6):
        super().__init__(parent, width=10, height=px(height), bg=parent["bg"], highlightthickness=0, bd=0)
        self.frac, self.fill, self.track = frac, fill, track
        self.bind("<Configure>", lambda e: self.draw())

    def set(self, frac):
        self.frac = frac
        self.draw()

    def draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 4:
            return
        rounded(self, 0, 0, w, h, h / 2, fill=self.track, outline="")
        if self.frac > 0:
            rounded(self, 0, 0, max(h, w * min(1.0, self.frac)), h, h / 2, fill=self.fill, outline="")


class Scroll(tk.Frame):
    """Vertically scrolling area; put content in .inner."""

    def __init__(self, parent, bg):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        sb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview, style="App.Vertical.TScrollbar")
        self.inner = tk.Frame(self.canvas, bg=bg)
        win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(win, width=e.width))
        self.canvas.configure(yscrollcommand=sb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def wheel(self, e):
        if self.inner.winfo_reqheight() > self.canvas.winfo_height():
            self.canvas.yview_scroll(int(-e.delta / 120), "units")


def wlabel(parent, **kw):
    """Label that re-wraps to its own width. Pack it with fill='x'."""
    lab = tk.Label(parent, justify="left", anchor="w", **kw)
    lab.bind("<Configure>", lambda e: lab.configure(wraplength=max(60, e.width - 4)))
    return lab


def title_bar(root, dark):
    """Match the Windows title bar to the theme."""
    try:
        import ctypes
        root.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        val = ctypes.c_int(1 if dark else 0)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(val), ctypes.sizeof(val))
    except Exception:
        pass


# ---------------------------------------------------------------- app
class App:
    def __init__(self, root):
        self.root = root
        self.settings = load_settings()
        self.theme = self.settings.get("theme", "dark") if self.settings.get("theme") in THEMES else "dark"
        self.entries = load_entries()
        self.by_date = {e["date"]: i for i, e in enumerate(self.entries)}
        self.view = "today"
        self.idx = self.default_index()
        self.timer = dict(total=0, left=0, end=0, running=False, label="")
        self.search_text, self.f_track, self.f_status = "", "All tracks", "All"
        self.note_path, self.note_query, self.note_tree = None, "", None
        self.scroll = self.tree = self.sync_label = None
        self.sync_msg = ("Notion: notes + progress sync on" if ns.ready()
                         else "Notes open in Notion · progress is saved in progress.txt")
        root.title(APP_NAME)
        w = min(px(1180), root.winfo_screenwidth() - 80)
        h = min(px(720), root.winfo_screenheight() - 120)
        root.geometry(f"{w}x{h}")
        root.minsize(min(w, px(860)), min(h, px(540)))
        root.bind_all("<Key>", self.on_key)
        root.bind_all("<MouseWheel>", self.on_wheel)
        self.render()
        self.tick()
        self.poll_sync()

    # ---------- data helpers ----------
    def today_s(self):
        return date.today().isoformat()

    def pending(self):
        st, t = statuses(), self.today_s()
        return [e for e in self.entries if e["date"] <= t and e["date"] not in st and not is_rest(e)]

    def default_index(self):
        p = self.pending()
        if p:
            return self.by_date[p[0]["date"]]
        return self.today_index()

    def today_index(self):
        t = self.today_s()
        return next((i for i, e in enumerate(self.entries) if e["date"] >= t), len(self.entries) - 1)

    def compute(self):
        st, t = statuses(), self.today_s()
        monday = (date.today() - timedelta(days=date.today().weekday())).isoformat()
        done = skipped = minutes = missed = best = run = week = 0
        tracks = {}
        for e in self.entries:
            if is_rest(e):
                continue
            tr = tracks.setdefault(track_name(e), [0, 0])
            tr[1] += 1
            s = st.get(e["date"])
            if s == "DONE":
                done += 1
                tr[0] += 1
                minutes += minutes_of(e)
                week += monday <= e["date"] <= t
            elif s == "SKIP":
                skipped += 1
            if e["date"] <= t:
                if s == "DONE":
                    run += 1
                    best = max(best, run)
                elif s == "SKIP" or e["date"] < t:
                    run = 0
                    missed += not s
        streak, d = 0, date.today()
        if d.isoformat() not in st:
            d -= timedelta(days=1)  # today not finished yet doesn't break the streak
        while d.isoformat() in self.by_date:
            e = self.entries[self.by_date[d.isoformat()]]
            if not is_rest(e):
                if st.get(d.isoformat()) != "DONE":
                    break
                streak += 1
            d -= timedelta(days=1)
        return dict(st=st, done=done, skipped=skipped, minutes=minutes, missed=missed, best=max(best, streak),
                    streak=streak, week=week, tracks=tracks, total=sum(v[1] for v in tracks.values()))

    def status_of(self, e, st):
        """(text, colour key) for a day."""
        s, t = st.get(e["date"]), self.today_s()
        if s == "DONE":
            return "Done", "ok"
        if s == "SKIP":
            return "Skipped", "warn"
        if is_rest(e):
            return "Rest", "muted"
        if e["date"] == t:
            return "Today", "accent"
        return ("Missed", "bad") if e["date"] < t else ("Upcoming", "muted")

    # ---------- frame ----------
    def render(self):
        for w in self.root.winfo_children():
            w.destroy()
        T = self.T = THEMES[self.theme]
        self.root.configure(bg=T["bg"])
        self.style()
        self.S = self.compute()
        self.scroll = self.tree = self.sync_label = self.note_tree = None
        side = tk.Frame(self.root, bg=T["side"], width=px(224))
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        self.build_side(side)
        main = tk.Frame(self.root, bg=T["bg"])
        main.pack(side="left", fill="both", expand=True)
        {"today": self.view_today, "dash": self.view_dash, "roadmap": self.view_roadmap,
         "notes": self.view_notes}[self.view](main)
        title_bar(self.root, self.theme == "dark")

    def style(self):
        T, s = self.T, ttk.Style(self.root)
        s.theme_use("clam")
        s.configure("App.Vertical.TScrollbar", background=T["card2"], troughcolor=T["bg"], bordercolor=T["bg"],
                    lightcolor=T["card2"], darkcolor=T["card2"], arrowcolor=T["muted"], gripcount=0, relief="flat")
        s.map("App.Vertical.TScrollbar", background=[("active", T["line"])])
        s.configure("App.Horizontal.TScrollbar", background=T["card2"], troughcolor=T["bg"], bordercolor=T["bg"],
                    lightcolor=T["card2"], darkcolor=T["card2"], arrowcolor=T["muted"], gripcount=0, relief="flat")
        s.map("App.Horizontal.TScrollbar", background=[("active", T["line"])])
        s.layout("App.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
        s.configure("App.Treeview", background=T["card"], fieldbackground=T["card"], foreground=T["fg"],
                    rowheight=px(30), borderwidth=0, font=("Segoe UI", 10))
        s.map("App.Treeview", background=[("selected", T["accent"])], foreground=[("selected", "#ffffff")])
        s.configure("App.Treeview.Heading", background=T["card2"], foreground=T["muted"], relief="flat",
                    borderwidth=0, font=("Segoe UI Semibold", 9), padding=(8, 6))
        s.map("App.Treeview.Heading", background=[("active", T["card2"])])

    def build_side(self, side):
        T, S, bg = self.T, self.S, self.T["side"]
        pad = px(18)
        tk.Label(side, text=APP_NAME, bg=bg, fg=T["fg"], font=("Segoe UI Semibold", 14)).pack(
            anchor="w", padx=pad, pady=(px(18), 0))
        tk.Label(side, text="Daily learning companion", bg=bg, fg=T["muted"], font=("Segoe UI", 9)).pack(
            anchor="w", padx=pad, pady=(0, px(14)))
        for key, text, hint in (("today", "Lesson", "1"), ("dash", "Dashboard", "2"), ("roadmap", "Roadmap", "3"),
                                ("notes", "Notes", "4")):
            active = key == self.view
            rbg = T["card2"] if active else bg
            row = tk.Frame(side, bg=rbg, cursor="hand2")
            row.pack(fill="x", padx=px(10), pady=1)
            strip = tk.Frame(row, bg=T["accent"] if active else rbg, width=px(3))
            strip.pack(side="left", fill="y")
            a = tk.Label(row, text=text, bg=rbg, fg=T["fg"] if active else T["muted"], pady=px(7), padx=px(10),
                         font=("Segoe UI Semibold" if active else "Segoe UI", 10), cursor="hand2")
            a.pack(side="left")
            b = tk.Label(row, text=hint, bg=rbg, fg=T["muted"], font=("Segoe UI", 8), padx=px(10), cursor="hand2")
            b.pack(side="right")
            for wdg in (row, a, b, strip):
                wdg.bind("<Button-1>", lambda e, k=key: self.set_view(k))

        bottom = tk.Frame(side, bg=bg)
        bottom.pack(side="bottom", fill="x", pady=px(12))
        for text, cmd in (("Learning Hub", self.open_hub), ("Progress log", self.open_progress),
                          ("Roadmap file", lambda: os.startfile(HERE / "roadmap.txt")),
                          ("Light mode" if self.theme == "dark" else "Dark mode", self.toggle_theme),
                          ("Shortcuts  ( ? )", self.show_keys)):
            lk = tk.Label(bottom, text=text, bg=bg, fg=T["muted"], font=("Segoe UI", 9), cursor="hand2", anchor="w")
            lk.pack(fill="x", padx=pad, pady=px(2))
            lk.bind("<Button-1>", lambda e, c=cmd: c())
            lk.bind("<Enter>", lambda e, w=lk: w.configure(fg=T["fg"]))
            lk.bind("<Leave>", lambda e, w=lk: w.configure(fg=T["muted"]))

        box = tk.Frame(side, bg=bg)
        box.pack(fill="x", padx=pad, pady=(px(20), 0))
        num = tk.Frame(box, bg=bg)
        num.pack(fill="x")
        tk.Label(num, text=str(S["streak"]), bg=bg, fg=T["warn"] if S["streak"] else T["muted"],
                 font=("Segoe UI Semibold", 26)).pack(side="left")
        tk.Label(num, text="day streak", bg=bg, fg=T["muted"], font=("Segoe UI", 9)).pack(
            side="left", padx=px(8), pady=(px(12), 0))
        frac = S["done"] / S["total"] if S["total"] else 0
        Bar(box, frac, T["ok"], T["empty"]).pack(fill="x", pady=(px(6), px(4)))
        tk.Label(box, text=f"{S['done']} of {S['total']} lessons · {frac:.0%}", bg=bg, fg=T["muted"],
                 font=("Segoe UI", 9)).pack(anchor="w")

        tp = tk.Frame(side, bg=bg)
        tp.pack(fill="x", padx=pad, pady=(px(22), 0))
        tk.Label(tp, text="FOCUS TIMER", bg=bg, fg=T["muted"], font=("Segoe UI Semibold", 8)).pack(anchor="w")
        self.timer_time = tk.Label(tp, text="--:--", bg=bg, fg=T["fg"], font=("Segoe UI Semibold", 22))
        self.timer_time.pack(anchor="w")
        self.timer_bar = Bar(tp, 0, T["accent"], T["empty"], height=5)
        self.timer_bar.pack(fill="x", pady=(px(2), px(6)))
        self.timer_name = wlabel(tp, text="", bg=bg, fg=T["muted"], font=("Segoe UI", 9))
        self.timer_name.pack(fill="x")
        self.timer_row = tk.Frame(tp, bg=bg)
        self.timer_row.pack(fill="x", pady=(px(8), 0))
        self.timer_buttons()
        self.update_timer_ui()

    # ---------- lesson view ----------
    def view_today(self, main):
        T, S = self.T, self.S
        st, t, P = S["st"], self.today_s(), px(26)
        e = self.entries[self.idx]
        s = st.get(e["date"])
        d = date.fromisoformat(e["date"])

        head = tk.Frame(main, bg=T["bg"])
        head.pack(fill="x", padx=P, pady=(px(18), px(8)))
        tk.Label(head, text=f"{d:%A, %d %B %Y}", bg=T["bg"], fg=T["fg"], font=("Segoe UI Semibold", 12)).pack(side="left")
        rel = "Today" if e["date"] == t else ("Upcoming" if e["date"] > t else "Past day")
        tk.Label(head, text=rel, bg=T["bg"], fg=T["accent"] if e["date"] == t else T["muted"],
                 font=("Segoe UI", 10)).pack(side="left", padx=px(10))
        for text, cmd in (("Next ▶", lambda: self.go(1)), ("Today", self.go_today), ("◀ Prev", lambda: self.go(-1))):
            RButton(head, text, cmd, T["card2"], T["fg"], size=9, bold=False, padx=11, pady=5).pack(
                side="right", padx=(px(6), 0))
        self.week_strip(main, d, st, P)

        sc = self.scroll = Scroll(main, T["bg"])
        sc.pack(fill="both", expand=True)
        f = sc.inner
        side_pad = (P, px(12))

        text, key = self.status_of(e, st)
        if text == "Today":
            text = "Pending"
        line = tk.Frame(f, bg=T["bg"])
        line.pack(fill="x", padx=side_pad, pady=(px(4), 0))
        self.pill(line, text, T[key]).pack(side="left")
        same = [x for x in self.entries if x["phase"] == e["phase"] and not is_rest(x)]
        if not is_rest(e) and e in same:
            tk.Label(line, text=f"{track_name(e)}  ·  day {same.index(e) + 1} of {len(same)}", bg=T["bg"],
                     fg=T["accent"], font=("Segoe UI", 10)).pack(side="left", padx=px(10))

        wlabel(f, text=e["title"], bg=T["bg"], fg=T["fg"], font=("Segoe UI Semibold", 20)).pack(
            fill="x", padx=side_pad, pady=(px(8), 0))
        wlabel(f, text=f"{minutes_of(e)} min  ·  {e['why']}", bg=T["bg"], fg=T["muted"], font=("Segoe UI", 10)).pack(
            fill="x", padx=side_pad, pady=(px(2), px(10)))

        behind = len([p for p in self.pending() if p["date"] < t])
        if behind:
            tint = mix(T["warn"], T["bg"], 0.86)
            c = Card(f, tint, pad=12, radius=12)
            c.pack(fill="x", padx=side_pad, pady=(0, px(8)))
            RButton(c.body, "Skip all missed", self.skip_missed, T["warn"], T["bg"], size=9, padx=10, pady=5).pack(side="right")
            wlabel(c.body, text=f"{behind} missed day(s) are waiting. Do them, skip them one by one, or skip them all.",
                   bg=tint, fg=T["warn"], font=("Segoe UI", 10)).pack(side="left", fill="x", expand=True)

        for b in e["blocks"]:
            c = Card(f, T["card"])
            c.pack(fill="x", padx=side_pad, pady=px(6))
            top = tk.Frame(c.body, bg=T["card"])
            top.pack(fill="x")
            self.pill(top, f"{b['minutes']} min", T["accent"]).pack(side="left")
            if not is_rest(e):
                RButton(top, "Notes", lambda b=b: self.open_notes(e, b), T["card2"], T["fg"], size=9, padx=11,
                        pady=5).pack(side="right")
                RButton(top, "Teach me", lambda b=b: self.teach(e, b), T["purple"], size=9, padx=11, pady=5).pack(
                    side="right", padx=px(6))
                RButton(top, "Start timer", lambda b=b: self.start_timer(b), T["accent"], size=9, padx=11,
                        pady=5).pack(side="right")
            wlabel(c.body, text=b["label"], bg=T["card"], fg=T["fg"], font=("Segoe UI Semibold", 13)).pack(
                fill="x", pady=(px(10), 0))
            for cap, val in (("UNDERSTAND", b.get("learn")), ("DO", b.get("task")), ("DONE WHEN", b.get("done_when"))):
                if val:
                    tk.Label(c.body, text=cap, bg=T["card"], fg=T["muted"], font=("Segoe UI Semibold", 8)).pack(
                        anchor="w", pady=(px(10), 0))
                    wlabel(c.body, text=val, bg=T["card"], fg=T["fg"], font=("Segoe UI", 10)).pack(fill="x")

        row = tk.Frame(f, bg=T["bg"])
        row.pack(fill="x", padx=side_pad, pady=(px(14), px(6)))
        if e["date"] <= t and not is_rest(e) and not s:
            RButton(row, "Done ✓", lambda: self.mark("DONE", e), T["ok"], padx=22).pack(side="left", padx=(0, px(8)))
            RButton(row, "Skip", lambda: self.mark("SKIP", e), T["card2"], T["fg"]).pack(side="left", padx=(0, px(8)))
        if s:
            RButton(row, "Undo", lambda: self.mark("UNDO", e), T["card2"], T["warn"]).pack(side="left")
        self.sync_label = tk.Label(f, text=self.sync_msg, bg=T["bg"], fg=T["muted"], font=("Segoe UI", 9))
        self.sync_label.pack(anchor="w", padx=side_pad, pady=(px(4), px(18)))

    def pill(self, parent, text, col):
        return tk.Label(parent, text=text, bg=mix(col, parent["bg"], 0.82), fg=col, font=("Segoe UI Semibold", 9),
                        padx=px(8), pady=px(2))

    def week_strip(self, parent, d, st, P):
        T = self.T
        row = tk.Frame(parent, bg=T["bg"])
        row.pack(fill="x", padx=P, pady=(0, px(10)))
        monday = d - timedelta(days=d.weekday())
        for i in range(7):
            day = monday + timedelta(days=i)
            j = self.by_date.get(day.isoformat())
            bg, fg = T["bg"], T["muted"]
            if j is not None:
                _, key = self.status_of(self.entries[j], st)
                if key == "muted":
                    bg, fg = (T["bg"], T["muted"]) if is_rest(self.entries[j]) else (T["card2"], T["fg"])
                else:
                    bg, fg = mix(T[key], T["bg"], 0.8), T[key]
            cell = tk.Label(row, text=f"{day:%a}\n{day.day}", width=6, bg=bg, fg=fg, font=("Segoe UI", 9), pady=px(4),
                            highlightthickness=2, highlightbackground=T["fg"] if day == d else T["bg"])
            cell.pack(side="left", padx=(0, px(6)))
            if j is not None:
                cell.configure(cursor="hand2")
                cell.bind("<Button-1>", lambda ev, j=j: self.jump(j))

    # ---------- dashboard ----------
    def view_dash(self, main):
        T, S, P = self.T, self.S, px(26)
        sc = self.scroll = Scroll(main, T["bg"])
        sc.pack(fill="both", expand=True)
        f = sc.inner
        side_pad = (P, px(12))
        tk.Label(f, text="Dashboard", bg=T["bg"], fg=T["fg"], font=("Segoe UI Semibold", 20)).pack(
            anchor="w", padx=side_pad, pady=(px(18), 0))
        sub = f"{S['done']} of {S['total']} lessons done"
        if S["missed"]:
            sub += f"  ·  {S['missed']} missed day(s) waiting"
        tk.Label(f, text=sub, bg=T["bg"], fg=T["muted"], font=("Segoe UI", 10)).pack(anchor="w", padx=side_pad)

        grid = tk.Frame(f, bg=T["bg"])
        grid.pack(fill="x", padx=side_pad, pady=(px(14), 0))
        tiles = (("Current streak", str(S["streak"]), "days in a row", T["warn"]),
                 ("Best streak", str(S["best"]), "days", T["fg"]),
                 ("Lessons done", str(S["done"]), f"{S['skipped']} skipped", T["ok"]),
                 ("Time learned", fmt_minutes(S["minutes"]), f"{S['week']} lesson(s) this week", T["accent"]))
        for i, (cap, big, small, col) in enumerate(tiles):
            grid.columnconfigure(i, weight=1, uniform="tile")
            c = Card(grid, T["card"], pad=14)
            c.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else px(10), 0))
            tk.Label(c.body, text=cap, bg=T["card"], fg=T["muted"], font=("Segoe UI", 9)).pack(anchor="w")
            tk.Label(c.body, text=big, bg=T["card"], fg=col, font=("Segoe UI Semibold", 22)).pack(anchor="w")
            tk.Label(c.body, text=small, bg=T["card"], fg=T["muted"], font=("Segoe UI", 9)).pack(anchor="w")

        c = Card(f, T["card"])
        c.pack(fill="x", padx=side_pad, pady=(px(12), 0))
        top = tk.Frame(c.body, bg=T["card"])
        top.pack(fill="x")
        tk.Label(top, text="Activity", bg=T["card"], fg=T["fg"], font=("Segoe UI Semibold", 12)).pack(side="left")
        self.heat_label = tk.Label(top, text="Hover a day, click to open it", bg=T["card"], fg=T["muted"],
                                   font=("Segoe UI", 9))
        self.heat_label.pack(side="right")
        cell, gap = px(15), px(4)
        cv = tk.Canvas(c.body, width=10, height=px(22) + 7 * (cell + gap), bg=T["card"], highlightthickness=0, bd=0)
        cv.pack(fill="x", pady=(px(10), px(4)))
        cv.bind("<Configure>", lambda ev: self.draw_heat(cv))
        cv.bind("<Motion>", lambda ev: self.heat_hover(cv))
        cv.bind("<Leave>", lambda ev: self.heat_label.configure(text="Hover a day, click to open it"))
        cv.bind("<Button-1>", lambda ev: self.heat_click(cv))
        legend = tk.Frame(c.body, bg=T["card"])
        legend.pack(anchor="w")
        for name, col in (("Done", T["ok"]), ("Skipped", T["warn"]), ("Missed", T["bad"]), ("Upcoming", T["empty"])):
            tk.Frame(legend, bg=col, width=px(11), height=px(11)).pack(side="left")
            tk.Label(legend, text=name, bg=T["card"], fg=T["muted"], font=("Segoe UI", 9)).pack(
                side="left", padx=(px(5), px(14)))

        c = Card(f, T["card"])
        c.pack(fill="x", padx=side_pad, pady=(px(12), 0))
        tk.Label(c.body, text="Tracks", bg=T["card"], fg=T["fg"], font=("Segoe UI Semibold", 12)).pack(anchor="w")
        g = tk.Frame(c.body, bg=T["card"])
        g.pack(fill="x", pady=(px(8), 0))
        g.columnconfigure(1, weight=1)
        now_track = track_name(self.entries[self.default_index()])
        for r, (name, (dn, tot)) in enumerate(S["tracks"].items()):
            cur = name == now_track
            tk.Label(g, text=name + ("   now" if cur else ""), bg=T["card"], fg=T["fg"] if cur or dn else T["muted"],
                     font=("Segoe UI Semibold" if cur else "Segoe UI", 10), anchor="w", width=22).grid(
                row=r, column=0, sticky="w", pady=px(5))
            Bar(g, dn / tot if tot else 0, T["ok"] if dn == tot else T["accent"], T["empty"], height=7).grid(
                row=r, column=1, sticky="ew", padx=px(10))
            tk.Label(g, text=f"{dn} / {tot}", bg=T["card"], fg=T["muted"], font=("Segoe UI", 9), anchor="e",
                     width=9).grid(row=r, column=2, sticky="e")

        events = load_events()
        c = Card(f, T["card"])
        c.pack(fill="x", padx=side_pad, pady=(px(12), px(20)))
        tk.Label(c.body, text="Your dates", bg=T["card"], fg=T["fg"], font=("Segoe UI Semibold", 12)).pack(anchor="w")
        if not events:
            lk = tk.Label(c.body, text="No upcoming dates. Add exam or CA dates to my-events.txt (click to open).",
                          bg=T["card"], fg=T["muted"], font=("Segoe UI", 10), cursor="hand2")
            lk.pack(anchor="w", pady=(px(6), 0))
            lk.bind("<Button-1>", lambda ev: os.startfile(EVENTS) if EVENTS.exists() else None)
        for when, name in events[:8]:
            left = (when - date.today()).days
            r = tk.Frame(c.body, bg=T["card"])
            r.pack(fill="x", pady=(px(6), 0))
            tk.Label(r, text=f"{when:%a %d %b}", bg=T["card"], fg=T["muted"], font=("Segoe UI", 10), width=12,
                     anchor="w").pack(side="left")
            tk.Label(r, text=name, bg=T["card"], fg=T["fg"], font=("Segoe UI", 10)).pack(side="left")
            tk.Label(r, text="today" if left == 0 else f"in {left} day(s)", bg=T["card"],
                     fg=T["warn"] if left <= 7 else T["muted"], font=("Segoe UI", 9)).pack(side="right")

    def draw_heat(self, cv):
        T, st, t = self.T, self.S["st"], self.today_s()
        cv.delete("all")
        self.heat_items = {}
        cell, gap, left, top = px(15), px(4), px(36), px(22)
        weeks = max(4, (cv.winfo_width() - left) // (cell + gap))
        first = date.fromisoformat(self.entries[0]["date"])
        s = max(first, date.today() - timedelta(weeks=min(10, weeks // 3)))
        start = s - timedelta(days=s.weekday())
        for r, name in ((0, "Mon"), (2, "Wed"), (4, "Fri"), (6, "Sun")):
            cv.create_text(0, top + r * (cell + gap) + cell / 2, text=name, anchor="w", fill=T["muted"],
                           font=("Segoe UI", 8))
        month = None
        for c in range(weeks):
            x = left + c * (cell + gap)
            monday = start + timedelta(weeks=c)
            if monday.month != month:
                month = monday.month
                cv.create_text(x, 0, text=f"{monday:%b}", anchor="nw", fill=T["muted"], font=("Segoe UI", 8))
            for r in range(7):
                iso = (monday + timedelta(days=r)).isoformat()
                j = self.by_date.get(iso)
                if j is None:
                    continue
                e, y = self.entries[j], top + r * (cell + gap)
                _, key = self.status_of(e, st)
                fill = mix(T["empty"], T["card"], 0.6) if is_rest(e) and key == "muted" else (
                    T["empty"] if key in ("muted", "accent") else T[key])
                item = rounded(cv, x, y, x + cell, y + cell, px(4), fill=fill,
                               outline=T["fg"] if iso == t else "", width=2)
                self.heat_items[item] = j

    def heat_hit(self, cv):
        cur = cv.find_withtag("current")
        return self.heat_items.get(cur[0]) if cur else None

    def heat_hover(self, cv):
        j = self.heat_hit(cv)
        cv.configure(cursor="hand2" if j is not None else "")
        if j is not None:
            e = self.entries[j]
            self.heat_label.configure(
                text=f"{date.fromisoformat(e['date']):%a %d %b %Y}  ·  {self.status_of(e, self.S['st'])[0]}  ·  "
                     f"{e['title'][:60]}")

    def heat_click(self, cv):
        j = self.heat_hit(cv)
        if j is not None:
            self.jump(j)

    # ---------- roadmap browser ----------
    def view_roadmap(self, main):
        T, S, P = self.T, self.S, px(26)
        tk.Label(main, text="Roadmap", bg=T["bg"], fg=T["fg"], font=("Segoe UI Semibold", 20)).pack(
            anchor="w", padx=P, pady=(px(18), 0))
        bar = tk.Frame(main, bg=T["bg"])
        bar.pack(fill="x", padx=P, pady=(px(10), px(10)))
        tk.Label(bar, text="Search", bg=T["bg"], fg=T["muted"], font=("Segoe UI", 10)).pack(side="left")
        self.search_var = tk.StringVar(value=self.search_text)
        self.search_entry = tk.Entry(bar, textvariable=self.search_var, bg=T["card"], fg=T["fg"], width=28,
                                     insertbackground=T["fg"], relief="flat", font=("Segoe UI", 10),
                                     highlightthickness=1, highlightbackground=T["line"], highlightcolor=T["accent"])
        self.search_entry.pack(side="left", padx=px(8), ipady=px(4))
        self.search_var.trace_add("write", lambda *a: self.fill_tree())
        self.track_var = tk.StringVar(value=self.f_track)
        self.status_var = tk.StringVar(value=self.f_status)
        for var, vals in ((self.track_var, ["All tracks"] + list(S["tracks"])),
                          (self.status_var, ["All", "Pending", "Done", "Skipped", "Upcoming"])):
            mb = tk.Menubutton(bar, text=var.get() + "  ▾", bg=T["card2"], fg=T["fg"], activebackground=T["line"],
                               activeforeground=T["fg"], relief="flat", bd=0, highlightthickness=0,
                               font=("Segoe UI", 10), padx=px(12), pady=px(5), cursor="hand2")
            menu = tk.Menu(mb, tearoff=0, bg=T["card"], fg=T["fg"], activebackground=T["accent"],
                           activeforeground="#ffffff", bd=0, font=("Segoe UI", 10))
            for val in vals:
                menu.add_command(label=val, command=lambda v=val, var=var, mb=mb: (
                    var.set(v), mb.configure(text=v + "  ▾"), self.fill_tree()))
            mb.configure(menu=menu)
            mb.pack(side="left", padx=(0, px(8)))
        self.count_label = tk.Label(bar, text="", bg=T["bg"], fg=T["muted"], font=("Segoe UI", 9))
        self.count_label.pack(side="right")

        tk.Label(main, text="Double-click a row, or select it and press Enter, to open that day.", bg=T["bg"],
                 fg=T["muted"], font=("Segoe UI", 9)).pack(side="bottom", anchor="w", padx=P, pady=(px(6), px(12)))
        wrap = tk.Frame(main, bg=T["bg"])
        wrap.pack(fill="both", expand=True, padx=(P, px(12)))
        cols = (("date", "Date", 130, "w"), ("track", "Track", 150, "w"), ("title", "Lesson", 380, "w"),
                ("min", "Min", 56, "e"), ("status", "Status", 96, "w"))
        tree = self.tree = ttk.Treeview(wrap, columns=[c[0] for c in cols], show="headings", style="App.Treeview",
                                        selectmode="browse")
        for cid, text, width, anchor in cols:
            tree.heading(cid, text=text, anchor=anchor)
            tree.column(cid, width=px(width), minwidth=px(50), anchor=anchor, stretch=cid == "title")
        for key in ("ok", "warn", "bad", "accent", "muted"):
            tree.tag_configure(key, foreground=T[key])
        vs = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview, style="App.Vertical.TScrollbar")
        tree.configure(yscrollcommand=vs.set)
        tree.pack(side="left", fill="both", expand=True)
        vs.pack(side="right", fill="y")
        tree.bind("<Double-1>", self.tree_open)
        tree.bind("<Return>", self.tree_open)
        self.fill_tree()

    def fill_tree(self):
        tree = self.tree
        if tree is None or not tree.winfo_exists():
            return
        self.search_text = q = self.search_var.get().strip()
        self.f_track, self.f_status = self.track_var.get(), self.status_var.get()
        q, st = q.lower(), self.S["st"]
        want = {"Pending": ("Today", "Missed"), "Done": ("Done",), "Skipped": ("Skipped",),
                "Upcoming": ("Upcoming",)}.get(self.f_status)
        tree.delete(*tree.get_children())
        shown = 0
        for i, e in enumerate(self.entries):
            text, key = self.status_of(e, st)
            if want and text not in want:
                continue
            if self.f_track != "All tracks" and (track_name(e) != self.f_track or is_rest(e)):
                continue
            d = date.fromisoformat(e["date"])
            when = f"{d:%a %d %b %Y}"
            if q:
                hay = " ".join([when, e["date"], e["title"], e["phase"]] + [
                    f"{b.get('learn', '')} {b.get('task', '')}" for b in e["blocks"]]).lower()
                if not all(word in hay for word in q.split()):
                    continue
            tree.insert("", "end", iid=str(i), tags=(key,),
                        values=(when, track_name(e), e["title"], minutes_of(e) or "", text))
            shown += 1
        self.count_label.configure(text=f"{shown} of {len(self.entries)} days")
        if tree.exists(str(self.idx)):
            tree.selection_set(str(self.idx))
            tree.see(str(self.idx))

    def tree_open(self, _ev=None):
        sel = self.tree.selection()
        if sel:
            self.jump(int(sel[0]))

    # ---------- notes library ----------
    def view_notes(self, main):
        T, P = self.T, px(26)
        head = tk.Frame(main, bg=T["bg"])
        head.pack(fill="x", padx=P, pady=(px(18), px(10)))
        tk.Label(head, text="Notes", bg=T["bg"], fg=T["fg"], font=("Segoe UI Semibold", 20)).pack(side="left")
        RButton(head, "Open file", self.open_note_file, T["card2"], T["fg"], size=9, bold=False, padx=11, pady=5).pack(
            side="right")
        self.note_var = tk.StringVar(value=self.note_query)
        self.search_entry = tk.Entry(head, textvariable=self.note_var, bg=T["card"], fg=T["fg"], width=24,
                                     insertbackground=T["fg"], relief="flat", font=("Segoe UI", 10),
                                     highlightthickness=1, highlightbackground=T["line"], highlightcolor=T["accent"])
        self.search_entry.pack(side="right", padx=px(10), ipady=px(4))
        tk.Label(head, text="Search", bg=T["bg"], fg=T["muted"], font=("Segoe UI", 10)).pack(side="right")
        self.note_var.trace_add("write", lambda *a: self.fill_notes())

        body = tk.Frame(main, bg=T["bg"])
        body.pack(fill="both", expand=True, padx=(P, px(12)), pady=(0, px(14)))
        left = tk.Frame(body, bg=T["card"], width=px(290))
        left.pack(side="left", fill="y", padx=(0, px(12)))
        left.pack_propagate(False)
        tree = self.note_tree = ttk.Treeview(left, show="tree", style="App.Treeview", selectmode="browse")
        tree.tag_configure("group", foreground=T["muted"], font=("Segoe UI Semibold", 9))
        tree.pack(fill="both", expand=True, padx=px(4), pady=px(6))
        tree.bind("<<TreeviewSelect>>", self.note_selected)

        right = tk.Frame(body, bg=T["bg"])
        right.pack(side="left", fill="both", expand=True)
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)
        vs = ttk.Scrollbar(right, orient="vertical", style="App.Vertical.TScrollbar")
        hs = ttk.Scrollbar(right, orient="horizontal", style="App.Horizontal.TScrollbar")
        txt = self.note_text = tk.Text(right, bg=T["card"], fg=T["fg"], font=("Segoe UI", 11), wrap="word",
                                       relief="flat", bd=0, highlightthickness=0, padx=px(24), pady=px(18),
                                       spacing1=px(2), spacing3=px(2), cursor="arrow", yscrollcommand=vs.set,
                                       xscrollcommand=hs.set)
        vs.configure(command=txt.yview)
        hs.configure(command=txt.xview)      # wide code and tables scroll sideways (or Shift + wheel)
        txt.grid(row=0, column=0, sticky="nsew")
        vs.grid(row=0, column=1, sticky="ns")
        hs.grid(row=1, column=0, sticky="ew")
        mono = ("Consolas", 10)
        txt.tag_configure("h1", font=("Segoe UI Semibold", 19), spacing1=px(4), spacing3=px(8))
        txt.tag_configure("h2", font=("Segoe UI Semibold", 14), foreground=T["accent"], spacing1=px(16), spacing3=px(6))
        txt.tag_configure("h3", font=("Segoe UI Semibold", 11), spacing1=px(10), spacing3=px(3))
        txt.tag_configure("bold", font=("Segoe UI Semibold", 11))
        txt.tag_configure("bullet", lmargin1=px(14), lmargin2=px(30))
        txt.tag_configure("code", font=mono, background=T["card2"], lmargin1=px(12), lmargin2=px(12), spacing1=0,
                          spacing3=0, wrap="none")
        txt.tag_configure("icode", font=mono, background=T["card2"])
        txt.tag_configure("table", font=mono, lmargin1=px(6), wrap="none")
        txt.tag_configure("tablehead", font=("Consolas", 10, "bold"), lmargin1=px(6), wrap="none")
        txt.tag_configure("hit", background=T["warn"], foreground=T["bg"])
        self.fill_notes()

    def fill_notes(self):
        tree = self.note_tree
        if tree is None or not tree.winfo_exists():
            return
        self.note_query = self.note_var.get().strip()
        words = self.note_query.lower().split()
        tree.delete(*tree.get_children())
        paths = []
        for gi, (group, items) in enumerate(load_notes()):
            keep = []
            for title, path in items:
                if words:
                    try:
                        hay = (title + " " + path.read_text(encoding="utf-8")).lower()
                    except OSError:
                        continue
                    if not all(w in hay for w in words):
                        continue
                keep.append((title, path))
            if keep:
                gid = f"group{gi}"
                tree.insert("", "end", iid=gid, text=group.upper(), open=True, tags=("group",))
                for title, path in keep:
                    tree.insert(gid, "end", iid=str(path), text=title)
                    paths.append(path)
        if not paths:
            self.show_note(None)
            return
        pick = self.note_path if self.note_path in paths else paths[0]
        tree.selection_set(str(pick))
        if pick != paths[0]:                 # leave the list at the top when the first note is the one open
            tree.after_idle(lambda: tree.exists(str(pick)) and tree.see(str(pick)))
        self.show_note(pick)

    def note_selected(self, _ev=None):
        sel = self.note_tree.selection()
        if sel and not sel[0].startswith("group") and Path(sel[0]) != self.note_path:
            self.show_note(Path(sel[0]))

    def open_note_file(self):
        target = self.note_path if self.note_path and self.note_path.exists() else NOTES
        if target.exists():
            os.startfile(target)

    def show_note(self, path):
        txt = self.note_text
        txt.configure(state="normal")
        txt.delete("1.0", "end")
        self.note_path = path
        if path is None:
            txt.insert("end", "No notes match.\n\nAdd .md files under the notes folder and they will appear here.")
        else:
            try:
                self.render_md(txt, path.read_text(encoding="utf-8"))
            except OSError as exc:
                txt.insert("end", f"Couldn't read this note: {exc}")
            for word in self.note_query.lower().split():
                pos = "1.0"
                while True:
                    pos = txt.search(word, pos, stopindex="end", nocase=True)
                    if not pos:
                        break
                    end = f"{pos}+{len(word)}c"
                    txt.tag_add("hit", pos, end)
                    pos = end
        txt.configure(state="disabled")
        txt.yview_moveto(0)

    @staticmethod
    def render_md(txt, md):
        """Small Markdown renderer: headings, bullets, code blocks, tables, `code` and **bold**."""
        def inline(text, *tags):
            for part in re.split(r"(`[^`]+`|\*\*[^*]+\*\*)", text):
                if part.startswith("`") and part.endswith("`") and len(part) > 2:
                    txt.insert("end", part[1:-1], tags + ("icode",))
                elif part.startswith("**") and part.endswith("**") and len(part) > 4:
                    txt.insert("end", part[2:-2], tags + ("bold",))
                elif part:
                    txt.insert("end", part, tags)

        def flush(rows):
            rows = [r for r in rows if not all(re.fullmatch(r":?-{2,}:?", c) for c in r)]
            if not rows:
                return
            cols = max(len(r) for r in rows)
            rows = [[re.sub(r"\*\*([^*]+)\*\*", r"\1", c.replace("`", "")) for c in r] + [""] * (cols - len(r))
                    for r in rows]
            widths = [max(len(r[i]) for r in rows) for i in range(cols)]
            for n, r in enumerate(rows):
                txt.insert("end", "   ".join(c.ljust(w) for c, w in zip(r, widths)).rstrip() + "\n",
                           ("tablehead",) if n == 0 else ("table",))
                if n == 0:
                    txt.insert("end", "   ".join("-" * w for w in widths) + "\n", ("table",))

        code, table = False, []
        for line in md.splitlines():
            if line.strip().startswith("```"):
                flush(table)
                table, code = [], not code
                continue
            if code:
                txt.insert("end", line + "\n", ("code",))
                continue
            if line.startswith("|"):
                cells = re.split(r"(?<!\\)\|", line.strip().strip("|"))   # \| is a literal bar inside a cell
                table.append([c.strip().replace("\\|", "|") for c in cells])
                continue
            flush(table)
            table = []
            if line.startswith("### "):
                txt.insert("end", line[4:] + "\n", ("h3",))
            elif line.startswith("## "):
                txt.insert("end", line[3:] + "\n", ("h2",))
            elif line.startswith("# "):
                txt.insert("end", line[2:] + "\n", ("h1",))
            elif line.startswith(("- ", "* ")):
                txt.insert("end", "\u2022  ", ("bullet",))
                inline(line[2:], "bullet")
                txt.insert("end", "\n", ("bullet",))
            else:
                inline(line)
                txt.insert("end", "\n")
        flush(table)

    # ---------- navigation ----------
    def set_view(self, view):
        self.view = view
        self.render()

    def jump(self, idx):
        self.idx, self.view = idx, "today"
        self.render()

    def go(self, step):
        self.idx = max(0, min(len(self.entries) - 1, self.idx + step))
        self.render()

    def go_today(self):
        self.jump(self.today_index())

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.settings["theme"] = self.theme
        try:
            SETTINGS.write_text(json.dumps(self.settings, indent=1), encoding="utf-8")
        except OSError:
            pass
        self.render()

    def show_keys(self):
        messagebox.showinfo("Keyboard shortcuts", "\n".join((
            "1 / 2 / 3 / 4\tLesson / Dashboard / Roadmap / Notes",
            "Left / Right\tPrevious / next day",
            "T\tJump to today",
            "D\tMark Done",
            "S\tSkip",
            "U\tUndo",
            "L\tTeach me (opens Claude)",
            "N\tOpen notes in Notion",
            "Space\tStart / pause the focus timer",
            "Ctrl+F or /\tSearch the roadmap (or notes, when Notes is open)",
            "Esc\tLeave the search box")))

    def on_wheel(self, ev):
        if self.scroll is not None and self.scroll.winfo_exists():
            self.scroll.wheel(ev)

    def on_key(self, ev):
        k = ev.keysym.lower()
        if isinstance(ev.widget, tk.Entry):
            if k == "escape":
                self.root.focus_set()
            elif k in ("return", "down") and self.tree is not None and self.tree.get_children():
                self.tree.focus_set()
                first = self.tree.selection() or self.tree.get_children()[:1]
                self.tree.selection_set(first)
                self.tree.focus(first[0])
            elif k in ("return", "down") and self.note_tree is not None:
                self.note_tree.focus_set()
            return
        if (ev.state & 0x4 and k == "f") or k == "slash":
            if self.view not in ("roadmap", "notes"):
                self.set_view("roadmap")
            self.search_entry.focus_set()
            self.search_entry.select_range(0, "end")
            return "break"
        if ev.state & 0x4 or ev.state & 0x20000:  # leave other Ctrl / Alt combinations alone
            return
        if k in ("1", "2", "3", "4"):
            self.set_view(("today", "dash", "roadmap", "notes")[int(k) - 1])
        elif k in ("question", "f1"):
            self.show_keys()
        elif k == "space":
            self.toggle_timer()
        elif k == "t":
            self.go_today()
        elif self.view == "today":
            e = self.entries[self.idx]
            s = statuses().get(e["date"])
            markable = e["date"] <= self.today_s() and not is_rest(e)
            if k in ("left", "right"):
                self.go(-1 if k == "left" else 1)
            elif k == "d" and markable and not s:
                self.mark("DONE", e)
            elif k == "s" and markable and not s:
                self.mark("SKIP", e)
            elif k == "u" and s:
                self.mark("UNDO", e)
            elif k == "l" and not is_rest(e):
                self.teach(e, e["blocks"][0])
            elif k == "n" and not is_rest(e):
                self.open_notes(e, e["blocks"][0])

    # ---------- focus timer ----------
    def start_timer(self, b):
        secs = b["minutes"] * 60
        self.timer = dict(total=secs, left=secs, end=time.monotonic() + secs, running=True, label=b["label"])
        self.timer_buttons()
        self.update_timer_ui()

    def toggle_timer(self):
        tm = self.timer
        if not tm["total"]:
            e = self.entries[self.idx]
            if not is_rest(e):
                self.start_timer(e["blocks"][0])
            return
        if tm["running"]:
            tm["left"], tm["running"] = max(0, tm["end"] - time.monotonic()), False
        elif tm["left"] > 0:
            tm["end"], tm["running"] = time.monotonic() + tm["left"], True
        self.timer_buttons()
        self.update_timer_ui()

    def reset_timer(self):
        self.timer = dict(total=0, left=0, end=0, running=False, label="")
        self.timer_buttons()
        self.update_timer_ui()

    def timer_buttons(self):
        try:
            for w in self.timer_row.winfo_children():
                w.destroy()
            T, tm = self.T, self.timer
            if tm["total"]:
                RButton(self.timer_row, "Pause" if tm["running"] else "Resume", self.toggle_timer, T["card2"], T["fg"],
                        size=9, padx=11, pady=5).pack(side="left", padx=(0, px(6)))
                RButton(self.timer_row, "Reset", self.reset_timer, T["card2"], T["muted"], size=9, padx=11,
                        pady=5).pack(side="left")
        except tk.TclError:
            pass

    def update_timer_ui(self):
        tm = self.timer
        left = int(round(tm["left"]))
        clock = f"{left // 60:02d}:{left % 60:02d}"
        try:
            self.root.title(f"{clock}  ·  {APP_NAME}" if tm["running"] else APP_NAME)
            self.timer_time.configure(text=clock if tm["total"] else "--:--")
            self.timer_bar.set(1 - tm["left"] / tm["total"] if tm["total"] else 0)
            name = tm["label"] + ("" if tm["running"] else "  (paused)") if tm["total"] else \
                "Press Start timer on a lesson card, or Space."
            if self.timer_name.cget("text") != name:
                self.timer_name.configure(text=name)
        except tk.TclError:
            pass

    def tick(self):
        self.root.after(500, self.tick)
        tm = self.timer
        if not tm["running"]:
            return
        tm["left"] = max(0, tm["end"] - time.monotonic())
        self.update_timer_ui()
        if tm["left"] <= 0:
            label = tm["label"]
            self.reset_timer()
            try:
                import winsound
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except Exception:
                self.root.bell()
            self.root.deiconify()
            self.root.lift()
            messagebox.showinfo("Time's up", f"Timer finished for:\n{label}\n\nPress Done if you finished the lesson.")

    # ---------- actions ----------
    def mark(self, status, e):
        log(status, e)
        if status in ("DONE", "SKIP"):
            p = self.pending()  # move on to the next unfinished day, if any
            if p:
                self.idx = self.by_date[p[0]["date"]]
        self.render()
        self.sync_async(lambda: ns.push_status(e, status))

    def skip_missed(self):
        t = self.today_s()
        missed = [e for e in self.pending() if e["date"] < t]
        if missed and messagebox.askyesno("Skip missed days",
                                          f"Mark {len(missed)} missed day(s) as skipped and jump to today?\n"
                                          "(You can Undo any of them later.)"):
            for e in missed:
                log("SKIP", e)
            self.go_today()
            self.sync_async(lambda: [ns.push_status(e, "SKIP") for e in missed] and f"Notion: {len(missed)} skipped")

    def teach(self, e, b):
        prompt = (f"Teach me my daily lesson. Topic - {b['label']}. Goal - {b.get('learn', '')}. "
                  f"Task - {b['task']}. Done when - {b['done_when']}. "
                  "Explain in plain simple language with small steps and examples, check my understanding with "
                  "questions as we go, then quiz me at the end. Save notes per my tutoring notes rule.")
        prompt = prompt.replace(";", ",").replace('"', "'")
        claude = shutil.which("claude") or str(Path.home() / ".local" / "bin" / "claude.exe")
        try:
            if shutil.which("wt"):
                subprocess.Popen(["wt", "-d", str(HUB), claude, prompt])
            else:
                subprocess.Popen(["cmd", "/c", "start", "Claude", "/D", str(HUB), "cmd", "/k", claude, prompt])
        except OSError as exc:
            messagebox.showerror("Teach me", f"Couldn't start Claude: {exc}")

    def open_notes(self, e, b):
        url = load_links().get("topics", {}).get(b.get("folder", ""))
        if url:  # every roadmap topic has a page in Notion > Learning Hub > Study Library
            open_notion(url)
            return
        if ns.ready():
            self.sync_msg = "Notion: opening notes..."

            def work():
                url = ns.ensure_notes_page(e, b)
                if url:
                    os.startfile(ns.desktop_url(url))
                    return "Notion: notes opened"
                return "Notion: couldn't make notes page"
            self.sync_async(work)
        else:
            folder = HUB / "Daily-Learning" / b["folder"]
            folder.mkdir(parents=True, exist_ok=True)
            for name, head in (("notes.txt", "NOTES - important points for interviews\n\n"),
                               ("journal.txt", "JOURNAL - what I learned (dated) + WHERE I WENT WRONG\n\n")):
                p = folder / name
                if not p.exists():
                    p.write_text(f"{b['label']}\n{head}", encoding="utf-8")
            os.startfile(folder)

    def open_hub(self):
        url = load_links().get("hub")
        if url:
            open_notion(url)
        else:
            os.startfile(HUB)

    def open_progress(self):
        cfg = ns.load_config()
        if ns.ready():
            os.startfile(ns.desktop_url(ns.page_url(cfg["progress_db_id"])))
        elif PROGRESS.exists():
            os.startfile(PROGRESS)
        else:
            messagebox.showinfo("Progress", "Nothing logged yet. Press Done on your first lesson!")

    # ---------- background Notion sync ----------
    def sync_async(self, fn):
        def run():
            try:
                self.sync_msg = fn() or self.sync_msg
            except Exception as exc:  # network/Notion errors must never break the app
                self.sync_msg = f"Notion sync failed (saved locally): {str(exc)[:80]}"
        threading.Thread(target=run, daemon=True).start()

    def poll_sync(self):
        try:
            lab = self.sync_label
            if lab is not None and lab.winfo_exists() and lab.cget("text") != self.sync_msg:
                lab.configure(text=self.sync_msg)
        except tk.TclError:
            pass
        self.root.after(500, self.poll_sync)


def main():
    global SCALE
    try:
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)  # sharp text on scaled displays
        except Exception:
            pass
        root = tk.Tk()
        SCALE = max(1.0, root.winfo_fpixels("1i") / 96)
        App(root)
        root.mainloop()
    except Exception as exc:
        messagebox.showerror(f"{APP_NAME} - error", f"{type(exc).__name__}: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
