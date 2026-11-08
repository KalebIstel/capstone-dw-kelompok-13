## Nama tim dan avatar
Nama tim: A3K
Avatar tim: Naga Bonar

## Komponen tiap anggota
Pilih komponen di kartu Tim saya; tulis di sini alasan pembagiannya.

### Catatan Status Anggota Tim
Tim Kelompok 13 awalnya beranggotakan 5 orang. Namun, **Siti Sarifah Sumamah mengambil cuti akademik pada semester ini** dan tidak lagi aktif dalam perkuliahan maupun pengerjaan capstone. Kondisi ini telah dilaporkan kepada pembimbing (Ardika Satria). 

Untuk memastikan seluruh luaran proyek tetap tercapai secara utuh sesuai standar silabus, beban 5 tahapan utama didistribusikan kepada 4 anggota aktif, di mana komponen *Transformasi dan panel* dikerjakan secara kolaboratif sebagai jembatan antara tahap pembersihan dan integrasi.

---

### Pembagian dan Alasan Komponen

1. **Alfayya Rafif Abiyyi Rosyid Ridlo — Ekstraksi dan lineage (Tahap 1)**
   * **Pilihan Komponen di Sistem:** Ekstraksi dan lineage
   * **Alasan Pembagian:** Kasus 13 memiliki 16 berkas mentah dengan variasi format yang beragam: CSV dan WebAPI JSON dari BPS (`var1186` dan `var2658`), SDMX-CSV beserta DSD JSON dari ILOSTAT (`SDG_0861_SEX_RT`, `SDG_A871_SEX_AGE_RT`, `SDG_B871_SEX_AGE_RT`), dan multi-layer JSON dari WDI (`SL.UEM.NEET.ZS` dan `SL.TLF.0714.ZS`). Alfayya bertanggung jawab membangun fungsi pembaca khusus di `src/ekstraksi/` untuk membaca seluruh format mentah tanpa mengubah berkas aslinya, serta memastikan setiap baris data terikat secara otomatis dengan metadata lineage `_berkas_raw` dan fungsi hash `_sha256_raw` dari `src.common.manifest`.

2. **Ashila Islamisahfa Vanisha — Profil dan pembersihan (Tahap 2–3)**
   * **Pilihan Komponen di Sistem:** Profil dan pembersihan
   * **Alasan Pembagian:** Karakteristik data Kasus 13 memiliki tantangan substantif: rentang seri pekerja anak BPS sangat pendek (2020–2025) dan terdapat perbedaan cakupan indikator dengan data global. Ashila bertugas memetakan kelengkapan grid wilayah $\times$ periode, menyusun profil statistik deskriptif dan deteksi anomali di `src/silver/`, serta membedakan antara nilai hilang (*missing*), sel tidak beririsan (*unaligned period*), dan patahan seri (*series breaks*) akibat perbedaan definisi umur. Semua perlakuan ini dicatat secara kuantitatif ke `log-keputusan.csv`.

3. **Kaleb Filbert Istel — Integrasi, penyimpanan, dan skala (Tahap 5–7)**
   * **Pilihan Komponen di Sistem:** Integrasi, penyimpanan, dan skala
   * **Alasan Pembagian:** Kaleb bertanggung jawab memuat data ke basis data analitis (DuckDB / SQLite), merancang skema relasional berindeks, serta menyusun tabel rekonsiliasi yang membandingkan seri BPS dengan ILOSTAT dan WDI. Mengingat ILO memiliki dua definisi pekerja anak dan WDI menggunakan kelompok umur 7–14 tahun, Kaleb bertugas mengkategorisasikan setiap selisih (definisi, metode, vintage, cakupan) tanpa menghapusnya. Selain itu, Kaleb menguji skalabilitas pipeline terhadap arsip WDI 142 rilis (`python unduh_data.py --arsip-wdi`) dengan membandingkan efisiensi komputasi pandas versus DuckDB/Dask.

4. **Anggun Nita — Validasi dan dokumentasi (Tahap 8, aktif sejak Sprint 1)**
   * **Pilihan Komponen di Sistem:** Validasi dan dokumentasi
   * **Alasan Pembagian:** Sesuai panduan kelompok, komponen validasi tidak menunggu Sprint 3 melainkan dimulai sejak perancangan skema Silver di Sprint 1. Anggun bertanggung jawab merumuskan skema pengujian otomatis menggunakan Pandera / Great Expectations (rentang persentase $0 \le x \le 100$, keunikan kunci komposit, validitas kode wilayah BPS 38 provinsi dan kode nasional 9999). Anggun juga menyusun dokumentasi komprehensif pada `docs/data-dictionary.md`, memvalidasi ketertelusuran lineage satu baris Gold ke berkas mentahnya, dan memverifikasi keterulangan (*reproducibility*) kode proyek.

