from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from app.models.user import User, AppSetting
from app.models.siswa import Siswa
from app import db
from app.utils.decorators import role_required
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as ExcelImage
import io, os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def parse_kelas_list(kelas_str):
    if not kelas_str or str(kelas_str).strip() in ['-', 'nan', 'None', '']:
        return []
    parts = str(kelas_str).replace(';', ',').replace('/', ',').split(',')
    cleaned = []
    for p in parts:
        c = p.strip().upper()
        if c and c != '-' and c not in cleaned:
            cleaned.append(c)
    return cleaned


def get_assigned_classes_map(exclude_guru_id=None):
    assigned = {}
    query = User.query.filter_by(role='guru', status='Aktif')
    if exclude_guru_id:
        query = query.filter(User.id != exclude_guru_id)

    for g in query.all():
        classes = parse_kelas_list(g.kelas)
        for c in classes:
            assigned[c] = g.nama or g.username
    return assigned


@admin_bp.route('/dashboard', endpoint='dashboard')
@admin_bp.route('/dashboard', endpoint='dashboard_admin')
@role_required('admin')
def dashboard_admin():
    tahun_ajaran = AppSetting.get_val('tahun_ajaran', '2026/2027')
    semester = AppSetting.get_val('semester', 'Ganjil')
    tahun_ajaran_full = f"Tahun Ajaran {tahun_ajaran} – Semester {semester}"

    guru_list = User.query.filter_by(role='guru').all()
    siswa_list = Siswa.query.all()

    return render_template(
        'admin/dashboard_admin.html',
        guru_list=guru_list,
        siswa_list=siswa_list,
        tahun_ajaran=tahun_ajaran,
        semester=semester,
        tahun_ajaran_full=tahun_ajaran_full
    )


@admin_bp.route('/update_tahun_ajaran', methods=['POST'])
@role_required('admin')
def update_tahun_ajaran():
    ta = request.form.get('tahun_ajaran', '').strip()
    sem = request.form.get('semester', '').strip()

    if ta and sem:
        AppSetting.set_val('tahun_ajaran', ta)
        AppSetting.set_val('semester', sem)
        flash(f'Tahun Ajaran berhasil diperbarui menjadi {ta} (Semester {sem})!', 'success')
    else:
        flash('Data Tahun Ajaran atau Semester tidak boleh kosong!', 'danger')

    return redirect(url_for('admin.dashboard_admin'))


@admin_bp.route('/template_guru')
@role_required('admin')
def template_guru():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Template_Guru_SDIT"

    ta_str = AppSetting.get_val('tahun_ajaran', '2026/2027')
    sem_str = AppSetting.get_val('semester', 'Ganjil')

    title_font = Font(name="Arial", size=13, bold=True, color="059669")
    subtitle_font = Font(name="Arial", size=10, bold=True, color="1E293B")
    info_font = Font(name="Arial", size=9, italic=True, color="475569")

    header_fill = PatternFill(start_color="059669", end_color="059669", fill_type="solid")
    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    data_font = Font(name="Arial", size=10)
    center_align = Alignment(horizontal="center", vertical="center")

    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

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

    ws['B1'] = "SDIT BINA MULIA"
    ws['B1'].font = title_font

    ws['B2'] = "FORMAT RESMI IMPORT DATA GURU & MUSYRIF"
    ws['B2'].font = subtitle_font

    ws['B3'] = f"Tahun Ajaran: {ta_str} (Semester {sem_str})  |  Contoh isi -> Nama: Ustadz Ahmad Fauzi | Username: ahmad_fauzi | Password: 123456 | Kelas: 1A, 2B"
    ws['B3'].font = info_font

    ws['B4'] = "Catatan: Kolom Nama Lengkap & Username wajib diisi mulai baris ke-7. Jangan ubah header pada baris ke-6!"
    ws['B4'].font = Font(name="Arial", size=9, italic=True, color="DC2626")

    ws.row_dimensions[1].height = 20
    ws.row_dimensions[2].height = 18

    headers = ["No", "Nama Lengkap", "Username", "Password Initial", "Kelas Binaan"]
    for col_idx, header_text in enumerate(headers, start=1):
        cell = ws.cell(row=6, column=col_idx, value=header_text)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
        cell.border = thin_border
    ws.row_dimensions[6].height = 28

    for row_idx in range(7, 32):
        ws.row_dimensions[row_idx].height = 22
        ws.cell(row=row_idx, column=1, value=row_idx - 6).alignment = center_align
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.font = data_font
            cell.border = thin_border
            if col_idx in [1, 3, 4, 5]:
                cell.alignment = center_align

    widths = [8, 36, 22, 20, 24]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name="Template_Resmi_Import_Guru_SDIT.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@admin_bp.route('/tambah_guru', methods=['POST'])
