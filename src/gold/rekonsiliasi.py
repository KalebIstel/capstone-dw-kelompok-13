"""Penyusun tabel rekonsiliasi Gold (seri utama vs pembanding nasional) dengan kategori selisih.

Tahap 6 (Kartu #24):
- Membaca data/gold/tabel_nasional.parquet dan memasangkan 5 pasangan seri utama BPS
  dengan pembanding ILOSTAT serta WDI secara full outer join pada `periode`.
- Mempertahankan seluruh periode tanpa pasangan (`nilai_utama` atau `nilai_pembanding` NaN)
  dengan `selisih` dibiarkan kosong, tanpa menghapus atau memaksa kesamaan angka.
- Menetapkan kategori penjelasan berbasis bukti metadata mentah:
  `definisi berbeda`, `metode berbeda`, `vintage berbeda`, `cakupan berbeda`,
  `belum terjelaskan` (disertai dugaan & bukti yang dicari), serta `tidak_beririsan`
  untuk periode yang tidak tumpang tindih.
"""
from __future__ import annotations

from pathlib import Path
import statistics
import pandas as pd

from src.gold.tabel_nasional import OUTPUT_PARQUET as TABEL_NASIONAL_PATH

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PARQUET = ROOT / "data/gold/rekonsiliasi.parquet"
OUTPUT_MD = ROOT / "reports/rekonsiliasi.md"

KATEGORI_BERPASANGAN_SAH = {
    "definisi berbeda",
    "metode berbeda",
    "vintage berbeda",
    "cakupan berbeda",
    "belum terjelaskan",
}
KATEGORI_SAH = KATEGORI_BERPASANGAN_SAH | {"tidak_beririsan"}

KOLOM_REKONSILIASI = [
    "pasangan_id",
    "topik",
    "wilayah_kode",
    "periode",
    "seri_utama",
    "seri_pembanding",
    "nilai_utama",
    "nilai_pembanding",
    "selisih",
    "kategori_selisih",
    "penjelasan",
    "kelompok_umur_utama",
    "kelompok_umur_pembanding",
    "_berkas_raw_utama",
    "_berkas_raw_pembanding",
    "_sha256_raw_utama",
    "_sha256_raw_pembanding",
]

