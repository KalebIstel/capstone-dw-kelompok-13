"""Skrip pemuat tabel Silver ke basis data relasional SQLite.

Membuat skema tabel sesuai skema.sql, memuat data/silver/silver.parquet,
dan memvalidasi integritas kunci primer serta batasan nilai.
"""
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SQL_SCHEMA_FILE = ROOT / "src/silver/skema.sql"
SILVER_PARQUET_FILE = ROOT / "data/silver/silver.parquet"
SQLITE_DB_FILE = ROOT / "data/silver/silver.db"


def inisialisasi_basis_data(db_path: Path = SQLITE_DB_FILE, schema_path: Path = SQL_SCHEMA_FILE) -> sqlite3.Connection:
    """Membuka koneksi SQLite dan menerapkan DDL dari skema.sql."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    with open(schema_path, "r", encoding="utf-8") as f:
        ddl = f.read()
    conn.executescript(ddl)
    conn.commit()
    return conn


def muat_silver_ke_sql(parquet_path: Path = SILVER_PARQUET_FILE, db_path: Path = SQLITE_DB_FILE) -> int:
    """Memuat data Silver Parquet ke tabel SQLite dengan penegakan kunci primer."""
    if not parquet_path.exists():
        raise FileNotFoundError(f"Berkas Silver Parquet tidak ditemukan: {parquet_path}")

    df = pd.read_parquet(parquet_path)
    total_baris_parquet = len(df)

    conn = inisialisasi_basis_data(db_path)
    cursor = conn.cursor()

    # Bersihkan isi tabel lama jika ada agar pemuatan bersih & deterministik
    cursor.execute("DELETE FROM silver;")
    conn.commit()

    # Masukkan data menggunakan parameterized query
    kolom = [
        "sumber", "seri_kode", "wilayah_kode", "nama_wilayah",
        "periode", "jenis_periode", "rincian", "nilai",
        "satuan", "_berkas_raw", "_sha256_raw"
    ]
    query_insert = f"""
    INSERT INTO silver ({', '.join(kolom)})
    VALUES ({', '.join(['?'] * len(kolom))});
    """

    data_tuples = [tuple(x) for x in df[kolom].to_numpy()]
    cursor.executemany(query_insert, data_tuples)
    conn.commit()

    # Verifikasi jumlah baris yang tersimpan
    cursor.execute("SELECT COUNT(*) FROM silver;")
    total_baris_sql = cursor.fetchone()[0]

    if total_baris_sql != total_baris_parquet:
        conn.close()
        raise ValueError(
            f"Jumlah baris tidak cocok! Parquet: {total_baris_parquet}, SQL: {total_baris_sql}"
        )

    # Uji coba penegakan kunci primer (Primary Key Uniqueness Test)
    # Mencoba menyisipkan baris pertama sekali lagi; harus memicu sqlite3.IntegrityError
    try:
        cursor.execute(query_insert, data_tuples[0])
        conn.close()
        raise AssertionError("Peringatan: Kunci primer gagal menolak baris duplikat!")
    except sqlite3.IntegrityError:
        # Berhasil ditolak sesuai aturan integritas relasional
        pass

    conn.close()
    return total_baris_sql


def ringkasan_sql(db_path: Path = SQLITE_DB_FILE):
    """Menampilkan ringkasan data yang tersimpan di SQLite."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=" * 70)
    print("RINGKASAN DATA SILVER DI BASIS DATA SQLITE")
    print("=" * 70)
    print(f"Berkas Database: {db_path}")

    cursor.execute("SELECT COUNT(*) FROM silver;")
    print(f"Total Baris   : {cursor.fetchone()[0]:,} baris")

    cursor.execute("SELECT COUNT(DISTINCT seri_kode) FROM silver;")
    print(f"Jumlah Seri   : {cursor.fetchone()[0]} seri")

    cursor.execute("SELECT COUNT(DISTINCT wilayah_kode) FROM silver;")
    print(f"Jumlah Wilayah: {cursor.fetchone()[0]} wilayah (provinsi + nasional)")

    cursor.execute("SELECT COUNT(DISTINCT _berkas_raw) FROM silver;")
    print(f"Berkas Sumber : {cursor.fetchone()[0]} berkas raw")

    print("\nRincian per Sumber Data:")
    cursor.execute("""
    SELECT sumber, COUNT(*) as baris, COUNT(DISTINCT seri_kode) as seri, 
           COUNT(DISTINCT wilayah_kode) as wilayah, MIN(nilai) as min_val, MAX(nilai) as max_val
    FROM silver
    GROUP BY sumber
    ORDER BY sumber;
    """)
    for row in cursor.fetchall():
        print(f" - {row[0]:<8}: {row[1]:>5} baris | {row[2]} seri | {row[3]:>2} wilayah | rentang nilai: {row[4]:.2f}% s.d. {row[5]:.2f}%")

    conn.close()
    print("=" * 70)


if __name__ == "__main__":
    n = muat_silver_ke_sql()
    print(f"Pemuatan berhasil: {n:,} baris dimuat ke SQLite.")
    ringkasan_sql()
