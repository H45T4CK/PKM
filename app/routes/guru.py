from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from app.models.siswa import Siswa, PREDIKAT_LABELS
from app.models.user import User, AppSetting
from app.models.record import RecordsTahsin, RecordsTahfidz
from app import db
from app.utils.decorators import role_required
from datetime import datetime
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as ExcelImage
from openpyxl.worksheet.datavalidation import DataValidation
import io, os, re


def extract_nama_depan(nama):
    if not nama:
        return 'murid'
    words = [re.sub(r'[^a-zA-Z0-9]', '', w) for w in str(nama).split() if re.sub(r'[^a-zA-Z0-9]', '', w)]
    if words:
        return words[0].lower()
    return 'murid'


def generate_unique_ortu_username(nama, custom_id=''):
    nama_depan = extract_nama_depan(nama)
    base_username = re.sub(r'[^a-zA-Z0-9_]', '', nama_depan).lower() or 'murid'

    # Bersihkan akun 'ortu' yatim (tidak punya data siswa) yang memakai base_username atau turunannya
    orphan_candidates = User.query.filter(
        User.role == 'ortu',
        db.func.lower(User.username).like(f"{base_username}%")
    ).all()
    for u in orphan_candidates:
        if len(u.siswa_binaan) == 0:
            db.session.delete(u)
    db.session.flush()

    # Cek ketersediaan username dasar
    if not User.query.filter(db.func.lower(User.username) == base_username).first():
        return base_username

    # Jika memang dipakai murid aktif lain yang namanya sama, tambahkan sufiks unik
    clean_id_suffix = re.sub(r'[^a-zA-Z0-9]', '', str(custom_id)).lower()
    if clean_id_suffix:
        suffix = clean_id_suffix[-3:] if len(clean_id_suffix) >= 3 else clean_id_suffix
        cand = f"{base_username}_{suffix}"
        if not User.query.filter(db.func.lower(User.username) == cand).first():
            return cand

    counter = 1
    while True:
        cand = f"{base_username}_{counter}"
        if not User.query.filter(db.func.lower(User.username) == cand).first():
            return cand
        counter += 1


def calc_class_avg_grade(grade_list):
    weights_map = {'A': 4.0, 'B+': 3.0, 'B': 2.0, 'C': 1.0}
    valid = [weights_map[g] for g in grade_list if g in weights_map]
    if not valid:
        return '-', 'Belum Ada Penilaian'
    avg = sum(valid) / len(valid)
    if avg >= 3.5:
        g = 'A'
    elif avg >= 2.5:
        g = 'B+'
    elif avg >= 1.5:
        g = 'B'
    else:
        g = 'C'
    return g, PREDIKAT_LABELS.get(g, '-')


guru_bp = Blueprint('guru', __name__)

GRADE_MAP = {
    'A': (100, 'Lulus'),
    'B+': (88, 'Lulus'),
    'B': (78, 'Lulus'),
    'C': (60, 'Tidak Lulus')
}


