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
