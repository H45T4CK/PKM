document.addEventListener("DOMContentLoaded", function () {
    updateLiveClock();
    setInterval(updateLiveClock, 1000);
    fetchWeatherSawangan();
    generateInteractiveCalendar();
});

function updateLiveClock() {
    const now = new Date();
    const days = ['Ahad', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
    const shortDays = ['Aha', 'Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab'];
    const months = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'];
    const shortMonths = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Ags', 'Sep', 'Okt', 'Nov', 'Des'];

    const hours = String(now.getHours()).padStart(2, '0');
    const mins = String(now.getMinutes()).padStart(2, '0');
    const secs = String(now.getSeconds()).padStart(2, '0');

    // Desktop Navbar
    const clockEl = document.getElementById('liveClock');
    if (clockEl) {
        clockEl.textContent = `${days[now.getDay()]}, ${now.getDate()} ${months[now.getMonth()]} ${now.getFullYear()} • ${hours}:${mins}:${secs} WIB`;
    }

    // Mobile 2-Baris (Anti Terpotong)
    const mobileTimeEl = document.getElementById('liveClockMobileTime');
    const mobileDateEl = document.getElementById('liveClockMobileDate');
    if (mobileTimeEl && mobileDateEl) {
        mobileTimeEl.textContent = `${hours}:${mins}:${secs} WIB`;
        mobileDateEl.textContent = `${shortDays[now.getDay()]}, ${now.getDate()} ${shortMonths[now.getMonth()]} ${now.getFullYear()}`;
    } else {
        const clockElMobile = document.getElementById('liveClockMobile');
        if (clockElMobile) {
            clockElMobile.textContent = `${hours}:${mins}:${secs} WIB`;
        }
    }

    // Modal Kalender
    const calClock = document.getElementById('calendarLiveClock');
    if (calClock) {
        calClock.textContent = `${hours}:${mins}:${secs} WIB`;
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
        emptyCell.className = 'calendar-cell bg-transparent border-0';
        daysGrid.appendChild(emptyCell);
    }

    for (let d = 1; d <= totalDays; d++) {
        const cell = document.createElement('div');
        cell.className = `calendar-cell ${d === todayDate ? 'today' : ''}`;
        cell.textContent = d;
        daysGrid.appendChild(cell);
    }
}

function getWeatherDetails(code, isNight) {
    let desc = isNight ? "Cerah (Malam)" : "Cerah Terik";
    let iconClass = isNight ? "bi-moon-stars-fill text-warning w-icon-cloud" : "bi-sun-fill text-warning w-icon-sun";
    let modalIconClass = isNight ? "bi-moon-stars-fill text-warning" : "bi-sun-fill text-warning";
    let sceneType = isNight ? "clear-night" : "sunny-day";
    let isStorm = false;

    if (code === 0) {
        desc = isNight ? "Cerah (Malam)" : "Cerah Terik";
        iconClass = isNight ? "bi-moon-stars-fill text-warning w-icon-cloud" : "bi-sun-fill text-warning w-icon-sun";
        modalIconClass = isNight ? "bi-moon-stars-fill text-warning" : "bi-sun-fill text-warning";
        sceneType = isNight ? "clear-night" : "sunny-day";
    } else if (code >= 1 && code <= 3) {
        desc = code === 1 ? "Cerah Berawan" : "Berawan";
        iconClass = isNight ? "bi-cloud-moon-fill text-info w-icon-cloud" : "bi-cloud-sun-fill text-warning w-icon-cloud";
        modalIconClass = isNight ? "bi-cloud-moon-fill text-info" : "bi-cloud-sun-fill text-info";
        sceneType = isNight ? "cloudy-night" : "cloudy-day";
    } else if (code >= 45 && code <= 48) {
        desc = "Berkabut";
        iconClass = "bi-cloud-haze2-fill text-light w-icon-cloud";
        modalIconClass = "bi-cloud-haze2-fill text-secondary";
        sceneType = isNight ? "cloudy-night" : "cloudy-day";
    } else if (code >= 51 && code <= 67) {
        desc = "Hujan Ringan";
        iconClass = "bi-cloud-drizzle-fill text-info w-icon-rain";
        modalIconClass = "bi-cloud-drizzle-fill text-primary";
        sceneType = isNight ? "rain-night" : "rain-day";
    } else if (code >= 71 && code <= 77) {
        desc = "Hujan Sedang";
        iconClass = "bi-cloud-rain-fill text-info w-icon-rain";
        modalIconClass = "bi-cloud-rain-fill text-primary";
        sceneType = isNight ? "rain-night" : "rain-day";
    } else if (code >= 80 && code <= 99) {
        desc = "Hujan Badai";
        iconClass = "bi-cloud-lightning-rain-fill text-warning w-icon-rain";
        modalIconClass = "bi-cloud-lightning-rain-fill text-danger";
        sceneType = isNight ? "rain-night" : "rain-day";
        isStorm = true;
    }

    return { desc, iconClass, modalIconClass, sceneType, isStorm };
}

function getSchoolWeatherAdvisory(code, temp, rainProb, uvVal, isNight) {
    if (code >= 80 && code <= 99) {
        return {
            icon: 'bi-exclamation-triangle-fill text-warning',
            text: 'Waspada hujan lebat disertai petir di Sawangan — siapkan payung/jas hujan dan utamakan keselamatan saat antar-jemput.'
        };
    }
    if ((code >= 51 && code <= 77) || rainProb >= 65) {
        return {
            icon: 'bi-umbrella-fill text-info',
            text: `Peluang hujan tinggi (${rainProb}%) — disarankan membawa payung atau mantel saat kepulangan murid.`
        };
    }
    if (!isNight && (uvVal >= 7 || temp >= 33)) {
        return {
            icon: 'bi-brightness-high-fill text-warning',
            text: `Cuaca cukup terik (${temp}°C, UV ${uvVal}) — ingatkan ananda untuk mencukupi kebutuhan air minum.`
        };
    }
    return {
        icon: 'bi-check-circle-fill text-success',
        text: isNight
            ? 'Cuaca malam di Sawangan cenderung kondusif dan tenang.'
            : 'Cuaca Sawangan kondusif untuk kegiatan belajar mengajar & penjemputan murid.'
    };
}

function buildStarsHtml(count) {
    let html = '';
    for (let i = 0; i < count; i++) {
        const top = ((i * 37) % 82) + 6;
        const left = ((i * 53) % 92) + 4;
        const size = (i % 3 === 0) ? 2.8 : 1.8;
        const dur = (2.2 + (i % 4) * 0.7).toFixed(1);
        const delay = ((i % 5) * 0.5).toFixed(1);
        html += `<span class="sky-star" style="top:${top}%; left:${left}%; width:${size}px; height:${size}px; --dur:${dur}s; --delay:${delay}s;"></span>`;
    }
    return html;
}

function buildCloudsHtml(configs) {
    return configs.map(c => {
        const darkCls = c.dark ? ' dark-cloud' : '';
        return `<div class="sky-cloud${darkCls}" style="top:${c.top}%; width:${c.width}px; height:${c.height}px; --cloud-alpha:${c.alpha}; --dur:${c.dur}s; --delay:${c.delay}s;"></div>`;
    }).join('');
}

function buildRainHtml(count) {
    let html = '';
    for (let i = 0; i < count; i++) {
        const left = ((i * 19) % 104) - 2;
        const len = 14 + (i % 4) * 4;
        const dur = (0.68 + (i % 5) * 0.11).toFixed(2);
        const delay = -((i % 7) * 0.23).toFixed(2);
        html += `<span class="sky-rain-drop" style="left:${left}%; --len:${len}px; --dur:${dur}s; --delay:${delay}s;"></span>`;
    }
    return html;
}

function createSceneMarkup(sceneType, isStorm, isMini) {
    let html = '';
    const scale = isMini ? 0.45 : 1;

    if (sceneType === 'sunny-day') {
        html += `
            <div class="sky-sun-wrap">
                <div class="sky-sun-rays"></div>
                <div class="sky-sun-core"></div>
            </div>
        `;
        html += buildCloudsHtml([
            { top: isMini ? 24 : 18, width: Math.round(88 * scale), height: Math.round(24 * scale), alpha: 0.36, dur: isMini ? 18 : 30, delay: -6, dark: false },
            { top: isMini ? 56 : 58, width: Math.round(64 * scale), height: Math.round(18 * scale), alpha: 0.26, dur: isMini ? 14 : 24, delay: -12, dark: false }
        ]);
    } else if (sceneType === 'cloudy-day') {
        html += buildCloudsHtml([
            { top: isMini ? 16 : 12, width: Math.round(118 * scale), height: Math.round(32 * scale), alpha: 0.38, dur: isMini ? 16 : 28, delay: -4, dark: false },
            { top: isMini ? 44 : 38, width: Math.round(92 * scale), height: Math.round(25 * scale), alpha: 0.28, dur: isMini ? 13 : 22, delay: -9, dark: false },
            { top: isMini ? 68 : 66, width: Math.round(130 * scale), height: Math.round(34 * scale), alpha: 0.24, dur: isMini ? 20 : 34, delay: -15, dark: false }
        ]);
    } else if (sceneType === 'rain-day') {
        html += buildCloudsHtml([
            { top: isMini ? 8 : 6, width: Math.round(132 * scale), height: Math.round(34 * scale), alpha: 0.44, dur: isMini ? 15 : 24, delay: -3, dark: true },
            { top: isMini ? 28 : 22, width: Math.round(105 * scale), height: Math.round(28 * scale), alpha: 0.36, dur: isMini ? 12 : 19, delay: -8, dark: true }
        ]);
        html += buildRainHtml(isMini ? 16 : 28);
        if (isStorm) html += `<div class="sky-lightning"></div>`;
    } else if (sceneType === 'clear-night') {
        html += `<div class="sky-moon"></div>`;
        html += buildStarsHtml(isMini ? 10 : 22);
    } else if (sceneType === 'cloudy-night') {
        html += `<div class="sky-moon"></div>`;
        html += buildStarsHtml(isMini ? 7 : 14);
        html += buildCloudsHtml([
            { top: isMini ? 22 : 20, width: Math.round(112 * scale), height: Math.round(30 * scale), alpha: 0.2, dur: isMini ? 16 : 28, delay: -5, dark: false },
            { top: isMini ? 56 : 56, width: Math.round(86 * scale), height: Math.round(23 * scale), alpha: 0.14, dur: isMini ? 13 : 22, delay: -11, dark: false }
        ]);
    } else if (sceneType === 'rain-night') {
        html += buildCloudsHtml([
            { top: isMini ? 10 : 8, width: Math.round(130 * scale), height: Math.round(34 * scale), alpha: 0.55, dur: isMini ? 15 : 24, delay: -4, dark: true },
            { top: isMini ? 28 : 24, width: Math.round(100 * scale), height: Math.round(26 * scale), alpha: 0.45, dur: isMini ? 12 : 19, delay: -9, dark: true }
        ]);
        html += buildRainHtml(isMini ? 16 : 28);
        if (isStorm) html += `<div class="sky-lightning"></div>`;
    }

    return html;
}

function renderWeatherScene(sceneType, isStorm) {
    const themeClass = `weather-theme-${sceneType}`;

    // 1. Kartu Hero di Dalam Modal
    const heroBg = document.getElementById('weatherHeroBg');
    const skyScene = document.getElementById('weatherSkyScene');
    if (heroBg && skyScene) {
        heroBg.className = `weather-hero-card ${themeClass} p-3 p-sm-4 rounded-4 mb-4 position-relative overflow-hidden text-white`;
        skyScene.innerHTML = createSceneMarkup(sceneType, isStorm, false);
    }

    // 2. Chip Cuaca di Navbar Desktop
    const desktopChip = document.getElementById('desktopWeatherChip');
    const desktopSky = document.getElementById('desktopWeatherSky');
    if (desktopChip && desktopSky) {
        desktopChip.className = `widget-chip weather-animated-chip ${themeClass} d-flex align-items-center gap-2`;
        desktopSky.innerHTML = createSceneMarkup(sceneType, isStorm, true);
    }

    // 3. Card Cuaca di Mobile / Tablet
    const mobileChip = document.getElementById('mobileWeatherChip');
    const mobileSky = document.getElementById('mobileWeatherSky');
    if (mobileChip && mobileSky) {
        mobileChip.className = `widget-mobile-card weather-animated-chip ${themeClass}`;
        mobileSky.innerHTML = createSceneMarkup(sceneType, isStorm, true);
    }
}

function fetchWeatherSawangan() {
    const nowHour = new Date().getHours();
    const initialNight = (nowHour >= 18 || nowHour < 6);
    renderWeatherScene(initialNight ? 'clear-night' : 'sunny-day', false);

    // Koordinat Presisi Kel. Pasir Putih, Kec. Sawangan, Kota Depok
    const url = 'https://api.open-meteo.com/v1/forecast?latitude=-6.4258&longitude=106.7842&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,weather_code,wind_speed_10m,precipitation,cloud_cover&hourly=temperature_2m,relative_humidity_2m,weather_code,precipitation_probability,wind_speed_10m,uv_index,is_day&daily=temperature_2m_max,temperature_2m_min&timezone=Asia%2FJakarta&forecast_days=2';

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 7000);

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
            const precipMm = cur.precipitation ?? 0;
            const cloudCover = cur.cloud_cover ?? 0;
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

            // Desktop & Mobile Chip
            setTxt('weatherTemp', `${temp}°C`);
            setTxt('weatherDesc', weatherInfo.desc);
            setHtml('weatherIcon', `<i class="bi ${weatherInfo.iconClass}"></i>`);

            setTxt('weatherTempMobile', `${temp}°C`);
            setTxt('weatherDescMobile', weatherInfo.desc);
            setHtml('weatherIconMobile', `<i class="bi ${weatherInfo.iconClass}"></i>`);

            // Modal Hero
            setTxt('modalCurrentTemp', `${temp}°C`);
            setTxt('modalCurrentDesc', weatherInfo.desc);

            if (isNight) {
                setHtml('modalDayNightBadge', `<i class="bi bi-moon-stars-fill text-warning"></i> Suasana Malam Hari`);
            } else {
                setHtml('modalDayNightBadge', `<i class="bi bi-sun-fill text-warning"></i> Suasana Siang Hari`);
            }

            renderWeatherScene(weatherInfo.sceneType, weatherInfo.isStorm);

            setHtml('modalFeelsLike', `<i class="bi bi-thermometer-half me-1 text-warning"></i>Terasa ${feelsLike}°C • Awan ${cloudCover}%`);
            setTxt('metricHumidity', `${humidity}%`);
            setTxt('metricWind', `${windSpeed} km/j`);
            setTxt('metricRainProb', `${rainProb}% (${precipMm} mm)`);

            let uvStatus = "Rendah";
            if (uvVal >= 3 && uvVal <= 5) uvStatus = "Sedang";
            else if (uvVal >= 6 && uvVal <= 7) uvStatus = "Tinggi";
            else if (uvVal >= 8) uvStatus = "Sangat Tinggi";
            setTxt('metricUV', isNight ? `0 (Malam)` : `${uvVal} (${uvStatus})`);

            if (data.daily && data.daily.temperature_2m_min && data.daily.temperature_2m_max) {
                const tMin = Math.round(data.daily.temperature_2m_min[0]);
                const tMax = Math.round(data.daily.temperature_2m_max[0]);
                setTxt('modalTempRange', `${tMin}°C – ${tMax}°C`);
            }

            // Rekomendasi Sekolah & Penjemputan
            const advisory = getSchoolWeatherAdvisory(cur.weather_code, temp, rainProb, uvVal, isNight);
            setHtml('modalWeatherAdvisory', `<i class="bi ${advisory.icon} flex-shrink-0"></i><span>${advisory.text}</span>`);

            renderHourlyDailySlots(data, now.getHours());
        })
        .catch(() => {
            clearTimeout(timeoutId);
            const h = new Date().getHours();
            const isNightFallback = (h >= 18 || h < 6);
            renderWeatherScene(isNightFallback ? 'clear-night' : 'sunny-day', false);

            const setTxt = (id, txt) => { const el = document.getElementById(id); if (el) el.textContent = txt; };
            setTxt('weatherTemp', '29°C');
            setTxt('weatherDesc', isNightFallback ? 'Cerah (Malam)' : 'Cerah Berawan');
            setTxt('weatherTempMobile', '29°C');
            setTxt('weatherDescMobile', isNightFallback ? 'Cerah (Malam)' : 'Cerah Berawan');

            const container3h = document.getElementById('weather3hContainer');
            if (container3h) {
                container3h.innerHTML = `
                    <div class="col-12 text-center py-3 text-muted small">
                        <i class="bi bi-wifi-off me-1"></i> Tidak dapat memuat prakiraan per jam saat offline.
                    </div>
                `;
            }
        });
}

