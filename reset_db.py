<<<<<<< HEAD
from app import app, db

with app.app_context():
    print("Apagando banco de dados...")
    db.drop_all()
    print("Recriando banco de dados...")
    db.create_all()
=======
from app import app, db

with app.app_context():
    print("Apagando banco de dados...")
    db.drop_all()
    print("Recriando banco de dados...")
    db.create_all()
>>>>>>> 8b74d408e92812e0b911c23f5103aeb050e23f8b
    print("✅ Banco de dados recriado com sucesso!")