import streamlit as st
import rasterio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from pathlib import Path

st.set_page_config(
    page_title="Klasifikasi Tutupan Lahan Jawa Timur",
    page_icon="🛰️",
    layout="wide"
)

st.title("🛰️ Klasifikasi Tutupan Lahan Jawa Timur")
st.caption("Pemetaan Sentinel-2 L2A menggunakan Random Forest")

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
    st.error(f"File raster tidak ditemukan: {FILE_TIF.name}")
    st.stop()

@st.cache_data
def baca_raster(path):
    with rasterio.open(path) as src:
        return src.read(1), str(src.crs), tuple(src.bounds)

hasil, crs, bounds = baca_raster(str(FILE_TIF))
valid = hasil > 0
total = int(valid.sum())

if total == 0:
    st.error("Tidak ada piksel klasifikasi yang valid.")
    st.stop()

rekap = []
for kode, nama in KELAS.items():
    jumlah = int(np.count_nonzero(hasil == kode))
    rekap.append({
        "Kode": kode,
        "Kelas": nama,
        "Jumlah piksel": jumlah,
        "Persentase (%)": round(jumlah / total * 100, 2)
    })

df = pd.DataFrame(rekap)

c1, c2, c3 = st.columns(3)
c1.metric("Piksel terklasifikasi", f"{total:,}".replace(",", "."))
c2.metric("Jumlah kelas", len(KELAS))
c3.metric("CRS raster", crs)

st.subheader("Peta klasifikasi")

fig, ax = plt.subplots(figsize=(12, 7))
peta = np.ma.masked_where(~valid, hasil)
cmap = ListedColormap([WARNA[i] for i in KELAS])

ax.imshow(peta, cmap=cmap, vmin=1, vmax=5, interpolation="nearest")
ax.set_axis_off()
ax.legend(
    handles=[Patch(facecolor=WARNA[k], label=KELAS[k]) for k in KELAS],
    loc="lower left",
    framealpha=0.95
)
st.pyplot(fig, use_container_width=True)
plt.close(fig)

st.caption(
    f"Batas raster: {bounds[0]:.4f}, {bounds[1]:.4f}, "
    f"{bounds[2]:.4f}, {bounds[3]:.4f}"
)

st.subheader("Distribusi kelas")
kiri, kanan = st.columns(2)

with kiri:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(
        df["Kelas"],
        df["Persentase (%)"],
        color=[WARNA[k] for k in df["Kode"]]
    )
    ax.set_ylabel("Persentase (%)")
    ax.tick_params(axis="x", rotation=25)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

with kanan:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.pie(
        df["Jumlah piksel"],
        labels=df["Kelas"],
        autopct="%1.1f%%",
        colors=[WARNA[k] for k in df["Kode"]],
        startangle=90
    )
    ax.axis("equal")
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

st.subheader("Tabel distribusi")
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
    "Hasil merupakan estimasi model. Validasi dengan data referensi independen "
    "diperlukan sebelum hasil digunakan sebagai luas tutupan lahan final."
)
