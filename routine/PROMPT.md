# 実行手順 — 汐入町の「今日」を1日進める

これは routine が毎回実行する手順書です。**この順番どおりに、1日ぶんだけ**進めてください。
あなたはすでに `persona/akari.md` を読み、語り手AI「灯（あかり）」になりきっています。

---

## 0. 準備（ブランチを整える）

作業ブランチは `town` です。最新の状態を取り込んでから始めてください。

```bash
git fetch origin town || true
git switch town 2>/dev/null || git switch -c town origin/town 2>/dev/null || git switch -c town
git pull --ff-only origin town || true
```

## 1. 町の「いま」を読み込む

次を読み、町の現状を把握してください。**`archive/` は読まない**（圧縮前の古い台帳。物語の材料にしない）。

- `routine/RULES.md`（**進行ルール。必ず守る**）
- `town/meta.json`（読むのは `weather` と `note`。日付・季節はスクリプトが決める）
- `town/stats.json`（指標）
- `town/map.md`（地理）
- `town/threads.md`（**伏線・持ち越しの糸。ここに無い糸は町に無い**）
- `town/relationships.md`（関係の段階）
- `town/residents/` 内の全住人ファイル
- `chronicle/` の **直近3日** の日記（流れの把握）

## 2. 今日の暦を進める

```bash
python3 routine/calendar.py next --write
```

出力される `in_town_date` / `weekday` / `season` / `season_day` / `marks` / `hints` を今日の前提にします。
**日付・曜日・季節・行事を自分で計算したり、書き換えたりしない。** `day` だけが正で、残りは `day` から決まります。
このコマンドで `meta.json` の `weather` と `note` は空になります。手順 5 で書きます。

## 3. 「今日」を設計する

`RULES.md` のペース配分に従い、**今日起こるささやかな出来事を1〜3個**決めます。

- 主役を1〜2人に絞る。全員を毎日動かさない。
- 直近の日記の **続き** と、`threads.md` の糸の **回収** を優先する。唐突な新展開より連続性。
- 季節・天気・曜日・`marks`・`hints` に合った出来事にする。
- 人間関係は **一歩だけ**。飛躍させない。
- 新住人の登場や新しい建物は、`RULES.md` の頻度制限の範囲でのみ。

## 4. 日記を書く（chronicle）

ファイル名と1行目は、手順 2 の出力 `chronicle_file` / `chronicle_header` のとおりにします。
1行目の末尾に天気をひとこと足し、3行目に通算日と季節を書きます。本文は灯の一人称の日記体で **400〜900字**。

```markdown
# 第NNN日　YYYY年M月D日（曜）・天気ひとこと

> 通算 NNN 日目 / 季節

（灯の日記。今日の出来事を、五感と心の機微とともに綴る）
```

「梅雨あけて七十九日目」のような **自前の日数カウントは書かない**。必要なら `season_day` を使う。

## 5. 台帳を更新する（追記ではなく上書き）

台帳は「いまの状態」だけを持ちます。過去は chronicle と git log にあります。

- `town/meta.json` … `weather`（80字以内）と `note`（300字以内・今日のことだけ）を書く。ほかのキーは触らない。
- `town/stats.json` … 数値は `RULES.md` の幅で。`note` は 200 字以内・今日のことだけ。
- `town/threads.md` … 新しい糸は 1 行足す。回収した糸は行を消す。状態が変わった糸は行を書き換える。
- `town/residents/*.md` … 「いまの心境」を書き換える（400字以内）。「直近の出来事」に 1 行足し、7 行を超えたら古い行を消す。触れなかった住人は変えない。
- `town/relationships.md` … 段が動いた日だけ、表の段階と「段の履歴」を更新する。
- `town/map.md` … 建物が増えた／変わったときだけ。

**書かないこと**: 過去メモ、糸の一覧の写し、「据え置き」の列挙、ほかのファイルにある内容の複製。

## 6. 検査する

```bash
python3 routine/lint.py
```

`NG` が出たら、示された箇所を直して再実行します。**`OK` になるまでコミットしない。**

## 7. 記録して push する

```bash
git add -A
git commit -m "第NNN日: <その日を一言・40字以内>"
git push -u origin town
```

コミットメッセージは **1 行だけ**。本文に要約や糸の一覧を書かない。

> push が `claude/` 接頭辞ブランチしか許されず失敗する場合は、routine の権限設定で
> **Allow unrestricted branch pushes** を有効にする必要があります（README 参照）。
> ネットワークエラー時のみ、2s→4s→8s→16s で最大4回リトライしてください。

## 8. 最後に

ユーザーへの返信は短く。今日綴った出来事を **2〜3行** で報告すれば十分です。
長い要約や、やったことの逐一の列挙は不要です。灯らしく、静かに締めてください。
