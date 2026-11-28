#unit testing modul pengujian (menguji logika validasi, algoritma pencarian/pengurutan, dan layanan bisnis terpisah dari UI)
#library, os & unittest (mengimpor modul sistem file dan framework pengujian bawaan Python serta package roadwatch)
import os
import unittest

from roadwatch import algoritma, services, storage
from roadwatch.validasi import (
    validasi_tingkat,
    validasi_foto,
    validasi_password,
    validasi_teks,
)


#unit testing class uji validasi (memastikan fungsi validasi menerima input sah dan melempar ValueError untuk input tidak valid)
class TestValidasi(unittest.TestCase):
    #uji validasi tingkat sah (memastikan input 'berat' dinormalisasi menjadi 'Berat')
    def test_tingkat_valid(self):
        self.assertEqual(validasi_tingkat("berat"), "Berat")

    #uji validasi tingkat salah (memastikan kategori di luar ringan/sedang/berat memicu ValueError)
    def test_tingkat_tidak_valid(self):
        with self.assertRaises(ValueError):
            validasi_tingkat("parah")

    #uji karakter pemisah terlarang (memastikan teks mengandung '|' ditolak agar format penyimpanan tetap aman)
    def test_teks_dengan_pipa_ditolak(self):
        with self.assertRaises(ValueError):
            validasi_teks("jalan|rusak", "Nama jalan")

    #uji ekstensi foto ditolak (memastikan format selain .jpg/.jpeg/.png memicu ValueError)
    def test_foto_tidak_valid(self):
        with self.assertRaises(ValueError):
            validasi_foto("gambar.gif")

    #uji batas panjang password (memastikan password kurang dari 6 karakter ditolak dengan ValueError)
    def test_password_pendek(self):
        with self.assertRaises(ValueError):
            validasi_password("123")


#unit testing class uji algoritma (memverifikasi akurasi linear search, binary search, sorting, dan perhitungan rekursif)
class TestAlgoritma(unittest.TestCase):
    #persiapan data uji (menyiapkan daftar laporan contoh sebelum setiap metode pengujian algoritma dijalankan)
    def setUp(self):
        self.data = [
            {"kode": "RW-0003", "jumlah_pelapor": 4},
            {"kode": "RW-0001", "jumlah_pelapor": 2},
            {"kode": "RW-0002", "jumlah_pelapor": 9},
        ]

    #uji linear search berhasil (memastikan indeks yang dikembalikan sesuai posisi kode laporan dalam daftar)
    def test_linear_search_ditemukan(self):
        self.assertEqual(algoritma.linear_search_laporan(self.data, "RW-0002"), 2)

    #uji linear search nihil (memastikan fungsi mengembalikan -1 saat kode laporan tidak ada)
    def test_linear_search_tidak_ditemukan(self):
        self.assertEqual(algoritma.linear_search_laporan(self.data, "RW-9999"), -1)

    #uji binary search berhasil (mengurutkan data dengan insertion sort lalu memastikan binary search menemukan target)
    def test_binary_search_ditemukan(self):
        terurut = algoritma.insertion_sort(self.data, "kode", menurun=False)
        indeks = algoritma.binary_search_laporan(terurut, "RW-0003")
        self.assertEqual(terurut[indeks]["kode"], "RW-0003")

    #uji bubble sort menurun (memastikan laporan dengan jumlah_pelapor terbanyak berada di urutan pertama)
    def test_bubble_sort_menurun(self):
        hasil = algoritma.bubble_sort(self.data, "jumlah_pelapor", menurun=True)
        self.assertEqual(hasil[0]["jumlah_pelapor"], 9)

    #uji selection sort menurun (memastikan laporan dengan jumlah_pelapor tersedikit berada di urutan terakhir)
    def test_selection_sort_menurun(self):
        hasil = algoritma.selection_sort(self.data, "jumlah_pelapor", menurun=True)
        self.assertEqual(hasil[-1]["jumlah_pelapor"], 2)

    #uji akumulasi rekursif (memastikan penjumlahan rekursif seluruh jumlah_pelapor menghasilkan total 15)
    def test_total_pelapor_rekursif(self):
        self.assertEqual(algoritma.total_pelapor_rekursif(self.data), 15)


