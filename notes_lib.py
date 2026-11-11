"""
notes_lib.py - reading, cleaning and saving the Markdown notes shown in the Notes view.

Kept separate from the window code so every rule here can be tested on its own.

Where notes live
  notes/<subject>/<NN>-<name>.md    one note per file; the folder is the subject
  The first line "# Title" is the note's name in the list. The NN number sets the order.
  Folders starting with "_" or "." are ignored (notes/_trash holds removed notes).
  .md, .markdown and .txt files are all read. Files saved straight into notes/ show as "Unsorted".
"""
import re
from pathlib import Path

NOTE_SUFFIXES = (".md", ".markdown", ".txt")
FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})")
HEADING = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t#]*$")
RULE = re.compile(r"^[ \t]*(-{3,}|\*{3,}|_{3,})[ \t]*$")
LIST_OR_TABLE = re.compile(r"^[ \t]*([-*+>|]|\d+[.)])[ \t]")
CHAT_LEAD = re.compile(r"(?i)^\W*(sure|okay|ok|great|certainly|absolutely|alright|of course|perfect|"
                       r"here(?:'s| is| are)|below is|let'?s (?:start|begin|go))\b")
CHAT_TAIL = re.compile(r"(?i)(\bnext\b|let me know|shall i|want me to|would you like|ready for|"
                       r"when you(?:'re| are) ready|hope this helps|happy to help|feel free)")


# ---------------------------------------------------------------- small helpers
def read_note(path):
    """Text of a note file. Copes with a BOM, Windows line endings and files saved as ANSI."""
    data = Path(path).read_bytes()
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            text = data.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = data.decode("utf-8", errors="replace")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def slugify(text, limit=50):
    """'Virtual environments & pip!' -> 'virtual-environments-pip'"""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:limit].rstrip("-") or "note"


def clean_title(text):
    """Strip Markdown marks and 'Note 1 of 6:' style prefixes from a title."""
    title = re.sub(r"[*_`]+", "", text).strip()
    title = re.sub(r"(?i)^(note|part|lesson|chapter|day)\s*#?\d+\s*(of\s*\d+)?\s*[:.\-–—|]+\s*", "", title)
    title = re.sub(r"^\d+[.)]\s+", "", title)
    return title.strip() or "Untitled note"


def code_mask(lines):
    """(mask, still_open): mask[i] is True when line i is a code fence or inside a code block."""
    mask, inside, fence = [], False, ""
    for line in lines:
        if not inside:
            m = FENCE.match(line)
            if m:
                inside, fence = True, m.group(1)
            mask.append(bool(m))
        else:
            if re.fullmatch(re.escape(fence[0]) + "{%d,}" % len(fence), line.strip()):
                inside = False
            mask.append(True)
    return mask, inside


def title_lines(lines):
    """Indexes of '# ' title lines that are not inside code blocks."""
    mask, _ = code_mask(lines)
    out = []
    for i, line in enumerate(lines):
        m = None if mask[i] else HEADING.match(line)
        if m and m.group(1) == "#":
            out.append(i)
    return out


def title_of(text):
    """The cleaned first '# ' title in the text, or None."""
    lines = text.split("\n")
    found = title_lines(lines)
    return clean_title(HEADING.match(lines[found[0]]).group(2)) if found else None


def set_title(text, title):
    """Replace the first '# ' title, or add one at the top."""
    lines = text.split("\n")
    found = title_lines(lines)
    if found:
        lines[found[0]] = "# " + title
        return "\n".join(lines)
    return "# " + title + "\n\n" + text.lstrip("\n")


def split_notes(text):
    """Split text holding several notes at each '# ' title. Returns the non-empty pieces."""
    lines = text.split("\n")
    cuts = [i for i in title_lines(lines) if i > 0]
    pieces, start = [], 0
    for cut in cuts:
        pieces.append("\n".join(lines[start:cut]))
        start = cut
    pieces.append("\n".join(lines[start:]))
    return [p.strip("\n") for p in pieces if p.strip()]


