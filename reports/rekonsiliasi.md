# Laporan Rekonsiliasi Seri Utama vs Pembanding Nasional (Tahap 6)

* **Penyusun:** Kaleb Filbert Istel (NIM: `124450053`)
* **Keluaran Parquet:** `data/gold/rekonsiliasi.parquet` (**80 baris** total across **5 pasangan**)
* **Tabel SQL DuckDB:** `gold_rekonsiliasi` pada `data/gold/capstone.duckdb` (`PRIMARY KEY (pasangan_id, periode, wilayah_kode)`)
* **Statistik Selisih (19 baris berpasangan):** median selisih = **`+0.711` poin persentase** (median absolut = `0.711` pp)

---

## 1. Ringkasan 5 Pasangan Rekonsiliasi (Panduan Kelompok Bagian 3)

Seluruh periode dari masing-masing seri utama dan pembanding digabung menggunakan *full outer join* sehingga periode tanpa pasangan tetap tampil (`selisih = NULL`, kategori `tidak_beririsan`), dan selisih angka tidak pernah dihapus ataupun dipaksa sama.

| ID | Pasangan & Kelompok Umur | Total Baris | Berpasangan (Irisan) | Tanpa Pasangan | Median Selisih (pp) |
|:---:|---|---:|---:|---:|---:|
| **P1** | `var1186` (15-24) vs `SDG_0861_SEX_RT` (15-24) | 26 | **9** (2015–2023) | 17 | +0.711 |
| **P2** | `var1186` (15-24) vs `SL.UEM.NEET.ZS` (15-24) | 30 | **9** (2015–2023) | 21 | +0.711 |
| **P3** | `var2658` (5-17) vs `SDG_A871_SEX_AGE_RT` (15-17) | 8 | **1** (2023) | 7 | -0.037 |
| **P4** | `var2658` (5-17) vs `SDG_B871_SEX_AGE_RT` (15-17) | 7 | **0** (Tidak ada (0 tahun)) | 7 | — |
| **P5** | `var2658` (5-17) vs `SL.TLF.0714.ZS` (7-14) | 9 | **0** (Tidak ada (0 tahun)) | 9 | — |

---

## 2. Tabel Selisih pada Seluruh Periode Beririsan (19 Baris)

