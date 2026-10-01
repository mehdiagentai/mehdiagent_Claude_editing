"""Hook history, so every reel gets a different hook (see ../references/hooks.md).

    python3 hooks.py recent [N]                                   # last N hooks (default 5), newest first
    python3 hooks.py add --style dark --archetype Destroy --prop scythe --line "opening sentence"
    python3 hooks.py check --archetype Race --prop "race track"   # exit 1 + reason if it repeats too soon

Stored in ~/.mehdiagent/hook-history.json (local only, never uploaded).
"""
import argparse, json, sys, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from settings import HOME  # noqa: E402

FILE = HOME / "hook-history.json"

def load() -> list:
    return json.loads(FILE.read_text()) if FILE.is_file() else []

def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("recent"); r.add_argument("n", nargs="?", type=int, default=5)
    a = sub.add_parser("add")
    c = sub.add_parser("check")
    for p in (a, c):
        p.add_argument("--archetype", required=True); p.add_argument("--prop", required=True)
    a.add_argument("--style", default="dark"); a.add_argument("--line", default="")
    args = ap.parse_args()
    hist = load()
    if args.cmd == "recent":
        if not hist:
            print("no hooks recorded yet - anything goes"); return 0
        for h in hist[::-1][:args.n]:
            print(f"{h['date']}  {h['style']:5s}  {h['archetype']:12s}  prop: {h['prop']:14s}  \"{h['line'][:60]}\"")
        return 0
    if args.cmd == "check":
        arch = [h["archetype"].lower() for h in hist[-2:]]
        props = [h["prop"].lower() for h in hist[-5:]]
        problems = []
        if args.archetype.lower() in arch:
            problems.append(f"archetype '{args.archetype}' was used in the last 2 reels")
        if args.prop.lower() in props:
            problems.append(f"prop '{args.prop}' was used in the last 5 reels")
        print("OK - fresh hook" if not problems else "REPEAT: " + "; ".join(problems))
        return 1 if problems else 0
    hist.append({"date": datetime.date.today().isoformat(), "style": args.style, "archetype": args.archetype,
                 "prop": args.prop, "line": args.line})
    HOME.mkdir(parents=True, exist_ok=True)
    FILE.write_text(json.dumps(hist, ensure_ascii=False, indent=1))
    print(f"recorded hook #{len(hist)}: {args.archetype} / {args.prop}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
