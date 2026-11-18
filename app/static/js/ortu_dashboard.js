function filterLinimasa(mode, btnEl) {
    document.querySelectorAll('.timeline-filter-pill').forEach(b => b.classList.remove('active'));
    if (btnEl) {
        btnEl.classList.add('active');
    } else {
        const targetBtn = document.querySelector(`.timeline-filter-pill[data-filter-mode="${mode}"]`);
        if (targetBtn) targetBtn.classList.add('active');
    }

    const cols = document.querySelectorAll('.timeline-col');
    const cards = document.querySelectorAll('.linimasa-card');

    cols.forEach(col => {
        const colType = col.getAttribute('data-col-type');
        if (mode === 'tahsin') {
            col.style.display = (colType === 'tahsin') ? '' : 'none';
            col.className = (colType === 'tahsin') ? 'col-12 timeline-col' : 'col-12 col-lg-6 timeline-col';
        } else if (mode === 'tahfidz') {
            col.style.display = (colType === 'tahfidz') ? '' : 'none';
            col.className = (colType === 'tahfidz') ? 'col-12 timeline-col' : 'col-12 col-lg-6 timeline-col';
        } else {
            col.style.display = '';
            col.className = 'col-12 col-lg-6 timeline-col';
        }
    });

    cards.forEach(card => {
        const paraf = card.getAttribute('data-paraf');
        if (mode === 'unverified') {
            card.style.display = (paraf === 'no') ? '' : 'none';
        } else {
            card.style.display = '';
        }
    });

    cols.forEach(col => {
        const emptyNotice = col.querySelector('.empty-filter-notice');
        if (!emptyNotice) return;

        const colCards = col.querySelectorAll('.linimasa-card');
        const hasVisibleCard = Array.from(colCards).some(c => c.style.display !== 'none');
        emptyNotice.classList.toggle('d-none', colCards.length === 0 || hasVisibleCard);
    });
}

function jumpToUnverified() {
    filterLinimasa('unverified', null);
    const section = document.getElementById('sectionLinimasa');
    if (section) {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}