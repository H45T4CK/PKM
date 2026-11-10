from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from app.models.siswa import Siswa
from app.models.user import User
from app.models.record import RecordsTahsin, RecordsTahfidz
from app import db
from app.utils.decorators import role_required
from datetime import datetime
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as ExcelImage
import io, os, re

def extract_nama_depan(nama):
    if not nama:
        return 'murid'
    words = [re.sub(r'[^a-zA-Z0-9]', '', w) for w in str(nama).split() if re.sub(r'[^a-zA-Z0-9]', '', w)]
    if words:
        return words[0].lower()
    return 'murid'

guru_bp = Blueprint('guru', __name__)

GRADE_MAP = {
    'A': (100, 'Lulus'),
    'B': (85, 'Lulus'),
    'C': (70, 'Belum Lulus'),
    'D': (55, 'Belum Lulus'),
    'E': (40, 'Belum Lulus')
}

@guru_bp.route('/dashboard_guru')
@role_required('guru')
def dashboard():
    q = request.args.get('q', '').strip().lower()
    kelas_filter = request.args.get('kelas_filter', '').strip()
    status_filter = request.args.get('status_filter', '').strip()
    
    query = Siswa.query

    # Ambil daftar kelas yang dibina guru (bisa lebih dari 1, misal "1A, 2B")
    guru_kelas_str = session.get('kelas', '').strip()
    guru_classes = [c.strip().upper() for c in guru_kelas_str.replace('/', ',').replace(';', ',').split(',') if c.strip() and c.strip() != '-']

    # Filter kelas
    if kelas_filter and kelas_filter.lower() != 'all':
        query = query.filter(db.func.upper(Siswa.kelas) == kelas_filter.upper())
    elif guru_classes:
        query = query.filter(db.func.upper(Siswa.kelas).in_(guru_classes))

    # Filter status aktif / tidak aktif
    if status_filter and status_filter.lower() != 'all':
        query = query.filter(db.func.lower(Siswa.status) == status_filter.lower())

    # Pencarian nama, NISN, atau kelas
    if q:
        query = query.filter(
            (db.func.lower(Siswa.nama).contains(q)) |
            (db.func.lower(Siswa.id).contains(q)) |
            (db.func.lower(Siswa.kelas).contains(q))
        )
    
    siswa_list = query.all()

    # Kelas unik untuk pilihan filter
    all_classes = guru_classes if guru_classes else [c[0].upper() for c in db.session.query(Siswa.kelas).distinct().all() if c[0]]
    all_classes = sorted(list(set(all_classes)))

    siswa_ids = [s.id for s in siswa_list]
    if siswa_ids:
        tahfidz_records = RecordsTahfidz.query.filter(RecordsTahfidz.siswa_id.in_(siswa_ids)).all()
        tahsin_records = RecordsTahsin.query.filter(RecordsTahsin.siswa_id.in_(siswa_ids)).all()
    else:
        tahfidz_records = []
        tahsin_records = []

    # Hitung data distribusi grade untuk grafik ApexCharts
    grade_distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
    for s in siswa_list:
        g = s.grade_rata_rata
        if g in grade_distribution:
            grade_distribution[g] += 1

    return render_template(
        'guru/dashboard_guru.html', 
        siswa_list=siswa_list, 
        now_date=datetime.now().strftime("%Y-%m-%d"),
        total_tahfidz_rec=len(tahfidz_records),
        total_tahsin_rec=len(tahsin_records),
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

    kelas_pilihan = request.form.get('kelas', '').strip().upper()
    if not kelas_pilihan:
        guru_kelas = session.get('kelas', '1A').strip()
        first_k = [c.strip().upper() for c in guru_kelas.split(',') if c.strip()]
        kelas_pilihan = first_k[0] if first_k else '1A'

    if not custom_id:
        count = Siswa.query.count()
        custom_id = f"S{count + 1:03d}"
        idx = count + 1
        while Siswa.query.get(custom_id):
            idx += 1
            custom_id = f"S{idx:03d}"

    ortu = User.query.filter_by(username=nama, role='ortu').first()
    if not ortu:
        ortu = User(username=nama, role='ortu', nama=f"Wali {nama}", kelas=kelas_pilihan, status='Aktif')
        ortu.set_password('1234')
        db.session.add(ortu)
        db.session.flush()

    new_siswa = Siswa(id=custom_id, nama=nama, kelas=kelas_pilihan, poin=0, status=status, user_id_ortu=ortu.id)
    db.session.add(new_siswa)
    db.session.commit()

    flash(f'Data murid {nama} berhasil ditambahkan!', 'success')
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
    db.session.delete(siswa)
    db.session.commit()
    flash(f'Data murid {nama} berhasil dihapus dari sistem!', 'success')
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

    grade = request.form.get('grade', 'A').upper()
    default_nilai, default_lulus = GRADE_MAP.get(grade, (100, 'Lulus'))
    
    nilai_input = request.form.get('nilai')
    nilai = int(nilai_input) if nilai_input and nilai_input.isdigit() else default_nilai
    status_lulus = 'Lulus' if grade in ['A', 'B'] else 'Belum Lulus'

    rec = RecordsTahsin(
        siswa_id=s.id,
        tanggal=request.form.get('tanggal') or datetime.now().strftime("%Y-%m-%d"),
        halaman_akhir=gabungan_halaman,
        catatan=request.form.get('catatan', ''),
        grade=grade,
        nilai=nilai,
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

    flash(f'Nilai Tahsin {s.nama} berhasil disimpan! Grade {grade} ({status_lulus})', 'success')
    return redirect(request.referrer or url_for('guru.dashboard'))

@guru_bp.route('/catat_tahfidz/<id_siswa>', methods=['POST'])
@role_required('guru')
def catat_tahfidz(id_siswa):
    s = Siswa.query.get_or_404(id_siswa)
    juz_pilihan = request.form.get('juz', '')
    surat_ayat = request.form.get('hafalan_terakhir', '-').strip()
    gabungan_hafalan = f"{juz_pilihan} - {surat_ayat}" if juz_pilihan else surat_ayat

    grade = request.form.get('grade', 'A').upper()
    default_nilai, default_lulus = GRADE_MAP.get(grade, (100, 'Lulus'))
    
    nilai_input = request.form.get('nilai')
    nilai = int(nilai_input) if nilai_input and nilai_input.isdigit() else default_nilai
    status_lulus = 'Lulus' if grade in ['A', 'B'] else 'Belum Lulus'

    rec = RecordsTahfidz(
        siswa_id=s.id,
        tanggal=request.form.get('tanggal') or datetime.now().strftime("%Y-%m-%d"),
        hafalan_terakhir=gabungan_hafalan,
        catatan=request.form.get('catatan', ''),
        grade=grade,
        nilai=nilai,
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
    if siswa.rata_rata_nilai is not None:
        siswa.poin = int(siswa.rata_rata_nilai)
    else:
        siswa.poin = 0
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
    if siswa.rata_rata_nilai is not None:
        siswa.poin = int(siswa.rata_rata_nilai)
    else:
        siswa.poin = 0
    db.session.commit()
    flash('Setoran Tahfidz berhasil dihapus dari histori!', 'success')
    return redirect(request.referrer or url_for('guru.dashboard'))

@guru_bp.route('/template_murid')
@role_required('guru')
def template_murid():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Template_Murid"

    guru_kelas_str = session.get('kelas', '1A').strip()
    first_kelas = [c.strip().upper() for c in guru_kelas_str.replace('/', ',').replace(';', ',').split(',') if c.strip() and c.strip() != '-']
    default_kelas = first_kelas[0] if first_kelas else '1A'

    img_path = os.path.join('app', 'static', 'img', 'logo-sdit-sm.png')
    if not os.path.exists(img_path):
        img_path = os.path.join('PKM-main', 'app', 'static', 'img', 'logo-sdit-sm.png')
    if os.path.exists(img_path):
        try:
            img = ExcelImage(img_path)
            img.width = 52
            img.height = 52
            ws.add_image(img, 'A1')
        except Exception:
            pass

    ws.merge_cells('B1:F1')
    ws['B1'] = "SDIT BINA MULIA"
    ws['B1'].font = Font(name="Arial", size=14, bold=True, color="059669")

    ws.merge_cells('B2:F2')
    ws['B2'] = "FORMAT RESMI IMPORT DATA MURID / SISWA"
    ws['B2'].font = Font(name="Arial", size=10, bold=True, color="1E293B")

    ws['B3'] = "Tahun Ajaran: 2026/2027"
    ws['B3'].font = Font(name="Arial", size=9, bold=True, color="475569")
    ws['D3'] = f"Kelas: {default_kelas}"
    ws['D3'].font = Font(name="Arial", size=9, bold=True, color="475569")

    ws.merge_cells('B4:F4')
    ws['B4'] = "Catatan: Username login wali/murid otomatis dibuat dari nama depan, password default adalah NISN."
    ws['B4'].font = Font(name="Arial", size=8, italic=True, color="64748B")

    ws.append([]) # row 5 blank

    header_fill = PatternFill(start_color="059669", end_color="059669", fill_type="solid")
    header_font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
    data_font = Font(name="Arial", size=10)
    center_align = Alignment(horizontal="center", vertical="center")
    left_align = Alignment(horizontal="left", vertical="center")
    thin_border = Border(
        left=Side(style='thin', color='D1D5DB'),
        right=Side(style='thin', color='D1D5DB'),
        top=Side(style='thin', color='D1D5DB'),
        bottom=Side(style='thin', color='D1D5DB')
    )

    headers = ["No", "NISN", "Nama Murid", "Kelas", "Jenis Kelamin", "Status"]
    ws.append(headers) # row 6

    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=6, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
        cell.border = thin_border
    ws.row_dimensions[6].height = 26

    # Kosongan: Buat baris kosong rapi siap diinput tanpa data dummy
    for row_idx in range(7, 26):
        ws.row_dimensions[row_idx].height = 22
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.font = data_font
            cell.border = thin_border
            if col_idx == 1:
                cell.value = row_idx - 6
                cell.alignment = center_align
            elif col_idx in [2, 4, 5, 6]:
                cell.alignment = center_align
            else:
                cell.alignment = left_align

    widths = [6, 18, 34, 12, 16, 14]
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
            # Deteksi baris header secara fleksibel
            df_raw = pd.read_excel(file, header=None)
            header_idx = 0
            for idx, r in df_raw.iterrows():
                row_str = " ".join([str(v).lower() for v in r.values if pd.notna(v)])
                if any(kw in row_str for kw in ['nama', 'murid', 'siswa', 'nisn', 'nis']):
                    header_idx = idx
                    break

            file.seek(0)
            df = pd.read_excel(file, skiprows=header_idx)
            imported_count = 0
            
            guru_kelas_str = session.get('kelas', '1A').strip()
            first_kelas = [c.strip().upper() for c in guru_kelas_str.replace('/', ',').replace(';', ',').split(',') if c.strip() and c.strip() != '-']
            default_kelas = first_kelas[0] if first_kelas else '1A'

            # Normalisasi nama kolom (lowercase & strip whitespace)
            orig_cols = list(df.columns)
            col_map = {}
            for col in orig_cols:
                clean_name = str(col).strip().lower()
                col_map[clean_name] = col

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

                # Logika pembuatan username & pass murid: username = nama depan, pass = NISN
                nama_depan = extract_nama_depan(nama)
                base_username = re.sub(r'[^a-zA-Z0-9_]', '', nama_depan).lower()
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
                    # Cari akun User ortu atau buat baru
                    ortu = None
                    # Cek username candidate
                    user_cand = base_username
                    conflict_user = User.query.filter(db.func.lower(User.username) == user_cand.lower()).first()
                    if conflict_user:
                        clean_id_suffix = re.sub(r'[^a-zA-Z0-9]', '', custom_id).lower()
                        user_cand = f"{base_username}_{clean_id_suffix[-3:]}" if len(clean_id_suffix) >= 3 else f"{base_username}_{clean_id_suffix}"
                        if User.query.filter(db.func.lower(User.username) == user_cand.lower()).first():
                            user_cand = f"{base_username}_{Siswa.query.count() + imported_count + 1}"

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
            flash(f'Gagal memproses file Excel: {str(e)}', 'danger')
    else:
        flash('File tidak valid! Mohon unggah spreadsheet format .xlsx atau .xls', 'danger')
    return redirect(request.referrer or url_for('guru.dashboard'))
