import os
from flask import current_app
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta

def calcular_consumo_luz(kwh_inicial, kwh_final, valor_kwh):
    """Calcula o consumo de luz e o valor a ser pago."""
    consumo = kwh_final - kwh_inicial
    valor = consumo * valor_kwh
    return consumo, valor

def gerar_pdf_nota(nota):
    """Gera um PDF para uma nota."""
    filename = f"nota_{nota.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(current_app.root_path, 'static', 'pdfs', filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    elements = []

    # Cabeçalho da nota
    data = [
        ["Nota de Aluguel"],
        [f"Data de Emissão: {nota.data_emissao.strftime('%d/%m/%Y')}"],
        [f"Inquilino: {nota.usuario.nome}"],
        [f"Endereço: {nota.casa.endereco}"],
        [""],
        ["Descrição", "Valor"]
    ]

    # Itens da nota
    for item in nota.itens:
        data.append([item.descricao, f"R$ {item.valor:.2f}"])

    # Total
    data.append(["Total", f"R$ {nota.valor_total:.2f}"])

    # Criar tabela
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table)
    doc.build(elements)

    return filename

def enviar_email(destinatario, assunto, corpo, anexo=None):
    """Envia um email com ou sem anexo."""
    remetente = current_app.config['EMAIL_REMETENTE']
    senha = current_app.config['EMAIL_SENHA']

    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = assunto

    msg.attach(MIMEText(corpo, 'plain'))

    if anexo:
        with open(anexo, "rb") as file:
            part = MIMEApplication(file.read(), Name=os.path.basename(anexo))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(anexo)}"'
        msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(remetente, senha)
    text = msg.as_string()
    server.sendmail(remetente, destinatario, text)
    server.quit()

def calcular_juros_atraso(valor, dias_atraso, taxa_diaria=0.0033):
    """Calcula juros por atraso no pagamento."""
    return valor * (1 + taxa_diaria) ** dias_atraso - valor

def verificar_contas_vencidas():
    """Verifica contas vencidas e retorna uma lista de contas em atraso."""
    from .models import Conta  # Importação local para evitar importação circular
    hoje = datetime.now().date()
    contas_vencidas = Conta.query.filter(Conta.data_vencimento < hoje, Conta.status != 'paga').all()
    return contas_vencidas

def gerar_relatorio_inadimplencia(data_inicio, data_fim):
    """Gera um relatório de inadimplência para um período específico."""
    from .models import Conta  # Importação local para evitar importação circular
    contas_vencidas = Conta.query.filter(
        Conta.data_vencimento.between(data_inicio, data_fim),
        Conta.status != 'paga'
    ).all()

    relatorio = []
    for conta in contas_vencidas:
        dias_atraso = (datetime.now().date() - conta.data_vencimento).days
        juros = calcular_juros_atraso(conta.valor_total, dias_atraso)
        relatorio.append({
            'inquilino': conta.casa.inquilinos[0].nome if conta.casa.inquilinos else 'N/A',
            'endereco': conta.casa.endereco,
            'valor_original': conta.valor_total,
            'dias_atraso': dias_atraso,
            'juros': juros,
            'valor_total': conta.valor_total + juros
        })

    return relatorio