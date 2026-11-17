
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data/raw/bps/2026-10-17")
OUTPUT_DIR = Path("reports")

FILES = {
    "var1186": DATA_DIR / "sdg8_neet.csv",
    "var2658": DATA_DIR / "sdg8_8_7_1_v2658.csv",
}


def deteksi_anomali(df, kode):
    """Mendeteksi kandidat anomali menggunakan IQR dan Z-score."""

    # Memisahkan data provinsi dari agregat nasional
    df = df[
        df["wilayah"].str.upper() != "INDONESIA"
    ].copy()

    df["nilai"] = pd.to_numeric(df["nilai"], errors="coerce")
    df["tahun"] = pd.to_numeric(df["tahun"], errors="coerce")

    # Menghitung batas IQR
    q1 = df["nilai"].quantile(0.25)
    q3 = df["nilai"].quantile(0.75)
    iqr = q3 - q1

    batas_bawah = q1 - (1.5 * iqr)
    batas_atas = q3 + (1.5 * iqr)

    # Menghitung Z-score
    rata_rata = df["nilai"].mean()
    standar_deviasi = df["nilai"].std(ddof=0)

    if standar_deviasi == 0:
        df["z_score"] = 0
    else:
        df["z_score"] = (
            df["nilai"] - rata_rata
        ) / standar_deviasi

    # Memberikan tanda kandidat anomali
    df["anomali_iqr"] = (
        (df["nilai"] < batas_bawah) |
        (df["nilai"] > batas_atas)
    )

    df["anomali_zscore"] = df["z_score"].abs() > 3

    df["kandidat_anomali"] = (
        df["anomali_iqr"] |
        df["anomali_zscore"]
    )

    # Menambahkan kode seri
    df["seri"] = kode

    # Mengambil hanya observasi yang terdeteksi
    hasil = df[df["kandidat_anomali"]].copy()

    # Menampilkan ringkasan
    print(f"\n{'=' * 55}")
    print(f"DETEKSI ANOMALI {kode}")
    print(f"{'=' * 55}")

    print("Jumlah observasi provinsi:", len(df))
    print("Q1:", q1)
    print("Q3:", q3)
    print("IQR:", iqr)
    print("Batas bawah IQR:", batas_bawah)
    print("Batas atas IQR:", batas_atas)
    print("Rata-rata:", rata_rata)
    print("Standar deviasi:", standar_deviasi)

    print("\nJumlah kandidat anomali IQR:", df["anomali_iqr"].sum())
    print(
        "Jumlah kandidat anomali Z-score:",
        df["anomali_zscore"].sum()
    )
    print(
        "Jumlah kandidat anomali gabungan:",
        len(hasil)
    )

    if not hasil.empty:
        print("\nDaftar kandidat anomali:")
        print(
            hasil[
                [
                    "tahun",
                    "wilayah",
                    "nilai",
                    "z_score",
                    "anomali_iqr",
                    "anomali_zscore",
                ]
            ].sort_values(
                by=["tahun", "wilayah"]
            ).to_string(index=False)
        )
    else:
        print("\nTidak ditemukan kandidat anomali.")

    return hasil


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    semua_hasil = []

    for kode, path in FILES.items():
        if not path.exists():
            raise FileNotFoundError(
                f"File tidak ditemukan: {path}"
            )

        data = pd.read_csv(path)

        hasil = deteksi_anomali(data, kode)
        semua_hasil.append(hasil)

    # Menggabungkan hasil kedua seri
    hasil_akhir = pd.concat(
        semua_hasil,
        ignore_index=True
    )

    # Menyimpan hasil deteksi
    hasil_akhir.to_csv(
        OUTPUT_DIR / "kandidat_anomali.csv",
        index=False
    )

    print("\n" + "=" * 55)
    print("SELESAI")
    print("=" * 55)
    print("Total kandidat anomali:", len(hasil_akhir))
    print("File tersimpan: reports/kandidat_anomali.csv")
