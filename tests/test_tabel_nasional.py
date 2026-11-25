"""Pengujian otomatis tabel nasional Gold (Kartu #22, persiapan Tahap 6)."""
from pathlib import Path
import sys
import unittest

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.gold.tabel_nasional import (
    KUNCI_TABEL_NASIONAL,
    METADATA_SERI_NASIONAL,
    bangun_tabel_nasional_gold,
    buat_tabel_nasional,
    buat_tabel_nasional_wide,
    verifikasi_tabel_nasional,
)


def _buat_baris_silver(**override) -> dict:
    dasar = {
        "sumber": "bps",
        "seri_kode": "var1186",
        "wilayah_kode": 9999,
        "nama_wilayah": "INDONESIA",
        "periode": "2023",
        "jenis_periode": "tahun",
        "rincian": "total",
        "nilai": 22.25,
        "satuan": "persen",
        "_berkas_raw": "bps/2026-10-17/sdg8_neet.csv",
        "_sha256_raw": "a" * 64,
    }
    dasar.update(override)
    return dasar


class TestTabelNasionalGold(unittest.TestCase):
    def test_kunci_unik_periode_seri_dan_asal_angka_sintetis(self):
        df = pd.DataFrame([
            _buat_baris_silver(seri_kode="var1186", periode="2023", rincian="total", nilai=22.25),
            _buat_baris_silver(
                sumber="ilostat",
                seri_kode="SDG_0861_SEX_RT",
                periode="2023",
                rincian="total",
                nilai=21.569,
                _berkas_raw="ilostat/2026-10-20/data/DF_SDG_0861_SEX_RT.csv",
            ),
            _buat_baris_silver(
                sumber="ilostat",
                seri_kode="SDG_0861_SEX_RT",
                periode="2023",
                rincian="laki-laki",
                nilai=16.966,
                _berkas_raw="ilostat/2026-10-20/data/DF_SDG_0861_SEX_RT.csv",
            ),
            _buat_baris_silver(
                sumber="ilostat",
                seri_kode="SDG_A871_SEX_AGE_RT",
                periode="2023",
                rincian="15-17",
                nilai=1.567,
                _berkas_raw="ilostat/2026-10-20/data/DF_SDG_A871_SEX_AGE_RT.csv",
            ),
            _buat_baris_silver(
                sumber="ilostat",
                seri_kode="SDG_A871_SEX_AGE_RT",
                periode="2023",
                rincian="perempuan_15-17",
                nilai=1.03,
                _berkas_raw="ilostat/2026-10-20/data/DF_SDG_A871_SEX_AGE_RT.csv",
            ),
            _buat_baris_silver(
                sumber="wdi",
                seri_kode="SL.UEM.NEET.ZS",
                periode="2023",
                rincian="total",
                nilai=21.569,
                _berkas_raw="wdi/2026-10-20/data/kelompok-06-hal-01.json",
            ),
        ])

        tabel = buat_tabel_nasional(df_silver=df)
        self.assertEqual(len(tabel), 4)
        self.assertEqual(int(tabel.duplicated(KUNCI_TABEL_NASIONAL).sum()), 0)

        asal_per_seri = dict(zip(tabel["seri_kode"], tabel["asal_angka"]))
        self.assertEqual(asal_per_seri["var1186"], "baris_indonesia")
        self.assertEqual(asal_per_seri["SDG_0861_SEX_RT"], "pembanding")
        self.assertEqual(asal_per_seri["SDG_A871_SEX_AGE_RT"], "pembanding")
        self.assertEqual(asal_per_seri["SL.UEM.NEET.ZS"], "pembanding")

        ringkasan = verifikasi_tabel_nasional(tabel, df, wajib_lengkap_7_seri=False)
        self.assertEqual(ringkasan["baris_tertelusur"], 4)

    def test_seri_utama_tanpa_baris_indonesia_ditolak_eksplisit(self):
        df = pd.DataFrame([
            _buat_baris_silver(
                seri_kode="var1186",
                wilayah_kode=1100,
                nama_wilayah="ACEH",
                periode="2023",
                nilai=20.1,
            ),
            _buat_baris_silver(
                sumber="wdi",
                seri_kode="SL.UEM.NEET.ZS",
                periode="2023",
                nilai=21.569,
                _berkas_raw="wdi/2026-10-20/data/kelompok-06-hal-01.json",
            ),
        ])
        with self.assertRaisesRegex(ValueError, "tidak menerbitkan baris Indonesia"):
            buat_tabel_nasional(df_silver=df)

    def test_snapshot_terbaru_dan_csv_prioritas_terjaga_dengan_lineage(self):
        df = pd.DataFrame([
            _buat_baris_silver(
                seri_kode="var2658",
                periode="2023",
                nilai=1.50,
                _berkas_raw="bps/2026-10-10/sdg8_8_7_1_v2658.csv",
            ),
            _buat_baris_silver(
                seri_kode="var2658",
                periode="2023",
                nilai=1.53,
                _berkas_raw="bps/2026-10-17/json/sdg8_8_7_1_v2658.json",
            ),
            _buat_baris_silver(
                seri_kode="var2658",
                periode="2023",
                nilai=1.53,
                _berkas_raw="bps/2026-10-17/sdg8_8_7_1_v2658.csv",
            ),
        ])
        tabel = buat_tabel_nasional(df_silver=df)
        self.assertEqual(len(tabel), 1)
        self.assertEqual(tabel.loc[0, "nilai"], 1.53)
        self.assertEqual(tabel.loc[0, "snapshot_tanggal"], "2026-10-17")
        self.assertEqual(tabel.loc[0, "_berkas_raw"], "bps/2026-10-17/sdg8_8_7_1_v2658.csv")

    def test_integrasi_silver_nyata_ke_tabel_nasional_gold(self):
        silver_path = ROOT / "data/silver/silver.parquet"
        if not silver_path.exists():
            self.skipTest("data/silver/silver.parquet belum tersedia")

        tabel, tabel_wide, ringkasan = bangun_tabel_nasional_gold(
            silver_path=silver_path,
            simpan=False,
        )

        # 11 var1186 + 6 var2658 + 24 SDG_0861 + 3 SDG_A871 + 1 SDG_B871 + 28 SL.UEM.NEET + 3 SL.TLF.0714 = 76
        self.assertEqual(len(tabel), 76)
        self.assertEqual(ringkasan["jumlah_periode"], 30)
        self.assertEqual(ringkasan["jumlah_seri"], 7)
        self.assertEqual(set(tabel["seri_kode"].unique()), set(METADATA_SERI_NASIONAL))
        self.assertEqual(int(tabel.duplicated(KUNCI_TABEL_NASIONAL).sum()), 0)

        self.assertEqual(ringkasan["asal_angka"], {"pembanding": 59, "baris_indonesia": 17})
        self.assertTrue(tabel["_berkas_raw"].notna().all())
        self.assertTrue(tabel["_sha256_raw"].notna().all())
        self.assertEqual(ringkasan["baris_tertelusur"], 76)

        # Wide pivot tetap 30 periode x 14 kolom (periode + 13 seri/rincian)
        wide_langsung = buat_tabel_nasional_wide(silver_path=silver_path)
        self.assertEqual(tabel_wide.shape, (30, 14))
        self.assertEqual(wide_langsung.shape, (30, 14))


if __name__ == "__main__":
    unittest.main()
