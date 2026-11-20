def linear_search(data: list, kata_kunci: str) -> list:
    hasil_pencarian = []
    target = kata_kunci.strip().lower()

    for indeks in range(len(data)):
        item = data[indeks]
        if (
            target in item["kode_laporan"].lower()
            or target in item["nama_jalan"].lower()
            or target in item["wilayah"].lower()
        ):
            hasil_pencarian.append(item)

    return hasil_pencarian


def binary_search(data_terurut: list, kode_target: str) -> int:
    indeks_awal = 0
    indeks_akhir = len(data_terurut) - 1
    target = kode_target.strip().upper()

    while indeks_awal <= indeks_akhir:
        indeks_tengah = (indeks_awal + indeks_akhir) // 2
        kode_tengah = data_terurut[indeks_tengah]["kode_laporan"].upper()

        if kode_tengah == target:
            return indeks_tengah
        elif kode_tengah < target:
            indeks_awal = indeks_tengah + 1
        else:
            indeks_akhir = indeks_tengah - 1

    return -1


def selection_sort(data: list, key_func=lambda x: x["skor_prioritas"], descending: bool = True) -> list:
    hasil = list(data)
    jumlah = len(hasil)

    for i in range(jumlah):
        indeks_pilihan = i
        for j in range(i + 1, jumlah):
            nilai_j = key_func(hasil[j])
            nilai_pilihan = key_func(hasil[indeks_pilihan])

            if descending:
                if nilai_j > nilai_pilihan:
                    indeks_pilihan = j
            else:
                if nilai_j < nilai_pilihan:
                    indeks_pilihan = j

        hasil[i], hasil[indeks_pilihan] = hasil[indeks_pilihan], hasil[i]

    return hasil


def insertion_sort(data: list, key_func=lambda x: x["kode_laporan"], descending: bool = False) -> list:
    hasil = list(data)
    jumlah = len(hasil)

    for i in range(1, jumlah):
        elemen_sisip = hasil[i]
        kunci_sisip = key_func(elemen_sisip)
        j = i - 1

        while j >= 0 and (
            (key_func(hasil[j]) < kunci_sisip) if descending else (key_func(hasil[j]) > kunci_sisip)
        ):
            hasil[j + 1] = hasil[j]
            j -= 1

        hasil[j + 1] = elemen_sisip

    return hasil


def hitung_total_skor_rekursif(daftar_laporan: list, indeks: int = 0) -> int:
    if indeks >= len(daftar_laporan):
        return 0

    return daftar_laporan[indeks]["skor_prioritas"] + hitung_total_skor_rekursif(daftar_laporan, indeks + 1)