import requests
import time

from typing import Tuple
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
# def get_coordinates(reg_address: str)-> Tuple:


keyword = ['отдел полиции', 'оп', 'отделение полиции', 'омвд']


def get_data_with_retries(get_data_func, max_tries: int = 3, delay: int =2):
    for attempt in range(max_tries):
        result = get_data_func()
        if result: 
            return result
        print(f"Попытка {attempt+1} не удалась, ждем {delay} сек и пробуем еще раз...")
        time.sleep(delay)
    return None


def get_coordinates(reg_address: str) -> Tuple:

    apikey = "7166c6cd-e13e-4dfc-b4d8-9aa72e1e01f5"
    address = reg_address # любой адрес целиком

    # Кодируем адрес
    address_encoded = quote_plus(address)

    url = f"https://geocode-maps.yandex.ru/v1/?apikey={apikey}&geocode={address_encoded}&format=json"

    response = requests.get(url)
    data = response.json()
    feature_member = data['response']['GeoObjectCollection']['featureMember']
    if feature_member:
        pos = feature_member[0]['GeoObject']['Point']['pos']
        lon, lat = map(float, pos.split())
        return (lon, lat)
    return None


def find_nearst_MVD(coordinates: Tuple[float, float]):
    lon, lat = coordinates
    url = f'https://xn--b1aew.xn--p1ai/district/get_closest_districts/?lat={lat}&lng={lon}&offset=0'
    try:

        cookies = {
            "close_apps_link": "yes",
            "csrf-token-name": "csrftokensec",
            "session": "rhql075pubdkhc40ek5a80tia3",

        }
        headers = {
            "User-Agent":  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers,cookies=cookies, timeout=10)
        response.raise_for_status()  # выбросит исключение если не 200
        data = response.json()

        html = data["view"]
        soup = BeautifulSoup(html, "html.parser")
        
        result = []
        for sl_item in soup.select(".sl-item"):
            name = sl_item.select_one(".sl-item-title b")
            name = name.text.strip() if name else ""
            position = sl_item.select_one(".sl-item-subtitle")
            position = position.text.strip() if position else ""
            # Телефон (берём первый bold после "Телефоны:")
            phone = ""
            phones_section = sl_item.select_one(".sl-list.font14")
            if phones_section:
                bolds = phones_section.find_all("b")
                for b in bolds:
                    if "Телефон" in b.previous_sibling or "телефон" in b.previous_sibling:
                        phone = b.text.strip()
                        break
                if not phone and bolds:
                    phone = bolds[0].text.strip()
            # Адрес — ищем bold с "ул" (или другой паттерн)
            address = ""
            if phones_section:
                for b in phones_section.find_all("b"):
                    if "ул" in b.text or "пр" in b.text or "дом" in b.text or "корп" in b.text:
                        address = b.text.strip()
                        break
            # Координаты (если есть)
            map_div = sl_item.select_one(".map-parent.map-child")
            lat = map_div.get("data-lat") if map_div else ""
            lng = map_div.get("data-lng") if map_div else ""

            result.append({
                "name": name,
                "position": position,
                "phone": phone,
                "address": address,
                "lat": lat,
                "lng": lng,
            })
        return result
    except Exception as e:
        print(f"Ошибка: {e}")


def get_mvd(reg_address) -> str:
    coordinates = get_data_with_retries(lambda: get_coordinates(reg_address))
    mvd_list = get_data_with_retries(lambda: find_nearst_MVD(coordinates))    
    final_mvd =''
    for i in mvd_list:
        if any(k.lower() in i['name'].lower() for k in keyword):
            final_mvd = i['name']
            break 
    return final_mvd 
