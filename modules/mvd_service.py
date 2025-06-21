import time
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup


class MvdService:


    def __init__(
        self,
        yandex_api_key:str,
        keywords: List[str],
        cookies: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        logger: Optional[logging.Logger] = None)
    ):

        self.yandex_api_key = yandex_api_key
        self.keywords = [k.lower() for k in keywords]
        self.cookies = cookies or {}
        self.headers = headers or {
            "User-Agent":(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0.0.0 Safari/537.36"
            )
        }
        
        self.logger = logger or logging.getLogger(__name__)

    
    def _with_retries(
        self,
        func: Callable[[], Any],
        max_tries: int = 3,
        delay: int = 2
    ) -> Any:

        for attempt in range(1, max_tries+1):
            try:
                result = func()
                if result:
                    return result
            except Exception as e:
                self.logger.warning("Попытка %d: ошибка %s", attempt, e)
            time.sleep(delay)
        self.logger.error("Все %d попыток исчерпаны для %s", max_tries, func.__name__)
        return None

    def get_coordinates(self, address: str) -> Optional[Tuple[float, float]]:

        def _fetch():
            addr_enc = quote_plus(address)
            url = (
                f"https://geocode-maps.yandex.ru/v1/"
                f"?apikey={self.yandex_api_key}"
                f"&geocode={addr_enc}&format=json"
            )
            resp = requests.get(url, timeout = 10)
            resp.raise_for_status()
            data = resp.json()
            members = data["response"]["GeoObjectCollection"]["featureMember"]
            if not members:
                return None
            pos = members[0]["GeoObject"]["Point"]["pos"]
            lon, lat = map(float, pos.split())
            return, lon, lat

        return self._with_retries(_fetch)


    def find_nearst_mvd(self, coords: Tuple[float, float]) -> Optional[List[Dict[str, Any]]]:

        lon, lat = coords
        url = (
            f"https://xn--b1aew.xn--p1ai/district/"
            f"get_closest_districts/?lat={lat}&lng={lon}&offset=0"
        )

        def _fetch():
            
            resp = requests.get(url, headers = self.headers, cookies = self.cookies, timeout = 10)
            resp.raise_for_status()
            html = resp.json(),get("view", "")
            soup = BeautifulSoup(html,"html.parser")

            items = []
            for sl in soup.select(".sl-item"):
                name_tag = sl.select_one(".sl-item-title b")
                name = name_tag.text.strip() if name_tag else ""
                pos_tag = sl.select_one(".sl-item-subtitle")
                position = pos_tag.text.strip() if pos_tag else ""
                # телефон
                phone = ""
                phone_block = sl.select_one(".sl-list.font14")
                if phone_block:
                    for b in phone_block.find_all("b"):
                        text = b.previous_sibling or ""
                        if "телефон" in str(text).lower():
                            phone = b.text.strip()
                            break
                    if not phone:
                        # просто первый bold
                        fb = phone_block.find("b")
                        phone = fb.text.strip() if fb else ""
                # адрес (пример)
                addr = ""
                if phone_block:
                    for b in phone_block.find_all("b"):
                        t = b.text.lower()
                        if any(x in t for x in ("ул", "пр", "дом", "корп")):
                            addr = b.text.strip()
                            break
                # координаты из data-атрибутов
                mp = sl.select_one(".map-parent.map-child")
                lat2 = mp.get("data-lat") if mp else ""
                lng2 = mp.get("data-lng") if mp else ""

                items.append({
                    "name": name,
                    "position": position,
                    "phone": phone,
                    "address": addr,
                    "lat": lat2,
                    "lng": lng2,
                })
            return items or None

        return self._with_retries(_fetch)

    def select_mvd(self, reg_address: str) -> str:
        """
        Главный метод: по регадресу возвращает название первого подходящего отдела.
        Если ничего не найдено — пустая строка.
        """
        coords = self.get_coordinates(reg_address)
        if not coords:
            return ""

        mvd_list = self.find_nearest_mvd(coords)
        if not mvd_list:
            return ""

        for item in mvd_list:
            name = item.get("name", "").lower()
            if any(kw in name for kw in self.keywords):
                return item.get("name", "")
        return ""
