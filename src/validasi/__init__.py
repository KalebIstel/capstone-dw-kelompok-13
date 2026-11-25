"""Tahap 8 — Validasi dan dokumentasi (Sprint 1 & Sprint 2).

Menjalankan validasi skema Pandera pada Silver serta validasi aturan Gold dan rekonsiliasi
otomatis melalui pipeline.py.
"""

from src.validasi.validasi_gold import validasi_gold
from src.validasi.validasi_silver import validasi_silver


def jalankan(silver=None, gold=None):
    hasil_silver = validasi_silver(silver)
    hasil_gold = validasi_gold(silver, gold)
    total_aturan = hasil_silver["aturan_validasi"] + hasil_gold["aturan_validasi"]
    total_lolos = hasil_silver["aturan_lolos"] + hasil_gold["aturan_lolos"]
    print(f"[VALIDASI TOTAL] Lolos {total_lolos}/{total_aturan} aturan (Silver + Gold).")
    return {
        "silver": hasil_silver,
        "gold": hasil_gold,
        "aturan_validasi": total_aturan,
        "aturan_lolos": total_lolos,
    }
