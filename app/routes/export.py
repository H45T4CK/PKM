from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file, Response
from app.models.siswa import Siswa
from app.models.user import User, AppSetting
from app import db
from app.utils.decorators import role_required
from datetime import datetime
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as ExcelImage
import io, os

export_bp = Blueprint('export', __name__)

PREDIKAT_FALLBACK = {
    'A': 'Mumtaz (Sangat Baik)',
    'B+': 'Jayyid Jiddan (Baik Sekali)',
    'B': 'Jayyid (Baik)',
    'C': 'Perlu Bimbingan',
    '-': 'Belum Dinilai'
}

EXPORT_COLUMNS = [
    "No",
    "NISN / ID",
    "Nama Murid",
    "Kelas",
    "Status Murid",
    "Materi Tahsin Terakhir",
    "Jml Setor Tahsin",
    "Grade Tahsin",
    "Predikat Tahsin",
    "Hafalan Tahfidz Terakhir",
    "Jml Setor Tahfidz",
    "Grade Tahfidz",
    "Predikat Tahfidz",
    "Grade Akhir Qur'an",
    "Predikat Akhir",
    "Status Kelulusan"
]


def _get_predikat_desc(siswa_obj, attr_name, grade_val):
    val = getattr(siswa_obj, attr_name, None)
    if val:
        return val
    return PREDIKAT_FALLBACK.get(grade_val, 'Belum Dinilai')


def _get_nama_musyrif_kelas(siswa):
    """Mengambil nama Guru Tahfidz / Musyrif yang mengampu kelas siswa secara otomatis."""
    target_kelas = (siswa.kelas or '').strip().upper()
    guru_list = User.query.filter_by(role='guru').order_by(User.id.asc()).all()
    matched_gurus = []

    for g in guru_list:
        g_classes = [
            x.strip().upper()
            for x in (g.kelas or '').replace('/', ',').replace(';', ',').split(',')
            if x.strip() and x.strip() != '-'
        ]
        if target_kelas and target_kelas in g_classes:
            matched_gurus.append(g)

    # Jika pengguna yang sedang login adalah guru dari kelas tersebut, gunakan namanya
    if session.get('role') == 'guru' and session.get('user'):
        logged_name = session.get('user').strip()
        for g in matched_gurus:
            if (g.nama or '').strip() == logged_name or (g.username or '').strip() == logged_name:
                return g.nama or g.username
        if not matched_gurus:
            return logged_name

    # Prioritaskan guru aktif yang terdaftar pada kelas siswa
    for g in matched_gurus:
        if (g.status or 'Aktif') == 'Aktif':
            return g.nama or g.username
    if matched_gurus:
        return matched_gurus[0].nama or matched_gurus[0].username

    # Fallback ke nama penilai terakhir pada riwayat setoran siswa jika ada
    for rec in reversed(siswa.tahfidz or []):
        if getattr(rec, 'penilai', None):
            return rec.penilai
    for rec in reversed(siswa.tahsin or []):
        if getattr(rec, 'penilai', None):
            return rec.penilai

    return ''


def _get_filtered_siswa():
    query = Siswa.query
    if session.get('role') == 'guru':
        guru_kelas = session.get('kelas', '').strip()
        if guru_kelas and guru_kelas != '-':
            classes = [
                c.strip().upper()
                for c in guru_kelas.replace('/', ',').replace(';', ',').split(',')
                if c.strip() and c.strip() != '-'
            ]
            if classes:
                query = query.filter(db.func.upper(Siswa.kelas).in_(classes))

    kelas_filter = request.args.get('kelas_filter', '').strip()
    if kelas_filter and kelas_filter.lower() != 'all':
        query = query.filter(db.func.upper(Siswa.kelas) == kelas_filter.upper())

    status_filter = request.args.get('status_filter', '').strip()
    if status_filter and status_filter.lower() != 'all':
        query = query.filter(db.func.lower(Siswa.status) == status_filter.lower())

    return query.order_by(Siswa.kelas.asc(), Siswa.nama.asc()).all()


