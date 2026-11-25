"""
build_roadmap.py - generates roadmap.json (read by today.py) and roadmap.txt.

DAILY = learning NEW related topics (skills for AI/ML jobs). No semester/CA/exam work here;
that is handled separately by talking to Claude directly.

Edit the lists below, then run:  python build_roadmap.py
Safe to rerun: progress.txt (your Done/Skip/Undo log) is never touched.
"""
import json
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
D = date.fromisoformat
START, END = D("2026-11-02"), D("2027-12-31")

# Time per day (change here if you want more/less)
WEEKDAY_MIN, WEEKEND_MIN, LIGHT_MIN = 60, 90, 30
# Exam seasons: lessons shrink to 30-min "mini" lessons, weekends are rest.
LIGHT_WINDOWS = [(D("2026-11-02"), D("2026-11-05")),   # CA week (Networking 3 Nov, Python 5 Nov)
                 (D("2026-12-05"), D("2027-01-06"))]   # end-terms 18-28 Dec + practicals 1-6 Jan

F = {"py": "Python", "git": "Git", "sql": "SQL", "linux": "Linux", "math": "Maths", "cs": "How-Things-Work",
     "np": "NumPy-Pandas", "dsa": "DSA", "ml": "Machine-Learning", "dl": "Deep-Learning",
     "genai": "GenAI", "deploy": "Deployment", "proj": "Projects", "review": "Weekly-Review"}


def lesson(track, topic, learn, task, done_when, folder, minutes):
    return {"label": f"{track}: {topic}", "minutes": minutes, "learn": learn, "task": task,
            "done_when": done_when, "folder": folder}


def in_light(d):
    return any(a <= d <= b for a, b in LIGHT_WINDOWS)


