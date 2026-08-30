# Penambangan Data - A
Repository ini dibuat untuk Mata Kuliah Proyek Sains Data Kelas B Semester 5, Program Studi Teknik Informatika.

Nama: ShofiatulMahmudah
NIM: 24041100023

## Panduan Cepat Jupyter Book (materi-PSD)

### 1. Persiapan Environment (PowerShell)
```powershell
# Dari folder PSD
..\.venv\Scripts\Activate.ps1

# Jika terkendala execution policy
# Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
```

### 2. Instalasi Dependensi
```powershell
pip install "jupyter-book==1.0.0" ghp-import
```
**Catatan:**
- `jupyter-book==1.0.0` dipakai agar versi Jupyter Book konsisten untuk mata kuliah ini dan tetap mendukung alur `jupyter-book create`.
- `ghp-import` dipakai untuk deploy GitHub Pages dari hasil build HTML.

### 3. Membuat Struktur Buku Baru
```powershell
jupyter-book create materi-PSD
```

### 4. Menambahkan Halaman Baru
Buat file markdown, misalnya `materi-PSD/logika.md`.
Daftarkan ke daftar isi di `materi-PSD/_toc.yml`.
Contoh:
```yaml
format: jb-book
root: intro
chapters:
  - file: pertemuan1
  - file: Proyek Sains Data pertemuan 2
  - file: pertemuan3
  - file: logika
```

### 5. Build Website
```powershell
jupyter-book build materi-PSD
```
Hasil website ada di: `materi-PSD/_build/html/index.html`

## Panduan Git (Push ke origin)

### 1. Cek perubahan
```powershell
git status
```

### 2. Stage semua perubahan
```powershell
git add .
```

### 3. Commit
```powershell
git commit -m "update materi pertemuan 3"
```

### 4. Push ke branch utama
```powershell
git push origin main
```

## Deploy GitHub Pages
Setelah build berhasil, deploy folder HTML ke branch `gh-pages`:
```powershell
ghp-import -n -p -f materi-PSD/_build/html
```
Keterangan opsi:
- `-n`: membuat file `.nojekyll`
- `-p`: langsung push ke remote
- `-f`: force overwrite branch `gh-pages`

URL situs biasanya: `https://username-kamu.github.io/nama-repo-kamu/`
