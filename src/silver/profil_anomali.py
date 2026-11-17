
from pathlib import Path
import pandas as pd


# ============================================================
# 1. KONFIGURASI
# ============================================================

DATA_DIR = Path("data/raw/bps/2026-10-17")
REPORT_DIR = Path("reports")

FILES = {
    "var1186": DATA_DIR / "sdg8_neet.csv",
    "var2658": DATA_DIR / "sdg8_8_7_1_v2658.csv",
}

# Rentang tahun yang diharapkan berdasarkan definisi seri
RENTANG_TAHUN = {
    "var1186": (2015, 2025),
    "var2658": (2020, 2025),
}

KOLOM_WAJIB = [
    "var_id",
    "wilayah_id",
    "wilayah",
    "turvar_id",
    "turvar",
    "tahun_id",
    "tahun",
    "periode_id",
    "periode",
    "nilai",
    "satuan",
]

KOLOM_KUNCI = [
    "var_id",
    "wilayah_id",
    "tahun",
]


# ============================================================
# 2. MEMBACA DATA
# ============================================================

def baca_data():
    """Membaca data mentah dan mengonversi kolom numerik."""

    data = {}

    for kode, path in FILES.items():

        if not path.exists():
            raise FileNotFoundError(
                f"File tidak ditemukan: {path}"
            )

        df = pd.read_csv(path)

        # Memeriksa kolom wajib sebelum pemrosesan
        kolom_hilang = [
            kolom for kolom in KOLOM_WAJIB
            if kolom not in df.columns
        ]

        if kolom_hilang:
            raise ValueError(
                f"{kode}: kolom wajib tidak ditemukan "
                f"{kolom_hilang}"
            )

        # Konversi kolom numerik
        df["tahun"] = pd.to_numeric(
            df["tahun"],
            errors="coerce"
        )

        df["nilai"] = pd.to_numeric(
            df["nilai"],
            errors="coerce"
        )

        data[kode] = df

    return data


# ============================================================
# 3. PEMERIKSAAN KUALITAS DATA
# ============================================================

