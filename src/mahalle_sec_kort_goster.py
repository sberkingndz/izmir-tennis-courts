import json
from pathlib import Path

# Proje kökünü bul (src'nin bir üstü)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "kortlar.json"


def load_courts():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    courts = load_courts()

    # Mahalle listesini çıkar (tekrarsız + sıralı)
    mahalleler = sorted({c["mahalle"] for c in courts})

    print("\nMahalle sec (numara yaz):")
    for i, m in enumerate(mahalleler, start=1):
        print(f"{i}) {m}")

    secim = input("\nSecim > ").strip()

    if not secim.isdigit():
        print("Numara girmen lazim kanka (1,2,3 gibi).")
        return

    idx = int(secim)
    if idx < 1 or idx > len(mahalleler):
        print("Gecersiz secim.")
        return

    secilen_mahalle = mahalleler[idx - 1]

    # O mahalledeki kortlari filtrele
    sonuc = [c for c in courts if c["mahalle"] == secilen_mahalle]

    print(f"\n✅ {secilen_mahalle} icin bulunan kortlar:")
    for c in sonuc:
        print(f"- {c['kort_adi']} ({c['ilce']}) | {c['lat']}, {c['lon']}")

    # Bonus: Google Maps linki (kullanici direk acsin)
    print("\nGoogle Maps linkleri:")
    for c in sonuc:
        lat, lon = c["lat"], c["lon"]
        print(f"- {c['kort_adi']}: https://www.google.com/maps?q={lat},{lon}")


if __name__ == "__main__":
    main()
