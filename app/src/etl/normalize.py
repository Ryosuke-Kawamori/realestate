from __future__ import annotations
from typing import Optional, Tuple
from ..utils.text import parse_walk_min, parse_price_yen, parse_area_m2
import re
import math
from datetime import datetime

def split_address(addr: str | None):
    # 簡易実装（必要に応じて強化）
    if not addr:
        return None, None, None
    # 都道府県
    prefectures = ["北海道","青森県","岩手県","宮城県","秋田県","山形県","福島県","茨城県","栃木県","群馬県","埼玉県","千葉県","東京都","神奈川県","新潟県","富山県","石川県","福井県","山梨県","長野県","岐阜県","静岡県","愛知県","三重県","滋賀県","京都府","大阪府","兵庫県","奈良県","和歌山県","鳥取県","島根県","岡山県","広島県","山口県","徳島県","香川県","愛媛県","高知県","福岡県","佐賀県","長崎県","熊本県","大分県","宮崎県","鹿児島県","沖縄県"]
    pref = next((p for p in prefectures if addr.startswith(p)), None)
    city = None
    ward = None
    if pref:
        rest = addr[len(pref):]
        m = re.match(r"(.+?市)?(.+?区)?", rest)
        if m:
            city = m.group(1)[:-1] if m.group(1) else None
            ward = m.group(2)[:-1] if m.group(2) else None
    return pref, city, ward

def estimate_age_years(built_text: str | None) -> Optional[float]:
    if not built_text:
        return None
    # 例: 築10年 / 2015年築 / 新築
    if "新築" in built_text:
        return 0.0
    m = re.search(r"(築|建築)\s*(\d+)\s*年", built_text)
    if m:
        try:
            return float(m.group(2))
        except:
            return None
    y = re.search(r"(19|20)\d{2}", built_text)
    if y:
        try:
            year = int(y.group(0))
            return float(datetime.now().year - year)
        except:
            return None
    return None

def normalize_item(raw) -> dict:
    price = parse_price_yen(raw.price_text)
    area = parse_area_m2(raw.area_text)
    land_area = parse_area_m2(raw.land_area_text)
    walk_min = parse_walk_min(raw.station_text or "")
    age = estimate_age_years(raw.built_text)
    pref, city, ward = split_address(raw.address_text)

    # 駅名の推定（簡易）
    station_name = None
    if raw.station_text:
        m = re.search(r"(.+?)駅", raw.station_text)
        if m:
            station_name = m.group(1)

    return {
        "url": raw.url,
        "title": raw.title,
        "address": raw.address_text,
        "prefecture": pref,
        "city": city,
        "ward": ward,
        "station_name": station_name,
        "station_walk_min": walk_min,
        "price_yen": price,
        "area_m2": area,
        "land_area_m2": land_area,
        "floor_plan": raw.floor_plan,
        "built_year": None,  # 詳細にパースする場合はここを強化
        "age_years": age,
        "structure": raw.structure,
        "raw": {
            "price_text": raw.price_text,
            "area_text": raw.area_text,
            "land_area_text": raw.land_area_text,
            "station_text": raw.station_text,
            "built_text": raw.built_text,
        }
    }