def periksa_data(data):
    """
    Memeriksa kualitas data setiap seri.
    Hasil pemeriksaan disimpan ke CSV.
    """

    ringkasan_pemeriksaan = []
    detail_missing = []
    detail_duplikat = []
    detail_rentang = []
    detail_identitas = []

    for kode, df in data.items():

        print("\n" + "=" * 60)
        print(f"PROFIL DAN PEMERIKSAAN DATA {kode}")
        print("=" * 60)

        # ----------------------------------------------------
        # A. INFORMASI UMUM
        # ----------------------------------------------------

        print("\nA. INFORMASI UMUM")

        print("Jumlah baris:", len(df))
        print("Jumlah kolom:", len(df.columns))
        print("Daftar kolom:", df.columns.tolist())

        print("\nRentang tahun aktual:")

        tahun_valid = df["tahun"].dropna()

        if not tahun_valid.empty:
            print(
                int(tahun_valid.min()),
                "-",
                int(tahun_valid.max())
            )
        else:
            print("Tidak tersedia.")

        # ----------------------------------------------------
        # B. MISSING VALUE
        # ----------------------------------------------------

        print("\nB. PEMERIKSAAN MISSING VALUE")

        missing = df.isna().sum()

        print(missing.to_string())

        for kolom, jumlah in missing.items():

            if jumlah > 0:
                detail_missing.append({
                    "seri": kode,
                    "kolom": kolom,
                    "jumlah_missing": int(jumlah),
                })

        total_missing = int(missing.sum())

        # ----------------------------------------------------
        # C. DUPLIKASI
        # ----------------------------------------------------

        print("\nC. PEMERIKSAAN DUPLIKASI")

        duplikat_baris = int(df.duplicated().sum())

        duplikat_kunci = int(
            df.duplicated(
                subset=KOLOM_KUNCI
            ).sum()
        )

        print(
            "Duplikasi seluruh kolom:",
            duplikat_baris
        )

        print(
            "Duplikasi seri-wilayah-tahun:",
            duplikat_kunci
        )

        data_duplikat = df[
            df.duplicated(
                subset=KOLOM_KUNCI,
                keep=False
            )
        ].copy()

        if data_duplikat.empty:
            print("Tidak ditemukan duplikasi kunci.")
        else:
            print("\nDetail duplikasi:")
            print(
                data_duplikat[
                    [
                        "var_id",
                        "wilayah_id",
                        "wilayah",
                        "tahun",
                        "nilai",
                    ]
                ].sort_values(
                    KOLOM_KUNCI
                ).to_string(index=False)
            )

            for _, baris in data_duplikat.iterrows():
                detail_duplikat.append({
                    "seri": kode,
                    "var_id": baris["var_id"],
                    "wilayah_id": baris["wilayah_id"],
                    "wilayah": baris["wilayah"],
                    "tahun": baris["tahun"],
                    "nilai": baris["nilai"],
                })

        # ----------------------------------------------------
        # D. PEMERIKSAAN NUMERIK
        # ----------------------------------------------------

        print("\nD. PEMERIKSAAN NUMERIK")

        jumlah_nilai_tidak_valid = int(
            df["nilai"].isna().sum()
        )

        jumlah_tahun_tidak_valid = int(
            df["tahun"].isna().sum()
        )

        jumlah_negatif = int(
            (df["nilai"] < 0).sum()
        )

        jumlah_di_atas_100 = int(
            (df["nilai"] > 100).sum()
        )

        print(
            "Nilai tidak numerik atau kosong:",
            jumlah_nilai_tidak_valid
        )

        print(
            "Tahun tidak numerik atau kosong:",
            jumlah_tahun_tidak_valid
        )

        print("Nilai negatif:", jumlah_negatif)

        print(
            "Nilai di atas 100:",
            jumlah_di_atas_100
        )

        di_luar_rentang = df[
            (df["nilai"] < 0) |
            (df["nilai"] > 100)
        ]

        if di_luar_rentang.empty:
            print("Tidak ada nilai di luar rentang 0-100.")
        else:
            print("\nDetail nilai di luar rentang:")

            print(
                di_luar_rentang[
                    [
                        "wilayah",
                        "tahun",
                        "nilai",
                    ]
                ].to_string(index=False)
            )

            for _, baris in di_luar_rentang.iterrows():
                detail_rentang.append({
                    "seri": kode,
                    "wilayah": baris["wilayah"],
                    "tahun": baris["tahun"],
                    "nilai": baris["nilai"],
                })

        # ----------------------------------------------------
        # E. PEMERIKSAAN SATUAN
        # ----------------------------------------------------

        print("\nE. PEMERIKSAAN SATUAN")

        print(
            df["satuan"]
            .value_counts(dropna=False)
            .to_string()
        )

        satuan_unik = (
            df["satuan"]
            .dropna()
            .astype(str)
            .str.strip()
            .str.upper()
            .unique()
        )

        satuan_tidak_sesuai = [
            satuan
            for satuan in satuan_unik
            if satuan != "PERSEN"
        ]

        print(
            "Jumlah jenis satuan:",
            len(satuan_unik)
        )

        print(
            "Satuan selain Persen:",
            satuan_tidak_sesuai
        )

        # ----------------------------------------------------
        # F. PEMERIKSAAN IDENTITAS WILAYAH
        # ----------------------------------------------------

        print("\nF. PEMERIKSAAN IDENTITAS WILAYAH")

        cek_nama = (
            df.groupby("wilayah")["wilayah_id"]
            .nunique()
        )

        nama_multi_id = cek_nama[
            cek_nama > 1
        ]

        cek_id = (
            df.groupby("wilayah_id")["wilayah"]
            .nunique()
        )

        id_multi_nama = cek_id[
            cek_id > 1
        ]

        print("Nama wilayah dengan lebih dari satu ID:")

        if nama_multi_id.empty:
            print("Tidak ditemukan.")
        else:
            print(nama_multi_id.to_string())

        print("\nID wilayah dengan lebih dari satu nama:")

        if id_multi_nama.empty:
            print("Tidak ditemukan.")
        else:
            print(id_multi_nama.to_string())

        for nama, jumlah in nama_multi_id.items():
            detail_identitas.append({
                "seri": kode,
                "jenis_masalah": "Nama wilayah memiliki banyak ID",
                "identitas": nama,
                "jumlah_perbedaan": int(jumlah),
            })

        for id_wilayah, jumlah in id_multi_nama.items():
            detail_identitas.append({
                "seri": kode,
                "jenis_masalah": "ID wilayah memiliki banyak nama",
                "identitas": id_wilayah,
                "jumlah_perbedaan": int(jumlah),
            })

        # ----------------------------------------------------
        # G. PEMERIKSAAN RENTANG TAHUN
        # ----------------------------------------------------

        print("\nG. PEMERIKSAAN RENTANG TAHUN")

        tahun_min, tahun_max = RENTANG_TAHUN[kode]

        tahun_di_luar = df[
            (df["tahun"] < tahun_min) |
            (df["tahun"] > tahun_max)
        ]

        print(
            "Rentang tahun yang diharapkan:",
            tahun_min,
            "-",
            tahun_max
        )

        print(
            "Jumlah tahun di luar rentang:",
            len(tahun_di_luar)
        )

        if not tahun_di_luar.empty:
            print(
                tahun_di_luar[
                    ["wilayah", "tahun"]
                ].to_string(index=False)
            )

        # ----------------------------------------------------
        # H. JUMLAH WILAYAH PER TAHUN
        # ----------------------------------------------------

        print("\nH. JUMLAH WILAYAH PER TAHUN")

        jumlah_wilayah = (
            df.groupby("tahun")["wilayah_id"]
            .nunique()
        )

        print(jumlah_wilayah.to_string())

        # ----------------------------------------------------
        # I. MENYIMPAN RINGKASAN PEMERIKSAAN
        # ----------------------------------------------------

        ringkasan_pemeriksaan.append({
            "seri": kode,
            "jumlah_baris": len(df),
            "jumlah_kolom": len(df.columns),
            "missing_value": total_missing,
            "duplikat_baris": duplikat_baris,
            "duplikat_kunci": duplikat_kunci,
            "nilai_tidak_valid": jumlah_nilai_tidak_valid,
            "tahun_tidak_valid": jumlah_tahun_tidak_valid,
            "nilai_negatif": jumlah_negatif,
            "nilai_di_atas_100": jumlah_di_atas_100,
            "jumlah_satuan": len(satuan_unik),
            "satuan_tidak_sesuai": len(satuan_tidak_sesuai),
            "nama_multi_id": len(nama_multi_id),
            "id_multi_nama": len(id_multi_nama),
            "tahun_di_luar_rentang": len(tahun_di_luar),
        })

    # --------------------------------------------------------
    # J. EKSPOR HASIL PEMERIKSAAN
    # --------------------------------------------------------

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    pd.DataFrame(
        ringkasan_pemeriksaan
    ).to_csv(
        REPORT_DIR / "ringkasan_pemeriksaan_kualitas.csv",
        index=False
    )

    # Fungsi untuk menyimpan detail, termasuk jika kosong
    def simpan_detail(data_detail, nama_file, kolom):
        hasil = pd.DataFrame(
            data_detail,
            columns=kolom
        )

        hasil.to_csv(
            REPORT_DIR / nama_file,
            index=False
        )

    simpan_detail(
        detail_missing,
        "detail_missing_value.csv",
        ["seri", "kolom", "jumlah_missing"]
    )

    simpan_detail(
        detail_duplikat,
        "detail_duplikasi.csv",
        [
            "seri",
            "var_id",
            "wilayah_id",
            "wilayah",
            "tahun",
            "nilai",
        ]
    )

    simpan_detail(
        detail_rentang,
        "detail_nilai_di_luar_rentang.csv",
        ["seri", "wilayah", "tahun", "nilai"]
    )

    simpan_detail(
        detail_identitas,
        "detail_konsistensi_wilayah.csv",
        [
            "seri",
            "jenis_masalah",
            "identitas",
            "jumlah_perbedaan",
        ]
    )

    print("\n" + "=" * 60)
    print("RINGKASAN PEMERIKSAAN KUALITAS DATA")
    print("=" * 60)

    print(
        pd.DataFrame(
            ringkasan_pemeriksaan
        ).to_string(index=False)
    )

    print("\nHasil pemeriksaan berhasil disimpan di folder reports.")