# ---------------------------------------------------------------- cleaning a pasted AI reply
def clean_pasted(raw):
    """Tidy an AI chat reply into a note. Returns (text, warnings for the person)."""
    warnings = []
    text = (raw or "").replace("\r\n", "\n").replace("\r", "\n")
    for junk in ("﻿", "​", "‌", "‍", "⁠"):
        text = text.replace(junk, "")
    text = text.replace(" ", " ").strip()
    if not text:
        return "", ["The clipboard is empty. Copy the AI's reply first (use its copy button), "
                    "or paste it into the box below."]

    # 1. The whole reply wrapped in one ```markdown block
    m = re.fullmatch(r"(`{3,}|~{3,})[ \t]*([A-Za-z]*)[ \t]*\n(.*)\n[ \t]*\1[ \t]*", text, re.S)
    if m and (m.group(2).lower() in ("markdown", "md")
              or (not m.group(2) and re.search(r"(?m)^#{1,3} ", m.group(3)))):
        text = m.group(3).strip()
        warnings.append("Removed the code block wrapped around the whole reply.")

    lines = text.split("\n")
    mask, _ = code_mask(lines)
    headings = [i for i, line in enumerate(lines) if not mask[i] and HEADING.match(line)]

    # 2. Chat before the title: "Sure! Here is note 1:"
    if headings and headings[0] > 0:
        lead = [line for line in lines[:headings[0]] if line.strip()]
        if lead and len(lead) <= 3 and CHAT_LEAD.search(lead[0]) and not any(mask[:headings[0]]):
            lines = lines[headings[0]:]
            warnings.append("Removed %d line(s) of chat before the title." % len(lead))

    # 3. Make sure there is a '# ' title at the top
    mask, _ = code_mask(lines)
    if not title_lines(lines):
        first = next((i for i, line in enumerate(lines) if line.strip()), None)
        if first is not None and not mask[first]:
            m = HEADING.match(lines[first])
            if m:
                lines[first] = "# " + clean_title(m.group(2))
                warnings.append("Made the first heading the title.")
            elif len(lines[first]) <= 90 and not LIST_OR_TABLE.match(lines[first]):
                lines[first] = "# " + clean_title(lines[first])
                warnings.append("Used the first line as the title.")
            else:
                warnings.append("No title line found. Type a title above.")
        else:
            warnings.append("No title line found. Type a title above.")

    # 4. Tidy every title line ("# **Note 2: SQL joins**" -> "# SQL joins")
    for i in title_lines(lines):
        lines[i] = "# " + clean_title(HEADING.match(lines[i]).group(2))

    # 5. Chat after the note: "Say next for note 2." Only short, plain, non-list lines at the very end.
    mask, still_open = code_mask(lines)
    dropped = 0
    if not still_open:
        while lines:
            last = lines[-1]
            if not last.strip():
                lines.pop()
                continue
            i = len(lines) - 1
            plain = not mask[i] and not HEADING.match(last) and not LIST_OR_TABLE.match(last)
            if plain and RULE.match(last):
                lines.pop()
                continue
            if plain and dropped < 3 and len(last) < 220 and CHAT_TAIL.search(last):
                lines.pop()
                dropped += 1
                continue
            break
    if dropped:
        warnings.append("Removed %d line(s) of chat at the end." % dropped)

    # 6. A reply cut off in the middle of a code block
    _, still_open = code_mask(lines)
    if still_open:
        lines.append("```")
        warnings.append("A code block was never closed, so the reply was probably cut off. "
                        "Ask the AI to continue, or check the end of the note.")

    text = "\n".join(lines).strip()
    mask, _ = code_mask(text.split("\n"))
    has_markdown = any(mask) or any(HEADING.match(line) or LIST_OR_TABLE.match(line)
                                    for line in text.split("\n"))
    if not has_markdown:
        warnings.append("No Markdown formatting found. You probably selected the text on the screen: "
                        "use the copy button under the AI's reply instead.")
    if len(text) < 300:
        warnings.append("This note is very short.")
    elif "check yourself" not in text.lower():
        warnings.append("No 'Check yourself' section, so the reply may be cut off or incomplete.")
    return text, warnings


# ---------------------------------------------------------------- guessing the subject
SUBJECT_WORDS = {
    "iot": ["esp32", "micropython", "gpio", "breadboard", "oled", "ssd1306", "mpu6050", "arduino", "sensor", "i2c"],
    "python": ["python", "pip", "venv", "pytest", "argparse", "pathlib", "traceback", "virtual environment"],
    "java": ["java", "jvm", "jdk", "javac", "spring", "maven"],
    "dsa-java": ["linked list", "binary search", "big-o", "recursion", "heap", "dynamic programming", "two pointers"],
    "git": ["git", "github", "commit", "branch", "merge", "rebase", "pull request"],
    "sql": ["sql", "select", "join", "group by", "window function", "cte"],
    "dbms": ["database", "index", "transaction", "schema", "postgresql", "normalisation", "normalization"],
    "os": ["linux", "terminal", "bash", "process", "chmod", "systemd", "kernel", "wsl"],
    "networks": ["network", "dns", "tcp", "subnet", "router", "wireshark", "ip address", "ping", "traceroute", "vpn"],
    "cloud": ["aws", "ec2", "s3", "iam", "azure", "gcp", "lambda", "cloud"],
    "numpy-pandas": ["pandas", "numpy", "dataframe", "matplotlib", "seaborn", "csv"],
    "machine-learning": ["scikit-learn", "sklearn", "regression", "classification", "overfitting", "cross-validation",
                         "feature engineering", "kaggle"],
    "deep-learning": ["pytorch", "tensor", "neural network", "cnn", "gpu", "cuda", "epoch", "backpropagation"],
    "genai": ["llm", "prompt", "rag", "embedding", "ollama", "token", "hallucination", "vector"],
    "deployment": ["docker", "fastapi", "deploy", "render", "github actions", "container", "https", "nginx"],
    "career": ["resume", "linkedin", "interview", "internship", "recruiter", "freelanc", "portfolio"],
}