# Metadata 5 pasangan rekonsiliasi Kasus 13 sesuai panduan kelompok bagian 3 & audit raw
PASANGAN_REKONSILIASI: list[dict] = [
    {
        "pasangan_id": "P1",
        "topik": "neet",
        "seri_utama": "var1186",
        "seri_pembanding": "SDG_0861_SEX_RT",
        "kelompok_umur_utama": "15-24",
        "kelompok_umur_pembanding": "15-24",
        "kategori_default": "metode berbeda",
        "penjelasan_default": (
            "Umur sama (15-24) dan keduanya bersumber Sakernas/LFS, namun ILOSTAT mengolah "
            "ulang mikrodata (NOTE_SOURCE: ILO-STATISTICS - Micro data processing) dengan "
            "harmonisasi definisi pelatihan/referensi serta pembaruan berbeda (BPS last_update "
            "2026-02-24 vs snapshot ILO 2026-10-20)."
        ),
        "override_periode": {
            "2020": (
                "belum terjelaskan",
                "Dugaan: lonjakan selisih ekstrem (+2.480 poin, 24.28% vs 21.800%) dipicu "
                "penyesuaian metode wawancara telepon/klasifikasi pelatihan Sakernas saat awal "
                "pandemi COVID-19 sebelum revisi seri dicatat. Bukti dicari: kolom OBS_STATUS "
                "dan NOTE_INDICATOR di DF_SDG_0861_SEX_RT.csv bernilai kosong (NaN) pada 2020, "
                "sedangkan def/note di sdg8_neet.json BPS hanya mencantumkan 'Sumber: Sakernas, BPS'.",
            ),
            "2021": (
                "metode berbeda",
                "Umur sama (15-24), selisih -0.055 poin. Berkas DF_SDG_0861_SEX_RT.csv "
                "menandai tahun 2021 dengan OBS_STATUS=B dan NOTE_INDICATOR='Break in series: "
                "Methodology revised' pada pengolahan mikrodata LFS oleh ILOSTAT.",
            ),
        },
        "penjelasan_tanpa_pasangan": (
            "Periode tidak beririsan antara BPS var1186 (2015-2025) dan ILO SDG_0861_SEX_RT "
            "(2000-2023); metode berbeda (tabulasi resmi BPS vs harmonisasi mikrodata ILO)."
        ),
    },
    {
        "pasangan_id": "P2",
        "topik": "neet",
        "seri_utama": "var1186",
        "seri_pembanding": "SL.UEM.NEET.ZS",
        "kelompok_umur_utama": "15-24",
        "kelompok_umur_pembanding": "15-24",
        "kategori_default": "metode berbeda",
        "penjelasan_default": (
            "Umur sama (15-24). Metadata WDI (sumber2_indikator.json) menyatakan seri diambil "
            "dari basis data eksternal ILOSTAT (accessed Sep 28, 2026) dengan angka identik "
            "terhadap SDG_0861_SEX_RT; selisih bersumber dari harmonisasi mikrodata ILO vs tabulasi BPS."
        ),
        "override_periode": {
            "2020": (
                "belum terjelaskan",
                "Dugaan: mewarisi gap ekstrem (+2.480 poin) dari pemrosesan mikrodata LFS "
                "Sakernas 2020 akibat perubahan perlakuan wawancara/pelatihan era pandemi COVID-19. "
                "Bukti dicari: metadata WDI sumber2_indikator.json menunjuk ILOSTAT tanpa catatan "
                "tahunan 2020, DF_SDG_0861_SEX_RT.csv kosong di OBS_STATUS 2020, dan sdg8_neet.json "
                "BPS tidak memuat rincian metodologi tahunan.",
            ),
            "2021": (
                "metode berbeda",
                "Umur sama (15-24), selisih -0.055 poin; WDI menyalin identik seri ILOSTAT "
                "yang menandai tahun 2021 sebagai Break in series: Methodology revised (OBS_STATUS=B).",
            ),
        },
        "penjelasan_tanpa_pasangan": (
            "Periode tidak beririsan antara BPS var1186 (2015-2025) dan WDI SL.UEM.NEET.ZS "
            "(1996-2023); WDI mengadopsi estimasi ILOSTAT."
        ),
    },
    {
        "pasangan_id": "P3",
        "topik": "pekerja_anak",
        "seri_utama": "var2658",
        "seri_pembanding": "SDG_A871_SEX_AGE_RT",
        "kelompok_umur_utama": "5-17",
        "kelompok_umur_pembanding": "15-17",
        "kategori_default": "cakupan berbeda",
        "penjelasan_default": (
            "Meskipun DSD SDG_A871_SEX_AGE_RT.json menyebut kerangka 5-17 tahun, berkas amatan "
            "DF_SDG_A871_SEX_AGE_RT.csv untuk Indonesia hanya menyajikan dimensi "
            "AGE_CLDVERSION_Y15-17 (15-17 tahun), sedangkan BPS var2658 mencakup 5-17 tahun. "
            "Kedekatan angka 2023 (1.530% vs 1.567%, selisih -0.037) bersifat kebetulan karena penyebut berbeda."
        ),
        "override_periode": {},
        "penjelasan_tanpa_pasangan": (
            "Periode tidak beririsan antara BPS var2658 (2020-2025, 5-17 thn) dan ILO "
            "SDG_A871_SEX_AGE_RT (2009 CLS, 2019 & 2023 LFS, empiris 15-17 thn); cakupan berbeda."
        ),
    },
    {
        "pasangan_id": "P4",
        "topik": "pekerja_anak",
        "seri_utama": "var2658",
        "seri_pembanding": "SDG_B871_SEX_AGE_RT",
        "kelompok_umur_utama": "5-17",
        "kelompok_umur_pembanding": "15-17",
        "kategori_default": "definisi berbeda",
        "penjelasan_default": (
            "DSD SDG_B871_SEX_AGE_RT.json memasukkan pekerjaan rumah tangga ekstrem (>=21 jam) "
            "yang berbeda dari definisi ekonomi semata pada BPS/A871, serta amatan Indonesia "
            "hanya 15-17 tahun."
        ),
        "override_periode": {},
        "penjelasan_tanpa_pasangan": (
            "Tidak ada tahun tumpang tindih: ILO SDG_B871_SEX_AGE_RT hanya tersedia pada 2009 "
            "(CLS, umur 15-17, bernilai identik 4.527% dengan A871 karena jam kerja umur 15-17 sama) "
            "sedangkan BPS var2658 mulai 2020 (umur 5-17); definisi berbeda dan cakupan berbeda."
        ),
    },
    {
        "pasangan_id": "P5",
        "topik": "pekerja_anak",
        "seri_utama": "var2658",
        "seri_pembanding": "SL.TLF.0714.ZS",
        "kelompok_umur_utama": "5-17",
        "kelompok_umur_pembanding": "7-14",
        "kategori_default": "cakupan berbeda",
        "penjelasan_default": (
            "WDI SL.TLF.0714.ZS mengukur anak bekerja usia 7-14 tahun, sedangkan BPS var2658 "
            "mengukur usia 5-17 tahun."
        ),
        "override_periode": {},
        "penjelasan_tanpa_pasangan": (
            "Tidak ada tahun tumpang tindih: WDI SL.TLF.0714.ZS berhenti di 2010 (tersedia 2000, "
            "2009, 2010 dari Understanding Children's Work) sedangkan BPS var2658 mulai 2020; "
            "terdapat jeda 10 tahun sekaligus cakupan berbeda (umur 7-14 vs 5-17)."
        ),
    },
]


