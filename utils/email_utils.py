from flask_mail import Message
from flask import url_for
from threading import Thread
import os

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def enviar_email_aprovacao(app, mail, caso, uploads):
    try:
        # Construir o email
        assunto = f'Caso #{caso.id} - Aprovado - {caso.cliente_nome}'
        
        # Criar corpo do email HTML
        corpo_html = f"""
        <html>
        <body>
            <h2>Caso Aprovado - #{caso.id}</h2>
            
            <h3>Informações do Cliente:</h3>
            <ul>
                <li><strong>Nome:</strong> {caso.cliente_nome}</li>
                <li><strong>Pedido:</strong> {caso.pedido_numero}</li>
                <li><strong>NF:</strong> {caso.nf_numero}</li>
                <li><strong>Tipo:</strong> {caso.tipo_caso}</li>
                <li><strong>Data:</strong> {caso.data_criacao.strftime('%d/%m/%Y %H:%M')}</li>
            </ul>
            
            <h3>Descrição:</h3>
            <p>{caso.descricao}</p>
            
            <h3>Arquivos Anexados:</h3>
            <ul>
        """
        
        # Adicionar links dos arquivos
        for upload in uploads:
            file_url = url_for('static', filename=f'uploads/{upload.filename}', _external=True)
            corpo_html += f'<li><a href="{file_url}">{upload.filename}</a></li>'
        
        corpo_html += """
            </ul>
            
            <p>Este caso foi aprovado e está pronto para processamento.</p>
            <p>Atenciosamente,<br>Sistema de Gestão de Trocas e Devoluções</p>
        </body>
        </html>
        """
        
        # Criar mensagem
        msg = Message(
            subject=assunto,
            recipients=[app.config['MAIL_USERNAME']],  # Email do SAC
            html=corpo_html
        )
        
        # Anexar arquivos
        for upload in uploads:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], upload.filename)
            if os.path.exists(file_path):
                with app.open_resource(file_path) as fp:
                    msg.attach(upload.filename, f"image/{upload.filename.split('.')[-1]}", fp.read())
        
        # Enviar email em thread separada
        thr = Thread(target=send_async_email, args=[app, msg])
        thr.start()
        
        return True
    except Exception as e:
        print(f"Erro ao enviar email: {str(e)}")
        return False