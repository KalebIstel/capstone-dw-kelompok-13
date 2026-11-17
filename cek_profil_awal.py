
import pandas as pd

files = {
    "var1186": "data/raw/bps/2026-10-17/sdg8_neet.csv",
    "var2658": "data/raw/bps/2026-10-17/sdg8_8_7_1_v2658.csv"
}

for nama_seri, file in files.items():
    df = pd.read_csv(file)

    print(f"\n========== {nama_seri} ==========")

    print("Jumlah baris:", len(df))
    print("Jumlah kolom:", len(df.columns))

    print("\nRentang tahun:")
    print(sorted(df["tahun"].unique()))

    print("\nJumlah provinsi per tahun:")
    print(df.groupby("tahun")["wilayah"].nunique())

    print("\nRincian:")
    print(df["turvar"].unique())

    print("\nSatuan:")
    print(df["satuan"].unique())

    print("\nJumlah nilai kosong:")
    print(df.isna().sum())

    print("\nJumlah baris duplikat:")
    print(df.duplicated().sum())

    print("\nStatistik deskriptif nilai:")
    print(df["nilai"].describe())
