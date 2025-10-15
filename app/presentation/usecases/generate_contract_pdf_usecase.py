from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether
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
        pass  # Se não conseguir, usa o padrão


def traduzir_mes(data):
    """Traduz mês para português caso o locale não funcione"""
    meses_pt = {
        'January': 'janeiro', 'February': 'fevereiro', 'March': 'março',
        'April': 'abril', 'May': 'maio', 'June': 'junho',
        'July': 'julho', 'August': 'agosto', 'September': 'setembro',
        'October': 'outubro', 'November': 'novembro', 'December': 'dezembro'
    }
    
    # Tenta formatar com locale
    try:
        data_formatada = data.strftime('%d de %B de %Y')
    except:
        data_formatada = data.strftime('%d de %B de %Y')
    
    # Substitui meses em inglês por português
    for en, pt in meses_pt.items():
        data_formatada = data_formatada.replace(en, pt)
    
    return data_formatada


def numero_por_extenso(numero):
    """Converte número em extenso (simplificado para 1-12)"""
    extenso = {
        1: 'um', 2: 'dois', 3: 'três', 4: 'quatro', 5: 'cinco', 6: 'seis',
        7: 'sete', 8: 'oito', 9: 'nove', 10: 'dez', 11: 'onze', 12: 'doze',
        13: 'treze', 14: 'quatorze', 15: 'quinze', 16: 'dezesseis', 
        17: 'dezessete', 18: 'dezoito', 19: 'dezenove', 20: 'vinte',
        24: 'vinte e quatro', 30: 'trinta', 31: 'trinta e um',
        60: 'sessenta'
    }
    return extenso.get(numero, str(numero))


def valor_por_extenso(valor):
    """Converte valor em reais por extenso (simplificado)"""
    partes = str(valor).split('.')
    reais = int(partes[0])
    centavos = int(partes[1]) if len(partes) > 1 else 0
    
    # Simplificado - apenas para valores comuns
    if reais < 1000:
        return f"{numero_por_extenso(reais)} reais"
    elif reais == 900:
        return "novecentos reais"
    elif reais == 1800:
        return "um mil e oitocentos reais"
    else:
        return f"{reais} reais"


