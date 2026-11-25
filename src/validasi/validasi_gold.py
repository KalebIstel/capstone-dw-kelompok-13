"""Aturan validasi tabel Gold dan rekonsiliasi (Sprint 2 - Kartu #25)."""

from pathlib import Path
import pandas as pd


def validasi_gold(df_silver: pd.DataFrame | None = None, gold: dict | None = None) -> dict:
    """Menjalankan 4 aturan validasi pada tabel Gold dan rekonsiliasi."""
    if df_silver is None:
        df_silver = pd.read_parquet("data/silver/silver.parquet")

    if gold is None:
        df_panel = pd.read_parquet("data/gold/panel.parquet")
        df_rekonsiliasi = pd.read_parquet("data/gold/tabel_nasional.parquet")
    else:
        df_panel = gold["panel"]
        df_rekonsiliasi = gold["tabel_nasional"]

    hasil_aturan = []

    # 1. Kunci panel unik pada panel Gold
    kunci_panel = ["seri_kode", "wilayah_kode", "periode", "rincian"]
    duplikat_panel = int(df_panel.duplicated(subset=kunci_panel).sum())
    lolos_1 = duplikat_panel == 0
    hasil_aturan.append({
        "nama": "Kunci panel unik",
        "lolos": lolos_1,
        "detail": f"0 duplikat pada {kunci_panel}" if lolos_1 else f"{duplikat_panel} baris duplikat ditemukan",
    })

    # 2. Satuan satu per indikator (pada panel Gold & tabel rekonsiliasi)
    satuan_ganda_panel = int((df_panel.groupby("indikator")["satuan"].nunique() > 1).sum())
    satuan_ganda_rekon = int((df_rekonsiliasi.groupby("indikator")["satuan"].nunique() > 1).sum())
    lolos_2 = (satuan_ganda_panel == 0) and (satuan_ganda_rekon == 0)
    hasil_aturan.append({
        "nama": "Satuan satu per indikator",
        "lolos": lolos_2,
        "detail": "Setiap indikator memiliki tepat 1 satuan" if lolos_2 else f"Satuan ganda: panel={satuan_ganda_panel}, rekon={satuan_ganda_rekon}",
    })

    # 3. Setiap sel Gold yang terisi punya pasangan di Silver
    sel_terisi = df_panel[df_panel["nilai"].notna()].copy()
    sel_terisi["wilayah_kode"] = sel_terisi["wilayah_kode"].astype(int)
    sel_terisi["periode"] = sel_terisi["periode"].astype(str)

    silver_kunci = df_silver[["seri_kode", "wilayah_kode", "periode", "rincian", "nilai"]].copy()
    silver_kunci["wilayah_kode"] = silver_kunci["wilayah_kode"].astype(int)
    silver_kunci["periode"] = silver_kunci["periode"].astype(str)

    gabung = sel_terisi.merge(
        silver_kunci,
        on=["seri_kode", "wilayah_kode", "periode", "rincian"],
        how="left",
        suffixes=("_gold", "_silver"),
    )
    tanpa_pasangan = int(gabung["nilai_silver"].isna().sum())
    lolos_3 = tanpa_pasangan == 0
    hasil_aturan.append({
        "nama": "Setiap sel Gold punya pasangan di Silver",
        "lolos": lolos_3,
        "detail": f"{len(sel_terisi)}/{len(sel_terisi)} sel terisi cocok dengan Silver" if lolos_3 else f"{tanpa_pasangan} sel Gold tanpa pasangan di Silver",
    })

    # 4. Setiap baris rekonsiliasi berpasangan punya kategori lengkap
    kolom_kategori = ["topik", "peran_seri", "asal_angka"]
    kosong_kategori = int(
        df_rekonsiliasi[kolom_kategori]
        .apply(lambda col: col.isna() | (col.astype(str).str.strip() == ""))
        .any(axis=1)
        .sum()
    )
    lolos_4 = (len(df_rekonsiliasi) > 0) and (kosong_kategori == 0)
    hasil_aturan.append({
        "nama": "Setiap baris rekonsiliasi punya kategori",
        "lolos": lolos_4,
        "detail": f"{len(df_rekonsiliasi)}/{len(df_rekonsiliasi)} baris memiliki kategori lengkap ({', '.join(kolom_kategori)})" if lolos_4 else f"{kosong_kategori} baris tanpa kategori lengkap",
    })

    total_aturan = len(hasil_aturan)
    total_lolos = sum(1 for a in hasil_aturan if a["lolos"])

    for idx, a in enumerate(hasil_aturan, start=1):
        status = "LOLOS" if a["lolos"] else "GAGAL"
        print(f"  [{status}] Aturan Gold {idx}: {a['nama']} -> {a['detail']}")

    print(
        f"[VALIDASI GOLD] Lolos {total_lolos}/{total_aturan} aturan "
        f"(panel: {len(df_panel)} sel, rekonsiliasi: {len(df_rekonsiliasi)} baris)."
    )

    if total_lolos < total_aturan:
        gagal = [a["nama"] for a in hasil_aturan if not a["lolos"]]
        raise ValueError(f"Validasi Gold gagal pada aturan: {', '.join(gagal)}")

    ringkasan = {
        "aturan_validasi": total_aturan,
        "aturan_lolos": total_lolos,
        "sel_panel": len(df_panel),
        "sel_terisi": len(sel_terisi),
        "baris_rekonsiliasi": len(df_rekonsiliasi),
        "detail_aturan": hasil_aturan,
    }
    perbarui_laporan_validasi(ringkasan)
    return ringkasan


def perbarui_laporan_validasi(ringkasan: dict) -> None:
    """Menambahkan bagian hasil validasi Gold & rekonsiliasi ke reports/validasi.md."""
    jalur = Path("reports/validasi.md")
    if not jalur.exists():
        return

    isi_lama = jalur.read_text(encoding="utf-8")
    penanda = "## Ringkasan Validasi Gold & Rekonsiliasi (Sprint 2)"
    if penanda in isi_lama:
        isi_lama = isi_lama.split(penanda)[0].rstrip()

    baris_detail = "\n".join(
        f"{i}. **{a['nama']}:** {'LOLOS' if a['lolos'] else 'GAGAL'} — {a['detail']}."
        for i, a in enumerate(ringkasan["detail_aturan"], start=1)
    )

    bagian_gold = f"""

{penanda}

- **Status:** LOLOS ({ringkasan['aturan_lolos']}/{ringkasan['aturan_validasi']} aturan)
- **Total sel panel Gold:** {ringkasan['sel_panel']} sel ({ringkasan['sel_terisi']} terisi, {ringkasan['sel_panel'] - ringkasan['sel_terisi']} kosong struktural)
- **Total baris rekonsiliasi (`tabel_nasional.parquet`):** {ringkasan['baris_rekonsiliasi']} baris
- **Skrip:** `src/validasi/validasi_gold.py` (dipanggil otomatis oleh `pipeline.py` melalui `validasi.jalankan(silver, gold)`)

### Daftar Aturan Gold & Rekonsiliasi yang Diuji

{baris_detail}
"""
    jalur.write_text(isi_lama.rstrip() + bagian_gold, encoding="utf-8")
