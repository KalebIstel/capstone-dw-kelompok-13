"""Skrip pemuat tabel Silver dan Gold ke basis data relasional DuckDB.

Menerapkan DDL berkunci primer dari src/gold/skema.sql untuk tabel:
1. silver (data/silver/silver.parquet)
2. gold_panel (data/gold/panel.parquet)
3. gold_tabel_nasional (data/gold/tabel_nasional.parquet)
4. gold_rekonsiliasi (data/gold/rekonsiliasi.parquet, bila tersedia)

Berkas basis data (*.duckdb) tidak di-commit dan dibangun ulang otomatis oleh pipeline.py.
"""
from __future__ import annotations

from pathlib import Path
import sys

_venv_lib = Path(__file__).resolve().parents[2] / ".venv" / "Lib" / "site-packages"
if _venv_lib.exists() and str(_venv_lib) not in sys.path:
    sys.path.insert(0, str(_venv_lib))

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SQL_SCHEMA_FILE = ROOT / "src/gold/skema.sql"
DUCKDB_FILE = ROOT / "data/gold/capstone.duckdb"

SPESIFIKASI_TABEL: dict[str, dict] = {
    "silver": {
        "parquet": ROOT / "data/silver/silver.parquet",
        "wajib": True,
        "kolom": [
            "sumber", "seri_kode", "wilayah_kode", "nama_wilayah",
            "periode", "jenis_periode", "rincian", "nilai",
            "satuan", "_berkas_raw", "_sha256_raw",
        ],
    },
    "gold_panel": {
        "parquet": ROOT / "data/gold/panel.parquet",
        "wajib": True,
        "kolom": [
            "seri_kode", "indikator", "wilayah_kode", "nama_wilayah",
            "periode", "sumber", "rincian", "nilai", "satuan",
            "status_wilayah", "status_data", "penanda_anomali",
            "arah_serentak_tahun", "catatan_anomali", "snapshot_tanggal",
            "_berkas_raw", "_sha256_raw",
        ],
    },
    "gold_tabel_nasional": {
        "parquet": ROOT / "data/gold/tabel_nasional.parquet",
        "wajib": True,
        "kolom": [
            "periode", "seri_kode", "topik", "indikator", "peran_seri",
            "asal_angka", "sumber", "wilayah_kode", "nama_wilayah",
            "rincian", "kelompok_umur", "nilai", "satuan",
            "snapshot_tanggal", "_berkas_raw", "_sha256_raw",
        ],
    },
    "gold_rekonsiliasi": {
        "parquet": ROOT / "data/gold/rekonsiliasi.parquet",
        "wajib": False,
        "kolom": [
            "pasangan_id", "topik", "wilayah_kode", "periode",
            "seri_utama", "seri_pembanding", "nilai_utama", "nilai_pembanding",
            "selisih", "kategori_selisih", "penjelasan",
            "kelompok_umur_utama", "kelompok_umur_pembanding",
            "_berkas_raw_utama", "_berkas_raw_pembanding",
            "_sha256_raw_utama", "_sha256_raw_pembanding",
        ],
    },
}


