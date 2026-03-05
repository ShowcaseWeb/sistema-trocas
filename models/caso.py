from . import db
from datetime import datetime

class Caso(db.Model):
    __tablename__ = 'casos'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_nome = db.Column(db.String(100), nullable=False)
    pedido_numero = db.Column(db.String(50), nullable=False)
    nf_numero = db.Column(db.String(50), nullable=False)
    nf_referencia = db.Column(db.String(50))
    tipo_caso = db.Column(db.String(20), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    
    # Valores
    valor_compra = db.Column(db.Float, default=0.0)
    valor_fabrica = db.Column(db.Float, default=0.0)
    
    # Status e datas
    status = db.Column(db.String(20), default='aguardando')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data_aprovacao = db.Column(db.DateTime)
    data_reprovacao = db.Column(db.DateTime)
    
    # Chaves estrangeiras (SEM backref aqui)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    aprovado_por_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reprovado_por_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relacionamento com uploads
    uploads = db.relationship('Upload', backref='caso', lazy=True, cascade='all, delete-orphan')
    
    # NOTA: Os backrefs para User estão definidos LA no models/user.py
    
    def __repr__(self):
        return f'<Caso {self.id} - {self.cliente_nome}>'

class Upload(db.Model):
    __tablename__ = 'uploads'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    filepath = db.Column(db.String(300), nullable=False)
    filetype = db.Column(db.String(50))
    data_upload = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Chave estrangeira
    caso_id = db.Column(db.Integer, db.ForeignKey('casos.id'), nullable=False)
    
    def __repr__(self):
        return f'<Upload {self.filename}>'