# ============================================================
# 4. STATISTIK DESKRIPTIF
# ============================================================

def hitung_statistik(df, kolom_grup=None):
    """Menghitung statistik deskriptif dan IQR."""

    def ringkasan(grup):

        nilai = grup["nilai"].dropna()

        q1 = nilai.quantile(0.25)
        q3 = nilai.quantile(0.75)

        return pd.Series({
            "jumlah_data": nilai.count(),
            "mean": nilai.mean(),
            "median": nilai.median(),
            "standar_deviasi": nilai.std(),
            "minimum": nilai.min(),
            "q1": q1,
            "q3": q3,
            "maksimum": nilai.max(),
            "iqr": q3 - q1,
        })

    if kolom_grup:

        return (
            df.groupby(
                kolom_grup,
                dropna=False
            )
            .apply(
                ringkasan,
                include_groups=False
            )
            .reset_index()
        )

    return ringkasan(df).to_frame().T


def buat_statistik(data):
    """Membuat statistik per seri, provinsi, dan nasional."""

    statistik_seri = []
    statistik_provinsi = []
    statistik_nasional = []

    for kode, df in data.items():

        # Memisahkan agregat nasional dari provinsi
        provinsi = df[
            df["wilayah"].str.strip().str.upper() != "INDONESIA"
        ].copy()

        nasional = df[
            df["wilayah"].str.strip().str.upper() == "INDONESIA"
        ].copy()

        # Statistik keseluruhan provinsi
        hasil_seri = hitung_statistik(provinsi)
        hasil_seri.insert(0, "seri", kode)

        statistik_seri.append(hasil_seri)

        # Statistik per provinsi
        hasil_provinsi = hitung_statistik(
            provinsi,
            ["wilayah"]
        )

        hasil_provinsi.insert(0, "seri", kode)

        statistik_provinsi.append(hasil_provinsi)

        # Statistik nasional
        if not nasional.empty:

            hasil_nasional = hitung_statistik(nasional)
            hasil_nasional.insert(0, "seri", kode)

            statistik_nasional.append(hasil_nasional)

        print("\n" + "=" * 60)
        print(f"STATISTIK DESKRIPTIF {kode}")
        print("=" * 60)

        print(
            "Jumlah observasi provinsi:",
            len(provinsi)
        )

        print(
            "Jumlah observasi nasional:",
            len(nasional)
        )

        print(
            "Jumlah nama provinsi unik:",
            provinsi["wilayah"].nunique()
        )

        print("\nStatistik keseluruhan provinsi:")
        print(hasil_seri.to_string(index=False))

        print("\nStatistik nasional:")

        if not nasional.empty:
            print(hasil_nasional.to_string(index=False))
        else:
            print("Tidak tersedia.")

    # Menggabungkan hasil statistik
    hasil_seri = pd.concat(
        statistik_seri,
        ignore_index=True
    )

    hasil_provinsi = pd.concat(
        statistik_provinsi,
        ignore_index=True
    )

    hasil_seri.to_csv(
        REPORT_DIR / "statistik_deskriptif_seri.csv",
        index=False
    )

    hasil_provinsi.to_csv(
        REPORT_DIR / "statistik_deskriptif_provinsi.csv",
        index=False
    )

    if statistik_nasional:

        hasil_nasional = pd.concat(
            statistik_nasional,
            ignore_index=True
        )

        hasil_nasional.to_csv(
            REPORT_DIR / "statistik_deskriptif_nasional.csv",
            index=False
        )

    print("\nFile statistik berhasil disimpan di folder reports.")


# ============================================================
# 5. PROGRAM UTAMA
# ============================================================

if __name__ == "__main__":

    # Membuat folder laporan jika belum tersedia
    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Membaca data
    data = baca_data()

    # Melakukan pemeriksaan kualitas
    periksa_data(data)

    # Menghitung statistik deskriptif
    buat_statistik(data)

    print("\n" + "=" * 60)
    print("PROSES PROFIL DATA SELESAI")
    print("=" * 60)
