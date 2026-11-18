document.addEventListener("DOMContentLoaded", function () {
    renderDistributionChart();

    const modalHapusGuru = document.getElementById('modalHapusSemuaSiswaGuru');
    if (modalHapusGuru) {
        modalHapusGuru.addEventListener('hidden.bs.modal', function () {
            const input = document.getElementById('inputKonfirmasiHapusGuru');
            if (input) {
                input.value = '';
                validasiKetikHapusGuru();
            }
        });
    }
});

/* ================= STATUS PREDIKAT & CHIP CEPAT ================= */
const gradeMap = {
    'A':  { status: 'LULUS', isPass: true },
    'B+': { status: 'LULUS', isPass: true },
    'B':  { status: 'LULUS', isPass: true },
    'C':  { status: 'TIDAK LULUS', isPass: false }
};

function updateGradeRadioStatus(gradeVal, labelId) {
    const data = gradeMap[gradeVal] || { status: 'LULUS', isPass: true };
    const labelEl = document.getElementById(labelId);
    if (labelEl) {
        labelEl.innerHTML = data.isPass
            ? `<i class="bi bi-check-circle-fill me-1"></i> Status: ${data.status}`
            : `<i class="bi bi-exclamation-circle-fill me-1"></i> Status: ${data.status}`;
        labelEl.className = 'badge px-3 py-1 rounded-pill ' + (data.isPass ? 'bg-success text-white' : 'bg-danger text-white');
    }
}

function fillQuickInput(inputId, prefixText) {
    const el = document.getElementById(inputId);
    if (!el) return;
    el.value = prefixText;
    el.focus();
}

function appendQuickNote(textareaId, noteText) {
    const el = document.getElementById(textareaId);
    if (!el) return;
    const current = el.value.trim();
    if (!current) {
        el.value = noteText;
    } else if (!current.includes(noteText)) {
        el.value = current + ' ' + noteText;
    }
    el.focus();
}

/* ================= PENCARIAN & FILTER TABEL MURID ================= */
function filterTabelRealtime() {
    const query = document.getElementById('liveSearchInput').value.toLowerCase().trim();
    const clearBtn = document.getElementById('clearSearchBtn');
    if (clearBtn) clearBtn.classList.toggle('d-none', query === '');

    const rows = document.querySelectorAll('.siswa-row');
    let visibleCount = 0;

    rows.forEach(row => {
        const nama = row.getAttribute('data-nama') || '';
        const nisn = (row.getAttribute('data-id') || '').toLowerCase();
        const kelas = row.getAttribute('data-kelas') || '';

        const matchQuery = nama.includes(query) || nisn.includes(query) || kelas.includes(query);
        row.style.display = matchQuery ? '' : 'none';
        if (matchQuery) visibleCount++;
    });

    const noMatch = document.getElementById('noMatchMuridAlert');
    if (noMatch) {
        noMatch.classList.toggle('d-none', visibleCount > 0 || rows.length === 0);
    }
}

function clearLiveSearch() {
    const input = document.getElementById('liveSearchInput');
    if (!input) return;
    input.value = '';
    filterTabelRealtime();
    input.focus();
}

function applyFilterKelas(kelas) {
    const url = new URL(window.location.href);
    url.searchParams.set('kelas_filter', kelas);
    window.location.href = url.toString();
}

function applyFilterStatus(status) {
    const url = new URL(window.location.href);
    url.searchParams.set('status_filter', status);
    window.location.href = url.toString();
}

/* ================= KONFIRMASI HAPUS MURID ================= */
function confirmHapusSiswa(btnOrId, namaArg) {
    const id = (typeof btnOrId === 'object' && btnOrId !== null) ? btnOrId.getAttribute('data-id') : btnOrId;
    const nama = (typeof btnOrId === 'object' && btnOrId !== null) ? btnOrId.getAttribute('data-nama') : namaArg;

    if (typeof showCustomConfirm === 'function') {
        showCustomConfirm({
            title: 'Hapus Data Murid?',
            message: `Apakah Anda yakin ingin menghapus data murid <strong>${nama}</strong> beserta seluruh riwayat setorannya?`,
            confirmText: 'Ya, Hapus Permanen',
            cancelText: 'Batal',
            type: 'danger',
            onConfirm: () => {
                window.location.href = `/hapus_siswa/${id}`;
            }
        });
    } else if (confirm(`Apakah Anda yakin ingin menghapus data murid ${nama}?`)) {
        window.location.href = `/hapus_siswa/${id}`;
    }
}

function validasiKetikHapusGuru() {
    const input = document.getElementById('inputKonfirmasiHapusGuru');
    const badge = document.getElementById('badgeKunciHapusGuru');
    const btn = document.getElementById('btnEksekusiHapusGuru');
    if (!input || !btn) return;

    const isUnlocked = input.value.trim().toUpperCase() === 'HAPUS';
    btn.disabled = !isUnlocked;

    if (badge) {
        badge.className = isUnlocked
            ? 'badge bg-success bg-opacity-10 text-success border border-success border-opacity-25 rounded-pill px-2.5 py-1'
            : 'badge bg-danger bg-opacity-10 text-danger border border-danger border-opacity-25 rounded-pill px-2.5 py-1';
        badge.innerHTML = isUnlocked
            ? '<i class="bi bi-unlock-fill me-1"></i> Siap Eksekusi'
            : '<i class="bi bi-lock-fill me-1"></i> Terkunci';
    }
}

function syncKonfirmasiHapusGuru(formEl) {
    const input = document.getElementById('inputKonfirmasiHapusGuru');
    const val = (input?.value || '').trim().toUpperCase();
    if (val !== 'HAPUS') {
        input?.focus();
        return false;
    }
    input.value = val;
    return true;
}

/* ================= GRAFIK DISTRIBUSI PREDIKAT ================= */
function renderDistributionChart() {
    const chartEl = document.getElementById('chartDistribution');
    if (!chartEl || typeof ApexCharts === 'undefined') return;

    const distData = [
        Number(chartEl.dataset.a || 0),
        Number(chartEl.dataset.bplus || 0),
        Number(chartEl.dataset.b || 0),
        Number(chartEl.dataset.c || 0)
    ];

    const totalMurid = distData.reduce((a, b) => a + b, 0);

    const options = {
        series: [{
            name: 'Jumlah Murid',
            data: distData
        }],
        chart: {
            type: 'bar',
            height: 250,
            toolbar: { show: false },
            fontFamily: 'Plus Jakarta Sans, sans-serif'
        },
        plotOptions: {
            bar: {
                borderRadius: 8,
                distributed: true,
                columnWidth: '50%',
                dataLabels: { position: 'top' }
            }
        },
        colors: ['#059669', '#10b981', '#0284c7', '#ef4444'],
        dataLabels: {
            enabled: true,
            offsetY: -20,
            style: { fontSize: '12px', colors: ["#304758"] }
        },
        xaxis: {
            categories: ['Grade A (Lulus)', 'Grade B+ (Lulus)', 'Grade B (Lulus)', 'Grade C (Perlu Bimbingan)'],
            labels: { style: { fontSize: '11px', fontWeight: 600 } }
        },
        yaxis: {
            title: { text: 'Jumlah Murid' },
            labels: { formatter: (val) => Math.floor(val) }
        },
        legend: { show: false },
        tooltip: {
            y: {
                formatter: function (val) {
                    const pct = totalMurid > 0 ? Math.round((val / totalMurid) * 100) : 0;
                    return `${val} Murid (${pct}%)`;
                }
            }
        }
    };

    const chart = new ApexCharts(chartEl, options);
    chart.render();
}