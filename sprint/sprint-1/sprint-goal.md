# Sprint 1 (9–22 November 2026)

## Sprint Goal

Semua berkas mentah Kasus 13 terbaca dengan lineage, setiap seri punya satuan dan kode SDG yang buktinya
tercatat, dan Silver pertama lolos pemeriksa skema serta aturan validasi dasar, sehingga Sprint 2 bisa
langsung menyusun panel dan tabel rekonsiliasi.

## Definition of Done yang Dipakai

- [x] **Pembaca semua format mentah:** BPS JSON/CSV (PR #5), WDI JSON (PR #10), ILOSTAT SDMX-CSV/DSD JSON (PR #11); 16 berkas mentah terverifikasi tanpa ada yang terlewat (PR #12).
- [x] **Profil dan calon anomali per seri utama:** 29 kandidat anomali terdeteksi (IQR & Z-score) dan dikategorikan (23 outlier asli, 6 patahan diduga); visualisasi tersimpan di `reports/gambar/` (PR #13, PR #14, PR #19).
- [x] **Missing, outlier, patahan, dan duplikat ditangani:** Dicatat lengkap pada `log-keputusan.csv` (K-001 s.d. K-010).
- [x] **Silver pertama lolos validasi skema:** `data/silver/silver.parquet` (1.325 baris observasi, 7 seri, 39 wilayah) lolos `python -m src.common.skema` (PR #15) dan 16/16 aturan Pandera `src/validasi/validasi_silver.py` (PR #22).
- [x] **Basis Data Relasional SQL:** Skema DDL `src/silver/skema.sql` ditegakkan pada basis data lokal `data/silver/silver.db` dengan penegakan kunci primer komposit 6 atribut (PR #21).
- [x] **Persiapan Integrasi Nasional:** Tabel nasional periode $\times$ seri (30 periode $\times$ 13 kolom) dan 5 daftar pasangan rekonsiliasi tersimpan di `reports/` (PR #20).
- [x] **Log Sprint semua anggota terisi:** Log tiga butir standar terisi lengkap di `sprint/sprint-1/` untuk seluruh 4 anggota aktif (Alfayya 124450006, Anggun 124450009, Ashila 124450028, Kaleb 124450053).
- [x] **Metrik individu di-commit:** File `results/<nim>/metrics.json` seluruh anggota aktif telah tercatat dan diverifikasi di Workbench.
- [x] **Penyatuan Komponen & Reproduksi Pipeline (Kartu #17):** Seluruh 24 PR tim ter-merge ke cabang utama; berkas starter dosen (`src/common/` & `unduh_data.py`) terlindungi 100% orisinal (0 diff); pipeline berjalan lolos sampai Silver dan tuntas hingga validasi dasar, terdokumentasi di [reports/integrasi_sprint1.md](file:///c:/Users/LENOVO/workbench-workspace/capstone-data-wrangling/reports/integrasi_sprint1.md).
- [x] **Kesiapan Demo Sprint 1:** Alur pipeline `python pipeline.py` teruji dari data mentah sampai pembentukan Silver dan validasi dasar; materi demo dan rekaman video disiapkan oleh tim Reproduksi & Demo (Anggun Nita didukung Kaleb Filbert Istel).