def _build_export_rows(siswa_list):
    rows = []
    for idx, s in enumerate(siswa_list, start=1):
        last_tahsin = s.tahsin[-1].halaman_akhir if s.tahsin else "-"
        last_tahfidz = s.tahfidz[-1].hafalan_terakhir if s.tahfidz else "-"
        g_tahsin = s.grade_tahsin
        g_tahfidz = s.grade_tahfidz
        g_akhir = s.grade_rata_rata

        rows.append({
            "No": idx,
            "NISN / ID": s.id,
            "Nama Murid": s.nama,
            "Kelas": s.kelas,
            "Status Murid": s.status_clean,
            "Materi Tahsin Terakhir": last_tahsin,
            "Jml Setor Tahsin": len(s.tahsin),
            "Grade Tahsin": g_tahsin,
            "Predikat Tahsin": _get_predikat_desc(s, 'predikat_tahsin_desc', g_tahsin),
            "Hafalan Tahfidz Terakhir": last_tahfidz,
            "Jml Setor Tahfidz": len(s.tahfidz),
            "Grade Tahfidz": g_tahfidz,
            "Predikat Tahfidz": _get_predikat_desc(s, 'predikat_tahfidz_desc', g_tahfidz),
            "Grade Akhir Qur'an": g_akhir,
            "Predikat Akhir": _get_predikat_desc(s, 'predikat_rata_rata_desc', g_akhir),
            "Status Kelulusan": s.status_kelulusan_rata_rata
        })
    return rows


def _apply_kop_surat(ws, subtitle_text, info_text):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(base_dir, 'static', 'img', 'logo-sdit.png')
    if os.path.exists(logo_path):
        try:
            img = ExcelImage(logo_path)
            img.width = 48
            img.height = 48
            ws.add_image(img, 'A1')
        except Exception:
            pass

    ws['B1'] = "SDIT BINA MULIA"
    ws['B1'].font = Font(name="Arial", size=13, bold=True, color="059669")

    ws['B2'] = subtitle_text
    ws['B2'].font = Font(name="Arial", size=10, bold=True, color="0F172A")

    ws['B3'] = info_text
    ws['B3'].font = Font(name="Arial", size=9, italic=True, color="475569")

    ws.row_dimensions[1].height = 20
    ws.row_dimensions[2].height = 18
    ws.row_dimensions[3].height = 16
    ws.row_dimensions[4].height = 8


def _configure_print_landscape(ws):
    ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0


@export_bp.route('/cetak_hafalan/<id_siswa>')
@export_bp.route('/riwayat_poin/<id_siswa>')
@role_required('guru', 'admin', 'ortu')
def cetak_hafalan_siswa(id_siswa):
    siswa = Siswa.query.get_or_404(id_siswa)
    ta_str = AppSetting.get_val('tahun_ajaran', '2026/2027')
    sem_str = AppSetting.get_val('semester', 'Ganjil')
    tanggal_cetak = datetime.now().strftime("%d/%m/%Y")
    nama_musyrif = _get_nama_musyrif_kelas(siswa)

    return render_template(
        'reports/lembar_hafalan.html',
        siswa=siswa,
        tanggal=tanggal_cetak,
        nama_musyrif=nama_musyrif,
        tahun_ajaran=ta_str,
        semester=sem_str,
        tahun_ajaran_full=f"Tahun Ajaran {ta_str} – Semester {sem_str}"
    )


