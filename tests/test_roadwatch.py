import os
import tempfile
import unittest
from roadwatch.services import PengelolaLaporan, hitung_total_angka, filter_laporan_dinamis
from roadwatch.storage import buat_file_eksklusif


class TestRoadWatch(unittest.TestCase):
    def setUp(self):
        self.folder_temp = tempfile.TemporaryDirectory()
        self.path_file = os.path.join(self.folder_temp.name, "laporan_uji.txt")
        self.pengelola = PengelolaLaporan(path_file=self.path_file)

    def tearDown(self):
        self.folder_temp.cleanup()

    def test_01_validasi_input_kosong(self):
        with self.assertRaises(ValueError):
            self.pengelola.buat_atau_gabung_laporan(
                nama_jalan="",
                wilayah="Kedaton",
                tingkat_kerusakan="Berat",
                foto="rusak.jpg",
            )

    def test_02_penggabungan_laporan_dan_args(self):
        self.assertEqual(hitung_total_angka(1, 2, 3), 6)

        res1 = self.pengelola.buat_atau_gabung_laporan("Jl. Raden Intan", "Tanjung Karang", "Ringan", "a.jpg")
        res2 = self.pengelola.buat_atau_gabung_laporan("Jl. Raden Intan", "Tanjung Karang", "Berat", "b.jpg")

        self.assertFalse(res1["digabung"])
        self.assertTrue(res2["digabung"])
        self.assertEqual(res2["data"]["jumlah_pelapor"], 2)
        self.assertEqual(res2["data"]["skor_prioritas"], 6)

    def test_03_linear_dan_binary_search(self):
        dibuat = self.pengelola.buat_atau_gabung_laporan("Jl. Antasari", "Sukabumi", "Sedang", "c.jpg")
        kode = dibuat["data"]["kode_laporan"]

        hasil_linear = self.pengelola.cari_kata_kunci("antasari")
        self.assertEqual(len(hasil_linear), 1)

        hasil_binary = self.pengelola.cari_berdasarkan_kode(kode)
        self.assertIsNotNone(hasil_binary)
        self.assertEqual(hasil_binary["nama_jalan"], "Jl. Antasari")

    def test_04_selection_sort_prioritas(self):
        self.pengelola.buat_atau_gabung_laporan("Jl. Satu", "Kemiling", "Ringan", "1.jpg")
        self.pengelola.buat_atau_gabung_laporan("Jl. Dua", "Kemiling", "Berat", "2.jpg")
        self.pengelola.buat_atau_gabung_laporan("Jl. Tiga", "Kemiling", "Sedang", "3.jpg")

        terurut = self.pengelola.ambil_laporan_terurut(kriteria="prioritas")
        urutan_skor = [item["skor_prioritas"] for item in terurut]
        self.assertEqual(urutan_skor, [3, 2, 1])

    def test_05_file_handling_eksklusif_dan_kwargs(self):
        self.assertFalse(buat_file_eksklusif(self.path_file))

        self.pengelola.buat_atau_gabung_laporan("Jl. Pramuka", "Rajabasa", "Berat", "p.jpg")
        hasil_filter = filter_laporan_dinamis(self.pengelola.daftar_laporan, wilayah="Rajabasa", status="Baru")
        self.assertEqual(len(hasil_filter), 1)


if __name__ == "__main__":
    unittest.main()