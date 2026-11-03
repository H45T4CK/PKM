from app import db

class RecordsPoin(db.Model):
    __tablename__ = 'records_poin'
    id = db.Column(db.Integer, primary_key=True)
    siswa_id = db.Column(db.String(50), db.ForeignKey('siswa.id'), nullable=False)
    tanggal = db.Column(db.String(50), nullable=False)
    kategori = db.Column(db.String(50), nullable=False)
    deskripsi = db.Column(db.String(255), nullable=False)
    poin = db.Column(db.Integer, nullable=False)
    pencatat = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            "id": self.id, 
            "tanggal": self.tanggal, 
            "kategori": self.kategori, 
            "deskripsi": self.deskripsi, 
            "poin": self.poin, 
            "pencatat": self.pencatat or ""
        }
    def __getitem__(self, key): return getattr(self, key)


class RecordsTahsin(db.Model):
    __tablename__ = 'records_tahsin'
    id = db.Column(db.Integer, primary_key=True)
    siswa_id = db.Column(db.String(50), db.ForeignKey('siswa.id'), nullable=False)
    tanggal = db.Column(db.String(50), nullable=False)
    halaman_akhir = db.Column(db.String(150), nullable=False)
    catatan = db.Column(db.Text, nullable=True)
    ceklist_guru = db.Column(db.Boolean, default=True)
    ceklist_ortu = db.Column(db.Boolean, default=False)
    catatan_ortu = db.Column(db.Text, nullable=True)
    penilai = db.Column(db.String(100), nullable=True)
    grade = db.Column(db.String(5), nullable=True, default='A')
    nilai = db.Column(db.Integer, nullable=True, default=100)
    status_lulus = db.Column(db.String(20), nullable=True, default='Lulus')

    def to_dict(self):
        return {
            "id": self.id, 
            "tanggal": self.tanggal, 
            "halaman_akhir": self.halaman_akhir, 
            "catatan": self.catatan or "", 
            "ceklist_guru": bool(self.ceklist_guru), 
            "ceklist_ortu": bool(self.ceklist_ortu), 
            "catatan_ortu": self.catatan_ortu or "", 
            "penilai": self.penilai or "",
            "grade": self.grade or "A",
            "nilai": self.nilai if self.nilai is not None else 100,
            "status_lulus": self.status_lulus or "Lulus"
        }
    def __getitem__(self, key): return getattr(self, key)


class RecordsTahfidz(db.Model):
    __tablename__ = 'records_tahfidz'
    id = db.Column(db.Integer, primary_key=True)
    siswa_id = db.Column(db.String(50), db.ForeignKey('siswa.id'), nullable=False)
    tanggal = db.Column(db.String(50), nullable=False)
    hafalan_terakhir = db.Column(db.String(150), nullable=False)
    catatan = db.Column(db.Text, nullable=True)
    ceklist_guru = db.Column(db.Boolean, default=True)
    ceklist_ortu = db.Column(db.Boolean, default=False)
    catatan_ortu = db.Column(db.Text, nullable=True)
    penilai = db.Column(db.String(100), nullable=True)
    grade = db.Column(db.String(5), nullable=True, default='A')
    nilai = db.Column(db.Integer, nullable=True, default=100)
    status_lulus = db.Column(db.String(20), nullable=True, default='Lulus')

    def to_dict(self):
        return {
            "id": self.id, 
            "tanggal": self.tanggal, 
            "hafalan_terakhir": self.hafalan_terakhir, 
            "catatan": self.catatan or "", 
            "ceklist_guru": bool(self.ceklist_guru), 
            "ceklist_ortu": bool(self.ceklist_ortu), 
            "catatan_ortu": self.catatan_ortu or "", 
            "penilai": self.penilai or "",
            "grade": self.grade or "A",
            "nilai": self.nilai if self.nilai is not None else 100,
            "status_lulus": self.status_lulus or "Lulus"
        }
    def __getitem__(self, key): return getattr(self, key)
