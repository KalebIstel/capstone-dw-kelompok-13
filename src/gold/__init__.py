"""Tahap 4–6 — Reshape, integrasi, dan penyimpanan ke Gold (pertemuan VII, IX, XI, XII). Milik tim.

Keluaran: data/gold/*.parquet (panel provinsi x tahun x indikator siap analisis, plus tabel
rekonsiliasi dengan pembanding nasional) dan basis data SQL (mis. data/gold/gold.sqlite).
"""
from src.gold.tabel_nasional import simpan_tabel_nasional


def jalankan(silver=None):
    """Terima Silver, tulis tabel Gold (Sprint 1: tabel nasional seri utama & pembanding), kembalikan {nama_tabel: DataFrame}."""
    tabel_nasional = simpan_tabel_nasional()
    return {"tabel_nasional": tabel_nasional}

