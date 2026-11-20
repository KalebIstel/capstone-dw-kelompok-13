# Daftar Pasangan Rekonsiliasi & Catatan Keterbandingan (Kasus 13)

* **Penyusun:** Kaleb Filbert Istel (NIM: 124450053)
* **Komponen:** Integrasi, Penyimpanan, dan Skala (Persiapan Tahap 6 — Sprint 1)
* **Kasus:** 13 — Klaster C: Pemuda NEET dan Pekerja Anak (SDG 8.6.1 & SDG 8.7.1)
* **Status Dokumen:** Rilis Resmi Persiapan Integrasi Sprint 1

---

## 1. Latar Belakang & Konteks Metodologi Seri

Sesuai panduan kelompok Kasus 13 dan panduan umum *Langkah Kerja Capstone Data Wrangling*, tahap integrasi bertugas menyandingkan seri utama (data BPS tingkat nasional/provinsi) dengan indikator pembanding internasional (ILOSTAT dan World Bank / WDI). Setiap selisih nilai antarsumber tidak dihapus atau dipaksa seragam, melainkan dipertahankan dan dijelaskan penyebabnya (kategori penjelasan: *definisi*, *metode*, *vintage*, *cakupan*, atau *belum terjelaskan*).

### A. Indikator Pemuda NEET (SDG 8.6.1)
*Youth Not in Education, Employment, or Training* (NEET) mengukur persentase generasi muda yang berada di luar sistem pendidikan formal, pasar tenaga kerja, maupun pelatihan vokasi.
- **BPS (`var1186`)**: Rentang data 2015–2025. Menggunakan populasi pemuda usia **15–24 tahun** bersumber dari Sakernas/Susenas.
- **ILOSTAT (`SDG_0861_SEX_RT`)**: Rentang data 2000–2023. Menggunakan batasan usia **15–24 tahun**. Tersedia disagregasi `SEX_T` (total), `SEX_M` (laki-laki), dan `SEX_F` (perempuan).
- **World Bank / WDI (`SL.UEM.NEET.ZS`)**: Rentang data 1996–2023. Menggunakan batasan usia **15–24 tahun**. Data bersumber dari estimasi model harmonisasi ILOSTAT.

**Kesimpulan Umur NEET:** Seluruh produsen data (BPS, ILO, dan WDI) memiliki **keselarasan penuh** pada kelompok umur acuan, yaitu **15–24 tahun**.

### B. Indikator Pekerja Anak (SDG 8.7.1)
Indikator ini mengukur proporsi anak-anak yang terjerumus dalam pekerjaan terlarang, membahayakan kesehatan/keselamatan, atau menghambat hak pendidikan dasar.
- **BPS (`var2658`)**: Rentang data 2020–2025 (seri pendek, 6 tahun). Mengacu pada batasan global anak usia **5–17 tahun**.
- **ILOSTAT Definisi A (`SDG_A871_SEX_AGE_RT`)**: Mengukur keterlibatan anak dalam aktivitas ekonomi berbahaya/melebihi jam kerja. Meskipun metadata standar SDG ILO mencakup rentang umur 5–17 tahun, **berkas amatan aktual di data raw hanya menyajikan observasi kelompok umur 15–17 tahun** (`AGE_CLDVERSION_Y15-17`). Hanya tersedia untuk tahun 2009, 2019, dan 2023.
- **ILOSTAT Definisi B (`SDG_B871_SEX_AGE_RT`)**: Memperluas Definisi A dengan memperhitungkan *hazardous unpaid household services* (pekerjaan rumah tangga ekstrem). Berkas amatan juga hanya menyajikan umur **15–17 tahun** dan hanya tersedia 1 tahun amatan (**2009**).
- **World Bank / WDI (`SL.TLF.0714.ZS`)**: Mengukur *Children in employment* khusus untuk kelompok umur **7–14 tahun**. Seri ini berhenti di tahun **2010** (tersedia 2000, 2009, dan 2010).

**Kesimpulan Umur & Definisi Pekerja Anak:** Terdapat **perbedaan cakupan umur dan definisi yang tajam**: BPS (5–17 tahun) vs ILO amatan (15–17 tahun) vs WDI (7–14 tahun). Kedua definisi ILO (A dan B) harus dipisahkan karena Definisi B memasukkan komponen pekerjaan domestik.

---

## 2. Matriks Daftar Pasangan Rekonsiliasi

Berikut adalah 5 pasangan rekonsiliasi yang diidentifikasi dari panduan kelompok Bagian 3:

