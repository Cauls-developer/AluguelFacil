from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, Usuario, Casa, Conta, Pagamento, Nota, ItemNota
from .forms import LoginForm, RegistroForm, CasaForm, ContaForm, PagamentoForm, NotaForm
from datetime import datetime

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('index.html')

@views.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(email=form.email.data).first()
        if user and user.check_senha(form.senha.data):
            login_user(user)
            return redirect(url_for('views.dashboard'))
        else:
            flash('Login inválido.')
    return render_template('login.html', form=form)

@views.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))

@views.route('/registro', methods=['GET', 'POST'])
def registro():
    form = RegistroForm()
    if form.validate_on_submit():
        user = Usuario(nome=form.nome.data, email=form.email.data)
        user.set_senha(form.senha.data)
        db.session.add(user)
        db.session.commit()
        flash('Registro bem-sucedido!')
        return redirect(url_for('views.login'))
    return render_template('registro.html', form=form)

@views.route('/dashboard')
@login_required
def dashboard():
    casas = Casa.query.all()
    contas = Conta.query.all()
    return render_template('dashboard.html', casas=casas, contas=contas)

@views.route('/casa/nova', methods=['GET', 'POST'])
@login_required
def nova_casa():
    form = CasaForm()
    if form.validate_on_submit():
        casa = Casa(endereco=form.endereco.data)
        db.session.add(casa)
        db.session.commit()
        flash('Nova casa adicionada!')
        return redirect(url_for('views.dashboard'))
    return render_template('nova_casa.html', form=form)

@views.route('/conta/nova', methods=['GET', 'POST'])
@login_required
def nova_conta():
    form = ContaForm()
    form.casa.choices = [(c.id, c.endereco) for c in Casa.query.all()]
    if form.validate_on_submit():
        conta = Conta(
            tipo=form.tipo.data,
            data_emissao=form.data_emissao.data,
            data_vencimento=form.data_vencimento.data,
            valor_total=form.valor_total.data,
            casa_id=form.casa.data
        )
        if form.tipo.data == 'luz':
            conta.kwh_inicial = form.kwh_inicial.data
            conta.kwh_final = form.kwh_final.data
            conta.valor_kwh = form.valor_kwh.data
        db.session.add(conta)
        db.session.commit()
        flash('Nova conta adicionada!')
        return redirect(url_for('views.dashboard'))
    return render_template('nova_conta.html', form=form)

@views.route('/pagamento/novo', methods=['GET', 'POST'])
@login_required
def novo_pagamento():
    form = PagamentoForm()
    form.conta.choices = [(c.id, f"{c.tipo} - {c.casa.endereco} - Vencimento: {c.data_vencimento}") for c in Conta.query.all()]
    if form.validate_on_submit():
        pagamento = Pagamento(
            valor=form.valor.data,
            data_pagamento=datetime.utcnow(),
            conta_id=form.conta.data,
            usuario_id=current_user.id
        )
        db.session.add(pagamento)
        db.session.commit()
        flash('Pagamento registrado!')
        return redirect(url_for('views.dashboard'))
    return render_template('novo_pagamento.html', form=form)

@views.route('/nota/nova', methods=['GET', 'POST'])
@login_required
def nova_nota():
    form = NotaForm()
    form.usuario.choices = [(u.id, u.nome) for u in Usuario.query.all()]
    form.casa.choices = [(c.id, c.endereco) for c in Casa.query.all()]
    if form.validate_on_submit():
        nota = Nota(
            valor_total=form.valor_total.data,
            usuario_id=form.usuario.data,
            casa_id=form.casa.data
        )
        for item in form.itens.data:
            item_nota = ItemNota(descricao=item['descricao'], valor=item['valor'])
            nota.itens.append(item_nota)
        db.session.add(nota)
        db.session.commit()
        flash('Nova nota emitida!')
        return redirect(url_for('views.dashboard'))
    return render_template('nova_nota.html', form=form)

@views.route('/relatorios')
@login_required
def relatorios():
    # Aqui você pode adicionar lógica para gerar relatórios
    return render_template('relatorios.html')