
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = Path("data/raw/bps/2026-10-17")
OUTPUT_DIR = Path("reports/gambar")

FILES = {
    "var1186": DATA_DIR / "sdg8_neet.csv",
    "var2658": DATA_DIR / "sdg8_8_7_1_v2658.csv",
}

# Provinsi yang terdeteksi sebagai kandidat anomali
PROVINSI_KANDIDAT = {
    "var1186": [
        "BALI",
        "DI YOGYAKARTA",
        "SULAWESI UTARA",
        "MALUKU",
        "PAPUA PEGUNUNGAN",
    ],
    "var2658": [
        "SULAWESI TENGGARA",
        "NUSA TENGGARA TIMUR",
        "PAPUA TENGAH",
    ],
}


def baca_data(path):
    df = pd.read_csv(path)

    df["tahun"] = pd.to_numeric(
        df["tahun"], errors="coerce"
    )
    df["nilai"] = pd.to_numeric(
        df["nilai"], errors="coerce"
    )

    # Mengeluarkan agregat nasional
    df = df[
        df["wilayah"].str.upper() != "INDONESIA"
    ].copy()

    return df.dropna(subset=["tahun", "nilai"])


def buat_boxplot(df, kode):
    data_per_tahun = [
        grup["nilai"].values
        for _, grup in df.groupby("tahun")
    ]

    daftar_tahun = sorted(df["tahun"].unique())

    plt.figure(figsize=(12, 6))

    plt.boxplot(
        data_per_tahun,
        tick_labels=daftar_tahun,
        showfliers=True
    )

    plt.title(f"Distribusi Nilai Provinsi per Tahun - {kode}")
    plt.xlabel("Tahun")
    plt.ylabel("Nilai (%)")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / f"boxplot_{kode}.png",
        dpi=300
    )
    plt.close()


def buat_grafik_tren(df, kode):
    plt.figure(figsize=(12, 6))

    for provinsi in PROVINSI_KANDIDAT[kode]:
        data_provinsi = df[
            df["wilayah"].str.upper() == provinsi
        ].sort_values("tahun")

        if data_provinsi.empty:
            continue

        plt.plot(
            data_provinsi["tahun"],
            data_provinsi["nilai"],
            marker="o",
            label=provinsi
        )

    plt.title(f"Tren Nilai Provinsi Kandidat Anomali - {kode}")
    plt.xlabel("Tahun")
    plt.ylabel("Nilai (%)")
    plt.xticks(sorted(df["tahun"].unique()))
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / f"tren_kandidat_{kode}.png",
        dpi=300
    )
    plt.close()

if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for kode, path in FILES.items():
        print(f"\nMembuat visualisasi {kode}...")

        df = baca_data(path)

        buat_boxplot(df, kode)
        buat_grafik_tren(df, kode)

        print("Visualisasi berhasil disimpan.")

    print("\nSeluruh visualisasi selesai.")
    print("Lokasi:", OUTPUT_DIR)