| ID | Periode | Seri Utama | Seri Pembanding | Nilai Utama | Nilai Pembanding | Selisih (Utama - Pembanding) | Kategori Penjelasan | Ringkasan Bukti |
|:---:|:---:|---|---|---:|---:|---:|---|---|
| P1 | 2015 | `var1186` | `SDG_0861_SEX_RT` | 24.77% | 22.919% | **+1.851** | `metode berbeda` | Umur sama (15-24) dan keduanya bersumber Sakernas/LFS, namun ILOSTAT mengolah ulang mikrodata (NOTE_SOURCE: ILO-STATISTICS - Micro data processing) dengan harmonisasi definisi pelatihan/referensi serta pembaruan berbeda (BPS last_update 2026-02-24 vs snapshot ILO 2026-10-20). |
| P1 | 2016 | `var1186` | `SDG_0861_SEX_RT` | 23.19% | 22.479% | **+0.711** | `metode berbeda` | Umur sama (15-24) dan keduanya bersumber Sakernas/LFS, namun ILOSTAT mengolah ulang mikrodata (NOTE_SOURCE: ILO-STATISTICS - Micro data processing) dengan harmonisasi definisi pelatihan/referensi serta pembaruan berbeda (BPS last_update 2026-02-24 vs snapshot ILO 2026-10-20). |
| P1 | 2017 | `var1186` | `SDG_0861_SEX_RT` | 21.41% | 21.449% | **-0.039** | `metode berbeda` | Umur sama (15-24) dan keduanya bersumber Sakernas/LFS, namun ILOSTAT mengolah ulang mikrodata (NOTE_SOURCE: ILO-STATISTICS - Micro data processing) dengan harmonisasi definisi pelatihan/referensi serta pembaruan berbeda (BPS last_update 2026-02-24 vs snapshot ILO 2026-10-20). |
| P1 | 2018 | `var1186` | `SDG_0861_SEX_RT` | 22.15% | 21.738% | **+0.412** | `metode berbeda` | Umur sama (15-24) dan keduanya bersumber Sakernas/LFS, namun ILOSTAT mengolah ulang mikrodata (NOTE_SOURCE: ILO-STATISTICS - Micro data processing) dengan harmonisasi definisi pelatihan/referensi serta pembaruan berbeda (BPS last_update 2026-02-24 vs snapshot ILO 2026-10-20). |
| P1 | 2019 | `var1186` | `SDG_0861_SEX_RT` | 21.77% | 20.547% | **+1.223** | `metode berbeda` | Umur sama (15-24) dan keduanya bersumber Sakernas/LFS, namun ILOSTAT mengolah ulang mikrodata (NOTE_SOURCE: ILO-STATISTICS - Micro data processing) dengan harmonisasi definisi pelatihan/referensi serta pembaruan berbeda (BPS last_update 2026-02-24 vs snapshot ILO 2026-10-20). |
| P1 | 2020 | `var1186` | `SDG_0861_SEX_RT` | 24.28% | 21.800% | **+2.480** | `belum terjelaskan` | Dugaan: lonjakan selisih ekstrem (+2. |
| P1 | 2021 | `var1186` | `SDG_0861_SEX_RT` | 22.40% | 22.455% | **-0.055** | `metode berbeda` | Umur sama (15-24), selisih -0. |
| P1 | 2022 | `var1186` | `SDG_0861_SEX_RT` | 23.22% | 22.336% | **+0.884** | `metode berbeda` | Umur sama (15-24) dan keduanya bersumber Sakernas/LFS, namun ILOSTAT mengolah ulang mikrodata (NOTE_SOURCE: ILO-STATISTICS - Micro data processing) dengan harmonisasi definisi pelatihan/referensi serta pembaruan berbeda (BPS last_update 2026-02-24 vs snapshot ILO 2026-10-20). |
| P1 | 2023 | `var1186` | `SDG_0861_SEX_RT` | 22.25% | 21.569% | **+0.681** | `metode berbeda` | Umur sama (15-24) dan keduanya bersumber Sakernas/LFS, namun ILOSTAT mengolah ulang mikrodata (NOTE_SOURCE: ILO-STATISTICS - Micro data processing) dengan harmonisasi definisi pelatihan/referensi serta pembaruan berbeda (BPS last_update 2026-02-24 vs snapshot ILO 2026-10-20). |
| P2 | 2015 | `var1186` | `SL.UEM.NEET.ZS` | 24.77% | 22.919% | **+1.851** | `metode berbeda` | Umur sama (15-24). |
| P2 | 2016 | `var1186` | `SL.UEM.NEET.ZS` | 23.19% | 22.479% | **+0.711** | `metode berbeda` | Umur sama (15-24). |
| P2 | 2017 | `var1186` | `SL.UEM.NEET.ZS` | 21.41% | 21.449% | **-0.039** | `metode berbeda` | Umur sama (15-24). |
| P2 | 2018 | `var1186` | `SL.UEM.NEET.ZS` | 22.15% | 21.738% | **+0.412** | `metode berbeda` | Umur sama (15-24). |
| P2 | 2019 | `var1186` | `SL.UEM.NEET.ZS` | 21.77% | 20.547% | **+1.223** | `metode berbeda` | Umur sama (15-24). |
| P2 | 2020 | `var1186` | `SL.UEM.NEET.ZS` | 24.28% | 21.800% | **+2.480** | `belum terjelaskan` | Dugaan: mewarisi gap ekstrem (+2. |
| P2 | 2021 | `var1186` | `SL.UEM.NEET.ZS` | 22.40% | 22.455% | **-0.055** | `metode berbeda` | Umur sama (15-24), selisih -0. |
| P2 | 2022 | `var1186` | `SL.UEM.NEET.ZS` | 23.22% | 22.336% | **+0.884** | `metode berbeda` | Umur sama (15-24). |
| P2 | 2023 | `var1186` | `SL.UEM.NEET.ZS` | 22.25% | 21.569% | **+0.681** | `metode berbeda` | Umur sama (15-24). |
| P3 | 2023 | `var2658` | `SDG_A871_SEX_AGE_RT` | 1.53% | 1.567% | **-0.037** | `cakupan berbeda` | Meskipun DSD SDG_A871_SEX_AGE_RT. |

---

## 3. Penjelasan Khusus Kategori `belum terjelaskan` (Dugaan & Bukti yang Dicari)

- **`P1` (2020, `var1186` vs `SDG_0861_SEX_RT`, selisih `+2.480` pp):** Dugaan: lonjakan selisih ekstrem (+2.480 poin, 24.28% vs 21.800%) dipicu penyesuaian metode wawancara telepon/klasifikasi pelatihan Sakernas saat awal pandemi COVID-19 sebelum revisi seri dicatat. Bukti dicari: kolom OBS_STATUS dan NOTE_INDICATOR di DF_SDG_0861_SEX_RT.csv bernilai kosong (NaN) pada 2020, sedangkan def/note di sdg8_neet.json BPS hanya mencantumkan 'Sumber: Sakernas, BPS'.
- **`P2` (2020, `var1186` vs `SL.UEM.NEET.ZS`, selisih `+2.480` pp):** Dugaan: mewarisi gap ekstrem (+2.480 poin) dari pemrosesan mikrodata LFS Sakernas 2020 akibat perubahan perlakuan wawancara/pelatihan era pandemi COVID-19. Bukti dicari: metadata WDI sumber2_indikator.json menunjuk ILOSTAT tanpa catatan tahunan 2020, DF_SDG_0861_SEX_RT.csv kosong di OBS_STATUS 2020, dan sdg8_neet.json BPS tidak memuat rincian metodologi tahunan.

---

## 4. Catatan Pasangan Pekerja Anak Tanpa Irisan & Perubahan Definisi (`P3`, `P4`, `P5`)

1. **`P3` (`var2658` vs `SDG_A871_SEX_AGE_RT`):** Hanya beririsan 1 tahun (**2023**: `1.530%` vs `1.567%`, selisih `-0.037` pp). Dikategorikan **`cakupan berbeda`** karena meski DSD menyebut kerangka 5–17 tahun, data aktual Indonesia di `DF_SDG_A871_SEX_AGE_RT.csv` hanya memuat kode dimensi `AGE_CLDVERSION_Y15-17` (**15–17 tahun**), bukan 5–17 tahun seperti BPS `var2658`. Selain itu, tahun 2009 pada seri ILO bersumber survei `CLS` sedangkan 2019 dan 2023 bersumber `LFS`.
2. **`P4` (`var2658` vs `SDG_B871_SEX_AGE_RT`):** Memiliki **0 tahun tumpang tindih** (`2009` di ILO vs `2020–2025` di BPS). DSD `SDG_B871_SEX_AGE_RT.json` memperluas definisi dengan memasukkan pekerjaan rumah tangga (≥ 21 jam/minggu; **`definisi berbeda`**). Pada tahun 2009 (`4.527%`, `CLS`), angkanya identik dengan `SDG_A871_SEX_AGE_RT` karena ambang umur 15–17 hanya menghitung aktivitas ekonomi ≥ 43 jam.
3. **`P5` (`var2658` vs `SL.TLF.0714.ZS`):** Memiliki **0 tahun tumpang tindih** karena WDI `SL.TLF.0714.ZS` (bersumber *Understanding Children's Work*, umur **7–14 tahun**) berhenti pada tahun **2010** (`2000, 2009, 2010`), sehingga terpisah jeda 10 tahun dari seri BPS `var2658` (`2020–2025`, umur **5–17 tahun**) dan tergolong **`cakupan berbeda`** jika dibandingkan lintas periode.
