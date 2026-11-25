import os
from datetime import datetime
from flask import Flask, jsonify, render_template, request, send_from_directory, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "roadwatch-lampung-secret-key-2026"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")

FILE_LAPORAN = os.path.join(DATA_DIR, "laporan.txt")
FILE_PENGGUNA = os.path.join(DATA_DIR, "pengguna.txt")
FILE_TINDAK_LANJUT = os.path.join(DATA_DIR, "tindak_lanjut.txt")

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

BOBOT_TINGKAT = {
    "ringan": 1,
    "sedang": 2,
    "berat": 3,
}


def pastikan_direktori_dan_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    if not os.path.exists(FILE_PENGGUNA):
        with open(FILE_PENGGUNA, "w", encoding="utf-8") as f:
            f.write("A001|Administrator|admin|admin123|admin|Admin PUPR\n")
            f.write("P001|Wira Karwana|wira|wira123|petugas|Petugas PUPR\n")

    if not os.path.exists(FILE_LAPORAN):
        with open(FILE_LAPORAN, "w", encoding="utf-8") as f:
            f.write("RW-0001|Jl. ZA Pagar Alam|Kedaton|Berat|1|31|Baru|25-11-2026|contoh_1.jpg\n")
            f.write("RW-0002|Jl. Teuku Umar|Kedaton|Sedang|3|23|Terverifikasi|24-11-2026|contoh_2.jpg\n")
            f.write("RW-0003|Jl. Ryacudu|Sukarame|Berat|2|32|Dalam Penanganan|23-11-2026|contoh_3.jpg\n")

    if not os.path.exists(FILE_TINDAK_LANJUT):
        with open(FILE_TINDAK_LANJUT, "w", encoding="utf-8") as f:
            f.write("RW-0003|Tim Bina Marga Wilayah II|Penambalan aspal hotmix dan perataan bahu jalan|26-11-2026|-|-\n")


def mengandung_pemisah(teks):
    return "|" in str(teks or "")


def ekstensi_valid(nama_file):
    if "." not in nama_file:
        return False
    eks = nama_file.rsplit(".", 1)[1].lower()
    return eks in ALLOWED_EXTENSIONS


def hitung_skor(tingkat, jumlah_pelapor):
    bobot = BOBOT_TINGKAT.get(str(tingkat).strip().lower(), 1)
    return bobot * 10 + int(jumlah_pelapor)


def normalisasi_tingkat(tingkat):
    t = str(tingkat or "").strip().lower()
    if t == "berat":
        return "Berat"
    if t == "sedang":
        return "Sedang"
    if t == "ringan":
        return "Ringan"
    return ""


def baca_pengguna():
    pastikan_direktori_dan_file()
    daftar = []
    with open(FILE_PENGGUNA, "r", encoding="utf-8") as f:
        for baris in f:
            baris = baris.strip()
            if not baris:
                continue
            bagian = baris.split("|")
            if len(bagian) >= 6:
                daftar.append({
                    "id": bagian[0],
                    "nama": bagian[1],
                    "username": bagian[2],
                    "password": bagian[3],
                    "peran": bagian[4],
                    "jabatan": bagian[5],
                })
    return daftar


def simpan_pengguna(daftar):
    with open(FILE_PENGGUNA, "w", encoding="utf-8") as f:
        for u in daftar:
            f.write(
                f"{u['id']}|{u['nama']}|{u['username']}|{u['password']}|{u['peran']}|{u['jabatan']}\n"
            )


def baca_laporan():
    pastikan_direktori_dan_file()
    daftar = []
    with open(FILE_LAPORAN, "r", encoding="utf-8") as f:
        for baris in f:
            baris = baris.strip()
            if not baris:
                continue
            bagian = baris.split("|")
            if len(bagian) >= 9:
                jumlah_pelapor = int(bagian[4])
                tingkat = bagian[3]
                skor = hitung_skor(tingkat, jumlah_pelapor)
                daftar.append({
                    "kode": bagian[0],
                    "jalan": bagian[1],
                    "kecamatan": bagian[2],
                    "tingkat": tingkat,
                    "jumlah_pelapor": jumlah_pelapor,
                    "skor": skor,
                    "status": bagian[6],
                    "tanggal": bagian[7],
                    "foto": bagian[8],
                })
    return daftar


