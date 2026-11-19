/* ================= DATA MASTER JILID UMMI, 40 HALAMAN, 30 JUZ & 114 SURAH ================= */
const DAFTAR_JILID_UMMI = [
    { value: "Ummi Jilid 1", label: "Ummi Jilid 1", tag: "Pemula", searchKey: "1 ummi jilid 1 pemula" },
    { value: "Ummi Jilid 2", label: "Ummi Jilid 2", tag: "Harokat", searchKey: "2 ummi jilid 2 harokat" },
    { value: "Ummi Jilid 3", label: "Ummi Jilid 3", tag: "Mad", searchKey: "3 ummi jilid 3 mad" },
    { value: "Ummi Jilid 4", label: "Ummi Jilid 4", tag: "Tasydid", searchKey: "4 ummi jilid 4 tasydid" },
    { value: "Ummi Jilid 5", label: "Ummi Jilid 5", tag: "Waqaf", searchKey: "5 ummi jilid 5 waqaf ghunnah" },
    { value: "Ummi Jilid 6", label: "Ummi Jilid 6", tag: "Qalqalah", searchKey: "6 ummi jilid 6 qalqalah idgham" },
    { value: "Gharib & Tajwid", label: "Gharib & Tajwid", tag: "Khusus", searchKey: "gharib tajwid khusus" },
    { value: "Al-Qur'an", label: "Al-Qur'an", tag: "Tadarus", searchKey: "alquran al-qur'an tadarus" }
];

const DAFTAR_HALAMAN_UMMI = (() => {
    const items = [];
    for (let i = 1; i <= 40; i++) {
        items.push({
            value: i === 40 ? "Hal. 40 (Khatam Jilid)" : `Hal. ${i}`,
            label: i === 40 ? "Hal. 40 (Khatam Jilid)" : `Hal. ${i}`,
            tag: i === 40 ? "Khatam" : `No. ${i}`,
            searchKey: `${i} hal ${i} halaman ${i} ${i === 40 ? "khatam" : ""}`
        });
    }
    items.push({
        value: "Ujian Kenaikan Jilid",
        label: "Ujian Kenaikan Jilid",
        tag: "Munaqasyah",
        searchKey: "ujian kenaikan jilid munaqasyah"
    });
    return items;
})();

const DAFTAR_30_JUZ = (() => {
    const ketJuz = {
        30: "Juz 'Amma",
        29: "Tabarak",
        28: "Qad Sami'allah",
        1: "Alif Lam Mim"
    };
    const items = [];
    for (let j = 30; j >= 1; j--) {
        items.push({
            value: `Juz ${j}`,
            label: `Juz ${j}`,
            tag: ketJuz[j] || `Juz ke-${j}`,
            searchKey: `${j} juz ${j} juz${j} ${(ketJuz[j] || "").toLowerCase()}`
        });
    }
    items.push({
        value: "Semua Juz (1–30)",
        label: "Semua Juz (1–30)",
        tag: "114 Surah",
        searchKey: "semua juz 1-30 all 114 surah"
    });
    return items;
})();

