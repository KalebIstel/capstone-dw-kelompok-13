# AI_LOG — A3K (Kelompok 13)

Satu baris per pemakaian AI yang bermakna (ChatGPT, Claude, Copilot, Bravais, dan sejenisnya).
Ringkas dan jujur; transkrip penuh tidak diminta. Yang dinilai bukan "pakai AI atau tidak",
melainkan "mengerti atau tidak" — isi kolom terakhir dengan apa yang Anda ubah dari keluarannya.

| Tanggal | Siapa (NIM) | Alat | Untuk apa | Apa yang diubah dari keluarannya |
|---|---|---|---|---|
| 2026-11-19 | 124450053 | Gemini | Penyusunan modul transformasi Silver (Tahap 4) | Menyesuaikan logika pemetaan rincian ILOSTAT (SEX_T dan kelompok umur 15-17), memvalidasi filter nilai null WDI, dan memeriksa kepatuhan skema terhadap src.common.skema |
| 2026-11-25 | 124450028 | Gemini | Penyusunan modul aturan satu nilai per sel Gold (`src/gold/aturan_gold.py`) dan uji unit | Menetapkan prioritas format CSV pada tanggal snapshot sama, aturan periode sub-tahunan berbasis periode akhir tanpa rata-rata sintetis, serta memverifikasi pewarisan penuh 29 penanda anomali Sprint 1 ke `data/gold/panel.parquet` |
| 2026-11-25 | 124450028 | Gemini | Pengawalan satuan, verifikasi ketertelusuran Silver, dan pembaruan metrik panel Gold (Kartu #21) | Menambahkan guard anti-campuran satuan (`seragamkan_satuan_per_indikator`), verifikasi 1-ke-1 ke kunci 6 atribut Silver (`verifikasi_ketertelusuran_silver`), serta memastikan penggabungan metrik Sprint 1 dan Sprint 2 di `results/124450028/metrics.json` |

| 2026-11-25 | 124450006 | Gemini | Penyusunan tabel nasional Gold (`src/gold/tabel_nasional.py`), pengujian unit, kamus data, dan log keputusan (Kartu #22) | Mengubah struktur output Gold `tabel_nasional.parquet` dari pivot wide menjadi tabel rapi 1 baris per `(periode, seri_kode)` (76 baris teramati) dengan kolom `asal_angka` (`baris_indonesia` vs `pembanding`), guard penolakan agregat provinsi tanpa bobot mikro, lineage `_berkas_raw` & `_sha256_raw` wajib per baris, serta mempertahankan pivot wide CSV di `reports/tabel_nasional_periode_seri.csv` |