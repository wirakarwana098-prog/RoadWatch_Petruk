const state = {
  daftarLaporan: [],
};

function escapeHtml(teks) {
  return String(teks ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function classBadgeTingkat(tingkat) {
  const t = String(tingkat).toLowerCase();
  if (t === "berat") return "badge badge-berat";
  if (t === "sedang") return "badge badge-sedang";
  return "badge badge-ringan";
}

function classBadgeStatus(status) {
  const s = String(status).toLowerCase();
  if (s === "baru") return "badge badge-baru";
  if (s === "terverifikasi") return "badge badge-terverifikasi";
  if (s === "dalam penanganan") return "badge badge-penanganan";
  if (s === "selesai") return "badge badge-selesai";
  return "badge badge-ditolak";
}

function tampilkanAlert(el, pesan, tipe = "success", kodeSalin = null) {
  el.className = `alert-box ${tipe === "success" ? "alert-success" : "alert-error"}`;
  el.innerHTML = `<div>${escapeHtml(pesan)}</div>`;
  if (kodeSalin) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "copy-code-btn";
    btn.textContent = `Salin Kode ${kodeSalin}`;
    btn.addEventListener("click", () => {
      navigator.clipboard?.writeText(kodeSalin);
      btn.textContent = `Tersalin (${kodeSalin})`;
    });
    el.appendChild(btn);
  }
  el.classList.remove("hidden");
}

async function muatStatistik() {
  try {
    const res = await fetch("/api/statistik");
    const data = await res.json();
    document.getElementById("statTotal").textContent = data.total ?? 0;
    document.getElementById("statPenanganan").textContent =
      data.rekap_status?.["Dalam Penanganan"] ?? 0;
    document.getElementById("statPersentase").textContent = `${data.persentase_selesai ?? 0}%`;
    document.getElementById("statPelapor").textContent = data.total_pelapor ?? 0;
  } catch (err) {
    console.error("Gagal memuat statistik:", err);
  }
}

function perbaruiHeroCard(laporanTeratas) {
  if (!laporanTeratas) return;
  document.getElementById("heroTopJalan").textContent = laporanTeratas.jalan;
  document.getElementById("heroTopKecamatan").textContent =
    `Kecamatan ${laporanTeratas.kecamatan} • Bandar Lampung`;
  document.getElementById("heroTopSkor").textContent = laporanTeratas.skor;
  document.getElementById("heroTopStatus").textContent = `/ ${laporanTeratas.status}`;
  document.getElementById("heroTopKode").textContent = laporanTeratas.kode;

  const tingkat = String(laporanTeratas.tingkat).toLowerCase();
  document.getElementById("heroPillRingan").classList.toggle("active", tingkat === "ringan");
  document.getElementById("heroPillSedang").classList.toggle("active", tingkat === "sedang");
  document.getElementById("heroPillBerat").classList.toggle("active", tingkat === "berat");

  const lebar = tingkat === "berat" ? "92%" : tingkat === "sedang" ? "62%" : "34%";
  document.getElementById("heroProgressBar").style.width = lebar;
}

async function muatDaftarPrioritas() {
  const status = document.getElementById("filterStatus").value;
  const kecamatan = document.getElementById("filterKecamatan").value;
  const tingkat = document.getElementById("filterTingkat").value;
  const metode = document.getElementById("selectMetodeSort")?.value || "selection";

  const params = new URLSearchParams();
  if (status) params.set("status", status);
  if (kecamatan) params.set("kecamatan", kecamatan);
  if (tingkat) params.set("tingkat", tingkat);
  if (metode) params.set("metode", metode);

  try {
    const res = await fetch(`/api/laporan?${params.toString()}`);
    const data = await res.json();
    const daftar = data.laporan || [];

    if (!status && !kecamatan && !tingkat && metode === "selection") {
      state.daftarLaporan = daftar;
      if (daftar.length > 0) {
        perbaruiHeroCard(daftar[0]);
      }
    }

    renderTabelPrioritas(daftar);
  } catch (err) {
    console.error("Gagal memuat daftar laporan:", err);
  }
}

function renderTabelPrioritas(daftar) {
  const tbody = document.getElementById("tbodyPrioritas");
  if (!daftar.length) {
    tbody.innerHTML = `<tr><td colspan="8" class="empty-cell">Belum ada laporan yang sesuai filter.</td></tr>`;
    return;
  }

  tbody.innerHTML = daftar
    .map((item, idx) => {
      const rank = String(idx + 1).padStart(2, "0");
      return `
        <tr>
          <td class="rank-num">${rank}</td>
          <td><span class="code-chip">${escapeHtml(item.kode)}</span></td>
          <td>
            <div class="road-title">${escapeHtml(item.jalan)}</div>
            <div class="road-sub">${escapeHtml(item.kecamatan)} • ${escapeHtml(item.tanggal)}</div>
          </td>
          <td><span class="${classBadgeTingkat(item.tingkat)}">${escapeHtml(item.tingkat)}</span></td>
          <td>${escapeHtml(item.jumlah_pelapor)} orang</td>
          <td><span class="score-pill">${escapeHtml(item.skor)}</span></td>
          <td><span class="${classBadgeStatus(item.status)}">${escapeHtml(item.status)}</span></td>
          <td>
            <button type="button" class="btn-table-action" data-lacak="${escapeHtml(item.kode)}">
              Detail
            </button>
          </td>
        </tr>
      `;
    })
    .join("");

  tbody.querySelectorAll("[data-lacak]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const kode = btn.getAttribute("data-lacak");
      document.getElementById("inputCariKode").value = kode;
      document.getElementById("cek-laporan").scrollIntoView({ behavior: "smooth" });
      lacakKodeLaporan(kode);
    });
  });
}

