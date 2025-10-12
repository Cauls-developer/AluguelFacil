from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.textlabels import Label
from reportlab.lib.units import cm
from datetime import date
import re
import os


def gerar_conta_inquilino(dados: dict):
    """
    Gera uma conta de energia elétrica personalizada para inquilinos em 1 página.
    """

    # === Nome do arquivo automático ===
    nome_limpo = re.sub(r'[^A-Za-z0-9]+', '_', dados["inquilino"]).strip("_")
    mes_ano = dados["mes_referencia"].replace(" ", "_").replace("/", "_")
    output_path = f"{nome_limpo}_{mes_ano}.pdf"

    # === Documento configurado para caber em 1 página ===
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='TitleCenter', fontSize=16, alignment=1, textColor=colors.HexColor("#0D47A1"), spaceAfter=8))
    styles.add(ParagraphStyle(name='SectionTitle', fontSize=11, textColor=colors.HexColor("#1565C0"), spaceAfter=4))
    styles.add(ParagraphStyle(name='NormalText', fontSize=9, leading=12))
    styles.add(ParagraphStyle(name='BigValue', fontSize=16, textColor=colors.red, alignment=1, spaceAfter=4))
    styles.add(ParagraphStyle(name='Footer', fontSize=8, alignment=1, textColor=colors.grey))

    content = []

    # === CABEÇALHO ===
    if dados.get("logo"):
        try:
            content.append(Image(dados["logo"], width=60, height=40))
        except Exception:
            pass

    content.append(Paragraph("<b>Conta de Energia Elétrica — Residencial</b>", styles['TitleCenter']))
    content.append(Spacer(1, 8))

    # === INFORMAÇÕES DO INQUILINO ===
    content.append(Paragraph("<b>Informações do Inquilino</b>", styles['SectionTitle']))

    tabela_inquilino = Table([
        ["Inquilino", dados["inquilino"]],
        ["Endereço", dados["endereco"]],
        ["Referência", dados["mes_referencia"]],
        ["Vencimento", dados["vencimento"]],
    ], colWidths=[3.5*cm, 10*cm])

    tabela_inquilino.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    content.append(tabela_inquilino)
    content.append(Spacer(1, 8))

    # === CONSUMO ===
    content.append(Paragraph("<b>Leituras de Consumo</b>", styles['SectionTitle']))
    data_consumo = [["Data", "Leitura (kWh)"]] + [[c["data"], str(c["leitura"])] for c in dados["leituras"]]
    tabela_consumo = Table(data_consumo, colWidths=[4*cm, 4*cm])
    tabela_consumo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E3F2FD")),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    ]))
    content.append(tabela_consumo)
    content.append(Paragraph(f"<b>Consumo Total:</b> {dados['consumo_total']} kWh", styles['NormalText']))
    content.append(Spacer(1, 8))

    # === VALORES ===
    content.append(Paragraph("<b>Resumo Financeiro</b>", styles['SectionTitle']))
    tabela_valores = Table(
        [["Descrição", "Valor (R$)"]] + dados["itens_financeiros"],
        colWidths=[7*cm, 3*cm]
    )
    tabela_valores.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E3F2FD")),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    content.append(tabela_valores)
    content.append(Spacer(1, 4))

    content.append(Paragraph("<b>Total a Pagar</b>", styles['SectionTitle']))
    content.append(Paragraph(f"R$ {dados['total']:.2f}", styles['BigValue']))
    content.append(Spacer(1, 6))

    # === PAGAMENTO ===
    content.append(Paragraph("<b>Dados para Pagamento</b>", styles['SectionTitle']))
    tabela_pagamento = Table([
        ["Banco", dados["banco"]],
        ["Titular PIX", dados["titular_pix"]],
        ["Chave PIX", dados["chave_pix"]],
    ], colWidths=[4*cm, 8*cm])
    tabela_pagamento.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ]))
    content.append(tabela_pagamento)
    content.append(Spacer(1, 10))

    # === GRÁFICO DE CONSUMO ===
    meses = [h['mes'] for h in dados['historico_consumo']]
    valores = [h['valor'] for h in dados['historico_consumo']]

    drawing = Drawing(350, 130)
    bc = VerticalBarChart()
    bc.x = 35
    bc.y = 25
    bc.height = 90
    bc.width = 270
    bc.data = [valores]
    bc.categoryAxis.categoryNames = meses
    bc.barWidth = 20
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = max(valores) * 1.2
    bc.valueAxis.valueStep = max(valores) // 4 if max(valores) > 0 else 100
    bc.bars[0].fillColor = colors.HexColor("#64B5F6")
    drawing.add(bc)

    content.append(drawing)
    content.append(Spacer(1, 6))

    # === RODAPÉ ===
    content.append(Paragraph("Gerado automaticamente em " + str(date.today()), styles['Footer']))

    # === GERAÇÃO DO PDF ===
    doc.build(content)
    print(f"✅ Conta gerada com sucesso: {output_path}")
    return output_path