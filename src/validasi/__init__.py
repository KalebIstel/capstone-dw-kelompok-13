"""Tahap 8 — Validasi dan dokumentasi (dimulai sejak Sprint 1).

Skema validasi dasar Silver menggunakan Pandera dijalankan otomatis oleh pipeline.py.
Validasi Gold akan ditambahkan pada Sprint 2-3 setelah tabel Gold terbentuk.
"""

from src.validasi.validasi_silver import validasi_silver


def jalankan(silver=None, gold=None):
    hasil_silver = validasi_silver(silver)
    return {"silver": hasil_silver}