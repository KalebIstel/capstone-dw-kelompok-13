"""Backlog 8 (Tahap 3): kategori tiap kandidat anomali. Hanya menandai, tidak mengubah nilai Silver.

Kategori:
- patahan_diduga : tahun itu serentak (>= AMBANG wilayah bergerak searah dibanding tahun sebelumnya)
                   dan kandidat bergerak searah dengan mayoritas.
- outlier_asli   : selain itu; ekstrem pada wilayah tertentu tanpa pola serentak.
- galat_input    : hanya bila nilai di luar RASIO_MIN-RASIO_MAKS kali median wilayahnya.
"""
import numpy as np
import pandas as pd

AMBANG = 0.80
RASIO_MIN, RASIO_MAKS = 0.5, 2.0
EVAL = "reports/evaluasi_anomali_per_tahun.csv"
KANDIDAT = "reports/daftar_final_kandidat_anomali.csv"
OUT_KATEGORI = "reports/kategori_anomali.csv"
OUT_TAHUN = "reports/tahun_serentak.csv"


def _panel(e):
    return {s: g.pivot_table(index="wilayah", columns="tahun", values="nilai") for s, g in e.groupby("seri")}


def tahun_serentak(panel):
    baris = []
    for seri, p in panel.items():
        d = p.diff(axis=1).iloc[:, 1:]
        for t in d.columns:
            x = d[t].dropna()
            naik, turun = (x > 0).mean(), (x < 0).mean()
            arah = "naik" if naik >= AMBANG else "turun" if turun >= AMBANG else "tidak serentak"
            baris.append({"seri": seri, "tahun": int(t), "n_wilayah": len(x),
                          "pct_naik": round(naik * 100, 2), "pct_turun": round(turun * 100, 2),
                          "arah_serentak": arah})
    return pd.DataFrame(baris)


def kategorikan(k, panel, ts):
    kali = k.groupby(["seri", "wilayah"]).size()
    hasil = []
    for r in k.itertuples():
        deret = panel[r.seri].loc[r.wilayah]
        rasio = r.nilai / deret.median()
        sebelum = deret.get(r.tahun - 1, np.nan)
        arah_w = None if pd.isna(sebelum) else ("naik" if r.nilai > sebelum else "turun")
        t = ts[(ts.seri == r.seri) & (ts.tahun == r.tahun)]
        t = t.iloc[0] if len(t) else None
        arah_s = t.arah_serentak if t is not None else "tidak ada"
        pct = None
        if t is not None and arah_w:
            pct = t.pct_naik if arah_w == "naik" else t.pct_turun
        n = kali[(r.seri, r.wilayah)]

        if rasio > RASIO_MAKS or rasio < RASIO_MIN:
            kat = "galat_input"
            alasan = f"nilai {rasio:.2f}x median wilayahnya, di luar {RASIO_MIN}-{RASIO_MAKS}x"
        elif arah_w is None:
            kat = "outlier_asli"
            alasan = f"tahun pertama wilayah, tidak ada pembanding; wilayah ini kandidat {n} kali"
        elif arah_s == arah_w:
            kat = "patahan_diduga"
            alasan = (f"{pct:.0f}% wilayah bergerak {arah_w} pada {r.tahun}, searah dengan kandidat; "
                      "metadata BPS tidak mengonfirmasi perubahan definisi, bisa juga kejadian riil")
        else:
            kat = "outlier_asli"
            if arah_s in ("tidak serentak", "tidak ada"):
                ket = f"hanya {pct:.0f}% wilayah bergerak {arah_w}, tidak serentak"
            else:
                ket = f"gerak kandidat ({arah_w}) berlawanan dengan arah serentak ({arah_s})"
            alasan = f"{ket}; wilayah ini kandidat {n} kali"

        hasil.append({"seri": r.seri, "tahun": r.tahun, "wilayah": r.wilayah, "nilai": r.nilai,
                      "nilai_tahun_sebelumnya": sebelum, "arah_wilayah": arah_w,
                      "arah_serentak": arah_s, "pct_searah": pct,
                      "rasio_median_wilayah": round(rasio, 3), "kategori": kat,
                      "alasan": alasan, "nilai_diubah": "tidak"})
    return pd.DataFrame(hasil)


def main():
    e, k = pd.read_csv(EVAL), pd.read_csv(KANDIDAT)
    panel = _panel(e)
    ts = tahun_serentak(panel)
    hasil = kategorikan(k, panel, ts)
    ts.to_csv(OUT_TAHUN, index=False)
    hasil.to_csv(OUT_KATEGORI, index=False)
    print(f"kandidat: {len(hasil)} | ambang serentak: {AMBANG:.0%}")
    print(hasil.kategori.value_counts().to_string())
    print("tahun serentak:")
    print(ts[ts.arah_serentak != "tidak serentak"].to_string(index=False))


if __name__ == "__main__":
    main()