def guess_subject(text):
    """Best-matching subject folder for a note, or None when the text is not clearly about one subject."""
    title = (title_of(text) or "").lower()
    body = text.lower()
    scores = {}
    for subject, words in SUBJECT_WORDS.items():
        score = 0
        for word in words:
            pattern = r"(?<![a-z0-9])" + re.escape(word)
            score += 4 * len(re.findall(pattern, title)) + min(3, len(re.findall(pattern, body)))
        scores[subject] = score
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    best, second = ranked[0], ranked[1]
    if best[1] >= 6 and best[1] >= 1.5 * second[1]:
        return best[0]
    return None


# ---------------------------------------------------------------- the notes folder
def _natural(path):
    m = re.match(r"(\d+)", path.name)
    return (int(m.group(1)) if m else 10 ** 9, path.name.lower())


def note_files(folder):
    """Note files in one folder, in number order (2 before 10)."""
    try:
        files = [p for p in Path(folder).iterdir()
                 if p.is_file() and p.name.lower().endswith(NOTE_SUFFIXES) and not p.name.startswith((".", "_", "~"))]
    except OSError:
        return []
    return sorted(files, key=_natural)


def note_title(path):
    """The note's '# ' title, or a name made from the file name."""
    try:
        text = read_note(path)
    except OSError:
        text = ""
    for line in text.split("\n")[:60]:
        if line.strip():
            m = HEADING.match(line.strip())
            if m and m.group(1) == "#":
                return clean_title(m.group(2))
            break
    stem = re.sub(r"\.(md|markdown)$", "", Path(path).stem, flags=re.I)
    stem = re.sub(r"^\d+[-_ ]*", "", stem).replace("-", " ").replace("_", " ").strip()
    return stem[:1].upper() + stem[1:] if stem else Path(path).name


def group_label(folder_name, groups):
    return groups.get(folder_name, folder_name.replace("-", " ").replace("_", " ").title())


def subject_folders(notes_dir):
    try:
        return [d for d in Path(notes_dir).iterdir() if d.is_dir() and not d.name.startswith(("_", "."))]
    except OSError:
        return []


def load_notes(notes_dir, groups):
    """[(group label, [(title, path), ...]), ...] in the order of `groups`, then the rest A to Z."""
    notes_dir = Path(notes_dir)
    known = list(groups)
    out = []
    for folder in sorted(subject_folders(notes_dir),
                         key=lambda d: (known.index(d.name) if d.name in known else len(known), d.name)):
        items = [(note_title(p), p) for p in note_files(folder)]
        if items:
            out.append((group_label(folder.name, groups), items))
    loose = [(note_title(p), p) for p in note_files(notes_dir)] if notes_dir.is_dir() else []
    if loose:
        out.append(("Unsorted (move into a subject folder)", loose))
    return out


def subjects(notes_dir, groups):
    """[(folder name, label), ...] for the subject picker: known subjects first, then any others."""
    names = list(groups) + sorted(d.name for d in subject_folders(notes_dir) if d.name not in groups)
    return [(name, group_label(name, groups)) for name in names]


def existing_titles(folder):
    """lower-case title -> path, for notes already in a folder."""
    return {note_title(p).lower(): p for p in note_files(folder)}


def plan_paths(folder, titles):
    """File paths for new notes: the next free numbers, two digits, plus a name from the title."""
    folder = Path(folder)
    numbers = [int(m.group(1)) for p in note_files(folder) for m in [re.match(r"(\d+)", p.name)] if m]
    n = max(numbers, default=0) + 1
    paths = []
    for title in titles:
        while True:
            path = folder / ("%02d-%s.md" % (n, slugify(title)))
            n += 1
            if not path.exists() and path not in paths:
                break
        paths.append(path)
    return paths
