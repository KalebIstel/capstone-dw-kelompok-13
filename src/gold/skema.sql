-- =============================================================================
-- Skema Basis Data Relasional Terpadu: Silver dan Gold (DuckDB / ANSI SQL)
-- Kasus 13: Pemuda NEET (SDG 8.6.1) dan Pekerja Anak (SDG 8.7.1)
-- =============================================================================

-- 1. Tabel Silver: observasi panjang terstandarisasi dan ber-lineage lengkap
CREATE TABLE IF NOT EXISTS silver (
    sumber          VARCHAR(16)  NOT NULL,
    seri_kode       VARCHAR(64)  NOT NULL,
    wilayah_kode    INTEGER      NOT NULL,
    nama_wilayah    VARCHAR(64)  NOT NULL,
    periode         VARCHAR(10)  NOT NULL,
    jenis_periode   VARCHAR(16)  NOT NULL,
    rincian         VARCHAR(64)  NOT NULL,
    nilai           DOUBLE       NOT NULL,
    satuan          VARCHAR(16)  NOT NULL,
    _berkas_raw     VARCHAR(255) NOT NULL,
    _sha256_raw     VARCHAR(64)  NOT NULL,

    PRIMARY KEY (sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw),

    CHECK (nilai >= 0.0 AND nilai <= 100.0),
    CHECK (jenis_periode IN ('tahun', 'semester', 'triwulan', 'bulan')),
    CHECK (wilayah_kode = 9999 OR (wilayah_kode >= 1100 AND wilayah_kode <= 9700))
);

CREATE INDEX IF NOT EXISTS idx_silver_seri_periode ON silver (seri_kode, periode);
CREATE INDEX IF NOT EXISTS idx_silver_wilayah ON silver (wilayah_kode);
CREATE INDEX IF NOT EXISTS idx_silver_sumber ON silver (sumber);


-- 2. Tabel Gold Panel: grid lengkap 38 provinsi x tahun x indikator utama BPS
-- Catatan: kolom nilai, penanda/catatan anomali, dan lineage mengizinkan NULL
-- khusus untuk sel kosong struktural (status_data != 'tersedia').
CREATE TABLE IF NOT EXISTS gold_panel (
    seri_kode             VARCHAR(64)  NOT NULL,
    indikator             VARCHAR(64)  NOT NULL,
    wilayah_kode          INTEGER      NOT NULL,
    nama_wilayah          VARCHAR(64)  NOT NULL,
    periode               VARCHAR(10)  NOT NULL,
    sumber                VARCHAR(16)  NOT NULL,
    rincian               VARCHAR(64)  NOT NULL,
    nilai                 DOUBLE,
    satuan                VARCHAR(16)  NOT NULL,
    status_wilayah        VARCHAR(32)  NOT NULL,
    status_data           VARCHAR(32)  NOT NULL,
    penanda_anomali       VARCHAR(32),
    arah_serentak_tahun   VARCHAR(32),
    catatan_anomali       VARCHAR(512),
    snapshot_tanggal      VARCHAR(16),
    _berkas_raw           VARCHAR(255),
    _sha256_raw           VARCHAR(64),

    PRIMARY KEY (wilayah_kode, periode, seri_kode),

    CHECK (nilai IS NULL OR (nilai >= 0.0 AND nilai <= 100.0)),
    CHECK (wilayah_kode >= 1100 AND wilayah_kode <= 9700),
    CHECK (status_wilayah IN ('eligible', 'belum_terbentuk', 'masa_transisi')),
    CHECK (status_data IN ('tersedia', 'belum_terbentuk', 'masa_transisi', 'missing'))
);

CREATE INDEX IF NOT EXISTS idx_gold_panel_indikator_periode ON gold_panel (indikator, periode);
CREATE INDEX IF NOT EXISTS idx_gold_panel_status_data ON gold_panel (status_data);


-- 3. Tabel Gold Nasional: seri utama BPS vs pembanding global (1 baris per periode x seri)
CREATE TABLE IF NOT EXISTS gold_tabel_nasional (
    periode           VARCHAR(10)  NOT NULL,
    seri_kode         VARCHAR(64)  NOT NULL,
    topik             VARCHAR(32)  NOT NULL,
    indikator         VARCHAR(64)  NOT NULL,
    peran_seri        VARCHAR(16)  NOT NULL,
    asal_angka        VARCHAR(32)  NOT NULL,
    sumber            VARCHAR(16)  NOT NULL,
    wilayah_kode      INTEGER      NOT NULL,
    nama_wilayah      VARCHAR(64)  NOT NULL,
    rincian           VARCHAR(64)  NOT NULL,
    kelompok_umur     VARCHAR(16)  NOT NULL,
    nilai             DOUBLE       NOT NULL,
    satuan            VARCHAR(16)  NOT NULL,
    snapshot_tanggal  VARCHAR(16)  NOT NULL,
    _berkas_raw       VARCHAR(255) NOT NULL,
    _sha256_raw       VARCHAR(64)  NOT NULL,

    PRIMARY KEY (periode, seri_kode),

    CHECK (nilai >= 0.0 AND nilai <= 100.0),
    CHECK (wilayah_kode = 9999),
    CHECK (peran_seri IN ('utama', 'pembanding')),
    CHECK (asal_angka IN ('baris_indonesia', 'agregat_provinsi', 'pembanding'))
);

CREATE INDEX IF NOT EXISTS idx_gold_nasional_topik_periode ON gold_tabel_nasional (topik, periode);


-- 4. Tabel Gold Rekonsiliasi: penyandingan seri utama vs pembanding nasional dan kategori selisih
-- Dimuat otomatis apabila keluaran rekonsiliasi Tahap 6 (data/gold/rekonsiliasi.parquet) tersedia.
CREATE TABLE IF NOT EXISTS gold_rekonsiliasi (
    pasangan_id               VARCHAR(32)  NOT NULL,
    topik                     VARCHAR(32)  NOT NULL,
    wilayah_kode              INTEGER      NOT NULL,
    periode                   VARCHAR(10)  NOT NULL,
    seri_utama                VARCHAR(64)  NOT NULL,
    seri_pembanding           VARCHAR(64)  NOT NULL,
    nilai_utama               DOUBLE,
    nilai_pembanding          DOUBLE,
    selisih                   DOUBLE,
    kategori_selisih          VARCHAR(32)  NOT NULL,
    penjelasan                VARCHAR(512) NOT NULL,
    kelompok_umur_utama       VARCHAR(16)  NOT NULL,
    kelompok_umur_pembanding  VARCHAR(16)  NOT NULL,
    _berkas_raw_utama         VARCHAR(255),
    _berkas_raw_pembanding    VARCHAR(255),
    _sha256_raw_utama         VARCHAR(64),
    _sha256_raw_pembanding    VARCHAR(64),

    PRIMARY KEY (pasangan_id, periode, wilayah_kode),

    CHECK (nilai_utama IS NULL OR (nilai_utama >= 0.0 AND nilai_utama <= 100.0)),
    CHECK (nilai_pembanding IS NULL OR (nilai_pembanding >= 0.0 AND nilai_pembanding <= 100.0)),
    CHECK (kategori_selisih IN (
        'definisi berbeda', 'metode berbeda', 'vintage berbeda',
        'cakupan berbeda', 'belum terjelaskan', 'tidak_beririsan'
    ))
);

CREATE INDEX IF NOT EXISTS idx_gold_rekon_topik_periode ON gold_rekonsiliasi (topik, periode);
