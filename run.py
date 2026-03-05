<<<<<<< HEAD
from app import app, db

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Banco de dados criado!")
=======
from app import app, db

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Banco de dados criado!")
>>>>>>> 8b74d408e92812e0b911c23f5103aeb050e23f8b
    app.run(debug=True)