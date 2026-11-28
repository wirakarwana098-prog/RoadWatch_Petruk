#modularitas modul services (mengatur logika bisnis utama laporan jalan rusak, prioritas, tindak lanjut, dan manajemen pengguna)
#library & modularitas (mengimpor datetime serta fungsi algoritma, storage, dan validasi internal)
from datetime import datetime

from . import algoritma
from .storage import (
    baca_semua_laporan,
    simpan_semua_laporan,
    tambah_baris_laporan,
    baca_semua_tindak_lanjut,
    tambah_baris_tindak_lanjut,
    perbarui_baris_tindak_lanjut,
    catat_log,
)
from .validasi import (
    validasi_teks,
    validasi_tingkat,
    validasi_foto,
    validasi_tanggal,
    validasi_password,
)

#konstanta aturan bisnis & akun default (menyimpan bobot kerusakan, alur transisi status valid, dan daftar akun awal)
BOBOT_KERUSAKAN = {"Ringan": 1, "Sedang": 2, "Berat": 3}
STATUS_VALID = ("Baru", "Terverifikasi", "Dalam Penanganan", "Selesai", "Ditolak")
TRANSISI_VALID = {
    "Terverifikasi": ("Dalam Penanganan",),
    "Dalam Penanganan": ("Selesai",),
}

PENGGUNA_AWAL = [
    {"id": "A001", "nama": "Administrator", "username": "admin", "password": "admin123", "peran": "admin"},
    {"id": "P001", "nama": "Wira Karwana", "username": "wira", "password": "wira123", "peran": "petugas"},
]


#generator kode unik (membuat kode berformat RW-XXXX yang belum terpakai menggunakan pengecekan linear search)
def buat_kode_laporan(daftar):
    urutan = len(daftar) + 1
    while True:
        kode = f"RW-{urutan:04d}"
        if algoritma.linear_search_laporan(daftar, kode) == -1:
            return kode
        urutan += 1


#kalkulasi skor prioritas (menghitung nilai urgensi berdasarkan rumus bobot tingkat kerusakan dikali 10 ditambah jumlah pelapor)
def hitung_skor_prioritas(laporan):
    bobot = BOBOT_KERUSAKAN.get(laporan["tingkat"], 0)
    return bobot * 10 + laporan["jumlah_pelapor"]


#helper pembaruan daftar (mengganti data laporan lama dengan versi terbaru berdasarkan kecocokan kode)
def _ganti_laporan(laporan):
    daftar = baca_semua_laporan()
    for i in range(len(daftar)):
        if daftar[i]["kode"] == laporan["kode"]:
            daftar[i] = laporan
            break
    return daftar


#logika tambah & gabung duplikat (memvalidasi input lalu menaikkan jumlah_pelapor jika lokasi sama atau membuat laporan baru)
def tambah_laporan(jalan, kecamatan, tingkat, foto):
    jalan = validasi_teks(jalan, "Nama jalan")
    kecamatan = validasi_teks(kecamatan, "Kecamatan")
    tingkat = validasi_tingkat(tingkat)
    foto = validasi_foto(foto)

    daftar = baca_semua_laporan()
    for l in daftar:
        if l["jalan"].lower() == jalan.lower() and l["kecamatan"].lower() == kecamatan.lower():
            l["jumlah_pelapor"] += 1
            simpan_semua_laporan(daftar)
            catat_log(f"Laporan duplikat lokasi {jalan}, {kecamatan} - pelapor bertambah")
            return l["kode"]

    laporan = {
        "kode": buat_kode_laporan(daftar),
        "jalan": jalan,
        "kecamatan": kecamatan,
        "tingkat": tingkat,
        "status": "Baru",
        "jumlah_pelapor": 1,
        "tanggal": datetime.now().strftime("%d-%m-%Y"),
    }
    tambah_baris_laporan(laporan)
    catat_log(f"Laporan baru {laporan['kode']} - {jalan}, {kecamatan}")
    return laporan["kode"]


#searching & keyword argument (mencari laporan berdasarkan kode menggunakan linear search atau binary search setelah diurutkan)
def cari_laporan(kode, pakai_binary=False):
    kode = validasi_teks(kode, "Kode laporan")
    daftar = baca_semua_laporan()
    if pakai_binary:
        terurut = algoritma.insertion_sort(daftar, "kode", menurun=False)
        indeks = algoritma.binary_search_laporan(terurut, kode)
        return terurut[indeks] if indeks != -1 else None
    indeks = algoritma.linear_search_laporan(daftar, kode)
    return daftar[indeks] if indeks != -1 else None


