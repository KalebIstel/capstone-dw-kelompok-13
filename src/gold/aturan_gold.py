"""Aturan satu nilai per sel Gold: snapshot, rincian sebanding, periode, dan penanda anomali.

Tahap 4 (persiapan Gold) untuk Kasus 13 (Pemuda NEET dan Pekerja Anak):
1. pilih_snapshot: memilih satu observasi per (sumber, seri_kode, wilayah_kode, periode, rincian)
   berdasarkan tanggal snapshot terbaru di _berkas_raw, lalu prioritas format CSV > JSON.
2. tangani_periode_subtahunan: memprioritaskan jenis_periode='tahun', dan bila hanya ada
   semester/triwulan/bulan, memilih sub-periode terakhir pada granularitas tertinggi
   (tahun > semester > triwulan > bulan) agar lineage 1-ke-1 tetap utuh.
3. pilih_rincian_dan_cakupan: memisahkan panel provinsi (rincian='total', wilayah != 9999)
   dari observasi nasional/disagregasi yang dikelola di Silver dan tabel_nasional.
4. bangun_grid_panel & sematkan_penanda_anomali: membentuk grid 38 provinsi x tahun seri
   dengan status sel kosong eksplisit (K-006) serta mewariskan penanda outlier_asli dan
   patahan_diduga dari Sprint 1 tanpa menghapus atau mengubah nilai observasi.
"""
from __future__ import annotations

from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SILVER_PATH = ROOT / "data/silver/silver.parquet"
PANEL_GOLD_PATH = ROOT / "data/gold/panel.parquet"
KATEGORI_ANOMALI_PATH = ROOT / "reports/kategori_anomali.csv"
TAHUN_SERENTAK_PATH = ROOT / "reports/tahun_serentak.csv"

SERI_PANEL_UTAMA = ("var1186", "var2658")
INDIKATOR_LABEL = {
    "var1186": "neet_15_24",
    "var2658": "pekerja_anak_5_17",
}
WILAYAH_DOB_PAPUA = {9200, 9500, 9600, 9700}

KUNCI_OBSERVASI = ["sumber", "seri_kode", "wilayah_kode", "periode", "rincian"]
KUNCI_PANEL_GOLD = ["wilayah_kode", "periode", "seri_kode"]
KUNCI_PANEL_INDIKATOR = ["nama_wilayah", "periode", "indikator"]

PRIORITAS_FORMAT = {"csv": 0, "json": 1}
PRIORITAS_JENIS_PERIODE = {"tahun": 0, "semester": 1, "triwulan": 2, "bulan": 3}

SATUAN_BAKU_MAP = {
    "persen": "persen",
    "%": "persen",
    "pt": "persen",
    "per 1.000": "per 1.000",
    "per 1000": "per 1.000",
    "per_1000": "per 1.000",
    "rupiah": "rupiah",
    "rp": "rupiah",
    "idr": "rupiah",
    "orang": "orang",
    "jiwa": "orang",
}
SATUAN_BAKU_SAH = {"persen", "per 1.000", "rupiah", "orang"}

KOLOM_PANEL_GOLD = [
    "seri_kode",
    "indikator",
    "wilayah_kode",
    "nama_wilayah",
    "periode",
    "sumber",
    "rincian",
    "nilai",
    "satuan",
    "status_wilayah",
    "status_data",
    "penanda_anomali",
    "arah_serentak_tahun",
    "catatan_anomali",
    "snapshot_tanggal",
    "_berkas_raw",
    "_sha256_raw",
]


def ekstrak_tanggal_snapshot(berkas_raw: str) -> str:
    """Ambil tanggal snapshot YYYY-MM-DD dari jalur _berkas_raw."""
    jalur = str(berkas_raw).replace("\\", "/")
    cocok = re.search(r"/(\d{4}-\d{2}-\d{2})/", jalur)
    return cocok.group(1) if cocok else "0000-00-00"


