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


class AppSetting(db.Model):
    __tablename__ = 'app_setting'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(100), nullable=False)

    @classmethod
    def get_val(cls, key_name, default_val=''):
        item = cls.query.filter_by(key=key_name).first()
        return item.value if item else default_val

    @classmethod
    def set_val(cls, key_name, val_name):
        item = cls.query.filter_by(key=key_name).first()
        if not item:
            item = cls(key=key_name, value=val_name)
            db.session.add(item)
        else:
            item.value = val_name
        db.session.commit()