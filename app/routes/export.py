from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file, Response
from app.models.siswa import Siswa
from app import db
from app.utils.decorators import role_required
from datetime import datetime
import pandas as pd
import io, os

export_bp = Blueprint('export', __name__)

def _build_export_rows(siswa_list):
    return [
        {
            "NISN / ID": s.id,
            "Nama Murid": s.nama,
            "Kelas": s.kelas,
            "Status Murid": s.status_clean,
            "Grade Tahsin": s.grade_tahsin,
            "Predikat Tahsin": s.predikat_tahsin_desc,
            "Grade Tahfidz": s.grade_tahfidz,
            "Predikat Tahfidz": s.predikat_tahfidz_desc,
            "Grade Akhir Qur'an": s.grade_rata_rata,
            "Predikat Akhir": s.predikat_rata_rata_desc,
            "Status Kelulusan": s.status_kelulusan_rata_rata
        }
        for s in siswa_list
    ]

@export_bp.route('/cetak_hafalan/<id_siswa>')
@export_bp.route('/riwayat_poin/<id_siswa>')
@role_required('guru', 'admin', 'ortu')
def cetak_hafalan_siswa(id_siswa):
    siswa = Siswa.query.get_or_404(id_siswa)
    return render_template('reports/lembar_hafalan.html', siswa=siswa)

@export_bp.route('/export_excel')
@role_required('guru', 'admin')
def export_excel():
    try:
        query = Siswa.query
        if session.get('role') == 'guru':
            guru_kelas = session.get('kelas', '').strip()
            if guru_kelas and guru_kelas != '-':
                classes = [c.strip().upper() for c in guru_kelas.replace('/', ',').replace(';', ',').split(',') if c.strip()]
                if classes:
                    query = query.filter(db.func.upper(Siswa.kelas).in_(classes))

        df = pd.DataFrame(_build_export_rows(query.all()))
        os.makedirs('data/exports', exist_ok=True)
        export_path = os.path.join('data/exports', 'Laporan_Murid_SDIT.xlsx')
        df.to_excel(export_path, index=False, engine='openpyxl')
        return send_file(export_path, as_attachment=True, download_name='Laporan_Murid_SDIT.xlsx')
    except Exception as e:
        flash(f'Export Excel gagal: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('guru.dashboard'))

@export_bp.route('/export_csv')
@role_required('guru', 'admin')
def export_csv():
    try:
        query = Siswa.query
        if session.get('role') == 'guru':
            guru_kelas = session.get('kelas', '').strip()
            if guru_kelas and guru_kelas != '-':
                classes = [c.strip().upper() for c in guru_kelas.replace('/', ',').replace(';', ',').split(',') if c.strip()]
                if classes:
                    query = query.filter(db.func.upper(Siswa.kelas).in_(classes))

        df = pd.DataFrame(_build_export_rows(query.all()))
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        return Response(buffer.getvalue().encode('utf-8-sig'), mimetype='text/csv', headers={"Content-Disposition": "attachment; filename=Laporan_Murid_SDIT.csv"})
    except Exception as e:
        flash(f'Export CSV gagal: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('guru.dashboard'))

@export_bp.route('/export_pdf')
@role_required('guru', 'admin')
def export_pdf():
    query = Siswa.query
    if session.get('role') == 'guru':
        guru_kelas = session.get('kelas', '').strip()
        if guru_kelas and guru_kelas != '-':
            classes = [c.strip().upper() for c in guru_kelas.replace('/', ',').replace(';', ',').split(',') if c.strip()]
            if classes:
                query = query.filter(db.func.upper(Siswa.kelas).in_(classes))

    siswa_list = query.all()
    return render_template('reports/laporansemua.html', siswa_list=siswa_list, tanggal=datetime.now().strftime("%d/%m/%Y"))