@guru_bp.route('/dashboard_guru')
@role_required('guru')
def dashboard():
    q = request.args.get('q', '').strip().lower()
    kelas_filter = request.args.get('kelas_filter', '').strip()
    status_filter = request.args.get('status_filter', '').strip()

    query = Siswa.query

    guru_kelas_str = session.get('kelas', '').strip()
    guru_classes = [c.strip().upper() for c in guru_kelas_str.replace('/', ',').replace(';', ',').split(',') if c.strip() and c.strip() != '-']

    if kelas_filter and kelas_filter.lower() != 'all':
        query = query.filter(db.func.upper(Siswa.kelas) == kelas_filter.upper())
    elif guru_classes:
        query = query.filter(db.func.upper(Siswa.kelas).in_(guru_classes))

    if status_filter and status_filter.lower() != 'all':
        query = query.filter(db.func.lower(Siswa.status) == status_filter.lower())

    if q:
        query = query.filter(
            (db.func.lower(Siswa.nama).contains(q)) |
            (db.func.lower(Siswa.id).contains(q)) |
            (db.func.lower(Siswa.kelas).contains(q))
        )

    siswa_list = query.all()

    all_classes = guru_classes if guru_classes else [c[0].upper() for c in db.session.query(Siswa.kelas).distinct().all() if c[0]]
    all_classes = sorted(list(set(all_classes)))

    siswa_ids = [s.id for s in siswa_list]
    if siswa_ids:
        tahfidz_records = RecordsTahfidz.query.filter(RecordsTahfidz.siswa_id.in_(siswa_ids)).all()
        tahsin_records = RecordsTahsin.query.filter(RecordsTahsin.siswa_id.in_(siswa_ids)).all()
    else:
        tahfidz_records = []
        tahsin_records = []

    # Distribusi grade untuk grafik ApexCharts & KPI murni huruf
    grade_distribution = {'A': 0, 'B+': 0, 'B': 0, 'C': 0}
    tahsin_grades = []
    tahfidz_grades = []
    overall_grades = []
    lulus_cnt = 0
    belum_cnt = 0

    for s in siswa_list:
        if s.grade_tahsin != '-':
            tahsin_grades.append(s.grade_tahsin)
        if s.grade_tahfidz != '-':
            tahfidz_grades.append(s.grade_tahfidz)

        g = s.grade_rata_rata
        if g != '-':
            overall_grades.append(g)
            if s.status_kelulusan_rata_rata == 'Lulus':
                lulus_cnt += 1
            else:
                belum_cnt += 1

        if g in grade_distribution:
            grade_distribution[g] += 1
        elif g in ['D', 'E']:
            grade_distribution['C'] += 1

    class_grade_tahsin, class_desc_tahsin = calc_class_avg_grade(tahsin_grades)
    class_grade_tahfidz, class_desc_tahfidz = calc_class_avg_grade(tahfidz_grades)
    class_grade_overall, class_desc_overall = calc_class_avg_grade(overall_grades)

    return render_template(
        'guru/dashboard_guru.html',
        siswa_list=siswa_list,
        now_date=datetime.now().strftime("%Y-%m-%d"),
        total_tahfidz_rec=len(tahfidz_records),
        total_tahsin_rec=len(tahsin_records),
        tahsin_assessed_cnt=len(tahsin_grades),
        tahfidz_assessed_cnt=len(tahfidz_grades),
        class_grade_tahsin=class_grade_tahsin,
        class_desc_tahsin=class_desc_tahsin,
        class_grade_tahfidz=class_grade_tahfidz,
        class_desc_tahfidz=class_desc_tahfidz,
        class_grade_overall=class_grade_overall,
        class_desc_overall=class_desc_overall,
        lulus_cnt=lulus_cnt,
        belum_cnt=belum_cnt,
        guru_classes=guru_classes,
        all_classes=all_classes,
        active_kelas_filter=kelas_filter,
        active_status_filter=status_filter,
        grade_dist=grade_distribution
    )


