"""Pengujian otomatis modul rekonsiliasi Gold Tahap 6 (Kartu #24)."""
from pathlib import Path
import sys
import unittest

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.gold.rekonsiliasi import (
    KATEGORI_BERPASANGAN_SAH,
    PASANGAN_REKONSILIASI,
    buat_tabel_rekonsiliasi,
    verifikasi_rekonsiliasi,
)


class TestRekonsiliasiGold(unittest.TestCase):
    """Menguji penyandingan 5 pasangan, periode tanpa pasangan, kategori selisih, dan bukti."""

    def test_integrasi_tabel_nasional_nyata_ke_rekonsiliasi(self):
        df = buat_tabel_rekonsiliasi()
        ringkasan = verifikasi_rekonsiliasi(df)

        self.assertEqual(ringkasan["pasangan_rekonsiliasi"], 5)
        self.assertEqual(ringkasan["total_baris"], 80)
        self.assertEqual(ringkasan["baris_berpasangan"], 19)
        self.assertEqual(ringkasan["baris_tanpa_pasangan"], 61)
        self.assertEqual(ringkasan["selisih_median"], 0.711)

        # Pastikan seluruh pasangan P1..P5 hadir dan periode tanpa pasangan tetap tampil (selisih NaN)
        self.assertEqual({spec["pasangan_id"] for spec in PASANGAN_REKONSILIASI}, set(df["pasangan_id"].unique()))
        tanpa_pasangan = df[df["nilai_utama"].isna() | df["nilai_pembanding"].isna()]
        self.assertEqual(len(tanpa_pasangan), 61)
        self.assertTrue(tanpa_pasangan["selisih"].isna().all())
        self.assertTrue((tanpa_pasangan["kategori_selisih"] == "tidak_beririsan").all())

        # Pastikan seluruh 19 baris berpasangan punya kategori sah dan selisih tidak dipaksa nol
        berpasangan = df[df["nilai_utama"].notna() & df["nilai_pembanding"].notna()]
        self.assertTrue(set(berpasangan["kategori_selisih"].unique()).issubset(KATEGORI_BERPASANGAN_SAH))
        self.assertTrue((berpasangan["selisih"].abs() > 0).all())

        # Pastikan baris belum terjelaskan (tahun 2020 pada P1 dan P2) disertai dugaan dan bukti dicari
        belum = berpasangan[berpasangan["kategori_selisih"] == "belum terjelaskan"]
        self.assertEqual(len(belum), 2)
        for teks in belum["penjelasan"]:
            self.assertIn("Dugaan:", teks)
            self.assertIn("Bukti dicari:", teks)

    def test_p4_dan_p5_pekerja_anak_tanpa_tumpang_tindih(self):
        df = buat_tabel_rekonsiliasi()
        p4 = df[df["pasangan_id"] == "P4"]
        p5 = df[df["pasangan_id"] == "P5"]
        self.assertEqual(len(p4), 7)
        self.assertEqual(len(p5), 9)
        self.assertTrue(p4["selisih"].isna().all())
        self.assertTrue(p5["selisih"].isna().all())

    def test_validasi_menolak_belum_terjelaskan_tanpa_bukti(self):
        df = buat_tabel_rekonsiliasi().copy()
        mask = (df["pasangan_id"] == "P1") & (df["periode"] == "2020")
        df.loc[mask, "penjelasan"] = "Belum diketahui penyebabnya."
        with self.assertRaises(AssertionError):
            verifikasi_rekonsiliasi(df)


if __name__ == "__main__":
    unittest.main()
