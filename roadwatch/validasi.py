def validasi_teks(nilai, nama_kolom="input"):
    if not isinstance(nilai, str) or nilai.strip() == "":
        raise ValueError(f"{nama_kolom} tidak boleh kosong.")
    if "|" in nilai:
        raise ValueError(f"{nama_kolom} tidak boleh mengandung karakter '|'.")
    return nilai.strip()


def validasi_tingkat(tingkat):
    tingkat = validasi_teks(tingkat, "Tingkat kerusakan").lower()
    if tingkat not in ("ringan", "sedang", "berat"):
        raise ValueError("Tingkat kerusakan harus ringan, sedang, atau berat.")
    return tingkat.capitalize()


def validasi_foto(foto):
    foto = validasi_teks(foto, "Nama file foto")
    if not foto.lower().endswith((".jpg", ".jpeg", ".png")):
        raise ValueError("Format foto harus .jpg, .jpeg, atau .png.")
    return foto


def validasi_tanggal(teks, format_tanggal="%d-%m-%Y"):
    teks = validasi_teks(teks, "Tanggal")
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


def validasi_password(password):
    if not isinstance(password, str) or len(password) < 6:
        raise ValueError("Password minimal 6 karakter.")
    return password