def simpan_laporan(daftar):
    with open(FILE_LAPORAN, "w", encoding="utf-8") as f:
        for l in daftar:
            f.write(
                f"{l['kode']}|{l['jalan']}|{l['kecamatan']}|{l['tingkat']}|"
                f"{l['jumlah_pelapor']}|{l['skor']}|{l['status']}|{l['tanggal']}|{l['foto']}\n"
            )


def baca_tindak_lanjut():
    pastikan_direktori_dan_file()
    daftar = []
    with open(FILE_TINDAK_LANJUT, "r", encoding="utf-8") as f:
        for baris in f:
            baris = baris.strip()
            if not baris:
                continue
            bagian = baris.split("|")
            if len(bagian) >= 6:
                daftar.append({
                    "kode": bagian[0],
                    "penanggung_jawab": bagian[1],
                    "catatan": bagian[2],
                    "tanggal_rencana": bagian[3],
                    "tanggal_selesai": bagian[4],
                    "foto_sesudah": bagian[5],
                })
    return daftar


def simpan_tindak_lanjut(daftar):
    with open(FILE_TINDAK_LANJUT, "w", encoding="utf-8") as f:
        for r in daftar:
            f.write(
                f"{r['kode']}|{r['penanggung_jawab']}|{r['catatan']}|"
                f"{r['tanggal_rencana']}|{r['tanggal_selesai']}|{r['foto_sesudah']}\n"
            )


def kunci_prioritas(item):
    return (item["skor"], item["jumlah_pelapor"], item["kode"])


def kunci_pelapor(item):
    return (item["jumlah_pelapor"], item["skor"], item["kode"])


def kunci_tanggal(item):
    try:
        tgl = datetime.strptime(item["tanggal"], "%d-%m-%Y")
    except ValueError:
        tgl = datetime.min
    return (tgl, item["skor"], item["kode"])


def selection_sort_prioritas(data):
    arr = list(data)
    n = len(arr)
    for i in range(n):
        idx_max = i
        for j in range(i + 1, n):
            if kunci_prioritas(arr[j]) > kunci_prioritas(arr[idx_max]):
                idx_max = j
        arr[i], arr[idx_max] = arr[idx_max], arr[i]
    return arr


def bubble_sort_prioritas(data):
    arr = list(data)
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if kunci_pelapor(arr[j]) < kunci_pelapor(arr[j + 1]):
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr


def insertion_sort_prioritas(data):
    arr = list(data)
    for i in range(1, len(arr)):
        key_item = arr[i]
        j = i - 1
        while j >= 0 and kunci_tanggal(arr[j]) < kunci_tanggal(key_item):
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key_item
    return arr


def insertion_sort_kode(data):
    arr = list(data)
    for i in range(1, len(arr)):
        key_item = arr[i]
        j = i - 1
        while j >= 0 and arr[j]["kode"].upper() > key_item["kode"].upper():
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key_item
    return arr


def linear_search_kode(data, target_kode):
    target = target_kode.strip().upper()
    for item in data:
        if item["kode"].upper() == target:
            return item
    return None


def binary_search_kode(data_terurut, target_kode):
    target = target_kode.strip().upper()
    low = 0
    high = len(data_terurut) - 1
    while low <= high:
        mid = (low + high) // 2
        kode_mid = data_terurut[mid]["kode"].upper()
        if kode_mid == target:
            return data_terurut[mid]
        if kode_mid < target:
            low = mid + 1
        else:
            high = mid - 1
    return None


def pengguna_saat_ini():
    user_id = session.get("user_id")
    if not user_id:
        return None
    for u in baca_pengguna():
        if u["id"] == user_id:
            return {
                "id": u["id"],
                "nama": u["nama"],
                "username": u["username"],
                "peran": u["peran"],
                "jabatan": u["jabatan"],
            }
    return None


def buat_kode_baru(daftar_laporan):
    max_num = 0
    for l in daftar_laporan:
        kode = l["kode"].upper()
        if kode.startswith("RW-"):
            angka_str = kode.replace("RW-", "")
            if angka_str.isdigit():
                num = int(angka_str)
                if num > max_num:
                    max_num = num
    return f"RW-{max_num + 1:04d}"


@app.route("/")
def halaman_utama():
    return render_template("index.html")


@app.route("/panel")
def halaman_panel():
    return render_template("panel.html")


@app.route("/uploads/<path:filename>")
def unduh_foto(filename):
    return send_from_directory(UPLOAD_DIR, filename)


