import re
from app import db

PREDIKAT_LABELS = {
    'A': 'Sangat Baik (Mumtaz)',
    'B+': 'Baik Sekali (Jayyid Jiddan)',
    'B': 'Baik (Jayyid)',
    'C': 'Perlu Bimbingan (Maqbul)',
    '-': 'Belum Dinilai'
}

class Siswa(db.Model):
    __tablename__ = 'siswa'
    id = db.Column(db.String(50), primary_key=True)
    nama = db.Column(db.String(150), nullable=False)
    kelas = db.Column(db.String(50), nullable=False)
    poin = db.Column(db.Integer, default=0)
    user_id_ortu = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    status = db.Column(db.String(20), default='Aktif')

    catatan = db.relationship('RecordsPoin', backref='siswa', lazy=True, cascade="all, delete-orphan", order_by="RecordsPoin.id.asc()")
    tahsin = db.relationship('RecordsTahsin', backref='siswa', lazy=True, cascade="all, delete-orphan", order_by="RecordsTahsin.id.asc()")
    tahfidz = db.relationship('RecordsTahfidz', backref='siswa', lazy=True, cascade="all, delete-orphan", order_by="RecordsTahfidz.id.asc()")

    @property
    def status_clean(self):
        return self.status or 'Aktif'

    @property
    def ortu_username(self):
        if self.ortu:
            return self.ortu.username
        return self.nama

    @staticmethod
    def get_predikat_desc(grade):
        g = str(grade).strip().upper() if grade else '-'
        return PREDIKAT_LABELS.get(g, 'Belum Dinilai')

    @staticmethod
    def _extract_grades(records):
        grades = []
        for r in records:
            g = getattr(r, 'grade', None)
            if g:
                grades.append(str(g).strip().upper())
            elif getattr(r, 'nilai', None) is not None:
                n = r.nilai
                if n >= 90:
                    grades.append('A')
                elif n >= 80:
                    grades.append('B+')
                elif n >= 70:
                    grades.append('B')
                else:
                    grades.append('C')
        return grades

    @classmethod
    def _calc_grade_from_records(cls, records):
        GRADE_WEIGHTS = {'A': 4.0, 'B+': 3.0, 'B': 2.0, 'C': 1.0}
        grades = cls._extract_grades(records)
        if not grades:
            return '-'
        # Aturan kelulusan: jika mendapat nilai C sebanyak 5 kali atau lebih, otomatis C (Tidak Lulus)
        if grades.count('C') >= 5:
            return 'C'
        weights = [GRADE_WEIGHTS.get(g, 1.0) for g in grades]
        avg = sum(weights) / len(weights)
        if avg >= 3.5:
            return 'A'
        if avg >= 2.5:
            return 'B+'
        if avg >= 1.5:
            return 'B'
        return 'C'

    @property
    def jumlah_c_tahsin(self):
        return self._extract_grades(self.tahsin).count('C')

    @property
    def jumlah_c_tahfidz(self):
        return self._extract_grades(self.tahfidz).count('C')

    @property
    def jumlah_c(self):
        return self._extract_grades(list(self.tahsin) + list(self.tahfidz)).count('C')

    @property
    def grade_tahsin(self):
        return self._calc_grade_from_records(self.tahsin)

    @property
    def predikat_tahsin_desc(self):
        return self.get_predikat_desc(self.grade_tahsin)

    @property
    def status_lulus_tahsin(self):
        g = self.grade_tahsin
        if g in ['A', 'B+', 'B']:
            return 'Lulus'
        if g == 'C':
            return 'Tidak Lulus'
        return 'Belum Dinilai'

    @property
    def rata_rata_tahsin(self):
        g = self.grade_tahsin
        return {'A': 100, 'B+': 88, 'B': 78, 'C': 60}.get(g, None)

    @property
    def grade_tahfidz(self):
        return self._calc_grade_from_records(self.tahfidz)

    @property
    def predikat_tahfidz_desc(self):
        return self.get_predikat_desc(self.grade_tahfidz)

    @property
    def status_lulus_tahfidz(self):
        g = self.grade_tahfidz
        if g in ['A', 'B+', 'B']:
            return 'Lulus'
        if g == 'C':
            return 'Tidak Lulus'
        return 'Belum Dinilai'

    @property
    def rata_rata_tahfidz(self):
        g = self.grade_tahfidz
        return {'A': 100, 'B+': 88, 'B': 78, 'C': 60}.get(g, None)

    @property
    def grade_rata_rata(self):
        all_recs = list(self.tahsin) + list(self.tahfidz)
        return self._calc_grade_from_records(all_recs)

    @property
    def predikat_rata_rata_desc(self):
        return self.get_predikat_desc(self.grade_rata_rata)

    @property
    def status_kelulusan_rata_rata(self):
        g = self.grade_rata_rata
        if g in ['A', 'B+', 'B']:
            return 'Lulus'
        if g == 'C':
            return 'Tidak Lulus'
        return 'Belum Dinilai'

    @property
    def rata_rata_nilai(self):
        g = self.grade_rata_rata
        return {'A': 100, 'B+': 88, 'B': 78, 'C': 60}.get(g, None)

    def _format_date(self, d_str):
        if not d_str:
            return "-"
        s = str(d_str).strip()
        if len(s) >= 10 and s[4] == '-' and s[7] == '-':
            return f"{s[8:10]}/{s[5:7]}/{s[0:4]}"
        return s

    @property
    def latest_tahsin(self):
        if self.tahsin:
            t = self.tahsin[-1]
            g = (t.grade or ('A' if t.nilai and t.nilai >= 90 else 'B')).upper()
            is_lulus = g in ['A', 'B+', 'B']
            return {
                "jenis": "Tahsin",
                "tanggal": self._format_date(t.tanggal),
                "materi": t.halaman_akhir,
                "grade": g,
                "predikat": self.get_predikat_desc(g),
                "nilai": t.nilai if t.nilai is not None else 100,
                "status_lulus": 'Lulus' if is_lulus else 'Tidak Lulus',
                "catatan": t.catatan or "",
                "penilai": t.penilai or "",
                "ceklist_ortu": bool(t.ceklist_ortu),
                "catatan_ortu": t.catatan_ortu or "",
                "id": t.id
            }
        return None

    @property
    def latest_tahfidz(self):
        if self.tahfidz:
            f = self.tahfidz[-1]
            g = (f.grade or ('A' if f.nilai and f.nilai >= 90 else 'B')).upper()
            is_lulus = g in ['A', 'B+', 'B']
            return {
                "jenis": "Tahfidz",
                "tanggal": self._format_date(f.tanggal),
                "materi": f.hafalan_terakhir,
                "grade": g,
                "predikat": self.get_predikat_desc(g),
                "nilai": f.nilai if f.nilai is not None else 100,
                "status_lulus": 'Lulus' if is_lulus else 'Tidak Lulus',
                "catatan": f.catatan or "",
                "penilai": f.penilai or "",
                "ceklist_ortu": bool(f.ceklist_ortu),
                "catatan_ortu": f.catatan_ortu or "",
                "id": f.id
            }
        return None

    @property
    def latest_setoran(self):
        latest = self.latest_tahsin
        f_latest = self.latest_tahfidz
        if f_latest and (not latest or f_latest['id'] >= latest['id']):
            return f_latest
        return latest

    @property
    def riwayat_capaian_tahsin(self):
        items = []
        for t in self.tahsin:
            g = (t.grade or ('A' if t.nilai and t.nilai >= 90 else 'B')).upper()
            is_lulus = g in ['A', 'B+', 'B']
            items.append({
                "id": t.id,
                "tanggal": self._format_date(t.tanggal),
                "materi": t.halaman_akhir,
                "grade": g,
                "predikat": self.get_predikat_desc(g),
                "nilai": t.nilai if t.nilai is not None else 100,
                "status_lulus": 'Lulus' if is_lulus else 'Tidak Lulus',
                "catatan": t.catatan or "Fasih, makharijul huruf & hukum tajwid sangat baik.",
                "penilai": t.penilai or "Musyrif",
                "ceklist_ortu": bool(t.ceklist_ortu),
                "catatan_ortu": t.catatan_ortu or ""
            })
        return items

    @property
    def riwayat_capaian_tahfidz(self):
        items = []
        for f in self.tahfidz:
            g = (f.grade or ('A' if f.nilai and f.nilai >= 90 else 'B')).upper()
            is_lulus = g in ['A', 'B+', 'B']
            items.append({
                "id": f.id,
                "tanggal": self._format_date(f.tanggal),
                "materi": f.hafalan_terakhir,
                "grade": g,
                "predikat": self.get_predikat_desc(g),
                "nilai": f.nilai if f.nilai is not None else 100,
                "status_lulus": 'Lulus' if is_lulus else 'Tidak Lulus',
                "catatan": f.catatan or "Hafalan lancar, mutqin, dan tartil.",
                "penilai": f.penilai or "Musyrif",
                "ceklist_ortu": bool(f.ceklist_ortu),
                "catatan_ortu": f.catatan_ortu or ""
            })
        return items

    @property
    def riwayat_grade(self):
        items = []
        for t in self.tahsin:
            g = (t.grade or 'A').upper()
            items.append({
                "jenis": "Tahsin",
                "tanggal": self._format_date(t.tanggal),
                "materi": t.halaman_akhir,
                "grade": g,
                "predikat": self.get_predikat_desc(g),
                "status_lulus": 'Lulus' if g in ['A', 'B+', 'B'] else 'Tidak Lulus',
                "id": t.id
            })
        for f in self.tahfidz:
            g = (f.grade or 'A').upper()
            items.append({
                "jenis": "Tahfidz",
                "tanggal": self._format_date(f.tanggal),
                "materi": f.hafalan_terakhir,
                "grade": g,
                "predikat": self.get_predikat_desc(g),
                "status_lulus": 'Lulus' if g in ['A', 'B+', 'B'] else 'Tidak Lulus',
                "id": f.id
            })
        items.sort(key=lambda x: x['id'], reverse=True)
        return items

    @property
    def has_catatan_ortu(self):
        return any(bool(t.catatan_ortu) for t in self.tahsin) or any(bool(f.catatan_ortu) for f in self.tahfidz)

    @property
    def has_paraf_ortu(self):
        return any(bool(t.ceklist_ortu) for t in self.tahsin) or any(bool(f.ceklist_ortu) for f in self.tahfidz)

    @property
    def total_catatan_ortu(self):
        return sum(1 for t in self.tahsin if t.catatan_ortu) + sum(1 for f in self.tahfidz if f.catatan_ortu)

    def to_dict(self):
        return {
            "id": self.id,
            "nama": self.nama,
            "kelas": self.kelas,
            "poin": self.poin,
            "status": self.status_clean,
            "jumlah_c": self.jumlah_c,
            "grade_tahsin": self.grade_tahsin,
            "predikat_tahsin": self.predikat_tahsin_desc,
            "status_lulus_tahsin": self.status_lulus_tahsin,
            "grade_tahfidz": self.grade_tahfidz,
            "predikat_tahfidz": self.predikat_tahfidz_desc,
            "status_lulus_tahfidz": self.status_lulus_tahfidz,
            "grade_rata_rata": self.grade_rata_rata,
            "predikat_rata_rata": self.predikat_rata_rata_desc,
            "status_lulus": self.status_kelulusan_rata_rata,
            "catatan": [c.to_dict() for c in self.catatan],
            "tahsin": [t.to_dict() for t in self.tahsin],
            "tahfidz": [f.to_dict() for f in self.tahfidz]
        }

    def __getitem__(self, key):
        if key == 'catatan': return [c.to_dict() for c in self.catatan]
        if key == 'tahsin': return [t.to_dict() for t in self.tahsin]
        if key == 'tahfidz': return [f.to_dict() for f in self.tahfidz]
        if key == 'rata_rata_nilai': return self.rata_rata_nilai
        if key == 'rata_rata_tahsin': return self.rata_rata_tahsin
        if key == 'rata_rata_tahfidz': return self.rata_rata_tahfidz
        if key == 'latest_tahsin': return self.latest_tahsin
        if key == 'latest_tahfidz': return self.latest_tahfidz
        if key == 'latest_setoran': return self.latest_setoran
        if key == 'riwayat_capaian_tahsin': return self.riwayat_capaian_tahsin
        if key == 'riwayat_capaian_tahfidz': return self.riwayat_capaian_tahfidz
        if key == 'riwayat_grade': return self.riwayat_grade
        if key == 'has_catatan_ortu': return self.has_catatan_ortu
        if key == 'has_paraf_ortu': return self.has_paraf_ortu
        if key == 'total_catatan_ortu': return self.total_catatan_ortu
        if key == 'jumlah_c': return self.jumlah_c
        if key == 'status': return self.status_clean
        return getattr(self, key)