# Laporan Tim — Kelompok 13, Kasus 13 (Pemuda NEET dan Pekerja Anak)

Satu dokumen bersama, enam bagian. Angka ditarik ulang secara presisi dari `data/silver/silver.parquet`, `data/gold/`, dan `log-keputusan.csv` yang sudah di-*commit*.

---

## 1. Ringkasan
Kelompok 13 menangani **Kasus 13 (Klaster C: Gender dan Ketenagakerjaan)** yang mencakup 7 seri indikator: 2 seri utama BPS (`var1186` — Persentase Pemuda NEET usia 15–24 dan `var2658` — Persentase Pekerja Anak usia 5–17), 2 seri pembanding World Development Indicators / WDI (`SL.UEM.NEET.ZS` dan `SL.TLF.0714.ZS`), serta 3 seri pembanding ILOSTAT (`SDG_0861_SEX_RT`, `SDG_A871_SEX_AGE_RT`, dan `SDG_B871_SEX_AGE_RT`). 

Temuan utama terkait kualitas data menunjukkan bahwa data BPS memiliki konsistensi internal sempurna (selisih nilai $0.00$ antara berkas CSV datar dan JSON WebAPI pada seluruh 605 observasi), namun memiliki dinamika kelengkapan grid observasi pada provinsi pemekaran baru Papua (2024–2025) serta disparitas konseptual kelompok umur dan instrumen survei yang signifikan saat direkonsiliasi dengan seri global ILO dan Bank Dunia.

---

## 2. Data dan Lineage
- **Sumber Data:** Berkas mentah terdiri dari 16 berkas di `data/raw/` yang terverifikasi cocok 100% terhadap `MANIFEST.csv` melalui fungsi `src.common.manifest.periksa()`:
  - BPS: 4 berkas nilai (2 CSV, 2 WebAPI JSON) + 1 berkas `manifest_asal.json`. Total: 1.210 baris observasi riil di Silver.
  - WDI: 1 berkas data JSON (`data/kelompok-06-hal-01.json`) + 2 berkas metadata indikator. Dari 3.894 baris mentah, 132 baris terkait Kasus 13, dan 31 observasi riil non-null dimuat ke Silver.
  - ILOSTAT: 3 berkas data SDMX-CSV + 5 berkas struktur DSD JSON dan metadata dataflow. Total: 84 baris observasi riil di Silver.
- **Pembentukan Lineage:** Setiap baris pada `data/silver/silver.parquet` menyematkan dua kolom lineage wajib: `_berkas_raw` (jalur relatif berkas sumber terhadap `data/raw/`) dan `_sha256_raw` (sidik jari kriptografis heksadesimal 64 karakter dari `MANIFEST.csv`), menjamin auditabilitas penuh ke sumber primer.

---

## 3. Masalah Data dan Penanganannya

### A. Tabel Rekapitulasi Masalah Data & Keputusan Pembersihan