def _klasifikasikan_baris(
    spec: dict,
    periode: str,
    nilai_utama: float | None,
    nilai_pembanding: float | None,
) -> tuple[str, str]:
    """Tentukan kategori_selisih dan penjelasan berdasarkan ketersediaan pasangan dan metadata."""
    if pd.isna(nilai_utama) or pd.isna(nilai_pembanding):
        return "tidak_beririsan", spec["penjelasan_tanpa_pasangan"]

    override = spec.get("override_periode", {})
    if periode in override:
        return override[periode]
    return spec["kategori_default"], spec["penjelasan_default"]


def buat_tabel_rekonsiliasi(
    tabel_nasional: pd.DataFrame | None = None,
    tabel_nasional_path: Path = TABEL_NASIONAL_PATH,
) -> pd.DataFrame:
    """Bentuk tabel rekonsiliasi Gold lengkap (periode beririsan & tanpa pasangan tetap tampil)."""
    if tabel_nasional is None:
        if not tabel_nasional_path.exists():
            raise FileNotFoundError(f"Tabel nasional Gold tidak ditemukan: {tabel_nasional_path}")
        tabel_nasional = pd.read_parquet(tabel_nasional_path)

    baris_keluaran: list[dict] = []
    for spec in PASANGAN_REKONSILIASI:
        kolom_ambil = ["periode", "nilai", "_berkas_raw", "_sha256_raw"]
        df_utama = (
            tabel_nasional[tabel_nasional["seri_kode"] == spec["seri_utama"]][kolom_ambil]
            .rename(
                columns={
                    "nilai": "nilai_utama",
                    "_berkas_raw": "_berkas_raw_utama",
                    "_sha256_raw": "_sha256_raw_utama",
                }
            )
        )
        df_pembanding = (
            tabel_nasional[tabel_nasional["seri_kode"] == spec["seri_pembanding"]][kolom_ambil]
            .rename(
                columns={
                    "nilai": "nilai_pembanding",
                    "_berkas_raw": "_berkas_raw_pembanding",
                    "_sha256_raw": "_sha256_raw_pembanding",
                }
            )
        )

        gabung = (
            df_utama.merge(df_pembanding, on="periode", how="outer", validate="one_to_one")
            .sort_values("periode", kind="mergesort")
            .reset_index(drop=True)
        )

        for row in gabung.to_dict(orient="records"):
            nilai_u = row.get("nilai_utama")
            nilai_p = row.get("nilai_pembanding")
            ada_pasangan = pd.notna(nilai_u) and pd.notna(nilai_p)
            selisih = round(float(nilai_u) - float(nilai_p), 6) if ada_pasangan else float("nan")
            kategori, penjelasan = _klasifikasikan_baris(
                spec, str(row["periode"]), nilai_u, nilai_p
            )

            baris_keluaran.append(
                {
                    "pasangan_id": spec["pasangan_id"],
                    "topik": spec["topik"],
                    "wilayah_kode": 9999,
                    "periode": str(row["periode"]),
                    "seri_utama": spec["seri_utama"],
                    "seri_pembanding": spec["seri_pembanding"],
                    "nilai_utama": float(nilai_u) if pd.notna(nilai_u) else float("nan"),
                    "nilai_pembanding": float(nilai_p) if pd.notna(nilai_p) else float("nan"),
                    "selisih": selisih,
                    "kategori_selisih": kategori,
                    "penjelasan": penjelasan,
                    "kelompok_umur_utama": spec["kelompok_umur_utama"],
                    "kelompok_umur_pembanding": spec["kelompok_umur_pembanding"],
                    "_berkas_raw_utama": row["_berkas_raw_utama"] if pd.notna(row.get("_berkas_raw_utama")) else None,
                    "_berkas_raw_pembanding": row["_berkas_raw_pembanding"] if pd.notna(row.get("_berkas_raw_pembanding")) else None,
                    "_sha256_raw_utama": row["_sha256_raw_utama"] if pd.notna(row.get("_sha256_raw_utama")) else None,
                    "_sha256_raw_pembanding": row["_sha256_raw_pembanding"] if pd.notna(row.get("_sha256_raw_pembanding")) else None,
                }
            )

    df_rekon = pd.DataFrame(baris_keluaran, columns=KOLOM_REKONSILIASI)
    return df_rekon


