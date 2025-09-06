from __future__ import annotations
import time
import httpx
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Iterable, Optional
from tenacity import retry, wait_fixed, stop_after_attempt
from ..utils.text import parse_walk_min, parse_price_yen, parse_area_m2

@dataclass
class RawItem:
    url: str
    title: Optional[str]
    price_text: Optional[str]
    area_text: Optional[str]
    land_area_text: Optional[str]
    station_text: Optional[str]
    address_text: Optional[str]
    built_text: Optional[str]
    floor_plan: Optional[str]
    structure: Optional[str]
    raw: dict

class RakumachiClient:
    def __init__(self, username: Optional[str]=None, password: Optional[str]=None, timeout: float=20.0):
        self.username = username
        self.password = password
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36"
        }
        self.client = httpx.Client(headers=self.headers, timeout=self.timeout, follow_redirects=True)

    def login(self) -> bool:
        # NOTE: 実装はダミー。必要ならログインフローを実装。
        # ログインが必要な場合は対象サイトの規約に従ってください。
        return True

    @retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
    def fetch(self, url: str) -> str:
        r = self.client.get(url)
        r.raise_for_status()
        return r.text

    def parse_list_page(self, html: str) -> Iterable[RawItem]:
        soup = BeautifulSoup(html, "html.parser")
        # サイト構造に合わせて調整すること。以下は雛形。
        cards = soup.select("div.property-card, li.property-card, div.listItem, div.searchResultItem")
        for c in cards:
            a = c.select_one("a[href]")
            url = a["href"] if a else None
            if not url:
                continue
            title = (c.select_one(".title, .property-title, h2, h3") or {}).get_text(strip=True) if c.select_one(".title, .property-title, h2, h3") else None
            price_text = (c.select_one(".price, .property-price") or {}).get_text(strip=True) if c.select_one(".price, .property-price") else None
            area_text = (c.select_one(".area, .building-area") or {}).get_text(strip=True) if c.select_one(".area, .building-area") else None
            land_area_text = (c.select_one(".land-area") or {}).get_text(strip=True) if c.select_one(".land-area") else None
            station_text = (c.select_one(".station, .access") or {}).get_text(strip=True) if c.select_one(".station, .access") else None
            address_text = (c.select_one(".address") or {}).get_text(strip=True) if c.select_one(".address") else None
            built_text = (c.select_one(".built-year, .age") or {}).get_text(strip=True) if c.select_one(".built-year, .age") else None
            floor_plan = (c.select_one(".floor-plan") or {}).get_text(strip=True) if c.select_one(".floor-plan") else None
            structure = (c.select_one(".structure") or {}).get_text(strip=True) if c.select_one(".structure") else None

            yield RawItem(
                url=url,
                title=title,
                price_text=price_text,
                area_text=area_text,
                land_area_text=land_area_text,
                station_text=station_text,
                address_text=address_text,
                built_text=built_text,
                floor_plan=floor_plan,
                structure=structure,
                raw={}
            )

    def close(self):
        self.client.close()
