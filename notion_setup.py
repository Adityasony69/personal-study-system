"""
notion_setup.py - run ONCE after connecting Notion (safe to rerun: it resumes and skips what's done).

Before running:
  1. notion.so/my-integrations -> New integration -> copy the secret
  2. Add a line to E:\\Vault\\secrets.env:   NOTION_TOKEN=<secret>
  3. In Notion create an empty page named exactly:  Learning Hub
     -> top-right "..." -> Connections -> add your integration
Then:  python notion_setup.py

What it does:
  - finds your "Learning Hub" page
  - creates a "Daily Progress" database with every day of the roadmap (Date, Lesson, Track, Status, Minutes)
  - copies your Done/Skip history from progress.txt
  - copies every notes.txt + journal.txt (and INDEX.txt) from E:\\Learning-Hub into Notion pages
  - creates a "Daily Learning Notes" page where today.py's Notes button makes new pages
  The .txt files are NOT deleted. They stay as an offline backup.
"""
import json
import sys
from pathlib import Path

import notion_sync as ns

HERE = Path(__file__).resolve().parent
HUB = HERE.parent


def main():
    token = ns.load_token()
    if not token:
        sys.exit("NOTION_TOKEN not found in E:\\Vault\\secrets.env - see the steps at the top of this file.")
    cfg = ns.load_config()

    # 1. find the Learning Hub page
    if not cfg.get("hub_page_id"):
        res = ns.api("POST", "/search", {"query": "Learning Hub", "filter": {"property": "object", "value": "page"}})
        hits = [p for p in res.get("results", [])
                if "".join(t["plain_text"] for t in
                           next((v["title"] for v in p.get("properties", {}).values() if v.get("type") == "title"), []))
                .strip().lower() == "learning hub"]
        if not hits:
            sys.exit('Could not see a page called "Learning Hub". Create it and add your integration under '
                     '"..." -> Connections, then run again.')
        cfg["hub_page_id"] = hits[0]["id"]
        ns.save_config(cfg)
    hub = cfg["hub_page_id"]
    print("Found Learning Hub page.")

    # 2. Daily Progress database
    if not cfg.get("progress_db_id"):
        db = ns.api("POST", "/databases", {
            "parent": {"type": "page_id", "page_id": hub},
            "icon": {"type": "emoji", "emoji": "📅"},
            "title": [{"type": "text", "text": {"content": "Daily Progress"}}],
            "properties": {
                "Lesson": {"title": {}},
                "Date": {"date": {}},
                "Track": {"select": {}},
                "Status": {"select": {"options": [
                    {"name": "Not started", "color": "gray"}, {"name": "Done", "color": "green"},
                    {"name": "Skipped", "color": "orange"}]}},
                "Minutes": {"number": {}},
            }})
        cfg["progress_db_id"] = db["id"]
        ns.save_config(cfg)
    print("Daily Progress database ready.")

    # 3. one row per roadmap day (resumable)
    entries = json.loads((HERE / "roadmap.json").read_text(encoding="utf-8"))["entries"]
    status_by_date = {}
    prog = HERE / "progress.txt"
    if prog.exists():
        for line in prog.read_text(encoding="utf-8").splitlines():
            p = line.split("\t")
            if len(p) >= 3 and not line.startswith("#"):
                status_by_date[p[2]] = ns.STATUS_NAME.get(p[1], "Not started")
    rows = cfg.setdefault("rows", {})
    todo = [e for e in entries if e["date"] not in rows and e["mode"] != "rest"]
    for i, e in enumerate(todo, 1):
        page = ns.api("POST", "/pages", {"parent": {"database_id": cfg["progress_db_id"]},
                                         "properties": ns.row_properties(e, status_by_date.get(e["date"], "Not started"))})
        rows[e["date"]] = page["id"]
        if i % 20 == 0 or i == len(todo):
            ns.save_config(cfg)
            print(f"  rows {i}/{len(todo)}")
    # statuses for rows that already existed
    for ds, st in status_by_date.items():
        if ds in rows:
            ns.api("PATCH", f"/pages/{rows[ds]}", {"properties": {"Status": {"select": {"name": st}}}})
    print("Progress rows ready.")

    # 4. Daily Learning Notes parent page
    if not cfg.get("daily_notes_page_id"):
        cfg["daily_notes_page_id"] = ns.create_page(hub, "Daily Learning Notes", icon="📒")["id"]
        ns.save_config(cfg)

    # 5. migrate notes.txt / journal.txt
    folders = cfg.setdefault("folders", {})
    if not cfg.get("library_page_id"):
        cfg["library_page_id"] = ns.create_page(hub, "Study Library (from Learning-Hub)", icon="📚")["id"]
        ns.save_config(cfg)
    subject_pages = cfg.setdefault("subject_pages", {})
    topic_dirs = sorted({p.parent for p in HUB.rglob("*.txt")
                         if p.name in ("notes.txt", "journal.txt") and "00-Roadmap" not in p.parts})
    for td in topic_dirs:
        rel = str(td.relative_to(HUB))
        if rel in folders:
            continue
        subject = td.relative_to(HUB).parts[0]
        if subject not in subject_pages:
            subject_pages[subject] = ns.create_page(cfg["library_page_id"], subject, icon="📁")["id"]
            ns.save_config(cfg)
        blocks = []
        for name, head in (("notes.txt", "Notes (interview points)"), ("journal.txt", "Journal")):
            f = td / name
            if f.exists():
                blocks.append({"object": "block", "type": "heading_2", "heading_2": {"rich_text": ns._rt(head)}})
                blocks += ns.text_to_blocks(f.read_text(encoding="utf-8", errors="replace"))
        topic_title = " / ".join(td.relative_to(HUB).parts[1:]) or subject
        page = ns.create_page(subject_pages[subject], topic_title, blocks, icon="📝")
        folders[rel] = ns.page_url(page["id"])
        ns.save_config(cfg)
        print(f"  migrated {rel}")

    idx = HUB / "INDEX.txt"
    if idx.exists() and not cfg.get("index_page_id"):
        cfg["index_page_id"] = ns.create_page(cfg["library_page_id"], "INDEX",
                                              ns.text_to_blocks(idx.read_text(encoding="utf-8")), icon="🗂️")["id"]
        ns.save_config(cfg)

    print("\nAll done. Open Notion -> Learning Hub.")
    print('Tip: in "Daily Progress" click "+ Add view" -> Calendar (by Date) or Board (by Status).')


if __name__ == "__main__":
    main()
