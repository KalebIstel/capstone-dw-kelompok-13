# Laporan Uji Reproduksi Klon Bersih & Panduan Demo Sprint 1

* **Penanggung Jawab:** Anggun Nita (NIM: 124450009)
* **Peran:** Validasi & Dokumentasi (Tahap 8) serta Reproduksi & Demo Tim
* **Kelompok:** 13 (Klaster C: Gender dan Ketenagakerjaan)
* **Kasus:** 13 — Pemuda NEET dan Pekerja Anak (SDG 8.6.1 & SDG 8.7.1)
* **Status Tugas Papan Tim:** Kartu #19 (*Uji reproduksi dari klon bersih dan rekaman Demo Sprint 1*)
* **Tanggal Pelaporan:** 22 November 2026

---

## 1. Ringkasan Eksekutif Uji Reproduksi

Sesuai kriteria evaluasi Capstone Data Wrangling, seluruh hasil kerja tim harus dapat direproduksi secara mandiri dari klon bersih (*fresh clone*) menggunakan satu perintah utama:
```bash
python pipeline.py
```
Uji reproduksi ini membuktikan bahwa:
1. Repositori bersih yang dikloning ke folder baru dapat mengunduh seluruh 16 berkas mentah Kasus 13 yang cocok 100% dengan `MANIFEST.csv`.
2. Pipeline otomatis mentransformasikan data mentah menjadi `data/silver/silver.parquet` (1.325 baris) yang bernilai deterministik dan identik dengan versi yang di-commit di repositori.
3. Seluruh tahapan berjalan tuntas dalam waktu **$\approx 1.7$ detik**, jauh di bawah ambang batas toleransi evaluasi dosen (15 menit).
4. Skema minimal lantai (`src.common.skema`) dan 16 aturan validasi deklaratif Pandera (`reports/validasi.md`) lulus 100% tanpa galat.

---

## 2. Catatan Waktu Eksekusi (*Benchmark Logs*)

Berikut adalah catatan waktu eksekusi riil dari lingkungan bersih (*fresh run*) pada mesin pengembang (Windows AMD64, Python 3.13):

| Tahapan Reproduksi | Perintah CLI | Durasi Rata-rata | Status | Hasil Utama |
|---|---|:---:|:---:|---|
| **0. Unduh Data Mentah** | `python unduh_data.py --kasus 13` | $\approx 4.2\text{ s}$ | **SUKSES** | 16 berkas mentah terekstrak ke `data/raw/` cocok SHA-256 |
| **1. Tahap Ekstraksi** | Bagian dari `pipeline.py` | $0.3\text{ s}$ | **SUKSES** | 1.426 baris mentah terbaca dengan lineage `_sha256_raw` |
| **2. Tahap Transformasi Silver** | Bagian dari `pipeline.py` | $0.5\text{ s}$ | **SUKSES** | `data/silver/silver.parquet` (1.325 baris, 7 seri, 39 wilayah) |
| **3. Tahap Persiapan Gold** | Bagian dari `pipeline.py` | $0.7\text{ s}$ | **SUKSES** | `data/gold/tabel_nasional.parquet` (30 periode $\times$ 13 kolom) |
| **4. Tahap Validasi Pandera** | Bagian dari `pipeline.py` | $0.2\text{ s}$ | **SUKSES** | 16/16 aturan Pandera lolos di `reports/validasi.md` |
| **Total Waktu Pipeline** | `python pipeline.py` | **$\approx 1.7\text{ s}$** | **SUKSES** | Alur satu perintah tuntas *end-to-end* |
| **5. Uji Skema Minimal** | `python -m src.common.skema data/silver/silver.parquet` | $0.4\text{ s}$ | **SUKSES** | `LOLOS 1,325 baris, 7 seri, 39 wilayah, 8 berkas sumber` |
| **6. Pemuatan SQL Silver** | `python src/silver/muat_sql.py` | $0.3\text{ s}$ | **SUKSES** | 1.325 baris termuat ke SQLite `data/silver/silver.db` |

> [!NOTE]
> Seluruh proses dari *fresh clone*, instalasi lingkungan, unduh data mentah, hingga validasi data selesai dalam waktu total kurang dari 2 menit.

---

## 3. Verifikasi Konsistensi Deterministik Parquet

Hasil pembentukan berkas `data/silver/silver.parquet` dari proses *fresh run* diverifikasi terhadap berkas yang telah di-commit di repositori:
- **Jumlah Baris:** 1.325 baris observasi (1.210 BPS + 31 WDI + 84 ILOSTAT).
- **Jumlah Kolom:** 11 kolom wajib skema Silver.
- **Rentang Nilai:** $0.38\%$ s.d. $41.23\%$.
- **Baris Kembar (*Duplicates*):** 0 baris kembar pada kunci komposit 6 atribut `(sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw)`.
- **Integritas Lineage:** 100% baris memiliki nilai `_berkas_raw` dan `_sha256_raw` yang sah dan tertelusur ke `MANIFEST.csv`.

