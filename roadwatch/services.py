import random
import statistics
from datetime import datetime

from roadwatch.validasi import validasi_laporan, validasi_status
from roadwatch.storage import (
    muat_semua_laporan,
    simpan_semua_laporan,
    tambah_laporan_baris,
    catat_log_aktivitas,
)
from roadwatch.algoritma import (
    linear_search,
    binary_search,
    selection_sort,
    insertion_sort,
    hitung_total_skor_rekursif,
)

BOBOT_KERUSAKAN = {
    "Ringan": 1,
    "Sedang": 2,
    "Berat": 3,
}

hitung_skor_prioritas = lambda tingkat, jumlah_pelapor: BOBOT_KERUSAKAN.get(tingkat, 1) * jumlah_pelapor


def hitung_total_angka(*args) -> int:
    total = 0
    for angka in args:
        total += angka
    return total


def filter_laporan_dinamis(daftar_laporan: list, **kwargs) -> list:
    hasil = list(daftar_laporan)
    for kunci, nilai in kwargs.items():
        if nilai:
            hasil = list(
                filter(
                    lambda item, k=kunci, v=str(nilai).strip().lower(): str(item.get(k, "")).lower() == v,
                    hasil,
                )
            )
    return hasil


class PengelolaLaporan:
    def __init__(self, path_file: str = "data/laporan.txt"):
        self.path_file = path_file
        self.daftar_laporan = muat_semua_laporan(path_file=self.path_file)

    def _buat_kode_unik(self) -> str:
        while True:
            kode = f"RW-{random.randint(1000, 9999)}"
            if self.cari_berdasarkan_kode(kode) is None:
                return kode

    def buat_atau_gabung_laporan(
        self, nama_jalan: str, wilayah: str, tingkat_kerusakan: str, foto: str
    ) -> dict:
        validasi_laporan(
            nama_jalan=nama_jalan,
            wilayah=wilayah,
            tingkat_kerusakan=tingkat_kerusakan,
            foto=foto,
        )

        for laporan in self.daftar_laporan:
            lokasi_sama = (
                laporan["nama_jalan"].strip().lower() == nama_jalan.strip().lower()
                and laporan["wilayah"].strip().lower() == wilayah.strip().lower()
            )
            if lokasi_sama and laporan["status"] not in ("Selesai", "Ditolak"):
                laporan["jumlah_pelapor"] = hitung_total_angka(laporan["jumlah_pelapor"], 1)
                if BOBOT_KERUSAKAN[tingkat_kerusakan] > BOBOT_KERUSAKAN[laporan["tingkat_kerusakan"]]:
                    laporan["tingkat_kerusakan"] = tingkat_kerusakan
                laporan["skor_prioritas"] = hitung_skor_prioritas(
                    laporan["tingkat_kerusakan"], laporan["jumlah_pelapor"]
                )
                simpan_semua_laporan(daftar_laporan=self.daftar_laporan, path_file=self.path_file)
                catat_log_aktivitas(f"Laporan ganda digabung ke {laporan['kode_laporan']}")
                return {
                    "digabung": True,
                    "pesan": "Lokasi sudah pernah dilaporkan. Laporan Anda digabung untuk menaikkan prioritas.",
                    "data": laporan,
                }

        laporan_baru = {
            "kode_laporan": self._buat_kode_unik(),
            "nama_jalan": nama_jalan.strip(),
            "wilayah": wilayah.strip(),
            "tingkat_kerusakan": tingkat_kerusakan,
            "foto": foto.strip(),
            "status": "Baru",
            "jumlah_pelapor": 1,
            "skor_prioritas": hitung_skor_prioritas(tingkat_kerusakan, 1),
            "tanggal_lapor": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "catatan_tindak_lanjut": "-",
        }
        self.daftar_laporan.append(laporan_baru)
        tambah_laporan_baris(laporan=laporan_baru, path_file=self.path_file)
        catat_log_aktivitas(f"Laporan baru dibuat: {laporan_baru['kode_laporan']}")
        return {
            "digabung": False,
            "pesan": "Laporan berhasil dikirim. Simpan kode laporan untuk mengecek progres.",
            "data": laporan_baru,
        }

    def cari_kata_kunci(self, kata_kunci: str) -> list:
        return linear_search(data=self.daftar_laporan, kata_kunci=kata_kunci)

    def cari_berdasarkan_kode(self, kode_laporan: str) -> dict | None:
        data_urut_kode = insertion_sort(
            data=self.daftar_laporan,
            key_func=lambda item: item["kode_laporan"],
            descending=False,
        )
        indeks = binary_search(data_terurut=data_urut_kode, kode_target=kode_laporan)
        if indeks != -1:
            return data_urut_kode[indeks]
        return None

    def ambil_laporan_terurut(self, kriteria: str = "prioritas", data_sumber: list = None) -> list:
        sumber = self.daftar_laporan if data_sumber is None else data_sumber
        pemilih_kunci = {
            "prioritas": lambda x: x["skor_prioritas"],
            "pelapor": lambda x: x["jumlah_pelapor"],
            "tanggal": lambda x: x["tanggal_lapor"],
        }.get(kriteria, lambda x: x["skor_prioritas"])

        return selection_sort(data=sumber, key_func=pemilih_kunci, descending=True)

    def perbarui_status_laporan(self, kode_laporan: str, status_baru: str, catatan: str = "-") -> dict:
        validasi_status(status_baru=status_baru)
        laporan = self.cari_berdasarkan_kode(kode_laporan=kode_laporan)
        if laporan is None:
            raise ValueError(f"Kode laporan '{kode_laporan}' tidak ditemukan.")

        laporan["status"] = status_baru
        if catatan.strip():
            laporan["catatan_tindak_lanjut"] = catatan.strip()

        simpan_semua_laporan(daftar_laporan=self.daftar_laporan, path_file=self.path_file)
        catat_log_aktivitas(f"Status {kode_laporan} diperbarui menjadi {status_baru}")
        return laporan

    def ringkasan_statistik(self) -> dict:
        if not self.daftar_laporan:
            return {
                "total_laporan": 0,
                "total_selesai": 0,
                "total_skor_prioritas": 0,
                "rata_rata_prioritas": 0.0,
            }

        daftar_skor = [item["skor_prioritas"] for item in self.daftar_laporan]
        laporan_selesai = filter_laporan_dinamis(self.daftar_laporan, status="Selesai")

        return {
            "total_laporan": len(self.daftar_laporan),
            "total_selesai": len(laporan_selesai),
            "total_skor_prioritas": hitung_total_skor_rekursif(self.daftar_laporan),
            "rata_rata_prioritas": round(statistics.mean(daftar_skor), 2),
        }