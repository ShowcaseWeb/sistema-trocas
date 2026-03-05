<<<<<<< HEAD
import os

class Config:
    SECRET_KEY = 'minha-chave-secreta'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///trocas.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
=======
import os

class Config:
    SECRET_KEY = 'minha-chave-secreta'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///trocas.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
>>>>>>> 8b74d408e92812e0b911c23f5103aeb050e23f8b
    UPLOAD_FOLDER = os.path.join('static', 'uploads')