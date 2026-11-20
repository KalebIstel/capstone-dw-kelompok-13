# Evaluasi Perancangan Skema SQL Silver dan Pilihan Basis Data
*Draf Laporan Tim — Tahap 5: Penyimpanan*

* **Penyusun:** Kaleb Filbert Istel (NIM: 124450053)
* **Komponen:** Integrasi, Penyimpanan, dan Skala (Tahap 5–7)
* **Kasus:** 13 — Pemuda NEET dan Pekerja Anak (SDG 8.6.1 & SDG 8.7.1)
* **Status:** Draf Resmi untuk Laporan Tim (`reports/tim.md`)

---

## 1. Perancangan Skema Relasional SQL Silver

Pada arsitektur *data wrangling* proyek capstone ini, lapis Silver berperan sebagai fondasi data bersih, terstandarisasi, dan ber-lineage lengkap. Skema SQL dirancang untuk menegakkan kontrak data (*data contract*) yang didefinisikan pada starter (`src/common/skema.py`).

### A. Definisi Kolom dan Tipe Data
Tabel `silver` didefinisikan dengan 11 kolom wajib melalui DDL ANSI SQL:

```sql
CREATE TABLE IF NOT EXISTS silver (
    sumber          VARCHAR(16)  NOT NULL,
    seri_kode       VARCHAR(64)  NOT NULL,
    wilayah_kode    INTEGER      NOT NULL,
    nama_wilayah    VARCHAR(64)  NOT NULL,
    periode         VARCHAR(10)  NOT NULL,
    jenis_periode   VARCHAR(16)  NOT NULL,
    rincian         VARCHAR(64)  NOT NULL,
    nilai           REAL         NOT NULL,
    satuan          VARCHAR(16)  NOT NULL,
    _berkas_raw     VARCHAR(255) NOT NULL,
    _sha256_raw     VARCHAR(64)  NOT NULL,
    
    PRIMARY KEY (sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw),
    CHECK (nilai >= 0.0 AND nilai <= 100.0),
    CHECK (jenis_periode IN ('tahun', 'semester', 'triwulan', 'bulan')),
    CHECK (wilayah_kode = 9999 OR (wilayah_kode >= 1100 AND wilayah_kode <= 9700))
);
```

### B. Rasionalisasi Kunci Primer Komposit (6 Atribut)
Kunci primer tabel `silver` dibentuk dari kombinasi enam kolom:
$$\text{PK} = \{\text{sumber}, \text{seri\_kode}, \text{wilayah\_kode}, \text{periode}, \text{rincian}, \text{\_berkas\_raw}\}$$

1. **Granularitas Observasi:** Satu baris data mewakili satu nilai amatan indikator pada suatu wilayah, periode waktu, dan kelompok rincian tertentu dari produsen data spesifik.
2. **Koeksistensi Dua Berkas Sumber (Lineage):** Sesuai aturan umum capstone Bagian 2, BPS menyediakan dua format untuk indikator yang sama, yaitu CSV datar dan respons JSON WebAPI (`sdg8_neet.csv` dan `sdg8_neet.json`). Kedua berkas sengaja disimpan bersamaan di Silver untuk keperluan verifikasi dan audit reproduksibilitas. Memasukkan atribut `_berkas_raw` ke dalam kunci primer memungkinkan koeksistensi kedua berkas tersebut tanpa bentrok kunci (*duplicate key violation*), sementara di tingkat data/analisis tetap dijamin tidak ada baris ganda yang berasal dari satu berkas yang sama.

### C. Batasan Integritas (*Integrity & Check Constraints*)
- `CHECK (nilai >= 0.0 AND nilai <= 100.0)`: Memastikan nilai rasio/persentase tidak melampaui batas matematis yang sah.
- `CHECK (jenis_periode IN (...))`: Mengunci kategori granularitas waktu ke format resmi yang didukung pipeline.
- `CHECK (wilayah_kode = 9999 OR (wilayah_kode >= 1100 AND wilayah_kode <= 9700))`: Memastikan kode wilayah valid menurut standar BPS (38 provinsi tahun 2025 dan kode nasional 9999).

---

## 2. Evaluasi Pemilihan Engine Basis Data

Dalam panduan Capstone Bagian 5.6 (Tahap 5), tim diinstruksikan untuk membandingkan tiga opsi basis data relasional: **SQLite**, **DuckDB**, dan **PostgreSQL**.

### A. Tabel Matriks Komparasi

| Parameter Evaluasi | SQLite | DuckDB | PostgreSQL |
|---|---|---|---|
| **Arsitektur Sistem** | *In-process / Embedded Serverless* | *In-process / Embedded Columnar* | *Client-Server RDBMS* |
| **Kebutuhan Dependensi** | Nol (*Zero-dependency*, bawaan Python `sqlite3`) | Paket Python (`duckdb`) | Memerlukan *daemon* PostgreSQL lokal/container |
| **Orientasi Penyimpanan** | Berorientasi Baris (*Row-oriented / OLTP*) | Berorientasi Kolom (*Columnar / OLAP*) | Berorientasi Baris/Tabel (*Hybrid OLTP*) |
| **Penegakan Kunci Primer** | Sangat Ketat (*B-Tree Index PK Enforcement*) | Mendukung PK (*Artful constraint check*) | Sangat Ketat (*Heavy transactional PK*) |
| **Integrasi Parquet** | Memerlukan jembatan Pandas/PyArrow | Pembacaan Parquet langsung (*Zero-copy pushdown*) | Memerlukan modul eksternal (`COPY` / FDW) |
| **Ukuran & Portabilitas** | 1 berkas biner portabel (`silver.db`) | 1 berkas biner portabel (`silver.duckdb`) | Terdistribusi dalam direktori data cluster |
| **Kesesuaian Target Reproduksi (< 15 Menit)** | **Sangat Sesuai (100% Mandiri)** | **Sangat Sesuai untuk Analisis** | **Kurang Sesuai** (rentan kendala konfigurasi port & auth) |