def gerar_contrato_locacao(dados: dict):
    """
    Gera um contrato de locação residencial em PDF baseado no modelo fornecido.
    
    Dados esperados:
    - locador: dict com nome, nacionalidade, estado_civil, profissao, rg, cpf, endereco
    - locatario: dict com nome, nacionalidade, estado_civil, profissao, data_nascimento, rg, cpf, endereco
    - imovel: dict com descricao_completa (sala, quartos, etc), endereco_completo
    - valores: dict com aluguel, caucao, seguro_fianca, dia_pagamento
    - datas: dict com inicio, fim, duracao_meses
    - multas: dict com atraso_percentual, juros_dia, rescisao_meses
    """
    
    # Nome do arquivo
    nome_limpo = re.sub(r'[^A-Za-z0-9]+', '_', dados["locatario"]["nome"]).strip("_")
    data_str = dados["datas"]["inicio"].strftime('%Y_%m_%d')
    output_path = f"Contrato_{nome_limpo}_{data_str}.pdf"
    
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
    
    # Remove estilos existentes se já foram definidos
    if 'ContractTitle' not in styles:
        styles.add(ParagraphStyle(
            name='ContractTitle', 
            fontSize=14, 
            alignment=TA_CENTER, 
            textColor=colors.black,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
    
    if 'ContractSubtitle' not in styles:
        styles.add(ParagraphStyle(
            name='ContractSubtitle', 
            fontSize=12, 
            alignment=TA_CENTER,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))
    
    if 'ContractClausula' not in styles:
        styles.add(ParagraphStyle(
            name='ContractClausula', 
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
    
    if 'ContractBody' not in styles:
        styles.add(ParagraphStyle(
            name='ContractBody', 
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            leading=14
        ))
    
    content = []
    
    # Título
    content.append(Paragraph("<b>CONTRATO DE LOCAÇÃO RESIDENCIAL COM CAUÇÃO</b>", styles['ContractTitle']))
    content.append(Spacer(1, 0.5*cm))
    
    # Identificação das Partes
    content.append(Paragraph("<b>IDENTIFICAÇÃO DAS PARTES CONTRATANTES</b>", styles['ContractSubtitle']))
    content.append(Spacer(1, 0.3*cm))
    
    # Locador
    loc = dados["locador"]
    locador_texto = f"""<b>LOCADOR: {loc['nome'].upper()}</b>, {loc['nacionalidade']}, {loc['estado_civil']}, 
    {loc['profissao']}, portador(a) da Cédula de Identidade RG sob o nº {loc['rg']} expedida pela SSP/BA, 
    inscrito(a) no CPF/MF sob o nº {loc['cpf']}, residente e domiciliado(a) em {loc['endereco']}."""
    content.append(Paragraph(locador_texto, styles['ContractBody']))
    content.append(Spacer(1, 0.3*cm))
    
    # Locatário
    locat = dados["locatario"]
    if isinstance(locat['data_nascimento'], datetime):
        data_nasc_str = traduzir_mes(locat['data_nascimento'])
    else:
        data_nasc_str = locat['data_nascimento']
    
    locatario_texto = f"""<b>LOCATÁRIO: {locat['nome'].upper()}</b>, {locat['nacionalidade']}, {locat['estado_civil']}, 
    {locat['profissao']}, nascido(a) em {data_nasc_str}, portador(a) da Cédula de Identidade sob o nº 
    {locat['rg']} expedida por SSP/BA, inscrito(a) no CPF/MF sob o nº {locat['cpf']}, residente e 
    domiciliado(a) em {locat['endereco']}."""
    content.append(Paragraph(locatario_texto, styles['ContractBody']))
    content.append(Spacer(1, 0.5*cm))
    
    # Introdução
    intro = """As partes acima identificadas têm, entre si, justas e acertadas o presente CONTRATO DE 
    LOCAÇÃO RESIDENCIAL COM CAUÇÃO, que se regerá pelas cláusulas seguintes e pelas condições de preços, 
    forma e termo de pagamento descrito no presente."""
    content.append(Paragraph(intro, styles['ContractBody']))
    content.append(Spacer(1, 0.5*cm))
    
    # DO OBJETO DO CONTRATO
    content.append(Paragraph("<b>DO OBJETO DO CONTRATO</b>", styles['ContractSubtitle']))
    content.append(Spacer(1, 0.3*cm))
    
    imovel = dados["imovel"]
    clausula1 = f"""<b>Cláusula 1ª.</b> O presente contrato tem como objeto a locação do imóvel de 
    propriedade do LOCADOR, composto por {imovel['descricao_completa']}, situado em {imovel['endereco_completo']}."""
    content.append(Paragraph(clausula1, styles['ContractBody']))
    content.append(Spacer(1, 0.3*cm))
    
    # DA UTILIZAÇÃO DO IMÓVEL
    content.append(Paragraph("<b>DA UTILIZAÇÃO DO IMÓVEL</b>", styles['ContractSubtitle']))
    content.append(Spacer(1, 0.3*cm))
    
    clausula2 = """<b>Cláusula 2ª.</b> A presente Locação destina-se restritivamente ao uso do imóvel 
    para fins residenciais, ficando proibida a sublocação ou destinação diversa da natureza a que se destina."""
    content.append(Paragraph(clausula2, styles['ContractBody']))
    content.append(Spacer(1, 0.5*cm))
    
    # DAS CONDIÇÕES DO IMÓVEL
    content.append(Paragraph("<b>DAS CONDIÇÕES DO IMÓVEL</b>", styles['ContractSubtitle']))
    content.append(Spacer(1, 0.3*cm))
    
    clausula3 = """<b>Cláusula 3ª.</b> Fica também acordado, que o imóvel será devolvido nas mesmas 
    condições em que foi entregue, além de, no ato da devolução e entrega das chaves, com todas as 
    despesas cabíveis ao LOCATÁRIO devidamente pagas, podendo o LOCADOR receber de forma diversa as 
    regras aqui estabelecidas."""
    content.append(Paragraph(clausula3, styles['ContractBody']))
    content.append(Spacer(1, 0.5*cm))
    
    # BENFEITORIAS E CONSTRUÇÕES
    content.append(Paragraph("<b>BENFEITORIAS E CONSTRUÇÕES</b>", styles['ContractSubtitle']))
    content.append(Spacer(1, 0.3*cm))
    
    clausulas_benfeitorias = [
        """<b>Cláusula 4ª.</b> Qualquer benfeitoria, construção ou reforma de qualquer natureza que seja 
        destinada ao imóvel objeto deste CONTRATO, deverá de imediato, ser submetida à autorização expressa 
        do LOCADOR.""",
        
        """<b>Cláusula 5ª.</b> Vindo a ser feita benfeitoria, será facultado ao LOCADOR aceitá-la ou não, 
        restando ao LOCATÁRIO em caso de não aceitação, ao final do contrato ou na entrega deste, modificar 
        o imóvel para a maneira que lhe foi entregue.""",
        
        """<b>Cláusula 6ª.</b> As benfeitorias, consertos ou reparos farão parte integrante do imóvel, 
        não assistindo ao LOCATÁRIO o direito de retenção ou indenização sobre ela."""
    ]
    
    for clausula in clausulas_benfeitorias:
        content.append(Paragraph(clausula, styles['ContractBody']))
        content.append(Spacer(1, 0.3*cm))
    
    content.append(Spacer(1, 0.3*cm))
    
    # DO SEGURO FIANÇA E CAUÇÃO
    content.append(Paragraph("<b>DO SEGURO FIANÇA E CAUÇÃO</b>", styles['ContractSubtitle']))
    content.append(Spacer(1, 0.3*cm))
    
    valores = dados["valores"]
    total_garantias = valores['caucao'] + valores['seguro_fianca']
    
    clausula12 = f"""<b>Cláusula 12ª.</b> O LOCATÁRIO concorda desde já, a pagar a título de seguro fiança, 
    o valor equivalente a 1 (um) mês de aluguel, no valor de R$ {valores['seguro_fianca']:.2f} 
    ({valor_por_extenso(valores['seguro_fianca'])}), e a título de caução o valor equivalente também a 1 (um) mês 
    de aluguel, no valor de R$ {valores['caucao']:.2f} ({valor_por_extenso(valores['caucao'])}), totalizando a 
    quantia de R$ {total_garantias:.2f} ({valor_por_extenso(total_garantias)})."""
    content.append(Paragraph(clausula12, styles['ContractBody']))
    content.append(Spacer(1, 0.3*cm))
    
    clausula13 = """<b>Cláusula 13ª.</b> O seguro fiança e o caução serão usados em todas as hipóteses as 
    quais se farão necessários recursos provenientes do LOCATÁRIO para cumprimento deste contrato."""
    content.append(Paragraph(clausula13, styles['ContractBody']))
    content.append(Spacer(1, 0.5*cm))
    
    # VALOR DO ALUGUEL
    content.append(Paragraph("<b>VALOR DO ALUGUEL, DESPESAS E TRIBUTOS</b>", styles['ContractSubtitle']))
    content.append(Spacer(1, 0.3*cm))
    
    datas = dados["datas"]
    primeira_data_pag = datas["inicio"].replace(day=valores['dia_pagamento'])
    primeira_data_pag_str = traduzir_mes(primeira_data_pag)
    
    clausula14 = f"""<b>Cláusula 14ª.</b> Como valor da locação o LOCATÁRIO se obrigará a pagar mensalmente 
    o valor total de R$ {valores['aluguel']:.2f} ({valor_por_extenso(valores['aluguel'])}) diretamente ao 
    LOCADOR, devendo fazê-lo todo dia {valores['dia_pagamento']} ({numero_por_extenso(valores['dia_pagamento'])}) 
    de cada mês, iniciando o pagamento a partir do dia {primeira_data_pag_str}."""
    content.append(Paragraph(clausula14, styles['ContractBody']))
    content.append(Spacer(1, 0.3*cm))
    
    multas = dados["multas"]
    paragrafo1 = f"""<b>Parágrafo Primeiro.</b> Caso o pagamento do aluguel não seja efetuado na data 
    acordada, incidirá multa de {multas['atraso_percentual']:.0f}%, mais juros de {multas['juros_dia']:.2f}% 
    ao dia sobre o valor do aluguel."""
    content.append(Paragraph(paragrafo1, styles['ContractBody']))
    content.append(Spacer(1, 0.5*cm))
    
    # DO PRAZO DE LOCAÇÃO
    content.append(Paragraph("<b>DO PRAZO DE LOCAÇÃO</b>", styles['ContractSubtitle']))
    content.append(Spacer(1, 0.3*cm))
    
    data_inicio_str = traduzir_mes(datas['inicio'])
    data_fim_str = traduzir_mes(datas['fim'])
    
    clausula15 = f"""<b>Cláusula 15ª.</b> A presente locação terá o prazo de {datas['duracao_meses']} 
    ({numero_por_extenso(datas['duracao_meses'])}) meses, com início no dia {data_inicio_str} 
    e término no dia {data_fim_str}."""
    content.append(Paragraph(clausula15, styles['ContractBody']))
    content.append(Spacer(1, 0.5*cm))
    
    # DA MULTA POR INFRAÇÃO
    content.append(Paragraph("<b>DA MULTA POR INFRAÇÃO</b>", styles['ContractSubtitle']))
    content.append(Spacer(1, 0.3*cm))
    
    clausula22 = f"""<b>Cláusula 22ª.</b> Caso o LOCATÁRIO devolva o imóvel antes do prazo mínimo de 
    {datas['duracao_meses']} ({numero_por_extenso(datas['duracao_meses'])}) meses da locação, pagará a 
    LOCADORA multa compensatória correspondente a {multas['rescisao_meses']} 
    ({numero_por_extenso(multas['rescisao_meses'])}) meses de aluguel em vigor à época."""
    content.append(Paragraph(clausula22, styles['ContractBody']))
    content.append(Spacer(1, 0.5*cm))
    
    # DO FORO
    content.append(Paragraph("<b>DO FORO</b>", styles['ContractSubtitle']))
    content.append(Spacer(1, 0.3*cm))
    
    clausula30 = """<b>Cláusula 30ª.</b> Para dirimir quaisquer controvérsias oriundas deste CONTRATO, 
    as partes elegem o foro da comarca de Salvador. Por estarem assim justos e contratados, firmam o 
    presente instrumento, em 2 (duas) vias de igual teor, juntamente com 2 (duas) testemunhas."""
    content.append(Paragraph(clausula30, styles['ContractBody']))
    content.append(Spacer(1, 0.5*cm))
    
    # Bloco de assinaturas - mantém tudo junto na mesma página
    assinaturas_content = []
    
    hoje = datetime.now()
    hoje_str = traduzir_mes(hoje)
    assinaturas_content.append(Paragraph(f"Salvador-BA, {hoje_str}.", styles['ContractBody']))
    assinaturas_content.append(Spacer(1, 1*cm))
    
    assinaturas = f"""
    <para align=center>
    ________________________________________________<br/>
    <b>{dados['locador']['nome'].upper()}</b><br/>
    <b>LOCADOR</b>
    </para>
    """
    assinaturas_content.append(Paragraph(assinaturas, styles['ContractBody']))
    assinaturas_content.append(Spacer(1, 0.8*cm))
    
    assinatura_locatario = f"""
    <para align=center>
    ________________________________________________<br/>
    <b>{dados['locatario']['nome'].upper()}</b><br/>
    <b>LOCATÁRIO</b>
    </para>
    """
    assinaturas_content.append(Paragraph(assinatura_locatario, styles['ContractBody']))
    assinaturas_content.append(Spacer(1, 0.8*cm))
    
    testemunhas = """
    <para align=left>
    <b>TESTEMUNHAS:</b><br/><br/>
    ________________________________________________<br/>
    NOME:<br/>
    CPF/MF:<br/><br/>
    ________________________________________________<br/>
    NOME:<br/>
    CPF/MF:
    </para>
    """
    assinaturas_content.append(Paragraph(testemunhas, styles['ContractBody']))
    
    # Adiciona o bloco de assinaturas mantendo tudo junto
    content.append(KeepTogether(assinaturas_content))
    
    # Gerar PDF
    doc.build(content)
    print(f"✅ Contrato gerado com sucesso: {output_path}")
    return output_path