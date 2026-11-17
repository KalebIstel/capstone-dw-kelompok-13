
import pandas as pd

files = {
    "var1186": "data/raw/bps/2026-10-17/sdg8_neet.csv",
    "var2658": "data/raw/bps/2026-10-17/sdg8_8_7_1_v2658.csv"
}

for nama, file in files.items():
    df = pd.read_csv(file)

    print(f"\n========== {nama} ==========")

    for tahun, data in df.groupby("tahun"):
        wilayah = sorted(data["wilayah"].unique())

        print(f"\nTahun {tahun} ({len(wilayah)} wilayah):")
        print(", ".join(wilayah))