const DAFTAR_114_SURAH = [
    [1, "Al-Fatihah", 7, [1]], [2, "Al-Baqarah", 286, [1, 2, 3]], [3, "Ali 'Imran", 200, [3, 4]],
    [4, "An-Nisa'", 176, [4, 5, 6]], [5, "Al-Ma'idah", 120, [6, 7]], [6, "Al-An'am", 165, [7, 8]],
    [7, "Al-A'raf", 206, [8, 9]], [8, "Al-Anfal", 75, [9, 10]], [9, "At-Taubah", 129, [10, 11]],
    [10, "Yunus", 109, [11]], [11, "Hud", 123, [11, 12]], [12, "Yusuf", 111, [12, 13]],
    [13, "Ar-Ra'd", 43, [13]], [14, "Ibrahim", 52, [13]], [15, "Al-Hijr", 99, [14]],
    [16, "An-Nahl", 128, [14]], [17, "Al-Isra'", 111, [15]], [18, "Al-Kahf", 110, [15, 16]],
    [19, "Maryam", 98, [16]], [20, "Taha", 135, [16]], [21, "Al-Anbiya'", 112, [17]],
    [22, "Al-Hajj", 78, [17]], [23, "Al-Mu'minun", 118, [18]], [24, "An-Nur", 64, [18]],
    [25, "Al-Furqan", 77, [18, 19]], [26, "Asy-Syu'ara'", 227, [19]], [27, "An-Naml", 93, [19, 20]],
    [28, "Al-Qasas", 88, [20]], [29, "Al-'Ankabut", 69, [20, 21]], [30, "Ar-Rum", 60, [21]],
    [31, "Luqman", 34, [21]], [32, "As-Sajdah", 30, [21]], [33, "Al-Ahzab", 73, [21, 22]],
    [34, "Saba'", 54, [22]], [35, "Fatir", 45, [22]], [36, "Yasin", 83, [22, 23]],
    [37, "As-Saffat", 182, [23]], [38, "Sad", 88, [23]], [39, "Az-Zumar", 75, [23, 24]],
    [40, "Ghafir", 85, [24]], [41, "Fussilat", 54, [24, 25]], [42, "Asy-Syura", 53, [25]],
    [43, "Az-Zukhruf", 89, [25]], [44, "Ad-Dukhan", 59, [25]], [45, "Al-Jasiyah", 37, [25]],
    [46, "Al-Ahqaf", 35, [26]], [47, "Muhammad", 38, [26]], [48, "Al-Fath", 29, [26]],
    [49, "Al-Hujurat", 18, [26]], [50, "Qaf", 45, [26]], [51, "Az-Zariyat", 60, [26, 27]],
    [52, "At-Tur", 49, [27]], [53, "An-Najm", 62, [27]], [54, "Al-Qamar", 55, [27]],
    [55, "Ar-Rahman", 78, [27]], [56, "Al-Waqi'ah", 96, [27]], [57, "Al-Hadid", 29, [27]],
    [58, "Al-Mujadilah", 22, [28]], [59, "Al-Hasyr", 24, [28]], [60, "Al-Mumtahanah", 13, [28]],
    [61, "As-Saff", 14, [28]], [62, "Al-Jumu'ah", 11, [28]], [63, "Al-Munafiqun", 11, [28]],
    [64, "At-Taghabun", 18, [28]], [65, "At-Talaq", 12, [28]], [66, "At-Tahrim", 12, [28]],
    [67, "Al-Mulk", 30, [29]], [68, "Al-Qalam", 52, [29]], [69, "Al-Haqqah", 52, [29]],
    [70, "Al-Ma'arij", 44, [29]], [71, "Nuh", 28, [29]], [72, "Al-Jinn", 28, [29]],
    [73, "Al-Muzzammil", 20, [29]], [74, "Al-Muddassir", 56, [29]], [75, "Al-Qiyamah", 40, [29]],
    [76, "Al-Insan", 31, [29]], [77, "Al-Mursalat", 50, [29]], [78, "An-Naba'", 40, [30]],
    [79, "An-Nazi'at", 46, [30]], [80, "'Abasa", 42, [30]], [81, "At-Takwir", 29, [30]],
    [82, "Al-Infitar", 19, [30]], [83, "Al-Mutaffifin", 36, [30]], [84, "Al-Insyiqaq", 25, [30]],
    [85, "Al-Buruj", 22, [30]], [86, "At-Tariq", 17, [30]], [87, "Al-A'la", 19, [30]],
    [88, "Al-Ghasyiyah", 26, [30]], [89, "Al-Fajr", 30, [30]], [90, "Al-Balad", 20, [30]],
    [91, "Asy-Syams", 15, [30]], [92, "Al-Lail", 21, [30]], [93, "Ad-Duha", 11, [30]],
    [94, "Al-Insyirah", 8, [30]], [95, "At-Tin", 8, [30]], [96, "Al-'Alaq", 19, [30]],
    [97, "Al-Qadr", 5, [30]], [98, "Al-Bayyinah", 8, [30]], [99, "Az-Zalzalah", 8, [30]],
    [100, "Al-'Adiyat", 11, [30]], [101, "Al-Qari'ah", 11, [30]], [102, "At-Takatsur", 8, [30]],
    [103, "Al-'Asr", 3, [30]], [104, "Al-Humazah", 9, [30]], [105, "Al-Fil", 5, [30]],
    [106, "Quraisy", 4, [30]], [107, "Al-Ma'un", 7, [30]], [108, "Al-Kautsar", 3, [30]],
    [109, "Al-Kafirun", 6, [30]], [110, "An-Nasr", 3, [30]], [111, "Al-Lahab", 5, [30]],
    [112, "Al-Ikhlas", 4, [30]], [113, "Al-Falaq", 5, [30]], [114, "An-Nas", 6, [30]]
];

