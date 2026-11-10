import re
from app import db

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

    @property
    def rata_rata_tahsin(self):
        nilai_list = [t.nilai for t in self.tahsin if t.nilai is not None]
        if not nilai_list:
            return None
        return round(sum(nilai_list) / len(nilai_list), 1)

    @property
    def grade_tahsin(self):
        avg = self.rata_rata_tahsin
        if avg is None: return '-'
        if avg >= 90: return 'A'
        if avg >= 80: return 'B'
        if avg >= 70: return 'C'
        if avg >= 60: return 'D'
        return 'E'

    @property
    def status_lulus_tahsin(self):
        g = self.grade_tahsin
        if g in ['A', 'B']: return 'Lulus'
        if g in ['C', 'D', 'E']: return 'Belum Lulus'
        return 'Belum Dinilai'

    @property
    def rata_rata_tahfidz(self):
        nilai_list = [f.nilai for f in self.tahfidz if f.nilai is not None]
        if not nilai_list:
            return None
        return round(sum(nilai_list) / len(nilai_list), 1)

    @property
    def grade_tahfidz(self):
        avg = self.rata_rata_tahfidz
        if avg is None: return '-'
        if avg >= 90: return 'A'
        if avg >= 80: return 'B'
        if avg >= 70: return 'C'
        if avg >= 60: return 'D'
        return 'E'

    @property
    def status_lulus_tahfidz(self):
        g = self.grade_tahfidz
        if g in ['A', 'B']: return 'Lulus'
        if g in ['C', 'D', 'E']: return 'Belum Lulus'
        return 'Belum Dinilai'

    @property
    def rata_rata_nilai(self):
        all_nilai = [t.nilai for t in self.tahsin if t.nilai is not None] + [f.nilai for f in self.tahfidz if f.nilai is not None]
        if not all_nilai:
            return None
        return round(sum(all_nilai) / len(all_nilai), 1)

    @property
    def grade_rata_rata(self):
        avg = self.rata_rata_nilai
        if avg is None: return '-'
        if avg >= 90: return 'A'
        if avg >= 80: return 'B'
        if avg >= 70: return 'C'
        if avg >= 60: return 'D'
        return 'E'

    @property
    def status_kelulusan_rata_rata(self):
        g = self.grade_rata_rata
        if g in ['A', 'B']: return 'Lulus'
        if g in ['C', 'D', 'E']: return 'Belum Lulus'
        return 'Belum Dinilai'

    @property
    def latest_tahsin(self):
        if self.tahsin:
            t = self.tahsin[-1]
            return {
                "jenis": "Tahsin",
                "tanggal": t.tanggal,
                "materi": t.halaman_akhir,
                "grade": t.grade or ('A' if t.nilai and t.nilai >= 90 else 'B'),
                "nilai": t.nilai if t.nilai is not None else 100,
                "status_lulus": t.status_lulus or ('Lulus' if (t.grade in ['A', 'B'] or (t.nilai and t.nilai >= 80)) else 'Belum Lulus'),
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
            return {
                "jenis": "Tahfidz",
                "tanggal": f.tanggal,
                "materi": f.hafalan_terakhir,
                "grade": f.grade or ('A' if f.nilai and f.nilai >= 90 else 'B'),
                "nilai": f.nilai if f.nilai is not None else 100,
                "status_lulus": f.status_lulus or ('Lulus' if (f.grade in ['A', 'B'] or (f.nilai and f.nilai >= 80)) else 'Belum Lulus'),
                "catatan": f.catatan or "",
                "penilai": f.penilai or "",
                "ceklist_ortu": bool(f.ceklist_ortu),
                "catatan_ortu": f.catatan_ortu or "",
                "id": f.id
            }
        return None

    @property
    def latest_setoran(self):
        latest = None
        if self.tahsin:
            t = self.tahsin[-1]
            latest = {
                "jenis": "Tahsin",
                "tanggal": t.tanggal,
                "materi": t.halaman_akhir,
                "grade": t.grade or ('A' if t.nilai and t.nilai >= 90 else 'B'),
                "nilai": t.nilai if t.nilai is not None else 100,
                "status_lulus": t.status_lulus or ('Lulus' if (t.grade in ['A', 'B'] or (t.nilai and t.nilai >= 80)) else 'Belum Lulus'),
                "catatan": t.catatan or "",
                "penilai": t.penilai or "",
                "ceklist_ortu": bool(t.ceklist_ortu),
                "catatan_ortu": t.catatan_ortu or "",
                "id": t.id
            }

        if self.tahfidz:
            f = self.tahfidz[-1]
            if not latest or f.id >= getattr(self.tahsin[-1], 'id', 0):
                latest = {
                    "jenis": "Tahfidz",
                    "tanggal": f.tanggal,
                    "materi": f.hafalan_terakhir,
                    "grade": f.grade or ('A' if f.nilai and f.nilai >= 90 else 'B'),
                    "nilai": f.nilai if f.nilai is not None else 100,
                    "status_lulus": f.status_lulus or ('Lulus' if (f.grade in ['A', 'B'] or (f.nilai and f.nilai >= 80)) else 'Belum Lulus'),
                    "catatan": f.catatan or "",
                    "penilai": f.penilai or "",
                    "ceklist_ortu": bool(f.ceklist_ortu),
                    "catatan_ortu": f.catatan_ortu or "",
                    "id": f.id
                }
        return latest

    @property
    def progress_tahsin_info(self):
        if not self.tahsin:
            return {
                "label": "Tahsin Al-Qur'an (Mulai)",
                "percent": 0,
                "deskripsi": "Belum ada catatan tahsin",
                "status": "Belum Dinilai",
                "evaluasi": "Menunggu evaluasi ustadz/ustadzah"
            }
        
        last = self.tahsin[-1]
        last_materi = last.halaman_akhir or ""
        cnt = len(self.tahsin)
        grade = last.grade or 'A'
        status = last.status_lulus or ('Lulus' if grade in ['A', 'B'] else 'Perlu Bimbingan')
        
        match_jilid = re.search(r'jilid\s*(\d+)', last_materi, re.IGNORECASE)
        match_juz = re.search(r'juz\s*(\d+)', last_materi, re.IGNORECASE)
        
        if match_jilid:
            jilid_num = min(int(match_jilid.group(1)), 6)
            pct = int((jilid_num / 6) * 100)
            label = f"Wafa Jilid {jilid_num} - {last_materi}"
            deskripsi = f"Capaian Wafa Jilid {jilid_num}/6 ({pct}%) - {cnt} kali evaluasi"
        elif match_juz:
            juz_num = min(int(match_juz.group(1)), 30)
            pct = int((juz_num / 30) * 100)
            label = f"Al-Qur'an Juz {juz_num} - {last_materi}"
            deskripsi = f"Capaian Juz {juz_num}/30 ({pct}%) - {cnt} kali evaluasi"
        else:
            pct = min(max(cnt * 10, 15), 100)
            label = last_materi
            deskripsi = f"Tercatat {cnt} kali evaluasi capaian Tahsin"

        return {
            "label": label,
            "percent": pct,
            "deskripsi": deskripsi,
            "status": status,
            "evaluasi": last.catatan or "Fasih, makharijul huruf dan tajwid sangat baik."
        }

    @property
    def progress_tahfidz_info(self):
        if not self.tahfidz:
            return {"label": "Target Juz 30 (Mulai)", "percent": 0, "deskripsi": "Belum ada riwayat setoran", "status": "Belum Dinilai", "evaluasi": "-"}
            
        last = self.tahfidz[-1]
        last_materi = last.hafalan_terakhir or ""
        cnt = len(self.tahfidz)
        pct = min(max(cnt * 10, 15), 100)
        grade = last.grade or 'A'
        status = last.status_lulus or ('Lulus' if grade in ['A', 'B'] else 'Perlu Bimbingan')
        return {
            "label": f"{last_materi}",
            "percent": pct,
            "deskripsi": f"Tercatat {cnt} kali setoran hafalan mutqin",
            "status": status,
            "evaluasi": last.catatan or "Hafalan lancar, mutqin dan tajwid terjaga."
        }

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
            "rata_rata_tahsin": self.rata_rata_tahsin,
            "grade_tahsin": self.grade_tahsin,
            "status_lulus_tahsin": self.status_lulus_tahsin,
            "rata_rata_tahfidz": self.rata_rata_tahfidz,
            "grade_tahfidz": self.grade_tahfidz,
            "status_lulus_tahfidz": self.status_lulus_tahfidz,
            "rata_rata_nilai": self.rata_rata_nilai,
            "grade_rata_rata": self.grade_rata_rata,
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
        if key == 'has_catatan_ortu': return self.has_catatan_ortu
        if key == 'has_paraf_ortu': return self.has_paraf_ortu
        if key == 'total_catatan_ortu': return self.total_catatan_ortu
        if key == 'status': return self.status_clean
        return getattr(self, key)
