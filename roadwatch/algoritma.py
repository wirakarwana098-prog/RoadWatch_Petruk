#modularitas (menyediakan algoritma pencarian, pengurutan manual, dan rekursi untuk pengolahan data laporan)
#linear search (menelusuri elemen daftar laporan satu per satu secara berurutan hingga kode cocok, mengembalikan indeks atau -1)
def linear_search_laporan(daftar, kode):
    kode = kode.strip().lower()
    for i in range(len(daftar)):
        if daftar[i]["kode"].lower() == kode:
            return i
    return -1


#binary search (membagi rentang indeks daftar yang sudah terurut menjadi dua secara berulang untuk menemukan kode lebih cepat)
def binary_search_laporan(daftar_terurut, kode):
    kode = kode.strip().lower()
    awal, akhir = 0, len(daftar_terurut) - 1
    while awal <= akhir:
        tengah = (awal + akhir) // 2
        kode_tengah = daftar_terurut[tengah]["kode"].lower()
        if kode_tengah == kode:
            return tengah
        elif kode_tengah < kode:
            awal = tengah + 1
        else:
            akhir = tengah - 1
    return -1


#selection sort (mencari nilai terbesar/terkecil pada sisa daftar lalu menukarnya ke posisi terurut tanpa mengubah list asli)
def selection_sort(daftar, kunci, menurun=True):
    data = list(daftar)
    n = len(data)
    for i in range(n):
        idx = i
        for j in range(i + 1, n):
            kiri, kanan = data[j][kunci], data[idx][kunci]
            if (kanan < kiri) if menurun else (kanan > kiri):
                idx = j
        data[i], data[idx] = data[idx], data[i]
    return data


#insertion sort (mengambil elemen satu per satu dan menyisipkannya ke posisi yang tepat pada bagian daftar yang sudah terurut)
def insertion_sort(daftar, kunci, menurun=False):
    data = list(daftar)
    for i in range(1, len(data)):
        kunci_data = data[i]
        j = i - 1
        while j >= 0 and ((data[j][kunci] < kunci_data[kunci]) if menurun
                          else (data[j][kunci] > kunci_data[kunci])):
            data[j + 1] = data[j]
            j -= 1
        data[j + 1] = kunci_data
    return data


#bubble sort (membandingkan pasangan elemen bersebelahan dan menukarnya berulang kali hingga seluruh daftar terurut)
def bubble_sort(daftar, kunci, menurun=True):
    data = list(daftar)
    n = len(data)
    for i in range(n - 1):
        for j in range(n - 1 - i):
            tukar = (data[j][kunci] < data[j + 1][kunci]) if menurun \
                else (data[j][kunci] > data[j + 1][kunci])
            if tukar:
                data[j], data[j + 1] = data[j + 1], data[j]
    return data


#rekursi agregasi data (menjumlahkan nilai jumlah_pelapor dari setiap laporan secara rekursif hingga mencapai batas akhir daftar)
def total_pelapor_rekursif(daftar, indeks=0):
    if indeks >= len(daftar):
        return 0
    return daftar[indeks]["jumlah_pelapor"] + total_pelapor_rekursif(daftar, indeks + 1)