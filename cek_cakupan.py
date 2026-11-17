from pathlib import Path
import pandas as pd

DATA_DIR = Path("data/raw/bps/2026-10-17")

FILES = {
    "var1186": DATA_DIR / "sdg8_neet.csv",
    "var2658": DATA_DIR / "sdg8_8_7_1_v2658.csv",
}

for kode, path in FILES.items():
    df = pd.read_csv(path)

    # Mengeluarkan data agregat nasional
    df = df[
        df["wilayah"].str.upper() != "INDONESIA"
    ].copy()

    # Membuat tabel jumlah provinsi yang tersedia setiap tahun
    cakupan = (
        df.groupby("tahun")
        .agg(
            jumlah_provinsi=("wilayah", "nunique"),
            jumlah_observasi=("wilayah", "count")
        )
        .reset_index()
    )

    print(f"\n{'=' * 50}")
    print(f"CAKUPAN PROVINSI {kode}")
    print(f"{'=' * 50}")
    print(cakupan.to_string(index=False))

    # Menampilkan provinsi yang belum muncul pada setiap tahun
    semua_provinsi = sorted(df["wilayah"].unique())

    for tahun in sorted(df["tahun"].unique()):
        tersedia = set(
            df.loc[df["tahun"] == tahun, "wilayah"]
        )
        belum_tersedia = sorted(set(semua_provinsi) - tersedia)

        print(f"\nTahun {tahun}")
        print("Jumlah provinsi tersedia:", len(tersedia))
        print("Provinsi belum tersedia:", belum_tersedia)

    cakupan.to_csv(
        f"reports/cakupan_{kode}.csv",
        index=False
    )