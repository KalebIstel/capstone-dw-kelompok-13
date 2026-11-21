# Laporan Integrasi Komponen ke Cabang Utama (Sprint 1)

* **Penanggung Jawab:** Alfayya Rafif Abiyyi Rosyid Ridlo (NIM: 124450006)
* **Peran:** Integrator Tim & Penanggung Jawab Ekstraksi/Lineage
* **Kelompok:** 13 (Klaster C: Gender dan Ketenagakerjaan)
* **Kasus:** 13 — Pemuda NEET dan Pekerja Anak (SDG 8.6.1 & SDG 8.7.1)
* **Status Tugas Papan Tim:** Kartu #17 (*Merge komponen ke main: python pipeline.py jalan sampai Silver*)
* **Tanggal Pelaporan:** 21 November 2026

---

## 1. Ringkasan Eksekutif Integrasi

Sebagai Integrator Tim, tugas utama pada Sprint 1 adalah memastikan seluruh hasil kerja anggota tim yang tersebar di berbagai cabang kerja (`<nim>/kerja`) dapat ditinjau (*code review*), diuji kesesuaiannya, dan digabungkan (*merged*) secara berkala ke cabang utama (`main`). 

Puncak dari integrasi Sprint 1 adalah memastikan perintah tunggal reproduksi tim:
```bash
python pipeline.py
```
berhasil dieksekusi secara otomatis dari berkas mentah ber-lineage (`data/raw/`) hingga menghasilkan tabel Silver (`data/silver/silver.parquet`) yang lolos uji skema minimal dan aturan validasi dasar deklaratif tanpa kegagalan sistem (*zero error*).

Selain itu, Integrator berkewajiban menjaga integritas berkas patokan starter dosen:
- Direktori `src/common/` (`manifest.py`, `skema.py`, `hasil.py`)
- Skrip pengunduh `unduh_data.py`
agar **sama sekali tidak diubah atau dimodifikasi** sepanjang proses *sprint*.

---

## 2. Matriks Konsolidasi Pull Request Tim (PR #1 – #24)

Seluruh kontribusi anggota tim aktif (Alfayya, Anggun, Ashila, Kaleb) telah diintegrasikan melalui alur Pull Request di GitHub yang terdokumentasi dan ditinjau:

