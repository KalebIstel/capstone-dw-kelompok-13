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

Total baris: 76 baris teramati (30 periode `1996`–`2025` $\times$ 7 seri Kasus 13) | Kunci unik: `[periode, seri_kode]` | Keluaran `src/gold/tabel_nasional.py` via `pipeline.py`. Menyandingkan seri utama BPS (`var1186`, `var2658`) dengan seri pembanding ILOSTAT (`SDG_0861_SEX_RT`, `SDG_A871_SEX_AGE_RT`, `SDG_B871_SEX_AGE_RT`) dan WDI (`SL.UEM.NEET.ZS`, `SL.TLF.0714.ZS`) dengan kedua definisi pekerja anak ILO tetap dipisah, dilengkapi asal angka (`asal_angka`) serta lineage `_berkas_raw` dan `_sha256_raw` di setiap baris.

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|
| `periode` | string (object) | YYYY (`^\d{4}$`) | tidak | `1996` s.d. `2025` (30 tahun) | K-018, `tangani_periode_subtahunan` | Tahun pengamatan nasional |
| `seri_kode` | string (object) | — | tidak | 7 seri Kasus 13 (`var1186`, `var2658`, `SDG_0861_SEX_RT`, `SDG_A871_SEX_AGE_RT`, `SDG_B871_SEX_AGE_RT`, `SL.UEM.NEET.ZS`, `SL.TLF.0714.ZS`) | `METADATA_SERI_NASIONAL` | Kode seri indikator |
| `topik` | string (object) | kategori | tidak | `neet`, `pekerja_anak` | `METADATA_SERI_NASIONAL` | Pengelompokan topik untuk penyandingan seri utama vs pembanding |
| `indikator` | string (object) | kategori | tidak | `neet_15_24`, `pekerja_anak_5_17`, `pekerja_anak_15_17`, `pekerja_anak_7_14` | `METADATA_SERI_NASIONAL` | Label analitis indikator beserta cakupan umur |
| `peran_seri` | string (object) | kategori | tidak | `utama` (17 baris), `pembanding` (59 baris) | `METADATA_SERI_NASIONAL` | Peran seri dalam rekonsiliasi Tahap 6 |
| `asal_angka` | string (object) | kategori | tidak | `baris_indonesia` (17 baris), `pembanding` (59 baris); mendukung `agregat_provinsi` | K-023 | Asal angka nasional per baris; seri utama Kasus 13 memakai baris Indonesia eksplisit (`9999`) |
| `sumber` | string (object) | — | tidak | `bps`, `ilostat`, `wdi` | Silver (`wilayah_kode=9999`) | Produsen data sumber |
| `wilayah_kode` | int64 | kode nasional | tidak | `9999` | K-001 | Kode wilayah nasional Indonesia |
| `nama_wilayah` | string (object) | — | tidak | `INDONESIA` | Silver (`wilayah_kode=9999`) | Nama wilayah nasional |
| `rincian` | string (object) | kategori | tidak | `total` (`var1186`, `var2658`, `SDG_0861_SEX_RT`, `SL.UEM.NEET.ZS`, `SL.TLF.0714.ZS`), `15-17` (`SDG_A871_SEX_AGE_RT`, `SDG_B871_SEX_AGE_RT`) | K-022 | Rincian agregat nasional sebanding agar unik 1 baris per `periode x seri` |
| `kelompok_umur` | string (object) | rentang usia | tidak | `15-24`, `5-17`, `15-17`, `7-14` | K-011, `METADATA_SERI_NASIONAL` | Cakupan kelompok umur resmi tiap seri |
| `nilai` | float64 | persen (0–100) | tidak | `1.53` s.d. `31.86` | Silver terdeduplikasi (K-017) | Nilai observasi nasional riil |
| `satuan` | string (object) | — | tidak | `persen` | K-003, K-021 | Satuan baku seragam |
| `snapshot_tanggal` | string (object) | YYYY-MM-DD | tidak | `2026-10-17`, `2026-10-20` | K-017, ekstrak dari `_berkas_raw` | Tanggal snapshot berkas sumber terpilih |
| `_berkas_raw` | string (object) | path relatif | tidak | 6 berkas nilai nasional di `data/raw/` | K-017, K-022, lineage Silver | Berkas sumber terpilih pada setiap baris |
| `_sha256_raw` | string (object) | heksadesimal 64-karakter | tidak | 6 hash SHA-256 sah di `MANIFEST.csv` | Lineage Silver | Sidik integritas berkas mentah asal baris |

*(Laporan pivot lebar `30 periode` $\times$ `14 kolom` beserta rincian gender ILOSTAT tetap dihasilkan di `reports/tabel_nasional_periode_seri.csv` untuk inspeksi manusia dan rujukan `reports/daftar_pasangan_rekonsiliasi.md`.)*

## data/gold/rekonsiliasi.parquet

