from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    casas = db.relationship('Casa', secondary='inquilino_casa', back_populates='inquilinos')
    pagamentos = db.relationship('Pagamento', back_populates='usuario')

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

class Casa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    endereco = db.Column(db.String(200), nullable=False)
    inquilinos = db.relationship('Usuario', secondary='inquilino_casa', back_populates='casas')
    contas = db.relationship('Conta', back_populates='casa')

inquilino_casa = db.Table('inquilino_casa',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuario.id'), primary_key=True),
    db.Column('casa_id', db.Integer, db.ForeignKey('casa.id'), primary_key=True)
)

class Conta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)  # 'água' ou 'luz'
    data_emissao = db.Column(db.Date, nullable=False)
    data_vencimento = db.Column(db.Date, nullable=False)
    valor_total = db.Column(db.Float, nullable=False)
    casa_id = db.Column(db.Integer, db.ForeignKey('casa.id'), nullable=False)
    casa = db.relationship('Casa', back_populates='contas')
    
    # Campos específicos para conta de luz
    kwh_inicial = db.Column(db.Float)
    kwh_final = db.Column(db.Float)
    valor_kwh = db.Column(db.Float)

    pagamentos = db.relationship('Pagamento', back_populates='conta')

class Pagamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    data_pagamento = db.Column(db.DateTime, default=datetime.utcnow)
    conta_id = db.Column(db.Integer, db.ForeignKey('conta.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    conta = db.relationship('Conta', back_populates='pagamentos')
    usuario = db.relationship('Usuario', back_populates='pagamentos')

class Nota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_emissao = db.Column(db.DateTime, default=datetime.utcnow)
    valor_total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pendente')  # 'pendente', 'paga', 'atrasada'
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    casa_id = db.Column(db.Integer, db.ForeignKey('casa.id'), nullable=False)
    
    usuario = db.relationship('Usuario')
    casa = db.relationship('Casa')
    itens = db.relationship('ItemNota', back_populates='nota')

class ItemNota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    nota_id = db.Column(db.Integer, db.ForeignKey('nota.id'), nullable=False)
    
    nota = db.relationship('Nota', back_populates='itens')