const DAFTAR_CATATAN_TAHSIN = [
    { value: "Fasih, tartil & makharijul huruf tepat (Lanjut halaman berikutnya).", label: "Fasih, tartil & makharijul huruf tepat (Lanjut)", tag: "Lulus" },
    { value: "Bacaan baik, perhatikan panjang pendek (mad) & dengung (ghunnah).", label: "Perhatikan panjang pendek (mad) & ghunnah", tag: "Tajwid" },
    { value: "Perhatikan huruf tekan (tasydid) & huruf pantul (qalqalah).", label: "Perhatikan huruf tekan (tasydid) & qalqalah", tag: "Tajwid" },
    { value: "Drilling persiapan ujian kenaikan jilid / naik ke Al-Qur'an.", label: "Drilling persiapan ujian kenaikan jilid", tag: "Ujian" },
    { value: "Perlu muroja'ah di rumah minimal 3x baca ulang 1 halaman (Mengulang).", label: "Muroja'ah di rumah min. 3x baca ulang (Mengulang)", tag: "Bimbingan" }
];

const DAFTAR_CATATAN_TAHFIDZ = [
    { value: "Hafalan lancar, mutqin, dan tartil (Lanjut ayat/surah berikutnya).", label: "Hafalan lancar, mutqin, dan tartil (Lanjut)", tag: "Mutqin" },
    { value: "Hafalan cukup lancar, perhatikan kelancaran sambungan antar ayat.", label: "Perhatikan kelancaran sambungan antar ayat", tag: "Lancar" },
    { value: "Perhatikan panjang pendek (mad) dan makhraj saat menyetor hafalan.", label: "Perhatikan tajwid & makhraj saat setoran hafalan", tag: "Tajwid" },
    { value: "Perlu muroja'ah ulang di rumah bersama orang tua sebelum lanjut.", label: "Perlu muroja'ah ulang di rumah bersama orang tua", tag: "Muroja'ah" }
];

