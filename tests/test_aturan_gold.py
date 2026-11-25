"""Pengujian otomatis aturan satu nilai per sel Gold (Kartu #20, Tahap 4)."""
from pathlib import Path
import sys
import unittest

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.gold.aturan_gold import (
    KUNCI_PANEL_GOLD,
    KUNCI_PANEL_INDIKATOR,
    bangun_panel_gold,
    pilih_rincian_dan_cakupan,
    pilih_snapshot,
    seragamkan_satuan_per_indikator,
    tangani_periode_subtahunan,
    verifikasi_ketertelusuran_silver,
)


def _buat_baris(**override) -> dict:
    dasar = {
        "sumber": "bps",
        "seri_kode": "var1186",
        "wilayah_kode": 1100,
        "nama_wilayah": "ACEH",
        "periode": "2023",
        "jenis_periode": "tahun",
        "rincian": "total",
        "nilai": 20.0,
        "satuan": "persen",
        "_berkas_raw": "bps/2026-10-17/sdg8_neet.csv",
        "_sha256_raw": "a" * 64,
    }
    dasar.update(override)
    return dasar


class TestAturanGold(unittest.TestCase):
    def test_pilih_snapshot_terbaru_menang_bila_angka_berbeda(self):
        df = pd.DataFrame([
            _buat_baris(nilai=20.1, _berkas_raw="bps/2026-10-10/sdg8_neet.csv"),
            _buat_baris(nilai=21.5, _berkas_raw="bps/2026-10-17/json/sdg8_neet.json"),
        ])
        hasil, ringkasan = pilih_snapshot(df)
        self.assertEqual(len(hasil), 1)
        self.assertEqual(hasil.loc[0, "nilai"], 21.5)
        self.assertEqual(hasil.loc[0, "snapshot_tanggal"], "2026-10-17")
        self.assertEqual(ringkasan["baris_tidak_terpilih"], 1)
        self.assertEqual(ringkasan["kunci_nilai_berbeda"], 1)

    def test_pilih_snapshot_prioritaskan_csv_pada_tanggal_sama(self):
        df = pd.DataFrame([
            _buat_baris(nilai=22.25, _berkas_raw="bps/2026-10-17/json/sdg8_neet.json"),
            _buat_baris(nilai=22.25, _berkas_raw="bps/2026-10-17/sdg8_neet.csv"),
        ])
        hasil, ringkasan = pilih_snapshot(df)
        self.assertEqual(len(hasil), 1)
        self.assertTrue(hasil.loc[0, "_berkas_raw"].endswith(".csv"))
        self.assertEqual(ringkasan["baris_tidak_terpilih"], 1)
        self.assertEqual(ringkasan["kunci_tanggal_sama_nilai_berbeda"], 0)

    def test_tangani_periode_subtahunan_semester_dan_bulan(self):
        df = pd.DataFrame([
            # Provinsi 1100 hanya punya semesteran -> ambil S2 (terakhir)
            _buat_baris(wilayah_kode=1100, periode="2020-S1", jenis_periode="semester", nilai=19.0),
            _buat_baris(wilayah_kode=1100, periode="2020-S2", jenis_periode="semester", nilai=21.0),
            # Provinsi 1200 punya bulanan dan tahunan asli -> tahunan asli menang
            _buat_baris(wilayah_kode=1200, periode="2020-02", jenis_periode="bulan", nilai=18.0),
            _buat_baris(wilayah_kode=1200, periode="2020-08", jenis_periode="bulan", nilai=23.0),
            _buat_baris(wilayah_kode=1200, periode="2020", jenis_periode="tahun", nilai=22.5),
            # Provinsi 1300 hanya punya bulanan -> ambil bulan terakhir (08 > 02)
            _buat_baris(wilayah_kode=1300, periode="2020-02", jenis_periode="bulan", nilai=15.0),
            _buat_baris(wilayah_kode=1300, periode="2020-08", jenis_periode="bulan", nilai=16.5),
        ])
        df_snap, _ = pilih_snapshot(df)
        hasil, ringkasan = tangani_periode_subtahunan(df_snap)
        self.assertEqual(len(hasil), 3)
        self.assertEqual(ringkasan["baris_tidak_terpilih"], 4)
        self.assertTrue((hasil["jenis_periode"] == "tahun").all())
        nilai_per_wilayah = dict(zip(hasil["wilayah_kode"], hasil["nilai"]))
        self.assertEqual(nilai_per_wilayah[1100], 21.0)
        self.assertEqual(nilai_per_wilayah[1200], 22.5)
        self.assertEqual(nilai_per_wilayah[1300], 16.5)

    def test_pilih_rincian_dan_cakupan_saring_nasional_dan_disagregasi(self):
        df = pd.DataFrame([
            _buat_baris(wilayah_kode=1100, rincian="total", nilai=20.0),
            _buat_baris(wilayah_kode=1100, rincian="laki-laki", nilai=19.0),
            _buat_baris(wilayah_kode=9999, nama_wilayah="INDONESIA", rincian="total", nilai=22.0),
            _buat_baris(
                sumber="ilostat",
                seri_kode="SDG_0861_SEX_RT",
                wilayah_kode=9999,
                nama_wilayah="INDONESIA",
                rincian="perempuan",
                nilai=24.0,
            ),
        ])
        prov, nas, ringkasan = pilih_rincian_dan_cakupan(df)
        self.assertEqual(len(prov), 1)
        self.assertEqual(prov.loc[0, "wilayah_kode"], 1100)
        self.assertEqual(len(nas), 2)
        self.assertEqual(ringkasan["baris_tidak_masuk_panel"], 3)

    def test_integrasi_silver_nyata_ke_panel_gold(self):
        silver_path = ROOT / "data/silver/silver.parquet"
        if not silver_path.exists():
            self.skipTest("data/silver/silver.parquet belum tersedia")

        panel, ringkasan = bangun_panel_gold(silver_path=silver_path, simpan=False)

        # Total sel: 418 (var1186: 11 tahun x 38) + 228 (var2658: 6 tahun x 38) = 646
        self.assertEqual(len(panel), 646)
        self.assertEqual(int(panel.duplicated(KUNCI_PANEL_GOLD).sum()), 0)

        # Rekonsiliasi baris Silver yang tidak terpilih
        self.assertEqual(ringkasan["snapshot"]["baris_masuk"], 1325)
        self.assertEqual(ringkasan["snapshot"]["baris_tidak_terpilih"], 605)
        self.assertEqual(ringkasan["periode"]["baris_tidak_terpilih"], 0)
        self.assertEqual(ringkasan["cakupan"]["baris_tidak_masuk_panel"], 132)
        self.assertEqual(ringkasan["cakupan"]["baris_panel_provinsi"], 588)

        # Status sel kosong K-006
        status_counts = panel["status_data"].value_counts().to_dict()
        self.assertEqual(status_counts["tersedia"], 588)
        self.assertEqual(status_counts["belum_terbentuk"], 36)
        self.assertEqual(status_counts["masa_transisi"], 8)
        self.assertEqual(status_counts["missing"], 14)

        # Penanda anomali Sprint 1 terbawa penuh tanpa dihapus
        anom_counts = panel["penanda_anomali"].value_counts(dropna=True).to_dict()
        self.assertEqual(anom_counts["outlier_asli"], 23)
        self.assertEqual(anom_counts["patahan_diduga"], 6)

    def test_seragamkan_satuan_dan_tolak_satuan_campur(self):
        df_valid = pd.DataFrame([
            _buat_baris(seri_kode="var1186", satuan="Persen"),
            _buat_baris(seri_kode="var2658", satuan="PT"),
        ])
        hasil = seragamkan_satuan_per_indikator(df_valid)
        self.assertEqual(set(hasil["satuan"]), {"persen"})

        df_campur = pd.DataFrame([
            _buat_baris(seri_kode="var1186", satuan="persen"),
            _buat_baris(seri_kode="var2658", satuan="orang"),
        ])
        with self.assertRaises(ValueError):
            seragamkan_satuan_per_indikator(df_campur)

    def test_ketertelusuran_dan_kunci_indikator_panel(self):
        silver_path = ROOT / "data/silver/silver.parquet"
        if not silver_path.exists():
            self.skipTest("data/silver/silver.parquet belum tersedia")

        df_silver = pd.read_parquet(silver_path)
        panel, ringkasan = bangun_panel_gold(df_silver=df_silver, simpan=False)
        self.assertEqual(int(panel.duplicated(KUNCI_PANEL_INDIKATOR).sum()), 0)
        self.assertEqual(ringkasan["ketertelusuran"]["sel_terisi"], 588)
        self.assertEqual(ringkasan["ketertelusuran"]["sel_tertelusur"], 588)

        jejak = verifikasi_ketertelusuran_silver(panel, df_silver)
        self.assertEqual(jejak["sel_kosong"], 58)


if __name__ == "__main__":
    unittest.main()
