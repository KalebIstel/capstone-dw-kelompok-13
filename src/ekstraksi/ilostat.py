"""Pembaca ILOSTAT (SDMX-CSV, DSD JSON, dataflow JSON) -> tabel panjang berlineage.

Tidak ada pembersihan: semua kolom CSV dipertahankan (termasuk OBS_STATUS, NOTE_*, SOURCE),
kode dimensi (SEX, AGE) tidak diterjemahkan. Satu-satunya konversi: OBS_VALUE dijadikan angka.
DSD hanya merujuk daftar kode (codelist) dan tidak memuat isinya, jadi rujukan itu dicatat apa adanya.
"""
import json

import pandas as pd

from src.common.manifest import RAW, sha256_raw

CSV_ILO = [
    "ilostat/2026-10-20/data/DF_SDG_0861_SEX_RT.csv",
    "ilostat/2026-10-20/data/DF_SDG_A871_SEX_AGE_RT.csv",
    "ilostat/2026-10-20/data/DF_SDG_B871_SEX_AGE_RT.csv",
]
DSD_ILO = [
    "ilostat/2026-10-20/dsd/SDG_0861_SEX_RT.json",
    "ilostat/2026-10-20/dsd/SDG_A871_SEX_AGE_RT.json",
    "ilostat/2026-10-20/dsd/SDG_B871_SEX_AGE_RT.json",
]
DATAFLOW_ILO = ["ilostat/2026-10-20/metadata/dataflow.json"]
ID_DATAFLOW = ["DF_SDG_0861_SEX_RT", "DF_SDG_A871_SEX_AGE_RT", "DF_SDG_B871_SEX_AGE_RT"]

KOLOM_CSV = ["DATAFLOW", "REF_AREA", "FREQ", "MEASURE", "SEX", "AGE", "TIME_PERIOD",
             "OBS_VALUE", "OBS_STATUS", "UNIT_MEASURE_TYPE", "UNIT_MEASURE", "UNIT_MULT",
             "SOURCE", "NOTE_SOURCE", "NOTE_INDICATOR", "NOTE_CLASSIF", "DECIMALS",
             "UPPER_BOUND", "LOWER_BOUND"]


def _lineage(df, berkas, fmt):
    df = df.copy()
    df["_format"] = fmt
    df["_berkas_raw"] = berkas
    df["_sha256_raw"] = sha256_raw(berkas)   # dari MANIFEST.csv, bukan ditulis tangan
    return df


def _json(berkas):
    with open(RAW / berkas, encoding="utf-8") as f:
        return json.load(f)


def baca_csv(berkas):
    """CSV SDMX apa adanya. Semua kolom teks; kolom AGE tidak ada di 0861 (dibiarkan kosong)."""
    df = pd.read_csv(RAW / berkas, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    tak_dikenal = set(df.columns) - set(KOLOM_CSV)
    if tak_dikenal:
        raise ValueError(f"{berkas}: kolom tak dikenal {sorted(tak_dikenal)}")
    df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="raise")
    return _lineage(df.reindex(columns=KOLOM_CSV), berkas, "csv")


def baca_dsd(berkas):
    """DSD: daftar komponen (dimensi, waktu, atribut, ukuran) beserta rujukan codelist-nya."""
    s = _json(berkas)["data"]["dataStructures"][0]
    komp = s["dataStructureComponents"]
    baris = []

    def tambah(jenis, daftar):
        if isinstance(daftar, dict):
            daftar = [daftar]
        for a in daftar or []:
            enum = (a.get("localRepresentation") or {}).get("enumeration")
            baris.append({
                "dsd_id": s["id"], "dsd_versi": s.get("version"),
                "dsd_nama": s.get("name"), "dsd_deskripsi": s.get("description"),
                "jenis_komponen": jenis, "komponen_id": a.get("id"),
                "codelist": enum.split("=")[-1] if enum else None,
            })

    dim = komp.get("dimensionList") or {}
    tambah("dimensi", dim.get("dimensions"))
    tambah("waktu", dim.get("timeDimensions"))
    tambah("atribut", (komp.get("attributeList") or {}).get("attributes"))
    tambah("ukuran", (komp.get("measureList") or {}).get("primaryMeasure"))
    return _lineage(pd.DataFrame(baris), berkas, "json")


def baca_dataflow(berkas):
    """Metadata dataflow, disaring ke tiga seri kasus 13 menurut id."""
    baris = []
    for o in _json(berkas)["data"]["dataflows"]:
        if o["id"] not in ID_DATAFLOW:
            continue
        baris.append({
            "dataflow_id": o["id"], "versi": o.get("version"), "agen": o.get("agencyID"),
            "nama": o.get("name"), "deskripsi": o.get("description"),
            "struktur": o.get("structure"),
        })
    return _lineage(pd.DataFrame(baris), berkas, "json")


def baca_semua():
    """{berkas: DataFrame} untuk CSV ILOSTAT (masuk tabel nilai)."""
    return {b: baca_csv(b) for b in CSV_ILO}


def baca_metadata_semua():
    """{berkas: DataFrame} untuk DSD dan dataflow (rujukan definisi dan kode)."""
    hasil = {b: baca_dsd(b) for b in DSD_ILO}
    hasil.update({b: baca_dataflow(b) for b in DATAFLOW_ILO})
    return hasil