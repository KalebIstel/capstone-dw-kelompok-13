"""Pengujian otomatis skema DDL SQL dan pemuatan DuckDB Silver + Gold (Kartu #23)."""
from pathlib import Path
import sys
import tempfile
import unittest

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.gold.muat_sql import (
    SPESIFIKASI_TABEL,
    inisialisasi_duckdb,
    muat_semua_ke_sql,
)


class TestSqlGoldDuckDB(unittest.TestCase):
    """Menguji DDL, kesesuaian jumlah baris Parquet vs SQL, dan batasan integritas DuckDB."""

    def test_ddl_dan_pemuatan_berkas_parquet_nyata(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "uji.duckdb"
            ringkasan = muat_semua_ke_sql(db_path=db_path)

            df_silver = pd.read_parquet(SPESIFIKASI_TABEL["silver"]["parquet"])
            df_panel = pd.read_parquet(SPESIFIKASI_TABEL["gold_panel"]["parquet"])
            df_nasional = pd.read_parquet(SPESIFIKASI_TABEL["gold_tabel_nasional"]["parquet"])

            self.assertEqual(ringkasan["silver"], len(df_silver))
            self.assertEqual(ringkasan["gold_panel"], len(df_panel))
            self.assertEqual(ringkasan["gold_tabel_nasional"], len(df_nasional))

            con = duckdb.connect(str(db_path))
            try:
                tabel_ada = {
                    row[0]
                    for row in con.execute(
                        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main';"
                    ).fetchall()
                }
                self.assertEqual(
                    tabel_ada,
                    {"silver", "gold_panel", "gold_tabel_nasional", "gold_rekonsiliasi"},
                )
            finally:
                con.close()

    def test_tolak_duplikat_primary_key_dan_nilai_tidak_sah(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "uji_pk.duckdb"
            muat_semua_ke_sql(db_path=db_path)

            con = duckdb.connect(str(db_path))
            try:
                for tabel in ("silver", "gold_panel", "gold_tabel_nasional"):
                    with self.subTest(tabel=tabel):
                        with self.assertRaises(duckdb.ConstraintException):
                            con.execute(f"INSERT INTO {tabel} SELECT * FROM {tabel} LIMIT 1;")

                # Uji CHECK constraint nilai di luar rentang 0..100 pada tabel nasional
                with self.assertRaises(duckdb.ConstraintException):
                    con.execute(
                        """
                        INSERT INTO gold_tabel_nasional VALUES (
                            '2099', 'var1186', 'neet', 'neet_15_24', 'utama',
                            'baris_indonesia', 'bps', 9999, 'INDONESIA', 'total',
                            '15-24', 150.0, 'persen', '2026-10-17',
                            'bps/2026-10-17/sdg8_neet.csv', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
                        );
                        """
                    )
            finally:
                con.close()

    def test_pemuatan_opsional_gold_rekonsiliasi(self):
        df_rekon = pd.DataFrame(
            [
                {
                    "pasangan_id": "P1",
                    "topik": "neet",
                    "wilayah_kode": 9999,
                    "periode": "2023",
                    "seri_utama": "var1186",
                    "seri_pembanding": "SDG_0861_SEX_RT",
                    "nilai_utama": 22.25,
                    "nilai_pembanding": 21.569,
                    "selisih": 0.681,
                    "kategori_selisih": "metode berbeda",
                    "penjelasan": "Survei Sakernas BPS vs model harmonisasi ILOSTAT.",
                    "kelompok_umur_utama": "15-24",
                    "kelompok_umur_pembanding": "15-24",
                    "_berkas_raw_utama": "bps/2026-10-17/sdg8_neet.csv",
                    "_berkas_raw_pembanding": "ilostat/2026-10-20/data/DF_SDG_0861_SEX_RT.csv",
                    "_sha256_raw_utama": "a" * 64,
                    "_sha256_raw_pembanding": "b" * 64,
                }
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "uji_rekon.duckdb"
            ringkasan = muat_semua_ke_sql(
                gold_dict={"rekonsiliasi": df_rekon},
                db_path=db_path,
            )
            self.assertEqual(ringkasan["gold_rekonsiliasi"], 1)

            con = duckdb.connect(str(db_path))
            try:
                with self.assertRaises(duckdb.ConstraintException):
                    con.execute("INSERT INTO gold_rekonsiliasi SELECT * FROM gold_rekonsiliasi LIMIT 1;")
            finally:
                con.close()

    def test_ddl_berdiri_sendiri_tanpa_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "kosong.duckdb"
            con = inisialisasi_duckdb(db_path=db_path, reset_tabel=False)
            try:
                for tabel in SPESIFIKASI_TABEL:
                    jumlah = con.execute(f"SELECT COUNT(*) FROM {tabel};").fetchone()[0]
                    self.assertEqual(jumlah, 0)
            finally:
                con.close()


if __name__ == "__main__":
    unittest.main()