| No | Kategori Masalah | Seri Terdampak | Baris / Kasus Terdampak | Rujukan Keputusan | Tindakan & Keputusan Pembersihan | Alternatif yang Ditolak | Dampak Terhadap Silver |
|:---:|:---|:---|:---:|:---:|:---|:---|:---:|
| 1 | **Format Wilayah & DOB Baru** | Semua seri BPS | 38 provinsi (termasuk 4 DOB Papua) | **K-001** | Standarisasi ke susunan 38 provinsi tahun 2025 (kode 2 digit BPS $\times 100$) dan 9999 untuk nasional. Empat provinsi baru Papua (`9200`, `9500`, `9600`, `9700`) diisi hanya pada tahun amatan yang tersedia (2024–2025) tanpa mengubah nilai historis provinsi induk. | Menggabungkan data DOB ke provinsi induk (`9100` dan `9400`) dengan pembobotan populasi, atau mengimputasi nilai historis 2015–2023. | Mempertahankan keaslian lineage riil BPS tanpa bias estimasi (0 baris diubah). |
| 2 | **Celah Panel (Missing Values)** | WDI (`SL.TLF.0714.ZS`, `SL.UEM.NEET.ZS`) | 101 baris pengamatan | **K-002** | Menyaring 101 baris amatan bernilai null (`NaN`) pada berkas mentah WDI sehingga hanya menyimpan 31 baris observasi riil non-null di Silver. | Mengimputasi nilai kosong (*forward-fill* / interpolasi) atau membiarkan nilai null masuk ke Silver. | Mengurangi 101 baris null dari berkas mentah WDI; Silver bersih dari nilai kosong. |
| 3 | **Format & Variasi Satuan** | Semua seri (7 seri) | 1.325 baris Silver | **K-003** | Menyeragamkan seluruh nilai satuan menjadi string tunggal `'persen'` pada lapis Silver berdasarkan metadata resmi BPS, WDI, dan ILOSTAT DSD. | Mempertahankan variasi string mentah seperti `'Persen'` (BPS), string kosong (WDI), atau `'PT'` (ILOSTAT). | Seluruh 1.325 baris Silver memiliki satuan seragam `'persen'`. |
| 4 | **Encoding Rincian Demografi** | BPS, WDI, ILOSTAT | 1.325 baris Silver | **K-004** | Membakukan kolom rincian: `'total'` untuk agregat nasional/provinsi tanpa disagregasi (BPS, WDI, ILO SEX_T), serta mengombinasikan kode dimensi demografi ILOSTAT (`'laki-laki'`, `'perempuan'`, `'15-17'`, `'laki-laki_15-17'`, `'perempuan_15-17'`). | Membuang rincian jenis kelamin dan kelompok umur pada ILOSTAT untuk memaksakan struktur tunggal sejak Silver. | Menyimpan rincian demografi apa adanya di Silver untuk seleksi analitis pada Gold. |
| 5 | **Deduplikasi Format Mentah** | BPS (`var1186`, `var2658`) | 1.210 baris (605 pasang kunci) | **K-005**, **K-009** | Menyimpan seluruh observasi dari berkas CSV datar (605 baris) dan JSON WebAPI (605 baris) di Silver dengan pembeda kolom `_berkas_raw`. Uji silang membuktikan selisih nilai $0.00$ pada seluruh 605 pasang kunci. | Memilih salah satu format secara sepihak dan membuang format lainnya sebelum masuk Silver. | 1.210 baris BPS disimpan di Silver; konsistensi antar-format terbukti $100\%$. |
| 6 | **Celah Observasi DOB Papua** | `var1186`, `var2658` | 38 sel kosong panel | **K-006** | Menetapkan status 4 DOB Papua: `belum_terbentuk` (<2022), `masa_transisi` (2022), dan `eligible` (mulai 2023). Ketiadaan data pada masa transisi tidak dihitung sebagai missing value galat survei. | Menghitung seluruh 38 provinsi sebagai eligible sejak 2015 sehingga memunculkan *false missingness*. | Mencegah salah tafsir kelengkapan panel pada evaluasi kualitas data. |
| 7 | **Outlier Riil vs Patahan Serentak** | `var1186`, `var2658` | 29 kandidat anomali | **K-007**, **K-008** | Mengklasifikasikan 29 kandidat anomali menjadi **23 outlier asli** dan **6 patahan diduga** (berdasarkan ambang pergerakan serentak $\ge 80\%$ wilayah searah). Seluruh nilai riil dipertahankan di Silver tanpa diubah (`nilai_diubah = tidak`). | Menghapus kandidat atau mengganti nilai ekstrem dengan median wilayah / imputasi. | Menjaga integritas data asli; 0 galat input numerik teridentifikasi. |
| 8 | **Patahan Metode ILO & Rekonsiliasi** | ILO `SDG_A871`, `SDG_B871` | 84 baris observasi | **K-010** | Menandai deret A871 sebagai patahan metode (2009 bersumber survei CLS, 2019 & 2023 bersumber Sakernas/LFS). Mencatat bahwa amatan 2009 A871 dan B871 bernilai identik karena kelompok 15–17 didefinisikan sama dari survei yang sama. | Menghapus salah satu seri sebagai duplikat, atau menganggap keduanya sebagai dua bukti independen. | Kedua seri dipertahankan sebagai seri terpisah sesuai kode DSD ILOSTAT. |
| 9 | **Koreksi Katalog & Kelompok Umur** | Semua seri pekerja anak | 4 seri pekerja anak | **K-011** | Mendokumentasikan perbedaan kelompok umur resmi: BPS 5–17 tahun (`var2658`), ILO 15–17 tahun (`SDG_A871`), dan WDI 7–14 tahun (`SL.TLF.0714.ZS`). Pasangan rekonsiliasi dikategorikan sebagai *perbedaan definisi/cakupan*. | Memaksakan perbandingan langsung tanpa koreksi catatan metadata kelompok umur. | Menghindari interpretasi keliru saat rekonsiliasi selisih angka antarsumber. |

---

### B. Rincian Temuan Kunci Profiling Data (Bahan Paparan Demo Sprint 1)

#### 1. Celah Panel dan Dinamika Wilayah Pemekaran Baru (DOB Papua)
Analisis kelengkapan matriks wilayah $\times$ periode (`reports/kelengkapan_panel_per_tahun.csv`) menunjukkan bahwa panel data Kasus 13 tidak berbentuk bujursangkar sempurna (*unbalanced panel*) akibat pemekaran wilayah administratif:
- **Seri NEET (`var1186`):**
  - Rentang 2015–2022: Terisi lengkap 34 provinsi (100% keterisian).
  - Tahun 2023: 38 provinsi berstatus eligible, 34 provinsi terisi, 4 DOB Papua belum terisi (89.47% keterisian).
  - Tahun 2024–2025: Terisi lengkap 38 provinsi (100% keterisian).