# ---------------------------------------------------------------------------
# 1) MINI lessons (30 min) for exam seasons - small, new, interesting
# ---------------------------------------------------------------------------
MINI = [
    ("How things work", "What happens when you open a website", "DNS lookup -> TCP connection -> HTTPS -> HTML -> browser renders.", "Open DevTools (F12) > Network tab, reload google.com, look at the first request.", "You can tell the story in 5 steps.", "cs"),
    ("How things work", "How Python runs your code", "Source -> bytecode -> Python virtual machine. Why Python is 'interpreted'.", "Run: python -c \"import dis; dis.dis('a=1+2')\" and look at the bytecode.", "You can explain .pyc files.", "cs"),
    ("How things work", "Binary, bits and bytes", "Why computers use 0/1, how numbers and text (ASCII/UTF-8) become bits.", "Convert 13, 42, 255 to binary by hand; check with bin() in Python.", "3 conversions correct.", "cs"),
    ("How things work", "What is an API?", "A menu of requests one program can make to another. REST, endpoints, request/response.", "Open https://api.github.com/users/aadityaasony in your browser and read the JSON.", "You can explain API with a restaurant example.", "cs"),
    ("How things work", "JSON in 30 minutes", "Objects, arrays, strings, numbers, true/false/null. json.loads / json.dumps.", "Write a JSON file describing yourself (skills list, projects), load it in Python.", "Loads without error.", "cs"),
    ("How things work", "HTTP methods + status codes", "GET/POST/PUT/DELETE; 200, 201, 301, 400, 401, 403, 404, 500.", "Use Python requests (or urllib) to GET a URL and print status_code.", "You know 401 vs 403.", "cs"),
    ("Linux", "Navigating like a pro", "pwd, ls -la, cd, mkdir -p, cp, mv, rm, tree, relative vs absolute paths.", "In Git Bash make a folder tree for a fake project in 10 commands.", "Done without the mouse.", "linux"),
    ("Linux", "Pipes, grep, find", "| pipes, grep -i -n -r, find -name, wc -l, head/tail.", "Count how many .py files you have under E:\\ with find + wc.", "One-liner works.", "linux"),
    ("Linux", "Permissions, processes, env vars", "chmod/rwx, ps, kill, top, $PATH, export.", "Print your PATH, add a test variable, read it back.", "You can explain what PATH does.", "linux"),
    ("Linux", "Your first bash script", "Shebang, variables, if, for loop, arguments $1.", "Script that backs up a folder into a dated zip.", "Script runs.", "linux"),
    ("How things work", "Virtual environments + pip", "Why venvs exist, python -m venv, pip install, requirements.txt.", "Make a venv, install requests, freeze to requirements.txt.", "requirements.txt exists.", "cs"),
    ("How things work", "Regex basics", "\\d \\w \\s . * + ? [] ^ $ groups. re.findall / re.sub.", "Extract all emails and phone numbers from a paragraph with re.", "Regex works on 3 test lines.", "cs"),
    ("How things work", "What is Docker (really)?", "Image vs container, why 'works on my machine' happens, Dockerfile idea.", "Read one Dockerfile on GitHub and explain each line in notes.", "Every line explained.", "cs"),
    ("How things work", "What is an LLM token?", "Text -> tokens -> numbers; why models have context limits; temperature.", "Paste a sentence into an online tokenizer and count tokens vs words.", "You know why tokens != words.", "cs"),
    ("How things work", "Big-O intuition", "O(1), O(n), O(n^2), O(log n) with everyday examples.", "Time a loop for n=1e3,1e4,1e5 and see the growth.", "You can guess Big-O of a nested loop.", "cs"),
    ("Maths", "Exponents + logarithms", "a^m*a^n, log as 'how many times do I multiply', log2 in computer science.", "10 practice questions; compute log2(1024) by thinking.", "10 done.", "math"),
    ("Maths", "Functions + graphs", "f(x), linear vs quadratic vs exponential shapes, slope.", "Plot y=2x+1, y=x^2, y=2^x with matplotlib.", "3 plots.", "math"),
    ("Maths", "Sets + logic", "Union, intersection, difference, AND/OR/NOT, truth tables.", "Do set ops in Python; write a truth table for (A and not B).", "Truth table correct.", "math"),
    ("Maths", "Vectors (what ML actually uses)", "A list of numbers with direction; addition, scaling, length.", "Add/scale vectors with NumPy; compute length with np.linalg.norm.", "You can explain a vector as an arrow.", "math"),
    ("Maths", "Dot product", "Sum of products; measures similarity; used in every neural network.", "Compute dot product by hand and with np.dot; cosine similarity of 2 sentences' word counts.", "Hand and NumPy answers match.", "math"),
    ("Maths", "Matrices", "Table of numbers; shape; matrix x vector.", "Multiply a 2x3 by 3x1 by hand and with NumPy.", "Shapes make sense to you.", "math"),
    ("Maths", "Probability basics", "Events, P(A), complement, independent events.", "Simulate 10,000 coin flips and dice rolls in Python.", "Simulation matches theory.", "math"),
    ("Maths", "Mean, median, variance, std", "Centre and spread; why ML scales features.", "Compute all 4 by hand for 6 numbers, check with statistics module.", "Matches.", "math"),
    ("Maths", "Derivative intuition", "Slope at a point; how fast something changes; why gradient descent needs it.", "Approximate slope of x^2 at x=3 with (f(x+h)-f(x))/h.", "You get close to 6.", "math"),
    ("How things work", "How Git stores history", "Snapshots, hashes, HEAD, branches are just pointers.", "Run git log --oneline --graph in any repo and identify HEAD.", "You can explain 'a branch is a pointer'.", "git"),
    ("How things work", "How a search engine ranks pages", "Crawling, indexing, ranking; TF-IDF idea.", "Write a tiny word-count 'search' over 3 text files in Python.", "Search returns the right file.", "cs"),
    ("How things work", "What is a recommendation system?", "Content-based vs collaborative filtering (Netflix/YouTube).", "Recommend movies from a 5x5 ratings table using similarity.", "Gives a sensible recommendation.", "cs"),
]

