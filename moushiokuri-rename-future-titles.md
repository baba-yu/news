# Future タイトル一括 rename — 別セッション引継ぎ

新ルール（[design/scheduled/1_daily_update-writer-rules.md §compose-prediction Field-level rules](design/scheduled/1_daily_update-writer-rules.md)）に従って、過去 corpus（2026-04-19 〜 2026-05-04 = 16 日 × 3 予測 = 48 件）の Future タイトルをリライトする。

## 背景（なぜやるか）

旧タイトルはトリガーイベント／観測者／日付始まりが多い：

- BAD: `Mag 7 Q1 earnings (Apr 29-30) reset the AI-capex ROI narrative — Q3 2026 sees first hyperscaler ...`
- BAD: `OpenAI Apr 28 WSJ initiates 2026 "AI-revenue disclosure rewrite" — by Q3 2026 ...`
- BAD: `WSJ OpenAI-revenue-miss + Mag 7 print collision triggers SEC + analyst push ...`

新ルール下では「予測の主体 + 動詞」始まりが必須：

- GOOD: `Big-3 hyperscalers ship MCP-server policy enforcement as default by Q4 2026`
- GOOD: `SEC publishes AI-revenue disclosure concept release by Q4 2026`
- GOOD: `Local-LLM training stack hits 70% VRAM reduction baseline by H2 2026`

`compose-prediction-backfill` は title を copy 継承するので、過去分は手動 rename が必要。

## スコープ（対象範囲）

