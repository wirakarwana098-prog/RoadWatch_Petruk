import os
import unittest

from roadwatch import algoritma, services, storage
from roadwatch.validasi import (
    validasi_tingkat,
    validasi_foto,
    validasi_password,
    validasi_teks,
)


class TestValidasi(unittest.TestCase):
    def test_tingkat_valid(self):
        self.assertEqual(validasi_tingkat("berat"), "Berat")

    def test_tingkat_tidak_valid(self):
        with self.assertRaises(ValueError):
            validasi_tingkat("parah")

    def test_teks_dengan_pipa_ditolak(self):
        with self.assertRaises(ValueError):
            validasi_teks("jalan|rusak", "Nama jalan")

    def test_foto_tidak_valid(self):
        with self.assertRaises(ValueError):
            validasi_foto("gambar.gif")

    def test_password_pendek(self):
        with self.assertRaises(ValueError):
            validasi_password("123")


class TestAlgoritma(unittest.TestCase):
    def setUp(self):
        self.data = [
            {"kode": "RW-0003", "jumlah_pelapor": 4},
            {"kode": "RW-0001", "jumlah_pelapor": 2},
            {"kode": "RW-0002", "jumlah_pelapor": 9},
        ]

    def test_linear_search_ditemukan(self):
        self.assertEqual(algoritma.linear_search_laporan(self.data, "RW-0002"), 2)

    def test_linear_search_tidak_ditemukan(self):
        self.assertEqual(algoritma.linear_search_laporan(self.data, "RW-9999"), -1)

    def test_binary_search_ditemukan(self):
        terurut = algoritma.insertion_sort(self.data, "kode", menurun=False)
        indeks = algoritma.binary_search_laporan(terurut, "RW-0003")
        self.assertEqual(terurut[indeks]["kode"], "RW-0003")

    def test_bubble_sort_menurun(self):
        hasil = algoritma.bubble_sort(self.data, "jumlah_pelapor", menurun=True)
        self.assertEqual(hasil[0]["jumlah_pelapor"], 9)

    def test_selection_sort_menurun(self):
        hasil = algoritma.selection_sort(self.data, "jumlah_pelapor", menurun=True)
        self.assertEqual(hasil[-1]["jumlah_pelapor"], 2)

    def test_total_pelapor_rekursif(self):
        self.assertEqual(algoritma.total_pelapor_rekursif(self.data), 15)


class TestServices(unittest.TestCase):
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

    def tearDown(self):
        for berkas in (storage.FILE_LAPORAN, storage.FILE_TINDAK_LANJUT):
            if os.path.exists(berkas):
                os.remove(berkas)
        storage.FILE_LAPORAN = self.asli
        storage.FILE_TINDAK_LANJUT = self.asli_tl

    def test_tambah_laporan_baru(self):
        kode = services.tambah_laporan("Jl. Test", "Rajabasa", "berat", "a.jpg")
        self.assertEqual(kode, "RW-0001")

    def test_laporan_lokasi_sama_digabung(self):
        services.tambah_laporan("Jl. Test", "Rajabasa", "berat", "a.jpg")
        services.tambah_laporan("Jl. Test", "Rajabasa", "ringan", "b.jpg")
        laporan = services.cari_laporan("RW-0001")
        self.assertEqual(laporan["jumlah_pelapor"], 2)

    def test_skor_prioritas(self):
        laporan = {"tingkat": "Berat", "jumlah_pelapor": 3}
        self.assertEqual(services.hitung_skor_prioritas(laporan), 33)

    def test_verifikasi_ubah_status(self):
        services.tambah_laporan("Jl. Test", "Rajabasa", "berat", "a.jpg")
        services.verifikasi_laporan("RW-0001", True, "petugas")
        laporan = services.cari_laporan("RW-0001")
        self.assertEqual(laporan["status"], "Terverifikasi")

    def test_ubah_status_tidak_sah(self):
        services.tambah_laporan("Jl. Test", "Rajabasa", "berat", "a.jpg")
        with self.assertRaises(ValueError):
            services.ubah_status("RW-0001", "Selesai", "petugas")

    def test_login_berhasil(self):
        self.assertIsNotNone(services.login("admin", "admin123"))

    def test_login_gagal(self):
        self.assertIsNone(services.login("admin", "salah"))


if __name__ == "__main__":
    unittest.main()
