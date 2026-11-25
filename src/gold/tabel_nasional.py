"""Penyusun tabel nasional Gold (satu baris per periode x seri) dan laporan wide pembanding.

Tahap 6 (persiapan integrasi Kasus 13 — Kartu #22):
- Memuat seluruh 7 seri Kasus 13 pada tingkat nasional (wilayah_kode=9999):
  2 seri utama BPS (var1186, var2658) dan 5 seri pembanding global
  (SDG_0861_SEX_RT, SDG_A871_SEX_AGE_RT, SDG_B871_SEX_AGE_RT, SL.UEM.NEET.ZS, SL.TLF.0714.ZS).
- Menerapkan aturan snapshot terbaru/format CSV > JSON serta konsolidasi periode
  dari src.gold.aturan_gold tanpa duplikasi logika.
- Menyaring rincian agregat nasional ('total' atau '15-17' pada A871/B871) agar kunci
  (periode, seri_kode) unik tepat satu baris per periode x seri.
- Menandai asal setiap angka nasional pada kolom 'asal_angka' ('baris_indonesia',
  'agregat_provinsi', atau 'pembanding') dan mewajibkan lineage _berkas_raw serta
  _sha256_raw di setiap baris.
- Aturan seri utama tanpa baris Indonesia: karena indikator persentase NEET dan pekerja
  anak bersifat non-aditif tanpa penimbang populasi mikro Sakernas (K-001, K-018, K-023),
  pipeline menolak agregat provinsi tanpa bobot dan menyatakan tidak ada padanan nasional
  otomatis bila suatu seri utama tidak menerbitkan baris wilayah_kode=9999.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd

from src.gold.aturan_gold import (
    pilih_snapshot,
    seragamkan_satuan_per_indikator,
    tangani_periode_subtahunan,
)

ROOT = Path(__file__).resolve().parents[2]
SILVER_PATH = ROOT / "data/silver/silver.parquet"
OUTPUT_CSV = ROOT / "reports/tabel_nasional_periode_seri.csv"
OUTPUT_PARQUET = ROOT / "data/gold/tabel_nasional.parquet"

KUNCI_TABEL_NASIONAL = ["periode", "seri_kode"]
ASAL_ANGKA_SAH = {"baris_indonesia", "agregat_provinsi", "pembanding"}

METADATA_SERI_NASIONAL = {
    "var1186": {
        "topik": "neet",
        "indikator": "neet_15_24",
        "peran_seri": "utama",
        "kelompok_umur": "15-24",
        "rincian_agregat": "total",
        "asal_angka": "baris_indonesia",
    },
    "var2658": {
        "topik": "pekerja_anak",
        "indikator": "pekerja_anak_5_17",
        "peran_seri": "utama",
        "kelompok_umur": "5-17",
        "rincian_agregat": "total",
        "asal_angka": "baris_indonesia",
    },
    "SDG_0861_SEX_RT": {
        "topik": "neet",
        "indikator": "neet_15_24",
        "peran_seri": "pembanding",
        "kelompok_umur": "15-24",
        "rincian_agregat": "total",
        "asal_angka": "pembanding",
    },
    "SL.UEM.NEET.ZS": {
        "topik": "neet",
        "indikator": "neet_15_24",
        "peran_seri": "pembanding",
        "kelompok_umur": "15-24",
        "rincian_agregat": "total",
        "asal_angka": "pembanding",
    },
    "SDG_A871_SEX_AGE_RT": {
        "topik": "pekerja_anak",
        "indikator": "pekerja_anak_15_17",
        "peran_seri": "pembanding",
        "kelompok_umur": "15-17",
        "rincian_agregat": "15-17",
        "asal_angka": "pembanding",
    },
    "SDG_B871_SEX_AGE_RT": {
        "topik": "pekerja_anak",
        "indikator": "pekerja_anak_15_17",
        "peran_seri": "pembanding",
        "kelompok_umur": "15-17",
        "rincian_agregat": "15-17",
        "asal_angka": "pembanding",
    },
    "SL.TLF.0714.ZS": {
        "topik": "pekerja_anak",
        "indikator": "pekerja_anak_7_14",
        "peran_seri": "pembanding",
        "kelompok_umur": "7-14",
        "rincian_agregat": "total",
        "asal_angka": "pembanding",
    },
}

SERI_UTAMA = tuple(
    kode for kode, meta in METADATA_SERI_NASIONAL.items() if meta["peran_seri"] == "utama"
)

KOLOM_TABEL_NASIONAL = [
    "periode",
    "seri_kode",
    "topik",
    "indikator",
    "peran_seri",
    "asal_angka",
    "sumber",
    "wilayah_kode",
    "nama_wilayah",
    "rincian",
    "kelompok_umur",
    "nilai",
    "satuan",
    "snapshot_tanggal",
    "_berkas_raw",
    "_sha256_raw",
]


def _muat_silver(
    silver_path: Path = SILVER_PATH,
    df_silver: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Muat tabel Silver dari DataFrame memori atau berkas Parquet."""
    if df_silver is not None:
        return df_silver
    if not silver_path.exists():
        raise FileNotFoundError(f"Berkas Silver tidak ditemukan: {silver_path}")
    return pd.read_parquet(silver_path)