@app.route("/api/sesi", methods=["GET"])
def api_sesi():
    user = pengguna_saat_ini()
    if user:
        return jsonify({"login": True, "pengguna": user})
    return jsonify({"login": False, "pengguna": None})


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    for u in baca_pengguna():
        if u["username"] == username and u["password"] == password:
            session["user_id"] = u["id"]
            return jsonify({
                "sukses": True,
                "pengguna": {
                    "id": u["id"],
                    "nama": u["nama"],
                    "username": u["username"],
                    "peran": u["peran"],
                    "jabatan": u["jabatan"],
                },
            })

    return jsonify({"sukses": False, "pesan": "Username atau password tidak sesuai."}), 401


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.pop("user_id", None)
    return jsonify({"sukses": True})


@app.route("/api/statistik", methods=["GET"])
def api_statistik():
    daftar = baca_laporan()
    rekap = {
        "Baru": 0,
        "Terverifikasi": 0,
        "Dalam Penanganan": 0,
        "Selesai": 0,
        "Ditolak": 0,
    }
    total_pelapor = 0
    for l in daftar:
        status = l["status"]
        if status in rekap:
            rekap[status] += 1
        total_pelapor += l["jumlah_pelapor"]

    total = len(daftar)
    persentase_selesai = round((rekap["Selesai"] / total) * 100) if total > 0 else 0

    return jsonify({
        "sukses": True,
        "total": total,
        "rekap_status": rekap,
        "persentase_selesai": persentase_selesai,
        "total_pelapor": total_pelapor,
    })


@app.route("/api/laporan", methods=["GET"])
def api_daftar_laporan():
    status_filter = request.args.get("status", "").strip()
    kecamatan_filter = request.args.get("kecamatan", "").strip()
    tingkat_filter = request.args.get("tingkat", "").strip()
    metode = request.args.get("metode", "selection").strip().lower()

    daftar = baca_laporan()

    if status_filter:
        daftar = [l for l in daftar if l["status"].lower() == status_filter.lower()]
    if kecamatan_filter:
        daftar = [l for l in daftar if l["kecamatan"].lower() == kecamatan_filter.lower()]
    if tingkat_filter:
        daftar = [l for l in daftar if l["tingkat"].lower() == tingkat_filter.lower()]

    if metode == "bubble":
        daftar = bubble_sort_prioritas(daftar)
    elif metode == "insertion":
        daftar = insertion_sort_prioritas(daftar)
    elif metode == "kode":
        daftar = insertion_sort_kode(daftar)
    else:
        daftar = selection_sort_prioritas(daftar)

    return jsonify({"sukses": True, "laporan": daftar})


@app.route("/api/laporan", methods=["POST"])
def api_tambah_laporan():
    jalan = str(request.form.get("jalan", "")).strip()
    kecamatan = str(request.form.get("kecamatan", "")).strip()
    tingkat = normalisasi_tingkat(request.form.get("tingkat", ""))
    foto = request.files.get("foto")

    if not jalan or not kecamatan or not tingkat:
        return jsonify({"sukses": False, "pesan": "Nama jalan, kecamatan, dan tingkat kerusakan wajib diisi."}), 400

    if mengandung_pemisah(jalan) or mengandung_pemisah(kecamatan):
        return jsonify({"sukses": False, "pesan": "Input tidak boleh mengandung karakter '|'."}), 400

    if not foto or not foto.filename:
        return jsonify({"sukses": False, "pesan": "Foto bukti kerusakan wajib diunggah."}), 400

    if not ekstensi_valid(foto.filename):
        return jsonify({"sukses": False, "pesan": "Format foto harus .jpg, .jpeg, atau .png."}), 400

    daftar = baca_laporan()
    jalan_norm = jalan.lower()
    kecamatan_norm = kecamatan.lower()

    for l in daftar:
        if (
            l["jalan"].strip().lower() == jalan_norm
            and l["kecamatan"].strip().lower() == kecamatan_norm
            and l["status"] not in ("Selesai", "Ditolak")
        ):
            l["jumlah_pelapor"] += 1
            bobot_lama = BOBOT_TINGKAT.get(l["tingkat"].lower(), 1)
            bobot_baru = BOBOT_TINGKAT.get(tingkat.lower(), 1)
            if bobot_baru > bobot_lama:
                l["tingkat"] = tingkat
            l["skor"] = hitung_skor(l["tingkat"], l["jumlah_pelapor"])
            simpan_laporan(daftar)
            return jsonify({
                "sukses": True,
                "kode": l["kode"],
                "pesan": f"Lokasi sudah pernah dilaporkan ({l['kode']}). Laporan digabungkan, total pelapor kini {l['jumlah_pelapor']} orang dengan skor {l['skor']}.",
            })

    kode_baru = buat_kode_baru(daftar)
    eks = foto.filename.rsplit(".", 1)[1].lower()
    nama_file_foto = secure_filename(f"{kode_baru.lower()}_{int(datetime.now().timestamp())}.{eks}")
    foto.save(os.path.join(UPLOAD_DIR, nama_file_foto))

    skor_awal = hitung_skor(tingkat, 1)
    tanggal_hari_ini = datetime.now().strftime("%d-%m-%Y")

    laporan_baru = {
        "kode": kode_baru,
        "jalan": jalan,
        "kecamatan": kecamatan,
        "tingkat": tingkat,
        "jumlah_pelapor": 1,
        "skor": skor_awal,
        "status": "Baru",
        "tanggal": tanggal_hari_ini,
        "foto": nama_file_foto,
    }
    daftar.append(laporan_baru)
    simpan_laporan(daftar)

    return jsonify({
        "sukses": True,
        "kode": kode_baru,
        "pesan": f"Laporan berhasil dikirim! Simpan kode {kode_baru} untuk memantau progres perbaikan.",
    }), 201