@guru_bp.route('/tambah_siswa', methods=['POST'])
@role_required('guru')
def tambah_siswa():
    nama = request.form.get('nama', '').strip()
    custom_id = request.form.get('nisn', '').strip()
    status = request.form.get('status', 'Aktif')

    if not nama:
        flash('Nama murid wajib diisi!', 'danger')
        return redirect(request.referrer or url_for('guru.dashboard'))

    kelas_pilihan = request.form.get('kelas', '').strip().upper()
    if not kelas_pilihan:
        guru_kelas = session.get('kelas', '1A').strip()
        first_k = [c.strip().upper() for c in guru_kelas.split(',') if c.strip()]
        kelas_pilihan = first_k[0] if first_k else '1A'

    if not custom_id:
        count = Siswa.query.count()
        idx = count + 1
        custom_id = f"S{idx:03d}"
        while Siswa.query.get(custom_id):
            idx += 1
            custom_id = f"S{idx:03d}"
    else:
        if Siswa.query.get(custom_id):
            flash(f'NISN / ID "{custom_id}" sudah terdaftar pada murid lain!', 'danger')
            return redirect(request.referrer or url_for('guru.dashboard'))

    try:
        user_cand = generate_unique_ortu_username(nama, custom_id)

        ortu = User(username=user_cand, role='ortu', nama=f"Wali {nama}", kelas=kelas_pilihan, status=status)
        ortu.set_password(custom_id)
        db.session.add(ortu)
        db.session.flush()

        new_siswa = Siswa(id=custom_id, nama=nama, kelas=kelas_pilihan, poin=0, status=status, user_id_ortu=ortu.id)
        db.session.add(new_siswa)
        db.session.commit()

        flash(f'Data murid {nama} berhasil ditambahkan! (Username login: {user_cand}, Password: {custom_id})', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal menambahkan data murid: {str(e)}', 'danger')

    return redirect(request.referrer or url_for('guru.dashboard'))


@guru_bp.route('/edit_siswa/<id_siswa>', methods=['POST'])
@role_required('guru')
def edit_siswa(id_siswa):
    siswa = Siswa.query.get_or_404(id_siswa)
    nama = request.form.get('nama', '').strip()
    username = request.form.get('username', '').strip()
    kelas = request.form.get('kelas', '').strip().upper()
    status = request.form.get('status', 'Aktif')

    if not nama or not username:
        flash('Nama dan Username murid tidak boleh kosong!', 'danger')
        return redirect(url_for('guru.dashboard'))

    ortu = None
    if siswa.user_id_ortu:
        ortu = User.query.get(siswa.user_id_ortu)
    if not ortu:
        ortu = User.query.filter_by(username=siswa.nama, role='ortu').first()

    conflict_user = User.query.filter(
        (db.func.lower(User.username) == username.lower()) &
        (User.id != (ortu.id if ortu else 0))
    ).first()
    if conflict_user:
        flash(f'Username "{username}" sudah digunakan akun lain!', 'danger')
        return redirect(url_for('guru.dashboard'))

    siswa.nama = nama
    siswa.kelas = kelas
    siswa.status = status

    if not ortu:
        ortu = User(username=username, role='ortu', nama=f"Wali {nama}", kelas=kelas, status=status)
        ortu.set_password('1234')
        db.session.add(ortu)
        db.session.flush()
        siswa.user_id_ortu = ortu.id
    else:
        ortu.username = username
        ortu.nama = f"Wali {nama}"
        ortu.kelas = kelas
        ortu.status = status

    db.session.commit()
    flash(f'Data murid {nama} berhasil diperbarui!', 'success')
    return redirect(request.referrer or url_for('guru.dashboard'))


@guru_bp.route('/hapus_siswa/<id_siswa>')
@role_required('guru')
def hapus_siswa(id_siswa):
    siswa = Siswa.query.get_or_404(id_siswa)
    nama = siswa.nama
    ortu = siswa.ortu if siswa.user_id_ortu else None

    try:
        db.session.delete(siswa)
        db.session.flush()

        # Hapus juga akun wali murid terkait jika tidak membina murid lain
        if ortu and ortu.role == 'ortu' and len(ortu.siswa_binaan) == 0:
            db.session.delete(ortu)

        db.session.commit()
        flash(f'Data murid {nama} beserta akun loginnya berhasil dihapus dari sistem!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal menghapus data murid: {str(e)}', 'danger')

    return redirect(request.referrer or url_for('guru.dashboard'))


@guru_bp.route('/hapus_semua_siswa', methods=['POST'])
@role_required('guru')
def hapus_semua_siswa():
    konfirmasi = request.form.get('konfirmasi', '').strip().upper()
    kelas_target = request.form.get('kelas_target', 'ALL').strip().upper()

    if konfirmasi != 'HAPUS':
        flash('Konfirmasi tidak valid! Harap ketik kata "HAPUS" untuk menghapus data murid.', 'danger')
        return redirect(url_for('guru.dashboard'))

    guru_kelas_str = session.get('kelas', '').strip()
    guru_classes = [
        c.strip().upper()
        for c in guru_kelas_str.replace('/', ',').replace(';', ',').split(',')
        if c.strip() and c.strip() != '-'
    ]

    query = Siswa.query
    if kelas_target != 'ALL':
        if guru_classes and kelas_target not in guru_classes:
            flash(f'Anda tidak memiliki akses menghapus murid pada kelas {kelas_target}!', 'danger')
            return redirect(url_for('guru.dashboard'))
        query = query.filter(db.func.upper(Siswa.kelas) == kelas_target)
    elif guru_classes:
        query = query.filter(db.func.upper(Siswa.kelas).in_(guru_classes))

    target_siswa_list = query.all()
    if not target_siswa_list:
        flash('Tidak ada data murid yang dapat dihapus pada pilihan kelas tersebut.', 'warning')
        return redirect(url_for('guru.dashboard'))

    try:
        deleted_count = len(target_siswa_list)
        ortu_candidates = []

        for s in target_siswa_list:
            if s.user_id_ortu and s.ortu:
                ortu_candidates.append(s.ortu)
            db.session.delete(s)

        db.session.flush()

        seen_ortu_ids = set()
        for ortu in ortu_candidates:
            if ortu.id not in seen_ortu_ids:
                seen_ortu_ids.add(ortu.id)
                if ortu.role == 'ortu' and len(ortu.siswa_binaan) == 0:
                    db.session.delete(ortu)

        db.session.commit()
        label_kelas = f"Kelas {kelas_target}" if kelas_target != 'ALL' else "semua kelas binaan"
        flash(f'Berhasil menghapus {deleted_count} data murid ({label_kelas}) beserta riwayat setorannya!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal menghapus data murid: {str(e)}', 'danger')

    return redirect(request.referrer or url_for('guru.dashboard'))


@guru_bp.route('/toggle_status_siswa/<id_siswa>', methods=['POST', 'GET'])
@role_required('guru')
def toggle_status_siswa(id_siswa):
    siswa = Siswa.query.get_or_404(id_siswa)
    status_req = request.form.get('status') or request.args.get('status')
    if status_req:
        siswa.status = status_req
    else:
        siswa.status = 'Tidak Aktif' if siswa.status_clean == 'Aktif' else 'Aktif'
    db.session.commit()
    flash(f'Status murid {siswa.nama} berhasil diubah menjadi {siswa.status}!', 'success')
    return redirect(request.referrer or url_for('guru.dashboard'))


@guru_bp.route('/catat_tahsin/<id_siswa>', methods=['POST'])
@role_required('guru')
def catat_tahsin(id_siswa):
    s = Siswa.query.get_or_404(id_siswa)
    juz_pilihan = request.form.get('juz', '')
    surat_ayat = request.form.get('halaman_akhir', '-').strip()
    gabungan_halaman = f"{juz_pilihan} - {surat_ayat}" if juz_pilihan else surat_ayat

    grade_raw = request.form.get('grade', 'A').strip()
    grade = 'B+' if grade_raw.upper() == 'B+' else grade_raw.upper()
    default_nilai, default_lulus = GRADE_MAP.get(grade, (100, 'Lulus'))
    status_lulus = 'Lulus' if grade in ['A', 'B+', 'B'] else 'Tidak Lulus'

    tgl_raw = request.form.get('tanggal') or ''
    if tgl_raw and len(tgl_raw) >= 10 and tgl_raw[4] == '-' and tgl_raw[7] == '-':
        tgl_simpan = f"{tgl_raw[8:10]}/{tgl_raw[5:7]}/{tgl_raw[0:4]}"
    elif tgl_raw:
        tgl_simpan = tgl_raw
    else:
        tgl_simpan = datetime.now().strftime("%d/%m/%Y")

    rec = RecordsTahsin(
        siswa_id=s.id,
        tanggal=tgl_simpan,
        halaman_akhir=gabungan_halaman,
        catatan=request.form.get('catatan', ''),
        grade=grade,
        nilai=default_nilai,
        status_lulus=status_lulus,
        ceklist_guru=True,
        ceklist_ortu=bool(request.form.get('ceklist_ortu')),
        penilai=session.get('user', 'Musyrif')
    )
    db.session.add(rec)
    db.session.flush()

    if s.rata_rata_nilai is not None:
        s.poin = int(s.rata_rata_nilai)
    db.session.commit()

    flash(f'Penilaian Tahsin {s.nama} berhasil disimpan! Grade {grade} ({status_lulus})', 'success')
    return redirect(request.referrer or url_for('guru.dashboard'))


@guru_bp.route('/catat_tahfidz/<id_siswa>', methods=['POST'])
@role_required('guru')
def catat_tahfidz(id_siswa):
    s = Siswa.query.get_or_404(id_siswa)
    juz_pilihan = request.form.get('juz', '')
    surat_ayat = request.form.get('hafalan_terakhir', '-').strip()
    gabungan_hafalan = f"{juz_pilihan} - {surat_ayat}" if juz_pilihan else surat_ayat

    grade_raw = request.form.get('grade', 'A').strip()
    grade = 'B+' if grade_raw.upper() == 'B+' else grade_raw.upper()
    default_nilai, default_lulus = GRADE_MAP.get(grade, (100, 'Lulus'))
    status_lulus = 'Lulus' if grade in ['A', 'B+', 'B'] else 'Tidak Lulus'

    tgl_raw = request.form.get('tanggal') or ''
    if tgl_raw and len(tgl_raw) >= 10 and tgl_raw[4] == '-' and tgl_raw[7] == '-':
        tgl_simpan = f"{tgl_raw[8:10]}/{tgl_raw[5:7]}/{tgl_raw[0:4]}"
    elif tgl_raw:
        tgl_simpan = tgl_raw
    else:
        tgl_simpan = datetime.now().strftime("%d/%m/%Y")

    rec = RecordsTahfidz(
        siswa_id=s.id,
        tanggal=tgl_simpan,
        hafalan_terakhir=gabungan_hafalan,
        catatan=request.form.get('catatan', ''),
        grade=grade,
        nilai=default_nilai,
        status_lulus=status_lulus,
        ceklist_guru=True,
        ceklist_ortu=bool(request.form.get('ceklist_ortu')),
        penilai=session.get('user', 'Musyrif')
    )
    db.session.add(rec)
    db.session.flush()

    if s.rata_rata_nilai is not None:
        s.poin = int(s.rata_rata_nilai)
    db.session.commit()

    flash(f'Setoran Tahfidz {s.nama} berhasil disimpan! Grade {grade} ({status_lulus})', 'success')
    return redirect(request.referrer or url_for('guru.dashboard'))


@guru_bp.route('/hapus_tahsin/<int:rec_id>')
@role_required('guru')
def hapus_tahsin(rec_id):
    rec = RecordsTahsin.query.get_or_404(rec_id)
    siswa = rec.siswa
    db.session.delete(rec)
    db.session.flush()
    siswa.poin = int(siswa.rata_rata_nilai) if siswa.rata_rata_nilai is not None else 0
    db.session.commit()
    flash('Catatan Tahsin berhasil dihapus dari histori!', 'success')
    return redirect(request.referrer or url_for('guru.dashboard'))


@guru_bp.route('/hapus_tahfidz/<int:rec_id>')
@role_required('guru')
def hapus_tahfidz(rec_id):
    rec = RecordsTahfidz.query.get_or_404(rec_id)
    siswa = rec.siswa
    db.session.delete(rec)
    db.session.flush()
    siswa.poin = int(siswa.rata_rata_nilai) if siswa.rata_rata_nilai is not None else 0
    db.session.commit()
    flash('Setoran Tahfidz berhasil dihapus dari histori!', 'success')
    return redirect(request.referrer or url_for('guru.dashboard'))


@guru_bp.route('/template_murid')
@role_required('guru')
def template_murid():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Template_Murid_SDIT"

    ta_str = AppSetting.get_val('tahun_ajaran', '2026/2027')
    sem_str = AppSetting.get_val('semester', 'Ganjil')

    guru_kelas_str = session.get('kelas', '1A').strip()
    first_kelas = [c.strip().upper() for c in guru_kelas_str.replace('/', ',').replace(';', ',').split(',') if c.strip() and c.strip() != '-']
    default_kelas = first_kelas[0] if first_kelas else '1A'

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(base_dir, 'static', 'img', 'logo-sdit.png')
    if os.path.exists(logo_path):
        try:
            img = ExcelImage(logo_path)
            img.width = 46
            img.height = 46
            ws.add_image(img, 'A1')
        except Exception:
            pass

    title_font = Font(name="Arial", size=13, bold=True, color="059669")
    subtitle_font = Font(name="Arial", size=10, bold=True, color="1E293B")
    info_font = Font(name="Arial", size=9, italic=True, color="64748B")

    header_fill = PatternFill(start_color="059669", end_color="059669", fill_type="solid")
    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    data_font = Font(name="Arial", size=10)
    center_align = Alignment(horizontal="center", vertical="center")
    left_align = Alignment(horizontal="left", vertical="center")

    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    ws['B1'] = "SDIT BINA MULIA"
    ws['B1'].font = title_font

    ws['B2'] = "FORMAT RESMI IMPORT DATA MURID / SISWA"
    ws['B2'].font = subtitle_font

    ws['B3'] = f"Tahun Ajaran: {ta_str} (Semester {sem_str})  |  Kelas Binaan: {default_kelas}"
    ws['B3'].font = info_font

    ws['B4'] = "Catatan: Password siswa defaultnya adalah NISN dan usernamenya adalah nama depan siswa. Jangan mengubah nama kolom di baris 6!"
    ws['B4'].font = Font(name="Arial", size=9, italic=True, color="DC2626")

    ws.row_dimensions[1].height = 20
    ws.row_dimensions[2].height = 18

    headers = ["No", "NISN", "Nama Murid", "Kelas", "Jenis Kelamin", "Status"]
    for col_idx, header_text in enumerate(headers, start=1):
        cell = ws.cell(row=6, column=col_idx, value=header_text)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
        cell.border = thin_border
    ws.row_dimensions[6].height = 28

    for row_idx in range(7, 57):
        ws.row_dimensions[row_idx].height = 22
        ws.cell(row=row_idx, column=1, value=row_idx - 6).alignment = center_align
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.font = data_font
            cell.border = thin_border
            if col_idx in [1, 2, 4, 5, 6]:
                cell.alignment = center_align
            else:
                cell.alignment = left_align

    # Dropdown Pilihan Otomatis (Baris 7 - 56)
    kelas_opsi = ",".join(first_kelas) if first_kelas else "1A,1B,1C,1D,2A,2B,2C,2D,3A,3B,3C,3D,4A,4B,4C,4D,5A,5B,5C,5D,6A,6B,6C,6D"
    dv_kelas = DataValidation(type="list", formula1=f'"{kelas_opsi}"', allow_blank=True)
    dv_kelas.error = "Pilih kelas yang tersedia pada daftar dropdown."
    dv_kelas.errorTitle = "Kelas Tidak Valid"
    ws.add_data_validation(dv_kelas)
    dv_kelas.add("D7:D56")

    dv_jk = DataValidation(type="list", formula1='"Laki-laki,Perempuan"', allow_blank=True)
    dv_jk.error = "Pilih Laki-laki atau Perempuan dari daftar."
    dv_jk.errorTitle = "Pilihan Tidak Valid"
    ws.add_data_validation(dv_jk)
    dv_jk.add("E7:E56")

    dv_status = DataValidation(type="list", formula1='"Aktif,Tidak Aktif"', allow_blank=True)
    dv_status.error = "Pilih Aktif atau Tidak Aktif dari daftar."
    dv_status.errorTitle = "Status Tidak Valid"
    ws.add_data_validation(dv_status)
    dv_status.add("F7:F56")

    widths = [8, 20, 36, 14, 18, 16]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name="Template_Resmi_Import_Murid_SDIT_Bina_Mulia.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@guru_bp.route('/import_excel', methods=['POST'])
@role_required('guru')
def import_excel():
    file = request.files.get('file_excel')
    if file and file.filename.endswith(('.xlsx', '.xls')):
        try:
            df_raw = pd.read_excel(file, header=None)
            header_idx = 0
            for idx, r in df_raw.iterrows():
                row_vals = [str(v).strip().lower() for v in r.values if pd.notna(v)]
                has_nama_col = any(v in ['nama murid', 'nama lengkap', 'nama siswa', 'nama'] for v in row_vals)
                has_id_or_kelas = any(v in ['nisn', 'nis', 'kelas', 'rombel'] for v in row_vals)
                if has_nama_col and has_id_or_kelas:
                    header_idx = idx
                    break

            file.seek(0)
            df = pd.read_excel(file, skiprows=header_idx)
            imported_count = 0

            guru_kelas_str = session.get('kelas', '1A').strip()
            first_kelas = [c.strip().upper() for c in guru_kelas_str.replace('/', ',').replace(';', ',').split(',') if c.strip() and c.strip() != '-']
            default_kelas = first_kelas[0] if first_kelas else '1A'

            orig_cols = list(df.columns)
            col_map = {str(col).strip().lower(): col for col in orig_cols}

            def find_val(row, candidates, fallback=''):
                for c in candidates:
                    for clean_k, real_col in col_map.items():
                        if c == clean_k or c in clean_k:
                            val = str(row.get(real_col, '')).strip()
                            if val and val.lower() != 'nan':
                                return val
                return fallback

            for _, row in df.iterrows():
                nama = find_val(row, ['nama murid', 'nama lengkap', 'nama siswa', 'nama', 'student'])
                if not nama or nama.lower() == 'nan':
                    continue

                raw_kelas = find_val(row, ['kelas', 'rombel', 'class'], default_kelas)
                kelas = re.sub(r'\s+', '', raw_kelas).upper() if raw_kelas else default_kelas

                raw_custom_id = find_val(row, ['nisn', 'nis', 'id murid', 'id siswa', 'id'])
                if raw_custom_id and raw_custom_id.lower() != 'nan':
                    custom_id = re.sub(r'\.0$', '', raw_custom_id)
                else:
                    count = Siswa.query.count() + imported_count + 1
                    custom_id = f"S{count:03d}"
                    while Siswa.query.get(custom_id):
                        count += 1
                        custom_id = f"S{count:03d}"

                raw_status = find_val(row, ['status', 'keaktifan'], 'Aktif')
                status = 'Tidak Aktif' if 'tidak' in raw_status.lower() else 'Aktif'
                password_siswa = custom_id

                existing_siswa = Siswa.query.get(custom_id)
                if existing_siswa:
                    existing_siswa.nama = nama
                    existing_siswa.kelas = kelas
                    existing_siswa.status = status
                    if existing_siswa.ortu:
                        existing_siswa.ortu.nama = f"Wali {nama}"
                        existing_siswa.ortu.kelas = kelas
                        existing_siswa.ortu.status = status
                        existing_siswa.ortu.set_password(password_siswa)
                else:
                    user_cand = generate_unique_ortu_username(nama, custom_id)

                    ortu = User(username=user_cand, role='ortu', nama=f"Wali {nama}", kelas=kelas, status=status)
                    ortu.set_password(password_siswa)
                    db.session.add(ortu)
                    db.session.flush()

                    new_siswa = Siswa(id=custom_id, nama=nama, kelas=kelas, poin=0, status=status, user_id_ortu=ortu.id)
                    db.session.add(new_siswa)
                imported_count += 1

            db.session.commit()
            flash(f'Alhamdulillah, berhasil mengimpor {imported_count} data murid! (Username login: nama depan murid, Password: NISN)', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal memproses file Excel: {str(e)}', 'danger')
    else:
        flash('File tidak valid! Mohon unggah spreadsheet format .xlsx atau .xls', 'danger')
    return redirect(request.referrer or url_for('guru.dashboard'))