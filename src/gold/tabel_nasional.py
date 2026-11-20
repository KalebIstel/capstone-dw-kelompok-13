"""Penyusun tabel nasional seri utama dan pembanding (periode x seri) untuk persiapan integrasi Tahap 6."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SILVER_PATH = ROOT / "data/silver/silver.parquet"
OUTPUT_CSV = ROOT / "reports/tabel_nasional_periode_seri.csv"
OUTPUT_PARQUET = ROOT / "data/gold/tabel_nasional.parquet"


def buat_tabel_nasional(silver_path: Path = SILVER_PATH) -> pd.DataFrame:
    """Ekstrak observasi nasional (wilayah_kode: 9999) dan bentuk pivot periode x seri."""
    if not silver_path.exists():
        raise FileNotFoundError(f"Berkas Silver tidak ditemukan: {silver_path}")
    
    df = pd.read_parquet(silver_path)
    
    # Saring hanya observasi nasional
    nasional = df[df["wilayah_kode"] == 9999].copy()
    
    # Deduplikasi sumber ganda BPS (CSV dan JSON WebAPI nilainya identik)
    # Ambil 1 representasi per kombinasi seri_kode, periode, dan rincian
    nas_dedup = nasional.drop_duplicates(subset=["seri_kode", "periode", "rincian"]).copy()
    
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


def simpan_tabel_nasional():
    """Bentuk dan simpan tabel nasional ke CSV dan Parquet."""
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    
    tabel = buat_tabel_nasional()
    
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
