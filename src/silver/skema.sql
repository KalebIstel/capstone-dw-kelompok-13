-- =============================================================================
-- Skema Tabel Silver (11 Kolom Baku Skema Starter Capstone Data Wrangling)
-- Sesuai src/common/skema.py dan aturan baku panduan Capstone
-- =============================================================================

CREATE TABLE IF NOT EXISTS silver (
    sumber          VARCHAR(16)  NOT NULL,
    seri_kode       VARCHAR(64)  NOT NULL,
    wilayah_kode    INTEGER      NOT NULL,
    nama_wilayah    VARCHAR(64)  NOT NULL,
    periode         VARCHAR(10)  NOT NULL,
    jenis_periode   VARCHAR(16)  NOT NULL,
    rincian         VARCHAR(64)  NOT NULL,
    nilai           REAL         NOT NULL,
    satuan          VARCHAR(16)  NOT NULL,
    _berkas_raw     VARCHAR(255) NOT NULL,
    _sha256_raw     VARCHAR(64)  NOT NULL,
    
    -- Kunci primer komposit 6 atribut sesuai aturan keunikan skema Silver
    PRIMARY KEY (sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw),
    
    -- Batasan validasi integritas data
    CHECK (nilai >= 0.0 AND nilai <= 100.0),
    CHECK (jenis_periode IN ('tahun', 'semester', 'triwulan', 'bulan')),
    CHECK (wilayah_kode = 9999 OR (wilayah_kode >= 1100 AND wilayah_kode <= 9700))
);

-- Indeks sekunder untuk efisiensi kueri analitis
CREATE INDEX IF NOT EXISTS idx_silver_seri_periode ON silver (seri_kode, periode);
CREATE INDEX IF NOT EXISTS idx_silver_wilayah ON silver (wilayah_kode);
CREATE INDEX IF NOT EXISTS idx_silver_sumber ON silver (sumber);