| No | Pasangan Rekonsiliasi | Seri Utama (BPS) | Seri Pembanding | Kelompok Umur | Periode Acuan | Periode Pembanding | Irisan Tahun | Status Keterbandingan | Kategori Penjelasan Selisih |
|:---:|---|---|---|:---:|:---:|:---:|:---:|---|---|
| **1** | **NEET: BPS vs ILO** | `var1186` (total) | `SDG_0861_SEX_RT` (total) | 15–24 vs 15–24 | 2015–2025 | 2000–2023 | **2015–2023 (9 tahun)** | **Kandidat Utama** (Sangat Sebanding) | **Metode berbeda** (Survei langsung Susenas/Sakernas BPS vs estimasi model harmonisasi ILO) |
| **2** | **NEET: BPS vs WDI** | `var1186` (total) | `SL.UEM.NEET.ZS` (total) | 15–24 vs 15–24 | 2015–2025 | 1996–2023 | **2015–2023 (9 tahun)** | **Kandidat Utama** (Sangat Sebanding) | **Metode berbeda** (WDI mengadopsi data ILO secara identik) |
| **3** | **Pekerja Anak: BPS vs ILO Def A** | `var2658` (total) | `SDG_A871_SEX_AGE_RT` (15–17) | 5–17 vs 15–17 | 2020–2025 | 2009, 2019, 2023 | **2023 (1 tahun)** | **Kandidat Terbatas** (Hanya 1 titik irisan) | **Cakupan berbeda** (BPS mengukur 5–17 thn, ILO amatan hanya 15–17 thn) |
| **4** | **Pekerja Anak: BPS vs ILO Def B** | `var2658` (total) | `SDG_B871_SEX_AGE_RT` (15–17) | 5–17 vs 15–17 | 2020–2025 | 2009 | **0 tahun** (Tidak beririsan) | **Bukan Pasangan Sebanding** | **Definisi berbeda** (memperhitungkan pekerjaan domestik) & periode terputus |
| **5** | **Pekerja Anak: BPS vs WDI** | `var2658` (total) | `SL.TLF.0714.ZS` (total) | 5–17 vs 7–14 | 2020–2025 | 2000, 2009, 2010 | **0 tahun** (Tidak beririsan) | **Bukan Pasangan Sebanding** | **Cakupan berbeda** (umur 7–14 vs 5–17) & periode terputus 10 tahun (2010 ke 2020) |

---

## 3. Catatan Evaluasi Angka pada Periode Beririsan

Berdasarkan data tabel nasional periode $\times$ seri yang telah dihasilkan di `reports/tabel_nasional_periode_seri.csv`:

### A. Evaluasi Pemuda NEET (2015–2023)
| Tahun | BPS `var1186` (%) | ILO `SDG_0861` Total (%) | WDI `SL.UEM.NEET` (%) | Selisih (BPS - ILO) | Selisih (BPS - WDI) |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 2015 | 24.77 | 22.919 | 22.919 | +1.851 | +1.851 |
| 2016 | 23.19 | 22.479 | 22.479 | +0.711 | +0.711 |
| 2017 | 21.41 | 21.449 | 21.449 | -0.039 | -0.039 |
| 2018 | 22.15 | 21.738 | 21.738 | +0.412 | +0.412 |
| 2019 | 21.77 | 20.547 | 20.547 | +1.223 | +1.223 |
| 2020 | 24.28 | 21.800 | 21.800 | +2.480 | +2.480 |
| 2021 | 22.40 | 22.455 | 22.455 | -0.055 | -0.055 |
| 2022 | 23.22 | 22.336 | 22.336 | +0.884 | +0.884 |
| 2023 | 22.25 | 21.569 | 21.569 | +0.681 | +0.681 |

*Observasi Analitis:*
1. Angka WDI dan ILO bernilai **persis identik** pada 9 tahun irisan tersebut.
2. Selisih BPS dengan ILO/WDI bernilai rata-rata $+0.905$ poin persentase (median $+0.711$). Angka BPS cenderung sedikit lebih tinggi, yang mengindikasikan perbedaan perlakuan bobot Sakernas dan definisi status keaktifan pelatihan jangka pendek antara BPS dan pemodelan ILO.

### B. Evaluasi Pekerja Anak (Irisan Tunggal 2023)
| Tahun | BPS `var2658` (5–17 thn) | ILO Def A `SDG_A871` (15–17 thn) | Selisih (BPS - ILO) |
|:---:|:---:|:---:|:---:|
| 2023 | 1.530% | 1.567% | -0.037% |

*Observasi Analitis:*
Meskipun angkanya tampak sangat dekat (1.53% vs 1.57%), perbandingan ini harus disertai catatan kritis bahwa ILO hanya mengukur kelompok usia 15–17 tahun, sedangkan BPS mengukur seluruh anak usia 5–17 tahun. Keselarasan angka ini secara statistik bersifat semu (*coincidental*) karena penyebut populasi dan definisi operasionalnya berbeda.

---

## 4. Rekomendasi Pelaksanaan Integrasi pada Sprint 2
1. **Penyusunan Panel Gold**: Tabel rekonsiliasi formal pada Tahap 6 akan difokuskan secara kuantitatif pada Pasangan 1 (`var1186` vs ILO) dan Pasangan 2 (`var1186` vs WDI) pada 9 tahun irisan (2015–2023).
2. **Penjelasan Naratif**: Pasangan pekerja anak (Pasangan 3, 4, dan 5) akan dilaporkan dengan kategori selisih *cakupan* dan *definisi*, dilengkapi penjelasan ketiadaan irisan waktu (*missing unaligned*) untuk mencegah kesalahan interpretasi bahwa data tersebut hilang (*missing value*).