| No. PR | Pembuat / Cabang Asal | Komponen / Tahap | Deskripsi Capaian Integrasi | Status |
|:---:|:---|:---|:---|:---:|
| **#1** | Kaleb (`124450053/kerja`) | Inisialisasi | Penyiapan repositori awal dan struktur cabang kerja | *Merged* |
| **#2** | Alfayya (`124450006/kerja`) | Inisialisasi | Inisialisasi cabang kerja ekstraksi | *Merged* |
| **#3** | Ashila (`124450028/kerja`) | Inisialisasi | Inisialisasi cabang kerja pembersihan | *Merged* |
| **#4** | Anggun (`124450009/kerja`) | Inisialisasi | Inisialisasi cabang kerja validasi | *Merged* |
| **#5** | Alfayya (`124450006/kerja`) | Ekstraksi (Tahap 1) | Pembaca berkas mentah BPS (CSV & JSON WebAPI) ber-lineage | *Merged* |
| **#6** | Kaleb (`124450053/kerja`) | Ekstraksi (Tahap 1) | Verifikasi kecocokan data mentah terhadap `MANIFEST.csv` | *Merged* |
| **#7** | Alfayya (`124450006/kerja`) | Ekstraksi (Tahap 1) | Parser metadata DSD-like BPS untuk seri var1186 dan var2658 | *Merged* |
| **#8** | Anggun (`124450009/kerja`) | Kamus Data (Tahap 8) | Inisialisasi kamus data skema Silver untuk 7 seri Kasus 13 | *Merged* |
| **#9** | Ashila (`124450028/kerja`) | Profiling (Tahap 2) | Analisis statistik deskriptif & deteksi anomali awal indikator BPS | *Merged* |
| **#10** | Alfayya (`124450006/wdi`) | Ekstraksi (Tahap 1) | Pembaca berkas WDI JSON dan penapisan seri Kasus 13 | *Merged* |
| **#11** | Alfayya (`124450006/ilostat`) | Ekstraksi (Tahap 1) | Pembaca berkas ILOSTAT SDMX-CSV dan parser codelist DSD JSON | *Merged* |
| **#12** | Alfayya (`124450006/ekstraksi-gabung`) | Ekstraksi (Tahap 1) | Penyatuan ekstraksi & verifikasi kelengkapan 16 berkas mentah | *Merged* |
| **#13** | Ashila (`124450028/kerja`) | Profiling (Tahap 2) | Deteksi menyeluruh 29 kandidat anomali dengan IQR & Z-score | *Merged* |
| **#14** | Ashila (`124450028/kerja`) | Profiling (Tahap 2) | Profiling ketersediaan data 5 seri pembanding global (ILO/WDI) | *Merged* |
| **#15** | Kaleb (`124450053/kerja`) | Silver (Tahap 4) | Modul transformasi Silver pertama (1.325 baris) lolos skema | *Merged* |
| **#16** | Ashila (`124450028/kerja`) | Pembersihan (Tahap 3) | Evaluasi kelengkapan grid panel dan pencatatan keputusan | *Merged* |
| **#17** | Kaleb (`124450053/kerja`) | Dokumentasi (Tahap 8) | Pembaruan data dictionary dengan definisi rincian baku | *Merged* |
| **#18** | Anggun (`124450009/metadata-umur-sdg`) | Metadata (Tahap 4) | Standarisasi metadata kelompok umur dan kode SDG per seri | *Merged* |
| **#19** | Alfayya (`124450006/anomali-kategori`) | Pembersihan (Tahap 3) | Kategorisasi 29 anomali (23 outlier riil, 6 patahan serentak) | *Merged* |
| **#20** | Kaleb (`124450053/kerja`) | Integrasi (Tahap 6) | Penyusunan tabel nasional periode $\times$ seri & 5 pasangan rekonsiliasi | *Merged* |
| **#21** | Kaleb (`124450053/kerja`) | Penyimpanan (Tahap 5) | DDL skema SQL dan pemuatan 1.325 baris Silver ke SQLite | *Merged* |
| **#22** | Anggun (`12445009/validasi-silver`) | Validasi (Tahap 8) | Skema validasi otomatis Pandera dasar Silver (16 aturan) | *Merged* |
| **#23** | Anggun (`12445009/data-dictionary-silver`) | Dokumentasi (Tahap 8) | Penambahan contoh penelusuran lineage Silver ke berkas mentah | *Merged* |
| **#24** | Kaleb (`124450053/kerja`) | Integrasi & Log (Sprint 1) | Rekapitulasi log sprint tim, sprint goal, & resolusi pipeline | *Siap Merge* |

---

## 3. Audit Integritas Berkas Terlindungi

Sesuai aturan baku capstone data wrangling, berkas yang disediakan oleh dosen sebagai penguji skema dan integritas data tidak boleh dimodifikasi sedikit pun oleh tim mahasiswa. 

Hasil audit Git terhadap berkas patokan starter sejak commit inisial (`d7f6877`):
```bash
git diff d7f6877 HEAD -- src/common/ unduh_data.py
```
**Hasil:** Output kosong (**0 byte diff**). 

| Berkas Patokan | Jalur Berkas | Status Audit | Keterangan |
|---|---|:---:|---|
| Pemeriksa Manifest | `src/common/manifest.py` | **ASLI (0 diff)** | Fungsi hash SHA-256 dan verifikasi berkas mentah terjaga utuh. |
| Penguji Skema Minimal | `src/common/skema.py` | **ASLI (0 diff)** | 11 kolom wajib dan kunci komposit lantai tetap orisinal. |
| Pencatat Metrik | `src/common/hasil.py` | **ASLI (0 diff)** | Format output `metrics.json` dan pembentukan `data_hash` baku. |
| Skrip Pengunduh Data | `unduh_data.py` | **ASLI (0 diff)** | Logika unduhan CLI untuk seluruh kasus tidak tersentuh. |

---

## 4. Bukti Eksekusi Pipeline Reproduksi

