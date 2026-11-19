r"""Transformasi data mentah hasil ekstraksi menjadi tabel terpadu Silver.

Mengikuti skema baku Silver (11 kolom wajib) dan aturan baku panduan:
- sumber: 'bps', 'wdi', 'ilostat'
- seri_kode: 'var1186', 'var2658', 'SL.TLF.0714.ZS', 'SL.UEM.NEET.ZS', 'SDG_0861_SEX_RT', 'SDG_A871_SEX_AGE_RT', 'SDG_B871_SEX_AGE_RT'
- wilayah_kode: integer (9999 untuk nasional Indonesia, kode BPS x 100 untuk provinsi)
- nama_wilayah: nama provinsi atau 'INDONESIA'
- periode: format 4-digit tahun (^\d{4}$)
- jenis_periode: 'tahun'
- rincian: 'total', 'laki-laki', 'perempuan', '15-17', 'laki-laki_15-17', 'perempuan_15-17'
- nilai: numerik float (tanpa missing value)
- satuan: 'persen'
- _berkas_raw, _sha256_raw: lineage berkas mentah sesuai MANIFEST.csv
"""
from pathlib import Path
import pandas as pd

KOLOM_SILVER = [
    "sumber",
    "seri_kode",
    "wilayah_kode",
    "nama_wilayah",
    "periode",
    "jenis_periode",
    "rincian",
    "nilai",
    "satuan",
    "_berkas_raw",
    "_sha256_raw",
]


def transformasi_bps(df_mentah: pd.DataFrame) -> pd.DataFrame:
    """Transformasi data mentah BPS (CSV dan JSON) ke skema Silver."""
    df = df_mentah.copy()
    
    # Standarisasi seri_kode (contoh: 1186 -> var1186)
    seri_kode = df["var_id"].apply(
        lambda x: f"var{x}" if not str(x).startswith("var") else str(x)
    )
    
    # Wilayah: kode BPS sudah berupa integer (1100 s.d. 9700, 9999)
    wilayah_kode = df["wilayah_id"].astype(int)
    nama_wilayah = df["wilayah"].astype(str)
    
    # Periode dan jenis_periode
    periode = df["tahun"].astype(str)
    jenis_periode = "tahun"
    
    # Rincian: turvar pada BPS tidak ada turunan, mewakili populasi total
    rincian = "total"
    
    # Nilai dan satuan baku
    nilai = pd.to_numeric(df["nilai"], errors="raise")
    satuan = "persen"
    
    hasil = pd.DataFrame({
        "sumber": "bps",
        "seri_kode": seri_kode,
        "wilayah_kode": wilayah_kode,
        "nama_wilayah": nama_wilayah,
        "periode": periode,
        "jenis_periode": jenis_periode,
        "rincian": rincian,
        "nilai": nilai,
        "satuan": satuan,
        "_berkas_raw": df["_berkas_raw"].astype(str),
        "_sha256_raw": df["_sha256_raw"].astype(str),
    })
    return hasil[KOLOM_SILVER]


def transformasi_wdi(df_mentah: pd.DataFrame) -> pd.DataFrame:
    """Transformasi data mentah WDI (JSON) ke skema Silver.
    
    Catatan wrangling: observasi bernilai null disaring keluar karena
    Silver hanya menyimpan observasi yang ada (tidak boleh ada null di kolom nilai).
    """
    df = df_mentah.copy()
    # Saring nilai non-null
    df = df[df["nilai"].notna()].copy()
    
    seri_kode = df["indikator_id"].astype(str)
    wilayah_kode = 9999
    nama_wilayah = "INDONESIA"
    periode = df["tahun"].astype(str)
    jenis_periode = "tahun"
    rincian = "total"
    nilai = pd.to_numeric(df["nilai"], errors="raise")
    satuan = "persen"
    
    hasil = pd.DataFrame({
        "sumber": "wdi",
        "seri_kode": seri_kode,
        "wilayah_kode": wilayah_kode,
        "nama_wilayah": nama_wilayah,
        "periode": periode,
        "jenis_periode": jenis_periode,
        "rincian": rincian,
        "nilai": nilai,
        "satuan": satuan,
        "_berkas_raw": df["_berkas_raw"].astype(str),
        "_sha256_raw": df["_sha256_raw"].astype(str),
    })
    return hasil[KOLOM_SILVER]


def parse_rincian_ilostat(row: pd.Series) -> str:
    """Ekstraksi dan standarisasi rincian demografi jenis kelamin dan umur ILOSTAT."""
    sex_map = {"SEX_T": "total", "SEX_M": "laki-laki", "SEX_F": "perempuan"}
    sex = sex_map.get(row.get("SEX"), str(row.get("SEX")).lower())
    age = str(row.get("AGE"))
    if pd.isna(row.get("AGE")) or age in ("nan", "None", ""):
        return sex
    if "Y15-17" in age or "15-17" in age:
        return f"{sex}_15-17" if sex != "total" else "15-17"
    return f"{sex}_{age}"


def parse_seri_ilostat(dataflow: str) -> str:
    """Ekstraksi seri_kode dari ID DATAFLOW ILOSTAT."""
    s = str(dataflow)
    if "DF_" in s:
        s = s.split("DF_")[1]
    if "(" in s:
        s = s.split("(")[0]
    return s


def transformasi_ilostat(df_mentah: pd.DataFrame) -> pd.DataFrame:
    """Transformasi data mentah ILOSTAT (SDMX-CSV) ke skema Silver."""
    df = df_mentah.copy()
    df = df[df["OBS_VALUE"].notna()].copy()
    
    seri_kode = df["DATAFLOW"].apply(parse_seri_ilostat)
    wilayah_kode = 9999
    nama_wilayah = "INDONESIA"
    periode = df["TIME_PERIOD"].astype(str)
    jenis_periode = "tahun"
    rincian = df.apply(parse_rincian_ilostat, axis=1)
    nilai = pd.to_numeric(df["OBS_VALUE"], errors="raise")
    satuan = "persen"
    
    hasil = pd.DataFrame({
        "sumber": "ilostat",
        "seri_kode": seri_kode,
        "wilayah_kode": wilayah_kode,
        "nama_wilayah": nama_wilayah,
        "periode": periode,
        "jenis_periode": jenis_periode,
        "rincian": rincian,
        "nilai": nilai,
        "satuan": satuan,
        "_berkas_raw": df["_berkas_raw"].astype(str),
        "_sha256_raw": df["_sha256_raw"].astype(str),
    })
    return hasil[KOLOM_SILVER]


def susun_silver(mentah: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Gabungkan hasil ekstraksi BPS, WDI, dan ILOSTAT ke dalam tabel Silver terpadu."""
    tabel_bps = transformasi_bps(mentah["bps"])
    tabel_wdi = transformasi_wdi(mentah["wdi"])
    tabel_ilo = transformasi_ilostat(mentah["ilostat"])
    
    df_silver = pd.concat([tabel_bps, tabel_wdi, tabel_ilo], ignore_index=True)
    return df_silver
