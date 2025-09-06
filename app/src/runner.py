from __future__ import annotations
import argparse, math
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from .db import init_db, SessionLocal
from .models import Listing
from .config import get_settings
from .scraper.rakumachi_scraper import RakumachiClient
from .etl.normalize import normalize_item
from .ml.train import train_and_save
from .ml.predict import score_new_listings
from .notify.discord import post_deal

def upsert_listing(session: Session, data: dict) -> int:
    # url をキーに upsert
    url = data.get("url")
    if not url:
        return 0
    existing = session.query(Listing).filter(Listing.url == url).first()
    now = datetime.now(timezone.utc)
    if existing:
        # update
        for k, v in data.items():
            setattr(existing, k, v)
        existing.last_seen_at = now
        session.add(existing)
        session.commit()
        return existing.id
    else:
        row = Listing(**data)
        session.add(row)
        session.commit()
        return row.id

def cmd_init_db():
    init_db()
    print("DB initialized.")

def cmd_scrape_once():
    st = get_settings()
    url = st.TARGET_LIST_URL
    if not url:
        print("TARGET_LIST_URL is not set. Skip.")
        return
    cli = RakumachiClient(st.RAKUMACHI_USER, st.RAKUMACHI_PASS)
    html = cli.fetch(url)
    items = list(cli.parse_list_page(html))
    inserted = 0
    with SessionLocal() as s:
        for it in items:
            data = normalize_item(it)
            if not data.get("price_yen"):
                continue
            if data.get("price_yen", 0) < st.MIN_PRICE_JPY:
                continue
            rid = upsert_listing(s, data)
            if rid:
                inserted += 1
    print(f"scrape_once: upserted {inserted} rows")

def cmd_train_model():
    res = train_and_save()
    print(res)

def cmd_scan_new():
    st = get_settings()
    scored = score_new_listings(st)
    if not scored:
        print("no scored")
        return
    # 通知: 閾値以下のもの
    with SessionLocal() as s:
        for sc in scored:
            if sc["residual_pct"] <= st.RESIDUAL_PCT_THRESHOLD:
                # listing 詳細
                li = s.query(Listing).filter(Listing.id == sc["listing_id"]).first()
                if not li:
                    continue
                post_deal({
                    "title": li.title,
                    "url": li.url,
                    "price_yen": li.price_yen,
                    "area_m2": li.area_m2,
                    "station_name": li.station_name,
                    "station_walk_min": li.station_walk_min,
                    "residual_pct": sc["residual_pct"],
                }, st.RESIDUAL_PCT_THRESHOLD)
    print("scan_new: done.")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["init-db","scrape-once","train-model","scan-new","all"], help="command")
    args = ap.parse_args()
    if args.cmd == "init-db":
        cmd_init_db()
    elif args.cmd == "scrape-once":
        cmd_scrape_once()
    elif args.cmd == "train-model":
        cmd_train_model()
    elif args.cmd == "scan-new":
        cmd_scan_new()
    elif args.cmd == "all":
        cmd_init_db()
        cmd_scrape_once()
        cmd_train_model()
        cmd_scan_new()

if __name__ == "__main__":
    main()
