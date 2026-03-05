from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, PasswordField, SubmitField, FloatField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, NumberRange
from models.user import User

class RegistrationForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Usuário já existe.')

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Login')

class CasoForm(FlaskForm):
    cliente_nome = StringField('Nome do Cliente', validators=[DataRequired()])
    pedido_numero = StringField('Número do Pedido', validators=[DataRequired()])
    nf_numero = StringField('Número da NF', validators=[DataRequired()])
    nf_referencia = StringField('NF de Referência', validators=[Optional()])  # NOVO
    
    # NOVOS CAMPOS DE VALOR
    valor_compra = FloatField('Valor da Compra (R$)', 
                             validators=[Optional(), NumberRange(min=0, message='Valor não pode ser negativo')])
    valor_fabrica = FloatField('Valor para Fábrica (R$)', 
                              validators=[Optional(), NumberRange(min=0, message='Valor não pode ser negativo')])
    
    tipo_caso = SelectField('Tipo de Caso', 
                          choices=[('troca', 'Troca'), 
                                 ('devolucao', 'Devolução'), 
                                 ('defeito', 'Defeito')])
    descricao = TextAreaField('Descrição', validators=[DataRequired()])
    fotos = FileField('Fotos', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    submit = SubmitField('Registrar')

class FiltroForm(FlaskForm):  # NOVO: Formulário de filtros
    cliente = StringField('Cliente')
    pedido = StringField('Pedido')
    nf = StringField('NF')
    status = SelectField('Status', choices=[('', 'Todos'), 
                                          ('aguardando', 'Aguardando'),
                                          ('aprovado', 'Aprovado'),
                                          ('reprovado', 'Reprovado')])
    data_inicio = DateField('Data Início', validators=[Optional()])
    data_fim = DateField('Data Fim', validators=[Optional()])
    submit = SubmitField('Filtrar')