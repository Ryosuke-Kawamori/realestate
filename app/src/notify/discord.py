from __future__ import annotations
import json, httpx
from ..config import get_settings

def post_deal(item: dict, threshold: float):
    st = get_settings()
    url = st.DISCORD_WEBHOOK_URL
    if not url:
        return {"status":"no_webhook"}
    # item keys: title, url, price_yen, area_m2, station_name, station_walk_min, residual_pct
    embed = {
        "title": f"割安物件検出 ({item.get('residual_pct'):+.1%})",
        "url": item.get("url"),
        "fields": [
            {"name":"タイトル","value": item.get("title") or "-", "inline": False},
            {"name":"価格","value": f"{item.get('price_yen'):,} 円" if item.get("price_yen") else "-", "inline": True},
            {"name":"面積","value": f"{item.get('area_m2')} ㎡" if item.get("area_m2") else "-", "inline": True},
            {"name":"駅","value": f"{item.get('station_name') or '-'} 徒歩{item.get('station_walk_min') or '-'}分", "inline": True},
        ]
    }
    payload = {"content": None, "embeds": [embed]}
    with httpx.Client(timeout=10) as c:
        r = c.post(url, json=payload)
        r.raise_for_status()
    return {"status":"ok"}
