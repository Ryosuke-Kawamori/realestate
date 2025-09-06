# rakumachi-deals
**楽待**（※サイト規約遵守）等から不動産価格を取得→DB保存→回帰モデルで推定価格を算出→残差（割安度）を判定→Discordに通知するまでを**Docker**で動かす一式。

> ⚠️ 注意: スクレイピングは対象サイトの**利用規約**・**robots.txt**・法令を遵守してください。ログインが必要/禁止されている場合や、商用/自動取得が禁止されている場合は**必ず許可**を得るか、代替の正規API/CSV等をご利用ください。本リポジトリは教育目的の雛形です。

---

## 構成
- **PostgreSQL**: 物件データ・スコアの保存
- **App (Python)**: スクレイピング/ETL/学習/通知/スケジューラ（APScheduler）
- **Adminer**: DBの簡易GUI

```
docker-compose.yml
app/
  Dockerfile
  requirements.txt
  src/
    config.py
    db.py
    models.py
    runner.py
    schedule.py
    utils/text.py
    scraper/rakumachi_scraper.py
    etl/normalize.py
    ml/features.py
    ml/train.py
    ml/predict.py
    notify/discord.py
sql/
  schema.sql
scripts/
  wait_for_port.py
.env.example
```

## クイックスタート
1. `.env.example` を `.env` にコピーして値を設定（Discord Webhookなど）
2. Docker起動：
   ```bash
   docker compose up -d --build
   ```
3. 初期化＆学習＆スキャン手動実行（任意）:
   ```bash
   docker compose exec app python -m src.runner init-db
   docker compose exec app python -m src.runner scrape-once
   docker compose exec app python -m src.runner train-model
   docker compose exec app python -m src.runner scan-new
   ```
4. 常駐スケジューラ（デフォルト: 30分毎スクレイプ、1日1回学習、随時スコアリング＆通知）は app コンテナ起動時に自動スタート。

## .env 設定例
```
# DB
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=rakumachi
POSTGRES_HOST=db
POSTGRES_PORT=5432

# 通知
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxxx/xxxx

# しきい値 (予測価格に対する割安度: -0.15 なら15%割安で通知)
RESIDUAL_PCT_THRESHOLD=-0.15
MIN_PRICE_JPY=5000000

# スケジュール（分）
SCRAPE_INTERVAL_MIN=30
RETRAIN_CRON=0 5 * * *    # 毎日5:00
SCAN_INTERVAL_MIN=10

# 楽待ログイン（必要な場合のみ）
RAKUMACHI_USER=
RAKUMACHI_PASS=

# スクレイピング対象URL（例: 楽待の検索結果ページ）
TARGET_LIST_URL=https://example.com/search?page=1
```

## 学習モデル
- 目的変数: `log(price_yen)`
- 説明変数: `log(area_m2)`, `age_years`, `age_years^2`, `station_walk_min`, `prefecture`, `city`, `ward`, `station_name` など
- 推定器: `Ridge` (scikit-learn) + OneHotエンコーディング（高次元カテゴリは必要に応じて縮約/ターゲットエンコーディングを導入可能）

## 使い方の流れ
1. **スクレイプ**: リストページを取得→カードごとにパース→DB upsert（新着検出）
2. **ETL**: 面積・築年数・駅徒歩などを正規化
3. **学習**: DB全体から回帰を学習→`/app/model/model.joblib` に保存
4. **スコア**: 新規/更新物件について予測→残差・残差率を計算
5. **通知**: 残差率がしきい値以下（割安）ならDiscordへ埋め込み通知

## 管理UI
- Adminer: http://localhost:8080  
  - サーバ: `db` ユーザ: `.env`の `POSTGRES_USER`、DB: `POSTGRES_DB`

## 免責
本ソフトウェアによって生じたいかなる損害についても作者は責任を負いません。自己責任でご利用ください。
