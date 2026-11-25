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

### Contoh penelusuran lineage baris Silver ke berkas mentah

Setiap baris pada data/silver/silver.parquet dapat ditelusuri kembali ke berkas mentah dan diverifikasi integritasnya lewat _berkas_raw dan _sha256_raw terhadap data/raw/MANIFEST.csv:

1. **Baris contoh data/silver/silver.parquet (indeks 0):** sumber=bps, seri_kode=var1186, wilayah_kode=1100 (ACEH), periode=2015 (tahun), rincian=total, nilai=25.65 (persen), _berkas_raw=bps/2026-10-17/sdg8_neet.csv, _sha256_raw=b35a8ea5b7d3e043f8f0ccd5afbbd8ed9276397f068efc8fe72fea360d72e4d5.
2. **Verifikasi berkas mentah:** Berkas berada di data/raw/bps/2026-10-17/sdg8_neet.csv dengan entri MANIFEST.csv (bait=25558, sha256=b35a8ea5b7d3e043f8f0ccd5afbbd8ed9276397f068efc8fe72fea360d72e4d5). Pemetaan wilayah ACEH -> 1100 mengikuti K-001, satuan persen mengikuti K-003, dan rincian=total mengikuti K-004.

## data/gold/panel.parquet

Total baris: 646 sel (`418` sel `var1186` 2015–2025 + `228` sel `var2658` 2020–2025) | Kunci unik: `[wilayah_kode, periode, seri_kode]` | Keluaran modul `src/gold/aturan_gold.py` via `pipeline.py`.

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|
| `seri_kode` | string (object) | — | tidak | `var1186`, `var2658` | K-019, `SERI_PANEL_UTAMA` | Kode seri utama tingkat provinsi |
| `indikator` | string (object) | — | tidak | `neet_15_24`, `pekerja_anak_5_17` | Pemetaan baku `INDIKATOR_LABEL` | Nama indikator analitis |
| `wilayah_kode` | int64 | kode BPS x 100 | tidak | `1100`–`9700` (38 provinsi) | K-001, K-019 | Kode provinsi 2 digit BPS $\times$ 100 (tanpa `9999`) |
| `nama_wilayah` | string (object) | — | tidak | 38 nama provinsi BPS | Silver (`var1186` 2025) | Nama resmi provinsi sesuai susunan 2025 |
| `periode` | string (object) | YYYY (`^\d{4}$`) | tidak | `2015`–`2025` (`var1186`), `2020`–`2025` (`var2658`) | K-018, `tangani_periode_subtahunan` | Tahun pengamatan |
| `sumber` | string (object) | — | tidak | `bps` | K-019 | Sumber seri utama provinsi |
| `rincian` | string (object) | — | tidak | `total` | K-019 | Agregat populasi sebanding yang masuk panel |
| `nilai` | float64 | persen (0–100) | ya (bila `status_data != 'tersedia'`) | `0.38` s.d. `35.38` (588 sel terisi, 58 kosong) | Silver terdeduplikasi (K-017) | Nilai indikator; tidak diubah/dihapus walau bertanda anomali |
| `satuan` | string (object) | — | tidak | `persen` | K-003 | Satuan indikator baku |
| `status_wilayah` | string (object) | kategori | tidak | `eligible`, `belum_terbentuk`, `masa_transisi` | K-006, K-020 | Eligibilitas administratif 4 DOB Papua (`9200, 9500, 9600, 9700`) |
| `status_data` | string (object) | kategori | tidak | `tersedia` (588), `belum_terbentuk` (36), `masa_transisi` (8), `missing` (14) | K-006, K-020 | Status ketersediaan nilai per sel panel |
| `penanda_anomali` | string (object) | kategori | ya (bila `status_data != 'tersedia'`) | `normal` (559), `outlier_asli` (23), `patahan_diduga` (6) | K-007, K-020, `reports/kategori_anomali.csv` | Penanda anomali Sprint 1 yang ikut terbawa ke Gold |
| `arah_serentak_tahun` | string (object) | kategori | ya (tahun pertama seri) | `naik`, `turun`, `tidak serentak` | `reports/tahun_serentak.csv` | Arah pergerakan serentak ($\ge 80\%$ wilayah) pada tahun terkait |
| `catatan_anomali` | string (object) | teks | ya (bila `normal` atau sel kosong) | Deskripsi alasan 29 kandidat anomali | `reports/kategori_anomali.csv` | Penjelasan klasifikasi `outlier_asli` / `patahan_diduga` |
| `snapshot_tanggal` | string (object) | YYYY-MM-DD | ya (bila `status_data != 'tersedia'`) | `2026-10-17` | K-017, ekstrak dari `_berkas_raw` | Tanggal snapshot sumber terpilih |
| `_berkas_raw` | string (object) | path relatif | ya (bila `status_data != 'tersedia'`) | `bps/2026-10-17/sdg8_neet.csv`, `bps/2026-10-17/sdg8_8_7_1_v2658.csv` | K-017, lineage Silver | Berkas sumber terpilih setelah aturan snapshot & format |
| `_sha256_raw` | string (object) | heksadesimal 64-karakter | ya (bila `status_data != 'tersedia'`) | 2 hash SHA-256 berkas CSV BPS di `MANIFEST.csv` | Lineage Silver | Sidik integritas berkas mentah asal sel |

## data/gold/tabel_nasional.parquet

Total baris: 30 periode (`1996`–`2025`) $\times$ 14 kolom (`periode` + 13 seri/rincian nasional BPS, ILOSTAT, dan WDI) | Kunci unik: `[periode]` | Keluaran `src/gold/tabel_nasional.py` yang memakai `pilih_snapshot` dan `tangani_periode_subtahunan`. Kedua definisi pekerja anak ILO (`SDG_A871_SEX_AGE_RT` dan `SDG_B871_SEX_AGE_RT`) disimpan sebagai kolom/seri terpisah.

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

