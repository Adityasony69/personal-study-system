"""
notion_sync.py - tiny Notion API client (standard library only) used by today.py and notion_setup.py.
Token is read from E:\\Vault\\secrets.env (NOTION_TOKEN=...). It is never printed or logged.
"""
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "notion_config.json"
VAULT = Path(r"E:\Vault\secrets.env")
API = "https://api.notion.com/v1"
VERSION = "2022-06-28"


def load_token():
    if not VAULT.exists():
        return None
    for line in VAULT.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line.startswith("export "):
            line = line[7:]
        if line.startswith("NOTION_TOKEN="):
            return line.split("=", 1)[1].strip().strip('"').strip("'") or None
    return None


def load_config():
    if CONFIG.exists():
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    return {}


def save_config(cfg):
    tmp = CONFIG.with_suffix(".tmp")
    tmp.write_text(json.dumps(cfg, indent=1), encoding="utf-8")
    tmp.replace(CONFIG)


def ready():
    cfg = load_config()
    return bool(load_token() and cfg.get("progress_db_id"))


def api(method, path, body=None, token=None, tries=5):
    token = token or load_token()
    if not token:
        raise RuntimeError("NOTION_TOKEN missing in E:\\Vault\\secrets.env")
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(tries):
        req = urllib.request.Request(API + path, data=data, method=method, headers={
            "Authorization": f"Bearer {token}", "Notion-Version": VERSION, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504) and attempt < tries - 1:
                time.sleep(float(e.headers.get("Retry-After", 1 + attempt)))
                continue
            msg = e.read().decode(errors="ignore")[:300]
            raise RuntimeError(f"Notion {e.code}: {msg}") from None
        except urllib.error.URLError:
            if attempt < tries - 1:
                time.sleep(1 + attempt)
                continue
            raise


def page_url(page_id):
    return "https://www.notion.so/" + page_id.replace("-", "")


def desktop_url(url):
    """notion:// opens the Notion desktop app directly."""
    return url.replace("https://", "notion://", 1)


# ---- text -> Notion blocks ------------------------------------------------
def _rt(text):
    return [{"type": "text", "text": {"content": text[:2000]}}]


def text_to_blocks(text):
    blocks = []
    para = []

    def flush():
        if para:
            chunk = "\n".join(para)
            for i in range(0, len(chunk), 2000):
                blocks.append({"object": "block", "type": "paragraph", "paragraph": {"rich_text": _rt(chunk[i:i + 2000])}})
            para.clear()

    for raw in text.splitlines():
        line = raw.rstrip()
        s = line.strip()
        if not s:
            flush()
        elif s.startswith(("- ", "* ", "• ")):
            flush()
            blocks.append({"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": _rt(s[2:])}})
        elif (s.isupper() and len(s) > 3 and len(s) < 80) or set(s) <= set("=-") and len(s) > 3:
            flush()
            if not set(s) <= set("=-"):
                blocks.append({"object": "block", "type": "heading_3", "heading_3": {"rich_text": _rt(s)}})
        else:
            para.append(line)
    flush()
    return blocks


def append_blocks(page_id, blocks, token=None):
    for i in range(0, len(blocks), 90):
        api("PATCH", f"/blocks/{page_id}/children", {"children": blocks[i:i + 90]}, token=token)


def create_page(parent_id, title, blocks=None, icon=None, token=None):
    body = {"parent": {"page_id": parent_id},
            "properties": {"title": {"title": _rt(title)}}}
    if icon:
        body["icon"] = {"type": "emoji", "emoji": icon}
    blocks = blocks or []
    body["children"] = blocks[:90]
    page = api("POST", "/pages", body, token=token)
    if len(blocks) > 90:
        append_blocks(page["id"], blocks[90:], token=token)
    return page


# ---- progress rows -------------------------------------------------------
STATUS_NAME = {"DONE": "Done", "SKIP": "Skipped", "UNDO": "Not started"}


def row_properties(entry, status="Not started"):
    b = entry["blocks"][0]
    return {
        "Lesson": {"title": _rt(entry["title"])},
        "Date": {"date": {"start": entry["date"]}},
        "Track": {"select": {"name": b["label"].split(":")[0][:90]}},
        "Status": {"select": {"name": status}},
        "Minutes": {"number": sum(x["minutes"] for x in entry["blocks"])},
    }


def push_status(entry, status_code):
    """Called by today.py in a background thread. Returns a short message."""
    cfg = load_config()
    if not (load_token() and cfg.get("progress_db_id")):
        return "Notion not connected"
    status = STATUS_NAME.get(status_code, "Not started")
    rows = cfg.setdefault("rows", {})
    pid = rows.get(entry["date"])
    if pid:
        api("PATCH", f"/pages/{pid}", {"properties": {"Status": {"select": {"name": status}}}})
    else:
        page = api("POST", "/pages", {"parent": {"database_id": cfg["progress_db_id"]},
                                      "properties": row_properties(entry, status)})
        rows[entry["date"]] = page["id"]
        save_config(cfg)
    return f"Notion: {status}"


def ensure_notes_page(entry, block):
    """Return the Notion URL for a block's notes, creating the page on first use."""
    cfg = load_config()
    folders = cfg.setdefault("folders", {})
    key = block["folder"]
    if key in folders:
        return folders[key]
    parent = cfg.get("daily_notes_page_id")
    if not parent:
        return None
    intro = [
        {"object": "block", "type": "callout", "callout": {"rich_text": _rt(
            f"Started {entry['date']}: {block['label']}\nGoal: {block.get('learn', '')}\nTask: {block['task']}"),
            "icon": {"type": "emoji", "emoji": "🎯"}}},
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": _rt("Notes (interview points)")}},
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": []}},
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": _rt("Journal - what I learned + where I went wrong")}},
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": []}},
    ]
    page = create_page(parent, key.replace("\\", " / "), intro, icon="📒")
    folders[key] = page_url(page["id"])
    save_config(cfg)
    return folders[key]
