from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from database.xml_storage import cargar_datos
import os

def generar_reporte_factura(numero_factura):
    try:
        facturas = cargar_datos('facturas')
        factura_data = None
        
        for factura in facturas:
            if factura['numero'] == numero_factura:
                factura_data = factura
                break
        
        if not factura_data:
            return None
        
        filename = f"factura_{numero_factura}.pdf"
        filepath = os.path.join('database', 'data', filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        elements.append(Paragraph("Tecnologías Chapinas, S.A.", styles['Title']))
        elements.append(Paragraph("Detalle de Factura", styles['Heading1']))
        elements.append(Spacer(1, 0.2*inch))
        
        info_data = [
            ['Número de Factura:', factura_data['numero']],
            ['NIT Cliente:', factura_data['nitCliente']],
            ['Fecha de Factura:', factura_data['fechaFactura']],
            ['Monto Total:', f"Q {float(factura_data['montoTotal']):.2f}"]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.3*inch))
        
        elements.append(Paragraph("Detalles de la Factura", styles['Heading2']))
        
        detalles_data = [['Instancia', 'Tiempo (horas)', 'Monto']]
        for detalle in factura_data['detalles']:
            detalles_data.append([
                detalle['idInstancia'],
                f"{float(detalle['tiempoTotal']):.2f}",
                f"Q {float(detalle['monto']):.2f}"
            ])
        
        detalles_table = Table(detalles_data, colWidths=[2*inch, 2*inch, 2*inch])
        detalles_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(detalles_table)
        
        doc.build(elements)
        return filepath
        
    except Exception as e:
        print(f"Error generando reporte: {str(e)}")
        return None

def generar_analisis_ventas(tipo, fecha_inicio, fecha_fin):
    try:
        if tipo == 'categorias':
            return generar_analisis_categorias(fecha_inicio, fecha_fin)
        elif tipo == 'recursos':
            return generar_analisis_recursos(fecha_inicio, fecha_fin)
        else:
            return None
    except Exception as e:
        print(f"Error en análisis de ventas: {str(e)}")
        return None

def generar_analisis_categorias(fecha_inicio, fecha_fin):
    filename = f"analisis_categorias_{fecha_inicio}_{fecha_fin}.pdf"
    filepath = os.path.join('database', 'data', filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    elements.append(Paragraph("Tecnologías Chapinas, S.A.", styles['Title']))
    elements.append(Paragraph("Análisis de Ventas por Categorías", styles['Heading1']))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph(f"Período: {fecha_inicio} a {fecha_fin}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    datos_analisis = [
        ['Categoría', 'Ingresos Totales', 'Configuración Más Popular']
    ]
    
    facturas = cargar_datos('facturas')
    total_ingresos = sum(float(factura['montoTotal']) for factura in facturas)
    
    datos_analisis.append(['Total General', f"Q {total_ingresos:.2f}", '-'])
    
    analisis_table = Table(datos_analisis, colWidths=[2.5*inch, 2*inch, 2.5*inch])
    analisis_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(analisis_table)
    
    doc.build(elements)
    return filepath

def generar_analisis_recursos(fecha_inicio, fecha_fin):
    filename = f"analisis_recursos_{fecha_inicio}_{fecha_fin}.pdf"
    filepath = os.path.join('database', 'data', filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    elements.append(Paragraph("Tecnologías Chapinas, S.A.", styles['Title']))
    elements.append(Paragraph("Análisis de Ventas por Recursos", styles['Heading1']))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph(f"Período: {fecha_inicio} a {fecha_fin}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    datos_analisis = [
        ['Recurso', 'Tipo', 'Ingresos Generados']
    ]
    
    recursos = cargar_datos('configuraciones')
    recursos_data = [r for r in recursos if r['tipo'] == 'recurso']
    
    for recurso in recursos_data[:5]:
        datos_analisis.append([
            recurso['nombre'],
            recurso['tipo_recurso'],
            f"Q {float(recurso['valor_x_hora']) * 100:.2f}"
        ])
    
    analisis_table = Table(datos_analisis, colWidths=[2.5*inch, 1.5*inch, 2*inch])
    analisis_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(analisis_table)
    
    doc.build(elements)
    return filepath