@app.route("/api/laporan/<kode>", methods=["GET"])
def api_detail_laporan(kode):
    pakai_binary = request.args.get("binary", "false").strip().lower() == "true"
    daftar = baca_laporan()

    if pakai_binary:
        terurut = insertion_sort_kode(daftar)
        ditemukan = binary_search_kode(terurut, kode)
        nama_algoritma = "Binary Search (Insertion Sort)"
    else:
        ditemukan = linear_search_kode(daftar, kode)
        nama_algoritma = "Linear Search"

    if not ditemukan:
        return jsonify({
            "sukses": False,
            "pesan": f"Laporan dengan kode '{kode.strip().upper()}' tidak ditemukan.",
        }), 404

    semua_riwayat = baca_tindak_lanjut()
    riwayat_kode = [r for r in semua_riwayat if r["kode"].upper() == ditemukan["kode"].upper()]

    return jsonify({
        "sukses": True,
        "algoritma": nama_algoritma,
        "laporan": ditemukan,
        "riwayat": riwayat_kode,
    })


@app.route("/api/petugas/verifikasi", methods=["POST"])
def api_verifikasi_laporan():
    user = pengguna_saat_ini()
    if not user:
        return jsonify({"sukses": False, "pesan": "Sesi berakhir, silakan login ulang."}), 401

    data = request.get_json(silent=True) or {}
    kode = str(data.get("kode", "")).strip().upper()
    valid = bool(data.get("valid", False))

    daftar = baca_laporan()
    target = linear_search_kode(daftar, kode)
    if not target:
        return jsonify({"sukses": False, "pesan": "Laporan tidak ditemukan."}), 404

    if target["status"] != "Baru":
        return jsonify({"sukses": False, "pesan": "Hanya laporan berstatus Baru yang dapat diverifikasi."}), 400

    target["status"] = "Terverifikasi" if valid else "Ditolak"
    simpan_laporan(daftar)

    return jsonify({"sukses": True, "laporan": target})