#error handling kontrol alur status (memvalidasi hak akses peran dan aturan transisi status sebelum menyimpan perubahan)
def ubah_status(kode, status_baru, peran):
    laporan = cari_laporan(kode)
    if laporan is None:
        raise ValueError("Kode laporan tidak ditemukan.")
    if peran not in ("petugas", "admin"):
        raise ValueError("Hanya petugas atau admin yang boleh mengubah status.")
    if status_baru not in STATUS_VALID:
        raise ValueError("Status tidak dikenal.")
    if status_baru not in TRANSISI_VALID.get(laporan["status"], ()):
        raise ValueError(f"Perubahan status tidak sah: dari {laporan['status']} ke {status_baru}.")
    laporan["status"] = status_baru
    simpan_semua_laporan(_ganti_laporan(laporan))
    catat_log(f"Status {kode} diubah menjadi {status_baru}")
    return laporan


#verifikasi laporan baru (mengubah status laporan 'Baru' menjadi 'Terverifikasi' atau 'Ditolak' oleh petugas/admin)
def verifikasi_laporan(kode, valid, peran):
    laporan = cari_laporan(kode)
    if laporan is None:
        raise ValueError("Kode laporan tidak ditemukan.")
    if peran not in ("petugas", "admin"):
        raise ValueError("Hanya petugas atau admin yang boleh memverifikasi.")
    if laporan["status"] != "Baru":
        raise ValueError(f"Laporan sudah diverifikasi (status: {laporan['status']}).")
    laporan["status"] = "Terverifikasi" if valid else "Ditolak"
    simpan_semua_laporan(_ganti_laporan(laporan))
    catat_log(f"Laporan {kode} {'terverifikasi' if valid else 'ditolak'} oleh {peran}")
    return laporan


#pencatatan tindak lanjut (menyimpan rencana perbaikan ke storage dan otomatis mengubah status laporan menjadi 'Dalam Penanganan')
def catat_tindak_lanjut(kode, catatan, penanggung_jawab, tanggal_rencana, peran):
    laporan = cari_laporan(kode)
    if laporan is None:
        raise ValueError("Kode laporan tidak ditemukan.")
    if peran not in ("petugas", "admin"):
        raise ValueError("Hanya petugas atau admin yang boleh mencatat tindak lanjut.")
    catatan = validasi_teks(catatan, "Catatan tindakan")
    penanggung_jawab = validasi_teks(penanggung_jawab, "Penanggung jawab")
    tanggal_rencana = validasi_tanggal(tanggal_rencana)

    tindak_lanjut = {
        "kode_laporan": laporan["kode"],
        "catatan": catatan,
        "penanggung_jawab": penanggung_jawab,
        "tanggal_rencana": tanggal_rencana,
        "tanggal_selesai": "-",
        "foto_sesudah": "-",
    }
    tambah_baris_tindak_lanjut(tindak_lanjut)

    if laporan["status"] == "Terverifikasi":
        ubah_status(laporan["kode"], "Dalam Penanganan", peran)

    catat_log(f"Tindak lanjut dicatat untuk {laporan['kode']}")
    return tindak_lanjut


#penyelesaian perbaikan (memperbarui tanggal selesai dan foto sesudah pada tindak lanjut terakhir lalu mengubah status ke 'Selesai')
def selesaikan_tindak_lanjut(kode, tanggal_selesai, foto_sesudah, peran):
    laporan = cari_laporan(kode)
    if laporan is None:
        raise ValueError("Kode laporan tidak ditemukan.")
    if peran not in ("petugas", "admin"):
        raise ValueError("Hanya petugas atau admin yang boleh menandai selesai.")
    if laporan["status"] != "Dalam Penanganan":
        raise ValueError("Status Selesai hanya bisa dari Dalam Penanganan.")

    semua = baca_semua_tindak_lanjut()
    cocok = [t for t in semua if t["kode_laporan"] == laporan["kode"]]
    if not cocok:
        raise ValueError("Catat tindak lanjut dulu sebelum menandai selesai.")

    tanggal_selesai = validasi_tanggal(tanggal_selesai)
    foto_sesudah = validasi_foto(foto_sesudah)

    terbaru = dict(cocok[-1])
    terbaru["tanggal_selesai"] = tanggal_selesai
    terbaru["foto_sesudah"] = foto_sesudah
    if not perbarui_baris_tindak_lanjut(laporan["kode"], len(cocok) - 1, terbaru):
        raise ValueError("Gagal memperbarui tindak lanjut.")

    ubah_status(laporan["kode"], "Selesai", peran)
    catat_log(f"Tindak lanjut {laporan['kode']} selesai pada {tanggal_selesai}")
    return terbaru


#riwayat penanganan (mengambil seluruh daftar catatan tindak lanjut yang terhubung dengan kode laporan tertentu)
def riwayat_tindak_lanjut(kode):
    laporan = cari_laporan(kode)
    if laporan is None:
        raise ValueError("Kode laporan tidak ditemukan.")
    semua = baca_semua_tindak_lanjut()
    return [t for t in semua if t["kode_laporan"] == laporan["kode"]]


