"""Хранит историю и следующий шаг одним атомарным обновлением."""
import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("action", choices=["init", "save", "status"])
parser.add_argument("folder", type=Path)
parser.add_argument("notes", nargs="*")
args = parser.parse_args()
path = args.folder / "state" / "current.json"
if args.action == "init":
    path.parent.mkdir(parents=True, exist_ok=True)
    (args.folder / "materials").mkdir(exist_ok=True)
    try:
        with path.open("x") as out:
            json.dump({"history": [], "next": "Уточнить решение и материалы"}, out, ensure_ascii=False)
    except FileExistsError:
        pass
if not path.exists():
    parser.exit(1, "Кейс отсутствует. Начните с init.\n")
if args.action == "save":
    if len(args.notes) != 2:
        parser.error("укажите завершённый и следующий шаг в кавычках")
    import sqlite3
    lock = sqlite3.connect(str(path.parent / ".lock.sqlite"), isolation_level=None)
    lock.execute("BEGIN IMMEDIATE")
    with lock:
        state = json.loads(path.read_text())
        event = {"time": datetime.now(timezone.utc).isoformat(), "done": args.notes[0], "next": args.notes[1]}
        if not state["history"] or any(state["history"][-1][k] != event[k] for k in ("done", "next")):
            state["history"].append(event)
            state["next"] = event["next"]
            with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as out:
                json.dump(state, out, ensure_ascii=False, indent=2)
            os.replace(out.name, path)
state = json.loads(path.read_text())
for event in state["history"]:
    print("✓", event["done"])
print("Далее —", state["next"])
