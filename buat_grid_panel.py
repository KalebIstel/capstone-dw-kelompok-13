
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data/raw/bps/2026-10-17")
REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

FILES = {
    "var1186": DATA_DIR / "sdg8_neet.csv",
    "var2658": DATA_DIR / "sdg8_8_7_1_v2658.csv",
}

PROVINSI_BARU = {
    "PAPUA BARAT DAYA",
    "PAPUA PEGUNUNGAN",
    "PAPUA SELATAN",
    "PAPUA TENGAH",
}

# Daftar acuan 38 provinsi berdasarkan data NEET tahun 2025
df_acuan = pd.read_csv(FILES["var1186"])
provinsi = sorted(
    df_acuan.loc[
        (df_acuan["tahun"] == 2025)
        & (df_acuan["wilayah"].str.upper() != "INDONESIA"),
        "wilayah"
    ].unique()
)

assert len(provinsi) == 38, "Daftar acuan bukan 38 provinsi."

semua_ringkasan = []

for seri, path in FILES.items():
    df = pd.read_csv(path)

    # Pisahkan data nasional dari panel provinsi
    nasional = df[df["wilayah"].str.upper() == "INDONESIA"].copy()
    df = df[df["wilayah"].str.upper() != "INDONESIA"].copy()

    tahun_list = sorted(df["tahun"].unique())

    # Bentuk grid lengkap tahun x 38 provinsi
    grid = pd.MultiIndex.from_product(
        [tahun_list, provinsi],
        names=["tahun", "wilayah"]
    ).to_frame(index=False)

    grid = grid.merge(
        df[["tahun", "wilayah", "nilai"]],
        on=["tahun", "wilayah"],
        how="left",
        validate="one_to_one"
    )

    grid["seri"] = seri

    def status_wilayah(row):
        if row["wilayah"] not in PROVINSI_BARU:
            return "eligible"
        if row["tahun"] < 2022:
            return "belum_terbentuk"
        if row["tahun"] == 2022:
            return "masa_transisi"
        return "eligible"

    grid["status_wilayah"] = grid.apply(status_wilayah, axis=1)

    grid["status_data"] = "tersedia"
    grid.loc[
        grid["status_wilayah"] == "belum_terbentuk",
        "status_data"
    ] = "belum_terbentuk"
    grid.loc[
        grid["status_wilayah"] == "masa_transisi",
        "status_data"
    ] = "masa_transisi"
    grid.loc[
        (grid["status_wilayah"] == "eligible")
        & grid["nilai"].isna(),
        "status_data"
    ] = "missing"

    grid = grid[
        [
            "seri", "tahun", "wilayah", "nilai",
            "status_wilayah", "status_data"
        ]
    ]

    grid.to_csv(
        REPORT_DIR / f"grid_panel_{seri}.csv",
        index=False
    )

    # Ringkasan kelengkapan hanya menghitung wilayah eligible
    for tahun in tahun_list:
        bagian = grid[
            (grid["tahun"] == tahun)
            & (grid["status_wilayah"] == "eligible")
        ]

        eligible = len(bagian)
        terisi = bagian["nilai"].notna().sum()
        missing = eligible - terisi

        semua_ringkasan.append({
            "seri": seri,
            "tahun": tahun,
            "jumlah_provinsi_eligible": eligible,
            "jumlah_terisi": int(terisi),
            "jumlah_missing": int(missing),
            "persen_terisi": round(
                terisi / eligible * 100, 2
            ) if eligible else 0
        })

    print(f"\n{seri}:")
    print(
        grid.groupby(["tahun", "status_data"])
        .size()
        .unstack(fill_value=0)
        .to_string()
    )

    print(
        f"Baris nasional yang dipisahkan: {len(nasional)}"
    )

ringkasan = pd.DataFrame(semua_ringkasan)
ringkasan.to_csv(
    REPORT_DIR / "kelengkapan_panel_per_tahun.csv",
    index=False
)

print("\nRingkasan kelengkapan:")
print(ringkasan.to_string(index=False))

print("\nTiga laporan berhasil dibuat di folder reports/.")
