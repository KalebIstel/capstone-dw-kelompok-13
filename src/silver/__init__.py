"""Tahap 2–4 — Profil, pembersihan, dan penyeragaman ke Silver (pertemuan II–VII). Milik tim.

Keluaran: data/silver/silver.parquet dengan skema minimal di src/common/skema.py.
Satu baris = satu seri x wilayah x periode x rincian x berkas sumber. Nilai dari sumber berbeda
TIDAK digabung di sini. Setiap keputusan pembersihan dicatat di log-keputusan.csv.
"""
from pathlib import Path
import pandas as pd

from src.silver.transformasi import susun_silver

OUTPUT_DIR = Path("data/silver")
SILVER_FILE = OUTPUT_DIR / "silver.parquet"


def jalankan(mentah: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Terima keluaran tahap 1, susun, tulis, dan kembalikan DataFrame Silver."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df_silver = susun_silver(mentah)
    df_silver.to_parquet(SILVER_FILE, index=False)
    print(f"Silver tersimpan di {SILVER_FILE} ({len(df_silver):,} baris)")
    return df_silver
