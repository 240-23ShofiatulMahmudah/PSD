import streamlit as st
import rasterio
import numpy as np
import pandas as pd
import folium
from folium import TileLayer
from streamlit_folium import st_folium
from pathlib import Path
from rasterio.warp import transform_bounds
from rasterio.enums import Resampling
from matplotlib import cm
from matplotlib.colors import to_hex
import base64
from io import BytesIO
from PIL import Image

st.set_page_config(
    page_title="Klasifikasi Tutupan Lahan Jawa Timur",
    page_icon="🛰️",
    layout="wide"
)

st.title("🛰️ Klasifikasi Tutupan Lahan Jawa Timur")
st.caption("Sentinel-2 L2A • Random Forest")

FILE_TIF = Path(__file__).parent / "klasifikasi_jawa_timur_random_forest.tif"

KELAS = {
    1: "Bangunan",
    2: "Pertanian",
    3: "Perairan",
    4: "Hutan biasa",
    5: "Mangrove"
}

WARNA = {
    1: "#e53935",
    2: "#fdd835",
    3: "#1e88e5",
    4: "#1b5e20",
    5: "#8bc34a"
}

if not FILE_TIF.exists():
    st.error(f"Raster tidak ditemukan: {FILE_TIF.name}")
    st.stop()

@st.cache_data
def baca_raster(path):
    with rasterio.open(path) as src:
        # Perkecil raster untuk tampilan web agar lebih ringan.
        skala = min(1, 1200 / max(src.width, src.height))
        out_h = max(1, int(src.height * skala))
        out_w = max(1, int(src.width * skala))

        arr = src.read(
            1,
            out_shape=(out_h, out_w),
            resampling=Resampling.nearest
        )

        bounds = transform_bounds(
            src.crs, "EPSG:4326", *src.bounds, densify_pts=21
        )
        return arr, bounds

hasil, bounds = baca_raster(str(FILE_TIF))
valid = hasil > 0

# Titik tengah raster untuk posisi awal peta.
lon_tengah = (bounds[0] + bounds[2]) / 2
lat_tengah = (bounds[1] + bounds[3]) / 2

# Buat peta dasar dengan citra satelit.
m = folium.Map(
    location=[lat_tengah, lon_tengah],
    zoom_start=8,
    tiles=None,
    control_scale=True
)

TileLayer(
    tiles="OpenStreetMap",
    name="Peta jalan",
    overlay=False,
    control=True
).add_to(m)

TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri, Maxar, Earthstar Geographics",
    name="Citra satelit",
    overlay=False,
    control=True,
    show=True
).add_to(m)

# Konversi raster hasil klasifikasi menjadi gambar overlay transparan.
@st.cache_data
def buat_overlay(arr):
    rgba = np.zeros((arr.shape[0], arr.shape[1], 4), dtype=np.uint8)

    for kode, warna in WARNA.items():
        rgb = tuple(
            int(warna[i:i+2], 16) for i in (1, 3, 5)
        )
        mask = arr == kode
        rgba[mask, 0] = rgb[0]
        rgba[mask, 1] = rgb[1]
        rgba[mask, 2] = rgb[2]
        rgba[mask, 3] = 175

    image = Image.fromarray(rgba, mode="RGBA")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

overlay_data = buat_overlay(hasil)

# Setiap kelas menjadi layer terpisah yang dapat diaktifkan/dimatikan.
for kode, nama in KELAS.items():
    mask = (hasil == kode).astype(np.uint8) * 255

    rgba = np.zeros((hasil.shape[0], hasil.shape[1], 4), dtype=np.uint8)
    rgb = tuple(int(WARNA[kode][i:i+2], 16) for i in (1, 3, 5))
    rgba[:, :, 0] = rgb[0]
    rgba[:, :, 1] = rgb[1]
    rgba[:, :, 2] = rgb[2]
    rgba[:, :, 3] = np.where(mask > 0, 175, 0)

    image = Image.fromarray(rgba, mode="RGBA")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    data = base64.b64encode(buffer.getvalue()).decode("utf-8")

    folium.raster_layers.ImageOverlay(
        image=f"data:image/png;base64,{data}",
        bounds=[
            [bounds[1], bounds[0]],
            [bounds[3], bounds[2]]
        ],
        name=nama,
        opacity=1,
        interactive=True,
        cross_origin=False,
        show=False
    ).add_to(m)

folium.LayerControl(collapsed=False).add_to(m)
m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

st.subheader("Peta interaktif")
st.caption("Pilih citra satelit atau peta jalan, lalu aktifkan kelas melalui kontrol layer di kanan atas peta.")

st_folium(
    m,
    use_container_width=True,
    height=650,
    returned_objects=[]
)

# Statistik kelas
st.subheader("Distribusi kelas")
total = int(np.count_nonzero(valid))
rekap = []

for kode, nama in KELAS.items():
    jumlah = int(np.count_nonzero(hasil == kode))
    rekap.append({
        "Kode": kode,
        "Kelas": nama,
        "Jumlah piksel": jumlah,
        "Persentase (%)": round(jumlah / total * 100, 2) if total else 0
    })

df = pd.DataFrame(rekap)
st.dataframe(df, use_container_width=True, hide_index=True)

st.download_button(
    "Unduh tabel CSV",
    data=df.to_csv(index=False).encode("utf-8-sig"),
    file_name="distribusi_tutupan_lahan_jatim.csv",
    mime="text/csv"
)

st.download_button(
    "Unduh peta GeoTIFF",
    data=FILE_TIF.read_bytes(),
    file_name=FILE_TIF.name,
    mime="image/tiff"
)

st.warning(
    "Hasil klasifikasi merupakan estimasi model dan perlu divalidasi "
    "menggunakan data referensi independen."
)
