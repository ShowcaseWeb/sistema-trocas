from app import app, db

with app.app_context():
    print("Apagando banco de dados...")
    db.drop_all()
    print("Recriando banco de dados...")
    db.create_all()
    print("✅ Banco de dados recriado com sucesso!")