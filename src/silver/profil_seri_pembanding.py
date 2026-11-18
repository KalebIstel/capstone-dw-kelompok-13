import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

BPS_DIR = ROOT / "data/raw/bps/2026-10-17"
ILO_DIR = ROOT / "data/raw/ilostat/2026-10-20"
WDI_DIR = ROOT / "data/raw/wdi/2026-10-20"

OUTPUT = ROOT / "reports/ketersediaan_seri_pembanding.csv"


def tahun_csv(path):
    df = pd.read_csv(path)
    return sorted(df["tahun"].dropna().astype(int).unique().tolist())


def tahun_beririsan(tahun_a, tahun_b):
    return sorted(set(tahun_a) & set(tahun_b))


def format_tahun(tahun):
    if not tahun:
        return "Tidak ada"

    return ", ".join(map(str, tahun))


def format_rentang(tahun):
    if not tahun:
        return "Tidak ada"

    if len(tahun) == 1:
        return str(tahun[0])

    return f"{tahun[0]}-{tahun[-1]}"


def metadata_bps(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return data[0]


def profil_bps(nama, csv_path, json_path, definisi, umur):
    df = pd.read_csv(csv_path)
    meta = metadata_bps(json_path)

    tahun = sorted(df["tahun"].dropna().astype(int).unique().tolist())
    tahun_json = sorted(int(x["label"]) for x in meta["tahun"])

    wilayah = sorted(df["wilayah"].dropna().unique().tolist())

    catatan = ""
    if tahun != tahun_json:
        catatan = (
            f"Periode CSV berbeda dengan metadata JSON. "
            f"CSV: {format_tahun(tahun)}; "
            f"JSON: {format_tahun(tahun_json)}. "
            f"Profil menggunakan tahun aktual CSV."
        )

    return {
        "seri": nama,
        "sumber": "BPS",
        "definisi": definisi,
        "wilayah_data": "Indonesia",
        "periode_tersedia": format_tahun(tahun),
        "rentang_periode": format_rentang(tahun),
        "jumlah_tahun": len(tahun),
        "jenis_kelamin": "Tidak tersedia",
        "kelompok_umur": umur,
        "rincian_wilayah": (
            f"{len(wilayah) - 1} provinsi dan Indonesia"
            if "INDONESIA" in wilayah
            else f"{len(wilayah)} wilayah"
        ),
        "satuan": ", ".join(df["satuan"].dropna().unique().tolist()),
        "irisan_tahun_NEET_BPS": "-",
        "irisan_tahun_pekerja_anak_BPS": "-",
        "status_kandidat": "Seri utama",
        "alasan_kandidat": "Digunakan sebagai acuan perbandingan.",
        "catatan": catatan,
    }


def profil_ilo(filename, kode, definisi, umur, status, alasan):
    path = ILO_DIR / "data" / filename
    df = pd.read_csv(path)

    df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
    valid = df[df["OBS_VALUE"].notna()].copy()

    tahun = sorted(valid["TIME_PERIOD"].astype(int).unique().tolist())

    sex_map = {
        "SEX_T": "Total",
        "SEX_M": "Laki-laki",
        "SEX_F": "Perempuan",
    }

    sex = sorted(valid["SEX"].dropna().unique().tolist())
    sex_label = ", ".join(sex_map.get(x, x) for x in sex)

    wilayah = ", ".join(valid["REF_AREA"].dropna().unique().tolist())
    satuan = ", ".join(valid["UNIT_MEASURE"].dropna().unique().tolist())

    return {
        "seri": kode,
        "sumber": "ILOSTAT",
        "definisi": definisi,
        "wilayah_data": wilayah,
        "periode_tersedia": format_tahun(tahun),
        "rentang_periode": format_rentang(tahun),
        "jumlah_tahun": len(tahun),
        "jenis_kelamin": sex_label,
        "kelompok_umur": umur,
        "rincian_wilayah": "Nasional (Indonesia/IDN), tanpa provinsi",
        "satuan": "Persen (PT)",
        "irisan_tahun_NEET_BPS": format_tahun(
            tahun_beririsan(tahun, TAHUN_NEET)
        ),
        "irisan_tahun_pekerja_anak_BPS": format_tahun(
            tahun_beririsan(tahun, TAHUN_ANAK)
        ),
        "status_kandidat": status,
        "alasan_kandidat": alasan,
        "catatan": (
            f"Satuan kode: {satuan}. "
            "Perbandingan wilayah hanya dapat dilakukan pada agregat nasional."
        ),
    }


def profil_wdi(data, kode, definisi, umur, status, alasan):
    observasi = [
        x for x in data[1]
        if x.get("indicator", {}).get("id") == kode
        and x.get("countryiso3code") == "IDN"
        and x.get("value") is not None
    ]

    tahun = sorted({int(x["date"]) for x in observasi})

    return {
        "seri": kode,
        "sumber": "World Bank / WDI",
        "definisi": definisi,
        "wilayah_data": "Indonesia",
        "periode_tersedia": format_tahun(tahun),
        "rentang_periode": format_rentang(tahun),
        "jumlah_tahun": len(tahun),
        "jenis_kelamin": "Total",
        "kelompok_umur": umur,
        "rincian_wilayah": "Nasional (Indonesia), tanpa provinsi",
        "satuan": "Persen",
        "irisan_tahun_NEET_BPS": format_tahun(
            tahun_beririsan(tahun, TAHUN_NEET)
        ),
        "irisan_tahun_pekerja_anak_BPS": format_tahun(
            tahun_beririsan(tahun, TAHUN_ANAK)
        ),
        "status_kandidat": status,
        "alasan_kandidat": alasan,
        "catatan": (
            "Nilai kosong tidak dihitung sebagai tahun tersedia. "
            "Perbandingan wilayah hanya pada agregat nasional."
        ),
    }


# ==========================================================
# 1. PROFIL SERI UTAMA BPS
# ==========================================================

neet = profil_bps(
    "var1186",
    BPS_DIR / "sdg8_neet.csv",
    BPS_DIR / "json/sdg8_neet.json",
    "Persentase usia muda yang tidak sekolah, bekerja, "
    "atau mengikuti pelatihan (NEET).",
    "15-24 tahun",
)

anak = profil_bps(
    "var2658",
    BPS_DIR / "sdg8_8_7_1_v2658.csv",
    BPS_DIR / "json/sdg8_8_7_1_v2658.json",
    "Persentase dan jumlah pekerja anak sesuai metadata SDGs global.",
    "5-17 tahun",
)

TAHUN_NEET = tahun_csv(BPS_DIR / "sdg8_neet.csv")
TAHUN_ANAK = tahun_csv(BPS_DIR / "sdg8_8_7_1_v2658.csv")


# ==========================================================
# 2. PROFIL SERI PEMBANDING ILOSTAT
# ==========================================================

hasil = [neet, anak]

hasil.append(
    profil_ilo(
        "DF_SDG_0861_SEX_RT.csv",
        "SDG_0861_SEX_RT",
        "Proporsi pemuda yang tidak sekolah, bekerja, "
        "atau mengikuti pelatihan (NEET) berdasarkan jenis kelamin.",
        "15-24 tahun",
        "Kandidat utama NEET",
        "Kelompok umur sama dengan BPS NEET. "
        "Gunakan SEX_T (total) karena BPS tidak memiliki rincian "
        "jenis kelamin. Irisan tahun tersedia 2015-2023. "
        "Hanya sebanding pada tingkat nasional.",
    )
)

hasil.append(
    profil_ilo(
        "DF_SDG_A871_SEX_AGE_RT.csv",
        "SDG_A871_SEX_AGE_RT",
        "Proporsi anak yang terlibat dalam aktivitas ekonomi "
        "berdasarkan jenis kelamin dan umur.",
        "Data tersedia: 15-17 tahun; definisi indikator mencakup 5-17 tahun.",
        "Kandidat terbatas pekerja anak",
        "Konsep aktivitas ekonomi anak berkaitan dengan indikator BPS. "
        "Namun, data ILO yang tersedia hanya umur 15-17 tahun, "
        "sedangkan BPS mencakup 5-17 tahun. Irisan tahun hanya 2023. "
        "Tidak dapat dianggap pembanding langsung seluruh kelompok umur.",
    )
)

hasil.append(
    profil_ilo(
        "DF_SDG_B871_SEX_AGE_RT.csv",
        "SDG_B871_SEX_AGE_RT",
        "Proporsi anak yang terlibat dalam aktivitas ekonomi "
        "dan pekerjaan rumah tangga berdasarkan jenis kelamin dan umur.",
        "Data tersedia: 15-17 tahun; definisi indikator mencakup 5-17 tahun.",
        "Bukan kandidat langsung",
        "Konsep mencakup pekerjaan rumah tangga sehingga berbeda "
        "dari indikator pekerja anak BPS. Selain itu, hanya tersedia "
        "tahun 2009 dan tidak ada irisan dengan periode BPS pekerja anak.",
    )
)


# ==========================================================
# 3. PROFIL SERI PEMBANDING WORLD BANK
# ==========================================================

wdi_path = WDI_DIR / "data/kelompok-06-hal-01.json"
wdi_data = json.loads(wdi_path.read_text(encoding="utf-8"))

hasil.append(
    profil_wdi(
        wdi_data,
        "SL.UEM.NEET.ZS",
        "Share of youth not in education, employment or training, "
        "total (% of youth population).",
        "15-24 tahun",
        "Kandidat utama NEET",
        "Kelompok umur sama dengan BPS NEET. "
        "Data total tanpa pemisahan jenis kelamin. "
        "Irisan tahun tersedia 2015-2023. "
        "Hanya sebanding pada tingkat nasional.",
    )
)

hasil.append(
    profil_wdi(
        wdi_data,
        "SL.TLF.0714.ZS",
        "Children in employment, total "
        "(% of children ages 7-14).",
        "7-14 tahun",
        "Bukan kandidat langsung",
        "Kelompok umur berbeda dari BPS pekerja anak (5-17 tahun). "
        "Data yang tersedia hanya tahun 2000, 2009, dan 2010, "
        "sehingga tidak memiliki irisan tahun dengan periode BPS.",
    )
)


# ==========================================================
# 4. SIMPAN TABEL
# ==========================================================

kolom = [
    "seri",
    "sumber",
    "definisi",
    "wilayah_data",
    "periode_tersedia",
    "rentang_periode",
    "jumlah_tahun",
    "jenis_kelamin",
    "kelompok_umur",
    "rincian_wilayah",
    "satuan",
    "irisan_tahun_NEET_BPS",
    "irisan_tahun_pekerja_anak_BPS",
    "status_kandidat",
    "alasan_kandidat",
    "catatan",
]

df_hasil = pd.DataFrame(hasil)[kolom]

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
df_hasil.to_csv(OUTPUT, index=False, encoding="utf-8-sig")

print("=" * 70)
print("PROFIL KETERSEDIAAN SERI PEMBANDING")
print("=" * 70)
print(df_hasil[
    ["seri", "periode_tersedia", "kelompok_umur",
     "status_kandidat"]
].to_string(index=False))

print("\nFile berhasil disimpan:", OUTPUT)
print("Jumlah seri:", len(df_hasil))
print("=" * 70)
