"""Penyusun tabel nasional seri utama dan pembanding (periode x seri) untuk persiapan integrasi Tahap 6."""
from pathlib import Path
import pandas as pd

from src.gold.aturan_gold import pilih_snapshot, tangani_periode_subtahunan

ROOT = Path(__file__).resolve().parents[2]
SILVER_PATH = ROOT / "data/silver/silver.parquet"
OUTPUT_CSV = ROOT / "reports/tabel_nasional_periode_seri.csv"
OUTPUT_PARQUET = ROOT / "data/gold/tabel_nasional.parquet"


def buat_tabel_nasional(
    silver_path: Path = SILVER_PATH,
    df_silver: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Ekstrak observasi nasional (wilayah_kode: 9999) dengan aturan Gold dan bentuk pivot periode x seri."""
    if df_silver is None:
        if not silver_path.exists():
            raise FileNotFoundError(f"Berkas Silver tidak ditemukan: {silver_path}")
        df = pd.read_parquet(silver_path)
    else:
        df = df_silver

    # Saring hanya observasi nasional lalu terapkan aturan snapshot dan periode Gold
    nasional = df[df["wilayah_kode"] == 9999].copy()
    nas_snap, _ = pilih_snapshot(nasional)
    nas_dedup, _ = tangani_periode_subtahunan(nas_snap)
    
    # Bentuk label kolom yang informatif: nama seri + rincian
    def label_kolom(row):
        seri = row["seri_kode"]
        rincian = row["rincian"]
        if rincian == "total":
            return f"{seri} (total)"
        return f"{seri} ({rincian})"
    
    nas_dedup["kolom_analitis"] = nas_dedup.apply(label_kolom, axis=1)
    
    # Reshape ke bentuk pivot periode x seri
    pivot = nas_dedup.pivot(
        index="periode",
        columns="kolom_analitis",
        values="nilai"
    ).sort_index()
    
    # Pastikan indeks periode menjadi kolom
    pivot = pivot.reset_index()
    pivot.columns.name = None
    
    return pivot


def simpan_tabel_nasional(df_silver: pd.DataFrame | None = None):
    """Bentuk dan simpan tabel nasional ke CSV dan Parquet."""
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    
    tabel = buat_tabel_nasional(df_silver=df_silver)
    
    # Simpan CSV untuk laporan dan inspeksi manusia
    tabel.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    
    # Simpan Parquet untuk konsumsi analitis efisien
    tabel.to_parquet(OUTPUT_PARQUET, index=False)
    
    print(f"Tabel nasional berhasil disimpan:")
    print(f" - CSV     : {OUTPUT_CSV} ({len(tabel)} periode x {len(tabel.columns)-1} seri/rincian)")
    print(f" - Parquet : {OUTPUT_PARQUET}")
    return tabel


if __name__ == "__main__":
    simpan_tabel_nasional()
