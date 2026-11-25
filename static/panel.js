const statePanel = {
  pengguna: null,
  semuaLaporan: [],
  kodeCekTerpilih: null,
  kodeProgresTerpilih: null,
  daftarPetugas: [],
  idPetugasTerpilih: null,
};

function escapeHtml(teks) {
  return String(teks ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function formatTanggalBackend(isoDate) {
  if (!isoDate || !isoDate.includes("-")) return isoDate;
  const [tahun, bulan, hari] = isoDate.split("-");
  return `${hari}-${bulan}-${tahun}`;
}

function classBadgeStatus(status) {
  const s = String(status).toLowerCase();
  if (s === "baru") return "badge badge-baru";
  if (s === "terverifikasi") return "badge badge-terverifikasi";
  if (s === "dalam penanganan") return "badge badge-penanganan";
  if (s === "selesai") return "badge badge-selesai";
  return "badge badge-ditolak";
}

function tampilkanAlert(pesan, tipe = "success") {
  const el = document.getElementById("alertGlobalPanel");
  el.className = `alert-box ${tipe === "success" ? "alert-success" : "alert-error"}`;
  el.textContent = pesan;
  el.classList.remove("hidden");
}

function sembunyikanAlert() {
  document.getElementById("alertGlobalPanel").classList.add("hidden");
}

function aktifkanMenu(menuId) {
  sembunyikanAlert();
  document.querySelectorAll(".sidebar-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.getAttribute("data-menu") === menuId);
  });
  document.querySelectorAll(".menu-section").forEach((sec) => {
    sec.classList.toggle("hidden", sec.id !== menuId);
  });
}

function sinkronTampilanLogin() {
  const viewLogin = document.getElementById("viewLoginPanel");
  const viewDash = document.getElementById("viewDashboardPanel");
  const headerId = document.getElementById("headerUserIdentity");
  const btnLogout = document.getElementById("btnLogoutPanel");
  const btnMenuPetugas = document.getElementById("navBtnPetugas");

  if (statePanel.pengguna) {
    viewLogin.classList.add("hidden");
    viewDash.classList.remove("hidden");
    headerId.classList.remove("hidden");
    btnLogout.classList.remove("hidden");

    const jabatan =
      statePanel.pengguna.peran === "admin" ? "Admin PUPR" : "Petugas PUPR";
    headerId.textContent = `${statePanel.pengguna.nama} (${jabatan})`;

    const isAdmin = statePanel.pengguna.peran === "admin";
    btnMenuPetugas.classList.toggle("hidden", !isAdmin);
  } else {
    viewLogin.classList.remove("hidden");
    viewDash.classList.add("hidden");
    headerId.classList.add("hidden");
    btnLogout.classList.add("hidden");
  }
}

async function muatSemuaData() {
  try {
    const [resLap, resStat] = await Promise.all([
      fetch("/api/laporan?metode=selection"),
      fetch("/api/statistik"),
    ]);
    const dataLap = await resLap.json();
    const dataStat = await resStat.json();

    statePanel.semuaLaporan = dataLap.laporan || [];
    const rekap = dataStat.rekap_status || {};

    document.getElementById("statDashTotal").textContent = dataStat.total ?? 0;
    document.getElementById("statDashBaru").textContent = rekap["Baru"] ?? 0;
    document.getElementById("statDashVerif").textContent = rekap["Terverifikasi"] ?? 0;
    document.getElementById("statDashProses").textContent = rekap["Dalam Penanganan"] ?? 0;
    document.getElementById("statDashSelesai").textContent = rekap["Selesai"] ?? 0;
    document.getElementById("statDashPelapor").textContent = dataStat.total_pelapor ?? 0;

    renderTabelDashboard();
    renderTabelCekLaporan();
    renderTabelSiapDitangani();

    if (statePanel.kodeCekTerpilih) {
      const masihAdaCek = statePanel.semuaLaporan.some((l) => l.kode === statePanel.kodeCekTerpilih);
      if (masihAdaCek) {
        await pilihLaporanCek(statePanel.kodeCekTerpilih);
      } else {
        resetPilihanCek();
      }
    }

    if (statePanel.kodeProgresTerpilih) {
      const masihAda = statePanel.semuaLaporan.some(
        (l) =>
          l.kode === statePanel.kodeProgresTerpilih &&
          (l.status === "Terverifikasi" || l.status === "Dalam Penanganan")
      );
      if (masihAda) {
        pilihLaporanProgres(statePanel.kodeProgresTerpilih);
      } else {
        resetPilihanProgres();
      }
    }

    if (statePanel.pengguna?.peran === "admin") {
      await muatDaftarPetugas();
    }
  } catch (err) {
    console.error("Gagal memuat data panel:", err);
  }
}

function renderTabelDashboard() {
  const tbody = document.getElementById("tbodyDashRingkasan");
  if (!statePanel.semuaLaporan.length) {
    tbody.innerHTML = `<tr><td colspan="7" class="empty-cell">Belum ada data laporan.</td></tr>`;
    return;
  }
  tbody.innerHTML = statePanel.semuaLaporan
    .map(
      (l) => `
      <tr>
        <td><span class="code-chip">${escapeHtml(l.kode)}</span></td>
        <td><strong>${escapeHtml(l.jalan)}</strong></td>
        <td>${escapeHtml(l.kecamatan)}</td>
        <td>${escapeHtml(l.tingkat)}</td>
        <td>${escapeHtml(l.jumlah_pelapor)}</td>
        <td><strong>${escapeHtml(l.skor)}</strong></td>
        <td><span class="${classBadgeStatus(l.status)}">${escapeHtml(l.status)}</span></td>
      </tr>
    `
    )
    .join("");
}

function renderTabelCekLaporan() {
  const kata = document.getElementById("inputFilterCek").value.trim().toLowerCase();
  const statusFilter = document.getElementById("selectStatusCek").value;

  const hasil = statePanel.semuaLaporan.filter((l) => {
    const cocokStatus = !statusFilter || l.status === statusFilter;
    const cocokKata =
      !kata ||
      l.kode.toLowerCase().includes(kata) ||
      l.jalan.toLowerCase().includes(kata) ||
      l.kecamatan.toLowerCase().includes(kata);
    return cocokStatus && cocokKata;
  });

  const tbody = document.getElementById("tbodyCekLaporan");
  if (!hasil.length) {
    tbody.innerHTML = `<tr><td colspan="5" class="empty-cell">Tidak ada laporan yang cocok.</td></tr>`;
    return;
  }

  tbody.innerHTML = hasil
    .map(
      (l) => `
      <tr class="${l.kode === statePanel.kodeCekTerpilih ? "selected-row" : ""}" data-cek-kode="${escapeHtml(l.kode)}">
        <td><span class="code-chip">${escapeHtml(l.kode)}</span></td>
        <td>
          <div class="road-title">${escapeHtml(l.jalan)}</div>
          <div class="road-sub">${escapeHtml(l.kecamatan)}</div>
        </td>
        <td>${escapeHtml(l.tingkat)}</td>
        <td><strong>${escapeHtml(l.skor)}</strong></td>
        <td><span class="${classBadgeStatus(l.status)}">${escapeHtml(l.status)}</span></td>
      </tr>
    `
    )
    .join("");

  tbody.querySelectorAll("tr[data-cek-kode]").forEach((row) => {
    row.addEventListener("click", () => {
      const kode = row.getAttribute("data-cek-kode");
      if (statePanel.kodeCekTerpilih === kode) {
        resetPilihanCek();
      } else {
        pilihLaporanCek(kode);
      }
    });
  });
}

function resetPilihanCek() {
  statePanel.kodeCekTerpilih = null;
  document.getElementById("cekWorkspace").classList.add("single-col");
  document.getElementById("cekDetailCard").classList.add("hidden");
  document.getElementById("cekDetailBox").classList.add("hidden");
  renderTabelCekLaporan();
}

async function pilihLaporanCek(kode) {
  statePanel.kodeCekTerpilih = kode;
  renderTabelCekLaporan();

  const res = await fetch(`/api/laporan/${encodeURIComponent(kode)}`);
  const data = await res.json();
  if (!res.ok || !data.sukses) return;

  const lap = data.laporan;
  const riwayat = data.riwayat || [];

  document.getElementById("cekWorkspace").classList.remove("single-col");
  document.getElementById("cekDetailCard").classList.remove("hidden");
  document.getElementById("cekDetailBox").classList.remove("hidden");

  document.getElementById("cekKode").textContent = lap.kode;
  const badge = document.getElementById("cekStatusBadge");
  badge.className = classBadgeStatus(lap.status);
  badge.textContent = lap.status;

  document.getElementById("cekJalan").textContent = lap.jalan;
  document.getElementById("cekKecamatan").textContent = `Kecamatan ${lap.kecamatan}`;
  document.getElementById("cekTingkatSkor").textContent = `${lap.tingkat} (Skor ${lap.skor})`;
  document.getElementById("cekPelaporTanggal").textContent = `${lap.jumlah_pelapor} orang • ${lap.tanggal}`;

  document.getElementById("boxVerifikasiAksi").classList.toggle("hidden", lap.status !== "Baru");

  const listEl = document.getElementById("cekRiwayatList");
  if (!riwayat.length) {
    listEl.innerHTML = `<p class="road-sub">Belum ada riwayat tindak lanjut.</p>`;
  } else {
    listEl.innerHTML = `<div class="timeline-list">
      ${riwayat
        .map(
          (r) => `
          <div class="timeline-item">
            <strong>PJ:</strong> ${escapeHtml(r.penanggung_jawab)}<br>
            <strong>Catatan:</strong> ${escapeHtml(r.catatan)}<br>
            <strong>Rencana:</strong> ${escapeHtml(r.tanggal_rencana)} •
            <strong>Selesai:</strong> ${escapeHtml(r.tanggal_selesai)} •
            <strong>Foto:</strong> ${escapeHtml(r.foto_sesudah)}
          </div>
        `
        )
        .join("")}
    </div>`;
  }
}

function renderTabelSiapDitangani() {
  const siap = statePanel.semuaLaporan.filter(
    (l) => l.status === "Terverifikasi" || l.status === "Dalam Penanganan"
  );
  const tbody = document.getElementById("tbodySiapDitangani");

  if (!siap.length) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty-cell">Belum ada laporan berstatus Terverifikasi atau Dalam Penanganan.</td></tr>`;
    return;
  }

  tbody.innerHTML = siap
    .map(
      (l) => `
      <tr class="${l.kode === statePanel.kodeProgresTerpilih ? "selected-row" : ""}" data-prog-kode="${escapeHtml(l.kode)}">
        <td><span class="code-chip">${escapeHtml(l.kode)}</span></td>
        <td><strong>${escapeHtml(l.jalan)}</strong></td>
        <td>${escapeHtml(l.kecamatan)}</td>
        <td>${escapeHtml(l.tingkat)}</td>
        <td><span class="${classBadgeStatus(l.status)}">${escapeHtml(l.status)}</span></td>
        <td><strong>${escapeHtml(l.skor)}</strong></td>
      </tr>
    `
    )
    .join("");

  tbody.querySelectorAll("tr[data-prog-kode]").forEach((row) => {
    row.addEventListener("click", () => {
      const kode = row.getAttribute("data-prog-kode");
      if (statePanel.kodeProgresTerpilih === kode) {
        resetPilihanProgres();
      } else {
        pilihLaporanProgres(kode);
      }
    });
  });
}