#sorting & keyword argument (menghitung skor tiap laporan lalu mengurutkannya menurun memakai selection, bubble, atau insertion sort)
def urutkan_prioritas(daftar=None, metode="selection"):
    daftar = baca_semua_laporan() if daftar is None else daftar
    diberi_skor = [dict(l, skor=hitung_skor_prioritas(l)) for l in daftar]
    if metode == "bubble":
        return algoritma.bubble_sort(diberi_skor, "skor", menurun=True)
    if metode == "insertion":
        return algoritma.insertion_sort(diberi_skor, "skor", menurun=True)
    return algoritma.selection_sort(diberi_skor, "skor", menurun=True)


#function lanjutan - *args & **kwargs (menyaring daftar laporan berdasarkan banyak status variadic dan kriteria atribut dinamis)
def filter_laporan(*status, **kriteria):
    daftar = baca_semua_laporan()
    hasil = daftar
    if status:
        hasil = [l for l in hasil if l["status"] in status]
    for kunci, nilai in kriteria.items():
        hasil = [l for l in hasil if str(l.get(kunci, "")).lower() == str(nilai).lower()]
    return hasil


#statistik & rekursi (menghitung total laporan, distribusi status, persentase selesai, dan total pelapor secara rekursif)
def rekap_laporan():
    daftar = baca_semua_laporan()
    rekap = {s: 0 for s in STATUS_VALID}
    for l in daftar:
        rekap[l["status"]] = rekap.get(l["status"], 0) + 1
    total = len(daftar)
    jumlah_selesai = rekap.get("Selesai", 0)
    persentase = round(jumlah_selesai * 100 / total, 1) if total else 0.0
    return {
        "total": total,
        "rekap_status": rekap,
        "total_pelapor": algoritma.total_pelapor_rekursif(daftar),
        "persentase_selesai": persentase,
    }


#akses daftar pengguna (mengembalikan daftar akun admin dan petugas yang terdaftar di memori)
def ambil_pengguna():
    return PENGGUNA_AWAL


#autentikasi pengguna (memverifikasi kecocokan username dan password lalu mencatat hasil login ke log aktivitas)
def login(username, password):
    username = validasi_teks(username, "Username")
    if not isinstance(password, str) or password == "":
        raise ValueError("Password tidak boleh kosong.")
    for pengguna in PENGGUNA_AWAL:
        if pengguna["username"] == username and pengguna["password"] == password:
            catat_log(f"Login berhasil: {username}")
            return pengguna
    catat_log(f"Login gagal: {username}")
    return None


#tambah petugas (memvalidasi otorisasi admin dan keunikan ID/username sebelum menambah petugas baru)
def tambah_pengguna(peran, id_pengguna, nama, username, password):
    if peran != "admin":
        raise ValueError("Hanya admin yang boleh menambah pengguna.")
    id_pengguna = validasi_teks(id_pengguna, "ID petugas")
    username = validasi_teks(username, "Username")
    password = validasi_password(password)
    nama = validasi_teks(nama, "Nama")
    if any(p["username"] == username for p in PENGGUNA_AWAL):
        raise ValueError("Username sudah dipakai.")
    if any(p["id"] == id_pengguna for p in PENGGUNA_AWAL):
        raise ValueError("ID pengguna sudah dipakai.")
    baru = {"id": id_pengguna, "nama": nama, "username": username,
            "password": password, "peran": "petugas"}
    PENGGUNA_AWAL.append(baru)
    catat_log(f"Petugas baru ditambahkan: {username}")
    return baru


#hapus petugas (menghapus akun petugas berdasarkan ID sambil melindungi akun admin utama agar tidak terhapus)
def hapus_pengguna(peran, id_pengguna):
    if peran != "admin":
        raise ValueError("Hanya admin yang boleh menghapus petugas.")
    id_pengguna = validasi_teks(id_pengguna, "ID petugas")
    for i in range(len(PENGGUNA_AWAL)):
        if PENGGUNA_AWAL[i]["id"] == id_pengguna:
            if PENGGUNA_AWAL[i]["peran"] == "admin":
                raise ValueError("Akun administrator utama tidak dapat dihapus.")
            terhapus = PENGGUNA_AWAL.pop(i)
            catat_log(f"Petugas dihapus: {terhapus['username']}")
            return terhapus
    raise ValueError("ID petugas tidak ditemukan.")


#reset password (memperbarui password pengguna berdasarkan ID setelah memvalidasi otorisasi admin)
def reset_password_pengguna(peran, id_pengguna, password_baru):
    if peran != "admin":
        raise ValueError("Hanya admin yang boleh mereset password.")
    id_pengguna = validasi_teks(id_pengguna, "ID petugas")
    password_baru = validasi_password(password_baru)
    for pengguna in PENGGUNA_AWAL:
        if pengguna["id"] == id_pengguna:
            pengguna["password"] = password_baru
            catat_log(f"Password direset untuk: {pengguna['username']}")
            return pengguna
    raise ValueError("ID petugas tidak ditemukan.")