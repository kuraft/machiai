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

> 既存の状態の上に積み上げます。`town` が無い初回だけ、現在の内容から作成されます。

## 1. 町の「いま」を読み込む

次を読み、町の現状を完全に把握してください。

- `routine/RULES.md`（**進行ルール。必ず守る**）
- `town/meta.json`（日付・季節・天気・通算日数）
- `town/stats.json`（指標）
- `town/map.md`（地理）
- `town/relationships.md`（関係性）
- `town/residents/` 内の全住人ファイル
- `chronicle/` の **直近2〜3日** の日記（流れと伏線の把握）

## 2. 「今日」を設計する

`RULES.md` のペース配分に従い、**今日起こるささやかな出来事を1〜3個**決めます。

- 主役を1〜2人に絞る。全員を毎日動かさない。
- 直近の日記からの **続き・伏線の回収** を優先する。唐突な新展開より連続性。
- 季節・天気・曜日に合った出来事にする（`meta.json` を見る）。
- 人間関係は **一歩だけ** 進める。飛躍させない。
- 新住人の登場や新しい建物は、`RULES.md` の頻度制限の範囲でのみ。

## 3. 日記を書く（chronicle）

`chronicle/` の最新番号 +1 のファイルを新規作成します（4桁ゼロ埋め。例 `0002.md`）。
冒頭にメタ情報、本文は灯の一人称の日記体で。目安 **400〜900字**。

```markdown
# 第NNN日　YYYY年M月D日（曜）・天気

> 通算 NNN 日目 / 季節

（ここに灯の日記。今日の出来事を、五感と心の機微とともに綴る）
```

## 4. 町の状態を更新する

今日の出来事を、関係する**状態ファイルにだけ**反映します（触らないファイルは変えない）。

- `town/residents/*.md` … 近況・心境・新しい関係の芽を追記
- `town/relationships.md` … 関係が動いたら段階を更新
- `town/map.md` … 建物が増えた／変わったときだけ
- `town/stats.json` … `RULES.md` の変動幅の範囲で微調整
- **`town/meta.json` … 必ず更新**：`day` を +1、日付・曜日・天気・季節を進める

> 状態ファイルは「事実の台帳」、chronicle は「物語」。両者の食い違いを残さないこと。

## 5. 記録して push する

```bash
git add -A
git commit -m "第NNN日: <その日を一言で>"
git push -u origin town
```

> push が `claude/` 接頭辞ブランチしか許されず失敗する場合は、routine の権限設定で
> **Allow unrestricted branch pushes** を有効にする必要があります（README 参照）。
> ネットワークエラー時のみ、2s→4s→8s→16s で最大4回リトライしてください。

## 6. 最後に

ユーザーへの返信は短く。今日綴った出来事を **2〜3行** で報告すれば十分です。
長い要約や、やったことの逐一の列挙は不要です。灯らしく、静かに締めてください。