5. **Pengalihan Komponen Transformasi dan Panel (Tahap 4)**
   * **Pelaksana:** Alfayya Rafif Abiyyi Rosyid Ridlo & Kaleb Filbert Istel (Kolaboratif)
   * **Alasan Pembagian:** Mengingat Siti Sarifah Sumamah cuti, tahap 4 diakomodasi bersama: Alfayya menangani penyeragaman 11 kolom wajib skema Silver (`sumber`, `seri_kode`, `wilayah_kode`, `nama_wilayah`, `periode`, `jenis_periode`, `rincian`, `nilai`, `satuan`, `_berkas_raw`, `_sha256_raw`) agar lolos `python -m src.common.skema`, sedangkan Kaleb mengawal *reshaping* tabel panjang menjadi panel lebar Gold (provinsi $\times$ periode $\times$ indikator) sebelum dimuat ke layer penyimpanan SQL.

## Tugas sampingan tiap anggota
Koordinator / Penjaga Data & Evaluasi / Integrator / Analis Utama / Reproduksi & Demo — siapa apa, dan mengapa.

### 1. Koordinator: Kaleb Filbert Istel
* **Mengapa:** Diperlukan kepemimpinan operasional yang adaptif untuk mengawal sprint berjalan tepat waktu, menjaga ritme kerja tim 4 orang, memimpin sesi standup berkala, dan mengelola pembagian kartu tugas di Papan Kanban Workbench.
* **Tanggung Jawab:**
  * Memimpin perencanaan sprint, penulisan *Sprint Goal*, dan pemecahan *backlog*.
  * Mengingatkan pengisian Log Sprint individu sebelum jendela waktu ditutup.
  * Menjadi narahubung utama tim dengan dosen pengampu dan pembimbing (Ardika Satria), terutama terkait pelaporan formal kondisi anggota yang cuti.

### 2. Penjaga Data & Evaluasi: Kaleb Filbert Istel (didukung Ashila Islamisahfa Vanisha)
* **Mengapa:** Karena tim beranggotakan 4 orang, peran ini dirangkap oleh Koordinator dengan dukungan Analis Utama guna menjamin integritas data Bronze tidak terganggu dan keputusan wrangling tervalidasi dengan benar.
* **Tanggung Jawab:**
  * Memastikan direktori `data/raw/` tidak pernah disunting manual, tidak diubah namanya, dan tidak ter-commit ke Git.
  * Mengawasi verifikasi checksum berkas mentah terhadap `data/raw/MANIFEST.csv`.
  * Memeriksa keterisian dan kepatuhan format pada `log-keputusan.csv` agar setiap keputusan wrangling mencantumkan alternatif yang ditolak serta estimasi dampak baris yang akurat.

### 3. Integrator: Alfayya Rafif Abiyyi Rosyid Ridlo
* **Mengapa:** Alfayya memegang komponen ekstraksi yang menjadi pintu masuk hulu data. Sebagai Integrator, ia berada di posisi paling strategis untuk memastikan keterpaduan kode dari cabang hulu sampai ke hilir.
* **Tanggung Jawab:**
  * Mengelola alur Pull Request (PR) di repositori GitHub tim; memastikan tidak ada kode yang di-push langsung ke cabang `main`.
  * Memeriksa konflik kode antarcabang kerja (`<nim>/kerja`) dan memastikan minimal satu rekan telah mereview PR sebelum digabungkan.
  * Menjaga agar skrip orkestrasi `pipeline.py` selalu dalam status dapat dieksekusi (*runnable*) dan menghasilkan luaran yang konsisten.

### 4. Analis Utama: Ashila Islamisahfa Vanisha
* **Mengapa:** Ashila menguasai profil data, missing value, dan patahan seri pada tahap eksplorasi. Pemahaman ini sangat krusial untuk menganalisis konteks indikator SDG 8.6.1 (Pemuda NEET) dan SDG 8.7.1 (Pekerja Anak).
* **Tanggung Jawab:**
  * Menganalisis perbedaan definisi operasional umur antar-lembaga (BPS usia 15–24 tahun vs WDI pekerja anak usia 7–14 tahun vs dua definisi ILO).
  * Menghasilkan visualisasi statistik deskriptif dan boxplot di `reports/gambar/`.
  * Memimpin penulisan interpretasi temuan substantif pada laporan utama kelompok (`reports/tim.md`).

