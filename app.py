import os
from flask import Flask, render_template, redirect, url_for, flash, request, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import datetime
from config import Config
from models import db
from models.user import User
from models.caso import Caso, Upload
from forms.forms import RegistrationForm, LoginForm, CasoForm, FiltroForm
from utils.email_utils import enviar_email_aprovacao
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Garantir pasta de uploads
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ============================================
# ROTAS PÚBLICAS
# ============================================

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registro feito com sucesso!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Usuário ou senha inválidos', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# ============================================
# ROTAS DO DASHBOARD E CASOS
# ============================================

@app.route('/dashboard')
@login_required
def dashboard():
    # Filtros
    cliente = request.args.get('cliente', '')
    pedido = request.args.get('pedido', '')
    nf = request.args.get('nf', '')
    status = request.args.get('status', '')
    
    query = Caso.query
    
    if cliente:
        query = query.filter(Caso.cliente_nome.contains(cliente))
    if pedido:
        query = query.filter(Caso.pedido_numero.contains(pedido))
    if nf:
        query = query.filter(Caso.nf_numero.contains(nf))
    if status:
        query = query.filter(Caso.status == status)
    
    casos = query.order_by(Caso.data_criacao.desc()).all()
    
    return render_template('dashboard.html', casos=casos)

@app.route('/novo_caso', methods=['GET', 'POST'])
@login_required
def novo_caso():
    form = CasoForm()
    
    if form.validate_on_submit():
        caso = Caso(
            cliente_nome=form.cliente_nome.data,
            pedido_numero=form.pedido_numero.data,
            nf_numero=form.nf_numero.data,
            nf_referencia=form.nf_referencia.data,
            valor_compra=form.valor_compra.data,
            valor_fabrica=form.valor_fabrica.data,
            tipo_caso=form.tipo_caso.data,
            descricao=form.descricao.data,
            user_id=current_user.id
        )
        db.session.add(caso)
        db.session.commit()
        
        # Salvar fotos
        if form.fotos.data:
            for foto in request.files.getlist('fotos'):
                if foto and foto.filename:
                    filename = secure_filename(f"{datetime.now().timestamp()}_{foto.filename}")
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    foto.save(filepath)
                    
                    upload = Upload(filename=filename, filepath=filepath, caso_id=caso.id)
                    db.session.add(upload)
            
            db.session.commit()
        
        flash('Caso registrado com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('novo_caso.html', form=form)

@app.route('/caso/<int:id>')
@login_required
def caso_detalhe(id):
    caso = Caso.query.get_or_404(id)
    return render_template('caso_detalhe.html', caso=caso)

# ============================================
# NOVAS ROTAS (EDIÇÃO, APROVAÇÃO, EXCLUSÃO)
# ============================================

@app.route('/caso/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_caso(id):
    caso = Caso.query.get_or_404(id)
    
    # Verificar permissão (só quem criou ou admin)
    if current_user.id != caso.user_id and current_user.username != 'admin':
        flash('Você não tem permissão para editar este caso.', 'danger')
        return redirect(url_for('caso_detalhe', id=id))
    
    form = CasoForm(obj=caso)
    
    if form.validate_on_submit():
        caso.cliente_nome = form.cliente_nome.data
        caso.pedido_numero = form.pedido_numero.data
        caso.nf_numero = form.nf_numero.data
        caso.nf_referencia = form.nf_referencia.data
        caso.valor_compra = form.valor_compra.data
        caso.valor_fabrica = form.valor_fabrica.data
        caso.tipo_caso = form.tipo_caso.data
        caso.descricao = form.descricao.data
        caso.data_atualizacao = datetime.utcnow()
        
        db.session.commit()
        flash('Caso atualizado com sucesso!', 'success')
        return redirect(url_for('caso_detalhe', id=id))
    
    return render_template('editar_caso.html', form=form, caso=caso)

@app.route('/caso/<int:id>/aprovar')
@login_required
def aprovar_caso(id):
    caso = Caso.query.get_or_404(id)
    caso.status = 'aprovado'
    caso.data_aprovacao = datetime.utcnow()
    caso.aprovado_por_id = current_user.id
    db.session.commit()
    
    # Enviar email
    enviar_email_aprovacao(app, mail, caso, caso.uploads)
    
    flash('Caso aprovado e email enviado!', 'success')
    return redirect(url_for('caso_detalhe', id=id))

@app.route('/caso/<int:id>/reprovar')
@login_required
def reprovar_caso(id):
    caso = Caso.query.get_or_404(id)
    caso.status = 'reprovado'
    caso.data_reprovacao = datetime.utcnow()
    caso.reprovado_por_id = current_user.id
    db.session.commit()
    flash('Caso reprovado!', 'warning')
    return redirect(url_for('caso_detalhe', id=id))

@app.route('/caso/<int:id>/apagar', methods=['POST'])
@login_required
def apagar_caso(id):
    caso = Caso.query.get_or_404(id)
    
    # Verificar permissão (só quem criou ou admin)
    if current_user.id != caso.user_id and current_user.username != 'admin':
        flash('Você não tem permissão para apagar este caso.', 'danger')
        return redirect(url_for('caso_detalhe', id=id))
    
    # Apagar fotos do disco
    for upload in caso.uploads:
        try:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], upload.filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Erro ao apagar arquivo: {e}")
    
    db.session.delete(caso)
    db.session.commit()
    flash('Caso apagado com sucesso!', 'success')
    return redirect(url_for('dashboard'))

# ============================================
# ROTAS DE EXPORTAÇÃO
# ============================================

@app.route('/exportar_excel')
@login_required
def exportar_excel():
    casos = Caso.query.all()
    
    data = []
    for caso in casos:
        data.append({
            'ID': caso.id,
            'Cliente': caso.cliente_nome,
            'Pedido': caso.pedido_numero,
            'NF': caso.nf_numero,
            'NF Referência': caso.nf_referencia or '',
            'Tipo': caso.tipo_caso,
            'Status': caso.status,
            'Valor Compra (R$)': caso.valor_compra or 0,
            'Valor Fábrica (R$)': caso.valor_fabrica or 0,
            'Data Criação': caso.data_criacao.strftime('%d/%m/%Y %H:%M'),
            'Data Aprovação': caso.data_aprovacao.strftime('%d/%m/%Y %H:%M') if caso.data_aprovacao else '',
            'Data Reprovação': caso.data_reprovacao.strftime('%d/%m/%Y %H:%M') if caso.data_reprovacao else '',
            'Data Atualização': caso.data_atualizacao.strftime('%d/%m/%Y %H:%M') if caso.data_atualizacao else '',
            'Descrição': caso.descricao
        })
    
    df = pd.DataFrame(data)
    
    # Criar arquivo Excel
    output = pd.ExcelWriter('casos.xlsx', engine='openpyxl')
    df.to_excel(output, index=False, sheet_name='Casos')
    output.close()
    
    return send_file('casos.xlsx', as_attachment=True, download_name='casos.xlsx')

# ============================================
# INICIALIZAÇÃO
# ============================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)