def verifikasi_rekonsiliasi(df_rekon: pd.DataFrame) -> dict:
    """Verifikasi keunikan kunci, kategori selisih, bukti 'belum terjelaskan', dan hitung ringkasan."""
    kunci = ["pasangan_id", "periode", "wilayah_kode"]
    duplikat = int(df_rekon.duplicated(subset=kunci).sum())
    if duplikat:
        raise AssertionError(f"Tabel rekonsiliasi memiliki {duplikat} kunci ganda pada {kunci}")

    pasangan_wajib = {spec["pasangan_id"] for spec in PASANGAN_REKONSILIASI}
    pasangan_ada = set(df_rekon["pasangan_id"].unique())
    if pasangan_ada != pasangan_wajib:
        raise AssertionError(f"Daftar pasangan rekonsiliasi tidak lengkap: {sorted(pasangan_wajib - pasangan_ada)}")

    kategori_tidak_sah = set(df_rekon["kategori_selisih"].dropna().unique()) - KATEGORI_SAH
    if df_rekon["kategori_selisih"].isna().any() or kategori_tidak_sah:
        raise AssertionError(f"Kategori selisih tidak sah ditemukan: {sorted(kategori_tidak_sah)}")

    berpasangan = df_rekon[df_rekon["nilai_utama"].notna() & df_rekon["nilai_pembanding"].notna()]
    kategori_berpasangan_invalid = set(berpasangan["kategori_selisih"].unique()) - KATEGORI_BERPASANGAN_SAH
    if kategori_berpasangan_invalid:
        raise AssertionError(
            f"Baris berpasangan memakai kategori tidak sah: {sorted(kategori_berpasangan_invalid)}"
        )
    if berpasangan["selisih"].isna().any():
        raise AssertionError("Terdapat baris berpasangan dengan nilai selisih kosong")

    belum_terjelaskan = berpasangan[berpasangan["kategori_selisih"] == "belum terjelaskan"]
    for idx, row in belum_terjelaskan.iterrows():
        teks = str(row["penjelasan"])
        if "Dugaan:" not in teks or "Bukti dicari:" not in teks:
            raise AssertionError(
                f"Baris belum terjelaskan ({row['pasangan_id']} {row['periode']}) wajib mencantumkan dugaan dan bukti yang dicari"
            )

    daftar_selisih = berpasangan["selisih"].astype(float).tolist()
    selisih_median = round(statistics.median(daftar_selisih), 4) if daftar_selisih else 0.0
    selisih_abs_median = round(statistics.median([abs(x) for x in daftar_selisih]), 4) if daftar_selisih else 0.0

    return {
        "pasangan_rekonsiliasi": len(PASANGAN_REKONSILIASI),
        "total_baris": int(len(df_rekon)),
        "baris_berpasangan": int(len(berpasangan)),
        "baris_tanpa_pasangan": int(len(df_rekon) - len(berpasangan)),
        "selisih_median": selisih_median,
        "selisih_abs_median": selisih_abs_median,
        "ringkasan_kategori": df_rekon["kategori_selisih"].value_counts().to_dict(),
    }