### 5. Reproduksi & Demo: Anggun Nita
* **Mengapa:** Anggun memegang komponen validasi dan dokumentasi, sehingga memiliki posisi netral yang ideal untuk menguji keterulangan sistem dari sudut pandang evaluator eksternal.
* **Tanggung Jawab:**
  * Melakukan uji reproduksi bersih (*fresh clone audit*): klon repositori, build environment baru, unduh paket, dan jalankan `python pipeline.py` untuk memastikan seluruh pipeline tuntas di bawah 15 menit tanpa galat.
  * Memvalidasi bahwa artefak metrik individu di `results/<nim>/metrics.json` telah dihitung dan tercatat dengan benar di sistem denyut Workbench.
  * Mempersiapkan skenario, memimpin perekaman layar, dan mengunggah video Demo Sprint (maksimal 10 menit, format MP4/WebM) untuk Sprint 1, Sprint 2, dan Sprint 3.

## Standup mingguan dan kanal komunikasi
Hari/jam standup: Selasa/15.00-16.40
Kanal: Luring

## Jika ada anggota yang menghilang

### Tindakan pada Sprint Pertama Tidak Muncul
1. **Peringatan dan Penelusuran Internal (1×24 Jam)**  
   Koordinator tim segera menghubungi anggota yang bersangkutan melalui kanal komunikasi primer (WhatsApp/telepon/email) dalam waktu maksimal 1×24 jam sejak ia tidak menghadiri jadwal *standup* mingguan atau tidak menunjukkan aktivitas di papan tugas dan Git.
2. **Batas Toleransi dan Mitigasi Tugas (H-3 Penutupan Sprint)**  
   Jika dalam 2×24 jam (paling lambat H-3 sebelum sprint ditutup) tidak ada konfirmasi dan progres kerja:
   - Kartu tugas anggota tersebut di kolom **Dikerjakan** ditarik kembali ke backlog atau dialihkan sementara ke anggota lain (sistem *buddy/backup*) agar tidak menghambat *pipeline* tim dan *Definition of Done* (DoD) tetap tercapai.
   - Anggota lain tidak mengutak-atik cabang kerja (`<nim>/kerja`) milik anggota yang bersangkutan; tugas pengganti dikerjakan dari cabang masing-masing dengan catatan penyesuaian yang jelas.
3. **Pencatatan dan Transparansi Sistem**  
   - Tim membiarkan kartu Log Sprint milik anggota tersebut tetap kosong (tidak diisikan oleh orang lain) sehingga sistem Workbench mencatat status tidak hadir/lampu merah secara objektif.
   - Koordinator dan anggota aktif mencantumkan kendala ketiadaan anggota tersebut pada isian **Hambatan** di Log Sprint masing-masing dan mengabarkannya kepada pembimbing (Ardika Satria) sebagai catatan awal.

---

### Tindakan pada Sprint Kedua Berturut-turut Tidak Muncul
1. **Eskalasi Resmi ke Pembimbing dan Dosen Pengampu**  
   Begitu sistem Workbench menerbitkan bendera peringatan akibat lampu merah dua sprint berturut-turut, Koordinator tim langsung menyampaikan laporan resmi tertulis kepada pembimbing (Ardika Satria) dan dosen pengampu. Laporan melampirkan bukti: ketiadaan commit di repo, ketiadaan Log Sprint, catatan rekap lampu Workbench, serta riwayat upaya komunikasi yang tidak direspons.
2. **Restrukturisasi Komponen Permanen**  
   Dengan persetujuan pembimbing:
   - Komponen utama serta tugas sampingan anggota yang bersangkutan dialihkan secara penuh dan permanen kepada anggota tim yang aktif.
   - Papan Tim (Backlog dan Sprint berjalan) diperbarui total untuk mendistribusikan ulang beban kerja secara proporsional.
3. **Isolasi Kontribusi dan Konsekuensi Penilaian**  
   - Hak akses cabang atau kontribusi yang bersangkutan di repositori dibekukan dari alur integrasi utama (*branch protection*).
   - Anggota tersebut tidak dicantumkan sebagai kontributor pada komponen, berkas hasil (`results/<nim>/metrics.json`), maupun laporan tim (`reports/tim.md`).
   - Tim menyerahkan keputusan administratif status akademik anggota tersebut (pengguguran keikutsertaan capstone atau nilai nol) sepenuhnya kepada dosen pengampu mata kuliah.
