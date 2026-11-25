from roadwatch import services, storage

PILIHAN_MENU = {
    "1": "Lapor jalan rusak",
    "2": "Cek status laporan",
    "3": "Lihat daftar laporan",
    "4": "Lihat dashboard",
    "5": "Login petugas / admin",
    "0": "Keluar",
}


def minta_teks(pertanyaan):
    while True:
        nilai = input(pertanyaan).strip()
        if nilai:
            return nilai
        print("Input tidak boleh kosong.")


def menu_utama():
    while True:
        print("\n=== ROADWATCH LAMPUNG ===")
        for kunci, teks in PILIHAN_MENU.items():
            print(f"{kunci}. {teks}")
        pilihan = input("Pilih: ").strip()

        if pilihan == "1":
            menu_lapor()
        elif pilihan == "2":
            menu_cek_status()
        elif pilihan == "3":
            menu_daftar_laporan()
        elif pilihan == "4":
            menu_dashboard()
        elif pilihan == "5":
            menu_login()
        elif pilihan == "0":
            print("Terima kasih.")
            break
        else:
            print("Pilihan tidak valid.")


def menu_lapor():
    print("\n--- Lapor jalan rusak ---")
    try:
        jalan = minta_teks("Nama jalan        : ")
        kecamatan = minta_teks("Kecamatan         : ")
        tingkat = minta_teks("Tingkat (ringan/sedang/berat): ")
        foto = minta_teks("Nama file foto (.jpg/.png): ")
        kode = services.tambah_laporan(jalan, kecamatan, tingkat, foto)
        print(f"Laporan diterima. Kode laporan Anda: {kode}")
    except ValueError as e:
        print(f"Gagal: {e}")


def menu_cek_status():
    kode = minta_teks("Masukkan kode laporan: ")
    laporan = services.cari_laporan(kode)
    if laporan is None:
        print("Kode tidak ditemukan.")
        return
    print(f"Kode      : {laporan['kode']}")
    print(f"Jalan     : {laporan['jalan']}")
    print(f"Kecamatan : {laporan['kecamatan']}")
    print(f"Tingkat   : {laporan['tingkat']}")
    print(f"Status    : {laporan['status']}")
    print(f"Pelapor   : {laporan['jumlah_pelapor']}")
    riwayat = services.riwayat_tindak_lanjut(kode)
    if not riwayat:
        print("Tindak lanjut: belum ada")
    else:
        print("Riwayat tindak lanjut:")
        for i, t in enumerate(riwayat, 1):
            print(f"  {i}. {t['catatan']} (PJ: {t['penanggung_jawab']})")
            print(f"     Rencana: {t['tanggal_rencana']} | Selesai: {t['tanggal_selesai']}")
            print(f"     Foto sesudah: {t['foto_sesudah']}")


def menu_daftar_laporan():
    daftar = services.filter_laporan()
    if not daftar:
        print("Belum ada laporan.")
        return
    for l in daftar:
        print(f"{l['kode']} | {l['jalan']} | {l['kecamatan']} | "
              f"{l['tingkat']} | {l['status']} | pelapor: {l['jumlah_pelapor']}")


def menu_dashboard():
    rekap = services.rekap_laporan()
    print("\n--- Dashboard RoadWatch Lampung ---")
    print(f"Total laporan      : {rekap['total']}")
    for status, jumlah in rekap["rekap_status"].items():
        print(f"{status:<18} : {jumlah}")
    print(f"Total pelapor      : {rekap['total_pelapor']}")
    print(f"Persentase selesai : {rekap['persentase_selesai']}%")
    print("\n--- Top 5 Prioritas ---")
    for i, l in enumerate(services.urutkan_prioritas()[:5], 1):
        print(f"{i}. {l['jalan']} ({l['kecamatan']}) | {l['tingkat']} | skor {l['skor']}")


def menu_login():
    username = minta_teks("Username: ")
    password = minta_teks("Password: ")
    pengguna = services.login(username, password)
    if pengguna is None:
        print("Login gagal. Username atau password salah.")
        return
    print(f"Selamat datang, {pengguna['nama']} ({pengguna['peran']})")
    menu_staf(pengguna)


def menu_staf(pengguna):
    while True:
        print("\n--- Menu Staf ---")
        print("1. Lihat laporan baru")
        print("2. Verifikasi laporan")
        print("3. Ubah status laporan")
        print("4. Catat tindak lanjut")
        print("5. Tandai tindak lanjut selesai")
        print("6. Lihat prioritas")
        if pengguna["peran"] == "admin":
            print("7. Tambah petugas")
        print("0. Logout")
        pilihan = input("Pilih: ").strip()

        try:
            if pilihan == "1":
                for l in services.filter_laporan("Baru"):
                    print(f"{l['kode']} | {l['jalan']} | {l['tingkat']}")
            elif pilihan == "2":
                kode = minta_teks("Kode laporan: ")
                jawab = minta_teks("Laporan valid? (y/n): ")
                services.verifikasi_laporan(kode, jawab.lower() == "y", pengguna["peran"])
                print("Verifikasi tersimpan.")
            elif pilihan == "3":
                kode = minta_teks("Kode laporan: ")
                status = minta_teks("Status baru (Dalam Penanganan/Selesai): ")
                services.ubah_status(kode, status, pengguna["peran"])
                print("Status diubah.")
            elif pilihan == "4":
                kode = minta_teks("Kode laporan: ")
                catatan = minta_teks("Catatan tindakan: ")
                pj = minta_teks("Penanggung jawab: ")
                tgl = minta_teks("Tanggal rencana (dd-MM-yyyy): ")
                services.catat_tindak_lanjut(kode, catatan, pj, tgl, pengguna["peran"])
                print("Tindak lanjut dicatat.")
            elif pilihan == "5":
                kode = minta_teks("Kode laporan: ")
                tgl = minta_teks("Tanggal selesai (dd-MM-yyyy): ")
                foto = minta_teks("Foto sesudah (.jpg/.png): ")
                services.selesaikan_tindak_lanjut(kode, tgl, foto, pengguna["peran"])
                print("Tindak lanjut ditandai selesai.")
            elif pilihan == "6":
                for i, l in enumerate(services.urutkan_prioritas(), 1):
                    print(f"{i}. {l['kode']} | {l['jalan']} | skor {l['skor']}")
            elif pilihan == "7" and pengguna["peran"] == "admin":
                tambah_petugas()
            elif pilihan == "0":
                print("Anda telah logout.")
                break
            else:
                print("Pilihan tidak valid.")
        except ValueError as e:
            print(f"Gagal: {e}")


def tambah_petugas():
    id_pengguna = minta_teks("ID petugas: ")
    nama = minta_teks("Nama petugas: ")
    username = minta_teks("Username: ")
    password = minta_teks("Password (min 6 karakter): ")
    services.tambah_pengguna("admin", id_pengguna, nama, username, password)
    print("Petugas ditambahkan.")


if __name__ == "__main__":
    storage.buat_file_laporan()
    storage.buat_file_tindak_lanjut()
    menu_utama()
