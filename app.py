
import base64
import io

import folium
import numpy as np
import rasterio
import streamlit as st
from PIL import Image
from rasterio.warp import transform_bounds
from streamlit_folium import st_folium

st.set_page_config(page_title="Klasifikasi Tutupan Lahan Modung", layout="wide")
st.title("Peta Klasifikasi Tutupan Lahan — Modung")
st.caption("Klasifikasi Sentinel-2 dengan lima kelas tutupan lahan.")

warna = {
    "Bangunan": (229, 57, 53),
    "Pertanian": (253, 216, 53),
    "Perairan": (30, 136, 229),
    "Hutan biasa": (46, 125, 50),
    "Mangrove": (142, 36, 170),
}

kode_kelas = {
    "Bangunan": 1,
    "Pertanian": 2,
    "Perairan": 3,
    "Hutan biasa": 4,
    "Mangrove": 5,
}

@st.cache_data
def baca_raster():
    with rasterio.open("klasifikasi_modung.tif") as src:
        arr = src.read(1)
        bounds = transform_bounds(src.crs, "EPSG:4326", *src.bounds)
    return arr, bounds

hasil, bounds = baca_raster()
west, south, east, north = bounds
center = [(south + north) / 2, (west + east) / 2]

peta = folium.Map(location=center, zoom_start=15, tiles=None)

folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Tiles © Esri",
    name="Citra satelit",
    overlay=False,
).add_to(peta)

for nama, kode in kode_kelas.items():
    rgba = np.zeros((*hasil.shape, 4), dtype=np.uint8)
    mask = hasil == kode
    rgba[mask, :3] = warna[nama]
    rgba[mask, 3] = 165

    buffer = io.BytesIO()
    Image.fromarray(rgba).save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    image_uri = "data:image/png;base64," + encoded

    folium.raster_layers.ImageOverlay(
        image=image_uri,
        bounds=[[south, west], [north, east]],
        name=nama,
        opacity=1,
        show=False,
    ).add_to(peta)

folium.LayerControl(collapsed=False).add_to(peta)
peta.fit_bounds([[south, west], [north, east]])

st.markdown(
    "**Petunjuk:** gunakan kontrol layer di kanan atas peta "
    "untuk menampilkan satu atau beberapa kelas."
)
st_folium(peta, use_container_width=True, height=650)

st.subheader("Legenda kelas")
for nama, rgb in warna.items():
    st.markdown(
        f'<span style="display:inline-block;width:14px;height:14px;'
        f'background:rgb{rgb};margin-right:8px"></span>{nama}',
        unsafe_allow_html=True,
    )

st.caption(
    "Hasil merupakan klasifikasi awal berbasis sampel. "
    "Periksa kembali akurasi tiap kelas sebelum digunakan sebagai "
    "data resmi atau untuk pengambilan keputusan."
)
