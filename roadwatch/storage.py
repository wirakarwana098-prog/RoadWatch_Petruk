import os
from datetime import datetime

FILE_LAPORAN = "data/laporan.txt"
FILE_TINDAK_LANJUT = "data/tindak_lanjut.txt"
FILE_LOG = "data/aktivitas.log"

HEADER_LAPORAN = "kode|jalan|kecamatan|tingkat|status|jumlah_pelapor|tanggal\n"
HEADER_TINDAK_LANJUT = (
    "kode_laporan|catatan|penanggung_jawab|tanggal_rencana|tanggal_selesai|foto_sesudah\n"
)

KOLOM_LAPORAN = ("kode", "jalan", "kecamatan", "tingkat", "status", "jumlah_pelapor", "tanggal")
KOLOM_TINDAK_LANJUT = (
    "kode_laporan", "catatan", "penanggung_jawab", "tanggal_rencana",
    "tanggal_selesai", "foto_sesudah",
)


def pastikan_folder():
    os.makedirs("data", exist_ok=True)


def _baris_ke_dict(baris, kolom):
    bagian = baris.strip().split("|")
    if len(bagian) != len(kolom):
        return None
    return dict(zip(kolom, bagian))


def _dict_ke_baris(data, kolom):
    return "|".join(str(data[k]) for k in kolom) + "\n"


def buat_file_laporan():
    pastikan_folder()
    try:
        with open(FILE_LAPORAN, "x") as f:
            f.write(HEADER_LAPORAN)
        return True
    except FileExistsError:
        return False


def buat_file_tindak_lanjut():
    pastikan_folder()
    try:
        with open(FILE_TINDAK_LANJUT, "x") as f:
            f.write(HEADER_TINDAK_LANJUT)
        return True
    except FileExistsError:
        return False


def baca_semua_laporan():
    pastikan_folder()
    daftar = []
    try:
        with open(FILE_LAPORAN, "r") as f:
            for baris in f:
                data = _baris_ke_dict(baris, KOLOM_LAPORAN)
                if data is None or data["kode"] == "kode":
                    continue
                data["jumlah_pelapor"] = int(data["jumlah_pelapor"])
                daftar.append(data)
    except FileNotFoundError:
        buat_file_laporan()
    return daftar


def baca_semua_tindak_lanjut():
    pastikan_folder()
    daftar = []
    try:
        with open(FILE_TINDAK_LANJUT, "r") as f:
            for baris in f:
                data = _baris_ke_dict(baris, KOLOM_TINDAK_LANJUT)
                if data is None or data["kode_laporan"] == "kode_laporan":
                    continue
                daftar.append(data)
    except FileNotFoundError:
        buat_file_tindak_lanjut()
    return daftar


def simpan_semua_laporan(daftar):
    pastikan_folder()
    with open(FILE_LAPORAN, "w") as f:
        f.write(HEADER_LAPORAN)
        for laporan in daftar:
            f.write(_dict_ke_baris(laporan, KOLOM_LAPORAN))


def tambah_baris_laporan(laporan):
    pastikan_folder()
    with open(FILE_LAPORAN, "a") as f:
        f.write(_dict_ke_baris(laporan, KOLOM_LAPORAN))


def tambah_baris_tindak_lanjut(tindak_lanjut):
    pastikan_folder()
    with open(FILE_TINDAK_LANJUT, "a") as f:
        f.write(_dict_ke_baris(tindak_lanjut, KOLOM_TINDAK_LANJUT))


def perbarui_baris_tindak_lanjut(kode_laporan, indeks_ke, data_baru):
    pastikan_folder()
    semua = baca_semua_tindak_lanjut()
    cocok = [t for t in semua if t["kode_laporan"] == kode_laporan]
    if indeks_ke < 0 or indeks_ke >= len(cocok):
        return False
    target = cocok[indeks_ke]
    for i in range(len(semua)):
        if semua[i] is target:
            semua[i] = data_baru
            break
    with open(FILE_TINDAK_LANJUT, "w") as f:
        f.write(HEADER_TINDAK_LANJUT)
        for t in semua:
            f.write(_dict_ke_baris(t, KOLOM_TINDAK_LANJUT))
    return True


def catat_log(aktivitas):
    pastikan_folder()
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(FILE_LOG, "a") as f:
        f.write(f"[{waktu}] {aktivitas}\n")