document.addEventListener("DOMContentLoaded", function () {
    renderDistributionChart();
    initSmartComboboxes();
    initMobileModalBackGuard();

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

/* ================= FIX BUG CLOSE / BACK HP LOMPAT KE LOGIN ================= */
function initMobileModalBackGuard() {
    let isClosingViaPopstate = false;

    if (!window.history.state || !window.history.state.dashboardRoot) {
        try {
            window.history.replaceState({ dashboardRoot: true }, '', window.location.href);
            window.history.pushState({ dashboardActive: true }, '', window.location.href);
        } catch (err) { /* ignore */ }
    }

    document.addEventListener('show.bs.modal', function (e) {
        const modalEl = e.target;
        if (!modalEl || !modalEl.id) return;
        try {
            window.history.pushState({ bsModalOpen: modalEl.id }, '', window.location.href);
        } catch (err) { /* ignore */ }
    });

    document.addEventListener('hidden.bs.modal', function (e) {
        closeAllSmartCombos();
        const modalEl = e.target;
        if (!isClosingViaPopstate && window.history.state && window.history.state.bsModalOpen === modalEl.id) {
            try {
                window.history.back();
            } catch (err) { /* ignore */ }
        }
        isClosingViaPopstate = false;
    });

    window.addEventListener('popstate', function () {
        const openCombos = document.querySelectorAll('.smart-combo-menu.show');
        if (openCombos.length > 0) {
            closeAllSmartCombos();
            try {
                window.history.pushState({ dashboardActive: true }, '', window.location.href);
            } catch (err) { /* ignore */ }
            return;
        }

        const openModals = document.querySelectorAll('.modal.show');
        if (openModals.length > 0 && typeof bootstrap !== 'undefined') {
            isClosingViaPopstate = true;
            const topModal = openModals[openModals.length - 1];
            const instance = bootstrap.Modal.getOrCreateInstance(topModal);
            instance.hide();
            return;
        }

        if (window.history.state && window.history.state.dashboardRoot) {
            try {
                window.history.pushState({ dashboardActive: true }, '', window.location.href);
            } catch (err) { /* ignore */ }
        }
    });
}

/* ================= SMART SEARCHABLE COMBOBOX (JILID, HALAMAN, JUZ, 114 SURAH & AYAT) ================= */
function initSmartComboboxes() {
    document.addEventListener('click', function (e) {
        // Tombol clear (X) di semua combobox
        const clearBtn = e.target.closest('.smart-combo-clear');
        if (clearBtn) {
            e.preventDefault();
            e.stopPropagation();
            const wrap = clearBtn.closest('.smart-combo-wrap');
            const input = wrap.querySelector('.smart-combo-input');
            const form = wrap.closest('form');
            const type = wrap.dataset.comboType;

            input.value = '';
            if (type === 'jilid') onTahsinJilidUpdated(form, '');
            if (type === 'juz') onTahfidzJuzUpdated(form);
            if (type === 'tahfidz') resetSurahMetadata(form);
            updateHiddenMateriValue(form);

            openSmartCombo(wrap, '');
            input.focus();
            return;
        }

        // Tombol panah buka/tutup combobox
        const toggleBtn = e.target.closest('.smart-combo-toggle');
        if (toggleBtn) {
            e.preventDefault();
            e.stopPropagation();
            const wrap = toggleBtn.closest('.smart-combo-wrap');
            const input = wrap.querySelector('.smart-combo-input');
            const menu = wrap.querySelector('.smart-combo-menu');
            const isOpen = menu.classList.contains('show');
            closeAllSmartCombos();
            if (!isOpen) {
                wrap.dataset.forceAll = '0';
                openSmartCombo(wrap, '');
                input.focus();
            }
            return;
        }

        // Tombol "Semua 114" di header daftar surah
        const showAllBtn = e.target.closest('[data-combo-show-all]');
        if (showAllBtn) {
            e.preventDefault();
            e.stopPropagation();
            const wrap = showAllBtn.closest('.smart-combo-wrap');
            wrap.dataset.forceAll = '1';
            renderSmartComboMenu(wrap, '');
            return;
        }

        // Klik salah satu item pilihan
        const optionItem = e.target.closest('.smart-combo-item');
        if (optionItem) {
            e.preventDefault();
            e.stopPropagation();
            const wrap = optionItem.closest('.smart-combo-wrap');
            const input = wrap.querySelector('.smart-combo-input');
            const type = wrap.dataset.comboType;
            const form = wrap.closest('form');

            input.value = optionItem.dataset.value || '';

            if (type === 'jilid') {
                onTahsinJilidUpdated(form, input.value);
            } else if (type === 'juz') {
                onTahfidzJuzUpdated(form);
            } else if (type === 'tahfidz') {
                const surahNo = parseInt(optionItem.dataset.no || '0', 10);
                const found = DAFTAR_114_SURAH.find(s => s[0] === surahNo);
                if (found) {
                    applySurahMetadata(form, found, true);
                }
            }

            updateHiddenMateriValue(form);
            closeAllSmartCombos();
            return;
        }

        if (!e.target.closest('.smart-combo-wrap')) {
            closeAllSmartCombos();
        }
    });

    document.addEventListener('focusin', function (e) {
        const input = e.target.closest('.smart-combo-input');
        if (!input) return;
        const wrap = input.closest('.smart-combo-wrap');
        closeAllSmartCombos(wrap);
        wrap.dataset.forceAll = '0';
        openSmartCombo(wrap, '');
    });

    document.addEventListener('input', function (e) {
        const input = e.target.closest('.smart-combo-input');
        if (!input) return;
        const wrap = input.closest('.smart-combo-wrap');
        const type = wrap.dataset.comboType;
        const form = wrap.closest('form');

        openSmartCombo(wrap, input.value);

        if (type === 'jilid') {
            onTahsinJilidUpdated(form, input.value);
        } else if (type === 'tahfidz') {
            syncSurahMetadataFromText(form, input.value);
        }

        updateHiddenMateriValue(form);
    });

    document.addEventListener('keydown', function (e) {
        const input = e.target.closest('.smart-combo-input');
        if (!input) return;
        const wrap = input.closest('.smart-combo-wrap');
        const menu = wrap.querySelector('.smart-combo-menu');
        if (!menu || !menu.classList.contains('show')) return;

        const items = Array.from(menu.querySelectorAll('.smart-combo-item'));
        let activeIdx = items.findIndex(el => el.classList.contains('active'));

        if (e.key === 'Escape') {
            e.preventDefault();
            e.stopPropagation();
            closeAllSmartCombos();
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (!items.length) return;
            if (activeIdx >= 0) items[activeIdx].classList.remove('active');
            const nextIdx = (activeIdx + 1) % items.length;
            items[nextIdx].classList.add('active');
            items[nextIdx].scrollIntoView({ block: 'nearest' });
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (!items.length) return;
            if (activeIdx >= 0) items[activeIdx].classList.remove('active');
            const prevIdx = activeIdx <= 0 ? items.length - 1 : activeIdx - 1;
            items[prevIdx].classList.add('active');
            items[prevIdx].scrollIntoView({ block: 'nearest' });
        } else if (e.key === 'Enter' && activeIdx >= 0) {
            e.preventDefault();
            items[activeIdx].click();
        }
    });
}

function openSmartCombo(wrap, keyword) {
    const menu = wrap.querySelector('.smart-combo-menu');
    renderSmartComboMenu(wrap, keyword);
    menu.classList.remove('drop-up');
    menu.classList.add('show');

    const rect = wrap.getBoundingClientRect();
    const spaceBelow = window.innerHeight - rect.bottom;
    const spaceAbove = rect.top;
    if (spaceBelow < 200 && spaceAbove > spaceBelow) {
        menu.classList.add('drop-up');
    }
}

function closeAllSmartCombos(exceptWrap = null) {
    document.querySelectorAll('.smart-combo-menu.show').forEach(menu => {
        if (exceptWrap && exceptWrap.contains(menu)) return;
        menu.classList.remove('show', 'drop-up');
    });
}

function renderSmartComboMenu(wrap, keyword) {
    const menu = wrap.querySelector('.smart-combo-menu');
    const type = wrap.dataset.comboType;
    const q = String(keyword || '').toLowerCase().trim();

    if (type === 'jilid') {
        const list = q
            ? DAFTAR_JILID_UMMI.filter(it => it.searchKey.includes(q) || it.label.toLowerCase().includes(q))
            : DAFTAR_JILID_UMMI;
        menu.innerHTML = renderSimpleOptionList(list, keyword, 'sky');
        return;
    }

    if (type === 'tahsin') {
        const list = q
            ? DAFTAR_HALAMAN_UMMI.filter(it => it.searchKey.includes(q) || it.label.toLowerCase().includes(q))
            : DAFTAR_HALAMAN_UMMI;
        menu.innerHTML = renderSimpleOptionList(list, keyword, 'sky');
        return;
    }

    if (type === 'juz') {
        const list = q
            ? DAFTAR_30_JUZ.filter(it => it.searchKey.includes(q) || it.label.toLowerCase().includes(q))
            : DAFTAR_30_JUZ;
        menu.innerHTML = renderSimpleOptionList(list, keyword, 'emerald');
        return;
    }

    if (type === 'catatan-tahsin') {
        const list = q
            ? DAFTAR_CATATAN_TAHSIN.filter(it => it.label.toLowerCase().includes(q) || it.value.toLowerCase().includes(q))
            : DAFTAR_CATATAN_TAHSIN;
        menu.innerHTML = renderSimpleOptionList(list, keyword, 'sky');
        return;
    }

    if (type === 'catatan-tahfidz') {
        const list = q
            ? DAFTAR_CATATAN_TAHFIDZ.filter(it => it.label.toLowerCase().includes(q) || it.value.toLowerCase().includes(q))
            : DAFTAR_CATATAN_TAHFIDZ;
        menu.innerHTML = renderSimpleOptionList(list, keyword, 'emerald');
        return;
    }

    // Type: ayat (Dinamis sesuai jumlah ayat surah terpilih)
    if (type === 'ayat') {
        const form = wrap.closest('form');
        const maxAyat = parseInt(form?.dataset.selectedMaxAyat || '0', 10);
        const surahName = form?.dataset.selectedSurahName || '';

        if (!maxAyat) {
            menu.innerHTML = `
                <div class="px-3 py-2 text-muted small">
                    ${q
                        ? `Simpan untuk memakai: <strong>"${escapeHtml(formatAyatText(keyword))}"</strong>`
                        : 'Pilih surah di atas untuk daftar ayat otomatis, atau ketik rentang (misal <strong>1-10</strong>).'}
                </div>`;
            return;
        }

        const ayatOptions = [
            {
                value: `Ayat 1–${maxAyat} • Khatam`,
                label: `Ayat 1–${maxAyat} (Khatam Surah)`,
                tag: 'Khatam',
                searchKey: `khatam semua 1-${maxAyat} 1–${maxAyat} ${maxAyat}`
            }
        ];

        for (let a = 1; a <= maxAyat; a++) {
            ayatOptions.push({
                value: `Ayat ${a}`,
                label: `Ayat ${a}`,
                tag: `dari ${maxAyat}`,
                searchKey: `${a} ayat ${a}`
            });
        }

        const filteredAyat = q
            ? ayatOptions.filter(it => it.searchKey.includes(q) || it.label.toLowerCase().includes(q))
            : ayatOptions;

        const header = `
            <div class="smart-combo-header">
                <span>${escapeHtml(surahName)} • Total ${maxAyat} Ayat</span>
                <span class="text-muted fw-normal">Ketik angka / rentang</span>
            </div>`;

        if (!filteredAyat.length) {
            menu.innerHTML = header + `<div class="px-3 py-2 text-muted small">Simpan untuk memakai rentang: <strong>"${escapeHtml(formatAyatText(keyword))}"</strong></div>`;
            return;
        }

        menu.innerHTML = header + renderSimpleOptionList(filteredAyat, keyword, 'emerald');
        return;
    }

    // Type: tahfidz (114 Surah)
    const form = wrap.closest('form');
    const juzInput = form ? form.querySelector('.materi-prefix-input') : null;
    const selectedJuzVal = juzInput ? juzInput.value.trim() : '';
    const juzMatch = selectedJuzVal.match(/^Juz\s*(\d+)$/i);
    const targetJuz = juzMatch ? parseInt(juzMatch[1], 10) : null;
    const isAllMode = selectedJuzVal === '' || selectedJuzVal.toLowerCase().includes('semua');
    const forceAll = wrap.dataset.forceAll === '1' || isAllMode || q.length > 0;

    let surahList = DAFTAR_114_SURAH;
    if (targetJuz && !forceAll) {
        surahList = DAFTAR_114_SURAH.filter(s => s[3].includes(targetJuz));
    } else if (q) {
        const normalizedQ = q.replace(/[^a-z0-9]/g, '');
        surahList = DAFTAR_114_SURAH.filter(s => {
            const [no, nama, ayat, juzArr] = s;
            const normName = nama.toLowerCase().replace(/[^a-z0-9]/g, '');
            const juzText = juzArr.map(j => `juz ${j} juz${j}`).join(' ');
            return String(no) === q ||
                `${no}.`.startsWith(q) ||
                nama.toLowerCase().includes(q) ||
                normName.includes(normalizedQ) ||
                juzText.includes(q) ||
                `${ayat} ayat`.includes(q);
        });
    }

    const headerHtml = (targetJuz && !forceAll)
        ? `<div class="smart-combo-header">
               <span>Juz ${targetJuz} • ${surahList.length} Surah</span>
               <button type="button" class="smart-combo-all-btn" data-combo-show-all>Semua 114</button>
           </div>`
        : `<div class="smart-combo-header">
               <span>${surahList.length} / 114 Surah</span>
               <span class="text-muted fw-normal">Ketik no / nama</span>
           </div>`;

    if (!surahList.length) {
        menu.innerHTML = headerHtml + `<div class="px-3 py-2 text-muted small">Simpan untuk memakai teks: <strong>"${escapeHtml(keyword)}"</strong></div>`;
        return;
    }

    const itemsHtml = surahList.map(s => {
        const [no, nama, ayat, juzArr] = s;
        const juzBadge = juzArr.length > 1 ? `Juz ${juzArr[0]}–${juzArr[juzArr.length - 1]}` : `Juz ${juzArr[0]}`;
        const fillVal = `Surah ${nama}`;
        return `
            <button type="button" class="smart-combo-item" data-value="${escapeHtml(fillVal)}" data-no="${no}" data-juz="${juzArr[0]}">
                <span class="smart-combo-title text-truncate">
                    <span class="smart-combo-num">${no}.</span> ${escapeHtml(nama)}
                </span>
                <span class="smart-combo-meta">${ayat} Ayat • ${juzBadge}</span>
            </button>
        `;
    }).join('');

    menu.innerHTML = headerHtml + itemsHtml;
}

function renderSimpleOptionList(items, keyword, theme) {
    if (!items.length) {
        return `<div class="px-3 py-2 text-muted small">Simpan untuk memakai teks: <strong>"${escapeHtml(keyword)}"</strong></div>`;
    }
    const badgeClass = theme === 'emerald' ? 'smart-combo-tag-emerald' : 'smart-combo-tag-sky';
    return items.map(it => `
        <button type="button" class="smart-combo-item" data-value="${escapeHtml(it.value)}">
            <span class="smart-combo-title text-truncate">${escapeHtml(it.label)}</span>
            ${it.tag ? `<span class="smart-combo-tag ${badgeClass}">${escapeHtml(it.tag)}</span>` : ''}
        </button>
    `).join('');
}

function applySurahMetadata(form, surahEntry, syncJuzField = true) {
    if (!form || !surahEntry) return;
    const [, nama, maxAyat, juzArr] = surahEntry;
    form.dataset.selectedMaxAyat = String(maxAyat);
    form.dataset.selectedSurahName = nama;

    const ayatInput = form.querySelector('.materi-ayat-input');
    if (ayatInput) {
        ayatInput.placeholder = `Pilih / ketik ayat (1–${maxAyat}) atau Khatam...`;
    }

    if (syncJuzField) {
        const juzInput = form.querySelector('.materi-prefix-input');
        if (juzInput && !juzInput.value.toLowerCase().includes('semua')) {
            juzInput.value = `Juz ${juzArr[0]}`;
        }
    }
}

function resetSurahMetadata(form) {
    if (!form) return;
    delete form.dataset.selectedMaxAyat;
    delete form.dataset.selectedSurahName;
    const ayatInput = form.querySelector('.materi-ayat-input');
    if (ayatInput) {
        ayatInput.placeholder = "Pilih / ketik ayat (misal 1-10 atau Khatam)...";
    }
}

function syncSurahMetadataFromText(form, text) {
    if (!form) return;
    const clean = String(text || '').trim().toLowerCase();
    if (!clean) {
        resetSurahMetadata(form);
        return;
    }

    const numMatch = clean.match(/^(\d{1,3})\b/);
    if (numMatch) {
        const no = parseInt(numMatch[1], 10);
        const found = DAFTAR_114_SURAH.find(s => s[0] === no);
        if (found) {
            applySurahMetadata(form, found, true);
            return;
        }
    }

    const stripped = clean.replace(/^surah\s+/, '').split('(')[0].trim();
    if (stripped.length >= 3) {
        const found = DAFTAR_114_SURAH.find(s => s[1].toLowerCase() === stripped);
        if (found) {
            applySurahMetadata(form, found, true);
            return;
        }
    }

    resetSurahMetadata(form);
}

function formatAyatText(rawAyat) {
    const val = String(rawAyat || '').trim();
    if (!val) return '';
    if (/^\d+(\s*[-–]\s*\d+)?$/.test(val)) {
        return `Ayat ${val.replace(/\s+/g, '')}`;
    }
    return val;
}

function onTahsinJilidUpdated(form, jilidVal) {
    const detailInput = form ? form.querySelector('.materi-detail-input') : null;
    if (!detailInput) return;
    const lower = String(jilidVal || '').toLowerCase();
    if (lower.includes('qur')) {
        detailInput.placeholder = "Contoh: Juz 1 Hal. 12 / Al-Baqarah";
    } else {
        detailInput.placeholder = "Pilih / ketik hal. 1–40...";
    }
}

function onTahfidzJuzUpdated(form) {
    const detailWrap = form ? form.querySelector('.smart-combo-wrap[data-combo-type="tahfidz"]') : null;
    if (!detailWrap) return;
    detailWrap.dataset.forceAll = '0';
    const menu = detailWrap.querySelector('.smart-combo-menu');
    if (menu && menu.classList.contains('show')) {
        openSmartCombo(detailWrap, '');
    }
}

function updateHiddenMateriValue(form) {
    if (!form) return;
    const prefixInput = form.querySelector('.materi-prefix-input');
    const detailInput = form.querySelector('.materi-detail-input');
    const ayatInput = form.querySelector('.materi-ayat-input');
    const hiddenInput = form.querySelector('.materi-hidden-value');
    if (!detailInput || !hiddenInput) return;

    const prefix = prefixInput ? prefixInput.value.trim() : '';
    const detail = detailInput.value.trim();
    const ayatFormatted = ayatInput ? formatAyatText(ayatInput.value) : '';

    if (!detail) {
        hiddenInput.value = '';
        return;
    }

    let combined = detail;
    if (ayatFormatted && !combined.toLowerCase().includes(ayatFormatted.toLowerCase())) {
        combined = `${combined} (${ayatFormatted})`;
    }

    if (!prefix || prefix.toLowerCase().includes('semua') || combined.toLowerCase().startsWith(prefix.toLowerCase())) {
        hiddenInput.value = combined;
    } else {
        hiddenInput.value = `${prefix} - ${combined}`;
    }
}

function syncMateriModal(form) {
    updateHiddenMateriValue(form);
    const hiddenInput = form.querySelector('.materi-hidden-value');
    const detailInput = form.querySelector('.materi-detail-input');
    if (!hiddenInput || !hiddenInput.value.trim()) {
        if (detailInput) detailInput.focus();
        return false;
    }
    return true;
}

function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

/* ================= STATUS PREDIKAT ================= */
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