@role_required('admin')
def tambah_guru():
    nama = request.form.get('nama', '').strip()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    kelas_input = request.form.get('kelas', '-').strip()
    status = request.form.get('status', 'Aktif')

    if not nama or not username or not password:
        flash('Semua kolom wajib diisi!', 'danger')
        return redirect(url_for('admin.dashboard_admin'))

    if User.query.filter(db.func.lower(User.username) == username.lower()).first():
        flash(f'Username "{username}" sudah digunakan oleh akun lain!', 'danger')
        return redirect(url_for('admin.dashboard_admin'))

    kelas_list = parse_kelas_list(kelas_input)
    if status == 'Aktif' and kelas_list:
        assigned_map = get_assigned_classes_map()
        conflict = []
        for c in kelas_list:
            if c in assigned_map:
                conflict.append(f"Kelas {c} (sudah dibina oleh {assigned_map[c]})")

        if conflict:
            flash(f'Gagal menambahkan guru! {", ".join(conflict)}. Setiap kelas binaan hanya boleh dibina oleh 1 guru!', 'danger')
            return redirect(url_for('admin.dashboard_admin'))

    formatted_kelas = ", ".join(kelas_list) if kelas_list else '-'
    new_guru = User(nama=nama, username=username, role='guru', kelas=formatted_kelas, status=status)
    new_guru.set_password(password)
    db.session.add(new_guru)
    db.session.commit()
    flash(f'Guru {nama} dengan kelas {formatted_kelas} berhasil ditambahkan!', 'success')

    return redirect(url_for('admin.dashboard_admin'))


@admin_bp.route('/edit_guru/<int:guru_id>', methods=['POST'])
@role_required('admin')
def edit_guru(guru_id):
    guru = User.query.get_or_404(guru_id)
    nama = request.form.get('nama', '').strip()
    username = request.form.get('username', '').strip()
    kelas_input = request.form.get('kelas', '-').strip()
    status = request.form.get('status', 'Aktif')

    existing_user = User.query.filter(
        (db.func.lower(User.username) == username.lower()) &
        (User.id != guru_id)
    ).first()
    if existing_user:
        flash(f'Username "{username}" sudah digunakan guru lain!', 'danger')
        return redirect(url_for('admin.dashboard_admin'))

    kelas_list = parse_kelas_list(kelas_input)
    if status == 'Aktif' and kelas_list:
        assigned_map = get_assigned_classes_map(exclude_guru_id=guru.id)
        conflict = []
        for c in kelas_list:
            if c in assigned_map:
                conflict.append(f"Kelas {c} (sudah dibina oleh {assigned_map[c]})")

        if conflict:
            flash(f'Gagal mengubah data guru! {", ".join(conflict)}. Setiap kelas binaan hanya boleh dibina oleh 1 guru!', 'danger')
            return redirect(url_for('admin.dashboard_admin'))

    guru.nama = nama
    guru.username = username
    guru.kelas = ", ".join(kelas_list) if kelas_list else '-'
    guru.status = status

    password_baru = request.form.get('password', '').strip()
    if password_baru:
        guru.set_password(password_baru)

    db.session.commit()
    flash(f'Data guru {guru.nama} berhasil diperbarui!', 'success')
    return redirect(url_for('admin.dashboard_admin'))


@admin_bp.route('/hapus_guru/<int:guru_id>')
@role_required('admin')
def hapus_guru(guru_id):
    guru = User.query.get_or_404(guru_id)
    nama = guru.nama
    db.session.delete(guru)
    db.session.commit()
    flash(f'Akun guru {nama} berhasil dihapus dari sistem!', 'success')
    return redirect(url_for('admin.dashboard_admin'))


@admin_bp.route('/edit_siswa/<id_siswa>', methods=['POST'])
@role_required('admin')
def edit_siswa(id_siswa):
    siswa = Siswa.query.get_or_404(id_siswa)
    nama = request.form.get('nama', '').strip()
    username = request.form.get('username', '').strip()
    kelas = request.form.get('kelas', '').strip().upper()
    status = request.form.get('status', 'Aktif')

    if not nama or not username:
        flash('Nama dan Username murid tidak boleh kosong!', 'danger')
        return redirect(url_for('admin.dashboard_admin'))

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
        flash(f'Username "{username}" sudah digunakan pengguna lain!', 'danger')
        return redirect(url_for('admin.dashboard_admin'))

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
    flash(f'Data murid {nama} (Username: {username}) berhasil diperbarui!', 'success')
    return redirect(url_for('admin.dashboard_admin'))


