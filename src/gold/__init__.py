"""Tahap 4–6 — Reshape, integrasi, dan penyimpanan ke Gold (pertemuan VII, IX, XI, XII). Milik tim.

Keluaran: data/gold/*.parquet (panel provinsi x tahun x indikator siap analisis, plus tabel
rekonsiliasi dengan pembanding nasional) dan basis data SQL (data/gold/capstone.duckdb).
"""
from src.gold.aturan_gold import bangun_panel_gold
from src.gold.muat_sql import cetak_ringkasan_sql, muat_semua_ke_sql
from src.gold.rekonsiliasi import simpan_rekonsiliasi
from src.gold.tabel_nasional import simpan_tabel_nasional


def jalankan(silver=None):
    """Terima Silver, terapkan aturan Gold, tulis panel, tabel nasional, & basis data DuckDB."""
    panel, ringkasan = bangun_panel_gold(silver)
    snap = ringkasan["snapshot"]
    per = ringkasan["periode"]
    cak = ringkasan["cakupan"]
    jejak = ringkasan["ketertelusuran"]
    anom = ringkasan["panel"]["penanda_anomali"]
    print(
        f"Panel Gold tersimpan di data/gold/panel.parquet ({ringkasan['panel']['total_sel']} sel) | "
        f"Silver tidak terpilih -> snapshot: {snap['baris_tidak_terpilih']}, "
        f"sub-tahunan: {per['baris_tidak_terpilih']}, "
        f"nasional/rincian non-panel: {cak['baris_tidak_masuk_panel']} | "
        f"tertelusur Silver: {jejak['sel_tertelusur']}/{jejak['sel_terisi']} | "
        f"penanda anomali: {anom.get('outlier_asli', 0)} outlier_asli, {anom.get('patahan_diduga', 0)} patahan_diduga"
    )
    tabel_nasional = simpan_tabel_nasional(df_silver=silver)
    rekonsiliasi, _ = simpan_rekonsiliasi(tabel_nasional=tabel_nasional)
    hasil_gold = {
        "panel": panel,
        "tabel_nasional": tabel_nasional,
        "rekonsiliasi": rekonsiliasi,
    }
    ringkasan_sql = muat_semua_ke_sql(silver_df=silver, gold_dict=hasil_gold)
    cetak_ringkasan_sql(ringkasan_sql)
    return hasil_gold

