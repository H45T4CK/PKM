from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.user import User
from app.models.siswa import Siswa
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if session.get('role') == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif session.get('role') == 'guru':
        return redirect(url_for('guru.dashboard'))
    elif session.get('role') == 'ortu':
        return redirect(url_for('ortu.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('Username dan Password wajib diisi!', 'danger')
            return render_template('auth/login.html')

        # 1. Cek langsung di tabel User berdasarkan username (case-insensitive)
        user = User.query.filter(db.func.lower(User.username) == username.lower()).first()

        if user and user.check_password(password):
            if user.status == 'Tidak Aktif':
                flash('Akun Anda telah dinonaktifkan! Hubungi Administrator.', 'danger')
                return render_template('auth/login.html')

            session.permanent = True
            session['user_id'] = user.id
            session['user'] = user.nama or user.username
            session['username'] = user.username
            session['role'] = user.role
            session['kelas'] = user.kelas or '-'

            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'guru':
                return redirect(url_for('guru.dashboard'))
            elif user.role == 'ortu':
                siswa = Siswa.query.filter(
                    (Siswa.user_id_ortu == user.id) | 
                    (db.func.lower(Siswa.nama) == user.username.lower())
                ).first()
                if siswa:
                    session['siswa_id'] = siswa.id
                    session['kelas'] = siswa.kelas
                return redirect(url_for('ortu.dashboard'))

        # 2. Cek apakah login menggunakan NISN atau Nama Siswa untuk akun Orang Tua / Wali
        siswa = Siswa.query.filter(
            (db.func.lower(Siswa.id) == username.lower()) | 
            (db.func.lower(Siswa.nama) == username.lower())
        ).first()

        if siswa:
            ortu = None
            if siswa.user_id_ortu:
                ortu = User.query.get(siswa.user_id_ortu)
            if not ortu:
                ortu = User.query.filter(
                    (db.func.lower(User.username) == siswa.nama.lower()) & 
                    (User.role == 'ortu')
                ).first()

            # Verifikasi password akun ortu atau default '1234'
            valid_pass = False
            if ortu:
                valid_pass = ortu.check_password(password)
            elif password == '1234':
                valid_pass = True

            if valid_pass:
                if not ortu:
                    ortu = User(username=siswa.nama, role='ortu', nama=f"Wali {siswa.nama}", kelas=siswa.kelas, status='Aktif')
                    ortu.set_password(password)
                    db.session.add(ortu)
                    db.session.flush()
                    siswa.user_id_ortu = ortu.id
                    db.session.commit()

                if ortu.status == 'Tidak Aktif':
                    flash('Akun murid/wali ini telah dinonaktifkan!', 'danger')
                    return render_template('auth/login.html')

                session.permanent = True
                session['user_id'] = ortu.id
                session['user'] = ortu.nama
                session['username'] = ortu.username
                session['role'] = 'ortu'
                session['kelas'] = siswa.kelas
                session['siswa_id'] = siswa.id
                return redirect(url_for('ortu.dashboard'))

        flash('Username atau Password yang Anda masukkan salah!', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
