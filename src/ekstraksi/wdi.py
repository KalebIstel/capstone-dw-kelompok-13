"""Pembaca WDI (World Bank, JSON) -> tabel panjang berlineage.

Tidak ada pembersihan: nilai null dibiarkan (menjadi NaN), tahun tetap teks, nama apa adanya.
Satu-satunya penyaringan: pengamatan dan metadata indikator dibatasi ke seri kasus 13
menurut `indicator.id` (berkas data memuat puluhan indikator lain).
"""
import json

import pandas as pd

from src.common.manifest import RAW, sha256_raw

SERI = ["SL.UEM.NEET.ZS", "SL.TLF.0714.ZS"]

DATA_WDI = ["wdi/2026-10-20/data/kelompok-06-hal-01.json"]
META_SUMBER = ["wdi/2026-10-20/metadata/sumber.json"]
META_INDIKATOR = [
    "wdi/2026-10-20/metadata/sumber2_indikator.json",
    "wdi/2026-10-20/metadata/sumber46_indikator.json",
]

KOLOM_DATA = ["indikator_id", "indikator_nama", "negara_id", "negara", "iso3",
              "tahun", "nilai", "unit", "skala", "obs_status", "desimal", "_diperbarui"]
KOLOM_META = ["indikator_id", "nama", "unit", "sumber_id", "sumber_nama",
              "catatan_sumber", "organisasi_sumber"]


def _lineage(df, berkas):
    df = df.copy()
    df["_format"] = "json"
    df["_berkas_raw"] = berkas
    df["_sha256_raw"] = sha256_raw(berkas)   # dari MANIFEST.csv, bukan ditulis tangan
    return df


def _muat(berkas):
    """Berkas WDI = larik dua unsur: [info halaman, daftar isi]."""
    with open(RAW / berkas, encoding="utf-8") as f:
        d = json.load(f)
    if not (isinstance(d, list) and len(d) == 2 and isinstance(d[1], list)):
        raise ValueError(f"{berkas}: bentuk tidak sesuai [info, daftar]")
    return d[0], d[1]


def baca_data(berkas):
    """Pengamatan WDI, disaring ke SERI menurut indicator.id. Nilai null tidak dibuang."""
    info, pengamatan = _muat(berkas)
    baris = []
    for o in pengamatan:
        ind = o["indicator"]
        if ind["id"] not in SERI:
            continue
        baris.append({
            "indikator_id": ind["id"], "indikator_nama": ind["value"],
            "negara_id": o["country"]["id"], "negara": o["country"]["value"],
            "iso3": o.get("countryiso3code"),
            "tahun": str(o["date"]),
            "nilai": o["value"],
            "unit": o.get("unit"), "skala": o.get("scale"),
            "obs_status": o.get("obs_status"), "desimal": o.get("decimal"),
            "_diperbarui": info.get("lastupdated"),
        })
    df = pd.DataFrame(baris, columns=KOLOM_DATA)
    df["nilai"] = pd.to_numeric(df["nilai"], errors="raise")   # None -> NaN
    return _lineage(df, berkas)


def baca_metadata_indikator(berkas):
    """Metadata indikator (nama, satuan, catatan), disaring ke SERI menurut id."""
    _, daftar = _muat(berkas)
    baris = []
    for o in daftar:
        if o["id"] not in SERI:
            continue
        sumber = o.get("source") or {}
        baris.append({
            "indikator_id": o["id"], "nama": o.get("name"), "unit": o.get("unit"),
            "sumber_id": sumber.get("id"), "sumber_nama": sumber.get("value"),
            "catatan_sumber": o.get("sourceNote"),
            "organisasi_sumber": o.get("sourceOrganization"),
        })
    return _lineage(pd.DataFrame(baris, columns=KOLOM_META), berkas)


def baca_metadata_sumber(berkas):
    """Daftar sumber data World Bank (tanpa indicator.id), dibaca utuh."""
    _, daftar = _muat(berkas)
    return _lineage(pd.DataFrame(daftar), berkas)


def baca_semua():
    """{berkas: DataFrame} untuk berkas data WDI (masuk tabel nilai)."""
    return {b: baca_data(b) for b in DATA_WDI}


def baca_metadata_semua():
    """{berkas: DataFrame} untuk berkas metadata WDI (rujukan satuan dan definisi)."""
    hasil = {b: baca_metadata_sumber(b) for b in META_SUMBER}
    hasil.update({b: baca_metadata_indikator(b) for b in META_INDIKATOR})
    return hasil