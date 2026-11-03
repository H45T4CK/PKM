from app import db
from app.models.user import User

def init_db_and_seed():
    db.create_all()

    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            username='admin',
            password='admin',
            role='admin',
            nama='Administrator SDIT',
            kelas='-',
            status='Aktif'
        )
        db.session.add(admin_user)
        db.session.commit()