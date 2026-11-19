document.addEventListener("DOMContentLoaded", function () {
    const resetModal = document.getElementById('modalResetDataAdmin');
    if (resetModal) {
        resetModal.addEventListener('hidden.bs.modal', function () {
            const input = document.getElementById('inputKonfirmasiHapus');
            if (input) {
                input.value = '';
                validasiKetikHapus();
            }
        });
    }
});

/* ================= PILIH KELAS GURU ================= */
function toggleClassInInput(inputId, classCode, btnElement) {
    const input = document.getElementById(inputId);
    if (!input) return;

    const curVal = input.value.trim();
    const classes = curVal ? curVal.split(',').map(c => c.trim().toUpperCase()).filter(c => c && c !== '-') : [];

    const idx = classes.indexOf(classCode);
    if (idx > -1) {
        classes.splice(idx, 1);
        if (btnElement) btnElement.classList.remove('selected');
    } else {
        classes.push(classCode);
        if (btnElement) btnElement.classList.add('selected');
    }

    input.value = classes.join(', ');
}

/* ================= FILTER TABEL GURU ================= */
let activeGuruStatusFilter = 'all';

function filterTabelGuru() {
    const query = document.getElementById('searchGuruInput').value.toLowerCase().trim();
    document.getElementById('clearSearchGuruBtn').classList.toggle('d-none', query === '');

    const rows = document.querySelectorAll('.guru-row');
    let visibleCount = 0;

    rows.forEach(row => {
        const nama = row.getAttribute('data-nama') || '';
        const username = row.getAttribute('data-username') || '';
        const kelas = row.getAttribute('data-kelas') || '';
        const rowStatus = row.getAttribute('data-status');

        const matchQuery = nama.includes(query) || username.includes(query) || kelas.includes(query);
        const matchStatus = activeGuruStatusFilter === 'all' || rowStatus === activeGuruStatusFilter;

        const visible = matchQuery && matchStatus;
        row.style.display = visible ? '' : 'none';
        if (visible) visibleCount++;
    });

    const noMatch = document.getElementById('noMatchGuruAlert');
    if (noMatch) noMatch.classList.toggle('d-none', visibleCount > 0 || rows.length === 0);
}

function clearSearchGuru() {
    const input = document.getElementById('searchGuruInput');
    input.value = '';
    filterTabelGuru();
    input.focus();
}

function setFilterGuruStatus(status, btnElement) {
    btnElement.parentElement?.querySelectorAll('.filter-pill').forEach(btn => btn.classList.remove('active'));
    btnElement?.classList.add('active');
    activeGuruStatusFilter = status;
    filterTabelGuru();
}

/* ================= FILTER TABEL MURID ================= */
let activeSiswaStatusFilter = 'all';
let activeSiswaLulusFilter = 'all';

function filterTabelSiswaAdmin() {
    const query = document.getElementById('searchSiswaInput').value.toLowerCase().trim();
    const selectedKelas = document.getElementById('filterKelasSiswaSelect').value;
    document.getElementById('clearSearchSiswaBtn').classList.toggle('d-none', query === '');

    const rows = document.querySelectorAll('.siswa-admin-row');
    let visibleCount = 0;

    rows.forEach(row => {
        const nama = row.getAttribute('data-nama') || '';
        const nisn = (row.getAttribute('data-id') || '').toLowerCase();
        const username = row.getAttribute('data-username') || '';
        const kelas = row.getAttribute('data-kelas') || '';
        const rowStatus = row.getAttribute('data-status');
        const rowLulus = row.getAttribute('data-lulus');

        const matchQuery = nama.includes(query) || nisn.includes(query) || username.includes(query) || kelas.includes(query);
        const matchKelas = selectedKelas === 'all' || kelas === selectedKelas;
        const matchStatus = activeSiswaStatusFilter === 'all' || rowStatus === activeSiswaStatusFilter;
        const matchLulus = activeSiswaLulusFilter === 'all' || rowLulus === activeSiswaLulusFilter;

        const visible = matchQuery && matchKelas && matchStatus && matchLulus;
        row.style.display = visible ? '' : 'none';
        if (visible) visibleCount++;
    });

    const noMatch = document.getElementById('noMatchSiswaAlert');
    if (noMatch) noMatch.classList.toggle('d-none', visibleCount > 0 || rows.length === 0);
}

function clearSearchSiswaAdmin() {
    const input = document.getElementById('searchSiswaInput');
    input.value = '';
    filterTabelSiswaAdmin();
    input.focus();
}

function setFilterSiswaStatus(status, btnElement) {
    btnElement.parentElement?.querySelectorAll('.filter-pill').forEach(btn => btn.classList.remove('active'));
    btnElement?.classList.add('active');
    activeSiswaStatusFilter = status;
    filterTabelSiswaAdmin();
}

function setFilterSiswaLulus(lulusStatus, btnElement) {
    btnElement.parentElement?.querySelectorAll('.filter-pill').forEach(btn => btn.classList.remove('active'));
    btnElement?.classList.add('active');
    activeSiswaLulusFilter = lulusStatus;
    filterTabelSiswaAdmin();
}

/* ================= KONFIRMASI RESET MASSAL ================= */
function validasiKetikHapus() {
    const input = document.getElementById('inputKonfirmasiHapus');
    const badge = document.getElementById('badgeStatusKunciHapus');
    const btns = document.querySelectorAll('.btn-eksekusi-hapus');
    if (!input) return;

    const isUnlocked = input.value.trim().toUpperCase() === 'HAPUS';
    btns.forEach(btn => { btn.disabled = !isUnlocked; });

    if (badge) {
        badge.className = isUnlocked
            ? 'badge bg-success bg-opacity-10 text-success border border-success border-opacity-25 rounded-pill px-2.5 py-1'
            : 'badge bg-danger bg-opacity-10 text-danger border border-danger border-opacity-25 rounded-pill px-2.5 py-1';
        badge.innerHTML = isUnlocked
            ? '<i class="bi bi-unlock-fill me-1"></i> Siap Eksekusi'
            : '<i class="bi bi-lock-fill me-1"></i> Terkunci';
    }
}

function syncKonfirmasiHapus(formEl) {
    const input = document.getElementById('inputKonfirmasiHapus');
    const val = (input?.value || '').trim().toUpperCase();
    if (val !== 'HAPUS') {
        input?.focus();
        return false;
    }
    const hiddenInput = formEl.querySelector('input[name="konfirmasi"]');
    if (hiddenInput) hiddenInput.value = val;
    return true;
}