# ---------------------------------------------------------------------------
# 2) FULL handcrafted lessons (weekdays, 6 Nov - 4 Dec): Python -> Git -> SQL
# ---------------------------------------------------------------------------
FULL = [
    ("Python", "Data types, strings, lists, dicts, sets", "Mutable vs immutable; when to use list vs dict vs set.", "Solve 5 small problems: reverse words, count chars with dict, remove duplicates, merge 2 dicts, list stats.", "5 programs run.", "py"),
    ("Python", "Functions, *args/**kwargs, scope, lambda", "LEGB scope; default-argument trap.", "Write 4 functions using defaults, *args, **kwargs; sort with key=lambda.", "You can explain LEGB.", "py"),
    ("Python", "Comprehensions, iterators, generators", "Lazy evaluation; yield vs return.", "Rewrite 3 loops as comprehensions; Fibonacci generator.", "You know when a generator saves memory.", "py"),
    ("Python", "Classes the real way", "self, class vs instance variables, @classmethod, @staticmethod.", "Student class with a class-level counter and from_string().", "You can explain self.", "py"),
    ("Python", "Inheritance + dunder methods", "super(), MRO, __str__, __eq__, __add__.", "Vector class with + and ==; Shape -> Circle/Rectangle.", "print(Class.__mro__) makes sense.", "py"),
    ("Python", "Abstraction + @property", "ABC, abstract methods, validation with properties.", "Payment ABC with UPI/Card; balance property that rejects negatives.", "Abstract class can't be instantiated, and you know why.", "py"),
    ("Python", "Errors + files", "try/except/else/finally, custom exceptions, with-open, CSV, JSON.", "Read a CSV, compute averages, write JSON, handle bad rows.", "Bad input doesn't crash it.", "py"),
    ("Python", "Modules, packages, decorators", "__init__.py, imports, how decorators wrap functions.", "A @timer decorator + a 2-module package.", "Package imports from another folder.", "py"),
    ("Git", "How Git really works", "Working dir -> staging -> commit; diff, log.", "Practice repo: 5 commits, git diff --staged, git log --oneline --graph.", "You can say what staging is for.", "git"),
    ("Git", "Branches + merge + conflict on purpose", "Fast-forward vs 3-way merge.", "2 branches edit the same line -> merge -> resolve conflict by hand.", "Conflict resolved by you.", "git"),
    ("Git", "Undo + rollback", "restore, reset --soft/--mixed/--hard, revert, reflog, stash.", "Commit junk, undo it 4 ways; rescue a 'lost' commit with reflog.", "You know revert is safe on shared branches, reset isn't.", "git"),
    ("Git", "Collaboration", "remote, fetch vs pull, push, fork, pull request, review.", "Fork a repo (or use a 2nd account), open a PR, review, merge.", "1 PR merged.", "git"),
    ("Git", "Rebase, tags, team workflow", "Rebase vs merge; never rebase shared history.", "Rebase a feature branch; write a 1-page Git cheat sheet.", "Cheat sheet written.", "git"),
    ("SQL", "SELECT, WHERE, ORDER BY, functions", "How a query is read: FROM -> WHERE -> SELECT -> ORDER.", "employees table (10 rows) in SQLite; 10 queries.", "10 correct.", "sql"),
    ("SQL", "GROUP BY + HAVING", "Aggregates; WHERE vs HAVING.", "8 queries: count per dept, avg salary > X, max per group.", "You know WHERE vs HAVING.", "sql"),
    ("SQL", "Joins", "Inner, left, right, self; Venn picture.", "departments table + 8 join queries incl. employee-manager self join.", "Venn diagram for each join.", "sql"),
    ("SQL", "Subqueries", "Nested queries, IN vs EXISTS, correlated subqueries.", "Second-highest salary 3 ways; employees above dept average.", "Second-highest without looking.", "sql"),
    ("SQL", "Window functions (interview favourite)", "ROW_NUMBER, RANK, DENSE_RANK, PARTITION BY, running totals.", "Top-2 earners per dept; running total of sales.", "Both queries work.", "sql"),
    ("SQL", "Indexes + query speed", "What an index is (book index), when it helps, EXPLAIN.", "Insert 100k rows with Python, time a query before/after CREATE INDEX.", "You saw the speed difference.", "sql"),
    ("SQL", "SQL from Python + pandas", "sqlite3 module, parameterised queries (SQL injection!), pd.read_sql.", "Load a CSV into SQLite, query it into a DataFrame.", "No string-formatted SQL anywhere.", "sql"),
    ("SQL", "10 classic interview queries", "Duplicates, Nth highest, consecutive days, pivots.", "Solve 10 on LeetCode/HackerRank SQL (easy-medium).", "10 solved.", "sql"),
]
WEEKEND_PROJECT = {  # what to build on Saturdays, by current track
    "Python": "Build a CLI Expense Tracker (add/list/delete expenses, save to JSON) using this week's Python.",
    "Git": "Put the Expense Tracker on GitHub: use a feature branch + a pull request for one new feature.",
    "SQL": "Move the Expense Tracker to SQLite: monthly totals and top categories with SQL.",
}

