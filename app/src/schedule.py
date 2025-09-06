from __future__ import annotations
import time, threading, sys, traceback, os, json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from .config import get_settings
from .db import init_db
from .runner import cmd_scrape_once, cmd_train_model, cmd_scan_new

def safe(fn):
    def _wrap():
        try:
            fn()
        except Exception as e:
            traceback.print_exc()
    return _wrap

def main():
    st = get_settings()
    # 初期化
    init_db()
    scheduler = BackgroundScheduler(timezone="Asia/Tokyo")

    # スクレイプ
    scheduler.add_job(safe(cmd_scrape_once), IntervalTrigger(minutes=st.SCRAPE_INTERVAL_MIN), id="scrape")
    # 学習
    try:
        trig = CronTrigger.from_crontab(st.RETRAIN_CRON, timezone="Asia/Tokyo")
    except Exception:
        trig = CronTrigger.from_crontab("0 5 * * *", timezone="Asia/Tokyo")
    scheduler.add_job(safe(cmd_train_model), trig, id="train")
    # スキャン＆通知
    scheduler.add_job(safe(cmd_scan_new), IntervalTrigger(minutes=st.SCAN_INTERVAL_MIN), id="scan")

    scheduler.start()
    print("Scheduler started.")
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        scheduler.shutdown()

if __name__ == "__main__":
    main()