- **Seri Pekerja Anak (`var2658`):**
  - Rentang 2020–2022: Terisi lengkap 34 provinsi (100% keterisian).
  - Tahun 2023: 34 terisi dari 38 eligible (89.47% keterisian).
  - Tahun 2024: 36 terisi dari 38 eligible (94.74% keterisian; amatan Papua Barat Daya dan Papua Selatan belum tercakup).
  - Tahun 2025: 34 terisi dari 38 eligible (89.47% keterisian; amatan Kep. Riau, Papua Barat Daya, Papua Pegunungan, dan Papua Selatan tidak tersedia pada rilis BPS).
- **Celah Data WDI:** Berkas mentah WDI memuat 101 baris `null` pada indikator Indonesia karena WDI menyediakan slot tahunan 1960–2025 meskipun survei empiris pekerja anak dan NEET hanya dilakukan pada tahun-tahun tertentu. Penyaringan 101 baris kosong menghasilkan 31 baris observasi riil yang bersih di Silver.

#### 2. Analisis 29 Kandidat Anomali: Outlier Asli vs Patahan Struktural
Pemeriksaan anomali statistik menggunakan ambang gabungan $1.5 \times \text{IQR}$ dan $|Z\text{-score}| > 3$ mendeteksi **29 kandidat anomali** (14 pada `var1186` dan 15 pada `var2658`). Berdasarkan analisis pergerakan serentak wilayah (`reports/tahun_serentak.csv`) dengan ambang $\ge 80\%$ wilayah searah, kandidat dipilah menjadi:
1. **23 Outlier Asli (*Genuine Outliers*):**
   - Merupakan cerminan disparitas riil ketenagakerjaan daerah.
   - Provinsi Bali (`var1186` berkisar 5.33% s.d. 14.90%) dan DI Yogyakarta (9.78% s.d. 14.24%) secara konsisten berada jauh di bawah median nasional (22.25%) karena tingginya partisipasi sekolah dan serapan sektor pariwisata/jasa.
   - Provinsi Maluku (puncak 35.38% pada 2023) dan Sulawesi Utara (puncak 33.54% pada 2022) mencatat angka NEET tertinggi akibat terbatasnya serapan industri formal bagi pemuda lulusan sekolah menengah.
2. **6 Patahan Diduga (*Suspected Structural Breaks*):**
   - **Tahun 2020 (`var1186`):** Terjadi kenaikan serentak pada **88.24% wilayah**. Kandidat anomali Bali (naik dari 9.40% ke 14.90%) dan DIY (naik dari 9.78% ke 12.71%) bergerak searah dengan guncangan makro pandemi COVID-19 yang menutup sektor pariwisata.
   - **Tahun 2021 (`var1186`):** Terjadi penurunan serentak pada **82.35% wilayah**. Kandidat anomali DIY (turun dari 12.71% ke 9.89%) bergerak searah dengan fase pemulihan ekonomi pasca pembatasan sosial.
   - **Tahun 2024 (`var1186`):** Terjadi penurunan serentak pada **88.24% wilayah**, termasuk penurunan Bali ke 7.26%.
   - **Tahun 2024 (`var2658`):** Terjadi lonjakan pekerja anak serentak pada **81.25% wilayah**, ditandai kenaikan tajam di Nusa Tenggara Timur (dari 3.57% ke 5.18%) dan Sulawesi Tenggara (dari 2.83% ke 5.12%).
3. **Konfirmasi Galat Input:**
   - Hasil audit pada `reports/ringkasan_pemeriksaan_kualitas.csv` membuktikan **0 nilai negatif**, **0 nilai di atas 100**, **0 duplikat baris**, dan **0 nilai berkali lipat dari median wilayah**. Oleh karena itu, diputuskan tidak ada nilai yang diubah atau dihapus (`nilai_diubah = tidak`).

#### 3. Konsistensi Internal Multi-Format BPS (CSV vs WebAPI JSON)
BPS menyediakan data dalam dua kanal distribusi: berkas CSV unduhan statis dan respons JSON dari WebAPI. Uji silang pada 605 observasi BPS membuktikan:
- Seluruh 605 kombinasi kunci komposit `(seri_kode, wilayah_kode, periode)` berpasangan sempurna antara CSV dan JSON.
- Nilai numerik persentase identik hingga desimal terakhir ($\Delta = 0.000000$).
- Hal ini membuktikan bahwa pada snapshot per 17 Oktober 2026, belum ada revisi data antara kedua saluran distribusi BPS.

