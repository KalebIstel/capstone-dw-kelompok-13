
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data/raw/bps/2026-10-17")
OUTPUT_DIR = Path("reports")

FILES = {
    "var1186": DATA_DIR / "sdg8_neet.csv",
    "var2658": DATA_DIR / "sdg8_8_7_1_v2658.csv",
}


def evaluasi_iqr(df, kode):
    """Membandingkan IQR gabungan dan IQR per tahun."""

    # Memisahkan data provinsi dari agregat nasional
    df = df[
        df["wilayah"].str.upper() != "INDONESIA"
    ].copy()

    df["tahun"] = pd.to_numeric(df["tahun"], errors="coerce")
    df["nilai"] = pd.to_numeric(df["nilai"], errors="coerce")

    df = df.dropna(subset=["tahun", "nilai"])

    # -----------------------------------------
    # 1. IQR GABUNGAN SELURUH TAHUN
    # -----------------------------------------

    q1_gabungan = df["nilai"].quantile(0.25)
    q3_gabungan = df["nilai"].quantile(0.75)
    iqr_gabungan = q3_gabungan - q1_gabungan

    batas_bawah_gabungan = q1_gabungan - 1.5 * iqr_gabungan
    batas_atas_gabungan = q3_gabungan + 1.5 * iqr_gabungan

    df["anomali_iqr_gabungan"] = (
        (df["nilai"] < batas_bawah_gabungan) |
        (df["nilai"] > batas_atas_gabungan)
    )

    # -----------------------------------------
    # 2. IQR PER TAHUN
    # -----------------------------------------

    statistik_tahunan = (
        df.groupby("tahun")["nilai"]
        .agg(
            jumlah_data="count",
            q1=lambda x: x.quantile(0.25),
            q3=lambda x: x.quantile(0.75),
        )
        .reset_index()
    )

    statistik_tahunan["iqr"] = (
        statistik_tahunan["q3"] -
        statistik_tahunan["q1"]
    )

    statistik_tahunan["batas_bawah"] = (
        statistik_tahunan["q1"] -
        1.5 * statistik_tahunan["iqr"]
    )

    statistik_tahunan["batas_atas"] = (
        statistik_tahunan["q3"] +
        1.5 * statistik_tahunan["iqr"]
    )

    # Menggabungkan batas tahunan ke data utama
    df = df.merge(
        statistik_tahunan[
            [
                "tahun",
                "q1",
                "q3",
                "iqr",
                "batas_bawah",
                "batas_atas",
            ]
        ],
        on="tahun",
        how="left"
    )

    df["anomali_iqr_tahunan"] = (
        (df["nilai"] < df["batas_bawah"]) |
        (df["nilai"] > df["batas_atas"])
    )

    # -----------------------------------------
    # 3. MEMBANDINGKAN HASIL KEDUA METODE
    # -----------------------------------------

    def tentukan_status(baris):
        if (
            baris["anomali_iqr_gabungan"] and
            baris["anomali_iqr_tahunan"]
        ):
            return "Terdeteksi oleh kedua metode"

        elif baris["anomali_iqr_gabungan"]:
            return "Hanya IQR gabungan"

        elif baris["anomali_iqr_tahunan"]:
            return "Hanya IQR tahunan"

        return "Tidak terdeteksi"

    df["status_perbandingan"] = df.apply(
        tentukan_status,
        axis=1
    )

    df["seri"] = kode

    # -----------------------------------------
    # 4. MENAMPILKAN HASIL
    # -----------------------------------------

    print(f"\n{'=' * 60}")
    print(f"EVALUASI ANOMALI {kode}")
    print(f"{'=' * 60}")

    print("\nBatas IQR gabungan:")
    print("Q1:", q1_gabungan)
    print("Q3:", q3_gabungan)
    print("IQR:", iqr_gabungan)
    print("Batas bawah:", batas_bawah_gabungan)
    print("Batas atas:", batas_atas_gabungan)

    print("\nStatistik IQR per tahun:")
    print(statistik_tahunan.to_string(index=False))

    print("\nPerbandingan hasil deteksi:")
    print(
        df["status_perbandingan"]
        .value_counts()
        .to_string()
    )

    kandidat = df[
        df["anomali_iqr_gabungan"] |
        df["anomali_iqr_tahunan"]
    ].copy()

    print("\nDaftar observasi kandidat:")
    if not kandidat.empty:
        print(
            kandidat[
                [
                    "tahun",
                    "wilayah",
                    "nilai",
                    "anomali_iqr_gabungan",
                    "anomali_iqr_tahunan",
                    "status_perbandingan",
                ]
            ]
            .sort_values(["tahun", "wilayah"])
            .to_string(index=False)
        )
    else:
        print("Tidak ditemukan kandidat.")

    return df, statistik_tahunan


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    semua_data = []
    semua_statistik = []

    for kode, path in FILES.items():
        if not path.exists():
            raise FileNotFoundError(
                f"File tidak ditemukan: {path}"
            )

        data = pd.read_csv(path)

        hasil, statistik = evaluasi_iqr(data, kode)

        semua_data.append(hasil)
        statistik["seri"] = kode
        semua_statistik.append(statistik)

    # Menggabungkan hasil kedua seri
    hasil_akhir = pd.concat(
        semua_data,
        ignore_index=True
    )

    statistik_akhir = pd.concat(
        semua_statistik,
        ignore_index=True
    )

    # Menyimpan seluruh hasil evaluasi
    hasil_akhir.to_csv(
        OUTPUT_DIR / "evaluasi_anomali_per_tahun.csv",
        index=False
    )

    # Menyimpan statistik IQR setiap tahun
    statistik_akhir.to_csv(
        OUTPUT_DIR / "statistik_iqr_per_tahun.csv",
        index=False
    )

    print("\n" + "=" * 60)
    print("EVALUASI SELESAI")
    print("=" * 60)
    print("File 1: reports/evaluasi_anomali_per_tahun.csv")
    print("File 2: reports/statistik_iqr_per_tahun.csv")
