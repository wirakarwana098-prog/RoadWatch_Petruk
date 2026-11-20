TINGKAT_KERUSAKAN_VALID = ("Ringan", "Sedang", "Berat")
STATUS_LAPORAN_VALID = ("Baru", "Terverifikasi", "Dalam Penanganan", "Selesai", "Ditolak")


def validasi_laporan(nama_jalan: str, wilayah: str, tingkat_kerusakan: str, foto: str) -> None:
    assert isinstance(nama_jalan, str) and isinstance(wilayah, str), "Nama jalan dan wilayah harus berupa teks!"

    if not nama_jalan.strip() or not wilayah.strip():
        raise ValueError("Nama jalan dan wilayah wajib diisi.")

    if tingkat_kerusakan not in TINGKAT_KERUSAKAN_VALID:
        raise ValueError(f"Tingkat kerusakan harus salah satu dari: {', '.join(TINGKAT_KERUSAKAN_VALID)}.")

    if not foto or not foto.strip():
        raise ValueError("Foto bukti kerusakan jalan wajib dilampirkan.")


def validasi_status(status_baru: str) -> None:
    assert isinstance(status_baru, str), "Status harus berupa teks!"
    if status_baru not in STATUS_LAPORAN_VALID:
        raise ValueError(f"Status '{status_baru}' tidak valid.")