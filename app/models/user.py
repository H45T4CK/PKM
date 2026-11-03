from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    nama = db.Column(db.String(150), nullable=True)
    kelas = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default='Aktif')

    siswa_binaan = db.relationship('Siswa', backref='ortu', lazy=True)

    def set_password(self, plain_password):
        self.password = generate_password_hash(plain_password)

    def check_password(self, plain_password):
        if not self.password.startswith('pbkdf2:') and not self.password.startswith('scrypt:'):
            return self.password == plain_password
        return check_password_hash(self.password, plain_password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "nama": self.nama or self.username,
            "kelas": self.kelas or "-",
            "status": self.status or "Aktif"
        }

    def __getitem__(self, key):
        return getattr(self, key)