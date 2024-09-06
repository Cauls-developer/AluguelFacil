from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FloatField, DateField, FieldList, FormField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from .models import Usuario

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistroForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirma_senha = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('senha')])
    submit = SubmitField('Registrar')

    def validate_email(self, email):
        user = Usuario.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email já está registrado. Por favor, use um diferente.')

class CasaForm(FlaskForm):
    endereco = StringField('Endereço', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('Adicionar Casa')

class ContaForm(FlaskForm):
    tipo = SelectField('Tipo de Conta', choices=[('agua', 'Água'), ('luz', 'Luz')], validators=[DataRequired()])
    data_emissao = DateField('Data de Emissão', format='%Y-%m-%d', validators=[DataRequired()])
    data_vencimento = DateField('Data de Vencimento', format='%Y-%m-%d', validators=[DataRequired()])
    valor_total = FloatField('Valor Total', validators=[DataRequired()])
    casa = SelectField('Casa', coerce=int, validators=[DataRequired()])
    
    # Campos específicos para conta de luz
    kwh_inicial = FloatField('KWh Inicial')
    kwh_final = FloatField('KWh Final')
    valor_kwh = FloatField('Valor do KWh')

    submit = SubmitField('Adicionar Conta')

    def validate_kwh(self, field):
        if self.tipo.data == 'luz' and not field.data:
            raise ValidationError('Este campo é obrigatório para contas de luz.')

    validate_kwh_inicial = validate_kwh
    validate_kwh_final = validate_kwh
    validate_valor_kwh = validate_kwh

class PagamentoForm(FlaskForm):
    valor = FloatField('Valor do Pagamento', validators=[DataRequired()])
    conta = SelectField('Conta', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Registrar Pagamento')

class ItemNotaForm(FlaskForm):
    descricao = StringField('Descrição', validators=[DataRequired()])
    valor = FloatField('Valor', validators=[DataRequired()])

class NotaForm(FlaskForm):
    valor_total = FloatField('Valor Total', validators=[DataRequired()])
    usuario = SelectField('Inquilino', coerce=int, validators=[DataRequired()])
    casa = SelectField('Casa', coerce=int, validators=[DataRequired()])
    itens = FieldList(FormField(ItemNotaForm), min_entries=1)
    submit = SubmitField('Emitir Nota')

class RelatorioForm(FlaskForm):
    tipo_relatorio = SelectField('Tipo de Relatório', choices=[
        ('financeiro', 'Relatório Financeiro'),
        ('consumo', 'Relatório de Consumo'),
        ('inadimplencia', 'Relatório de Inadimplência')
    ])
    data_inicio = DateField('Data de Início', format='%Y-%m-%d', validators=[DataRequired()])
    data_fim = DateField('Data de Fim', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Gerar Relatório')