function renderHourlyDailySlots(data, currentHour) {
    const container = document.getElementById('weather3hContainer');
    if (!container || !data.hourly) return;

    const targetHours = [6, 9, 12, 15, 18, 21];
    const times = data.hourly.time;
    const temps = data.hourly.temperature_2m;
    const codes = data.hourly.weather_code;
    const rainProbs = data.hourly.precipitation_probability || [];
    const winds = data.hourly.wind_speed_10m || [];
    const isDays = data.hourly.is_day || [];

    // Cari slot terdekat dengan jam sekarang
    let closestSlot = 6;
    let minDiff = 99;
    targetHours.forEach(h => {
        const diff = Math.abs(currentHour - h);
        if (diff < minDiff) {
            minDiff = diff;
            closestSlot = h;
        }
    });

    let cardsHtml = '';
    for (let i = 0; i < 24 && i < times.length; i++) {
        const hourNum = parseInt(times[i].split('T')[1].split(':')[0], 10);
        if (!targetHours.includes(hourNum)) continue;

        const temp = Math.round(temps[i]);
        const rainP = rainProbs[i] || 0;
        const windS = Math.round(winds[i] || 0);
        const isNightCard = isDays[i] !== undefined ? (isDays[i] === 0) : (hourNum < 6 || hourNum >= 18);
        const weatherInfo = getWeatherDetails(codes[i], isNightCard);
        const isCurrentSlot = (hourNum === closestSlot);

        const cardStyle = isNightCard
            ? `background: linear-gradient(160deg, #0f172a 0%, #1e293b 100%); color: #ffffff; border: ${isCurrentSlot ? '2px solid #facc15' : '1px solid rgba(255,255,255,0.14)'};`
            : `background: #f8fafc; color: #0f172a; border: ${isCurrentSlot ? '2px solid #0284c7' : '1px solid #e2e8f0'};`;

        const timeBadge = isNightCard
            ? `<span class="badge rounded-pill px-2 py-1 fw-bold" style="background: rgba(255,255,255,0.14); color: #ffffff; font-size: 0.69rem;">${String(hourNum).padStart(2, '0')}:00 WIB</span>`
            : `<span class="badge bg-dark text-white rounded-pill px-2 py-1 fw-bold" style="font-size: 0.69rem;">${String(hourNum).padStart(2, '0')}:00 WIB</span>`;

        const activeTag = isCurrentSlot
            ? `<div class="forecast-status-slot"><span class="badge bg-warning text-dark rounded-pill px-2 py-1" style="font-size: 0.58rem; font-weight: 800; letter-spacing: 0.3px;">SAAT INI</span></div>`
            : `<div class="forecast-status-slot"></div>`;

        cardsHtml += `
            <div class="col-6 col-md-4 col-lg-2">
                <div class="forecast-slot-card p-2 p-sm-3 rounded-4 text-center h-100 shadow-sm d-flex flex-column justify-content-between" style="${cardStyle}">
                    <div>
                        ${activeTag}
                        <div>${timeBadge}</div>
                        <div class="fs-2 my-1"><i class="bi ${weatherInfo.modalIconClass}"></i></div>
                        <div class="fw-extrabold fs-4 mb-0">${temp}°C</div>
                        <div class="fw-bold ${isNightCard ? 'text-white-50' : 'text-muted'}" style="font-size: 0.72rem; line-height: 1.25; min-height: 28px; display: flex; align-items: center; justify-content: center;">
                            ${weatherInfo.desc}
                        </div>
                    </div>
                    <div class="mt-2 pt-2 border-top border-secondary border-opacity-25 d-flex justify-content-around align-items-center fw-bold" style="font-size: 0.7rem;">
                        <span title="Peluang Hujan" style="color: ${isNightCard ? '#7dd3fc' : '#0284c7'};"><i class="bi bi-droplet-fill"></i> ${rainP}%</span>
                        <span title="Kecepatan Angin" style="color: ${isNightCard ? '#fde047' : '#475569'};"><i class="bi bi-wind"></i> ${windS}k/j</span>
                    </div>
                </div>
            </div>
        `;
    }
    container.innerHTML = cardsHtml;
}

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