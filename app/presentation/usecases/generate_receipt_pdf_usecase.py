from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import cm
from datetime import datetime
import re
import os
import locale

# Tenta configurar locale para português
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
    except:
        pass


def traduzir_mes(data):
    """Traduz mês para português"""
    meses_pt = {
        'January': 'janeiro', 'February': 'fevereiro', 'March': 'março',
        'April': 'abril', 'May': 'maio', 'June': 'junho',
        'July': 'julho', 'August': 'agosto', 'September': 'setembro',
        'October': 'outubro', 'November': 'novembro', 'December': 'dezembro'
    }
    
    try:
        data_formatada = data.strftime('%d de %B de %Y')
    except:
        data_formatada = data.strftime('%d de %B de %Y')
    
    for en, pt in meses_pt.items():
        data_formatada = data_formatada.replace(en, pt)
    
    return data_formatada


def gerar_recibo_pagamento(dados: dict):
    """
    Gera um recibo de pagamento em PDF.
    
    Dados esperados:
    - numero_recibo: número do recibo
    - valor: valor do pagamento
    - valor_extenso: valor por extenso
    - nome_pagador: nome de quem pagou
    - cpf_pagador: CPF de quem pagou (opcional)
    - nome_recebedor: nome de quem recebeu
    - cpf_recebedor: CPF de quem recebeu (opcional)
    - referente_a: descrição do que está sendo pago
    - descricao: descrição detalhada (opcional)
    - data_pagamento: data do pagamento
    - forma_pagamento: forma de pagamento (opcional)
    - observacoes: observações adicionais (opcional)
    """
    
    # Nome do arquivo
    nome_limpo = re.sub(r'[^A-Za-z0-9]+', '_', dados["nome_pagador"]).strip("_")
    data_str = dados["data_pagamento"].strftime('%Y_%m_%d')
    output_path = f"Recibo_{dados['numero_recibo']}_{nome_limpo}_{data_str}.pdf"
    
    # Configuração do documento
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    
    if 'ReceiptTitle' not in styles:
        styles.add(ParagraphStyle(
            name='ReceiptTitle',
            fontSize=18,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#1565C0"),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
    
    if 'ReceiptSubtitle' not in styles:
        styles.add(ParagraphStyle(
            name='ReceiptSubtitle',
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica'
        ))
    
    if 'ReceiptBody' not in styles:
        styles.add(ParagraphStyle(
            name='ReceiptBody',
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=16
        ))
    
    if 'ReceiptValue' not in styles:
        styles.add(ParagraphStyle(
            name='ReceiptValue',
            fontSize=16,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#2E7D32"),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
    
    content = []
    
    # Cabeçalho
    content.append(Paragraph("<b>RECIBO DE PAGAMENTO</b>", styles['ReceiptTitle']))
    content.append(Paragraph(f"Nº {dados['numero_recibo']}", styles['ReceiptSubtitle']))
    content.append(Spacer(1, 0.5*cm))
    
    # Valor em destaque
    content.append(Paragraph(f"R$ {dados['valor']:.2f}", styles['ReceiptValue']))
    content.append(Paragraph(f"({dados['valor_extenso']})", styles['ReceiptBody']))
    content.append(Spacer(1, 0.5*cm))
    
    # Corpo do recibo
    data_pagamento_str = traduzir_mes(dados['data_pagamento'])
    
    texto_recibo = f"""Recebi de <b>{dados['nome_pagador']}</b>"""
    
    if dados.get('cpf_pagador'):
        texto_recibo += f""", CPF nº <b>{dados['cpf_pagador']}</b>"""
    
    texto_recibo += f""", a quantia de <b>R$ {dados['valor']:.2f} ({dados['valor_extenso']})</b>, 
    referente a <b>{dados['referente_a']}</b>."""
    
    if dados.get('descricao'):
        texto_recibo += f""" {dados['descricao']}"""
    
    content.append(Paragraph(texto_recibo, styles['ReceiptBody']))
    content.append(Spacer(1, 0.5*cm))
    
    # Forma de pagamento
    if dados.get('forma_pagamento'):
        forma_pag_texto = {
            'dinheiro': 'dinheiro',
            'pix': 'PIX',
            'transferencia': 'transferência bancária',
            'cheque': 'cheque',
            'cartao': 'cartão'
        }.get(dados['forma_pagamento'].lower(), dados['forma_pagamento'])
        
        content.append(Paragraph(
            f"Forma de pagamento: <b>{forma_pag_texto}</b>",
            styles['ReceiptBody']
        ))
        content.append(Spacer(1, 0.3*cm))
    
    # Observações
    if dados.get('observacoes'):
        content.append(Paragraph(
            f"<b>Observações:</b> {dados['observacoes']}",
            styles['ReceiptBody']
        ))
        content.append(Spacer(1, 0.5*cm))
    
    # Tabela de informações
    info_data = [
        ['Data do Pagamento:', data_pagamento_str],
        ['Valor:', f"R$ {dados['valor']:.2f}"],
    ]
    
    info_table = Table(info_data, colWidths=[5*cm, 10*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#E3F2FD")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    
    content.append(info_table)
    content.append(Spacer(1, 1*cm))
    
    # Data e local
    hoje = datetime.now()
    hoje_str = traduzir_mes(hoje)
    content.append(Paragraph(
        f"Salvador-BA, {hoje_str}.",
        styles['ReceiptBody']
    ))
    content.append(Spacer(1, 2*cm))
    
    # Assinatura do recebedor
    assinatura = f"""
    <para align=center>
    ________________________________________________<br/>
    <b>{dados['nome_recebedor']}</b><br/>
    """
    
    if dados.get('cpf_recebedor'):
        assinatura += f"CPF: {dados['cpf_recebedor']}<br/>"
    
    assinatura += """
    <i>Recebedor</i>
    </para>
    """
    
    content.append(Paragraph(assinatura, styles['ReceiptBody']))
    content.append(Spacer(1, 1*cm))
    
    # Linha pontilhada para corte (para segunda via)
    content.append(Spacer(1, 0.5*cm))
    content.append(Paragraph(
        "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -",
        styles['ReceiptBody']
    ))
    content.append(Spacer(1, 0.3*cm))
    content.append(Paragraph(
        "<i>Via do Pagador</i>",
        styles['ReceiptSubtitle']
    ))
    
    # Gerar PDF
    doc.build(content)
    print(f"✅ Recibo gerado com sucesso: {output_path}")
    return output_path