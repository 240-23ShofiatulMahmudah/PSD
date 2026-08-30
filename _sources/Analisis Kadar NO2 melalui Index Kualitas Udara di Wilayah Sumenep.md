---
title: Analisis Kadar NO2 melalui Index Kualitas Udara di Wilayah Sumenep

---

# Analisis Kadar NO2 melalui Index Kualitas Udara di Wilayah Sumenep

## 1. BUSINESS UNDERSTANDING
### a. Mengamati Kualitas Udara

Indeks Kualitas Udara (Air Quality Index/AQI) merupakan indikator yang digunakan untuk menggambarkan kondisi kualitas udara berdasarkan konsentrasi beberapa polutan di atmosfer. Semakin tinggi tingkat pencemaran, semakin buruk kualitas udara dan semakin besar potensi dampaknya terhadap kesehatan

| Polutan        | Sumber utama                                |
| -------------- | ------------------------------------------- |
| **NO₂**        | Kendaraan, industri, pembakaran bahan bakar |
| **CO**         | Pembakaran tidak sempurna                   |
| **SO₂**        | Industri dan pembakaran bahan bakar fosil   |
| **O₃**         | Reaksi kimia polutan di atmosfer            |
| **PM2.5/PM10** | Debu, kendaraan, pembakaran, industri       |

### b. Polutan yang diamati

Pada penelitian ini, polutan yang diamati adalah Nitrogen Dioksida (NO₂). NO₂ dipilih karena merupakan salah satu parameter kualitas udara yang tersedia pada data Sentinel-5P/TROPOMI dari Copernicus dan dapat digunakan untuk mengamati perubahan NO₂ secara temporal maupun spasial.

### c. Tujuan

Menganalisis perubahan nilai NO₂ di wilayah Sumenep selama periode 24 Agustus 2025 sampai 24 Agustus 2026 berdasarkan data Sentinel-5P/TROPOMI.


## 2. DATA UNDERSTANDING
### a. Sumber Data

Data NO₂ diperoleh dari Copernicus Data Space Ecosystem menggunakan satelit **Sentinel-5P/TROPOMI**. Data diunduh dalam format CSV time-series.

Sumber: https://dataspace.copernicus.eu/

**Dataset:** 
![Download Data csv](Dataset.csv)

| Keterangan       | Isi                               |
| ---------------- | --------------------------------- |
| Sumber           | Copernicus Data Space Ecosystem   |
| Satelit          | Sentinel-5P                       |
| Instrumen        | TROPOMI                           |
| Parameter        | NO₂                               |
| Jenis data       | Tropospheric NO₂ Column           |
| Satuan           | mol/m²                            |
| Wilayah          | Sumenep, Madura                   |
| Periode          | 24 Agustus 2025 – 24 Agustus 2026 |
| Format           | CSV                               |
| Jumlah observasi | 294                               |


**Wilayah:**
| Parameter  | Nilai                   |
| ---------- | ----------------------- |
| Wilayah    | Sumenep, Madura         |
| Bentuk AOI | Polygon                 |
| Longitude  | 113.608246 – 114.114990 |
| Latitude   | -7.134248 – -6.865082   |
| Format     | GeoJSON                 |

```
{
  "type": "Polygon",
  "coordinates": [
    [
      [113.608246, -6.865082],
      [114.11499, -6.865082],
      [114.11499, -7.134248],
      [113.608246, -7.134248],
      [113.608246, -6.865082]
    ]
  ]
}
```

* ![Download File GeoJSON](AOI_Sumenep.geojson)

![Peta AOI Sumenep](1.png)

## 3. EKSPLORASI DATA CSV
### a. Upload CSV ke Google Colab
jalankan:
```
from google.colab import files

uploaded = files.upload()
```
![image](3.png)

### b. Jalankan kode analisis ini
Setelah upload, jalankan:
```
import pandas as pd
import matplotlib.pyplot as plt

# Membaca file CSV
file_name = next(iter(uploaded))
df = pd.read_csv(file_name)

# Mengubah kolom tanggal
df["C0/date"] = pd.to_datetime(df["C0/date"])

# Mengurutkan berdasarkan tanggal
df = df.sort_values("C0/date")

# Menampilkan informasi dataset
print("Jumlah data:", len(df))
print("Tanggal awal:", df["C0/date"].min().date())
print("Tanggal akhir:", df["C0/date"].max().date())

# Statistik NO2
print("\nStatistik NO2:")
print(df["C0/mean"].describe())
```
![image](4.png)

### c. Buat grafik time-series
```
plt.figure(figsize=(12,5))

plt.plot(
    df["C0/date"],
    df["C0/mean"]
)

plt.title("Perubahan NO₂ di Sumenep")
plt.xlabel("Tanggal")
plt.ylabel("NO₂ (mol/m²)")
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()
```
![image](5.png)

### d. Buat grafik rata-rata bulanan

