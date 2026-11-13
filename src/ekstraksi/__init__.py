"""Tahap 1 — Ekstraksi (pertemuan X). Milik tim.

Baca setiap berkas di data/raw/ (CSV, JSON WebAPI BPS, XLSX BNPB, SDMX ILO, JSON WDI) menjadi
DataFrame mentah yang setia pada sumbernya: jangan membersihkan di sini, cukup ratakan struktur
dan catat asal tiap baris (`_berkas_raw` relatif data/raw/, `_sha256_raw` dari src.common.manifest).
"""
import pandas as pd

from src.ekstraksi import bps, wdi


def jalankan():
    """Kembalikan {nama_sumber: DataFrame mentah}."""
    return {
        "bps": pd.concat(bps.baca_semua().values(), ignore_index=True),
        "wdi": pd.concat(wdi.baca_semua().values(), ignore_index=True),
    }