async function lacakKodeLaporan(kodeInput) {
  const kode = kodeInput.trim();
  if (!kode) return;

  const pakaiBinary = document.getElementById("checkBinarySearch").checked;
  const box = document.getElementById("hasilLacak");

  try {
    const res = await fetch(
      `/api/laporan/${encodeURIComponent(kode)}?binary=${pakaiBinary ? "true" : "false"}`
    );
    const data = await res.json();

    if (!res.ok || !data.sukses) {
      box.innerHTML = `<div class="alert-box alert-error">${escapeHtml(data.pesan || "Laporan tidak ditemukan.")}</div>`;
      box.classList.remove("hidden");
      return;
    }

    const lap = data.laporan;
    const riwayat = data.riwayat || [];

    const riwayatHtml = riwayat.length
      ? `<div class="timeline-list">
          ${riwayat
            .map(
              (r) => `
              <div class="timeline-item">
                <strong>Penanggung Jawab:</strong> ${escapeHtml(r.penanggung_jawab)}<br>
                <strong>Catatan:</strong> ${escapeHtml(r.catatan)}<br>
                <strong>Rencana:</strong> ${escapeHtml(r.tanggal_rencana)} •
                <strong>Selesai:</strong> ${escapeHtml(r.tanggal_selesai)} •
                <strong>Foto Sesudah:</strong> ${escapeHtml(r.foto_sesudah)}
              </div>
            `
            )
            .join("")}
        </div>`
      : `<p class="road-sub" style="margin-top:12px;">Belum ada catatan tindak lanjut lapangan untuk laporan ini.</p>`;

    box.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">
        <div>
          <span class="code-chip">${escapeHtml(lap.kode)}</span>
          <span class="road-sub" style="margin-left:8px;">Ditemukan via ${escapeHtml(data.algoritma)}</span>
        </div>
        <span class="${classBadgeStatus(lap.status)}">${escapeHtml(lap.status)}</span>
      </div>

      <div class="detail-grid">
        <div class="detail-box">
          <span>Lokasi Jalan</span>
          <strong>${escapeHtml(lap.jalan)}</strong>
        </div>
        <div class="detail-box">
          <span>Kecamatan</span>
          <strong>${escapeHtml(lap.kecamatan)}</strong>
        </div>
        <div class="detail-box">
          <span>Tingkat & Jumlah Pelapor</span>
          <strong>${escapeHtml(lap.tingkat)} (${escapeHtml(lap.jumlah_pelapor)} pelapor)</strong>
        </div>
        <div class="detail-box">
          <span>Skor Prioritas & Tanggal</span>
          <strong>Skor ${escapeHtml(lap.skor)} • ${escapeHtml(lap.tanggal)}</strong>
        </div>
      </div>

      <h4 style="font-size:0.92rem;margin-top:12px;">Riwayat Tindak Lanjut Dinas</h4>
      ${riwayatHtml}
    `;
    box.classList.remove("hidden");
  } catch (err) {
    box.innerHTML = `<div class="alert-box alert-error">Terjadi kesalahan koneksi saat melacak kode.</div>`;
    box.classList.remove("hidden");
  }
}

function initFormLaporan() {
  const inputFoto = document.getElementById("inputFoto");
  const placeholder = document.getElementById("fileDropPlaceholder");
  const previewBox = document.getElementById("filePreviewBox");
  const previewImg = document.getElementById("previewImg");
  const previewName = document.getElementById("previewFileName");

  inputFoto.addEventListener("change", () => {
    const file = inputFoto.files?.[0];
    if (!file) {
      placeholder.classList.remove("hidden");
      previewBox.classList.add("hidden");
      return;
    }
    previewName.textContent = file.name;
    previewImg.src = URL.createObjectURL(file);
    placeholder.classList.add("hidden");
    previewBox.classList.remove("hidden");
  });

  const form = document.getElementById("formLaporan");
  const alertEl = document.getElementById("alertFormLaporan");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(form);

    try {
      const res = await fetch("/api/laporan", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();

      if (!res.ok || !data.sukses) {
        tampilkanAlert(alertEl, data.pesan || "Gagal mengirim laporan.", "error");
        return;
      }

      tampilkanAlert(alertEl, data.pesan, "success", data.kode);
      form.reset();
      placeholder.classList.remove("hidden");
      previewBox.classList.add("hidden");

      await Promise.all([muatStatistik(), muatDaftarPrioritas()]);
    } catch (err) {
      tampilkanAlert(alertEl, "Gagal terhubung ke server.", "error");
    }
  });
}

async function sinkronLabelSesiNavbar() {
  try {
    const res = await fetch("/api/sesi");
    const data = await res.json();
    const labelBtn = document.getElementById("labelAksesPetugas");
    if (data.login && data.pengguna) {
      labelBtn.textContent = `Panel ${data.pengguna.nama.split(" ")[0]}`;
    } else {
      labelBtn.textContent = "Akses Petugas";
    }
  } catch (err) {
    console.error("Gagal cek sesi:", err);
  }
}

function initNavScrollSpy() {
  const navLinks = Array.from(document.querySelectorAll('.nav-links a[href^="#"]'));
  if (!navLinks.length) return;

  const sections = navLinks
    .map((link) => {
      const targetId = link.getAttribute("href");
      const section = targetId ? document.querySelector(targetId) : null;
      return section ? { link, section } : null;
    })
    .filter(Boolean);

  function setActiveLink(activeLink) {
    navLinks.forEach((link) => {
      link.classList.toggle("active", link === activeLink);
    });
  }

  function updateActiveOnScroll() {
    const navbar = document.querySelector(".navbar");
    const navHeight = navbar ? navbar.offsetHeight : 80;
    const triggerLine = window.scrollY + navHeight + 140;

    if (sections.length && triggerLine < sections[0].section.offsetTop) {
      setActiveLink(null);
      return;
    }

    const nearBottom =
      window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 16;
    if (nearBottom && sections.length) {
      setActiveLink(sections[sections.length - 1].link);
      return;
    }

    let current = null;
    for (const item of sections) {
      if (item.section.offsetTop <= triggerLine) {
        current = item.link;
      }
    }
    setActiveLink(current);
  }

  navLinks.forEach((link) => {
    link.addEventListener("click", () => {
      setActiveLink(link);
    });
  });

  window.addEventListener("scroll", updateActiveOnScroll, { passive: true });
  updateActiveOnScroll();
}

document.addEventListener("DOMContentLoaded", async () => {
  initNavScrollSpy();
  initFormLaporan();

  ["filterStatus", "filterKecamatan", "filterTingkat", "selectMetodeSort"].forEach((id) => {
    document.getElementById(id)?.addEventListener("change", muatDaftarPrioritas);
  });

  document.getElementById("formCekKode").addEventListener("submit", (e) => {
    e.preventDefault();
    lacakKodeLaporan(document.getElementById("inputCariKode").value);
  });

  await Promise.all([muatStatistik(), muatDaftarPrioritas(), sinkronLabelSesiNavbar()]);
});