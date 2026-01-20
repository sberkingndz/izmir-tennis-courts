import math
import pandas as pd
import os
print("CWD:", os.getcwd())
print("data klasoru var mi?:", os.path.exists("data"))
print("data icindeki dosyalar:", os.listdir("data") if os.path.exists("data") else "YOK")


DATA_PATH = "data/bornova_bostanli_tenis_kortlari.csv"

# Geocode ile bulduğun merkez koordinatları (çıktından aldım)
PLACES = {
    "bornova": (38.46619, 27.21919),
    "bostanli": (38.45703, 27.09836),
}

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def normalize(s: str) -> str:
    s = s.strip().lower()
    return (s.replace("ı","i").replace("ş","s").replace("ğ","g")
             .replace("ü","u").replace("ö","o").replace("ç","c"))

def main():
    df = pd.read_csv(DATA_PATH)

    print("Nereden arayalim? (Bornova / Bostanli)")
    place_in = input("> ")
    key = normalize(place_in)

    if key not in PLACES:
        print("Sadece 'Bornova' veya 'Bostanli' yaz kanka 🙂")
        return

    user_lat, user_lon = PLACES[key]
    print(f"Konum: {user_lat:.5f}, {user_lon:.5f}")

    df["distance_km"] = df.apply(
        lambda r: haversine_km(user_lat, user_lon, r["lat"], r["lon"]),
        axis=1
    )

    out = df.sort_values("distance_km").head(10)

    print("\nEn yakin 10 tenis noktasi:")
    for i, r in enumerate(out.itertuples(index=False), start=1):
        name = r.name if isinstance(r.name, str) and r.name.strip() else "(Isim yok)"
        print(f"{i}. {name} | {r.distance_km:.2f} km")

if __name__ == "__main__":
    main()
