# src/silver/bangun.py
import json
import os
from pathlib import Path

import pandas as pd

from src.common.manifest import sha256_raw
from src.silver.metadata import SERI_META

RAW = Path("data/raw")

KOLOM = ["sumber", "seri_kode", "wilayah_kode", "nama_wilayah", "periode",
         "jenis_periode", "rincian", "nilai", "satuan", "_berkas_raw", "_sha256_raw"]

PROV_38 = {11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 31, 32, 33, 34, 35, 36,
           51, 52, 53, 61, 62, 63, 64, 65, 71, 72, 73, 74, 75, 76, 81, 82,
           91, 92, 94, 95, 96, 97}

SEX = {"SEX_T": "total", "SEX_M": "laki-laki", "SEX_F": "perempuan"}


def _lineage(df, berkas):
    df = df.copy()
    df["_berkas_raw"] = berkas
    df["_sha256_raw"] = sha256_raw(berkas)
    return df


def kode_wilayah(k):
    k = int(k)
    if k in (0, 9999):
        return 9999
    if k < 100:
        k *= 100
    return k if (k // 100) in PROV_38 else None


def bps_csv(berkas, var_id):
    d = pd.read_csv(RAW / berkas, dtype=str)
    mentah = len(d)
    d = d[d["var_id"] == var_id]
    assert set(d["periode"]) == {"Tahun"}, f"periode non-tahunan: {set(d['periode'])}"
    d = _lineage(d, berkas)
    out = pd.DataFrame({
        "sumber": "BPS",
        "seri_kode": "var" + var_id,
        "wilayah_kode": d["wilayah_id"].map(kode_wilayah),
        "nama_wilayah": d["wilayah"],
        "periode": d["tahun"],
        "jenis_periode": "tahun",
        "rincian": d["turvar"].str.strip().str.lower().replace({"tidak ada": "total"}),
        "nilai": pd.to_numeric(d["nilai"], errors="coerce"),
        "satuan": "persen",
        "catatan": "",
        "_berkas_raw": d["_berkas_raw"],
        "_sha256_raw": d["_sha256_raw"],
    })
    return out, mentah


def ilo_csv(berkas):
    d = pd.read_csv(RAW / berkas, dtype=str)
    mentah = len(d)
    d = _lineage(d, berkas)
    rincian = d["SEX"].map(SEX).fillna(d["SEX"])
    if "AGE" in d.columns:
        rincian = rincian + "_" + d["AGE"].str.split("_Y").str[-1]
    out = pd.DataFrame({
        "sumber": "ILOSTAT",
        "seri_kode": d["DATAFLOW"].str.extract(r"DF_(.+?)\(")[0],
        "wilayah_kode": 9999,
        "nama_wilayah": "Indonesia",
        "periode": d["TIME_PERIOD"],
        "jenis_periode": "tahun",
        "rincian": rincian,
        "nilai": pd.to_numeric(d["OBS_VALUE"], errors="coerce"),
        "satuan": "persen",
        "catatan": d["OBS_STATUS"].map(lambda v: "" if pd.isna(v) else f"patahan_seri_{v}"),
        "_berkas_raw": d["_berkas_raw"],
        "_sha256_raw": d["_sha256_raw"],
    })
    return out, mentah


def wdi_json(berkas, seri):
    meta, obs = json.load(open(RAW / berkas, encoding="utf-8"))
    mentah = len(obs)
    baris = [{"seri_kode": o["indicator"]["id"], "periode": str(o["date"]),
              "nilai": o["value"]}
             for o in obs
             if o["indicator"]["id"] in seri and o.get("countryiso3code") == "IDN"]
    d = _lineage(pd.DataFrame(baris), berkas)
    out = pd.DataFrame({
        "sumber": "WDI",
        "seri_kode": d["seri_kode"],
        "wilayah_kode": 9999,
        "nama_wilayah": "Indonesia",
        "periode": d["periode"],
        "jenis_periode": "tahun",
        "rincian": d["seri_kode"].map({"SL.UEM.NEET.ZS": "total", "SL.TLF.0714.ZS": "total"}),
        "nilai": pd.to_numeric(d["nilai"], errors="coerce"),
        "satuan": "persen",
        "catatan": "",
        "_berkas_raw": d["_berkas_raw"],
        "_sha256_raw": d["_sha256_raw"],
    })
    return out, mentah


def bangun_silver():
    pekerjaan = [
        bps_csv("bps/2026-10-17/sdg8_neet.csv", "1186"),
        bps_csv("bps/2026-10-17/sdg8_8_7_1_v2658.csv", "2658"),
        ilo_csv("ilostat/2026-10-20/data/DF_SDG_0861_SEX_RT.csv"),
        ilo_csv("ilostat/2026-10-20/data/DF_SDG_A871_SEX_AGE_RT.csv"),
        ilo_csv("ilostat/2026-10-20/data/DF_SDG_B871_SEX_AGE_RT.csv"),
        wdi_json("wdi/2026-10-20/data/kelompok-06-hal-01.json",
                 {"SL.UEM.NEET.ZS", "SL.TLF.0714.ZS"}),
    ]
    s = pd.concat([p[0] for p in pekerjaan], ignore_index=True)
    baris_mentah = sum(p[1] for p in pekerjaan)
    n0 = len(s)

    tak_terdaftar = set(s["seri_kode"]) - set(SERI_META)
    assert not tak_terdaftar, f"seri belum ada di metadata: {tak_terdaftar}"
    s["satuan"] = s["seri_kode"].map(lambda k: SERI_META[k]["satuan"])
    s["jenis_periode"] = s["seri_kode"].map(lambda k: SERI_META[k]["periode"])

    wil_salah = s["wilayah_kode"].isna().sum()
    kosong = s["nilai"].isna().sum()
    print(f"berkas=6 baris_mentah={baris_mentah} baris_disaring={n0}")
    print(f"wilayah di luar 38 provinsi: {wil_salah} | nilai kosong: {kosong}")

    s = s.dropna(subset=["nilai", "wilayah_kode"]).copy()
    s["wilayah_kode"] = s["wilayah_kode"].astype(int)
    s["nilai"] = s["nilai"].astype(float)

    kunci = ["sumber", "seri_kode", "wilayah_kode", "periode", "rincian", "_berkas_raw"]
    kembar = s.duplicated(kunci).sum()
    print(f"baris kembar pada kunci: {kembar}")
    if kembar:
        print(s[s.duplicated(kunci, keep=False)].sort_values(kunci).head(10))
        raise SystemExit("Ada kunci kembar: putuskan aturannya, catat di log.")

    print(f"baris_silver={len(s)}")
    return s[KOLOM + ["catatan"]].reset_index(drop=True)


if __name__ == "__main__":
    os.makedirs("data/silver", exist_ok=True)
    bangun_silver().to_parquet("data/silver/silver.parquet", index=False)