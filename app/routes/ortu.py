from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.models.siswa import Siswa
from app.models.record import RecordsTahsin, RecordsTahfidz
from app import db
from app.utils.decorators import role_required

ortu_bp = Blueprint('ortu', __name__)

@ortu_bp.route('/dashboard_ortu')
@role_required('ortu')
def dashboard():
    siswa_id = session.get('siswa_id')
    siswa = Siswa.query.get(siswa_id) if siswa_id else None
    
    if not siswa and session.get('user_id'):
        siswa = Siswa.query.filter_by(user_id_ortu=session.get('user_id')).first()
        
    if not siswa and session.get('username'):
        siswa = Siswa.query.filter(
            (db.func.lower(Siswa.nama) == session.get('username', '').lower()) |
            (db.func.lower(Siswa.id) == session.get('username', '').lower())
        ).first()

    if siswa:
        session['siswa_id'] = siswa.id
        if session.get('user_id') and not siswa.user_id_ortu:
            siswa.user_id_ortu = session.get('user_id')
            db.session.commit()

    return render_template('ortu/dashboard_ortu.html', siswa=siswa)

@ortu_bp.route('/api/ortu_status')
@role_required('ortu')
def api_ortu_status():
    siswa_id = session.get('siswa_id')
    siswa = Siswa.query.get(siswa_id) if siswa_id else None
    if not siswa: return jsonify({"error": "Murid tidak ditemukan"}), 404

    return jsonify({
        "rata_rata_nilai": siswa.rata_rata_nilai,
        "grade_rata_rata": siswa.grade_rata_rata,
        "status_kelulusan": siswa.status_kelulusan_rata_rata,
        "tahfidz_count": len(siswa.tahfidz),
        "tahsin_count": len(siswa.tahsin),
        "last_tahfidz": siswa.tahfidz[-1].hafalan_terakhir if siswa.tahfidz else "—",
        "last_tahfidz_date": siswa.tahfidz[-1].tanggal if siswa.tahfidz else "Belum ada setoran",
        "last_tahsin": siswa.tahsin[-1].halaman_akhir if siswa.tahsin else "—",
        "last_tahsin_date": siswa.tahsin[-1].tanggal if siswa.tahsin else "Belum ada catatan"
    })

@ortu_bp.route('/ortu_ceklis/<jenis>/<int:rec_id>', methods=['POST'])
@role_required('ortu')
def ortu_ceklis(jenis, rec_id):
    rec = RecordsTahfidz.query.get_or_404(rec_id) if jenis == 'tahfidz' else RecordsTahsin.query.get_or_404(rec_id)
    rec.ceklist_ortu = True
    
    catatan_ortu = request.form.get('catatan_ortu', '').strip()
    if catatan_ortu:
        rec.catatan_ortu = catatan_ortu
        
    db.session.commit()
    flash('Paraf digital & konfirmasi muroja\'ah rumah berhasil disimpan!', 'success')
    return redirect(url_for('ortu.dashboard'))
