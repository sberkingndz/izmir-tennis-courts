import time
import requests
import pandas as pd

# Overpass sunucuları (fallback)
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
]


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

# Her bölge için arama yarıçapı (metre)
RADIUS_M = 4000  # 6 km iyi başlangıç; az gelirse 8000 yap

QUERY_TEMPLATE = r"""
[out:json][timeout:60];
(
  nwr["leisure"="pitch"]["sport"="tennis"](around:{radius},{lat},{lon});
  nwr["sport"="tennis"](around:{radius},{lat},{lon});
);
out center tags;
"""


def geocode(place: str):
    params = {"q": place, "format": "json", "limit": 1}
    headers = {"User-Agent": "izmir-tenis-kortlari/1.0 (demo)"}
    r = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    if not data:
        return None
    return float(data[0]["lat"]), float(data[0]["lon"])


import time
import requests

def post_overpass(query: str):
    last_err = None

    for url in OVERPASS_URLS:
        for attempt in range(1, 4):
            try:
                resp = requests.post(url, data={"data": query}, timeout=120)

                # Yoğunluk / geçici hata
                if resp.status_code in (429, 502, 503, 504):
                    print(f"{url} -> HTTP {resp.status_code} (yogun). Bekliyorum...")
                    time.sleep(2 * attempt)
                    continue

                # Başka HTTP hatası
                if resp.status_code != 200:
                    print(f"{url} -> HTTP {resp.status_code}. Body (ilk 200): {resp.text[:200]!r}")
                    time.sleep(2 * attempt)
                    continue

                # 200 geldi ama JSON mu?
                ct = (resp.headers.get("Content-Type") or "").lower()
                if "json" not in ct:
                    print(f"{url} -> JSON degil! Content-Type: {ct}. Body (ilk 200): {resp.text[:200]!r}")
                    time.sleep(2 * attempt)
                    continue

                # JSON parse
                return resp.json()

            except Exception as e:
                last_err = e
                print(f"{url} -> Hata: {type(e).__name__}: {e}")
                time.sleep(2 * attempt)

        print("Bu sunucu olmadi, digerine geciyorum...\n")

    raise last_err



def element_to_row(el: dict) -> dict:
    tags = el.get("tags", {}) or {}

    lat = el.get("lat")
    lon = el.get("lon")
    center = el.get("center")
    if (lat is None or lon is None) and center:
        lat = center.get("lat")
        lon = center.get("lon")

    return {
        "osm_type": el.get("type"),
        "osm_id": el.get("id"),
        "name": tags.get("name"),
        "operator": tags.get("operator"),
        "access": tags.get("access"),
        "surface": tags.get("surface"),
        "lit": tags.get("lit"),
        "indoor": tags.get("indoor"),
        "website": tags.get("website"),
        "phone": tags.get("phone"),
        "lat": lat,
        "lon": lon,
        "raw_tags": tags,
    }


def main():
    places = [
        ("Bornova", "Bornova, Izmir, Turkey"),
        ("Bostanli", "Bostanlı, Karşıyaka, Izmir, Turkey"),
    ]

    all_elements = []

    for label, query_place in places:
        print(f"\nGeocode: {label} -> {query_place}")
        loc = geocode(query_place)
        if loc is None:
            print(f"Konum bulunamadi: {query_place}")
            continue

        lat, lon = loc
        print(f"{label} koordinat: {lat:.5f}, {lon:.5f}")

        overpass_query = QUERY_TEMPLATE.format(radius=RADIUS_M, lat=lat, lon=lon)
        print(f"{label} icin tenis kortlari cekiliyor (radius={RADIUS_M}m)...")
        data = post_overpass(overpass_query)
        elements = data.get("elements", [])
        print(f"{label} ham eleman: {len(elements)}")
        all_elements.extend(elements)

        # Nominatim/Overpass'a saygi: araya minik bekleme
        time.sleep(1)

    print(f"\nToplam ham eleman: {len(all_elements)}")

    rows = [element_to_row(el) for el in all_elements]
    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.dropna(subset=["lat", "lon"]).copy()
        df = df.drop_duplicates(subset=["osm_type", "osm_id"])

    csv_path = "data/bornova_bostanli_tenis_kortlari.csv"
    json_path = "data/bornova_bostanli_tenis_kortlari.json"

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    df.to_json(json_path, orient="records", force_ascii=False, indent=2)

    print(f"\nKaydedildi: {csv_path}")
    print(f"Kaydedildi: {json_path}")
    print(f"Toplam (temiz): {len(df)}")


if __name__ == "__main__":
    main()
