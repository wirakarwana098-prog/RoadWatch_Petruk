from flask import Flask, jsonify, request
from roadwatch.services import PengelolaLaporan, filter_laporan_dinamis


class AplikasiRoadWatch:
    def __init__(self, path_file: str = "data/laporan.txt"):
        self.app = Flask(__name__)
        self.pengelola = PengelolaLaporan(path_file=path_file)
        self._isi_data_awal()
        self._daftarkan_rute()

    def _isi_data_awal(self) -> None:
        if not self.pengelola.daftar_laporan:
            data_awal = [
                ("Jl. ZA Pagar Alam", "Kedaton", "Berat", "pagar_alam.jpg"),
                ("Jl. Teuku Umar", "Kedaton", "Sedang", "teuku_umar.jpg"),
                ("Jl. Soekarno-Hatta", "Sukarame", "Berat", "bypass.jpg"),
                ("Jl. Kartini", "Tanjung Karang Pusat", "Ringan", "kartini.jpg"),
            ]
            for jalan, wilayah, tingkat, foto in data_awal:
                self.pengelola.buat_atau_gabung_laporan(
                    nama_jalan=jalan,
                    wilayah=wilayah,
                    tingkat_kerusakan=tingkat,
                    foto=foto,
                )

    def _daftarkan_rute(self) -> None:
        @self.app.route("/api/laporan", methods=["GET"])
        def menu_daftar_laporan():
            kata_kunci = request.args.get("q", "")
            wilayah = request.args.get("wilayah", "")
            status = request.args.get("status", "")
            urut = request.args.get("sort_by", "prioritas")

            if kata_kunci:
                data = self.pengelola.cari_kata_kunci(kata_kunci=kata_kunci)
            elif wilayah or status:
                data = filter_laporan_dinamis(
                    self.pengelola.daftar_laporan,
                    wilayah=wilayah,
                    status=status,
                )
            else:
                data = self.pengelola.daftar_laporan

            hasil_urut = self.pengelola.ambil_laporan_terurut(kriteria=urut, data_sumber=data)
            return jsonify(hasil_urut)

        @self.app.route("/api/lapor", methods=["POST"])
        def aksi_kirim_laporan():
            payload = request.get_json(silent=True) or {}
            try:
                hasil = self.pengelola.buat_atau_gabung_laporan(
                    nama_jalan=payload.get("nama_jalan", ""),
                    wilayah=payload.get("wilayah", ""),
                    tingkat_kerusakan=payload.get("tingkat_kerusakan", ""),
                    foto=payload.get("foto", ""),
                )
                return jsonify(hasil), 201
            except (ValueError, AssertionError) as err:
                return jsonify({"error": str(err)}), 400

        @self.app.route("/api/cek/<kode_laporan>", methods=["GET"])
        def aksi_cek_kode(kode_laporan: str):
            hasil = self.pengelola.cari_berdasarkan_kode(kode_laporan=kode_laporan)
            if hasil is None:
                return jsonify({"error": "Kode laporan tidak ditemukan."}), 404
            return jsonify(hasil)

        @self.app.route("/api/petugas/status", methods=["POST"])
        def aksi_ubah_status():
            payload = request.get_json(silent=True) or {}
            try:
                hasil = self.pengelola.perbarui_status_laporan(
                    kode_laporan=payload.get("kode_laporan", ""),
                    status_baru=payload.get("status_baru", ""),
                    catatan=payload.get("catatan", "-"),
                )
                return jsonify(hasil)
            except (ValueError, AssertionError) as err:
                return jsonify({"error": str(err)}), 400

        @self.app.route("/api/statistik", methods=["GET"])
        def menu_statistik():
            return jsonify(self.pengelola.ringkasan_statistik())

    def jalankan(self, port: int = 5000) -> None:
        self.app.run(debug=True, port=port)


if __name__ == "__main__":
    aplikasi = AplikasiRoadWatch()
    aplikasi.jalankan(port=5000)