---

## 4. Skenario Naskah Video Demo Sprint 1 ($\le 10$ Menit)

Video rekaman demo dirancang terstruktur dalam 4 babak utama sesuai panduan dosen:

### Babak 1: Pendahuluan, Berkas Mentah, & Audit Lineage (Menit 00:00 – 02:00)
- **Tujuan:** Memperlihatkan bahwa data berasal dari sumber otentik dan memiliki integritas kriptografis.
- **Tindakan di Layar:**
  - Menampilkan struktur repositori hasil klon bersih.
  - Membuka berkas `data/raw/MANIFEST.csv`.
  - Menjalankan perintah pemeriksaan kecocokan manifest:
    ```bash
    python -c "from src.common.manifest import periksa; print(periksa())"
    ```
  - Menjelaskan bahwa 16 berkas mentah Kasus 13 (BPS, WDI, ILOSTAT) cocok 100% dengan sidik jari SHA-256.

### Babak 2: Arsitektur Modul Pembaca Ekstraksi (Menit 02:00 – 04:00)
- **Tujuan:** Memperlihatkan modul ekstraksi modular di `src/ekstraksi/`.
- **Tindakan di Layar:**
  - Memperlihatkan skrip `src/ekstraksi/bps.py` (parser CSV dan WebAPI JSON dinamis).
  - Memperlihatkan skrip `src/ekstraksi/wdi.py` (penapisan 132 baris pengamatan kasus 13 dari berkas multi-indikator Bank Dunia).
  - Memperlihatkan skrip `src/ekstraksi/ilostat.py` (parser SDMX-CSV dan pembaca codelist DSD JSON).
  - Menyoroti bagaimana fungsi penempelan `_berkas_raw` dan `_sha256_raw` disematkan secara otomatis pada setiap pembaca.

### Babak 3: Eksekusi Alur Pipeline Satu Perintah & Basis Data (Menit 04:00 – 07:00)
- **Tujuan:** Mendemonstrasikan reproduksi satu perintah tim.
- **Tindakan di Layar:**
  - Menjalankan perintah utama di terminal:
    ```bash
    python pipeline.py
    ```
  - Memperlihatkan kecepatan eksekusi ($\approx 1.7$ detik) dan empat tahap yang berjalan mulus: ekstraksi $\to$ silver $\to$ gold $\to$ validasi.
  - Membuka dan memperlihatkan berkas keluaran: `data/silver/silver.parquet` (1.325 baris) dan `data/gold/tabel_nasional.parquet` (30 periode $\times$ 13 seri).
  - Menjalankan skrip pemuatan basis data relasional:
    ```bash
    python src/silver/muat_sql.py
    ```
  - Memperlihatkan ringkasan 1.325 baris Silver yang berhasil ditegakkan kunci primer kompositnya pada SQLite `data/silver/silver.db`.

### Babak 4: Pemeriksa Skema Minimal & Validasi Otomatis Pandera (Menit 07:00 – 09:30)
- **Tujuan:** Membuktikan kepatuhan skema dan kualitas data tanpa regresi.
- **Tindakan di Layar:**
  - Menjalankan uji lantai skema starter dosen:
    ```bash
    python -m src.common.skema data/silver/silver.parquet
    ```
    *(Output: LOLOS 1,325 baris, 7 seri, 39 wilayah, 8 berkas sumber).*
  - Membuka berkas laporan validasi otomatis [reports/validasi.md](file:///c:/Users/LENOVO/workbench-workspace/capstone-data-wrangling/reports/validasi.md).
  - Memperlihatkan 16 aturan Pandera yang diuji di `src/validasi/validasi_silver.py` dengan status 100% lolos (rentang persen 0–100, kode wilayah BPS 38 provinsi, keunikan 6 atribut komposit, dan kecocokan hash SHA-256).

### Penutup (Menit 09:30 – 10:00)
- **Tujuan:** Menyimpulkan ketercapaian seluruh *Definition of Done* Sprint 1 dan kesiapan melangkah ke Sprint 2 (penyusunan panel lebar dan tabel rekonsiliasi selisih).

---

## 5. Kesimpulan Kesiapan Kartu #19

Pengujian reproduksi klon bersih telah tuntas diverifikasi tanpa celah kegagalan. Dengan ketersediaan naskah skenario video di atas dan catatan waktu eksekusi yang terukur, seluruh kriteria *Definition of Done* untuk **Kartu Papan Tim #19** dinyatakan **SELESAI LENGKAP**.