function pilihLaporanProgres(kode) {
  statePanel.kodeProgresTerpilih = kode;
  renderTabelSiapDitangani();
  const lap = statePanel.semuaLaporan.find((l) => l.kode === kode);
  const actionBar = document.getElementById("progresActionBar");
  if (!lap) {
    resetPilihanProgres();
    return;
  }
  actionBar.classList.remove("hidden");
}

function resetPilihanProgres() {
  statePanel.kodeProgresTerpilih = null;
  document.getElementById("progresActionBar").classList.add("hidden");
  renderTabelSiapDitangani();
}

function generateIdPetugasOtomatis() {
  const daftarPetugasSaja = statePanel.daftarPetugas.filter((u) => {
    const peran = String(u.peran || "").toLowerCase();
    const id = String(u.id || "").toUpperCase();
    return peran === "petugas" || id.startsWith("P");
  });

  let maxAngka = 0;
  for (const u of daftarPetugasSaja) {
    const match = String(u.id || "").match(/(\d+)$/);
    if (match) {
      const num = parseInt(match[1], 10);
      if (num > maxAngka) maxAngka = num;
    }
  }

  const nextNum = Math.max(maxAngka + 1, daftarPetugasSaja.length + 1);
  const existingIds = new Set(statePanel.daftarPetugas.map((u) => String(u.id || "").toUpperCase()));

  let candidateNum = nextNum;
  let candidateId = `P${String(candidateNum).padStart(3, "0")}`;
  while (existingIds.has(candidateId)) {
    candidateNum += 1;
    candidateId = `P${String(candidateNum).padStart(3, "0")}`;
  }
  return candidateId;
}