- **期間**: 2026-04-19 〜 2026-05-04（16 日分）
- **件数**: 48 件（毎日 3 予測 × 16 日）
- **言語**: EN canonical → JA / ES / FIL fanout
- **ID 不変**: `prediction_id` は SHA-1(`prediction_date` + `prediction_summary`) なので、**title だけ変えれば ID は保たれる**（[app/src/ingest.py:298](app/src/ingest.py#L298)）。`prediction_summary` は触らない。

## 変更対象ファイル（surface area）

renaming は **sourcedata JSON が単一の真実の源** で、そこから rerender で全部伝播する。

### 直接書き換える

| ファイル | フィールド | 補足 |
|---|---|---|
| `app/sourcedata/<date>/predictions.json` | `predictions[].title` | 16 日 × 3 = 48 エントリ |
| `app/sourcedata/locales/<date>/<L>/predictions.json` | `predictions[].title` | 16 × 3 × 3 = 144 エントリ（JA/ES/FIL） |

### rerender で自動伝播

| ファイル | 処理 |
|---|---|
| `report/<L>/news-YYYYMMDD.md` `## Future` 番号付きリスト | `python -m app.skills.render_news_md --date <date> --locale <L> --write` |
| DB `predictions.title` | `python -m app.src.cli ingest-sourcedata --date <date>` — `_upsert_prediction` の COALESCE は非 NULL を上書きするので OK ([app/src/ingest.py:354](app/src/ingest.py#L354)) |
| `docs/data/graph-{tech,business,mix}.json` の prediction node `label` / `short_label` / `title` | `python -m app.src.cli export` |

### **触らない（理由付き）**

- `prediction_summary` — ID の hash 入力。変えると ID が破壊されて bridges / needs / evidence_links が全部リンク切れ
- `prediction_short_label` — `prediction_summary` から派生する別フィールド（[app/skills/backfill_short_labels.py](app/skills/backfill_short_labels.py)）。validation table と bridge narrative はこれを使う。タイトル規則とは別軸の関心
- `future-prediction/<L>/future-prediction-YYYYMMDD.md` — `short_label` 経由なので title rename の影響なし
- `app/sourcedata/<date>/bridges.json` — `prediction_ref.short_label` 経由なので影響なし
- スナップショット（`docs/data/snapshots/`, `memory/snapshots/`） — point-in-time 履歴。書き換えない

## 実行手順（4 ステップ）

### Step 1. EN タイトルのリライト（LLM sub-agent）

新規スキル提案: `design/skills/rename-future-titles.md`（仕様だけ書いて実装はこのタスクで）

Sub-agent 1 件あたり：

- **Input**: `prediction_id`, 旧 `title`, 旧 `body`, `reasoning.so_that`（実際の予測中核）, `reasoning.landing`（時間軸）
- **Rules**: [design/scheduled/1_daily_update-writer-rules.md §compose-prediction Field-level rules](design/scheduled/1_daily_update-writer-rules.md) の title 節を全文同梱
- **Output**: 新 `title`（≤80 chars、新規則準拠）一行のみ
- **Reply contract**: `OK <pid> <new_title>` または `KEEP <pid>`（既に新規則準拠で書き換え不要のとき）または `FAIL <pid> <reason>`

並列度：日付ごとに 3 sub-agent を fan out（compose-prediction と同じ shape）。16 日逐次 × 3 並列で 48 件 ≈ 16 ラウンド。

実装場所案：
- `app/skills/rename_future_titles.py` — orchestrator（dry-run / apply / 単一日付指定 / 全期間モード）
- `design/skills/rename-future-titles.md` — sub-agent 契約

#### Dry-run モード必須

48 件全部の `OLD → NEW` 比較表を吐く。ユーザー目視レビュー後に `--apply` で書き戻し。LLM の暴走防止。

### Step 2. ロケール再翻訳

EN 確定後、JA / ES / FIL を `locale-fanout` で再生成：

```bash
for date_iso in 2026-04-19 ... 2026-05-04; do
  python -m app.skills.locale_fanout --date $date_iso --kind predictions
done
```

または `compose-prediction-backfill` 系の翻訳 sub-agent パターン（[design/skills/locale-fanout.md](design/skills/locale-fanout.md) 参照）。

ロケール JSON の他フィールド（body / reasoning / summary）の既存翻訳は保持。**title だけ差し替え**。

### Step 3. rerender + DB 再 ingest + graph 再 export

```bash
for date_iso in 2026-04-19 ... 2026-05-04; do
  for loc in en ja es fil; do
    python -m app.skills.render_news_md --date $date_iso --locale $loc --write
  done
  python -m app.src.cli ingest-sourcedata --date $date_iso
done

python -m app.src.cli export   # graph-{tech,business,mix}.json 一括再生成
```

`ingest-sourcedata` の `_upsert_prediction` は title を `COALESCE(?, title)` で更新するので、新 title が DB に伝播する。

### Step 4. テスト

#### 自動

- `python -m app.skills.daily_flow_check --date 2026-05-04 --strict` — 全バケット再検証（4 ロケール × 16 日分のファイル整合）
- `python -m app.skills.lint_markdown_clean report/` — 禁止トークン検出
- `python -m app.skills.post_write_integrity --kind news` — markdown 整合性
- 新規ユニットテスト案（必須）：
  - `app/tests/test_rename_future_titles.py`
    - sub-agent output schema バリデーション
    - dry-run idempotent
    - apply 後の `prediction_id` 不変性（48 件全部について SHA-1 hash 再計算で照合）
    - rerender 後の `## Future` リスト先頭が新 title になっている

#### 目視

- ダッシュボードを起動（`docs/index.html` を local serve）して、過去 16 日のスナップショットがロード可能（タイトルが新規則になっている）
- BIZ / TECH / MIX 各ビューで予測カードのタイトル先頭が「主語+動詞」であることを確認
- 7d / 30d / 90d ウィンドウ切替で表示崩れなし

## 既知のリスク・確認事項

1. **`prediction_summary` を巻き添えで触らない** — ID の hash 入力。スキル prompt で明示的に「summary は変えない」を入れる
2. **再 ingest 時の `prediction_short_label` 巻き戻り** — `backfill_short_labels.py` が summary から再導出する場合、これは title 変更の影響を受けない（別系統）。念のため再 ingest 後に `short_label` の整合性を確認
3. **scope 配属は本タスクでは変わらない** — matcher は `summary` を見るので title rename だけでは `scope_id` / theme assignment は不変。matcher の primary 判定そのものは概ね妥当（実機検証で 34 件中 7 件が hint と乖離、うち真に誤判定は 2 件のみ — 下記「並列タスク」参照）。本タスクの主目的は「タイトル品質」であって「scope 配属の修正」ではない。過去分の `scope_hint`（LLM 自己申告メタデータ）は再生成しない
4. **Sunday スナップショットの旧タイトル** — `docs/data/snapshots/<date>/graph-*.json` には旧タイトルが凍結。**意図的に放置**（履歴の一貫性のため）。current `docs/data/graph-*.json` だけ更新
5. **READMEs（4 ロケール）** — 直近 3 日の予測リストを抜粋している場合あり。`run_update_pages` を流すと自動再生成されるなら問題なし。要確認

## 進捗トラッキング

このタスクを開始したら、以下のいずれかで状態保存：
- `git commit` メッセージに `rename-future-titles: <date>` を含める（日付ごとにアトミックコミット）
- このファイル末尾に「## 進捗ログ」を追記して `git commit`

完了条件：
- [ ] 48 件の dry-run レビュー完了
- [ ] 48 件 EN 適用済 + commit
- [ ] 144 件ロケール適用済 + commit
- [ ] DB 再 ingest 完了 + commit
- [ ] graph 再 export 完了 + commit
- [ ] daily_flow_check / lint / post-write-integrity 全 green
- [ ] ダッシュボード目視確認 OK
- [ ] このファイル削除 or `done/` に移動

## 並列タスク：scope 表示の非対称緩和（別 moushiokuri 推奨）

**前提の訂正（実機検証 2026-05-05 後）**:

当初は「matcher が tech 主体の予測を biz に多数決で流している」疑いがあったが、コード読み + dry-run（`experiment_title_match.py`）で**多数決ロジックは存在しないこと**を確認。`prediction.9d68206f94f7d87d` "Local-LLM training stack hits 70% VRAM reduction" の例で言うと：

- matcher の primary 判定は **scope=tech**（IDF score 3.0 vs biz 2.67）。正しい
- BIZ ビューで「5 親」に見えるのは [`extra_theme_parents`](app/src/export.py#L686)（同 scope 内の二次テーマ展開、threshold=0.55）が biz scope で 4 個ヒットしただけ
- TECH ビューでは tech scope 内で同関数が走り、他の tech テーマがどれも threshold を越えなかったので 1 親のまま
- multi-scope 配属は仕様（[reference/future-prediction.md §How predictions get clustered](reference/future-prediction.md)）。両 scope に等価で配属される

つまり「primary が biz になっている」のは表示上の錯覚で、scope 判定ロジックの真値は tech。**本タスクでの修正対象は scope 判定ロジックではなく、表示の非対称感**。

**コーパス全体の matcher 健全性**（`experiment_title_match.py --tech-dropouts` 実行結果）:

- hint=tech|cross な予測: 34 件
- うち matcher primary が biz になった: 7 件
- うち真に matcher 誤判定（題材から見て tech が正しい）: **2 件のみ**
  - `prediction.36f4ab773b39713e` "Training-vs-inference SKU split" — biz 3.53 vs tech 3.42（margin +0.12）
  - `prediction.f960d058dc42c7c6` "KV-cache-compression dtype" — biz 3.83 vs tech 2.78（margin +1.05、`open_weight_vs_proprietary` が "open-source inference engines" に過剰反応）

残り 5 件は題材的に biz 寄り（hint が cross / 過剰申告）で matcher の biz 判定が妥当。

**実機検証で却下された案**:

- 純粋 title-match: 52 件中 9 件で primary 反転、うち 8 件が tech→biz 方向（短い title だと希少 biz 語の支配が逆に強まる）。**回帰**

**まだ生きてる修正候補**:

a. **`SECONDARY_THEME_THRESHOLD = 0.55` の引き上げ**（[app/src/export.py:99](app/src/export.py#L99)） — biz scope 側の secondary 親が 4 個付く要因。0.65〜0.70 に上げると非対称が縮む。tech / biz 両 scope に同時適用なので tech 側の secondary も削れる方向に動く点は要注意（tech 側はもともと secondary 0 件なので副作用なし、と本ケースでは確認済）

b. **scope 別動的閾値**: tech と biz でテーマキーワード設計の粒度が違うので、threshold も scope 別に校正したい。実装は (a) より重い

c. **tech テーマキーワード再点検**: training / kernel / VRAM / quantization 系のキーワードが `local_inference_runtime` に集中していて他 tech テーマに分散していない疑い。過去 90 日の hint=tech 予測 × tech 各テーマの IDF score 表を出して、tech 側で secondary が育たない真因を確認。`local_training_runtime` / `kernel_efficiency` 等の新規 tech テーマ切り出し候補があれば提案

d. **matcher の真誤判定 2 件の個別対応**:
  - `prediction.36f4ab773b39713e`: margin +0.12 と僅差。閾値ゲートとは別に「margin < 0.5 のときは hint を尊重する」ようなタイブレーカを入れる手も。1 件のために導入する価値があるかは要評価
  - `prediction.f960d058dc42c7c6`: `business.open_weight_vs_proprietary` のキーワードに `vLLM`/`SGLang`/`Ollama` 等の OSS プロジェクト名が入っているなら過剰反応。テーマキーワード側の問題

**順序**:

1. 本タスク（タイトル rename）完了 → title が新規則準拠
2. 別 moushiokuri で (a) の閾値感度分析（0.55 / 0.60 / 0.65 / 0.70 で biz 側親数の分布変化を見る）
3. (a) を採用するかしないかを判断 → 採用なら DB 再 ingest + graph 再 export
4. 必要なら (c)（tech テーマキーワード拡充）を別タスクで

**本タスクとの依存**:

- 独立。タイトル rename は scope 配属に影響しないので、どちらを先にやってもよい
- ただしダッシュボード目視確認のときに「親数の非対称」が気になるなら、本タスク完了後に (a) の感度分析だけ先に走らせて閾値だけ上げる、という最小介入で改善できる
