# Pilihan Basis Data dan Rancangan Skema SQL Silver & Gold (Tahap 5)

* **Penyusun:** Kaleb Filbert Istel (NIM: 124450053)
* **Komponen:** Integrasi, Penyimpanan, dan Skala (Tahap 5–7)
* **Kasus:** 13 — Klaster C: Gender dan Ketenagakerjaan (Pemuda NEET [SDG 8.6.1] & Pekerja Anak [SDG 8.7.1])
* **Rujukan Keputusan:** `K-024` di [log-keputusan.csv](file:///c:/Users/LENOVO/workbench-workspace/capstone-data-wrangling/log-keputusan.csv), diringkas di [reports/tim.md](file:///c:/Users/LENOVO/workbench-workspace/capstone-data-wrangling/reports/tim.md) bagian *Data dan lineage*.

---

## 1. Skema SQL Terpadu Silver dan Gold (`src/gold/skema.sql`)

Seluruh tabel Silver dan Gold didefinisikan dengan DDL eksplisit, tipe data terukur, kunci primer komposit anti-duplikasi, batasan `CHECK`, serta indeks kueri pada [src/gold/skema.sql](file:///c:/Users/LENOVO/workbench-workspace/capstone-data-wrangling/src/gold/skema.sql), dan dibangun ulang otomatis ke `data/gold/capstone.duckdb` setiap kali `python pipeline.py` dijalankan lewat [src/gold/muat_sql.py](file:///c:/Users/LENOVO/workbench-workspace/capstone-data-wrangling/src/gold/muat_sql.py). Berkas `.duckdb` dikecualikan dari Git melalui `.gitignore` (`*.duckdb`).

| Tabel SQL | Sumber Parquet | Kunci Primer (`PRIMARY KEY`) | Jumlah Kolom | Jumlah Baris (Parquet == SQL) | Batasan Integritas (`CHECK` / `NOT NULL`) |
|---|---|---|---:|---:|---|
| **`silver`** | `data/silver/silver.parquet` | `(sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw)` | 11 | **1.325** | Seluruh kolom `NOT NULL`; `0 <= nilai <= 100`; `jenis_periode` baku; `wilayah_kode` valid (38 prov + `9999`). |
| **`gold_panel`** | `data/gold/panel.parquet` | `(wilayah_kode, periode, seri_kode)` | 17 | **646** | `nilai IS NULL` diizinkan hanya saat `status_data != 'tersedia'` (58 sel kosong struktural); `0 <= nilai <= 100`; status wilayah & data tervalidasi. |
| **`gold_tabel_nasional`** | `data/gold/tabel_nasional.parquet` | `(periode, seri_kode)` | 16 | **76** | Seluruh 16 kolom `NOT NULL` termasuk `_berkas_raw` & `_sha256_raw`; `wilayah_kode = 9999`; `peran_seri` & `asal_angka` terkunci. |
| **`gold_rekonsiliasi`** | `data/gold/rekonsiliasi.parquet` *(siap Tahap 6)* | `(pasangan_id, periode, wilayah_kode)` | 17 | **0** *(siap-isi saat keluaran Tahap 6 hadir)* | `kategori_selisih` terkunci (`definisi`, `metode`, `vintage`, `cakupan`, `identik`, `belum terjelaskan`, `tidak_beririsan`); rentang nilai sah. |

*(Skema SQLite khusus Silver dari Sprint 1 di [src/silver/skema.sql](file:///c:/Users/LENOVO/workbench-workspace/capstone-data-wrangling/src/silver/skema.sql) dan [src/silver/muat_sql.py](file:///c:/Users/LENOVO/workbench-workspace/capstone-data-wrangling/src/silver/muat_sql.py) tetap dipertahankan utuh untuk kompatibilitas skrip mandiri Sprint 1).*

---

## 2. Perbandingan Engine Basis Data: DuckDB vs SQLite vs PostgreSQL

| Aspek Penilaian | **DuckDB** *(Pilihan Utama Silver+Gold)* | **SQLite** *(Pilihan Pendamping Silver)* | **PostgreSQL** *(Ditolak)* |
|---|---|---|---|
| **Model Operasi** | *In-process serverless* (library Python `duckdb`) | *In-process serverless* (bawaan Python `sqlite3`) | *Client-server* (butuh *daemon*, port, dan user/auth) |
| **Kebutuhan Setup Reproduksi** | Cukup `pip install -r requirements.txt` | Tanpa instalasi tambahan (*zero-dependency*) | Harus instal/konfigurasi server di tiap laptop anggota |
| **Orientasi Penyimpanan** | **Kolumnar (*OLAP*)** — unggul untuk agregasi panel lebar Gold & arsip WDI 142 rilis | **Baris (*OLTP*)** — sangat ringan untuk data transaksional/observasi awal | Hibrida *row-oriented* kuat untuk multi-user konkuren |
| **Integrasi Pandas / Parquet** | Pembacaan/registrasi DataFrame & Parquet langsung (*zero-copy*) | Harus iterasi *tuple* lewat DB-API | Harus lewat adaptor eksternal (`psycopg`/`COPY`) |
| **Penegakan Kunci Primer & `CHECK`** | Ketat: menolak kunci ganda lewat `duckdb.ConstraintException` | Ketat: menolak kunci ganda lewat `sqlite3.IntegrityError` | Sangat ketat dan transaksional |
| **Kesesuaian Pipeline < 15 Menit** | **Sangat Sesuai** (waktu muat + uji PK $< 0.2$ detik) | **Sesuai** (khusus Silver $< 0.1$ detik) | **Tidak Praktis** (rawan gagal koneksi antar-mesin penguji) |

**Kesimpulan Pemilihan Engine:**
- **DuckDB (`data/gold/capstone.duckdb`)** cocok untuk lapis terintegrasi **Silver dan Gold** karena pipeline analitis ini bertipe *single-writer analytical workload* yang mengolah panel provinsi, rekonsiliasi seri nasional, dan nantinya ratusan rilis arsip WDI (Tahap 7), tanpa membebani lingkungan reproduksi dengan server eksternal seperti PostgreSQL.
- **SQLite (`data/silver/silver.db`)** tetap menjadi pelengkap ideal pada lapis Silver murni karena bawaan standar Python (*zero-dependency*).

---

## 3. Perbandingan Pendekatan: Skema SQL Relasional vs Dokumen JSON Mentah

| Dimensi Evaluasi | **Skema Relasional SQL (Silver & Gold)** | **Dokumen JSON Mentah (Gaya NoSQL / Bronze)** |
|---|---|---|
| **Mekanisme Skema** | ***Schema-on-write***: tipe kolom (`INTEGER`, `DOUBLE`), `NOT NULL`, `PRIMARY KEY`, dan `CHECK` divalidasi saat data masuk. | ***Schema-on-read***: struktur baru ditafsirkan ketika dibaca skrip; rentan angka tersimpan sebagai string atau kunci bercabang tidak konsisten (mis. kunci `datacontent` WebAPI BPS). |
| **Keunikan & Anti-Duplikasi** | Ditegakkan otomatis oleh mesin basis data; penyisipan baris ganda langsung gagal (`ConstraintException`). | Membutuhkan pemindaian dokumen penuh (*full scan*) manual pada setiap pembacaan untuk mendeteksi duplikasi. |
| **Kueri Analitis & Join** | Sangat cepat: penggabungan Silver $\leftrightarrow$ Gold, agregasi lintas provinsi/tahun, dan filter dieksekusi dalam milidetik via indeks kolumnar. | Lambat dan boros memori: seluruh file JSON harus di-*parse* terlebih dahulu sebelum penjumlahan atau penyaringan bisa dilakukan. |
| **Efisiensi Penyimpanan** | Ringkas dalam format biner tanpa mengulang nama field di setiap baris. | Redundan karena setiap objek mengulang nama atribut teks. |
| **Kecocokan Per Lapis** | **Tepat untuk lapis Silver dan Gold** (fondasi data terstandardisasi dan panel analitis siap pakai). | **Tepat hanya untuk lapis Bronze (`data/raw/`)** guna menyimpan respons asli sumber data secara utuh dan setia tanpa modifikasi (Prinsip 1). |
