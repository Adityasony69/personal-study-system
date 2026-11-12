"""
today.py - "Today's Topic": your daily NEW-skill lesson, progress tracker and dashboard.

Views (sidebar, or keys 1 to 5)
  Lesson      the day's lesson cards, with Done / Skip / Undo, a focus timer, Teach me and Notes
  Dashboard   streaks, time learned, activity heatmap, progress per track, your own dates
  Roadmap     every day of the roadmap, searchable and filterable; double-click a row to open it
  Notes       study notes by subject. Paste note (Ctrl+V) saves an AI reply into the right folder;
              Remove moves a note to notes/_trash
  Daily Topic one new thing a day to research and think about, with a timer and your own research notes

Keyboard
  Left / Right  previous / next day        T  jump to today
  D  Done    S  Skip    U  Undo            L  Teach me    N  Notes
  Space  start / pause the focus timer     Ctrl+F or /  search (roadmap, or notes when open)
  1-5    switch view                       ?  show this list

Everything is logged in progress.txt (append-only history). If Notion is connected
(run notion_setup.py once), every Done/Skip/Undo is also synced there.
"""
import json
import os
import random
import re
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
import urllib.parse
import webbrowser
from datetime import date, datetime, timedelta
from pathlib import Path
from tkinter import messagebox, ttk

HERE = Path(__file__).resolve().parent
HUB = HERE.parent
sys.path.insert(0, str(HERE))
import notes_lib as nl  # noqa: E402
import notion_sync as ns  # noqa: E402

ROADMAP = HERE / "roadmap.json"
PROGRESS = HERE / "progress.txt"
LINKS = HERE / "notion_links.json"
SETTINGS = HERE / "settings.json"
EVENTS = HERE / "my-events.txt"
NOTES = HERE / "notes"
NOTE_GROUPS = {"iot": "IoT with ESP32", "os": "Operating systems in practice", "dbms": "Databases in practice",
               "networks": "Networking in practice", "cloud": "Cloud in practice", "python": "Python",
               "java": "Java", "dsa-java": "DSA in Java", "git": "Git", "sql": "SQL",
               "numpy-pandas": "NumPy and Pandas", "machine-learning": "Machine Learning",
               "deep-learning": "Deep Learning", "genai": "GenAI", "deployment": "Deployment", "career": "Career",
               "os-exam": "OS exam theory (units 1 to 5)", "research": "My research"}
TOPICS = HERE / "daily_topics.json"
TOPIC_LOG = HERE / "topic_log.txt"
TOPIC_START = date(2026, 11, 1)
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
    """[(group title, [(note title, path), ...]), ...]; see notes_lib for the folder rules."""
    return nl.load_notes(NOTES, NOTE_GROUPS)