@admin_bp.route('/edit_password_siswa/<id_siswa>', methods=['POST'])
@role_required('admin')
def edit_password_siswa(id_siswa):
    siswa = Siswa.query.get_or_404(id_siswa)
    password_baru = request.form.get('password', '').strip()

    if not password_baru:
        flash('Password baru tidak boleh kosong!', 'danger')
        return redirect(url_for('admin.dashboard_admin'))

    ortu = None
    if siswa.user_id_ortu:
        ortu = User.query.get(siswa.user_id_ortu)
    if not ortu:
        ortu = User.query.filter_by(username=siswa.nama, role='ortu').first()

    if not ortu:
        ortu = User(username=siswa.nama, role='ortu', nama=f"Wali {siswa.nama}", kelas=siswa.kelas, status='Aktif')
        ortu.set_password(password_baru)
        db.session.add(ortu)
        db.session.flush()
        siswa.user_id_ortu = ortu.id
    else:
        ortu.set_password(password_baru)

    db.session.commit()
    flash(f'Password akun murid/wali untuk {siswa.nama} berhasil diperbarui!', 'success')
    return redirect(url_for('admin.dashboard_admin'))


@admin_bp.route('/import_guru', methods=['POST'])
@role_required('admin')
def import_guru():
    file = request.files.get('file_excel_guru')
    if not file or not file.filename.lower().endswith(('.xlsx', '.xls')):
        flash('Format file tidak valid! Harap unggah file .xlsx atau .xls', 'danger')
        return redirect(url_for('admin.dashboard_admin'))

    try:
        # Baca file sekali ke memori BytesIO agar tidak habis saat dibaca 2x oleh pandas
        file_bytes = io.BytesIO(file.read())
        file_bytes.seek(0)
        df_raw = pd.read_excel(file_bytes, header=None, dtype=str)

        header_row_idx = None
        is_murid_template = False

        for idx, row in df_raw.iterrows():
            row_vals = [str(v).strip().lower() for v in row.values if pd.notna(v)]
            if any('nisn' in v for v in row_vals):
                is_murid_template = True
            has_nama = any(v in ['nama', 'nama lengkap', 'nama guru', 'nama musyrif'] for v in row_vals)
            has_user = any(v in ['username', 'username login', 'user'] for v in row_vals)
            if has_nama and has_user:
                header_row_idx = idx
                break

        if header_row_idx is None:
            if is_murid_template:
                flash('File yang diunggah adalah Template Murid, bukan Template Guru! Silakan unduh Template Guru terlebih dahulu.', 'danger')
            else:
                flash('Header kolom tidak dikenali! Pastikan file memiliki kolom "Nama Lengkap" dan "Username" sesuai Template Guru.', 'danger')
            return redirect(url_for('admin.dashboard_admin'))

        file_bytes.seek(0)
        df = pd.read_excel(file_bytes, skiprows=header_row_idx, dtype=str)

        # Normalisasi nama kolom (huruf kecil & tanpa spasi berlebih)
        col_map = {str(col).strip().lower(): col for col in df.columns}

        def get_col_val(row, aliases, default=''):
            for alias in aliases:
                if alias in col_map:
                    val = row.get(col_map[alias])
                    if pd.notna(val):
                        s = str(val).strip()
                        if s.lower() not in ['nan', 'none', '']:
                            return s
            return default

        imported_count = 0
        skipped = []
        assigned_map = get_assigned_classes_map()

        for _, row in df.iterrows():
            nama = get_col_val(row, ['nama lengkap', 'nama', 'nama guru', 'nama musyrif'])
            username = get_col_val(row, ['username', 'username login', 'user'])
            password = get_col_val(row, ['password initial', 'password', 'kata sandi', 'pass'], default='123456')
            raw_kelas = get_col_val(row, ['kelas binaan', 'kelas', 'rombel'], default='-')

            if not nama or not username:
                continue

            if User.query.filter(db.func.lower(User.username) == username.lower()).first():
                skipped.append(f"{nama} (Username '{username}' sudah terdaftar)")
                continue

            kelas_list = parse_kelas_list(raw_kelas)
            has_conflict = False
            for c in kelas_list:
                if c in assigned_map:
                    skipped.append(f"{nama} (Kelas {c} sudah dibina {assigned_map[c]})")
                    has_conflict = True
                    break

            if has_conflict:
                continue

            formatted_kelas = ", ".join(kelas_list) if kelas_list else '-'
            new_guru = User(nama=nama, username=username, role='guru', kelas=formatted_kelas, status='Aktif')
            new_guru.set_password(password)
            db.session.add(new_guru)

            for c in kelas_list:
                assigned_map[c] = nama
            imported_count += 1

        db.session.commit()

        if imported_count > 0:
            msg = f'Alhamdulillah, berhasil mengimpor {imported_count} data guru!'
            if skipped:
                msg += f' Dilewati: {"; ".join(skipped)}'
            flash(msg, 'success')
        elif skipped:
            flash(f'Tidak ada guru baru yang ditambahkan. Dilewati: {"; ".join(skipped)}', 'warning')
        else:
            flash('Tidak ada baris data guru yang terisi pada file Excel. Pastikan Nama Lengkap dan Username sudah diisi mulai baris ke-7.', 'warning')

    except Exception as e:
        db.session.rollback()
        flash(f'Gagal mengimpor file Excel: {str(e)}', 'danger')

    return redirect(url_for('admin.dashboard_admin'))