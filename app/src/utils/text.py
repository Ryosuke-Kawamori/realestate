import re
from typing import Optional

def parse_walk_min(s: str | None) -> Optional[int]:
    if not s:
        return None
    m = re.search(r"(徒歩|歩)\s*(\d+)\s*分", s)
    if m:
        try:
            return int(m.group(2))
        except:
            return None
    # fallback: any number + 分
    m2 = re.search(r"(\d+)\s*分", s)
    if m2:
        try:
            return int(m2.group(1))
        except:
            return None
    return None

def parse_price_yen(s: str | None) -> Optional[int]:
    if not s:
        return None
    # 例: 3,580万円 / 3.58億円 / 3580万円
    s = s.replace(",", "").replace(" ", "")
    oku = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*億", s)
    if oku:
        try:
            v = float(oku.group(1)) * 100_000_000
            return int(v)
        except:
            return None
    man = re.search(r"([0-9]+)\s*万", s)
    if man:
        try:
            v = int(man.group(1)) * 10_000
            return v
        except:
            return None
    # 純粋な数字円表記
    digits = re.findall(r"\d+", s)
    if digits:
        try:
            return int("".join(digits))
        except:
            return None
    return None

def parse_area_m2(s: str | None) -> Optional[float]:
    if not s:
        return None
    s = s.replace(",", "").replace(" ", "")
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*m\^?2|([0-9]+(?:\.[0-9]+)?)\s*㎡", s)
    if m:
        for g in m.groups():
            if g:
                try:
                    return float(g)
                except:
                    pass
    # just digits fallback
    try:
        return float(re.findall(r"[0-9]+(?:\.[0-9]+)?", s)[0])
    except:
        return None
