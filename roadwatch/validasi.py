#modularitas modul validasi (memastikan seluruh input pengguna memenuhi aturan format sebelum diproses atau disimpan)

#error handling raise validasi teks (memeriksa teks tidak kosong dan bebas karakter pemisah '|' agar struktur file tidak rusak)
def validasi_teks(nilai, nama_kolom="input"):
    if not isinstance(nilai, str) or nilai.strip() == "":
        raise ValueError(f"{nama_kolom} tidak boleh kosong.")
    if "|" in nilai:
        raise ValueError(f"{nama_kolom} tidak boleh mengandung karakter '|'.")
    return nilai.strip()


#validasi kategori (memastikan tingkat kerusakan hanya bernilai ringan, sedang, atau berat lalu menormalisasi huruf kapital)
def validasi_tingkat(tingkat):
    tingkat = validasi_teks(tingkat, "Tingkat kerusakan").lower()
    if tingkat not in ("ringan", "sedang", "berat"):
        raise ValueError("Tingkat kerusakan harus ringan, sedang, atau berat.")
    return tingkat.capitalize()


#validasi ekstensi file (memeriksa nama file foto berakhiran .jpg, .jpeg, atau .png dan melempar ValueError jika tidak sesuai)
def validasi_foto(foto):
    foto = validasi_teks(foto, "Nama file foto")
    if not foto.lower().endswith((".jpg", ".jpeg", ".png")):
        raise ValueError("Format foto harus .jpg, .jpeg, atau .png.")
    return foto


#error handling try/except & raise tanggal (memverifikasi format tanggal dd-MM-yyyy menggunakan datetime.strptime)
def validasi_tanggal(teks, format_tanggal="%d-%m-%Y"):
    teks = validasi_teks(teks, "Tanggal")
    #library - datetime (mengimpor kelas datetime untuk mengurai dan memvalidasi format string tanggal)
    from datetime import datetime
    try:
        datetime.strptime(teks, format_tanggal)
    except ValueError:
        raise ValueError(
            "Format tanggal harus "
            + format_tanggal.replace("%d", "dd").replace("%m", "MM").replace("%Y", "yyyy")
            + "."
        )
    return teks


#validasi keamanan akun (memastikan password bertipe string dengan panjang minimal 6 karakter)
def validasi_password(password):
    if not isinstance(password, str) or len(password) < 6:
        raise ValueError("Password minimal 6 karakter.")
    return password