#unit testing class uji layanan bisnis (menguji siklus hidup laporan, penggabungan duplikat, skor prioritas, dan autentikasi)
class TestServices(unittest.TestCase):
    #isolasi file uji (mengalihkan path storage ke file sementara agar pengujian tidak mengubah data produksi)
    def setUp(self):
        self.asli = storage.FILE_LAPORAN
        self.asli_tl = storage.FILE_TINDAK_LANJUT
        storage.FILE_LAPORAN = "data/test_laporan.txt"
        storage.FILE_TINDAK_LANJUT = "data/test_tindak_lanjut.txt"
        for berkas in (storage.FILE_LAPORAN, storage.FILE_TINDAK_LANJUT):
            if os.path.exists(berkas):
                os.remove(berkas)
        storage.buat_file_laporan()
        storage.buat_file_tindak_lanjut()

    #pembersihan file uji (menghapus file sementara dan mengembalikan path storage asli setelah tiap pengujian selesai)
    def tearDown(self):
        for berkas in (storage.FILE_LAPORAN, storage.FILE_TINDAK_LANJUT):
            if os.path.exists(berkas):
                os.remove(berkas)
        storage.FILE_LAPORAN = self.asli
        storage.FILE_TINDAK_LANJUT = self.asli_tl

    #uji pembuatan laporan baru (memastikan laporan pertama mendapat kode otomatis RW-0001)
    def test_tambah_laporan_baru(self):
        kode = services.tambah_laporan("Jl. Test", "Rajabasa", "berat", "a.jpg")
        self.assertEqual(kode, "RW-0001")

    #uji deteksi duplikat lokasi (memastikan laporan pada jalan dan kecamatan sama menambah jumlah_pelapor)
    def test_laporan_lokasi_sama_digabung(self):
        services.tambah_laporan("Jl. Test", "Rajabasa", "berat", "a.jpg")
        services.tambah_laporan("Jl. Test", "Rajabasa", "ringan", "b.jpg")
        laporan = services.cari_laporan("RW-0001")
        self.assertEqual(laporan["jumlah_pelapor"], 2)

    #uji rumus skor prioritas (memastikan tingkat Berat dengan 3 pelapor menghasilkan skor 33)
    def test_skor_prioritas(self):
        laporan = {"tingkat": "Berat", "jumlah_pelapor": 3}
        self.assertEqual(services.hitung_skor_prioritas(laporan), 33)

    #uji verifikasi petugas (memastikan laporan valid berubah statusnya dari 'Baru' menjadi 'Terverifikasi')
    def test_verifikasi_ubah_status(self):
        services.tambah_laporan("Jl. Test", "Rajabasa", "berat", "a.jpg")
        services.verifikasi_laporan("RW-0001", True, "petugas")
        laporan = services.cari_laporan("RW-0001")
        self.assertEqual(laporan["status"], "Terverifikasi")

    #uji larangan lompat status (memastikan perubahan langsung dari 'Baru' ke 'Selesai' melempar ValueError)
    def test_ubah_status_tidak_sah(self):
        services.tambah_laporan("Jl. Test", "Rajabasa", "berat", "a.jpg")
        with self.assertRaises(ValueError):
            services.ubah_status("RW-0001", "Selesai", "petugas")

    #uji login kredensial valid (memastikan akun admin default berhasil masuk dan mengembalikan data pengguna)
    def test_login_berhasil(self):
        self.assertIsNotNone(services.login("admin", "admin123"))

    #uji login kredensial salah (memastikan password yang keliru mengembalikan None)
    def test_login_gagal(self):
        self.assertIsNone(services.login("admin", "salah"))


#entry point pengujian (menjalankan seluruh rangkaian test suite unittest saat file dieksekusi langsung)
if __name__ == "__main__":
    unittest.main()