### B. Justifikasi Keputusan Pemilihan untuk Tim

1. **Pilihan Utama untuk Lapis Silver: SQLite (`data/silver/silver.db`)**
   - **Kemandirian Lingkungan (*Self-contained*):** Modul `sqlite3` adalah modul standar Python, menjamin skrip `muat_sql.py` dapat berjalan di lingkungan laptop mana pun tanpa perlu koneksi internet untuk mengunduh paket eksternal (mematuhi Prinsip 3: *Satu perintah mereproduksi semuanya dalam waktu < 15 menit*).
   - **Penegakan Transaksional Kuat:** SQLite menegakkan batasan kunci primer komposit secara absolut. Jika terdapat rekonsiliasi yang salah atau data duplikat yang lolos dari tahap pembersihan, SQLite akan langsung melempar `IntegrityError`.
   - **Kompak:** Seluruh 1.325 baris Silver tersimpan dalam satu file `data/silver/silver.db` berukuran hanya $\approx 420\text{ KB}$.

2. **Rencana Penggunaan Bersama DuckDB pada Tahap Panel Gold (Sprint 2 & 3):**
   - Untuk transformasi panel lebar Gold (provinsi $\times$ periode $\times$ indikator) dan analisis skala arsip WDI 142 rilis (Tahap 7), DuckDB akan diintegrasikan karena keunggulan vektorisasi kolumnar dan efisiensi memori yang jauh lebih tinggi untuk kueri analitis berat.

---

## 3. Komparasi: Skema SQL Relasional vs Penyimpanan Dokumen JSON Mentah

Panduan meminta perbandingan antara menyimpan data dalam skema SQL terstruktur versus mempertahankan respons JSON WebAPI mentah sebagai dokumen (gaya NoSQL / Document Store).

| Dimensi Evaluasi | Skema Relasional SQL (Tabular) | Dokumen JSON Mentah (Document Store) |
|---|---|---|
| **Paradigma Skema** | *Schema-on-Write* (Skema divalidasi saat data dimasukkan) | *Schema-on-Read* (Struktur diinterpretasikan saat data dibaca) |
| **Jaminan Integritas & Tipe Data** | Mutlak: tipe data (`REAL`, `INTEGER`), `NOT NULL`, dan `CHECK` ditegakkan di level storage engine. | Rentan: tipe data bercampur teks/angka di dalam atribut JSON, *null* tersamar. |
| **Penegakan Keunikan Kunci** | Otomatis melalui *Composite Primary Key Index*. | Sulit dan mahal: membutuhkan pemindaian dokumen penuh (*full document scan*) untuk memastikan tidak ada kunci ganda. |
| **Kecepatan Kueri Analitis (Agregasi)** | Sangat Cepat: Kueri `SELECT AVG(nilai) ... GROUP BY wilayah_kode` dieksekusi dalam beberapa milidetik via indeks. | Lambat: Memerlukan *deserialization* (parsing JSON teks) dari seluruh dokumen sebelum agregasi dapat dihitung. |
| **Efisiensi Ruang Penyimpanan** | Sangat Efisien: Tipe data biner tanpa redundansi nama field per baris. | Boros: Setiap entri mengulang string kunci (`var_id`, `wilayah_id`, `datacontent`, dll.). |
| **Peran Ideal dalam Pipeline** | **Wajib di Lapis Silver dan Gold** (menjamin data siap analisis dan bebas anomali). | **Hanya cocok di Lapis Bronze** (arsip setia sumber mentah). |

### Kesimpulan Komparatif
Menyimpan data mentah sebagai dokumen JSON sangat ideal untuk **Tahap 1 (Bronze)** karena mematuhi Prinsip 1 (*Data mentah tidak pernah diubah*). Namun, untuk **Lapis Silver**, pendekatan dokumen JSON harus ditinggalkan dan ditransformasikan ke dalam skema SQL relasional terindeks. Skema relasional menjamin konsistensi tipe data, menghilangkan ambiguitas desimal, menegakkan keunikan amatan, dan memungkinkan kueri analitis multi-dimensi secara instan.

---

## 4. Hasil Verifikasi Implementasi Pemuatan

Skrip pemuat [src/silver/muat_sql.py](file:///c:/Users/LENOVO/workbench-workspace/capstone-data-wrangling/src/silver/muat_sql.py) telah dieksekusi pada `data/silver/silver.parquet`:

1. **Integritas Baris:** Sebanyak **1.325 baris observasi** berhasil dimuat ke dalam `data/silver/silver.db` tanpa satupun data yang hilang atau terpotong ($100\%$ konsisten terhadap berkas Parquet).
2. **Distribusi Seri:**
   - **BPS:** 1.210 baris (2 seri: `var1186` dan `var2658`, 38 provinsi + nasional).
   - **ILOSTAT:** 84 baris (3 seri: `SDG_0861_SEX_RT`, `SDG_A871_SEX_AGE_RT`, `SDG_B871_SEX_AGE_RT`, nasional).
   - **WDI:** 31 baris (2 seri: `SL.UEM.NEET.ZS` dan `SL.TLF.0714.ZS`, nasional).
3. **Uji Validasi Penegakan Kunci Primer:** Percobaan penyisipan baris duplikat secara terprogram berhasil memicu `sqlite3.IntegrityError: UNIQUE constraint failed: silver...`, membuktikan bahwa proteksi integritas kunci primer di tingkat basis data berfungsi dengan sempurna.
