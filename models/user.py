from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relacionamento com casos que o usuário CRIOU
    casos_criados = db.relationship('Caso', 
                                    foreign_keys='Caso.user_id',
                                    backref='usuario_criador', 
                                    lazy=True)
    
    # Relacionamento com casos que o usuário APROVOU
    casos_aprovados = db.relationship('Caso', 
                                      foreign_keys='Caso.aprovado_por_id',
                                      backref='usuario_aprovador', 
                                      lazy=True)
    
    # Relacionamento com casos que o usuário REPROVOU
    casos_reprovados = db.relationship('Caso', 
                                       foreign_keys='Caso.reprovado_por_id',
                                       backref='usuario_reprovador', 
                                       lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'