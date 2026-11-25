# Laporan Validasi Otomatis — Kelompok 13

## Ringkasan Validasi Silver (Sprint 1)

- **Status:** LOLOS (16/16 aturan)
- **Total baris tervalidasi:** 1325 baris
- **Library:** Pandera (`src/validasi/validasi_silver.py`)

### Daftar Aturan Dasar yang Diuji

1. **Kelengkapan & tipe 11 kolom wajib Silver:** `sumber`, `seri_kode`, `wilayah_kode`, `nama_wilayah`, `periode`, `jenis_periode`, `rincian`, `nilai`, `satuan`, `_berkas_raw`, `_sha256_raw`.
2. **Rentang nilai masuk akal:** Seluruh nilai bersatuan `persen` berada pada rentang `0` hingga `100` (aktual: `0.38` s.d. `41.23`).
3. **Keunikan kunci komposit:** Kombinasi `[sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw]` unik tanpa duplikat.
4. **Konsistensi satuan & rincian:** Setiap `seri_kode` memiliki tepat satu satuan (`persen`), seluruh 7 seri Kasus 13 hadir lengkap, dan nilai `rincian` sesuai dengan daftar pada `docs/data-dictionary.md`.
5. **Integritas wilayah & lineage:** `wilayah_kode` hanya berisi kode 38 provinsi BPS (`1100`–`9700`) atau `9999` (Indonesia), dan setiap baris memiliki `_berkas_raw` serta `_sha256_raw` (SHA-256 64 karakter heksadesimal).

*(Validasi tabel Gold dan penelusuran lineage baris Gold ke `_berkas_raw` akan ditambahkan pada Sprint 2–3 setelah panel Gold terbentuk.)*

## Ringkasan Validasi Gold & Rekonsiliasi (Sprint 2)

- **Status:** LOLOS (4/4 aturan)
- **Total sel panel Gold:** 646 sel (588 terisi, 58 kosong struktural)
- **Total baris rekonsiliasi (`tabel_nasional.parquet`):** 76 baris
- **Skrip:** `src/validasi/validasi_gold.py` (dipanggil otomatis oleh `pipeline.py` melalui `validasi.jalankan(silver, gold)`)

### Daftar Aturan Gold & Rekonsiliasi yang Diuji

1. **Kunci panel unik:** LOLOS — 0 duplikat pada ['seri_kode', 'wilayah_kode', 'periode', 'rincian'].
2. **Satuan satu per indikator:** LOLOS — Setiap indikator memiliki tepat 1 satuan.
3. **Setiap sel Gold punya pasangan di Silver:** LOLOS — 588/588 sel terisi cocok dengan Silver.
4. **Setiap baris rekonsiliasi punya kategori:** LOLOS — 76/76 baris memiliki kategori lengkap (topik, peran_seri, asal_angka).