# ---------------------------------------------------------------------------
# 3) WEEKLY themes (Mon-Fri lessons follow a 5-step pattern)
# ---------------------------------------------------------------------------
PATTERN = ["Learn: read/watch 1 good explanation, write notes in your own words.",
           "Build: code it from scratch (no shortcuts).",
           "Apply: use it on a small real dataset/problem.",
           "Go deeper: one variation, edge case or harder problem.",
           "Recap: quiz yourself (press 'Teach me' -> ask Claude to quiz you), redo the hardest bit."]
WEEKS = (
    [("NumPy-Pandas", "NumPy arrays, broadcasting, vectorisation", "np"),
     ("NumPy-Pandas", "Pandas: DataFrames, filtering, groupby, merge", "np"),
     ("NumPy-Pandas", "Visualisation + EDA (Matplotlib/Seaborn) on a Kaggle dataset", "np")] +
    [("DSA", t, "dsa") for t in [
        "Big-O + complexity", "Arrays: prefix sums, Kadane", "Strings", "Hashing (dict/set)", "Two pointers",
        "Sliding window", "Recursion + backtracking basics", "Sorting: merge + quick", "Binary search",
        "Linked lists", "Stacks", "Queues + deques", "Trees: traversals", "Binary search trees",
        "Heaps / priority queue", "Graphs: BFS + DFS", "Graphs: shortest path + topo sort", "Greedy",
        "Dynamic programming 1 (1D)", "Dynamic programming 2 (2D)"]] +
    [("Machine-Learning", t, "ml") for t in [
        "Linear regression from scratch (gradient descent)", "Logistic regression + log loss",
        "kNN + decision trees", "Random forests + gradient boosting (XGBoost)",
        "Model evaluation: train/test, cross-validation, metrics", "Feature engineering + data leakage",
        "Clustering (K-Means, DBSCAN) + PCA", "scikit-learn pipelines end-to-end"]] +
    [("Deep-Learning", t, "dl") for t in [
        "Neural network from scratch (NumPy)", "PyTorch basics: tensors, autograd, training loop",
        "CNNs for images", "RNN/LSTM intuition", "Transformers + attention (intuition)",
        "Hugging Face: using pretrained models"]] +
    [("GenAI", t, "genai") for t in [
        "LLM APIs: calling a model from Python", "Prompt engineering properly", "Embeddings + vector search",
        "RAG: chat with your own PDFs", "AI agents + tool use basics"]] +
    [("Deployment", t, "deploy") for t in [
        "FastAPI: serve a model as an API", "Docker your ML app", "GitHub Actions: tests + CI",
        "Deploy free (Hugging Face Spaces / Render)"]]
)

# ---------------------------------------------------------------------------
# Generate days
# ---------------------------------------------------------------------------
entries = {}


def add(d, phase, title, blocks, why, mode):
    entries[d.isoformat()] = {"date": d.isoformat(), "phase": phase, "title": title, "mode": mode,
                              "blocks": blocks, "why": why}