@app.route("/api/petugas/tindak-lanjut", methods=["POST"])
def api_catat_tindak_lanjut():
    user = pengguna_saat_ini()
    if not user:
        return jsonify({"sukses": False, "pesan": "Sesi berakhir, silakan login ulang."}), 401

    data = request.get_json(silent=True) or {}
    kode = str(data.get("kode", "")).strip().upper()
    catatan = str(data.get("catatan", "")).strip()
    penanggung_jawab = str(data.get("penanggung_jawab", "")).strip()
    tanggal_rencana = str(data.get("tanggal_rencana", "")).strip()

    if not kode or not catatan or not penanggung_jawab or not tanggal_rencana:
        return jsonify({"sukses": False, "pesan": "Semua kolom tindak lanjut wajib diisi."}), 400

    if mengandung_pemisah(catatan) or mengandung_pemisah(penanggung_jawab) or mengandung_pemisah(tanggal_rencana):
        return jsonify({"sukses": False, "pesan": "Input tidak boleh mengandung karakter '|'."}), 400

    daftar = baca_laporan()
    target = linear_search_kode(daftar, kode)
    if not target:
        return jsonify({"sukses": False, "pesan": "Laporan tidak ditemukan."}), 404

    if target["status"] not in ("Terverifikasi", "Dalam Penanganan"):
        return jsonify({"sukses": False, "pesan": "Laporan harus berstatus Terverifikasi atau Dalam Penanganan."}), 400

    target["status"] = "Dalam Penanganan"
    simpan_laporan(daftar)

    daftar_tl = baca_tindak_lanjut()
    daftar_tl.append({
        "kode": target["kode"],
        "penanggung_jawab": penanggung_jawab,
        "catatan": catatan,
        "tanggal_rencana": tanggal_rencana,
        "tanggal_selesai": "-",
        "foto_sesudah": "-",
    })
    simpan_tindak_lanjut(daftar_tl)

    return jsonify({"sukses": True, "pesan": "Tindak lanjut berhasil dicatat."})


@app.route("/api/petugas/selesai", methods=["POST"])
def api_tandai_selesai():
    user = pengguna_saat_ini()
    if not user:
        return jsonify({"sukses": False, "pesan": "Sesi berakhir, silakan login ulang."}), 401

    kode = str(request.form.get("kode", "")).strip().upper()
    tanggal_selesai = str(request.form.get("tanggal_selesai", "")).strip()
    foto_sesudah = request.files.get("foto_sesudah")

    if not kode or not tanggal_selesai:
        return jsonify({"sukses": False, "pesan": "Kode laporan dan tanggal selesai wajib diisi."}), 400

    if mengandung_pemisah(tanggal_selesai):
        return jsonify({"sukses": False, "pesan": "Input tidak boleh mengandung karakter '|'."}), 400

    if not foto_sesudah or not foto_sesudah.filename:
        return jsonify({"sukses": False, "pesan": "Foto sesudah perbaikan wajib diunggah."}), 400

    if not ekstensi_valid(foto_sesudah.filename):
        return jsonify({"sukses": False, "pesan": "Format foto harus .jpg, .jpeg, atau .png."}), 400

    daftar = baca_laporan()
    target = linear_search_kode(daftar, kode)
    if not target:
        return jsonify({"sukses": False, "pesan": "Laporan tidak ditemukan."}), 404

    if target["status"] not in ("Terverifikasi", "Dalam Penanganan"):
        return jsonify({"sukses": False, "pesan": "Laporan belum diverifikasi atau sudah selesai."}), 400

    eks = foto_sesudah.filename.rsplit(".", 1)[1].lower()
    nama_file_sesudah = secure_filename(f"selesai_{target['kode'].lower()}_{int(datetime.now().timestamp())}.{eks}")
    foto_sesudah.save(os.path.join(UPLOAD_DIR, nama_file_sesudah))

    target["status"] = "Selesai"
    simpan_laporan(daftar)

    daftar_tl = baca_tindak_lanjut()
    diperbarui = False
    for r in reversed(daftar_tl):
        if r["kode"].upper() == target["kode"].upper() and r["tanggal_selesai"] == "-":
            r["tanggal_selesai"] = tanggal_selesai
            r["foto_sesudah"] = nama_file_sesudah
            diperbarui = True
            break

    if not diperbarui:
        daftar_tl.append({
            "kode": target["kode"],
            "penanggung_jawab": user["nama"],
            "catatan": "Perbaikan jalan telah diselesaikan",
            "tanggal_rencana": tanggal_selesai,
            "tanggal_selesai": tanggal_selesai,
            "foto_sesudah": nama_file_sesudah,
        })

    simpan_tindak_lanjut(daftar_tl)
    return jsonify({"sukses": True, "pesan": f"Laporan {target['kode']} berhasil ditandai Selesai."})


@app.route("/api/admin/pengguna", methods=["GET"])
def api_admin_daftar_pengguna():
    user = pengguna_saat_ini()
    if not user or user["peran"] != "admin":
        return jsonify({"sukses": False, "pesan": "Akses ditolak. Khusus Administrator."}), 403

    hasil = []
    for u in baca_pengguna():
        hasil.append({
            "id": u["id"],
            "nama": u["nama"],
            "username": u["username"],
            "peran": u["peran"],
            "jabatan": u["jabatan"],
        })
    return jsonify({"sukses": True, "pengguna": hasil})


