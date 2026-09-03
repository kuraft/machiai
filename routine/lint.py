#!/usr/bin/env python3
"""台帳の肥大化ガード — 上限を超えたファイルを検出する。コミット前に必ず通す。

  python3 routine/lint.py        → 全部 OK なら終了コード 0、超過があれば 1 と直すべき箇所

原則: 台帳（town/）は「いまの状態」だけを持つ。過去は chronicle/ と git log にある。
      追記で伸ばさず、上書きで保つ。
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOWN = ROOT / "town"

# 文字数の上限（バイトではなく文字）
LIMITS = {
    "meta.weather": 80,
    "meta.note": 300,
    "stats.note": 200,
    "resident_file": 4000,
    "relationships.md": 6000,
    "threads.md": 4000,
    "map.md": 4000,
    "chronicle_body_max": 1500,
    "chronicle_body_min": 250,
    "ledger_line": 400,        # 台帳の 1 行の上限（長大な段落を禁じる）
    "threads_rows": 20,
}
FORBIDDEN = ["過去メモ", "据え置き（上限", "held（"]  # 肥大化の常習表現


def main() -> int:
    errs = []

    def over(label, text, limit, path):
        n = len(text)
        if n > limit:
            errs.append(f"{path}: {label} が {n} 字（上限 {limit}）")

    meta = json.loads((TOWN / "meta.json").read_text(encoding="utf-8"))
    stats = json.loads((TOWN / "stats.json").read_text(encoding="utf-8"))
    if not meta.get("weather"):
        errs.append("town/meta.json: weather が空です（80 字以内で今日の天気を）")
    if not meta.get("note"):
        errs.append("town/meta.json: note が空です（300 字以内で今日の要点を）")
    over("weather", meta.get("weather", ""), LIMITS["meta.weather"], "town/meta.json")
    over("note", meta.get("note", ""), LIMITS["meta.note"], "town/meta.json")
    over("note", stats.get("note", ""), LIMITS["stats.note"], "town/stats.json")
    for key in ("happiness", "liveliness"):
        v = stats.get(key)
        if not isinstance(v, int) or not 0 <= v <= 100:
            errs.append(f"town/stats.json: {key} は 0–100 の整数（いま {v!r}）")

    ledgers = list((TOWN / "residents").glob("*.md")) + [TOWN / "relationships.md", TOWN / "threads.md", TOWN / "map.md"]
    for p in ledgers:
        if not p.exists():
            errs.append(f"{p.relative_to(ROOT)} がありません")
            continue
        text = p.read_text(encoding="utf-8")
        limit = LIMITS["resident_file"] if p.parent.name == "residents" else LIMITS[p.name]
        over("全体", text, limit, p.relative_to(ROOT))
        for i, line in enumerate(text.splitlines(), 1):
            if len(line) > LIMITS["ledger_line"]:
                errs.append(f"{p.relative_to(ROOT)}:{i}: 1 行が {len(line)} 字（上限 {LIMITS['ledger_line']}）— 箇条書きに分けるか削る")
                break
        for w in FORBIDDEN:
            if w in text:
                errs.append(f"{p.relative_to(ROOT)}: 「{w}」を含む — 伏線は threads.md に 1 行で、過去は書かない")
                break
        if p.name == "threads.md":
            rows = [l for l in text.splitlines() if l.startswith("| ") and not l.startswith("| 糸") and not l.startswith("| ---")]
            if len(rows) > LIMITS["threads_rows"]:
                errs.append(f"town/threads.md: 糸が {len(rows)} 本（上限 {LIMITS['threads_rows']}）— 回収した糸を消す")
    for label, text in (("meta.note", meta.get("note", "")), ("stats.note", stats.get("note", ""))):
        for w in FORBIDDEN:
            if w in text:
                errs.append(f"{label}: 「{w}」を含む — 今日のことだけを書く")
                break

    day = meta.get("day")
    if isinstance(day, int):
        f = ROOT / "chronicle" / f"{day:04d}.md"
        if f.exists():
            body = re.sub(r"^(#.*|>.*)$", "", f.read_text(encoding="utf-8"), flags=re.M).strip()
            over("本文", body, LIMITS["chronicle_body_max"], f.relative_to(ROOT))
            if len(body) < LIMITS["chronicle_body_min"]:
                errs.append(f"{f.relative_to(ROOT)}: 本文が {len(body)} 字（下限 {LIMITS['chronicle_body_min']}）")

    cal = subprocess.run([sys.executable, str(ROOT / "routine" / "calendar.py"), "check"], capture_output=True, text=True)
    if cal.returncode != 0:
        errs.append(cal.stdout.strip())

    if errs:
        print("NG: 直してからコミットしてください")
        for e in errs:
            print("  - " + e)
        return 1
    print("OK: 台帳は上限内、暦も整合しています")
    return 0


if __name__ == "__main__":
    sys.exit(main())
