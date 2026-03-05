import os

class Config:
    SECRET_KEY = 'minha-chave-secreta'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///trocas.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join('static', 'uploads')