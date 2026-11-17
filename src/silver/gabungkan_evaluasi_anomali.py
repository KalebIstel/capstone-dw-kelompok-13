
from pathlib import Path
import pandas as pd

OUTPUT_DIR = Path("reports")

# Membaca hasil evaluasi IQR
iqr = pd.read_csv(
    OUTPUT_DIR / "evaluasi_anomali_per_tahun.csv"
)

# Membaca hasil deteksi IQR gabungan dan Z-score
zscore = pd.read_csv(
    OUTPUT_DIR / "kandidat_anomali.csv"
)

# Mengambil kolom yang diperlukan
kolom_zscore = [
    "seri",
    "tahun",
    "wilayah",
    "nilai",
    "z_score",
    "anomali_iqr",
    "anomali_zscore",
]

zscore = zscore[kolom_zscore].rename(
    columns={
        "anomali_iqr": "anomali_iqr_gabungan_awal"
    }
)

# Menggabungkan berdasarkan identitas observasi
hasil = iqr.merge(
    zscore,
    on=["seri", "tahun", "wilayah", "nilai"],
    how="left",
    validate="one_to_one"
)

# Mengisi status False untuk observasi yang tidak terdeteksi
hasil["anomali_zscore"] = (
    hasil["anomali_zscore"].fillna(False).astype(bool)
)

hasil["anomali_iqr_gabungan_awal"] = (
    hasil["anomali_iqr_gabungan_awal"]
    .fillna(False)
    .astype(bool)
)

# Memeriksa konsistensi hasil IQR gabungan
hasil["konsisten_iqr_gabungan"] = (
    hasil["anomali_iqr_gabungan"] ==
    hasil["anomali_iqr_gabungan_awal"]
)

# Mengambil observasi yang terdeteksi minimal satu metode
hasil["kandidat_anomali"] = (
    hasil["anomali_iqr_gabungan"] |
    hasil["anomali_iqr_tahunan"] |
    hasil["anomali_zscore"]
)

kandidat = hasil[
    hasil["kandidat_anomali"]
].copy()

# Menentukan metode deteksi setiap observasi
def metode_deteksi(baris):
    metode = []

    if baris["anomali_iqr_gabungan"]:
        metode.append("IQR gabungan")

    if baris["anomali_iqr_tahunan"]:
        metode.append("IQR tahunan")

    if baris["anomali_zscore"]:
        metode.append("Z-score")

    return "; ".join(metode)


kandidat["metode_deteksi"] = kandidat.apply(
    metode_deteksi,
    axis=1
)

# Menyusun kolom laporan
kolom_laporan = [
    "seri",
    "tahun",
    "wilayah",
    "nilai",
    "z_score",
    "anomali_iqr_gabungan",
    "anomali_iqr_tahunan",
    "anomali_zscore",
    "metode_deteksi",
]

kandidat = kandidat[kolom_laporan].sort_values(
    ["seri", "tahun", "wilayah"]
)

# Menyimpan hasil akhir
kandidat.to_csv(
    OUTPUT_DIR / "daftar_final_kandidat_anomali.csv",
    index=False
)

# Menampilkan ringkasan
print("\n" + "=" * 60)
print("DAFTAR FINAL KANDIDAT ANOMALI")
print("=" * 60)

print("\nJumlah kandidat per seri:")
print(kandidat.groupby("seri").size().to_string())

print("\nJumlah berdasarkan metode:")
print(
    kandidat["metode_deteksi"]
    .value_counts()
    .to_string()
)

print("\nTotal kandidat:", len(kandidat))

print("\nFile berhasil disimpan:")
print("reports/daftar_final_kandidat_anomali.csv")