mini_i = full_i = week_i = 0
week_day = 0          # 0..4 within current weekly theme
current_track = "Python"
d = START
while d <= END:
    wd = d.weekday()
    if in_light(d):
        if wd < 5 and mini_i < len(MINI):
            tr, tp, lr, tk, dw, fk = MINI[mini_i]; mini_i += 1
            add(d, "Light season (exams) - 30-min mini lessons", f"{tr}: {tp}",
                [lesson(tr, tp, lr, tk, dw, F[fk], LIGHT_MIN)],
                "Exams this period: keep the habit alive with a tiny new topic.", "mini")
        else:
            add(d, "Light season (exams)", "Rest day",
                [lesson("Rest", "No lesson today", "Rest is part of the plan.", "Optional: redo any mini lesson you liked.",
                        "You rested.", F["review"], 0)],
                "Exam weekends are for exams.", "rest")
    elif full_i < len(FULL):
        if wd < 5:
            tr, tp, lr, tk, dw, fk = FULL[full_i]; full_i += 1; current_track = tr
            add(d, f"Track: {tr}", f"{tr}: {tp}", [lesson(tr, tp, lr, tk, dw, F[fk], WEEKDAY_MIN)],
                "One track at a time: finish it, then move on.", "lesson")
        elif wd == 5:
            add(d, f"Track: {current_track}", f"Build day: {current_track}",
                [lesson("Project", f"Build with {current_track}", "Using it > reading about it.",
                        WEEKEND_PROJECT[current_track], "Committed to GitHub.", F["proj"], WEEKEND_MIN)],
                "Projects are what you'll show in interviews.", "build")
        else:
            add(d, f"Track: {current_track}", "Weekly review",
                [lesson("Review", "This week", "Spaced repetition beats re-reading.",
                        "Re-read this week's notes, press 'Teach me' and ask Claude to quiz you on the week, "
                        "write 'WHERE I WENT WRONG' in the journal.", "Journal updated.", F["review"], WEEKEND_MIN)],
                "Review turns lessons into memory.", "review")
    else:
        if week_i >= len(WEEKS):
            week_i = len(WEEKS) - 1  # stays on the last theme; extend WEEKS to plan further
        tr, theme, fk = WEEKS[week_i]
        if wd < 5:
            if wd == 0 or week_day == 0:
                week_day = 0
            step = PATTERN[min(week_day, 4)]
            add(d, f"Track: {tr}", f"{tr}: {theme} (day {week_day+1}/5)",
                [lesson(tr, theme, step.split(":")[0], step, "Code or notes saved for today.",
                        F[fk] + "\\" + theme.split(":")[0].split("(")[0].strip().replace(" ", "-").replace("/", "-")[:40],
                        WEEKDAY_MIN)],
                "One theme per week, 5 steps: learn, build, apply, deepen, recap.", "lesson")
            week_day += 1
        elif wd == 5:
            add(d, f"Track: {tr}", f"Build day: {theme}",
                [lesson("Project", theme, "Put the week's topic into a real project.",
                        f"Add '{theme}' to one of your projects (or start a small new one). Push to GitHub.",
                        "Committed + pushed.", F["proj"], WEEKEND_MIN)],
                "Projects are what you'll show in interviews.", "build")
        else:
            add(d, f"Track: {tr}", "Weekly review",
                [lesson("Review", theme, "Spaced repetition beats re-reading.",
                        "Quiz yourself with 'Teach me', redo the hardest problem, journal: where I went wrong.",
                        "Journal updated.", F["review"], WEEKEND_MIN)],
                "Review turns lessons into memory.", "review")
            week_i += 1; week_day = 0
    d += timedelta(days=1)

data = {"generated": date.today().isoformat(), "entries": [entries[k] for k in sorted(entries)]}
(HERE / "roadmap.json").write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")

L = ["DAILY LEARNING ROADMAP - new skills only (semester prep is separate, with Claude)", "=" * 72,
     f"Weekdays {WEEKDAY_MIN} min, weekends {WEEKEND_MIN} min, exam seasons {LIGHT_MIN}-min mini lessons.",
     "Generated by build_roadmap.py, so edit that file, not this one.", ""]
cur = None
for e in data["entries"]:
    if e["phase"] != cur:
        cur = e["phase"]; L += ["", cur, "-" * len(cur)]
    if e["mode"] in ("rest",):
        continue
    L.append(f"  {e['date']} {D(e['date']).strftime('%a')}  {e['title']}")
(HERE / "roadmap.txt").write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"{len(data['entries'])} days | minis used {mini_i}/{len(MINI)} | full {full_i}/{len(FULL)} | weekly themes reached {week_i}/{len(WEEKS)}")
