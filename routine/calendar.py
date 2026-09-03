#!/usr/bin/env python3
"""汐入町の暦 — 通算日数から日付・曜日・季節・行事を決定論的に導く。

使い方:
  python3 routine/calendar.py show [N]      通算 N 日目（省略時は meta.json の day）の暦を表示
  python3 routine/calendar.py next          翌日の暦を表示（meta.json は書き換えない）
  python3 routine/calendar.py next --write  翌日へ進め、meta.json の暦フィールドを書き換える
  python3 routine/calendar.py check         meta.json と chronicle の整合を検査（不整合なら終了コード 1）

暦の定義（変更するときはこのファイルだけを直す）:
  - 第1日 = 2026-04-06（月）。以後 1 日ずつ進む。うるう年は datetime に任せる。
  - 季節は月日で固定:  春 3/1–6/4 ／ 梅雨 6/5–7/19 ／ 夏 7/20–8/31 ／ 秋 9/1–11/30 ／ 冬 12/1–2/末
  - 節気は目安の固定日。行事・学校の休みも固定日。
"""
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
META = ROOT / "town" / "meta.json"
CHRONICLE = ROOT / "chronicle"

EPOCH = dt.date(2026, 4, 6)  # 第1日
WEEKDAYS = "月火水木金土日"
MONTH_NAMES = {1: "睦月", 2: "如月", 3: "弥生", 4: "卯月", 5: "皐月", 6: "水無月",
               7: "文月", 8: "葉月", 9: "長月", 10: "神無月", 11: "霜月", 12: "師走"}

# (開始月, 開始日) → 季節名。年をまたぐ冬は 12/1 開始で 2 月末まで。
SEASONS = [((3, 1), "春"), ((6, 5), "梅雨"), ((7, 20), "夏"), ((9, 1), "秋"), ((12, 1), "冬")]

MARKS = {
    (1, 1): "元日", (1, 2): "正月二日", (1, 3): "三が日の最終日", (1, 7): "七草",
    (2, 3): "節分", (2, 4): "立春", (3, 3): "桃の節句", (3, 20): "春分（目安）",
    (4, 1): "新年度", (5, 5): "立夏・こどもの日", (6, 21): "夏至（目安）", (7, 7): "七夕",
    (8, 7): "立秋（目安）", (8, 13): "お盆の入り", (8, 16): "お盆の明け",
    (9, 23): "秋分（目安）", (11, 7): "立冬（目安）", (12, 22): "冬至（目安）", (12, 31): "大晦日",
}
# 学校の長期休み（開始月日, 終了月日）
SCHOOL_BREAKS = [((7, 21), (8, 31), "夏休み"), ((12, 24), (1, 7), "冬休み"), ((3, 25), (4, 7), "春休み")]


def date_of(day: int) -> dt.date:
    if day < 1:
        raise ValueError("day は 1 以上")
    return EPOCH + dt.timedelta(days=day - 1)


def _in_range(d: dt.date, start, end) -> bool:
    s, e = (d.year, *start), (d.year, *end)
    if start <= end:
        return s <= (d.year, d.month, d.day) <= e
    return (d.month, d.day) >= start or (d.month, d.day) <= end


def season_of(d: dt.date):
    """(季節名, 季節に入って何日目) を返す。"""
    md = (d.month, d.day)
    current = SEASONS[-1]  # 1〜2月は前年 12/1 開始の冬
    for start, name in SEASONS:
        if md >= start:
            current = (start, name)
    start, name = current
    year = d.year if md >= start else d.year - 1
    since = d - dt.date(year, *start)
    return name, since.days + 1


def info(day: int) -> dict:
    d = date_of(day)
    season, season_day = season_of(d)
    wd = WEEKDAYS[d.weekday()]
    marks = []
    if (d.month, d.day) in MARKS:
        marks.append(MARKS[(d.month, d.day)])
    for start, end, label in SCHOOL_BREAKS:
        if _in_range(d, start, end):
            marks.append(label)
    hints = []
    if wd in "土日" or any(m in ("夏休み", "冬休み", "春休み") for m in marks):
        hints.append("学校は休み（すみれは授業なし）")
    else:
        hints.append("授業日")
    if wd == "日":
        hints.append("診療所は休診")
    return {
        "day": day,
        "in_town_date": d.isoformat(),
        "weekday": wd,
        "season": season,
        "season_day": season_day,
        "month_name": MONTH_NAMES[d.month],
        "marks": marks,
        "hints": hints,
        "chronicle_file": f"chronicle/{day:04d}.md",
        "chronicle_header": header(day),
    }


def header(day: int) -> str:
    d = date_of(day)
    return f"# 第{day}日　{d.year}年{d.month}月{d.day}日（{WEEKDAYS[d.weekday()]}）・"


def load_meta() -> dict:
    return json.loads(META.read_text(encoding="utf-8"))


def save_meta(meta: dict) -> None:
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def apply(meta: dict, day: int) -> dict:
    i = info(day)
    for k in ("day", "in_town_date", "weekday", "season", "season_day", "month_name", "marks", "hints"):
        meta[k] = i[k]
    meta["weather"] = ""  # 灯が今日の天気を 80 字以内で書く
    meta["note"] = ""     # 灯が今日の要点を 300 字以内で書く
    return meta


def check() -> int:
    errors = []
    meta = load_meta()
    day = meta.get("day")
    if not isinstance(day, int):
        print("NG: meta.json の day が整数ではありません")
        return 1
    expect = info(day)
    for k in ("in_town_date", "weekday", "season", "season_day", "month_name", "marks"):
        if meta.get(k) != expect[k]:
            errors.append(f"meta.json {k}: {meta.get(k)!r} → 正しくは {expect[k]!r}")
    f = ROOT / expect["chronicle_file"]
    if not f.exists():
        errors.append(f"{expect['chronicle_file']} がありません（day={day}）")
    else:
        lines = f.read_text(encoding="utf-8").splitlines()
        if not lines or not lines[0].startswith(expect["chronicle_header"]):
            errors.append(f"{expect['chronicle_file']} 1行目は次で始めること: {expect['chronicle_header']}")
        want = f"> 通算 {day} 日目 / {expect['season']}"
        if not any(l.strip() == want for l in lines[:5]):
            errors.append(f"{expect['chronicle_file']} 冒頭5行に次の行がありません: {want}")
    if errors:
        print("NG: 暦の不整合")
        for e in errors:
            print("  - " + e)
        print("  → `python3 routine/calendar.py show` の値に合わせて直してください。day だけが正で、日付・曜日・季節は day から決まります。")
        return 1
    print(f"OK: 第{day}日 {expect['in_town_date']}（{expect['weekday']}）{expect['season']}")
    return 0


def main(argv) -> int:
    cmd = argv[1] if len(argv) > 1 else "show"
    if cmd == "show":
        day = int(argv[2]) if len(argv) > 2 else load_meta()["day"]
        print(json.dumps(info(day), ensure_ascii=False, indent=1))
        return 0
    if cmd == "next":
        meta = load_meta()
        day = meta["day"] + 1
        print(json.dumps(info(day), ensure_ascii=False, indent=1))
        if "--write" in argv:
            save_meta(apply(meta, day))
            print(f"meta.json を第{day}日へ進めました。weather と note を書いてください。", file=sys.stderr)
        return 0
    if cmd == "check":
        return check()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
