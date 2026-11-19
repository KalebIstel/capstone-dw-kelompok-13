# Data dictionary — A3K (Kelompok 13)

Satu tabel per keluaran (Silver dan setiap tabel Gold). Isi dari data nyata, bukan dari ingatan:
tipe, satuan, rentang, dan jumlah kosong dihitung ulang setiap kali pipeline berjalan.

## data/silver/silver.parquet

Total baris: 1.325 baris | Kunci komposit: `[sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw]`

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|
| `sumber` | string (object) | — | tidak | `bps`, `wdi`, `ilostat` | Direktori `data/raw/<sumber>/` | Nama produsen/sumber data mentah |
| `seri_kode` | string (object) | — | tidak | `var1186`, `var2658`, `SL.TLF.0714.ZS`, `SL.UEM.NEET.ZS`, `SDG_0861_SEX_RT`, `SDG_A871_SEX_AGE_RT`, `SDG_B871_SEX_AGE_RT` | `data/KASUS.md`, metadata mentah | Kode unik seri indikator dari katalog sumber |
| `wilayah_kode` | int64 | kode BPS x 100 / 9999 | tidak | `1100`–`9700`, `9999` | Standar BPS 38 provinsi & K-001 | Kode wilayah numerik (9999 = Nasional Indonesia, provinsi = 2 digit BPS x 100) |
| `nama_wilayah` | string (object) | — | tidak | 38 nama provinsi BPS (mis. `ACEH`, `PAPUA`, dll.) dan `INDONESIA` | Berkas mentah BPS / standar nasional | Nama administratif wilayah observasi |
| `periode` | string (object) | YYYY (`^\d{4}$`) | tidak | `1996` s.d. `2025` | Kolom tahun sumber | Periode pengamatan tahunan |
| `jenis_periode` | string (object) | kategori waktu | tidak | `tahun` | Aturan baku skema Silver | Seluruh indikator kasus 13 merupakan pengamatan tahunan |
| `rincian` | string (object) | string label | tidak | `total`, `laki-laki`, `perempuan`, `15-17`, `laki-laki_15-17`, `perempuan_15-17` | K-004, dimensi `turvar` BPS & `SEX`/`AGE` ILOSTAT | Rincian kategori demografi pengamatan |
| `nilai` | float64 | persen (0–100) | tidak | `0.38` s.d. `41.23` | Kolom nilai/datacontent/OBS_VALUE sumber | Nilai observasi numerik riil |
| `satuan` | string (object) | — | tidak | `persen` | K-003, metadata BPS/WDI/ILOSTAT | Satuan baku indikator yang telah diseragamkan |
| `_berkas_raw` | string (object) | path relatif | tidak | 8 berkas nilai di `data/raw/` | Lineage berkas mentah | Jalur relatif berkas sumber terhadap `data/raw/` |
| `_sha256_raw` | string (object) | heksadesimal 64-karakter | tidak | 8 sidik SHA-256 yang sah di `MANIFEST.csv` | `src.common.manifest.sha256_raw` | Sidik integritas berkas mentah asal observasi |

## data/gold/<tabel>.parquet

*(Akan dilengkapi pada Sprint 2 setelah panel Gold dan tabel rekonsiliasi terbentuk)*

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|

## Laporan grid panel dan kelengkapan provinsi

Bagian ini mendokumentasikan laporan analisis panel untuk dua seri BPS pada kasus 13. Laporan disimpan sebagai CSV di folder `reports/`, bukan sebagai tabel Gold.

### Sumber dan cakupan

| Seri | Indikator | Berkas sumber | Rentang tahun |
|---|---|---|---|
| `var1186` | NEET | `sdg8_neet.csv` | 2015–2025 |
| `var2658` | Pekerja anak | `sdg8_8_7_1_v2658.csv` | 2020–2025 |

### Aturan pembentukan grid

1. Baris nasional dengan `wilayah` bernilai `INDONESIA` dipisahkan dan tidak dimasukkan ke panel provinsi.
2. Grid dibentuk dari kombinasi setiap tahun pengamatan pada masing-masing seri dengan daftar acuan 38 provinsi.
3. Empat provinsi baru di Papua yang diperiksa dalam aturan ini adalah `PAPUA BARAT DAYA`, `PAPUA PEGUNUNGAN`, `PAPUA SELATAN`, dan `PAPUA TENGAH`.
4. Untuk keperluan analisis panel, empat provinsi tersebut diberi status `belum_terbentuk` sebelum 2022, `masa_transisi` pada 2022, dan `eligible` mulai 2023. Ini adalah asumsi operasional yang dicatat pada K-002, bukan pernyataan bahwa data pengamatan tersedia pada tahun pembentukan administratifnya.
5. Provinsi lain berstatus `eligible` pada seluruh tahun dalam rentang seri.
6. Baris berstatus `eligible` yang tidak memiliki nilai pengamatan diberi `status_data=missing`. Baris dengan nilai diberi `status_data=tersedia`.
7. Status `belum_terbentuk` dan `masa_transisi` tidak dihitung sebagai missing dan tidak masuk penyebut perhitungan persentase kelengkapan.
8. Persentase terisi dihitung sebagai `jumlah_terisi / jumlah_provinsi_eligible * 100`.

