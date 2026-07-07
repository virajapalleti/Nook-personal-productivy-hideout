import json
import os
import shutil
import sys
import tempfile


def get_data_path():
    if getattr(sys, "frozen", False):
        # running as a PyInstaller exe — store data next to the exe,
        # not the temp extraction dir __file__ would point to
        base = os.path.dirname(sys.executable)
    else:
        # running as a plain python script
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "data.json")


PATH = get_data_path()

DEFAULT = {
    "accent": "#4EC9B0",
    "bg": "#1e1e1e",
    "expanded": [],
    "categories": []
}


def _normalize(d):
    """Patch missing keys and repair malformed categories/tasks so the UI
    never hits a KeyError on old or hand-edited data files."""
    if not isinstance(d, dict):
        return dict(DEFAULT)
    for k, v in DEFAULT.items():
        if k not in d:
            d[k] = list(v) if isinstance(v, list) else v
    if not isinstance(d["categories"], list):
        d["categories"] = []
    if not isinstance(d["expanded"], list):
        d["expanded"] = []
    cats = []
    for cat in d["categories"]:
        if not isinstance(cat, dict) or not str(cat.get("name", "")).strip():
            continue
        cat["name"] = str(cat["name"])
        tasks = []
        for t in cat.get("tasks", []) if isinstance(cat.get("tasks"), list) else []:
            if not isinstance(t, dict) or not str(t.get("text", "")).strip():
                continue
            tasks.append({"text": str(t["text"]), "done": bool(t.get("done", False))})
        cat["tasks"] = tasks
        cats.append(cat)
    d["categories"] = cats
    return d


def load():
    if not os.path.exists(PATH):
        save(DEFAULT)
        return dict(DEFAULT)
    try:
        with open(PATH, "r", encoding="utf-8") as f:
            d = json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        # corrupted file — keep a backup for the user, start fresh
        try:
            shutil.copyfile(PATH, PATH + ".corrupt.bak")
        except OSError:
            pass
        save(DEFAULT)
        return dict(DEFAULT)
    return _normalize(d)


def save(data):
    # atomic write: dump to a temp file in the same directory, then
    # os.replace() it over data.json so a crash mid-write can never
    # leave a half-written (corrupted) file behind
    dir_ = os.path.dirname(PATH)
    fd, tmp = tempfile.mkstemp(prefix=".data-", suffix=".tmp", dir=dir_)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, PATH)
    except OSError:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise