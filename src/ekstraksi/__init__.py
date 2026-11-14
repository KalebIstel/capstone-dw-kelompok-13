"""Tahap 1 — Ekstraksi (pertemuan X). Milik tim.

Baca setiap berkas di data/raw/ (CSV, JSON WebAPI BPS, XLSX BNPB, SDMX ILO, JSON WDI) menjadi
DataFrame mentah yang setia pada sumbernya: jangan membersihkan di sini, cukup ratakan struktur
dan catat asal tiap baris (`_berkas_raw` relatif data/raw/, `_sha256_raw` dari src.common.manifest).

jalankan() mengembalikan tabel NILAI per sumber (bentuk yang dipakai tahap Silver).
Metadata (catatan unduhan BPS, metadata WDI, DSD dan dataflow ILO) dibaca lewat baca_metadata().
periksa_cakupan() memastikan setiap berkas di MANIFEST.csv terbaca oleh salah satu pembaca.
"""
import json

import pandas as pd

from src.common.manifest import baca, sha256_raw
from src.ekstraksi import bps, ilostat, wdi

SUMBER = ("bps", "wdi", "ilostat")


def _catatan_bps():
    """manifest_asal.json dibungkus 1 baris berlineage (isi JSON utuh sebagai teks)."""
    hasil = {}
    for b in bps.CATATAN_BPS:
        df = pd.DataFrame([{"isi_json": json.dumps(bps.baca_catatan(b), ensure_ascii=False)}])
        df["_format"] = "json"
        df["_berkas_raw"] = b
        df["_sha256_raw"] = sha256_raw(b)
        hasil[b] = df
    return hasil


def baca_nilai():
    """{berkas: DataFrame} untuk 8 berkas yang memuat nilai (BPS 4, WDI 1, ILOSTAT 3)."""
    return {**bps.baca_semua(), **wdi.baca_semua(), **ilostat.baca_semua()}


def baca_metadata():
    """{berkas: DataFrame} untuk 8 berkas metadata (BPS 1, WDI 3, ILOSTAT 4)."""
    return {**_catatan_bps(), **wdi.baca_metadata_semua(), **ilostat.baca_metadata_semua()}


def periksa_cakupan(*kumpulan):
    """Cocokkan berkas yang terbaca dengan MANIFEST.csv. Galat bila ada yang terlewat atau asing."""
    terbaca = set()
    for k in kumpulan:
        for df in k.values():
            terbaca |= set(df["_berkas_raw"].unique())
    manifest = set(baca())
    terlewat, asing = sorted(manifest - terbaca), sorted(terbaca - manifest)
    if terlewat or asing:
        raise ValueError(f"cakupan ekstraksi tidak cocok dengan MANIFEST.csv: terlewat={terlewat}, asing={asing}")
    return len(terbaca)


def jalankan():
    """Kembalikan {nama_sumber: DataFrame mentah} untuk tabel nilai; cakupan 16 berkas diperiksa."""
    nilai = baca_nilai()
    periksa_cakupan(nilai, baca_metadata())
    return {s: pd.concat([df for b, df in nilai.items() if b.split("/")[0] == s], ignore_index=True)
            for s in SUMBER}