def load_topics():
    """[(niche id, niche label, [(title, what it is, question), ...]), ...] from daily_topics.json"""
    try:
        data = json.loads(TOPICS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return [(n["id"], n["label"], [tuple(t) for t in n["topics"] if len(t) == 3])
            for n in data.get("niches", []) if n.get("topics")]


def topic_log():
    """[(day, niche, title), ...] of topics marked as researched, oldest first."""
    out = []
    try:
        for line in TOPIC_LOG.read_text(encoding="utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) >= 3 and not line.startswith("#"):
                out.append((parts[0][:10], parts[1], parts[2]))
    except OSError:
        pass
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
        self.notes_flash, self.paste_win = "", None
        self.topics = load_topics()
        self.topic = None                     # None = show the topic of the day
        self.topic_niche = self.settings.get("topic_niche", "all")
        try:
            self.topic_minutes = max(5, min(60, int(self.settings.get("topic_minutes", 15))))
        except (TypeError, ValueError):
            self.topic_minutes = 15
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
         "notes": self.view_notes, "topic": self.view_topic}[self.view](main)
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
                                ("notes", "Notes", "4"), ("topic", "Daily Topic", "5")):
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
        daily = self.daily_topic()
        if daily:
            c = Card(f, T["card"], pad=12, radius=12)
            c.pack(fill="x", padx=side_pad, pady=(px(10), px(4)))
            RButton(c.body, "Open", lambda: self.topic_today(), T["card2"], T["fg"], size=9, bold=False, padx=11,
                    pady=5).pack(side="right")
            tk.Label(c.body, text="DAILY TOPIC", bg=T["card"], fg=T["muted"], font=("Segoe UI Semibold", 8)).pack(
                side="left", padx=(0, px(12)))
            wlabel(c.body, text=daily[1], bg=T["card"], fg=T["fg"], font=("Segoe UI", 10)).pack(
                side="left", fill="x", expand=True)
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
        if self.notes_flash:
            tk.Label(head, text=self.notes_flash, bg=T["bg"], fg=T["ok"], font=("Segoe UI", 10)).pack(
                side="left", padx=px(14))
        RButton(head, "Remove", self.remove_note, T["card2"], T["muted"], size=9, bold=False, padx=11, pady=5).pack(
            side="right")
        RButton(head, "Open file", self.open_note_file, T["card2"], T["fg"], size=9, bold=False, padx=11, pady=5).pack(
            side="right", padx=(0, px(8)))
        RButton(head, "Paste note", self.paste_note, T["accent"], size=9, padx=12, pady=5).pack(
            side="right", padx=(0, px(8)))
        RButton(head, "Ask Claude", self.ask_claude_note, T["purple"], size=9, padx=12, pady=5).pack(
            side="right", padx=(0, px(8)))
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
        txt.tag_configure("bullet2", lmargin1=px(34), lmargin2=px(50))
        txt.tag_configure("quote", lmargin1=px(18), lmargin2=px(18), foreground=T["muted"])
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
        groups, paths = [], []
        for group, items in load_notes():
            keep = []
            for title, path in items:
                if words:
                    try:
                        hay = (title + " " + nl.read_note(path)).lower()
                    except OSError:
                        continue
                    if not all(w in hay for w in words):
                        continue
                keep.append((title, path))
            if keep:
                groups.append((group, keep))
                paths += [path for _, path in keep]
        if not paths:
            self.show_note(None)
            return
        pick = self.note_path if self.note_path in paths else paths[0]
        for gi, (group, keep) in enumerate(groups):
            gid = f"group{gi}"
            is_open = bool(words) or pick in [path for _, path in keep]
            tree.insert("", "end", iid=gid, text=f"{group.upper()}  ({len(keep)})", open=is_open, tags=("group",))
            for title, path in keep:
                tree.insert(gid, "end", iid=str(path), text=title)
        tree.selection_set(str(pick))
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

    def ask_claude_note(self):
        """Open Claude Code in a terminal, pointed at the note that is open right now."""
        path = self.note_path
        if not path or not path.exists():
            messagebox.showinfo("Ask Claude", "Open a note first, then press Ask Claude.")
            return
        self.launch_claude(
            f"I am studying my note '{path.stem}' from my {path.parent.name} notes. "
            f"Read this file first - {path} - then give me a 3 line recap of it and ask what I want - "
            "explain a part more simply, quiz me on it, or give me a small practice task. "
            "Use plain simple language and small steps. Do not change the file unless I ask.", "Ask Claude")

    def show_note(self, path):
        txt = self.note_text
        txt.configure(state="normal")
        txt.delete("1.0", "end")
        self.note_path = path
        if path is None:
            txt.insert("end", "No notes match.\n\nPress Paste note (or Ctrl+V) to add one from an AI reply, "
                              "or save .md files into a subject folder under notes.")
        else:
            try:
                self.render_md(txt, nl.read_note(path))
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
            text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r"\1 (\2)", text)   # [label](url) -> label (url)
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
            if line.strip().startswith(("```", "~~~")):
                flush(table)
                table, code = [], not code
                continue
            if code:
                txt.insert("end", line + "\n", ("code",))
                continue
            if line.lstrip().startswith("|"):
                cells = re.split(r"(?<!\\)\|", line.strip().strip("|"))   # \| is a literal bar inside a cell
                table.append([c.strip().replace("\\|", "|") for c in cells])
                continue
            flush(table)
            table = []
            heading = re.match(r"^(#{1,6})[ \t]+(.+?)[ \t#]*$", line)
            bullet = re.match(r"^([ \t]*)[-*+][ \t]+(.*)$", line)
            number = re.match(r"^([ \t]*)(\d+[.)])[ \t]+(.*)$", line)
            if heading:
                level = min(len(heading.group(1)), 3)
                txt.insert("end", re.sub(r"\*\*|__|`", "", heading.group(2)) + "\n", ("h%d" % level,))
            elif re.fullmatch(r"[ \t]*(-{3,}|\*{3,}|_{3,})[ \t]*", line):
                txt.insert("end", "\n")
            elif bullet:
                tag = "bullet2" if len(bullet.group(1).expandtabs(4)) >= 2 else "bullet"
                txt.insert("end", "\u2022  ", (tag,))
                inline(bullet.group(2), tag)
                txt.insert("end", "\n", (tag,))
            elif number:
                tag = "bullet2" if len(number.group(1).expandtabs(4)) >= 2 else "bullet"
                txt.insert("end", number.group(2) + "  ", (tag,))
                inline(number.group(3), tag)
                txt.insert("end", "\n", (tag,))
            elif line.lstrip().startswith(">"):
                inline(line.lstrip()[1:].lstrip(), "quote")
                txt.insert("end", "\n", ("quote",))
            else:
                inline(line)
                txt.insert("end", "\n")
        flush(table)

    # ---------- adding and removing notes ----------
    def flash(self, message, seconds=8):
        """Show a short message next to the Notes title, then clear it."""
        self.notes_flash = message

        def clear():
            if self.notes_flash == message:
                self.notes_flash = ""
                if self.view == "notes":
                    self.render()
        self.root.after(seconds * 1000, clear)

    def remove_note(self):
        path = self.note_path
        if not path or not path.exists():
            messagebox.showinfo("Remove note", "Pick a note in the list first.")
            return
        title = nl.note_title(path)
        if not messagebox.askyesno("Remove note", f"Move '{title}' to the trash?\n\n"
                                   "It goes to notes\\_trash, so you can move it back later."):
            return
        trash = NOTES / "_trash"
        trash.mkdir(parents=True, exist_ok=True)
        subject = path.parent.name if path.parent != NOTES else "unsorted"
        target = trash / f"{subject}__{path.name}"
        if target.exists():
            target = trash / f"{subject}__{datetime.now():%Y%m%d-%H%M%S}__{path.name}"
        try:
            shutil.move(str(path), str(target))
        except OSError as exc:
            messagebox.showerror("Remove note", f"Couldn't move it: {exc}")
            return
        self.note_path = None
        self.flash(f"Moved '{title}' to the trash")
        self.render()

    def paste_note(self):
        """Window that takes an AI reply from the clipboard, tidies it and saves it in the right folder."""
        if self.paste_win is not None and self.paste_win.winfo_exists():
            self.paste_win.deiconify()
            self.paste_win.lift()
            return
        T = self.T
        dlg = self.paste_win = tk.Toplevel(self.root)
        dlg.title("Paste a note")
        dlg.configure(bg=T["bg"])
        dlg.transient(self.root)
        w = min(px(920), self.root.winfo_screenwidth() - 60)
        h = min(px(720), self.root.winfo_screenheight() - 100)
        dlg.geometry(f"{w}x{h}+{self.root.winfo_rootx() + px(40)}+{max(0, self.root.winfo_rooty() - px(10))}")
        dlg.minsize(min(w, px(640)), min(h, px(480)))
        title_bar(dlg, self.theme == "dark")

        subjects = nl.subjects(NOTES, NOTE_GROUPS)
        labels = dict(subjects)
        current = self.note_path.parent.name if self.note_path and self.note_path.parent != NOTES else ""
        start = self.settings.get("paste_subject") or current or "python"
        state = {"subject": start, "warnings": [], "auto_title": "", "job": None, "guessed": False}
        pad = px(18)

        frame = tk.Frame(dlg, bg=T["bg"])
        frame.pack(fill="both", expand=True, padx=pad, pady=pad)
        frame.columnconfigure(1, weight=1)
        tk.Label(frame, text="Paste a note", bg=T["bg"], fg=T["fg"], font=("Segoe UI Semibold", 16)).grid(
            row=0, column=0, columnspan=3, sticky="w")
        tk.Label(frame, text="Copy the AI's reply with the copy button under it, then check it here and press Save.",
                 bg=T["bg"], fg=T["muted"], font=("Segoe UI", 10)).grid(row=1, column=0, columnspan=3, sticky="w",
                                                                        pady=(0, px(12)))

        def field_label(row, text):
            tk.Label(frame, text=text, bg=T["bg"], fg=T["muted"], font=("Segoe UI", 10)).grid(
                row=row, column=0, sticky="w", padx=(0, px(12)), pady=px(4))

        def entry(parent, var, width):
            return tk.Entry(parent, textvariable=var, bg=T["card"], fg=T["fg"], insertbackground=T["fg"],
                            relief="flat", font=("Segoe UI", 10), width=width, highlightthickness=1,
                            highlightbackground=T["line"], highlightcolor=T["accent"])

        field_label(2, "Subject")
        srow = tk.Frame(frame, bg=T["bg"])
        srow.grid(row=2, column=1, columnspan=2, sticky="w")
        mb = tk.Menubutton(srow, text="", bg=T["card2"], fg=T["fg"], activebackground=T["line"],
                           activeforeground=T["fg"], relief="flat", bd=0, highlightthickness=0,
                           font=("Segoe UI", 10), padx=px(12), pady=px(4), cursor="hand2", width=26, anchor="w")
        menu = tk.Menu(mb, tearoff=0, bg=T["card"], fg=T["fg"], activebackground=T["accent"],
                       activeforeground="#ffffff", bd=0, font=("Segoe UI", 10))
        mb.configure(menu=menu)
        mb.pack(side="left")
        tk.Label(srow, text="or a new subject", bg=T["bg"], fg=T["muted"], font=("Segoe UI", 10)).pack(
            side="left", padx=(px(14), px(8)))
        new_var = tk.StringVar()
        entry(srow, new_var, 22).pack(side="left", ipady=px(3))
        hint = tk.Label(frame, text="", bg=T["bg"], fg=T["muted"], font=("Segoe UI", 9))
        hint.grid(row=3, column=1, columnspan=2, sticky="w")

        field_label(4, "Title")
        title_var = tk.StringVar()
        title_entry = entry(frame, title_var, 50)
        title_entry.grid(row=4, column=1, columnspan=2, sticky="ew", ipady=px(3))

        where = tk.Label(frame, text="", bg=T["bg"], fg=T["ok"], font=("Segoe UI", 10), anchor="w", justify="left")
        where.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(px(8), 0))
        warn = tk.Label(frame, text="", bg=T["bg"], fg=T["warn"], font=("Segoe UI", 10), anchor="w", justify="left")
        warn.grid(row=6, column=0, columnspan=3, sticky="ew")
        warn.bind("<Configure>", lambda e: warn.configure(wraplength=max(200, e.width - 8)))

        boxf = tk.Frame(frame, bg=T["bg"])
        boxf.grid(row=7, column=0, columnspan=3, sticky="nsew", pady=(px(8), px(10)))
        frame.rowconfigure(7, weight=1)
        box = tk.Text(boxf, bg=T["card"], fg=T["fg"], insertbackground=T["fg"], font=("Consolas", 10),
                      wrap="word", relief="flat", bd=0, highlightthickness=1, highlightbackground=T["line"],
                      highlightcolor=T["accent"], padx=px(12), pady=px(10), undo=True)
        sb = ttk.Scrollbar(boxf, orient="vertical", command=box.yview, style="App.Vertical.TScrollbar")
        box.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        box.pack(side="left", fill="both", expand=True)

        buttons = tk.Frame(frame, bg=T["bg"])
        buttons.grid(row=8, column=0, columnspan=3, sticky="ew")

        def folder_name():
            typed = new_var.get().strip()
            return nl.slugify(typed, 40) if typed else state["subject"]

        def compute():
            text = box.get("1.0", "end-1c")
            folder = NOTES / folder_name()
            parts = nl.split_notes(text)
            titles = []
            for i, part in enumerate(parts):
                found = nl.title_of(part)
                if len(parts) == 1 or (found is None and i == 0):
                    typed = title_var.get().strip()
                    found = nl.clean_title(typed) if typed else found
                titles.append(found or "")
            return text, folder, parts, titles

        def refresh():
            state["job"] = None
            if not dlg.winfo_exists():
                return
            text, folder, parts, titles = compute()
            mb.configure(text="  " + labels.get(state["subject"], nl.group_label(state["subject"], NOTE_GROUPS))
                         + "  \u25be")
            if new_var.get().strip():
                hint.configure(text=f"New subject: it will be created as notes\\{folder.name}")
            elif state["guessed"]:
                hint.configure(text="Subject guessed from the text. Change it if it's wrong.")
            else:
                hint.configure(text="")
            problems = list(state["warnings"])
            if not text.strip():
                problems = ["Nothing to save yet. Press Paste from clipboard, or paste into the box (Ctrl+V)."]
            elif not all(titles):
                problems.insert(0, "Type a title for this note.")
            existing = nl.existing_titles(folder)
            for t in titles:
                if t and t.lower() in existing:
                    problems.append(f"'{t}' is already saved in this subject; Save will ask whether to replace it.")
            if len(parts) > 1:
                problems.insert(0, f"This contains {len(parts)} notes; each will be saved as its own file.")
            if text.strip() and all(titles):
                paths = nl.plan_paths(folder, titles)
                shown = ", ".join(p.name for p in paths[:3]) + (f" and {len(paths) - 3} more" if len(paths) > 3 else "")
                where.configure(text=f"Will save to  notes\\{folder.name}\\  as  {shown}", fg=T["ok"])
            else:
                where.configure(text="")
            warn.configure(text="\n".join("\u2022 " + x for x in problems))

        def schedule(*_):
            if state["job"] is not None:
                dlg.after_cancel(state["job"])
            state["job"] = dlg.after(250, refresh)

        def sync_title():
            """Keep the Title box in step with the '# ' line until the person types their own."""
            found = nl.title_of(box.get("1.0", "end-1c"))
            if found and (not title_var.get().strip() or title_var.get() == state["auto_title"]):
                title_var.set(found)
                state["auto_title"] = found

        def load_text(raw):
            text, warnings = nl.clean_pasted(raw)
            state["warnings"] = warnings
            guess = nl.guess_subject(text) if text.strip() else None
            if guess and not new_var.get().strip():
                state["subject"], state["guessed"] = guess, True
            else:
                state["guessed"] = False
            box.delete("1.0", "end")
            box.insert("1.0", text)
            box.edit_reset()
            title_var.set("")
            state["auto_title"] = ""
            sync_title()
            box.mark_set("insert", "1.0")
            box.see("1.0")
            schedule()

        def from_clipboard():
            try:
                raw = self.root.clipboard_get()
            except tk.TclError:
                raw = ""
            load_text(raw)

        def tidy():
            load_text(box.get("1.0", "end-1c"))

        def choose(name):
            state["subject"], state["guessed"] = name, False
            new_var.set("")
            schedule()

        for name, label in subjects:
            menu.add_command(label=label, command=lambda n=name: choose(n))

        def on_modified(_e=None):
            if box.edit_modified():
                box.edit_modified(False)
                state["warnings"] = [x for x in state["warnings"] if "empty" not in x]
                sync_title()
                schedule()

        def on_paste(_e=None):
            if not box.get("1.0", "end-1c").strip():
                try:
                    raw = self.root.clipboard_get()
                except tk.TclError:
                    return None
                load_text(raw)
                return "break"
            return None

        def save(_e=None):
            text, folder, parts, titles = compute()
            if not text.strip():
                dlg.bell()
                return "break"
            if not all(titles):
                messagebox.showwarning("Paste a note", "Type a title for the note first.", parent=dlg)
                title_entry.focus_set()
                return "break"
            try:
                folder.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                messagebox.showerror("Paste a note", f"Couldn't create the folder: {exc}", parent=dlg)
                return "break"
            existing = nl.existing_titles(folder)
            planned = nl.plan_paths(folder, titles)
            saved = []
            for part, title, path in zip(parts, titles, planned):
                target = path
                old = existing.get(title.lower())
                if old is not None:
                    answer = messagebox.askyesnocancel(
                        "Note already exists", f"'{title}' is already saved as {old.name}.\n\n"
                        "Yes: replace it with this one\nNo: keep both\nCancel: stop here", parent=dlg)
                    if answer is None:
                        break
                    if answer:
                        target = old
                body = nl.set_title(part, title).strip() + "\n"
                try:
                    target.write_bytes(body.encode("utf-8"))
                except OSError as exc:
                    messagebox.showerror("Paste a note", f"Couldn't save {target.name}: {exc}", parent=dlg)
                    break
                saved.append(target)
            if not saved:
                return "break"
            self.settings["paste_subject"] = folder.name
            self.save_settings()
            close()
            self.note_query, self.note_path = "", saved[-1]
            count = f"{len(saved)} notes" if len(saved) > 1 else f"'{titles[0]}'"
            self.flash(f"Saved {count} in {nl.group_label(folder.name, NOTE_GROUPS)}")
            self.view = "notes"
            self.render()
            return "break"

        def close(_e=None):
            if state["job"] is not None:
                dlg.after_cancel(state["job"])
                state["job"] = None
            self.paste_win = None
            dlg.destroy()

        RButton(buttons, "Paste from clipboard", from_clipboard, T["card2"], T["fg"], size=9, padx=12, pady=6).pack(
            side="left")
        RButton(buttons, "Tidy text", tidy, T["card2"], T["fg"], size=9, bold=False, padx=12, pady=6).pack(
            side="left", padx=px(8))
        RButton(buttons, "Save note", save, T["ok"], size=10, padx=18, pady=6).pack(side="right")
        RButton(buttons, "Cancel", close, T["card2"], T["fg"], size=10, bold=False, padx=14, pady=6).pack(
            side="right", padx=px(8))

        box.bind("<<Modified>>", on_modified)
        box.bind("<<Paste>>", on_paste)
        title_var.trace_add("write", schedule)
        new_var.trace_add("write", schedule)
        dlg.bind("<Escape>", close)
        dlg.bind("<Control-s>", save)
        dlg.bind("<Control-Return>", save)
        dlg.protocol("WM_DELETE_WINDOW", close)
        self.paste_ui = dict(box=box, title=title_var, new=new_var, where=where, warn=warn, save=save, hint=hint,
                             state=state,
                             choose=choose, close=close, refresh=refresh, load=load_text)
        from_clipboard()
        box.focus_set()

    # ---------- daily topic ----------
    def save_settings(self):
        try:
            SETTINGS.write_text(json.dumps(self.settings, indent=1), encoding="utf-8")
        except OSError:
            pass

    def topic_pool(self):
        """[(niche label, title, what it is, question), ...] for the chosen niche."""
        return [(label, *t) for nid, label, items in self.topics for t in items
                if self.topic_niche in ("all", nid)]

    def daily_topic(self):
        """Same topic all day, a new one tomorrow, no repeats until the pool runs out."""
        pool = self.topic_pool()
        if not pool:
            return None
        order = list(range(len(pool)))
        random.Random(20261101).shuffle(order)
        return pool[order[(date.today() - TOPIC_START).days % len(pool)]]

    def view_topic(self, main):
        T, P = self.T, px(26)
        sc = self.scroll = Scroll(main, T["bg"])
        sc.pack(fill="both", expand=True)
        f = sc.inner
        side_pad = (P, px(12))
        log = topic_log()
        days = {d for d, _, _ in log}
        streak, d = 0, date.today()
        if d.isoformat() not in days:
            d -= timedelta(days=1)
        while d.isoformat() in days:
            streak += 1
            d -= timedelta(days=1)

        head = tk.Frame(f, bg=T["bg"])
        head.pack(fill="x", padx=side_pad, pady=(px(18), 0))
        tk.Label(head, text="Daily Topic", bg=T["bg"], fg=T["fg"], font=("Segoe UI Semibold", 20)).pack(side="left")
        tk.Label(head, text=f"{len(log)} researched  ·  {streak}-day streak", bg=T["bg"], fg=T["muted"],
                 font=("Segoe UI", 10)).pack(side="right")
        tk.Label(f, text="One new thing a day to research and think about.", bg=T["bg"], fg=T["muted"],
                 font=("Segoe UI", 10)).pack(anchor="w", padx=side_pad)

        daily = self.daily_topic()
        topic = self.topic or daily
        bar = tk.Frame(f, bg=T["bg"])
        bar.pack(fill="x", padx=side_pad, pady=(px(12), px(8)))
        labels = {"all": "All niches"}
        labels.update({nid: label for nid, label, _ in self.topics})
        mb = tk.Menubutton(bar, text=labels.get(self.topic_niche, "All niches") + "  ▾", bg=T["card2"], fg=T["fg"],
                           activebackground=T["line"], activeforeground=T["fg"], relief="flat", bd=0,
                           highlightthickness=0, font=("Segoe UI", 10), padx=px(12), pady=px(5), cursor="hand2")
        menu = tk.Menu(mb, tearoff=0, bg=T["card"], fg=T["fg"], activebackground=T["accent"],
                       activeforeground="#ffffff", bd=0, font=("Segoe UI", 10))
        for nid, label in labels.items():
            menu.add_command(label=label, command=lambda n=nid: self.topic_set_niche(n))
        mb.configure(menu=menu)
        mb.pack(side="left")
        RButton(bar, "Spin another", self.topic_spin, T["accent"], size=9, padx=12, pady=5).pack(side="left", padx=px(8))
        if topic != daily:
            RButton(bar, "Back to today's topic", self.topic_today, T["card2"], T["fg"], size=9, bold=False, padx=12,
                    pady=5).pack(side="left")
        if not topic:
            tk.Label(f, text="No topics found. Check daily_topics.json.", bg=T["bg"], fg=T["warn"],
                     font=("Segoe UI", 10)).pack(anchor="w", padx=side_pad, pady=px(20))
            return
        niche, title, brief, question = topic
        done = any(t == title for _, _, t in log)

        c = Card(f, T["card"], pad=20)
        c.pack(fill="x", padx=side_pad, pady=px(6))
        top = tk.Frame(c.body, bg=T["card"])
        top.pack(fill="x")
        self.pill(top, niche, T["accent"]).pack(side="left")
        tag = f"Topic of the day  ·  {date.today():%a %d %b}" if topic == daily else "Random pick"
        tk.Label(top, text=tag, bg=T["card"], fg=T["muted"], font=("Segoe UI", 9)).pack(side="left", padx=px(10))
        if done:
            self.pill(top, "Researched ✓", T["ok"]).pack(side="right")
        wlabel(c.body, text=title, bg=T["card"], fg=T["fg"], font=("Segoe UI Semibold", 22)).pack(
            fill="x", pady=(px(12), px(4)))
        wlabel(c.body, text=brief, bg=T["card"], fg=T["fg"], font=("Segoe UI", 12)).pack(fill="x")
        tk.Label(c.body, text="THINK ABOUT", bg=T["card"], fg=T["muted"], font=("Segoe UI Semibold", 8)).pack(
            anchor="w", pady=(px(14), 0))
        wlabel(c.body, text=question, bg=T["card"], fg=T["fg"], font=("Segoe UI", 11)).pack(fill="x")

        c = Card(f, T["card"])
        c.pack(fill="x", padx=side_pad, pady=px(6))
        row = tk.Frame(c.body, bg=T["card"])
        row.pack(fill="x")
        tk.Label(row, text="Research timer", bg=T["card"], fg=T["fg"], font=("Segoe UI Semibold", 11)).pack(side="left")
        RButton(row, "Start timer", self.topic_timer, T["accent"], size=9, padx=12, pady=5).pack(side="right")
        RButton(row, "+", lambda: self.topic_minutes_change(5), T["card2"], T["fg"], size=9, padx=9, pady=5).pack(
            side="right", padx=(0, px(10)))
        tk.Label(row, text=f"{self.topic_minutes} min", bg=T["card"], fg=T["fg"], font=("Segoe UI Semibold", 11),
                 width=7).pack(side="right")
        RButton(row, "−", lambda: self.topic_minutes_change(-5), T["card2"], T["fg"], size=9, padx=9, pady=5).pack(
            side="right")
        row = tk.Frame(c.body, bg=T["card"])
        row.pack(fill="x", pady=(px(12), 0))
        RButton(row, "Search the web", lambda: self.topic_web(title), T["card2"], T["fg"], size=9, padx=12,
                pady=5).pack(side="left", padx=(0, px(8)))
        RButton(row, "Ask Claude", lambda: self.topic_claude(topic), T["purple"], size=9, padx=12, pady=5).pack(
            side="left", padx=(0, px(8)))
        RButton(row, "My notes", lambda: self.topic_notes(topic), T["card2"], T["fg"], size=9, padx=12, pady=5).pack(
            side="left")
        if not done:
            RButton(row, "Mark researched ✓", lambda: self.topic_mark(topic), T["ok"], size=9, padx=12, pady=5).pack(
                side="right")
        tk.Label(c.body, text="HOW TO RESEARCH IT", bg=T["card"], fg=T["muted"], font=("Segoe UI Semibold", 8)).pack(
            anchor="w", pady=(px(14), px(2)))
        for step in ("1.  What is it? Write it in two sentences of your own.",
                     "2.  Find one real example.",
                     "3.  Find the strongest argument against it.",
                     "4.  Write your own view in My notes."):
            tk.Label(c.body, text=step, bg=T["card"], fg=T["fg"], font=("Segoe UI", 10)).pack(anchor="w")

        if log:
            c = Card(f, T["card"])
            c.pack(fill="x", padx=side_pad, pady=(px(6), px(20)))
            tk.Label(c.body, text="Recently researched", bg=T["card"], fg=T["fg"], font=("Segoe UI Semibold", 12)).pack(
                anchor="w")
            for day, n, t in reversed(log[-6:]):
                r = tk.Frame(c.body, bg=T["card"])
                r.pack(fill="x", pady=(px(5), 0))
                tk.Label(r, text=f"{date.fromisoformat(day):%d %b}", bg=T["card"], fg=T["muted"], font=("Segoe UI", 10),
                         width=8, anchor="w").pack(side="left")
                tk.Label(r, text=t, bg=T["card"], fg=T["fg"], font=("Segoe UI", 10)).pack(side="left")
                tk.Label(r, text=n, bg=T["card"], fg=T["muted"], font=("Segoe UI", 9)).pack(side="right")

    def topic_today(self):
        self.topic, self.view = None, "topic"
        self.render()

    def topic_spin(self):
        pool = self.topic_pool()
        current = self.topic or self.daily_topic()
        others = [t for t in pool if t != current]
        if others:
            self.topic = random.choice(others)
            self.render()

    def topic_set_niche(self, niche):
        self.topic_niche, self.topic = niche, None
        self.settings["topic_niche"] = niche
        self.save_settings()
        self.render()

    def topic_minutes_change(self, delta):
        self.topic_minutes = max(5, min(60, self.topic_minutes + delta))
        self.settings["topic_minutes"] = self.topic_minutes
        self.save_settings()
        self.render()

    def topic_timer(self):
        topic = self.topic or self.daily_topic()
        if topic:
            self.start_timer({"minutes": self.topic_minutes, "label": "Research: " + topic[1]})

    def topic_web(self, title):
        webbrowser.open("https://www.google.com/search?q=" + urllib.parse.quote_plus(title + " explained"))

    def topic_claude(self, topic):
        niche, title, brief, question = topic
        self.launch_claude(f"Help me research today's topic. Topic - {title} ({niche}). Summary - {brief} "
                           f"Question to think about - {question} "
                           "Explain it in plain simple language, give one real example and the strongest argument "
                           "against it, then ask me for my own view and push back on it.", "Ask Claude")

    def topic_notes(self, topic):
        niche, title, brief, question = topic
        folder = NOTES / "research"
        folder.mkdir(parents=True, exist_ok=True)
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]
        path = folder / f"{slug}.md"
        if not path.exists():
            path.write_text(f"# {title}\n\n{niche}  ·  started {date.today():%d %b %Y}\n\n"
                            f"## What it is\n{brief}\n\n## Think about\n{question}\n\n"
                            "## What I found\n- \n\n## A real example\n- \n\n## The argument against\n- \n\n"
                            "## My view\n- \n\n## Sources\n- \n", encoding="utf-8")
        os.startfile(path)

    def topic_mark(self, topic):
        first = not TOPIC_LOG.exists()
        with TOPIC_LOG.open("a", encoding="utf-8") as fh:
            if first:
                fh.write("# day\tniche\ttopic   (topics marked as researched)\n")
            fh.write(f"{datetime.now():%Y-%m-%d %H:%M}\t{topic[0]}\t{topic[1]}\n")
        self.render()

    def launch_claude(self, prompt, title="Claude"):
        prompt = prompt.replace(";", ",").replace('"', "'")
        claude = shutil.which("claude") or str(Path.home() / ".local" / "bin" / "claude.exe")
        try:
            if shutil.which("wt"):
                subprocess.Popen(["wt", "-d", str(HUB), claude, prompt])
            else:
                subprocess.Popen(["cmd", "/c", "start", "Claude", "/D", str(HUB), "cmd", "/k", claude, prompt])
        except OSError as exc:
            messagebox.showerror(title, f"Couldn't start Claude: {exc}")

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
        self.save_settings()
        self.render()

    def show_keys(self):
        messagebox.showinfo("Keyboard shortcuts", "\n".join((
            "1 to 5\tLesson / Dashboard / Roadmap / Notes / Daily Topic",
            "Left / Right\tPrevious / next day",
            "T\tJump to today",
            "D\tMark Done",
            "S\tSkip",
            "U\tUndo",
            "L\tTeach me (opens Claude)",
            "N\tOpen notes in Notion",
            "Space\tStart / pause the timer",
            "R\tSpin another topic (in Daily Topic)",
            "Ctrl+F or /\tSearch the roadmap (or notes, when Notes is open)",
            "Ctrl+V\tPaste a note (in Notes)",
            "Esc\tLeave the search box")))

    def on_wheel(self, ev):
        if self.scroll is not None and self.scroll.winfo_exists():
            self.scroll.wheel(ev)

    def on_key(self, ev):
        k = ev.keysym.lower()
        try:
            if ev.widget.winfo_toplevel() is not self.root:
                return                      # typing in another window, such as Paste a note
        except (AttributeError, tk.TclError):
            return
        if isinstance(ev.widget, tk.Text) and str(ev.widget.cget("state")) == "normal":
            return
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
        if ev.state & 0x4 and k == "v" and self.view == "notes":
            self.paste_note()
            return "break"
        if ev.state & 0x4 or ev.state & 0x20000:  # leave other Ctrl / Alt combinations alone
            return
        if k in ("1", "2", "3", "4", "5"):
            self.set_view(("today", "dash", "roadmap", "notes", "topic")[int(k) - 1])
        elif k == "r" and self.view == "topic":
            self.topic_spin()
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
        if not tm["total"] and self.view == "topic":
            self.topic_timer()
            return
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
                "Press Start timer on a lesson or topic, or Space."
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
            messagebox.showinfo("Time's up", f"Timer finished for:\n{label}")

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
        self.launch_claude(prompt, "Teach me")

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