#### 4. Keterbandingan Metodologi & Definisi Seri Pembanding Global
Pemeriksaan metadata ILOSTAT DSD dan WDI mengonfirmasi batasan komparabilitas yang krusial untuk persiapan integrasi Tahap 6:
- **Indikator NEET (SDG 8.6.1):** Definisi BPS (`var1186`), ILO (`SDG_0861_SEX_RT`), dan WDI (`SL.UEM.NEET.ZS`) selaras pada kelompok umur **15–24 tahun**. Seri WDI dan total ILO terbukti bernilai identik 100% (contoh: tahun 2023 nasional tercatat 16.99% di kedua sumber global, dibandingkan 21.01% pada BPS), menunjukkan bahwa World Bank mengadopsi data terharmonisasi ILO.
- **Indikator Pekerja Anak (SDG 8.7.1):**
  - BPS (`var2658`): Mengukur persentase anak usia **5–17 tahun** yang bekerja (rentang 0.38% s.d. 6.32%).
  - ILO Definisi A (`SDG_A871_SEX_AGE_RT`): Secara konseptual mencakup 5–17 tahun, namun berkas amatan empiris Indonesia hanya memuat kelompok umur **15–17 tahun** (`AGE_CLDVERSION_Y15-17`) dengan amatan riil tahun 2023 sebesar 1.70% (laki-laki 2.10%, perempuan 1.30%).
  - WDI (`SL.TLF.0714.ZS`): Mengukur anak usia **7–14 tahun** pada periode 1996–2010 (rentang 3.70% s.d. 9.94%), sehingga memiliki irisan waktu 0 tahun dengan data BPS (2020–2025).

---

## 4. Integrasi dan Rekonsiliasi
*(Draf awal telah disiapkan pada `reports/daftar_pasangan_rekonsiliasi.md` dan `reports/tabel_nasional_periode_seri.csv` dengan 5 pasangan teridentifikasi; analisis selisih kuantitatif penuh dan dekomposisi revisi akan dikerjakan pada Sprint 2).*

---

## 5. Validasi dan Reproduksibilitas
- **Skema Validasi Otomatis:** Diuji melalui pustaka Pandera (`src/validasi/validasi_silver.py`) dengan 16 aturan ketat yang mencakup validasi tipe kolom, kelengkapan 11 atribut, batasan rasio persentase ($0 \le \text{nilai} \le 100$), regex periode tahun `^\d{4}$`, konsistensi satuan tunggal, dan kecocokan hash SHA-256 terhadap `MANIFEST.csv`. Hasil validasi: **16/16 aturan LOLOS** (`reports/validasi.md`).
- **Waktu Eksekusi Satu Perintah:** Perintah `python pipeline.py` menyelesaikan seluruh tahapan (ekstraksi 16 berkas mentah $\to$ transformasi Silver 1.325 baris $\to$ pembentukan tabel nasional Gold $\to$ validasi dasar Pandera) dalam waktu $\approx 0.6$ detik pada mesin pengembang lokal.

---

## 6. Pembagian Kerja Tim

| Anggota Tim | NIM | Komponen Utama | Tugas Sampingan | Kontribusi Utama Sprint 1 & Tanggung Jawab Laporan |
|---|:---:|---|---|---|
| **Alfayya Rafif Abiyyi Rosyid Ridlo** | 124450006 | Ekstraksi dan Lineage (Tahap 1) | Integrator Tim | Menulis Bagian 2 (*Data dan lineage*) & mengawal penggabungan 24 PR serta alur reproduksi pipeline (`reports/integrasi_sprint1.md`). |
| **Anggun Nita** | 124450009 | Validasi dan Dokumentasi (Tahap 8) | Reproduksi & Demo | Menulis Bagian 5 (*Validasi dan reproduksibilitas*), mengembangkan 16 aturan Pandera (`reports/validasi.md`), dan memimpin rekaman Demo Sprint 1. |
| **Ashila Islamisahfa Vanisha** | 124450028 | Profil dan Pembersihan Data (Tahap 2–3) | Analis Utama | Menulis Bagian 3 (*Masalah data dan penanganannya*), menganalisis 29 anomali, kelengkapan grid panel DOB Papua, dan materi presentasi demo. |
| **Kaleb Filbert Istel** | 124450053 | Integrasi, Penyimpanan, & Skala (Tahap 5–7) | Koordinator Tim & Data Keeper | Menulis Bagian 1 (*Ringkasan*), Bagian 4 (*Integrasi dan rekonsiliasi*), merancang skema SQL Silver (`silver.db`), dan tabel nasional Gold (`tabel_nasional.parquet`). |
