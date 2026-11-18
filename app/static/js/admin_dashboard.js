document.addEventListener("DOMContentLoaded", function () {
    updateLiveClock();
    setInterval(updateLiveClock, 1000);
    fetchWeatherSawangan();
    generateInteractiveCalendar();

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

/* ================= JAM & KALENDER ================= */
function updateLiveClock() {
    const now = new Date();
    const days = ['Ahad', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
    const months = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'];
    const shortMonths = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Ags', 'Sep', 'Okt', 'Nov', 'Des'];

    const hours = String(now.getHours()).padStart(2, '0');
    const mins = String(now.getMinutes()).padStart(2, '0');
    const secs = String(now.getSeconds()).padStart(2, '0');

    const clockEl = document.getElementById('liveClock');
    if (clockEl) {
        clockEl.textContent = `${days[now.getDay()]}, ${now.getDate()} ${months[now.getMonth()]} ${now.getFullYear()} • ${hours}:${mins}:${secs} WIB`;
    }

    const clockElMobile = document.getElementById('liveClockMobile');
    if (clockElMobile) {
        clockElMobile.textContent = `${hours}:${mins} WIB • ${now.getDate()} ${shortMonths[now.getMonth()]}`;
    }
}

function generateInteractiveCalendar() {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth();
    const todayDate = now.getDate();

    const days = ['Ahad', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
    const months = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'];

    const monthTitle = document.getElementById('calendarMonthTitle');
    const todayHeader = document.getElementById('calendarTodayHeader');
    const daysGrid = document.getElementById('calendarDaysGrid');

    if (monthTitle) monthTitle.textContent = `Kalender ${months[month]} ${year}`;
    if (todayHeader) todayHeader.textContent = `${days[now.getDay()]}, ${todayDate} ${months[month]} ${year}`;

    if (!daysGrid) return;
    daysGrid.innerHTML = '';

    const firstDay = new Date(year, month, 1).getDay();
    const totalDays = new Date(year, month + 1, 0).getDate();

    for (let i = 0; i < firstDay; i++) {
        const emptyCell = document.createElement('div');
        emptyCell.className = 'calendar-cell bg-transparent';
        daysGrid.appendChild(emptyCell);
    }

    for (let d = 1; d <= totalDays; d++) {
        const cell = document.createElement('div');
        cell.className = `calendar-cell ${d === todayDate ? 'today' : ''}`;
        cell.textContent = d;
        daysGrid.appendChild(cell);
    }
}

/* ================= PRAKIRAAN CUACA OPEN-METEO ================= */
function getWeatherDetails(code, isNight) {
    let desc = "Cerah";
    let iconClass = isNight ? "bi-moon-stars-fill text-warning" : "bi-sun-fill text-warning";

    if (code === 0) {
        desc = isNight ? "Cerah (Malam)" : "Cerah";
        iconClass = isNight ? "bi-moon-stars-fill text-warning" : "bi-sun-fill text-warning";
    } else if (code >= 1 && code <= 3) {
        desc = "Berawan";
        iconClass = isNight ? "bi-cloud-moon-fill text-info" : "bi-cloud-sun-fill text-info";
    } else if (code >= 45 && code <= 48) {
        desc = "Berkabut";
        iconClass = "bi-cloud-haze2-fill text-secondary";
    } else if (code >= 51 && code <= 67) {
        desc = "Hujan Ringan";
        iconClass = "bi-cloud-drizzle-fill text-primary";
    } else if (code >= 71 && code <= 77) {
        desc = "Hujan Sedang";
        iconClass = "bi-cloud-rain-fill text-primary";
    } else if (code >= 80 && code <= 99) {
        desc = "Hujan Badai";
        iconClass = "bi-cloud-lightning-rain-fill text-danger";
    }

    return { desc, iconClass };
}

function fetchWeatherSawangan() {
    const url = 'https://api.open-meteo.com/v1/forecast?latitude=-6.417&longitude=106.783&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,weather_code,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,weather_code,precipitation_probability,wind_speed_10m,uv_index&timezone=Asia%2FJakarta';

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 6000);

    fetch(url, { signal: controller.signal })
        .then(response => {
            clearTimeout(timeoutId);
            if (!response.ok) throw new Error("API Response Error: " + response.status);
            return response.json();
        })
        .then(data => {
            if (!data || !data.current) return;

            const cur = data.current;
            const temp = Math.round(cur.temperature_2m);
            const feelsLike = Math.round(cur.apparent_temperature);
            const humidity = cur.relative_humidity_2m;
            const windSpeed = Math.round(cur.wind_speed_10m);
            const isNight = (cur.is_day === 0);
            const weatherInfo = getWeatherDetails(cur.weather_code, isNight);

            const now = new Date();
            const currentISO = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}T${String(now.getHours()).padStart(2, '0')}:00`;

            let targetIdx = 0;
            if (data.hourly && data.hourly.time) {
                const foundIdx = data.hourly.time.findIndex(t => t.startsWith(currentISO));
                targetIdx = foundIdx !== -1 ? foundIdx : now.getHours();
            }

            const rainProb = (data.hourly && data.hourly.precipitation_probability) ? (data.hourly.precipitation_probability[targetIdx] || 0) : 0;
            const uvVal = (data.hourly && data.hourly.uv_index) ? Math.round(data.hourly.uv_index[targetIdx] || 0) : 0;

            const setTxt = (id, txt) => { const el = document.getElementById(id); if (el) el.textContent = txt; };
            const setHtml = (id, html) => { const el = document.getElementById(id); if (el) el.innerHTML = html; };

            setTxt('weatherTemp', `${temp}°C`);
            setTxt('weatherDesc', weatherInfo.desc);
            setHtml('weatherIcon', `<i class="bi ${weatherInfo.iconClass}"></i>`);

            setTxt('weatherTempMobile', `${temp}°C`);
            setTxt('weatherDescMobile', weatherInfo.desc);
            setHtml('weatherIconMobile', `<i class="bi ${weatherInfo.iconClass}"></i>`);

            setTxt('modalCurrentTemp', `${temp}°C`);
            setTxt('modalCurrentDesc', weatherInfo.desc);

            const heroBg = document.getElementById('weatherHeroBg');
            if (isNight) {
                setHtml('modalDayNightBadge', `<i class="bi bi-moon-stars-fill text-warning me-1"></i> Suasana Malam Hari`);
                if (heroBg) heroBg.style.background = 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)';
            } else {
                setHtml('modalDayNightBadge', `<i class="bi bi-sun-fill text-warning me-1"></i> Suasana Siang Hari`);
                if (heroBg) heroBg.style.background = 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)';
            }

            setHtml('modalFeelsLike', `<i class="bi bi-thermometer-half me-1 text-warning"></i>Sensasi Terasa: ${feelsLike}°C`);
            setTxt('metricHumidity', `${humidity}%`);
            setTxt('metricWind', `${windSpeed} km/j`);
            setTxt('metricRainProb', `${rainProb}%`);

            let uvStatus = "Rendah";
            if (uvVal >= 3 && uvVal <= 5) uvStatus = "Sedang";
            else if (uvVal >= 6) uvStatus = "Tinggi";
            setTxt('metricUV', `${uvVal} (${uvStatus})`);

            renderHourly3hForecast(data);
        })
        .catch(() => {
            clearTimeout(timeoutId);
            const container = document.getElementById('weather3hContainer');
            if (container) {
                container.innerHTML = `
                    <div class="col-12 text-center py-4 text-danger">
                        <i class="bi bi-exclamation-triangle-fill fs-3 mb-2 d-block"></i>
                        <h6 class="fw-bold mb-1">Gagal Memuat Data Cuaca</h6>
                        <small class="text-muted">Periksa koneksi internet Anda lalu muat ulang halaman.</small>
                    </div>
                `;
            }
            const mDesc = document.getElementById('modalCurrentDesc');
            const wDesc = document.getElementById('weatherDesc');
            if (mDesc) mDesc.textContent = "Offline";
            if (wDesc) wDesc.textContent = "Offline";
        });
}

function renderHourly3hForecast(data) {
    const container = document.getElementById('weather3hContainer');
    if (!container || !data.hourly) return;

    container.innerHTML = '';
    const targetHours = [6, 9, 12, 15, 18, 21];

    const times = data.hourly.time;
    const temps = data.hourly.temperature_2m;
    const codes = data.hourly.weather_code;
    const rainProbs = data.hourly.precipitation_probability || [];
    const winds = data.hourly.wind_speed_10m || [];

    for (let i = 0; i < 24; i++) {
        const hourNum = parseInt(times[i].split('T')[1].split(':')[0], 10);
        if (!targetHours.includes(hourNum)) continue;

        const temp = Math.round(temps[i]);
        const rainP = rainProbs[i] || 0;
        const windS = Math.round(winds[i] || 0);
        const isNightCard = (hourNum < 6 || hourNum >= 18);
        const weatherInfo = getWeatherDetails(codes[i], isNightCard);

        const cardBgStyle = isNightCard
            ? 'background: #0f172a; color: #ffffff; border: 1px solid rgba(255,255,255,0.15); box-shadow: 0 4px 12px rgba(0,0,0,0.2);'
            : 'background: #f8fafc; color: #0f172a; border: 1px solid #e2e8f0;';

        const badgeHtml = isNightCard
            ? `<span class="badge rounded-pill px-2.5 py-1 small fw-bold mb-2" style="background-color: rgba(255,255,255,0.15); color: #ffffff;">${String(hourNum).padStart(2, '0')}:00 WIB</span>`
            : `<span class="badge bg-dark text-white rounded-pill px-2.5 py-1 small fw-bold mb-2">${String(hourNum).padStart(2, '0')}:00 WIB</span>`;

        const metricTextColor = isNightCard ? '#ffffff' : '#0f172a';

        const col = document.createElement('div');
        col.className = 'col-6 col-md-4 col-lg-2';
        col.innerHTML = `
            <div class="p-3 rounded-4 text-center transition-all h-100" style="${cardBgStyle}">
                ${badgeHtml}
                <div class="fs-2 my-1"><i class="bi ${weatherInfo.iconClass}"></i></div>
                <div class="fw-extrabold fs-4 mb-0">${temp}°C</div>
                <small class="d-block fw-bold ${isNightCard ? 'text-white-50' : 'text-muted'} text-truncate" style="font-size: 0.74rem;">${weatherInfo.desc}</small>
                <div class="mt-2 pt-2 border-top border-secondary border-opacity-25 d-flex justify-content-around align-items-center fw-bold" style="font-size: 0.76rem;">
                    <span title="Peluang Hujan" style="color: ${metricTextColor};"><i class="bi bi-cloud-rain-fill text-primary"></i> ${rainP}%</span>
                    <span title="Kecepatan Angin" style="color: ${metricTextColor};"><i class="bi bi-wind text-warning"></i> ${windS}k/h</span>
                </div>
            </div>
        `;
        container.appendChild(col);
    }
}

/* ================= UTILITAS FORM & PILIH KELAS ================= */
function toggleGenericPassword(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    if (!input || !icon) return;

    const show = input.type === 'password';
    input.type = show ? 'text' : 'password';
    icon.classList.toggle('bi-eye-slash-fill', !show);
    icon.classList.toggle('bi-eye-fill', show);
    icon.classList.toggle('text-muted', !show);
    icon.classList.toggle('text-primary', show);
}

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