def inisialisasi_duckdb(
    db_path: Path = DUCKDB_FILE,
    schema_path: Path = SQL_SCHEMA_FILE,
    reset_tabel: bool = True,
) -> duckdb.DuckDBPyConnection:
    """Membuka koneksi DuckDB dan menerapkan DDL dari src/gold/skema.sql."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    if reset_tabel:
        for nama_tabel in reversed(list(SPESIFIKASI_TABEL)):
            con.execute(f"DROP TABLE IF EXISTS {nama_tabel};")
    ddl = schema_path.read_text(encoding="utf-8")
    con.execute(ddl)
    return con


def _muat_satu_tabel(
    con: duckdb.DuckDBPyConnection,
    nama_tabel: str,
    df: pd.DataFrame,
    kolom: list[str],
) -> int:
    """Sisipkan DataFrame ke tabel DuckDB sesuai urutan kolom DDL dan verifikasi jumlah baris."""
    alias_tmp = f"_tmp_{nama_tabel}"
    con.register(alias_tmp, df[kolom])
    daftar_kolom = ", ".join(kolom)
    con.execute(f"INSERT INTO {nama_tabel} ({daftar_kolom}) SELECT {daftar_kolom} FROM {alias_tmp};")
    con.unregister(alias_tmp)

    baris_sql = int(con.execute(f"SELECT COUNT(*) FROM {nama_tabel};").fetchone()[0])
    if baris_sql != len(df):
        raise ValueError(
            f"Jumlah baris {nama_tabel} tidak cocok! Parquet/DF: {len(df)}, SQL: {baris_sql}"
        )
    return baris_sql


def _uji_kunci_primer(con: duckdb.DuckDBPyConnection, nama_tabel: str) -> None:
    """Pastikan kunci primer menolak penyisipan baris duplikat dengan duckdb.ConstraintException."""
    con.begin()
    try:
        con.execute(f"INSERT INTO {nama_tabel} SELECT * FROM {nama_tabel} LIMIT 1;")
    except duckdb.ConstraintException:
        con.rollback()
        return
    con.rollback()
    raise AssertionError(f"Kunci primer pada tabel '{nama_tabel}' gagal menolak baris duplikat!")


def _ambil_dataframe_sumber(
    nama_tabel: str,
    spec: dict,
    sumber_df: dict[str, pd.DataFrame],
) -> pd.DataFrame | None:
    """Ambil DataFrame dari memori atau baca berkas Parquet terkait bila tersedia."""
    if nama_tabel in sumber_df and sumber_df[nama_tabel] is not None:
        return sumber_df[nama_tabel]
    jalur_parquet: Path = spec["parquet"]
    if jalur_parquet.exists():
        return pd.read_parquet(jalur_parquet)
    if spec["wajib"]:
        raise FileNotFoundError(f"Berkas Parquet wajib untuk '{nama_tabel}' tidak ditemukan: {jalur_parquet}")
    return None


def muat_semua_ke_sql(
    silver_df: pd.DataFrame | None = None,
    gold_dict: dict[str, pd.DataFrame] | None = None,
    db_path: Path = DUCKDB_FILE,
    schema_path: Path = SQL_SCHEMA_FILE,
) -> dict[str, int]:
    """Muat tabel Silver dan seluruh tabel Gold ke DuckDB serta verifikasi jumlah baris dan PK."""
    sumber_df: dict[str, pd.DataFrame] = {}
    if silver_df is not None:
        sumber_df["silver"] = silver_df
    if gold_dict:
        pemetaan = {
            "panel": "gold_panel",
            "tabel_nasional": "gold_tabel_nasional",
            "rekonsiliasi": "gold_rekonsiliasi",
        }
        for kunci_gold, nama_tabel in pemetaan.items():
            if kunci_gold in gold_dict and gold_dict[kunci_gold] is not None:
                sumber_df[nama_tabel] = gold_dict[kunci_gold]

    con = inisialisasi_duckdb(db_path=db_path, schema_path=schema_path, reset_tabel=True)
    ringkasan: dict[str, int] = {}
    try:
        for nama_tabel, spec in SPESIFIKASI_TABEL.items():
            df = _ambil_dataframe_sumber(nama_tabel, spec, sumber_df)
            if df is None:
                ringkasan[nama_tabel] = 0
                continue
            jumlah = _muat_satu_tabel(con, nama_tabel, df, spec["kolom"])
            if jumlah > 0:
                _uji_kunci_primer(con, nama_tabel)
            ringkasan[nama_tabel] = jumlah
    finally:
        con.close()

    return ringkasan


def cetak_ringkasan_sql(ringkasan: dict[str, int], db_path: Path = DUCKDB_FILE) -> None:
    """Tampilkan ringkasan isi tabel DuckDB Silver dan Gold."""
    bagian = ", ".join(f"{k}={v}" for k, v in ringkasan.items())
    rel_db = db_path.relative_to(ROOT) if db_path.is_relative_to(ROOT) else db_path
    print(f"Basis data SQL (DuckDB) tersimpan di {rel_db} ({bagian})")


if __name__ == "__main__":
    hasil = muat_semua_ke_sql()
    cetak_ringkasan_sql(hasil)