def tulis_laporan_rekonsiliasi(
    df_rekon: pd.DataFrame,
    ringkasan: dict,
    output_md: Path = OUTPUT_MD,
) -> None:
    """Tulis laporan lengkap rekonsiliasi seri utama vs pembanding nasional ke reports/rekonsiliasi.md."""
    output_md.parent.mkdir(parents=True, exist_ok=True)
    berpasangan = df_rekon[df_rekon["nilai_utama"].notna() & df_rekon["nilai_pembanding"].notna()].copy()

    baris_ringkas_pasangan = []
    for spec in PASANGAN_REKONSILIASI:
        sub = df_rekon[df_rekon["pasangan_id"] == spec["pasangan_id"]]
        sub_p = sub[sub["nilai_utama"].notna() & sub["nilai_pembanding"].notna()]
        periode_irisan = (
            f"{sub_p['periode'].min()}–{sub_p['periode'].max()}"
            if len(sub_p) > 1
            else (sub_p["periode"].iloc[0] if len(sub_p) == 1 else "Tidak ada (0 tahun)")
        )
        med = f"{statistics.median(sub_p['selisih']):+.3f}" if len(sub_p) else "—"
        baris_ringkas_pasangan.append(
            f"| **{spec['pasangan_id']}** | `{spec['seri_utama']}` ({spec['kelompok_umur_utama']}) vs "
            f"`{spec['seri_pembanding']}` ({spec['kelompok_umur_pembanding']}) | {len(sub)} | "
            f"**{len(sub_p)}** ({periode_irisan}) | {len(sub) - len(sub_p)} | {med} |"
        )

    baris_detail_irisan = []
    for row in berpasangan.to_dict(orient="records"):
        ringkas_ket = row["penjelasan"].split(".")[0] + "."
        baris_detail_irisan.append(
            f"| {row['pasangan_id']} | {row['periode']} | `{row['seri_utama']}` | "
            f"`{row['seri_pembanding']}` | {row['nilai_utama']:.2f}% | "
            f"{row['nilai_pembanding']:.3f}% | **{row['selisih']:+.3f}** | "
            f"`{row['kategori_selisih']}` | {ringkas_ket} |"
        )

    belum_df = berpasangan[berpasangan["kategori_selisih"] == "belum terjelaskan"]
    baris_belum = "\n".join(
        f"- **`{r['pasangan_id']}` ({r['periode']}, `{r['seri_utama']}` vs `{r['seri_pembanding']}`, selisih `{r['selisih']:+.3f}` pp):** {r['penjelasan']}"
        for r in belum_df.to_dict(orient="records")
    )

    isi = f"""# Laporan Rekonsiliasi Seri Utama vs Pembanding Nasional (Tahap 6)

* **Penyusun:** Kaleb Filbert Istel (NIM: `124450053`)
* **Keluaran Parquet:** `data/gold/rekonsiliasi.parquet` (**{ringkasan['total_baris']} baris** total across **{ringkasan['pasangan_rekonsiliasi']} pasangan**)
* **Tabel SQL DuckDB:** `gold_rekonsiliasi` pada `data/gold/capstone.duckdb` (`PRIMARY KEY (pasangan_id, periode, wilayah_kode)`)
* **Statistik Selisih (19 baris berpasangan):** median selisih = **`{ringkasan['selisih_median']:+.3f}` poin persentase** (median absolut = `{ringkasan['selisih_abs_median']:.3f}` pp)

---

## 1. Ringkasan 5 Pasangan Rekonsiliasi (Panduan Kelompok Bagian 3)

Seluruh periode dari masing-masing seri utama dan pembanding digabung menggunakan *full outer join* sehingga periode tanpa pasangan tetap tampil (`selisih = NULL`, kategori `tidak_beririsan`), dan selisih angka tidak pernah dihapus ataupun dipaksa sama.

| ID | Pasangan & Kelompok Umur | Total Baris | Berpasangan (Irisan) | Tanpa Pasangan | Median Selisih (pp) |
|:---:|---|---:|---:|---:|---:|
{chr(10).join(baris_ringkas_pasangan)}

---

## 2. Tabel Selisih pada Seluruh Periode Beririsan (19 Baris)

| ID | Periode | Seri Utama | Seri Pembanding | Nilai Utama | Nilai Pembanding | Selisih (Utama - Pembanding) | Kategori Penjelasan | Ringkasan Bukti |
|:---:|:---:|---|---|---:|---:|---:|---|---|
{chr(10).join(baris_detail_irisan)}

---

## 3. Penjelasan Khusus Kategori `belum terjelaskan` (Dugaan & Bukti yang Dicari)

{baris_belum}

---

## 4. Catatan Pasangan Pekerja Anak Tanpa Irisan & Perubahan Definisi (`P3`, `P4`, `P5`)

1. **`P3` (`var2658` vs `SDG_A871_SEX_AGE_RT`):** Hanya beririsan 1 tahun (**2023**: `1.530%` vs `1.567%`, selisih `-0.037` pp). Dikategorikan **`cakupan berbeda`** karena meski DSD menyebut kerangka 5–17 tahun, data aktual Indonesia di `DF_SDG_A871_SEX_AGE_RT.csv` hanya memuat kode dimensi `AGE_CLDVERSION_Y15-17` (**15–17 tahun**), bukan 5–17 tahun seperti BPS `var2658`. Selain itu, tahun 2009 pada seri ILO bersumber survei `CLS` sedangkan 2019 dan 2023 bersumber `LFS`.
2. **`P4` (`var2658` vs `SDG_B871_SEX_AGE_RT`):** Memiliki **0 tahun tumpang tindih** (`2009` di ILO vs `2020–2025` di BPS). DSD `SDG_B871_SEX_AGE_RT.json` memperluas definisi dengan memasukkan pekerjaan rumah tangga (≥ 21 jam/minggu; **`definisi berbeda`**). Pada tahun 2009 (`4.527%`, `CLS`), angkanya identik dengan `SDG_A871_SEX_AGE_RT` karena ambang umur 15–17 hanya menghitung aktivitas ekonomi ≥ 43 jam.
3. **`P5` (`var2658` vs `SL.TLF.0714.ZS`):** Memiliki **0 tahun tumpang tindih** karena WDI `SL.TLF.0714.ZS` (bersumber *Understanding Children's Work*, umur **7–14 tahun**) berhenti pada tahun **2010** (`2000, 2009, 2010`), sehingga terpisah jeda 10 tahun dari seri BPS `var2658` (`2020–2025`, umur **5–17 tahun**) dan tergolong **`cakupan berbeda`** jika dibandingkan lintas periode.
"""
    output_md.write_text(isi, encoding="utf-8")