@app.route("/api/admin/pengguna", methods=["POST"])
def api_admin_tambah_pengguna():
    user = pengguna_saat_ini()
    if not user or user["peran"] != "admin":
        return jsonify({"sukses": False, "pesan": "Akses ditolak. Khusus Administrator."}), 403

    data = request.get_json(silent=True) or {}
    id_baru = str(data.get("id", "")).strip().upper()
    nama = str(data.get("nama", "")).strip()
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    if not id_baru or not nama or not username or not password:
        return jsonify({"sukses": False, "pesan": "Semua kolom petugas wajib diisi."}), 400

    if any(mengandung_pemisah(v) for v in (id_baru, nama, username, password)):
        return jsonify({"sukses": False, "pesan": "Input tidak boleh mengandung karakter '|'."}), 400

    if len(password) < 6:
        return jsonify({"sukses": False, "pesan": "Password minimal 6 karakter."}), 400

    daftar = baca_pengguna()
    for u in daftar:
        if u["id"].upper() == id_baru:
            return jsonify({"sukses": False, "pesan": f"ID {id_baru} sudah terdaftar."}), 400
        if u["username"].lower() == username.lower():
            return jsonify({"sukses": False, "pesan": f"Username '{username}' sudah digunakan."}), 400

    pengguna_baru = {
        "id": id_baru,
        "nama": nama,
        "username": username,
        "password": password,
        "peran": "petugas",
        "jabatan": "Petugas PUPR",
    }
    daftar.append(pengguna_baru)
    simpan_pengguna(daftar)

    return jsonify({
        "sukses": True,
        "pengguna": {
            "id": pengguna_baru["id"],
            "nama": pengguna_baru["nama"],
            "username": pengguna_baru["username"],
            "peran": pengguna_baru["peran"],
            "jabatan": pengguna_baru["jabatan"],
        },
    }), 201


@app.route("/api/admin/pengguna/<user_id>", methods=["DELETE"])
def api_admin_hapus_pengguna(user_id):
    user = pengguna_saat_ini()
    if not user or user["peran"] != "admin":
        return jsonify({"sukses": False, "pesan": "Akses ditolak. Khusus Administrator."}), 403

    target_id = user_id.strip().upper()
    if target_id == user["id"].upper():
        return jsonify({"sukses": False, "pesan": "Tidak dapat menghapus akun yang sedang aktif digunakan."}), 400

    daftar = baca_pengguna()
    baru = []
    ditemukan = False
    for u in daftar:
        if u["id"].upper() == target_id:
            if u["peran"] == "admin":
                return jsonify({"sukses": False, "pesan": "Akun Administrator utama tidak dapat dihapus."}), 400
            ditemukan = True
            continue
        baru.append(u)

    if not ditemukan:
        return jsonify({"sukses": False, "pesan": "Akun petugas tidak ditemukan."}), 404

    simpan_pengguna(baru)
    return jsonify({"sukses": True, "pesan": f"Akun petugas {target_id} berhasil dihapus."})


@app.route("/api/admin/pengguna/<user_id>/reset-password", methods=["POST"])
def api_admin_reset_password(user_id):
    user = pengguna_saat_ini()
    if not user or user["peran"] != "admin":
        return jsonify({"sukses": False, "pesan": "Akses ditolak. Khusus Administrator."}), 403

    data = request.get_json(silent=True) or {}
    password_baru = str(data.get("password_baru", "")).strip()

    if len(password_baru) < 6:
        return jsonify({"sukses": False, "pesan": "Password baru minimal 6 karakter."}), 400

    if mengandung_pemisah(password_baru):
        return jsonify({"sukses": False, "pesan": "Password tidak boleh mengandung karakter '|'."}), 400

    target_id = user_id.strip().upper()
    daftar = baca_pengguna()
    ditemukan = False
    for u in daftar:
        if u["id"].upper() == target_id:
            u["password"] = password_baru
            ditemukan = True
            break

    if not ditemukan:
        return jsonify({"sukses": False, "pesan": "Akun petugas tidak ditemukan."}), 404

    simpan_pengguna(daftar)
    return jsonify({"sukses": True, "pesan": f"Password untuk {target_id} berhasil diperbarui."})


if __name__ == "__main__":
    pastikan_direktori_dan_file()
    app.run(debug=True, port=5000)