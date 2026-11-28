#modularitas inisialisasi package (mengatur antarmuka publik package roadwatch agar modul internal mudah diakses)
#modularitas impor validasi (mengekspos fungsi-fungsi pengecekan input dari modul validasi.py)
from .validasi import (
    validasi_teks,
    validasi_tingkat,
    validasi_foto,
    validasi_tanggal,
    validasi_password,
)
#modularitas impor storage (mengekspos konstanta path file dan fungsi operasi baca/tulis dari modul storage.py)
from .storage import (
    FILE_LAPORAN,
    FILE_TINDAK_LANJUT,
    FILE_LOG,
    buat_file_laporan,
    buat_file_tindak_lanjut,
    baca_semua_laporan,
    baca_semua_tindak_lanjut,
    simpan_semua_laporan,
    tambah_baris_laporan,
    tambah_baris_tindak_lanjut,
    perbarui_baris_tindak_lanjut,
    catat_log,
)

#enkapsulasi package (mendefinisikan daftar simbol resmi yang diekspor saat package diimpor)
__all__ = [
    "validasi_teks",
    "validasi_tingkat",
    "validasi_foto",
    "validasi_tanggal",
    "validasi_password",
    "FILE_LAPORAN",
    "FILE_TINDAK_LANJUT",
    "FILE_LOG",
    "buat_file_laporan",
    "buat_file_tindak_lanjut",
    "baca_semua_laporan",
    "baca_semua_tindak_lanjut",
    "simpan_semua_laporan",
    "tambah_baris_laporan",
    "tambah_baris_tindak_lanjut",
    "perbarui_baris_tindak_lanjut",
    "catat_log",
]