@export_bp.route('/export_excel')
@role_required('guru', 'admin')
def export_excel():
    try:
        siswa_list = _get_filtered_siswa()
        rows = _build_export_rows(siswa_list)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Rekap_Capaian_Murid"

        ta_str = AppSetting.get_val('tahun_ajaran', '2026/2027')
        sem_str = AppSetting.get_val('semester', 'Ganjil')
        tgl_cetak = datetime.now().strftime("%d/%m/%Y %H:%M WIB")
        kelas_info = session.get('kelas', 'Semua Kelas') if session.get('role') == 'guru' else 'Semua Kelas'

        header_fill = PatternFill(start_color="059669", end_color="059669", fill_type="solid")
        header_font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
        zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

        lulus_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
        lulus_font = Font(name="Arial", size=10, bold=True, color="166534")
        gagal_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
        gagal_font = Font(name="Arial", size=10, bold=True, color="991B1B")
        neutral_font = Font(name="Arial", size=10, color="1E293B")
        bold_font = Font(name="Arial", size=10, bold=True, color="0F172A")

        center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
        left_align = Alignment(horizontal="left", vertical="center", wrap_text=True)

        thin_border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        _apply_kop_surat(
            ws,
            "REKAPITULASI CAPAIAN & PREDIKAT TAHSIN - TAHFIDZ MURID",
            f"Tahun Ajaran: {ta_str} (Semester {sem_str})  |  Kelas Binaan: {kelas_info}  |  Dicetak: {tgl_cetak}"
        )

        header_row = 5
        ws.row_dimensions[header_row].height = 30
        for col_idx, col_name in enumerate(EXPORT_COLUMNS, start=1):
            cell = ws.cell(row=header_row, column=col_idx, value=col_name)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_align
            cell.border = thin_border

        center_cols = {1, 2, 4, 5, 7, 8, 11, 12, 14, 16}
        if rows:
            for r_offset, row_data in enumerate(rows):
                r_idx = header_row + 1 + r_offset
                ws.row_dimensions[r_idx].height = 24
                is_even = (r_offset % 2 == 1)

                for c_idx, col_name in enumerate(EXPORT_COLUMNS, start=1):
                    val = row_data.get(col_name, "-")
                    cell = ws.cell(row=r_idx, column=c_idx, value=val)
                    cell.border = thin_border
                    cell.font = bold_font if c_idx in {3, 8, 12, 14} else neutral_font
                    cell.alignment = center_align if c_idx in center_cols else left_align

                    if is_even:
                        cell.fill = zebra_fill

                    if col_name == "Status Kelulusan":
                        if val == "Lulus":
                            cell.fill = lulus_fill
                            cell.font = lulus_font
                        elif val == "Tidak Lulus":
                            cell.fill = gagal_fill
                            cell.font = gagal_font
            ws.auto_filter.ref = f"A{header_row}:{get_column_letter(len(EXPORT_COLUMNS))}{header_row + len(rows)}"
        else:
            ws.merge_cells(start_row=6, start_column=1, end_row=6, end_column=len(EXPORT_COLUMNS))
            empty_cell = ws.cell(row=6, column=1, value="Belum ada data murid pada kelas binaan ini.")
            empty_cell.alignment = center_align
            empty_cell.font = Font(name="Arial", size=9, italic=True, color="64748B")
            ws.row_dimensions[6].height = 26

        col_widths = [6, 16, 28, 10, 14, 28, 14, 13, 24, 28, 14, 13, 24, 16, 24, 18]
        for idx, width in enumerate(col_widths, start=1):
            ws.column_dimensions[get_column_letter(idx)].width = width
        ws.freeze_panes = "D6"
        _configure_print_landscape(ws)

        # Sheet 2: Riwayat Setoran
        ws_log = wb.create_sheet(title="Riwayat_Setoran")
        _apply_kop_surat(
            ws_log,
            "LOG RIWAYAT SETORAN TAHSIN & TAHFIDZ MURID",
            f"Tahun Ajaran: {ta_str} (Semester {sem_str})  |  Kelas Binaan: {kelas_info}  |  Dicetak: {tgl_cetak}"
        )

        log_headers = [
            "No", "Tanggal", "NISN / ID", "Nama Murid", "Kelas",
            "Program", "Materi / Surah / Halaman", "Grade", "Status",
            "Catatan Musyrif", "Penilai", "Paraf Ortu", "Catatan Ortu"
        ]
        ws_log.row_dimensions[5].height = 28
        for col_idx, h_text in enumerate(log_headers, start=1):
            c = ws_log.cell(row=5, column=col_idx, value=h_text)
            c.fill = header_fill
            c.font = header_font
            c.alignment = center_align
            c.border = thin_border

        log_row_idx = 6
        for s in siswa_list:
            for t in s.tahsin:
                vals = [
                    log_row_idx - 5, t.tanggal, s.id, s.nama, s.kelas,
                    "Tahsin", t.halaman_akhir, t.grade, t.status_lulus,
                    t.catatan or "-", t.penilai or "-",
                    "Sudah" if t.ceklist_ortu else "Belum", t.catatan_ortu or "-"
                ]
                ws_log.row_dimensions[log_row_idx].height = 22
                for c_i, v in enumerate(vals, start=1):
                    cell = ws_log.cell(row=log_row_idx, column=c_i, value=v)
                    cell.font = neutral_font
                    cell.border = thin_border
                    cell.alignment = center_align if c_i in {1, 2, 3, 5, 6, 8, 9, 12} else left_align
                log_row_idx += 1

            for f in s.tahfidz:
                vals = [
                    log_row_idx - 5, f.tanggal, s.id, s.nama, s.kelas,
                    "Tahfidz", f.hafalan_terakhir, f.grade, f.status_lulus,
                    f.catatan or "-", f.penilai or "-",
                    "Sudah" if f.ceklist_ortu else "Belum", f.catatan_ortu or "-"
                ]
                ws_log.row_dimensions[log_row_idx].height = 22
                for c_i, v in enumerate(vals, start=1):
                    cell = ws_log.cell(row=log_row_idx, column=c_i, value=v)
                    cell.font = neutral_font
                    cell.border = thin_border
                    cell.alignment = center_align if c_i in {1, 2, 3, 5, 6, 8, 9, 12} else left_align
                log_row_idx += 1

        if log_row_idx == 6:
            ws_log.merge_cells(start_row=6, start_column=1, end_row=6, end_column=len(log_headers))
            c_empty = ws_log.cell(row=6, column=1, value="Belum ada riwayat transaksi setoran Tahsin maupun Tahfidz.")
            c_empty.alignment = center_align
            c_empty.font = Font(name="Arial", size=9, italic=True, color="64748B")
            ws_log.row_dimensions[6].height = 26
        else:
            ws_log.auto_filter.ref = f"A5:{get_column_letter(len(log_headers))}{log_row_idx - 1}"

        log_widths = [6, 14, 16, 26, 10, 12, 30, 10, 15, 32, 18, 12, 28]
        for idx, width in enumerate(log_widths, start=1):
            ws_log.column_dimensions[get_column_letter(idx)].width = width
        ws_log.freeze_panes = "A6"
        _configure_print_landscape(ws_log)

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        filename = f"Laporan_Murid_SDIT_{datetime.now().strftime('%Y%m%d')}.xlsx"
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        flash(f'Export Excel gagal: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('guru.dashboard'))


@export_bp.route('/export_master_excel')
@role_required('admin')
def export_master_excel():
    try:
        guru_list = User.query.filter_by(role='guru').order_by(User.id.asc()).all()
        siswa_list = Siswa.query.order_by(Siswa.kelas.asc(), Siswa.nama.asc()).all()

        ta_str = AppSetting.get_val('tahun_ajaran', '2026/2027')
        sem_str = AppSetting.get_val('semester', 'Ganjil')
        tgl_cetak = datetime.now().strftime("%d/%m/%Y %H:%M WIB")
        info_banner = f"Tahun Ajaran: {ta_str} (Semester {sem_str})  |  Kurikulum Metode Ummi  |  Dicetak Admin: {tgl_cetak}"

        wb = openpyxl.Workbook()

        # Styling Umum
        subtitle_font = Font(name="Arial", size=10, bold=True, color="0F172A")
        info_font = Font(name="Arial", size=9, italic=True, color="64748B")

        header_emerald = PatternFill(start_color="059669", end_color="059669", fill_type="solid")
        header_slate = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
        total_fill = PatternFill(start_color="ECFDF5", end_color="ECFDF5", fill_type="solid")
        header_font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
        zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

        lulus_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
        lulus_font = Font(name="Arial", size=10, bold=True, color="166534")
        gagal_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
        gagal_font = Font(name="Arial", size=10, bold=True, color="991B1B")
        muted_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
        muted_font = Font(name="Arial", size=10, italic=True, color="64748B")

        neutral_font = Font(name="Arial", size=10, color="1E293B")
        bold_font = Font(name="Arial", size=10, bold=True, color="0F172A")
        total_font = Font(name="Arial", size=10, bold=True, color="065F46")

        center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
        left_align = Alignment(horizontal="left", vertical="center", wrap_text=True)
        thin_border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        # =========================================================
        # SHEET 1: RINGKASAN EKSEKUTIF SEKOLAH & PER ROMBEL
        # =========================================================
        ws_sum = wb.active
        ws_sum.title = "Ringkasan_Sekolah"
        _apply_kop_surat(
            ws_sum,
            "REKAPITULASI MASTER DATA GURU, MURID & CAPAIAN AL-QUR'AN",
            info_banner
        )

        total_guru_aktif = sum(1 for g in guru_list if (g.status or 'Aktif') == 'Aktif')
        total_siswa_aktif = sum(1 for s in siswa_list if s.status_clean == 'Aktif')
        total_tahsin = sum(len(s.tahsin) for s in siswa_list)
        total_tahfidz = sum(len(s.tahfidz) for s in siswa_list)
        total_lulus = sum(1 for s in siswa_list if s.status_kelulusan_rata_rata == 'Lulus')
        total_bimbingan = sum(1 for s in siswa_list if s.status_kelulusan_rata_rata == 'Tidak Lulus')
        total_belum = len(siswa_list) - total_lulus - total_bimbingan
        pct_lulus = round((total_lulus / len(siswa_list) * 100), 1) if siswa_list else 0.0

        kpi_rows = [
            ("Total Guru & Musyrif Terdaftar", f"{len(guru_list)} Guru ({total_guru_aktif} Aktif Mengajar)"),
            ("Total Murid Terdaftar", f"{len(siswa_list)} Murid ({total_siswa_aktif} Aktif)"),
            ("Total Transaksi Setoran Tahsin", f"{total_tahsin} Kali Evaluasi"),
            ("Total Transaksi Setoran Tahfidz", f"{total_tahfidz} Kali Setoran"),
            ("Murid Lulus Standar Minimal (Grade A / B+ / B)", f"{total_lulus} Murid ({pct_lulus}%)"),
            ("Murid Perlu Bimbingan (Grade C / ≥5x C)", f"{total_bimbingan} Murid"),
            ("Murid Belum Memiliki Penilaian", f"{total_belum} Murid"),
        ]

        ws_sum.cell(row=5, column=1, value="INDIKATOR STATISTIK SEKOLAH").fill = header_slate
        ws_sum.cell(row=5, column=1).font = header_font
        ws_sum.cell(row=5, column=1).alignment = left_align
        ws_sum.cell(row=5, column=2, value="JUMLAH / CAPAIAN").fill = header_slate
        ws_sum.cell(row=5, column=2).font = header_font
        ws_sum.cell(row=5, column=2).alignment = center_align
        ws_sum.row_dimensions[5].height = 26

        for idx, (label, val) in enumerate(kpi_rows, start=6):
            ws_sum.row_dimensions[idx].height = 22
            c1 = ws_sum.cell(row=idx, column=1, value=label)
            c2 = ws_sum.cell(row=idx, column=2, value=val)
            c1.font = neutral_font
            c2.font = bold_font
            c1.alignment = left_align
            c2.alignment = center_align
            c1.border = thin_border
            c2.border = thin_border
            if idx % 2 == 1:
                c1.fill = zebra_fill
                c2.fill = zebra_fill

        # Tabel Rekap Per Rombel / Kelas
        ws_sum['A14'] = "REKAPITULASI CAPAIAN PER ROMBEL / KELAS"
        ws_sum['A14'].font = subtitle_font
        ws_sum.row_dimensions[14].height = 22

        kelas_headers = ["No", "Kelas", "Musyrif / Guru Pembina", "Jumlah Murid", "Murid Lulus", "Perlu Bimbingan", "Belum Dinilai"]
        ws_sum.row_dimensions[15].height = 28
        for c_i, h_t in enumerate(kelas_headers, start=1):
            c = ws_sum.cell(row=15, column=c_i, value=h_t)
            c.fill = header_emerald
            c.font = header_font
            c.alignment = center_align
            c.border = thin_border

        kelas_guru_map = {}
        for g in guru_list:
            if g.kelas and g.kelas != '-':
                for k in [x.strip().upper() for x in g.kelas.replace('/', ',').replace(';', ',').split(',') if x.strip()]:
                    kelas_guru_map[k] = g.nama or g.username

        all_kelas_set = sorted(list({s.kelas.upper() for s in siswa_list if s.kelas} | set(kelas_guru_map.keys())))
        start_kls_row = 16
        for idx, kls in enumerate(all_kelas_set, start=1):
            r_i = start_kls_row + idx - 1
            ws_sum.row_dimensions[r_i].height = 22
            s_kls = [s for s in siswa_list if (s.kelas or '').upper() == kls]
            cnt_lulus = sum(1 for s in s_kls if s.status_kelulusan_rata_rata == 'Lulus')
            cnt_gagal = sum(1 for s in s_kls if s.status_kelulusan_rata_rata == 'Tidak Lulus')
            cnt_belum = len(s_kls) - cnt_lulus - cnt_gagal

            row_vals = [idx, kls, kelas_guru_map.get(kls, "-"), len(s_kls), cnt_lulus, cnt_gagal, cnt_belum]
            for c_i, v in enumerate(row_vals, start=1):
                cell = ws_sum.cell(row=r_i, column=c_i, value=v)
                cell.border = thin_border
                cell.font = bold_font if c_i in {2, 5} else neutral_font
                cell.alignment = left_align if c_i == 3 else center_align
                if idx % 2 == 0:
                    cell.fill = zebra_fill

        end_kls_row = start_kls_row + len(all_kelas_set) - 1
        total_row_idx = end_kls_row + 1 if all_kelas_set else start_kls_row
        ws_sum.row_dimensions[total_row_idx].height = 25

        ws_sum.merge_cells(start_row=total_row_idx, start_column=1, end_row=total_row_idx, end_column=3)
        ws_sum.cell(row=total_row_idx, column=1, value="TOTAL KESELURUHAN SEKOLAH").alignment = center_align
        for c_i in range(1, 8):
            tc = ws_sum.cell(row=total_row_idx, column=c_i)
            tc.fill = total_fill
            tc.font = total_font
            tc.border = thin_border
            if c_i >= 4:
                col_ltr = get_column_letter(c_i)
                tc.value = f"=SUM({col_ltr}{start_kls_row}:{col_ltr}{end_kls_row})" if all_kelas_set else 0
                tc.alignment = center_align

        # Blok Pengesahan / Tanda Tangan
        sign_start = total_row_idx + 3
        ws_sum.cell(row=sign_start, column=1, value="Mengetahui,").font = neutral_font
        ws_sum.cell(row=sign_start + 1, column=1, value="Kepala Sekolah SDIT Bina Mulia").font = bold_font
        ws_sum.cell(row=sign_start + 5, column=1, value="( .................................................. )").font = bold_font

        ws_sum.cell(row=sign_start, column=5, value=f"Depok, {datetime.now().strftime('%d %B %Y')}").font = neutral_font
        ws_sum.cell(row=sign_start + 1, column=5, value="Koordinator Tahsin & Tahfidz Al-Qur'an").font = bold_font
        ws_sum.cell(row=sign_start + 5, column=5, value="( .................................................. )").font = bold_font

        sum_widths = [44, 28, 32, 16, 16, 18, 16]
        for i, w in enumerate(sum_widths, start=1):
            ws_sum.column_dimensions[get_column_letter(i)].width = w
        _configure_print_landscape(ws_sum)

        # =========================================================
        # SHEET 2: DATA GURU & MUSYRIF
        # =========================================================
        ws_guru = wb.create_sheet(title="Data_Guru_Musyrif")
        _apply_kop_surat(
            ws_guru,
            "DAFTAR AKUN GURU & MUSYRIF AL-QUR'AN",
            info_banner
        )

        guru_headers = ["No", "ID Staf", "Nama Lengkap Guru / Musyrif", "Username Login", "Kelas Binaan", "Jml Murid Binaan", "Status Akun"]
        ws_guru.row_dimensions[5].height = 28
        for c_i, h_t in enumerate(guru_headers, start=1):
            c = ws_guru.cell(row=5, column=c_i, value=h_t)
            c.fill = header_slate
            c.font = header_font
            c.alignment = center_align
            c.border = thin_border

        if guru_list:
            for idx, g in enumerate(guru_list, start=1):
                r_i = 5 + idx
                ws_guru.row_dimensions[r_i].height = 23
                g_classes = [x.strip().upper() for x in (g.kelas or '').replace('/', ',').replace(';', ',').split(',') if x.strip() and x.strip() != '-']
                jml_binaan = sum(1 for s in siswa_list if (s.kelas or '').upper() in g_classes)
                g_status = g.status or 'Aktif'
                staf_code = f"G-{idx:04d}"

                vals = [idx, staf_code, g.nama or '-', g.username, g.kelas or '-', jml_binaan, g_status]
                for c_i, v in enumerate(vals, start=1):
                    cell = ws_guru.cell(row=r_i, column=c_i, value=v)
                    cell.border = thin_border
                    cell.font = bold_font if c_i == 3 else neutral_font
                    cell.alignment = left_align if c_i in {3, 4, 5} else center_align
                    if idx % 2 == 0:
                        cell.fill = zebra_fill
                    if c_i == 7:
                        cell.fill = lulus_fill if g_status == 'Aktif' else gagal_fill
                        cell.font = lulus_font if g_status == 'Aktif' else gagal_font
            ws_guru.auto_filter.ref = f"A5:{get_column_letter(len(guru_headers))}{5 + len(guru_list)}"
        else:
            ws_guru.merge_cells(start_row=6, start_column=1, end_row=6, end_column=len(guru_headers))
            c_e = ws_guru.cell(row=6, column=1, value="Belum ada data guru terdaftar.")
            c_e.alignment = center_align
            c_e.font = info_font

        guru_widths = [6, 14, 34, 22, 22, 18, 16]
        for i, w in enumerate(guru_widths, start=1):
            ws_guru.column_dimensions[get_column_letter(i)].width = w
        ws_guru.freeze_panes = "A6"
        _configure_print_landscape(ws_guru)

        # =========================================================
        # SHEET 3: DATA CAPAIAN SELURUH MURID
        # =========================================================
        ws_siswa = wb.create_sheet(title="Data_Capaian_Murid")
        _apply_kop_surat(
            ws_siswa,
            "DATA INDUK & CAPAIAN PREDIKAT SELURUH MURID",
            info_banner
        )

        master_siswa_cols = [
            "No", "NISN / ID", "Nama Murid", "Username Wali", "Kelas", "Status Murid",
            "Setoran Terakhir", "Materi Tahsin Terakhir", "Jml Tahsin", "Grade Tahsin", "Predikat Tahsin",
            "Hafalan Tahfidz Terakhir", "Jml Tahfidz", "Grade Tahfidz", "Predikat Tahfidz",
            "Grade Akhir", "Predikat Akhir", "Status Kelulusan"
        ]
        ws_siswa.row_dimensions[5].height = 28
        for c_i, h_t in enumerate(master_siswa_cols, start=1):
            c = ws_siswa.cell(row=5, column=c_i, value=h_t)
            c.fill = header_emerald
            c.font = header_font
            c.alignment = center_align
            c.border = thin_border

        center_s_cols = {1, 2, 5, 6, 7, 9, 10, 13, 14, 16, 18}
        if siswa_list:
            for idx, s in enumerate(siswa_list, start=1):
                r_i = 5 + idx
                ws_siswa.row_dimensions[r_i].height = 23
                ortu_uname = getattr(s, 'ortu_username', None) or (s.ortu.username if getattr(s, 'ortu', None) else '-')
                last_tahsin = s.tahsin[-1].halaman_akhir if s.tahsin else "-"
                last_tahfidz = s.tahfidz[-1].hafalan_terakhir if s.tahfidz else "-"
                latest_info = getattr(s, 'latest_setoran', None)
                tgl_terakhir = latest_info['tanggal'] if latest_info else "-"

                g_tahsin = s.grade_tahsin
                g_tahfidz = s.grade_tahfidz
                g_akhir = s.grade_rata_rata
                st_lulus = s.status_kelulusan_rata_rata
                st_murid = s.status_clean

                vals = [
                    idx, s.id, s.nama, ortu_uname, s.kelas, st_murid,
                    tgl_terakhir, last_tahsin, len(s.tahsin), g_tahsin, _get_predikat_desc(s, 'predikat_tahsin_desc', g_tahsin),
                    last_tahfidz, len(s.tahfidz), g_tahfidz, _get_predikat_desc(s, 'predikat_tahfidz_desc', g_tahfidz),
                    g_akhir, _get_predikat_desc(s, 'predikat_rata_rata_desc', g_akhir), st_lulus
                ]
                for c_i, v in enumerate(vals, start=1):
                    cell = ws_siswa.cell(row=r_i, column=c_i, value=v)
                    cell.border = thin_border
                    cell.font = bold_font if c_i in {3, 10, 14, 16} else neutral_font
                    cell.alignment = center_align if c_i in center_s_cols else left_align
                    if idx % 2 == 0:
                        cell.fill = zebra_fill

                    if c_i == 6:
                        cell.fill = lulus_fill if st_murid == 'Aktif' else gagal_fill
                        cell.font = lulus_font if st_murid == 'Aktif' else gagal_font
                    elif c_i == 18:
                        if st_lulus == "Lulus":
                            cell.fill = lulus_fill
                            cell.font = lulus_font
                        elif st_lulus == "Tidak Lulus":
                            cell.fill = gagal_fill
                            cell.font = gagal_font
                        else:
                            cell.fill = muted_fill
                            cell.font = muted_font
            ws_siswa.auto_filter.ref = f"A5:{get_column_letter(len(master_siswa_cols))}{5 + len(siswa_list)}"
        else:
            ws_siswa.merge_cells(start_row=6, start_column=1, end_row=6, end_column=len(master_siswa_cols))
            c_e = ws_siswa.cell(row=6, column=1, value="Belum ada data murid terdaftar.")
            c_e.alignment = center_align
            c_e.font = info_font

        siswa_widths = [6, 15, 28, 18, 9, 13, 15, 26, 11, 13, 22, 26, 11, 13, 22, 13, 22, 18]
        for i, w in enumerate(siswa_widths, start=1):
            ws_siswa.column_dimensions[get_column_letter(i)].width = w
        ws_siswa.freeze_panes = "D6"
        _configure_print_landscape(ws_siswa)

        # =========================================================
        # SHEET 4: RIWAYAT SETORAN SEMUA MURID
        # =========================================================
        ws_log = wb.create_sheet(title="Riwayat_Setoran_Semua")
        _apply_kop_surat(
            ws_log,
            "LOG RIWAYAT SETORAN TAHSIN & TAHFIDZ SELURUH MURID",
            info_banner
        )

        log_headers = [
            "No", "Tanggal", "NISN / ID", "Nama Murid", "Kelas",
            "Program", "Materi / Surah / Halaman", "Grade", "Status",
            "Catatan Musyrif", "Penilai", "Paraf Ortu", "Catatan Ortu"
        ]
        ws_log.row_dimensions[5].height = 28
        for c_i, h_t in enumerate(log_headers, start=1):
            c = ws_log.cell(row=5, column=c_i, value=h_t)
            c.fill = header_slate
            c.font = header_font
            c.alignment = center_align
            c.border = thin_border

        log_row_idx = 6
        for s in siswa_list:
            for t in s.tahsin:
                vals = [
                    log_row_idx - 5, t.tanggal, s.id, s.nama, s.kelas,
                    "Tahsin", t.halaman_akhir, t.grade, t.status_lulus,
                    t.catatan or "-", t.penilai or "-",
                    "Sudah" if t.ceklist_ortu else "Belum", t.catatan_ortu or "-"
                ]
                ws_log.row_dimensions[log_row_idx].height = 22
                for c_i, v in enumerate(vals, start=1):
                    cell = ws_log.cell(row=log_row_idx, column=c_i, value=v)
                    cell.font = neutral_font
                    cell.border = thin_border
                    cell.alignment = center_align if c_i in {1, 2, 3, 5, 6, 8, 9, 12} else left_align
                log_row_idx += 1

            for f in s.tahfidz:
                vals = [
                    log_row_idx - 5, f.tanggal, s.id, s.nama, s.kelas,
                    "Tahfidz", f.hafalan_terakhir, f.grade, f.status_lulus,
                    f.catatan or "-", f.penilai or "-",
                    "Sudah" if f.ceklist_ortu else "Belum", f.catatan_ortu or "-"
                ]
                ws_log.row_dimensions[log_row_idx].height = 22
                for c_i, v in enumerate(vals, start=1):
                    cell = ws_log.cell(row=log_row_idx, column=c_i, value=v)
                    cell.font = neutral_font
                    cell.border = thin_border
                    cell.alignment = center_align if c_i in {1, 2, 3, 5, 6, 8, 9, 12} else left_align
                log_row_idx += 1

        if log_row_idx == 6:
            ws_log.merge_cells(start_row=6, start_column=1, end_row=6, end_column=len(log_headers))
            c_e = ws_log.cell(row=6, column=1, value="Belum ada riwayat setoran Tahsin maupun Tahfidz yang tercatat.")
            c_e.alignment = center_align
            c_e.font = info_font
            ws_log.row_dimensions[6].height = 26
        else:
            ws_log.auto_filter.ref = f"A5:{get_column_letter(len(log_headers))}{log_row_idx - 1}"

        log_widths = [6, 14, 16, 26, 10, 12, 30, 10, 15, 32, 18, 12, 28]
        for i, w in enumerate(log_widths, start=1):
            ws_log.column_dimensions[get_column_letter(i)].width = w
        ws_log.freeze_panes = "A6"
        _configure_print_landscape(ws_log)

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        filename = f"Rekap_Master_SDIT_Bina_Mulia_{datetime.now().strftime('%Y%m%d')}.xlsx"
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        flash(f'Gagal mengekspor Rekap Master Excel: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('admin.dashboard_admin'))


@export_bp.route('/export_csv')
@role_required('guru', 'admin')
def export_csv():
    try:
        siswa_list = _get_filtered_siswa()
        df = pd.DataFrame(_build_export_rows(siswa_list), columns=EXPORT_COLUMNS)
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        return Response(
            buffer.getvalue().encode('utf-8-sig'),
            mimetype='text/csv',
            headers={"Content-Disposition": "attachment; filename=Laporan_Murid_SDIT.csv"}
        )
    except Exception as e:
        flash(f'Export CSV gagal: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('guru.dashboard'))


@export_bp.route('/export_pdf')
@role_required('guru', 'admin')
def export_pdf():
    siswa_list = _get_filtered_siswa()
    ta_str = AppSetting.get_val('tahun_ajaran', '2026/2027')
    sem_str = AppSetting.get_val('semester', 'Ganjil')
    return render_template(
        'reports/laporansemua.html',
        siswa_list=siswa_list,
        tanggal=datetime.now().strftime("%d/%m/%Y"),
        tahun_ajaran=ta_str,
        semester=sem_str,
        tahun_ajaran_full=f"Tahun Ajaran {ta_str} – Semester {sem_str}"
    )