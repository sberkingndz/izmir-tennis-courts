import json
from pathlib import Path

import streamlit as st
import pandas as pd

import folium
from streamlit_folium import st_folium

# Proje kökü
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "kortlar.json"

st.set_page_config(page_title="Izmir Tenis Kortlari", layout="wide")

@st.cache_data
def load_courts():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

courts = load_courts()

st.title("Izmir Tenis Kortlari (MVP)")
st.caption("Mahalle sec → o mahalledeki kortlari gor → haritada ac")

# Mahalle listesi
mahalleler = sorted({c["mahalle"] for c in courts})
secilen_mahalle = st.selectbox("Mahalle sec:", mahalleler)

# Filtre
filtered = [c for c in courts if c["mahalle"] == secilen_mahalle]

st.subheader(f"{secilen_mahalle} icin kortlar")

# Tablo
df = pd.DataFrame(filtered)
df["maps_link"] = df.apply(lambda r: f"https://www.google.com/maps?q={r['lat']},{r['lon']}", axis=1)

# Linkleri düzgün göstermek için ayrı liste
st.dataframe(
    df[["kort_adi", "ilce", "bolge", "lat", "lon", "maps_link"]],
    use_container_width=True
)

st.markdown("**Google Maps linkleri:**")
for c in filtered:
    lat, lon = c["lat"], c["lon"]
    st.markdown(f"- [{c['kort_adi']}](https://www.google.com/maps?q={lat},{lon})")

# Harita
st.subheader("Harita")

# Haritayı mahalledeki ilk korta merkezle (yoksa İzmir merkez)
if filtered:
    center_lat = filtered[0]["lat"]
    center_lon = filtered[0]["lon"]
else:
    center_lat, center_lon = 38.4237, 27.1428  # Izmir

m = folium.Map(location=[center_lat, center_lon], zoom_start=13)

for c in filtered:
    folium.Marker(
        location=[c["lat"], c["lon"]],
        popup=f"{c['kort_adi']} ({c['ilce']})",
        tooltip=c["kort_adi"]
    ).add_to(m)

st_folium(m, width=1100, height=600)