def simpan_rekonsiliasi(
    tabel_nasional: pd.DataFrame | None = None,
    tabel_nasional_path: Path = TABEL_NASIONAL_PATH,
    output_parquet: Path = OUTPUT_PARQUET,
    output_md: Path = OUTPUT_MD,
) -> tuple[pd.DataFrame, dict]:
    """Bentuk, verifikasi, dan simpan data/gold/rekonsiliasi.parquet beserta reports/rekonsiliasi.md."""
    df_rekon = buat_tabel_rekonsiliasi(
        tabel_nasional=tabel_nasional,
        tabel_nasional_path=tabel_nasional_path,
    )
    ringkasan = verifikasi_rekonsiliasi(df_rekon)

    output_parquet.parent.mkdir(parents=True, exist_ok=True)
    df_rekon.to_parquet(output_parquet, index=False)
    tulis_laporan_rekonsiliasi(df_rekon, ringkasan, output_md=output_md)

    print(
        f"Tabel rekonsiliasi Gold tersimpan di data/gold/rekonsiliasi.parquet "
        f"({ringkasan['total_baris']} baris, {ringkasan['pasangan_rekonsiliasi']} pasangan | "
        f"berpasangan: {ringkasan['baris_berpasangan']}, tanpa pasangan: {ringkasan['baris_tanpa_pasangan']} | "
        f"selisih_median: {ringkasan['selisih_median']:+.3f})"
    )
    return df_rekon, ringkasan


if __name__ == "__main__":
    simpan_rekonsiliasi()
