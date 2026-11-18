document.addEventListener("DOMContentLoaded", function () {
    updateLiveClock();
    setInterval(updateLiveClock, 1000);
    fetchWeatherSawangan();
    generateInteractiveCalendar();
});

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
            setTxt('metricUV', `${uvVal}`);

            const container3h = document.getElementById('weather3hContainer');
            if (container3h && data.hourly && data.hourly.time) {
                let cardsHtml = '';
                let count = 0;

                for (let i = targetIdx; i < data.hourly.time.length && count < 4; i += 3) {
                    const timeStr = data.hourly.time[i];
                    const hourStr = timeStr.split('T')[1].substring(0, 5);
                    const hTemp = Math.round(data.hourly.temperature_2m[i]);
                    const hCode = data.hourly.weather_code[i];
                    const hRain = data.hourly.precipitation_probability ? data.hourly.precipitation_probability[i] : 0;
                    const hHourNum = parseInt(hourStr.split(':')[0], 10);
                    const hIsNight = (hHourNum >= 18 || hHourNum < 6);
                    const hInfo = getWeatherDetails(hCode, hIsNight);

                    cardsHtml += `
                        <div class="col-6 col-md-3">
                            <div class="card-modern p-3 text-center border-0 h-100 shadow-sm" style="background: #f8fafc; border-radius: 14px;">
                                <span class="text-muted fw-bold d-block mb-1" style="font-size: 0.75rem;">${hourStr} WIB</span>
                                <i class="bi ${hInfo.iconClass} fs-3 my-1 d-block"></i>
                                <div class="fw-extrabold text-dark fs-5">${hTemp}°C</div>
                                <span class="badge bg-light text-dark border px-2 py-0.5 rounded-pill mt-1" style="font-size: 0.65rem;">${hInfo.desc}</span>
                                <div class="text-primary mt-1" style="font-size: 0.68rem; font-weight: 600;">
                                    <i class="bi bi-droplet-fill me-0.5"></i>${hRain}%
                                </div>
                            </div>
                        </div>
                    `;
                    count++;
                }
                container3h.innerHTML = cardsHtml;
            }
        })
        .catch(() => {
            clearTimeout(timeoutId);
            const wTemp = document.getElementById('weatherTemp');
            const wDesc = document.getElementById('weatherDesc');
            if (wTemp) wTemp.textContent = '29°C';
            if (wDesc) wDesc.textContent = 'Cerah Berawan';

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