Total baris: 80 baris (**5 pasangan** $\times$ gabungan penuh periode: **19 baris berpasangan** + **61 baris tanpa pasangan** tetap tampil) | Kunci unik: `[pasangan_id, periode, wilayah_kode]` | Keluaran `src/gold/rekonsiliasi.py` via `pipeline.py`.

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|
| `pasangan_id` | string (object) | kode pasangan | tidak | `P1` s.d. `P5` | `PASANGAN_REKONSILIASI` | Pengenal 5 pasangan seri utama vs pembanding |
| `topik` | string (object) | kategori | tidak | `neet`, `pekerja_anak` | `METADATA_SERI_NASIONAL` | Topik indikator pasangan |
| `wilayah_kode` | int64 | kode nasional | tidak | `9999` | K-001 | Kode wilayah nasional Indonesia |
| `periode` | string (object) | YYYY (`^\d{4}$`) | tidak | `1996` s.d. `2025` | Outer join `periode` `tabel_nasional` | Tahun pengamatan (beririsan & tanpa pasangan) |
| `seri_utama` | string (object) | kode seri BPS | tidak | `var1186`, `var2658` | K-025 | Kode seri utama nasional |
| `seri_pembanding` | string (object) | kode seri global | tidak | `SDG_0861_SEX_RT`, `SL.UEM.NEET.ZS`, `SDG_A871_SEX_AGE_RT`, `SDG_B871_SEX_AGE_RT`, `SL.TLF.0714.ZS` | K-025 | Kode seri pembanding ILOSTAT / WDI |
| `nilai_utama` | float64 | persen (0–100) | ya (bila tanpa pasangan utama) | `1.53` s.d. `24.77` | `tabel_nasional.parquet` | Nilai seri utama BPS |
| `nilai_pembanding` | float64 | persen (0–100) | ya (bila tanpa pasangan pembanding) | `1.567` s.d. `31.86` | `tabel_nasional.parquet` | Nilai seri pembanding ILOSTAT / WDI |
| `selisih` | float64 | poin persentase | ya (bila tanpa pasangan) | `-0.055` s.d. `+2.480` (median `+0.711`) | `nilai_utama - nilai_pembanding` | Selisih tanpa dihapus/dipaksa sama |
| `kategori_selisih` | string (object) | kategori | tidak | `metode berbeda`, `cakupan berbeda`, `belum terjelaskan`, `definisi berbeda`, `vintage berbeda`, `tidak_beririsan` | K-025, `src/gold/rekonsiliasi.py` | Kategori penjelasan selisih atau status tanpa irisan |
| `penjelasan` | string (object) | teks | tidak | Penjelasan bukti metadata, dugaan, dan ketiadaan irisan | Audit raw BPS/ILO/WDI | Bukti empiris DSD, `SOURCE`, `OBS_STATUS`, & metadata |
| `kelompok_umur_utama` | string (object) | rentang usia | tidak | `15-24`, `5-17` | K-011 | Cakupan umur seri utama |
| `kelompok_umur_pembanding` | string (object) | rentang usia | tidak | `15-24`, `15-17`, `7-14` | K-011, audit empiris `AGE` | Cakupan umur aktual seri pembanding |
| `_berkas_raw_utama` | string (object) | path relatif | ya (bila tanpa nilai utama) | Berkas CSV BPS di `data/raw/` | Lineage `tabel_nasional` | Sumber berkas mentah seri utama |
| `_berkas_raw_pembanding` | string (object) | path relatif | ya (bila tanpa nilai pembanding) | Berkas ILOSTAT/WDI di `data/raw/` | Lineage `tabel_nasional` | Sumber berkas mentah seri pembanding |
| `_sha256_raw_utama` | string (object) | heksadesimal 64-karakter | ya (bila tanpa nilai utama) | Hash SHA-256 `MANIFEST.csv` | Lineage `tabel_nasional` | Sidik integritas sumber utama |
| `_sha256_raw_pembanding` | string (object) | heksadesimal 64-karakter | ya (bila tanpa nilai pembanding) | Hash SHA-256 `MANIFEST.csv` | Lineage `tabel_nasional` | Sidik integritas sumber pembanding |

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

## Basis data relasional SQL (`data/gold/capstone.duckdb`)

Dibentuk otomatis oleh `python pipeline.py` melalui `src/gold/muat_sql.py` menggunakan DDL berkunci primer di `src/gold/skema.sql` (dikecualikan dari Git lewat `*.duckdb` pada `.gitignore`, lihat keputusan `K-024` dan `reports/basis-data.md`).

| Nama Tabel | Sumber Parquet | Kunci Primer (`PRIMARY KEY`) | Jumlah Baris | Keterangan |
|---|---|---|---:|---|
| `silver` | `data/silver/silver.parquet` | `(sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw)` | 1.325 | Tabel panjang Silver lengkap ber-lineage |
| `gold_panel` | `data/gold/panel.parquet` | `(wilayah_kode, periode, seri_kode)` | 646 | Panel provinsi $\times$ tahun $\times$ indikator BPS dengan status sel kosong & penanda anomali |
| `gold_tabel_nasional` | `data/gold/tabel_nasional.parquet` | `(periode, seri_kode)` | 76 | Tabel nasional seri utama BPS vs pembanding ILO/WDI dengan `asal_angka` & lineage |
| `gold_rekonsiliasi` | `data/gold/rekonsiliasi.parquet` | `(pasangan_id, periode, wilayah_kode)` | 80 | Tabel rekonsiliasi 5 pasangan seri utama vs pembanding nasional & kategori selisih |

