"""Aturan validasi dasar tabel Silver menggunakan Pandera (Kasus 13)."""

from pathlib import Path
import pandas as pd
import pandera.pandas as pa
from pandera.pandas import Check, Column, DataFrameSchema

SUMBER_SAH = {"bps", "wdi", "ilostat"}

SERI_SAH = {
    "var1186",
    "var2658",
    "SL.TLF.0714.ZS",
    "SL.UEM.NEET.ZS",
    "SDG_0861_SEX_RT",
    "SDG_A871_SEX_AGE_RT",
    "SDG_B871_SEX_AGE_RT",
}

RINCIAN_TERDAFTAR = {
    "total",
    "laki-laki",
    "perempuan",
    "15-17",
    "laki-laki_15-17",
    "perempuan_15-17",
}

WILAYAH_SAH = {
    9999,
    1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2100,
    3100, 3200, 3300, 3400, 3500, 3600,
    5100, 5200, 5300,
    6100, 6200, 6300, 6400, 6500,
    7100, 7200, 7300, 7400, 7500, 7600,
    8100, 8200,
    9100, 9200, 9300, 9400, 9500, 9600, 9700,
}

skema_silver = DataFrameSchema(
    columns={
        "sumber": Column(str, Check.isin(SUMBER_SAH), nullable=False),
        "seri_kode": Column(str, Check.isin(SERI_SAH), nullable=False),
        "wilayah_kode": Column(int, Check.isin(WILAYAH_SAH), nullable=False, coerce=True),
        "nama_wilayah": Column(str, Check(lambda s: s.str.strip().str.len() > 0), nullable=False),
        "periode": Column(str, Check.str_matches(r"^\d{4}$"), nullable=False),
        "jenis_periode": Column(str, Check.isin(["tahun"]), nullable=False),
        "rincian": Column(
            str,
            Check.isin(
                RINCIAN_TERDAFTAR,
                error="Ditemukan rincian yang tidak terdaftar di docs/data-dictionary.md",
            ),
            nullable=False,
        ),
        "nilai": Column(float, nullable=False, coerce=True),
        "satuan": Column(str, Check.isin(["persen"]), nullable=False),
        "_berkas_raw": Column(str, Check(lambda s: s.str.strip().str.len() > 0), nullable=False),
        "_sha256_raw": Column(str, Check.str_matches(r"^[0-9a-fA-F]{64}$"), nullable=False),
    },
    checks=[
        Check(
            lambda df: df.loc[df["satuan"] == "persen", "nilai"].between(0, 100).all(),
            error="Nilai dengan satuan 'persen' berada di luar rentang 0-100",
        ),
        Check(
            lambda df: (df.groupby("seri_kode")["satuan"].nunique() == 1).all(),
            error="Ditemukan seri_kode dengan satuan ganda",
        ),
        Check(
            lambda df: set(df["seri_kode"].unique()) == SERI_SAH,
            error="Daftar seri_kode di Silver tidak lengkap sesuai 7 seri Kasus 13",
        ),
        Check(
            lambda df: df["_berkas_raw"].notna().all() and df["_sha256_raw"].notna().all(),
            error="Ditemukan baris Silver tanpa jejak _berkas_raw atau _sha256_raw",
        ),
    ],
    unique=["sumber", "seri_kode", "wilayah_kode", "periode", "rincian", "_berkas_raw"],
    strict=False,
)


def validasi_silver(df_silver: pd.DataFrame | None = None) -> dict:
    """Menjalankan validasi skema Pandera pada Silver dan menulis laporan ringkas."""
    if df_silver is None:
        df_silver = pd.read_parquet("data/silver/silver.parquet")

    df_lolos = skema_silver.validate(df_silver, lazy=True)

    jumlah_aturan = len(skema_silver.columns) + len(skema_silver.checks) + 1
    ringkasan = {
        "aturan_validasi": jumlah_aturan,
        "aturan_lolos": jumlah_aturan,
        "baris_silver": len(df_lolos),
    }

    tulis_laporan_validasi(df_lolos, ringkasan)
    print(
        f"[VALIDASI SILVER] Lolos {ringkasan['aturan_lolos']}/{ringkasan['aturan_validasi']} "
        f"aturan untuk {ringkasan['baris_silver']} baris."
    )
    return ringkasan


def tulis_laporan_validasi(df_silver: pd.DataFrame, ringkasan: dict) -> None:
    """Menyimpan laporan hasil validasi dasar Silver ke reports/validasi.md."""
    Path("reports").mkdir(parents=True, exist_ok=True)
    isi = f"""# Laporan Validasi Otomatis — Kelompok 13

## Ringkasan Validasi Silver (Sprint 1)

- **Status:** LOLOS ({ringkasan['aturan_lolos']}/{ringkasan['aturan_validasi']} aturan)
- **Total baris tervalidasi:** {ringkasan['baris_silver']} baris
- **Library:** Pandera (`src/validasi/validasi_silver.py`)

### Daftar Aturan Dasar yang Diuji

1. **Kelengkapan & tipe 11 kolom wajib Silver:** `sumber`, `seri_kode`, `wilayah_kode`, `nama_wilayah`, `periode`, `jenis_periode`, `rincian`, `nilai`, `satuan`, `_berkas_raw`, `_sha256_raw`.
2. **Rentang nilai masuk akal:** Seluruh nilai bersatuan `persen` berada pada rentang `0` hingga `100` (aktual: `{df_silver['nilai'].min():.2f}` s.d. `{df_silver['nilai'].max():.2f}`).
3. **Keunikan kunci komposit:** Kombinasi `[sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw]` unik tanpa duplikat.
4. **Konsistensi satuan & rincian:** Setiap `seri_kode` memiliki tepat satu satuan (`persen`), seluruh 7 seri Kasus 13 hadir lengkap, dan nilai `rincian` sesuai dengan daftar pada `docs/data-dictionary.md`.
5. **Integritas wilayah & lineage:** `wilayah_kode` hanya berisi kode 38 provinsi BPS (`1100`–`9700`) atau `9999` (Indonesia), dan setiap baris memiliki `_berkas_raw` serta `_sha256_raw` (SHA-256 64 karakter heksadesimal).

*(Validasi tabel Gold dan penelusuran lineage baris Gold ke `_berkas_raw` akan ditambahkan pada Sprint 2–3 setelah panel Gold terbentuk.)*
"""
    Path("reports/validasi.md").write_text(isi, encoding="utf-8")