function sinkronInputIdPetugasOtomatis() {
  const inputId = document.getElementById("newIdPetugas");
  if (inputId) {
    inputId.value = generateIdPetugasOtomatis();
  }
}

async function muatDaftarPetugas() {
  const res = await fetch("/api/admin/pengguna");
  const data = await res.json();
  if (!res.ok || !data.sukses) return;

  statePanel.daftarPetugas = data.pengguna || [];
  renderTabelPetugasAdmin();
  sinkronInputIdPetugasOtomatis();
}

function renderTabelPetugasAdmin() {
  const tbody = document.getElementById("tbodyPetugasAdmin");
  tbody.innerHTML = statePanel.daftarPetugas
    .map(
      (u) => `
      <tr class="${u.id === statePanel.idPetugasTerpilih ? "selected-row" : ""}" data-user-id="${escapeHtml(u.id)}">
        <td><strong>${escapeHtml(u.id)}</strong></td>
        <td>${escapeHtml(u.nama)}</td>
        <td><code>${escapeHtml(u.username)}</code></td>
        <td>${escapeHtml(u.jabatan)}</td>
      </tr>
    `
    )
    .join("");

  tbody.querySelectorAll("tr[data-user-id]").forEach((row) => {
    row.addEventListener("click", () => {
      statePanel.idPetugasTerpilih = row.getAttribute("data-user-id");
      renderTabelPetugasAdmin();
    });
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  document.getElementById("btnToggleDark").addEventListener("click", () => {
    const aktif = document.body.classList.toggle("dark-mode");
    document.getElementById("btnToggleDark").textContent = aktif ? "Mode Terang" : "Mode Gelap";
  });

  document.querySelectorAll(".sidebar-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      aktifkanMenu(btn.getAttribute("data-menu"));
    });
  });

  document.getElementById("formLoginPanel").addEventListener("submit", async (e) => {
    e.preventDefault();
    const alertLogin = document.getElementById("alertLoginPanel");
    const username = document.getElementById("panelUsername").value;
    const password = document.getElementById("panelPassword").value;

    const res = await fetch("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok || !data.sukses) {
      alertLogin.className = "alert-box alert-error";
      alertLogin.textContent = data.pesan || "Login gagal.";
      alertLogin.classList.remove("hidden");
      return;
    }

    alertLogin.classList.add("hidden");
    statePanel.pengguna = data.pengguna;
    sinkronTampilanLogin();
    await muatSemuaData();
  });

  document.getElementById("btnLogoutPanel").addEventListener("click", async () => {
    await fetch("/api/logout", { method: "POST" });
    statePanel.pengguna = null;
    statePanel.idPetugasTerpilih = null;
    resetPilihanCek();
    resetPilihanProgres();
    sinkronTampilanLogin();
  });

  document.getElementById("inputFilterCek").addEventListener("input", renderTabelCekLaporan);
  document.getElementById("selectStatusCek").addEventListener("change", renderTabelCekLaporan);
  document.getElementById("btnKembaliCekLaporan").addEventListener("click", resetPilihanCek);

  async function kirimVerifikasi(valid) {
    if (!statePanel.kodeCekTerpilih) return;
    const res = await fetch("/api/petugas/verifikasi", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ kode: statePanel.kodeCekTerpilih, valid }),
    });
    const data = await res.json();
    if (!res.ok || !data.sukses) {
      tampilkanAlert(data.pesan || "Gagal memverifikasi laporan.", "error");
      return;
    }
    tampilkanAlert(`Status ${statePanel.kodeCekTerpilih} diubah menjadi ${data.laporan.status}.`);
    await muatSemuaData();
    await pilihLaporanCek(statePanel.kodeCekTerpilih);
  }

  document.getElementById("btnVerifTerima").addEventListener("click", () => kirimVerifikasi(true));
  document.getElementById("btnVerifTolak").addEventListener("click", () => kirimVerifikasi(false));

  // Buka Pop-up Catat Tindak Lanjut
  const modalTl = document.getElementById("modalCatatTindakLanjut");
  document.getElementById("btnBukaPopupTindakLanjut").addEventListener("click", () => {
    if (!statePanel.kodeProgresTerpilih) return;
    const lap = statePanel.semuaLaporan.find((l) => l.kode === statePanel.kodeProgresTerpilih);
    document.getElementById("labelTargetModalTl").textContent = lap
      ? `Laporan: ${lap.kode} — ${lap.jalan} (${lap.kecamatan})`
      : `Laporan: ${statePanel.kodeProgresTerpilih}`;
    modalTl.classList.remove("hidden");
  });

  document.getElementById("btnTutupModalTl").addEventListener("click", () => modalTl.classList.add("hidden"));
  document.getElementById("btnBatalModalTl").addEventListener("click", () => modalTl.classList.add("hidden"));
  modalTl.addEventListener("click", (e) => {
    if (e.target === modalTl) modalTl.classList.add("hidden");
  });

  // Buka Pop-up Tandai Selesai
  const modalSelesai = document.getElementById("modalTandaiSelesai");
  document.getElementById("btnBukaPopupSelesai").addEventListener("click", () => {
    if (!statePanel.kodeProgresTerpilih) return;
    const lap = statePanel.semuaLaporan.find((l) => l.kode === statePanel.kodeProgresTerpilih);
    document.getElementById("labelTargetModalSelesai").textContent = lap
      ? `Laporan: ${lap.kode} — ${lap.jalan} (${lap.kecamatan})`
      : `Laporan: ${statePanel.kodeProgresTerpilih}`;
    modalSelesai.classList.remove("hidden");
  });

  document.getElementById("btnTutupModalSelesai").addEventListener("click", () => modalSelesai.classList.add("hidden"));
  document.getElementById("btnBatalModalSelesai").addEventListener("click", () => modalSelesai.classList.add("hidden"));
  modalSelesai.addEventListener("click", (e) => {
    if (e.target === modalSelesai) modalSelesai.classList.add("hidden");
  });

  // Submit Form Pop-up Catat Tindak Lanjut
  document.getElementById("formProgresTindakLanjut").addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!statePanel.kodeProgresTerpilih) {
      tampilkanAlert("Pilih laporan terlebih dahulu.", "error");
      return;
    }
    const payload = {
      kode: statePanel.kodeProgresTerpilih,
      catatan: document.getElementById("progCatatan").value,
      penanggung_jawab: document.getElementById("progPj").value,
      tanggal_rencana: formatTanggalBackend(document.getElementById("progTglRencana").value),
    };
    const res = await fetch("/api/petugas/tindak-lanjut", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok || !data.sukses) {
      tampilkanAlert(data.pesan || "Gagal mencatat tindak lanjut.", "error");
      modalTl.classList.add("hidden");
      return;
    }
    e.target.reset();
    modalTl.classList.add("hidden");
    tampilkanAlert(`Tindak lanjut ${statePanel.kodeProgresTerpilih} dicatat (Dalam Penanganan).`);
    await muatSemuaData();
  });

  // Submit Form Pop-up Tandai Selesai
  document.getElementById("formProgresSelesai").addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!statePanel.kodeProgresTerpilih) {
      tampilkanAlert("Pilih laporan terlebih dahulu.", "error");
      return;
    }
    const formData = new FormData();
    formData.append("kode", statePanel.kodeProgresTerpilih);
    formData.append(
      "tanggal_selesai",
      formatTanggalBackend(document.getElementById("progTglSelesai").value)
    );
    formData.append("foto_sesudah", document.getElementById("progFotoSesudah").files[0]);

    const res = await fetch("/api/petugas/selesai", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    if (!res.ok || !data.sukses) {
      tampilkanAlert(data.pesan || "Gagal menandai selesai.", "error");
      modalSelesai.classList.add("hidden");
      return;
    }
    e.target.reset();
    modalSelesai.classList.add("hidden");
    tampilkanAlert(`Laporan ${statePanel.kodeProgresTerpilih} berhasil ditandai Selesai.`);
    resetPilihanProgres();
    await muatSemuaData();
  });

  // Buka Pop-up Tambah Petugas Baru & isi ID otomatis
  const modalTambahPetugas = document.getElementById("modalTambahPetugas");
  document.getElementById("btnBukaPopupTambahPetugas").addEventListener("click", () => {
    sinkronInputIdPetugasOtomatis();
    modalTambahPetugas.classList.remove("hidden");
  });
  document.getElementById("btnTutupModalTambahPetugas").addEventListener("click", () => {
    modalTambahPetugas.classList.add("hidden");
  });
  modalTambahPetugas.addEventListener("click", (e) => {
    if (e.target === modalTambahPetugas) modalTambahPetugas.classList.add("hidden");
  });

  // Admin: Tambah Petugas
  document.getElementById("formTambahPetugasBaru").addEventListener("submit", async (e) => {
    e.preventDefault();
    sinkronInputIdPetugasOtomatis();
    const payload = {
      id: document.getElementById("newIdPetugas").value,
      nama: document.getElementById("newNamaPetugas").value,
      username: document.getElementById("newUserPetugas").value,
      password: document.getElementById("newPassPetugas").value,
    };
    const res = await fetch("/api/admin/pengguna", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok || !data.sukses) {
      tampilkanAlert(data.pesan || "Gagal menambah petugas.", "error");
      modalTambahPetugas.classList.add("hidden");
      return;
    }
    e.target.reset();
    modalTambahPetugas.classList.add("hidden");
    tampilkanAlert(`Petugas ${data.pengguna.nama} (${data.pengguna.id}) berhasil ditambahkan.`);
    await muatDaftarPetugas();
  });

  // Admin: Hapus Petugas Terpilih
  document.getElementById("btnHapusPetugasTerpilih").addEventListener("click", async () => {
    if (!statePanel.idPetugasTerpilih) {
      tampilkanAlert("Klik salah satu baris petugas di tabel terlebih dahulu.", "error");
      return;
    }
    const res = await fetch(
      `/api/admin/pengguna/${encodeURIComponent(statePanel.idPetugasTerpilih)}`,
      { method: "DELETE" }
    );
    const data = await res.json();
    if (!res.ok || !data.sukses) {
      tampilkanAlert(data.pesan || "Gagal menghapus petugas.", "error");
      return;
    }
    statePanel.idPetugasTerpilih = null;
    tampilkanAlert(data.pesan);
    await muatDaftarPetugas();
  });

  // Admin: Reset Password Terpilih
  const modalReset = document.getElementById("modalResetPass");
  document.getElementById("btnResetPasswordTerpilih").addEventListener("click", () => {
    if (!statePanel.idPetugasTerpilih) {
      tampilkanAlert("Klik salah satu baris petugas di tabel terlebih dahulu.", "error");
      return;
    }
    const target = statePanel.daftarPetugas.find((u) => u.id === statePanel.idPetugasTerpilih);
    document.getElementById("labelTargetReset").textContent =
      `Masukkan password baru untuk ${target?.nama || statePanel.idPetugasTerpilih} (${target?.username || ""}).`;
    modalReset.classList.remove("hidden");
  });

  document.getElementById("btnTutupModalReset").addEventListener("click", () => {
    modalReset.classList.add("hidden");
  });
  document.getElementById("btnBatalModalReset").addEventListener("click", () => {
    modalReset.classList.add("hidden");
  });
  modalReset.addEventListener("click", (e) => {
    if (e.target === modalReset) modalReset.classList.add("hidden");
  });

  document.getElementById("formKonfirmasiResetPass").addEventListener("submit", async (e) => {
    e.preventDefault();
    const passwordBaru = document.getElementById("inputPasswordBaruModal").value;
    const res = await fetch(
      `/api/admin/pengguna/${encodeURIComponent(statePanel.idPetugasTerpilih)}/reset-password`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password_baru: passwordBaru }),
      }
    );
    const data = await res.json();
    if (!res.ok || !data.sukses) {
      tampilkanAlert(data.pesan || "Gagal mereset password.", "error");
      return;
    }
    e.target.reset();
    modalReset.classList.add("hidden");
    tampilkanAlert(data.pesan);
  });

  const resSesi = await fetch("/api/sesi");
  const dataSesi = await resSesi.json();
  statePanel.pengguna = dataSesi.login ? dataSesi.pengguna : null;
  sinkronTampilanLogin();
  if (statePanel.pengguna) {
    await muatSemuaData();
  }
});