def _terapkan_aturan_dasar(df_silver: pd.DataFrame) -> pd.DataFrame:
    """Jalankan pemilihan snapshot, konsolidasi periode tahunan, dan penyeragaman satuan."""
    df_snap, _ = pilih_snapshot(df_silver)
    df_tahunan, _ = tangani_periode_subtahunan(df_snap)
    return seragamkan_satuan_per_indikator(df_tahunan)


def buat_tabel_nasional(
    silver_path: Path = SILVER_PATH,
    df_silver: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Bentuk tabel nasional Gold rapi (satu baris per periode x seri) beserta asal_angka dan lineage."""
    df = _muat_silver(silver_path=silver_path, df_silver=df_silver)
    df_bersih = _terapkan_aturan_dasar(df)

    tak_dikenal = set(df_bersih["seri_kode"].unique()) - set(METADATA_SERI_NASIONAL)
    if tak_dikenal:
        raise ValueError(f"Ditemukan seri_kode tidak terdaftar pada tabel nasional: {sorted(tak_dikenal)}")

    nasional_semua = df_bersih[df_bersih["wilayah_kode"] == 9999].copy()

    # Pastikan seri utama yang hadir di Silver memiliki baris Indonesia eksplisit (wilayah_kode=9999).
    seri_di_silver = set(df_bersih["seri_kode"].unique())
    for seri_utama in SERI_UTAMA:
        if seri_utama not in seri_di_silver:
            continue
        rincian_wajib = METADATA_SERI_NASIONAL[seri_utama]["rincian_agregat"]
        ada_indonesia = (
            (nasional_semua["seri_kode"] == seri_utama)
            & (nasional_semua["rincian"] == rincian_wajib)
        ).any()
        if not ada_indonesia:
            raise ValueError(
                f"Seri utama '{seri_utama}' tidak menerbitkan baris Indonesia (wilayah_kode=9999, "
                f"rincian='{rincian_wajib}'). Sesuai aturan K-001/K-018/K-023, agregat provinsi tanpa "
                "bobot populasi mikro Sakernas ditolak karena persentase bersifat non-aditif."
            )

    mask_agregat = nasional_semua.apply(
        lambda row: row["rincian"] == METADATA_SERI_NASIONAL[row["seri_kode"]]["rincian_agregat"],
        axis=1,
    )
    nasional = nasional_semua[mask_agregat].copy()

    for kolom_meta in ("topik", "indikator", "peran_seri", "kelompok_umur", "asal_angka"):
        nasional[kolom_meta] = nasional["seri_kode"].map(
            lambda s, k=kolom_meta: METADATA_SERI_NASIONAL[s][k]
        )

    urutan_peran = {"utama": 0, "pembanding": 1}
    nasional["_urutan_peran"] = nasional["peran_seri"].map(urutan_peran)
    nasional = (
        nasional.sort_values(
            by=["periode", "topik", "_urutan_peran", "seri_kode"],
            kind="mergesort",
        )
        .drop(columns=["_urutan_peran"])
        .reset_index(drop=True)
    )
    return nasional[KOLOM_TABEL_NASIONAL]


def buat_tabel_nasional_wide(
    silver_path: Path = SILVER_PATH,
    df_silver: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Bentuk tabel pivot lebar (periode x seri/rincian) untuk inspeksi manusia di reports/."""
    df = _muat_silver(silver_path=silver_path, df_silver=df_silver)
    df_bersih = _terapkan_aturan_dasar(df)
    nasional = df_bersih[df_bersih["wilayah_kode"] == 9999].copy()

    nasional["kolom_analitis"] = [
        f"{seri} ({rincian})" for seri, rincian in zip(nasional["seri_kode"], nasional["rincian"])
    ]
    pivot = nasional.pivot(
        index="periode",
        columns="kolom_analitis",
        values="nilai",
    ).sort_index()
    pivot = pivot.reset_index()
    pivot.columns.name = None
    return pivot


def verifikasi_tabel_nasional(
    tabel: pd.DataFrame,
    df_silver: pd.DataFrame,
    wajib_lengkap_7_seri: bool = True,
) -> dict:
    """Verifikasi keunikan (periode, seri_kode), kelengkapan asal_angka, dan ketertelusuran Silver."""
    duplikat = int(tabel.duplicated(KUNCI_TABEL_NASIONAL).sum())
    if duplikat:
        raise AssertionError(
            f"Tabel nasional Gold melanggar keunikan kunci {KUNCI_TABEL_NASIONAL}: {duplikat} duplikat"
        )

    if wajib_lengkap_7_seri:
        seri_ada = set(tabel["seri_kode"].unique())
        seri_wajib = set(METADATA_SERI_NASIONAL)
        if seri_ada != seri_wajib:
            raise AssertionError(
                f"Daftar seri tabel nasional tidak lengkap: kurang {sorted(seri_wajib - seri_ada)}"
            )

    asal_tidak_sah = set(tabel["asal_angka"].dropna().unique()) - ASAL_ANGKA_SAH
    if tabel["asal_angka"].isna().any() or asal_tidak_sah:
        raise AssertionError(f"Nilai asal_angka tidak sah pada tabel nasional: {sorted(asal_tidak_sah)}")

    for kolom_wajib in ("nilai", "_berkas_raw", "_sha256_raw"):
        if tabel[kolom_wajib].isna().any():
            raise AssertionError(f"Ditemukan nilai kosong pada kolom wajib '{kolom_wajib}' tabel nasional")

    kunci_silver = ["sumber", "seri_kode", "wilayah_kode", "periode", "rincian", "_berkas_raw"]
    silver_ref = df_silver[kunci_silver + ["nilai", "_sha256_raw"]].copy()
    jejak = tabel.merge(
        silver_ref,
        on=kunci_silver,
        how="left",
        validate="one_to_one",
        suffixes=("", "_silver"),
    )

    tidak_ditemukan = int(jejak["nilai_silver"].isna().sum())
    if tidak_ditemukan:
        raise AssertionError(f"{tidak_ditemukan} baris tabel nasional tidak tertelusur ke Silver")

    selisih_nilai = int(((jejak["nilai"] - jejak["nilai_silver"]).abs() > 1e-12).sum())
    if selisih_nilai:
        raise AssertionError(f"{selisih_nilai} baris tabel nasional memiliki nilai berbeda dari Silver")

    beda_sha = int((jejak["_sha256_raw"] != jejak["_sha256_raw_silver"]).sum())
    if beda_sha:
        raise AssertionError(f"{beda_sha} baris tabel nasional memiliki _sha256_raw berbeda dari Silver")

    return {
        "total_baris": int(len(tabel)),
        "jumlah_periode": int(tabel["periode"].nunique()),
        "jumlah_seri": int(tabel["seri_kode"].nunique()),
        "asal_angka": tabel["asal_angka"].value_counts().to_dict(),
        "baris_tertelusur": int(len(jejak)),
    }


def bangun_tabel_nasional_gold(
    df_silver: pd.DataFrame | None = None,
    silver_path: Path = SILVER_PATH,
    output_parquet: Path = OUTPUT_PARQUET,
    output_csv: Path = OUTPUT_CSV,
    simpan: bool = True,
    wajib_lengkap_7_seri: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Bangun, verifikasi, dan (opsional) simpan tabel nasional Gold Parquet serta pivot wide CSV."""
    df_sumber = _muat_silver(silver_path=silver_path, df_silver=df_silver)
    tabel = buat_tabel_nasional(df_silver=df_sumber)
    tabel_wide = buat_tabel_nasional_wide(df_silver=df_sumber)
    ringkasan = verifikasi_tabel_nasional(
        tabel,
        df_sumber,
        wajib_lengkap_7_seri=wajib_lengkap_7_seri,
    )

    if simpan:
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        output_parquet.parent.mkdir(parents=True, exist_ok=True)
        tabel.to_parquet(output_parquet, index=False)
        tabel_wide.to_csv(output_csv, index=False, encoding="utf-8-sig")

    return tabel, tabel_wide, ringkasan


def simpan_tabel_nasional(df_silver: pd.DataFrame | None = None) -> pd.DataFrame:
    """Bentuk, verifikasi, dan simpan tabel nasional Gold Parquet beserta laporan wide CSV."""
    tabel, tabel_wide, ringkasan = bangun_tabel_nasional_gold(df_silver=df_silver, simpan=True)
    asal = ringkasan["asal_angka"]
    print(
        f"Tabel nasional Gold tersimpan di data/gold/tabel_nasional.parquet "
        f"({ringkasan['total_baris']} baris, {ringkasan['jumlah_periode']} periode x "
        f"{ringkasan['jumlah_seri']} seri | asal_angka: {asal.get('baris_indonesia', 0)} baris_indonesia, "
        f"{asal.get('pembanding', 0)} pembanding | tertelusur Silver: "
        f"{ringkasan['baris_tertelusur']}/{ringkasan['total_baris']}) & CSV wide: "
        f"reports/tabel_nasional_periode_seri.csv ({len(tabel_wide)} periode x {len(tabel_wide.columns) - 1} kolom)"
    )
    return tabel


if __name__ == "__main__":
    simpan_tabel_nasional()