Perintah tunggal reproduksi tim `python pipeline.py` telah teruji berjalan tuntas dari data mentah sampai Silver, Gold, dan Validasi.

### Log Eksekusi:
```text
$ python pipeline.py
data/raw: 16 berkas cocok dengan MANIFEST.csv
ekstraksi  selesai dalam 0.2 s
Silver tersimpan di data\silver\silver.parquet (1,325 baris)
silver     selesai dalam 0.1 s
Tabel nasional berhasil disimpan:
 - CSV     : reports\tabel_nasional_periode_seri.csv (30 periode x 13 seri/rincian)
 - Parquet : data\gold\tabel_nasional.parquet
gold       selesai dalam 0.1 s
[VALIDASI SILVER] Lolos 16/16 aturan untuk 1325 baris.
validasi   selesai dalam 0.1 s
Periksa skema minimal: python -m src.common.skema data/silver/silver.parquet
```

### Rincian Tahapan yang Tereksekusi:
1. **Tahap 1 — Ekstraksi:**
   Membaca seluruh 16 berkas mentah di `data/raw/` yang cocok dengan `MANIFEST.csv` (1.210 baris BPS, 132 baris WDI, 84 baris ILOSTAT).
2. **Tahap 2–4 — Transformasi ke Silver:**
   Menghasilkan berkas `data/silver/silver.parquet` berukuran 1.325 baris observasi, 7 seri indikator, 39 wilayah (38 provinsi + 1 nasional), dan 8 berkas raw penyusun.
3. **Tahap 5–6 — Penyusunan Tabel Nasional Gold:**
   Mengekstrak baris nasional (`wilayah_kode: 9999`) ke bentuk pivot `periode x seri` sebanyak 30 periode tahunan (1996–2025) $\times$ 13 kolom indikator/disagregasi, tersimpan di `data/gold/tabel_nasional.parquet` dan `reports/tabel_nasional_periode_seri.csv`.
4. **Tahap 8 — Validasi Otomatis Pandera:**
   Mengeksekusi 16 aturan validasi deklaratif terhadap tabel Silver dengan status **100% LOLOS**, tercatat pada `reports/validasi.md`.

---

## 5. Bukti Pemeriksaan Skema Lantai & Basis Data SQL

### A. Uji Skema Minimal Silver
```bash
$ python -m src.common.skema data/silver/silver.parquet
LOLOS  1,325 baris, 7 seri, 39 wilayah, 8 berkas sumber
```
*Tabel Silver memenuhi 11 kolom wajib, tidak memiliki baris kembar pada kunci komposit 6 atribut, dan seluruh hash SHA-256 cocok dengan `MANIFEST.csv`.*

### B. Uji Integritas Basis Data Relasional SQLite
```bash
$ python src/silver/muat_sql.py
Pemuatan berhasil: 1,325 baris dimuat ke SQLite.
======================================================================
RINGKASAN DATA SILVER DI BASIS DATA SQLITE
======================================================================
Berkas Database: data/silver/silver.db
Total Baris   : 1,325 baris
Jumlah Seri   : 7 seri
Jumlah Wilayah: 39 wilayah (provinsi + nasional)
Berkas Sumber : 8 berkas raw
======================================================================
```
*Kunci primer komposit 6 atribut `(sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw)` dan batasan nilai `CHECK (nilai >= 0 AND nilai <= 100)` terbukti aktif menegakkan integritas data.*

---

## 6. Kesimpulan Kesiapan Sprint 1

Berdasarkan seluruh pengujian di atas, cabang `main` berada dalam kondisi **sangat stabil, bersih, dan *reproducible***:
- ✅ Seluruh cabang anggota tim terintegrasi tanpa konflik merge.
- ✅ Berkas patokan dosen terlindungi 100% tanpa modifikasi.
- ✅ Perintah `python pipeline.py` lolos dari data mentah hingga Silver (dan Gold serta Validasi).
- ✅ Seluruh kriteria *Definition of Done* Sprint 1 terpenuhi dan terbukti pada artefak repositori.

Dengan demikian, kriteria selesai untuk **Kartu Papan Tim #17** dinyatakan **TERPENUHI LENGKAP**.