### Struktur berkas laporan

#### `reports/grid_panel_var1186.csv` dan `reports/grid_panel_var2658.csv`

Satu baris merepresentasikan satu kombinasi seri, tahun, dan provinsi dalam grid.

| Kolom | Tipe/format | Keterangan |
|---|---|---|
| `seri` | string | Kode seri, yaitu `var1186` atau `var2658` |
| `tahun` | integer | Tahun pengamatan |
| `wilayah` | string | Nama provinsi |
| `nilai` | numerik | Nilai indikator dari data sumber; kosong jika tidak tersedia pada kombinasi tahun-provinsi |
| `status_wilayah` | kategori | `eligible`, `belum_terbentuk`, atau `masa_transisi` |
| `status_data` | kategori | `tersedia`, `missing`, `belum_terbentuk`, atau `masa_transisi` |

#### `reports/kelengkapan_panel_per_tahun.csv`

Satu baris merepresentasikan satu seri pada satu tahun pengamatan.

| Kolom | Tipe/format | Keterangan |
|---|---|---|
| `seri` | string | Kode seri indikator |
| `tahun` | integer | Tahun pengamatan |
| `jumlah_provinsi_eligible` | integer | Jumlah provinsi yang masuk penyebut kelengkapan |
| `jumlah_terisi` | integer | Jumlah provinsi eligible yang memiliki nilai |
| `jumlah_missing` | integer | Jumlah provinsi eligible tanpa nilai |
| `persen_terisi` | numerik, persen | Persentase provinsi eligible yang memiliki nilai, dibulatkan dua angka desimal |

### Hasil pemeriksaan saat laporan dibuat

| Seri | Tahun | Eligible | Terisi | Missing | Terisi (%) |
|---|---:|---:|---:|---:|---:|
| `var1186` | 2015–2022 | 34 per tahun | 34 per tahun | 0 per tahun | 100,00 |
| `var1186` | 2023 | 38 | 34 | 4 | 89,47 |
| `var1186` | 2024–2025 | 38 per tahun | 38 per tahun | 0 per tahun | 100,00 |
| `var2658` | 2020–2022 | 34 per tahun | 34 per tahun | 0 per tahun | 100,00 |
| `var2658` | 2023 | 38 | 34 | 4 | 89,47 |
| `var2658` | 2024 | 38 | 36 | 2 | 94,74 |
| `var2658` | 2025 | 38 | 34 | 4 | 89,47 |

Angka pada tabel ini merupakan hasil pemeriksaan ketika laporan dibuat. Jalankan kembali `python buat_grid_panel.py` setelah data sumber berubah agar laporan diperbarui.

### Skrip pembentuk laporan

Skrip `buat_grid_panel.py` membentuk kedua grid panel dan ringkasan kelengkapan berdasarkan berkas sumber di `data/raw/bps/2026-10-17/`. Skrip memeriksa bahwa daftar acuan berisi 38 provinsi dan menggunakan validasi satu-ke-satu pada penggabungan data sumber ke grid.

## Metadata seri: satuan, periode, kelompok umur, kode SDG

| Seri | Satuan | Periode | Kelompok umur | Kode SDG | Bukti |
|---|---|---|---|---|---|
| var1186 | persen | tahun | 15-24 | 8.6.1 | judul tabel BPS (manifest_asal.json) |
| var2658 | persen | tahun | 5-17 | 8.7.1 | judul tabel BPS (manifest_asal.json) |
| SDG_0861_SEX_RT | persen | tahun | 15-24 | 8.6.1 | DSD ILO; OBS_STATUS=B (patahan seri) |
| SDG_A871_SEX_AGE_RT | persen | tahun | 15-17 | 8.7.1 | DSD ILO (aktivitas ekonomi) |
| SDG_B871_SEX_AGE_RT | persen | tahun | 15-17 | 8.7.1 | DSD ILO (aktivitas ekonomi + pekerjaan rumah tangga) |
| SL.UEM.NEET.ZS | persen | tahun | 15-24 | - | metadata WDI |
| SL.TLF.0714.ZS | persen | tahun | 7-14 | - | metadata WDI |

Catatan: kelompok umur berbeda antar sumber, sehingga pasangan rekonsiliasi pekerja anak
dikategorikan "definisi", bukan selisih biasa.

