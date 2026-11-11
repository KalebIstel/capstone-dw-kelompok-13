"""Pembaca BPS (CSV datar dan JSON WebAPI) -> tabel panjang berlineage.

Tidak ada pembersihan: nilai, nama wilayah, dan kode dibiarkan seperti di sumber.
Satu-satunya konversi: kolom `nilai` dijadikan angka (pemisah desimal di berkas = titik).
"""
import json
from pathlib import Path

import pandas as pd

from src.common.manifest import RAW, sha256_raw

CSV_BPS = [
    "bps/2026-10-17/sdg8_neet.csv",
    "bps/2026-10-17/sdg8_8_7_1_v2658.csv",
]
JSON_BPS = [
    "bps/2026-10-17/json/sdg8_neet.json",
    "bps/2026-10-17/json/sdg8_8_7_1_v2658.json",
]
CATATAN_BPS = ["bps/2026-10-17/manifest_asal.json"]

KOLOM = ["var_id", "wilayah_id", "wilayah", "turvar_id", "turvar", "tahun_id",
         "tahun", "periode_id", "periode", "nilai", "satuan"]


def _lineage(df, berkas, fmt):
    df = df.copy()
    df["_format"] = fmt
    df["_berkas_raw"] = berkas
    df["_sha256_raw"] = sha256_raw(berkas)   # dari MANIFEST.csv, bukan ditulis tangan
    return df


def baca_csv(berkas):
    """CSV datar hasil skrip pengunduh. Semua kolom dibaca sebagai teks agar kode tidak berubah."""
    df = pd.read_csv(RAW / berkas, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    df["nilai"] = pd.to_numeric(df["nilai"], errors="raise")
    return _lineage(df[KOLOM], berkas, "csv")


def baca_json(berkas):
    """JSON WebAPI BPS: daftar halaman, tiap halaman punya daftar kode + datacontent."""
    with open(RAW / berkas, encoding="utf-8") as f:
        halaman = json.load(f)
    if isinstance(halaman, dict):
        halaman = [halaman]

    baris = []
    for i, h in enumerate(halaman):
        dc = h.get("datacontent") or {}
        terpakai = set()
        for v in h.get("var", []):
            for w in h.get("vervar", []):
                for tv in h.get("turvar", []):
                    for t in h.get("tahun", []):
                        for tt in h.get("turtahun", []):
                            kunci = f"{w['val']}{v['val']}{tv['val']}{t['val']}{tt['val']}"
                            if kunci in dc:
                                terpakai.add(kunci)
                                baris.append({
                                    "var_id": str(v["val"]),
                                    "wilayah_id": str(w["val"]), "wilayah": w["label"],
                                    "turvar_id": str(tv["val"]), "turvar": tv["label"],
                                    "tahun_id": str(t["val"]), "tahun": str(t["label"]),
                                    "periode_id": str(tt["val"]), "periode": tt["label"],
                                    "nilai": dc[kunci],
                                    "satuan": v.get("unit"),
                                    "_halaman": i,
                                })
        sisa = set(dc) - terpakai
        if sisa:
            raise ValueError(f"{berkas} halaman {i}: {len(sisa)} kunci datacontent tidak terpetakan, contoh {sorted(sisa)[:3]}")
    df = pd.DataFrame(baris, columns=KOLOM + ["_halaman"])
    df["nilai"] = pd.to_numeric(df["nilai"], errors="raise")
    return _lineage(df, berkas, "json")


def baca_catatan(berkas):
    """manifest_asal.json: metadata unduhan (judul, satuan, waktu). Dibaca untuk uji satuan, bukan masuk tabel nilai."""
    with open(RAW / berkas, encoding="utf-8") as f:
        return json.load(f)


def baca_semua():
    """{berkas: DataFrame} untuk semua CSV dan JSON BPS."""
    hasil = {b: baca_csv(b) for b in CSV_BPS}
    hasil.update({b: baca_json(b) for b in JSON_BPS})
    return hasil