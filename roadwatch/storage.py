import os
from datetime import datetime

PEMISAH_KOLOM = "|"


def pastikan_folder_ada(path_file: str) -> None:
    folder = os.path.dirname(path_file)
    if folder:
        os.makedirs(folder, exist_ok=True)


def buat_file_eksklusif(path_file: str = "data/laporan.txt") -> bool:
    pastikan_folder_ada(path_file)
    try:
        with open(path_file, mode="x", encoding="utf-8") as file:
            file.write("")
        return True
    except FileExistsError:
        return False


def simpan_semua_laporan(daftar_laporan: list, path_file: str = "data/laporan.txt") -> None:
    pastikan_folder_ada(path_file)
    with open(path_file, mode="w", encoding="utf-8") as file:
        for lap in daftar_laporan:
            baris = PEMISAH_KOLOM.join([
                str(lap["kode_laporan"]),
                str(lap["nama_jalan"]),
                str(lap["wilayah"]),
                str(lap["tingkat_kerusakan"]),
                str(lap["foto"]),
                str(lap["status"]),
                str(lap["jumlah_pelapor"]),
                str(lap["skor_prioritas"]),
                str(lap["tanggal_lapor"]),
                str(lap["catatan_tindak_lanjut"]),
            ])
            file.write(baris + "\n")


def tambah_laporan_baris(laporan: dict, path_file: str = "data/laporan.txt") -> None:
    pastikan_folder_ada(path_file)
    with open(path_file, mode="a", encoding="utf-8") as file:
        baris = PEMISAH_KOLOM.join([
            str(laporan["kode_laporan"]),
            str(laporan["nama_jalan"]),
            str(laporan["wilayah"]),
            str(laporan["tingkat_kerusakan"]),
            str(laporan["foto"]),
            str(laporan["status"]),
            str(laporan["jumlah_pelapor"]),
            str(laporan["skor_prioritas"]),
            str(laporan["tanggal_lapor"]),
            str(laporan["catatan_tindak_lanjut"]),
        ])
        file.write(baris + "\n")


def muat_semua_laporan(path_file: str = "data/laporan.txt") -> list:
    daftar_laporan = []
    status_baca = "Selesai memproses pembacaan file."
    try:
        with open(path_file, mode="r", encoding="utf-8") as file:
            for nomor_baris, baris in enumerate(file, start=1):
                teks_bersih = baris.strip()
                if not teks_bersih:
                    continue
                kolom = teks_bersih.split(PEMISAH_KOLOM)
                if len(kolom) != 10:
                    raise ValueError(f"Format kolom tidak lengkap pada baris ke-{nomor_baris}")

                daftar_laporan.append({
                    "kode_laporan": kolom[0],
                    "nama_jalan": kolom[1],
                    "wilayah": kolom[2],
                    "tingkat_kerusakan": kolom[3],
                    "foto": kolom[4],
                    "status": kolom[5],
                    "jumlah_pelapor": int(kolom[6]),
                    "skor_prioritas": int(kolom[7]),
                    "tanggal_lapor": kolom[8],
                    "catatan_tindak_lanjut": kolom[9],
                })
    except FileNotFoundError:
        buat_file_eksklusif(path_file)
        status_baca = "File belum ditemukan, membuat file penyimpanan baru."
    except ValueError as err:
        catat_log_aktivitas(f"[WARNING] Data corrupt terdeteksi: {err}")
        status_baca = f"Sebagian data dilewati karena corrupt: {err}"
    finally:
        catat_log_aktivitas(f"[READ] {status_baca} (Total termuat: {len(daftar_laporan)})")

    return daftar_laporan


def catat_log_aktivitas(pesan: str, path_log: str = "data/aktivitas.log") -> None:
    pastikan_folder_ada(path_log)
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(path_log, mode="a", encoding="utf-8") as file:
        file.write(f"[{waktu}] {pesan}\n")