```
monthly = (
    df.set_index("C0/date")["C0/mean"]
    .resample("ME")
    .mean()
    .reset_index()
)

plt.figure(figsize=(12,5))

plt.plot(
    monthly["C0/date"],
    monthly["C0/mean"],
    marker="o"
)

plt.title("Rata-rata Bulanan NO₂ di Sumenep")
plt.xlabel("Bulan")
plt.ylabel("NO₂ (mol/m²)")
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()
```
![image](6.png)

### e. Simpan hasil rata-rata bulanan sebagai CSV
```
monthly.to_csv(
    "NO2_Sumenep_Bulanan.csv",
    index=False
)

print("CSV berhasil dibuat.")
```
Eksplorasi data dilakukan menggunakan Google Colab dengan Python. Data CSV NO₂ diolah untuk melihat perubahan nilai NO₂ berdasarkan waktu. Analisis dilakukan menggunakan nilai rata-rata NO₂ (C0/mean) dan divisualisasikan dalam bentuk grafik time-series serta rata-rata bulanan.

## 4. VISUALISASI PETA DENGAN FOLIUM
Membuat peta wilayah pengamatan Sumenep menggunakan:

GeoJSON + Folium + Google Colab
### a. Upload GeoJSON
di google colab:
```
from google.colab import files

uploaded_geojson = files.upload()
```

![image](7.png)

### b. Buat peta
```
import folium
import json

# Membaca GeoJSON
file_geojson = next(iter(uploaded_geojson))

with open(file_geojson, "r") as f:
    geojson_data = json.load(f)

# Membuat peta
m = folium.Map(
    location=[-7.0, 113.85],
    zoom_start=9
)

# Menambahkan AOI
folium.GeoJson(
    geojson_data,
    name="AOI Sumenep",
    tooltip="Wilayah Pengamatan Sumenep"
).add_to(m)

folium.LayerControl().add_to(m)

m
```
Setelah dijalankan, akan muncul peta interaktif.
![image](8.png)

### c. Simpan peta
```
m.save("Peta_AOI_Sumenep.html")
```
file yang dihasilkan:
```
Peta_AOI_Sumenep.html
```
Visualisasi spasial dilakukan menggunakan Folium dengan memanfaatkan file GeoJSON sebagai batas wilayah pengamatan. Peta digunakan untuk menampilkan Area of Interest (AOI) penelitian di wilayah Sumenep.

## 5. ANALISIS HASIL GRAFIK
Gunakan hasil grafik time-series dan rata-rata bulanan dari Point 3.
### a. Cari 3 hal dari grafik

Catat:

1. Nilai NO₂ tertinggi dan tanggalnya.
1. Nilai NO₂ terendah dan tanggalnya.
1. Bulan dengan rata-rata NO₂ tertinggi dan terendah.

Dari data CSV yang kamu gunakan sebelumnya, hasilnya:

* Tertinggi: 10 Desember 2025 → 3.5046 × 10⁻⁵ mol/m²
* Terendah: 16 November 2025 → -1.3911 × 10⁻⁶ mol/m²
* Rata-rata bulanan tertinggi berada pada Januari–Februari 2026.

### b. Buat interpretasi singkat
Berdasarkan hasil visualisasi, nilai NO₂ di wilayah pengamatan Sumenep mengalami fluktuasi selama periode 24 Agustus 2025–24 Agustus 2026. Nilai NO₂ tertinggi tercatat pada 10 Desember 2025, sedangkan nilai terendah tercatat pada 16 November 2025. Rata-rata bulanan menunjukkan nilai relatif tinggi pada akhir 2025 hingga awal 2026 dan kemudian mengalami perubahan pada bulan-bulan berikutnya.

### c. Catat statistik utama
| Statistik        |                 Hasil |
| ---------------- | --------------------: |
| Jumlah observasi |                   294 |
| Rata-rata NO₂    |  1.3293 × 10⁻⁵ mol/m² |
| Minimum          | −1.3911 × 10⁻⁶ mol/m² |
| Maksimum         |  3.5046 × 10⁻⁵ mol/m² |

## 6. OUTPUT CSV HASIL ANALISIS
### a. Buat CSV rata-rata bulanan
```
monthly.to_csv(
    "NO2_Sumenep_Bulanan.csv",
    index=False
)
```
### b. Download CSV
```
from google.colab import files

files.download("NO2_Sumenep_Bulanan.csv")
```
file terunduh:

![Download Data NO2](NO2_Sumenep_Bulanan.csv)

Hasil pengolahan data NO₂ kemudian dirangkum berdasarkan rata-rata bulanan dan disimpan dalam format CSV. File tersebut digunakan sebagai data hasil analisis dan dapat digunakan kembali untuk visualisasi atau pembuatan dashboard.

## 7. Kesimpulan
Data Sentinel-5P/TROPOMI dari Copernicus dapat digunakan untuk mengamati perubahan NO₂ di wilayah Sumenep. Selama periode 24 Agustus 2025–24 Agustus 2026, nilai NO₂ mengalami fluktuasi dari waktu ke waktu. Analisis dilakukan menggunakan Python untuk menghasilkan statistik dan visualisasi grafik, sedangkan Folium digunakan untuk menampilkan wilayah pengamatan berdasarkan AOI GeoJSON.