def ekstrak_format_berkas(berkas_raw: str) -> str:
    """Ambil ekstensi berkas mentah dalam huruf kecil (mis. 'csv', 'json')."""
    ekstensi = Path(str(berkas_raw)).suffix.lower().lstrip(".")
    return ekstensi or "lainnya"


def pilih_snapshot(df_silver: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Pilih tepat satu baris per kunci observasi berdasarkan snapshot terbaru dan format.

    Aturan:
    - Kelompokkan menurut (sumber, seri_kode, wilayah_kode, periode, rincian).
    - Urutkan tanggal snapshot menurun (snapshot terbaru menang bila angkanya berbeda).
    - Bila tanggal snapshot sama (mis. CSV datar vs JSON WebAPI BPS pada tanggal sama),
      prioritaskan berkas CSV atas JSON setelah memeriksa konsistensi nilainya.
    """
    if df_silver.empty:
        return df_silver.copy(), {
            "baris_masuk": 0,
            "baris_terpilih": 0,
            "baris_tidak_terpilih": 0,
            "kunci_ganda": 0,
            "kunci_nilai_berbeda": 0,
            "kunci_tanggal_sama_nilai_berbeda": 0,
        }

    df = df_silver.copy()
    df["snapshot_tanggal"] = df["_berkas_raw"].map(ekstrak_tanggal_snapshot)
    df["_format_berkas"] = df["_berkas_raw"].map(ekstrak_format_berkas)
    df["_prioritas_format"] = df["_format_berkas"].map(lambda fmt: PRIORITAS_FORMAT.get(fmt, 99))

    statistik_kunci = df.groupby(KUNCI_OBSERVASI, sort=False)["nilai"].agg(["count", "nunique"])
    kunci_ganda = int((statistik_kunci["count"] > 1).sum())
    kunci_nilai_berbeda = int((statistik_kunci["nunique"] > 1).sum())

    statistik_tanggal = df.groupby(KUNCI_OBSERVASI + ["snapshot_tanggal"], sort=False)["nilai"].nunique()
    kunci_tanggal_sama_nilai_berbeda = int((statistik_tanggal > 1).sum())

    df_terurut = df.sort_values(
        by=KUNCI_OBSERVASI + ["snapshot_tanggal", "_prioritas_format", "_berkas_raw"],
        ascending=[True, True, True, True, True, False, True, True],
        kind="mergesort",
    )
    df_terpilih = df_terurut.drop_duplicates(subset=KUNCI_OBSERVASI, keep="first").copy()
    df_terpilih = df_terpilih.drop(columns=["_format_berkas", "_prioritas_format"]).reset_index(drop=True)

    ringkasan = {
        "baris_masuk": int(len(df)),
        "baris_terpilih": int(len(df_terpilih)),
        "baris_tidak_terpilih": int(len(df) - len(df_terpilih)),
        "kunci_ganda": kunci_ganda,
        "kunci_nilai_berbeda": kunci_nilai_berbeda,
        "kunci_tanggal_sama_nilai_berbeda": kunci_tanggal_sama_nilai_berbeda,
    }
    return df_terpilih, ringkasan


def _urutan_subperiode(periode: str, jenis_periode: str) -> int:
    """Kembalikan urutan numerik sub-periode dalam satu tahun (semakin besar = semakin akhir)."""
    teks = str(periode).strip()
    if jenis_periode == "tahun":
        return 0
    if jenis_periode == "semester":
        cocok = re.match(r"^\d{4}-S([12])$", teks)
        if not cocok:
            raise ValueError(f"Format periode semester tidak sah: {periode}")
        return int(cocok.group(1))
    if jenis_periode == "triwulan":
        cocok = re.match(r"^\d{4}-Q([1-4])$", teks)
        if not cocok:
            raise ValueError(f"Format periode triwulan tidak sah: {periode}")
        return int(cocok.group(1))
    if jenis_periode == "bulan":
        cocok = re.match(r"^\d{4}-(0[1-9]|1[0-2])$", teks)
        if not cocok:
            raise ValueError(f"Format periode bulan tidak sah: {periode}")
        return int(cocok.group(1))
    raise ValueError(f"jenis_periode tidak dikenal: {jenis_periode}")


def tangani_periode_subtahunan(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Konversi atau pilih tepat satu observasi per tahun untuk periode semesteran/triwulanan/bulanan.

    Aturan:
    - Ekstrak tahun 4-digit dari kolom periode.
    - Prioritaskan granularitas tahun > semester > triwulan > bulan.
    - Bila dalam tahun yang sama terdapat beberapa observasi sub-tahunan pada granularitas
      tertinggi yang tersedia, pilih sub-periode paling akhir dalam tahun (S2, Q4, bulan 12)
      guna menjaga nilai observasi riil (indikator persentase non-aditif) dan lineage 1-ke-1.
    """
    if df.empty:
        return df.copy(), {
            "baris_masuk": 0,
            "baris_terpilih": 0,
            "baris_tidak_terpilih": 0,
            "baris_subtahunan_masuk": 0,
        }

    hasil = df.copy()
    hasil["_tahun"] = hasil["periode"].astype(str).str.slice(0, 4)
    tak_dikenal = set(hasil["jenis_periode"].dropna()) - set(PRIORITAS_JENIS_PERIODE)
    if tak_dikenal:
        raise ValueError(f"jenis_periode tidak dikenal: {sorted(tak_dikenal)}")

    baris_subtahunan = int((hasil["jenis_periode"] != "tahun").sum())
    hasil["_prioritas_periode"] = hasil["jenis_periode"].map(PRIORITAS_JENIS_PERIODE)
    hasil["_sub_urutan"] = [
        _urutan_subperiode(p, j) for p, j in zip(hasil["periode"], hasil["jenis_periode"])
    ]

    kunci_tahunan = ["sumber", "seri_kode", "wilayah_kode", "_tahun", "rincian"]
    hasil_terurut = hasil.sort_values(
        by=kunci_tahunan + ["_prioritas_periode", "_sub_urutan", "snapshot_tanggal", "_berkas_raw"],
        ascending=[True, True, True, True, True, True, False, False, True],
        kind="mergesort",
    )
    hasil_terpilih = hasil_terurut.drop_duplicates(subset=kunci_tahunan, keep="first").copy()
    hasil_terpilih["periode"] = hasil_terpilih["_tahun"]
    hasil_terpilih["jenis_periode"] = "tahun"
    hasil_terpilih = hasil_terpilih.drop(
        columns=["_tahun", "_prioritas_periode", "_sub_urutan"]
    ).reset_index(drop=True)

    ringkasan = {
        "baris_masuk": int(len(df)),
        "baris_terpilih": int(len(hasil_terpilih)),
        "baris_tidak_terpilih": int(len(df) - len(hasil_terpilih)),
        "baris_subtahunan_masuk": baris_subtahunan,
    }
    return hasil_terpilih, ringkasan


def pilih_rincian_dan_cakupan(
    df: pd.DataFrame,
    seri_panel: tuple[str, ...] = SERI_PANEL_UTAMA,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Pisahkan observasi panel provinsi x tahun dari observasi nasional dan rincian non-total.

    Aturan panel provinsi:
    - Hanya wilayah provinsi (wilayah_kode != 9999), seri utama panel (var1186, var2658),
      dan rincian agregat sebanding ('total') yang masuk panel provinsi Gold.
    - Observasi nasional (wilayah_kode == 9999) beserta disagregasi gender/umur ILOSTAT
      tetap berada di Silver dan disajikan pada tabel_nasional dengan kedua definisi pekerja
      anak ILO (SDG_A871_SEX_AGE_RT dan SDG_B871_SEX_AGE_RT) terpisah.
    """
    mask_provinsi = (
        (df["wilayah_kode"] != 9999)
        & (df["seri_kode"].isin(seri_panel))
        & (df["rincian"] == "total")
    )
    df_provinsi = df[mask_provinsi].copy().reset_index(drop=True)
    df_nasional = df[df["wilayah_kode"] == 9999].copy().reset_index(drop=True)

    ganda_panel = int(df_provinsi.duplicated(KUNCI_PANEL_GOLD).sum())
    if ganda_panel:
        raise ValueError(f"Ditemukan {ganda_panel} baris ganda pada kunci panel {KUNCI_PANEL_GOLD}")

    tidak_masuk = df[~mask_provinsi]
    ringkasan = {
        "baris_masuk": int(len(df)),
        "baris_panel_provinsi": int(len(df_provinsi)),
        "baris_tidak_masuk_panel": int(len(tidak_masuk)),
        "baris_nasional": int(len(df_nasional)),
        "rincian_tidak_masuk": {
            "bps_nasional": int(((tidak_masuk["sumber"] == "bps") & (tidak_masuk["wilayah_kode"] == 9999)).sum()),
            "wdi_nasional": int((tidak_masuk["sumber"] == "wdi").sum()),
            "ilostat_nasional_total_atau_15_17": int(
                ((tidak_masuk["sumber"] == "ilostat") & (tidak_masuk["rincian"].isin(["total", "15-17"]))).sum()
            ),
            "ilostat_nasional_disagregasi_gender": int(
                ((tidak_masuk["sumber"] == "ilostat") & (~tidak_masuk["rincian"].isin(["total", "15-17"]))).sum()
            ),
            "provinsi_rincian_atau_seri_lain": int((tidak_masuk["wilayah_kode"] != 9999).sum()),
        },
    }
    return df_provinsi, df_nasional, ringkasan


def _status_wilayah_papua(wilayah_kode: int, tahun: int) -> str:
    """Terapkan aturan K-006 untuk status eligibilitas 4 provinsi DOB Papua."""
    if wilayah_kode not in WILAYAH_DOB_PAPUA:
        return "eligible"
    if tahun < 2022:
        return "belum_terbentuk"
    if tahun == 2022:
        return "masa_transisi"
    return "eligible"


def bangun_grid_panel(df_provinsi: pd.DataFrame) -> pd.DataFrame:
    """Bangun grid lengkap 38 provinsi x tahun seri dengan kategori sel kosong eksplisit."""
    acuan_provinsi = (
        df_provinsi[["wilayah_kode", "nama_wilayah"]]
        .drop_duplicates()
        .sort_values("wilayah_kode")
        .reset_index(drop=True)
    )
    if len(acuan_provinsi) != 38:
        raise ValueError(f"Jumlah provinsi acuan harus 38, ditemukan {len(acuan_provinsi)}")

    bagian_panel = []
    for seri in SERI_PANEL_UTAMA:
        sub = df_provinsi[df_provinsi["seri_kode"] == seri].copy()
        tahun_list = sorted(sub["periode"].astype(str).unique())

        grid = acuan_provinsi.merge(
            pd.DataFrame({"periode": tahun_list}),
            how="cross",
        )
        grid["seri_kode"] = seri
        grid["indikator"] = INDIKATOR_LABEL[seri]
        grid["sumber"] = "bps"
        grid["rincian"] = "total"
        grid["satuan"] = "persen"

        grid = grid.merge(
            sub[["wilayah_kode", "periode", "nilai", "snapshot_tanggal", "_berkas_raw", "_sha256_raw"]],
            on=["wilayah_kode", "periode"],
            how="left",
            validate="one_to_one",
        )

        tahun_int = grid["periode"].astype(int)
        grid["status_wilayah"] = [
            _status_wilayah_papua(int(wk), int(th)) for wk, th in zip(grid["wilayah_kode"], tahun_int)
        ]

        grid["status_data"] = "tersedia"
        grid.loc[grid["status_wilayah"] == "belum_terbentuk", "status_data"] = "belum_terbentuk"
        grid.loc[grid["status_wilayah"] == "masa_transisi", "status_data"] = "masa_transisi"
        grid.loc[(grid["status_wilayah"] == "eligible") & grid["nilai"].isna(), "status_data"] = "missing"
        bagian_panel.append(grid)

    panel = pd.concat(bagian_panel, ignore_index=True)
    panel = panel.sort_values(["seri_kode", "periode", "wilayah_kode"]).reset_index(drop=True)
    return panel


def sematkan_penanda_anomali(
    df_panel: pd.DataFrame,
    kategori_path: Path = KATEGORI_ANOMALI_PATH,
    tahun_serentak_path: Path = TAHUN_SERENTAK_PATH,
) -> pd.DataFrame:
    """Sematkan penanda outlier_asli, patahan_diduga, dan arah tahun serentak dari Sprint 1."""
    hasil = df_panel.copy()
    hasil["_tahun_int"] = hasil["periode"].astype(int)

    if kategori_path.exists():
        kat = pd.read_csv(kategori_path)
        kat = kat[["seri", "tahun", "wilayah", "kategori", "alasan"]].rename(
            columns={
                "seri": "seri_kode",
                "tahun": "_tahun_int",
                "wilayah": "nama_wilayah",
                "kategori": "penanda_anomali",
                "alasan": "catatan_anomali",
            }
        )
        hasil = hasil.merge(
            kat,
            on=["seri_kode", "_tahun_int", "nama_wilayah"],
            how="left",
            validate="one_to_one",
        )
        jumlah_cocok = int(hasil["penanda_anomali"].notna().sum())
        if jumlah_cocok != len(kat):
            raise ValueError(
                f"Penanda anomali tidak cocok penuh: {jumlah_cocok} cocok dari {len(kat)} baris di {kategori_path}"
            )
    else:
        hasil["penanda_anomali"] = pd.Series(pd.NA, index=hasil.index, dtype="object")
        hasil["catatan_anomali"] = pd.Series(pd.NA, index=hasil.index, dtype="object")

    mask_normal = (hasil["status_data"] == "tersedia") & hasil["penanda_anomali"].isna()
    hasil.loc[mask_normal, "penanda_anomali"] = "normal"

    if tahun_serentak_path.exists():
        ts = pd.read_csv(tahun_serentak_path)
        ts = ts[["seri", "tahun", "arah_serentak"]].rename(
            columns={
                "seri": "seri_kode",
                "tahun": "_tahun_int",
                "arah_serentak": "arah_serentak_tahun",
            }
        )
        hasil = hasil.merge(
            ts,
            on=["seri_kode", "_tahun_int"],
            how="left",
            validate="many_to_one",
        )
    else:
        hasil["arah_serentak_tahun"] = pd.Series(pd.NA, index=hasil.index, dtype="object")

    hasil = hasil.drop(columns=["_tahun_int"])
    return hasil[KOLOM_PANEL_GOLD]


def seragamkan_satuan_per_indikator(df: pd.DataFrame) -> pd.DataFrame:
    """Seragamkan satuan per indikator ke label baku dan tolak satuan campur dalam satu kolom nilai."""
    if df.empty:
        return df.copy()

    hasil = df.copy()
    satuan_normal = hasil["satuan"].astype(str).str.strip().str.lower().map(
        lambda s: SATUAN_BAKU_MAP.get(s, s)
    )
    tak_baku = set(satuan_normal) - SATUAN_BAKU_SAH
    if tak_baku:
        raise ValueError(f"Ditemukan satuan di luar daftar baku {sorted(SATUAN_BAKU_SAH)}: {sorted(tak_baku)}")

    hasil["satuan"] = satuan_normal

    satuan_per_seri = hasil.groupby("seri_kode")["satuan"].nunique()
    seri_ganda = satuan_per_seri[satuan_per_seri > 1]
    if not seri_ganda.empty:
        raise ValueError(f"Seri memiliki satuan ganda: {seri_ganda.to_dict()}")

    if hasil["satuan"].nunique() > 1:
        raise ValueError(
            "Kolom nilai panel tidak boleh mencampur satuan berbeda: "
            f"{sorted(hasil['satuan'].unique())}"
        )
    return hasil


def verifikasi_ketertelusuran_silver(panel: pd.DataFrame, df_silver: pd.DataFrame) -> dict:
    """Pastikan kunci panel unik dan seluruh sel terisi Gold tertelusur 1-ke-1 ke baris Silver asalnya."""
    duplikat_kode = int(panel.duplicated(KUNCI_PANEL_GOLD).sum())
    if duplikat_kode:
        raise AssertionError(f"Panel Gold melanggar keunikan kunci {KUNCI_PANEL_GOLD}: {duplikat_kode} duplikat")

    duplikat_indikator = int(panel.duplicated(KUNCI_PANEL_INDIKATOR).sum())
    if duplikat_indikator:
        raise AssertionError(
            f"Panel Gold melanggar keunikan kunci {KUNCI_PANEL_INDIKATOR}: {duplikat_indikator} duplikat"
        )

    terisi = panel[panel["status_data"] == "tersedia"].copy()
    kunci_silver = ["sumber", "seri_kode", "wilayah_kode", "periode", "rincian", "_berkas_raw"]
    silver_ref = df_silver[kunci_silver + ["nilai", "_sha256_raw"]].copy()

    jejak = terisi.merge(
        silver_ref,
        on=kunci_silver,
        how="left",
        validate="one_to_one",
        suffixes=("", "_silver"),
    )

    tidak_ditemukan = int(jejak["nilai_silver"].isna().sum())
    if tidak_ditemukan:
        raise AssertionError(f"{tidak_ditemukan} sel Gold tidak tertelusur ke baris Silver asalnya")

    selisih_nilai = int(((jejak["nilai"] - jejak["nilai_silver"]).abs() > 1e-12).sum())
    if selisih_nilai:
        raise AssertionError(f"{selisih_nilai} sel Gold memiliki nilai berbeda dari baris Silver asalnya")

    beda_sha = int((jejak["_sha256_raw"] != jejak["_sha256_raw_silver"]).sum())
    if beda_sha:
        raise AssertionError(f"{beda_sha} sel Gold memiliki _sha256_raw berbeda dari baris Silver asalnya")

    return {
        "sel_terisi": int(len(terisi)),
        "sel_tertelusur": int(len(jejak)),
        "sel_kosong": int(len(panel) - len(terisi)),
    }


def bangun_panel_gold(
    df_silver: pd.DataFrame | None = None,
    silver_path: Path = SILVER_PATH,
    output_path: Path = PANEL_GOLD_PATH,
    kategori_path: Path = KATEGORI_ANOMALI_PATH,
    tahun_serentak_path: Path = TAHUN_SERENTAK_PATH,
    simpan: bool = True,
) -> tuple[pd.DataFrame, dict]:
    """Jalankan seluruh aturan pemilihan Gold dan hasilkan panel provinsi x tahun x indikator."""
    if df_silver is None:
        if not silver_path.exists():
            raise FileNotFoundError(f"Berkas Silver tidak ditemukan: {silver_path}")
        df_silver = pd.read_parquet(silver_path)

    df_snap, ringkasan_snap = pilih_snapshot(df_silver)
    df_tahunan, ringkasan_periode = tangani_periode_subtahunan(df_snap)
    df_provinsi, _, ringkasan_cakupan = pilih_rincian_dan_cakupan(df_tahunan)
    df_provinsi = seragamkan_satuan_per_indikator(df_provinsi)

    panel = bangun_grid_panel(df_provinsi)
    panel = sematkan_penanda_anomali(
        panel,
        kategori_path=kategori_path,
        tahun_serentak_path=tahun_serentak_path,
    )

    ringkasan_jejak = verifikasi_ketertelusuran_silver(panel, df_silver)

    if simpan:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        panel.to_parquet(output_path, index=False)

    ringkasan = {
        "snapshot": ringkasan_snap,
        "periode": ringkasan_periode,
        "cakupan": ringkasan_cakupan,
        "ketertelusuran": ringkasan_jejak,
        "panel": {
            "total_sel": int(len(panel)),
            "status_data": panel["status_data"].value_counts().to_dict(),
            "penanda_anomali": panel["penanda_anomali"].value_counts(dropna=True).to_dict(),
        },
    }
    return panel, ringkasan
