from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
from database.xml_storage import cargar_datos, cargar_recursos, cargar_categorias, cargar_clientes, cargar_consumos, cargar_facturas
from datetime import datetime
import os

def generar_reporte_factura(numero_factura):
    """
    Genera un reporte PDF detallado de una factura específica.
    Incluye: datos generales, detalle por instancia, recursos consumidos y su aporte al cobro.
    """
    try:
        print(f"\n=== GENERANDO REPORTE DE FACTURA: {numero_factura} ===")
        
        # Cargar todos los datos necesarios
        facturas = cargar_facturas()
        clientes = cargar_clientes()
        consumos = cargar_consumos()
        categorias = cargar_categorias()
        recursos = cargar_recursos()
        
        # Buscar la factura específica
        factura_data = None
        for factura in facturas:
            if factura['numero'] == numero_factura:
                factura_data = factura
                break
        
        if not factura_data:
            print(f"❌ Factura {numero_factura} no encontrada")
            return None
        
        print(f"✅ Factura encontrada - Cliente: {factura_data['nitCliente']}")
        
        # Buscar datos del cliente
        cliente_data = None
        for cliente in clientes:
            if cliente['nit'] == factura_data['nitCliente']:
                cliente_data = cliente
                break
        
        # Crear archivo PDF
        filename = f"factura_{numero_factura}.pdf"
        filepath = os.path.join('database', 'data', filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter,
                              rightMargin=40, leftMargin=40,
                              topMargin=40, bottomMargin=40)
        elements = []
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2980b9'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # ========== ENCABEZADO ==========
        elements.append(Paragraph("Tecnologías Chapinas, S.A.", title_style))
        elements.append(Paragraph("Factura Detallada de Servicios en la Nube", styles['Heading2']))
        elements.append(Spacer(1, 0.3*inch))
        
        # ========== INFORMACIÓN GENERAL DE LA FACTURA ==========
        elements.append(Paragraph("INFORMACIÓN GENERAL", heading_style))
        
        info_data = [
            ['Número de Factura:', factura_data['numero']],
            ['Fecha de Emisión:', factura_data['fechaFactura']],
            ['NIT Cliente:', factura_data['nitCliente']],
            ['Nombre Cliente:', cliente_data['nombre'] if cliente_data else 'N/A'],
            ['Correo Electrónico:', cliente_data.get('correo', 'N/A') if cliente_data else 'N/A'],
        ]
        
        info_table = Table(info_data, colWidths=[2.2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.4*inch))
        
        # ========== DETALLE POR INSTANCIA ==========
        elements.append(Paragraph("DETALLE DE INSTANCIAS FACTURADAS", heading_style))
        
        total_general = 0
        
        for detalle in factura_data['detalles']:
            id_instancia = detalle['idInstancia']
            tiempo_total = float(detalle['tiempoTotal'])
            monto_instancia = float(detalle['monto'])
            total_general += monto_instancia
            
            # Buscar información de la instancia
            instancia_info = None
            config_id = None
            
            for cliente in clientes:
                for instancia in cliente.get('instancias', []):
                    if str(instancia['id']) == str(id_instancia):
                        instancia_info = instancia
                        config_id = instancia['idConfiguracion']
                        break
                if instancia_info:
                    break
            
            # Encabezado de instancia
            instancia_header = f"Instancia: {instancia_info['nombre'] if instancia_info else id_instancia} (ID: {id_instancia})"
            elements.append(Paragraph(instancia_header, styles['Heading3']))
            
            # Información básica de la instancia
            inst_info = [
                ['Configuración ID:', config_id if config_id else 'N/A'],
                ['Tiempo Total Consumido:', f"{tiempo_total:.2f} horas"],
                ['Monto Total Instancia:', f"Q {monto_instancia:.2f}"]
            ]
            
            inst_table = Table(inst_info, colWidths=[2*inch, 4*inch])
            inst_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f5e9')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#c8e6c9'))
            ]))
            elements.append(inst_table)
            elements.append(Spacer(1, 0.2*inch))
            
            # ========== DETALLE DE RECURSOS Y SU APORTE ==========
            if config_id:
                # Buscar la configuración
                config_recursos = None
                for categoria in categorias:
                    for config in categoria.get('configuraciones', []):
                        if str(config['id']) == str(config_id):
                            config_recursos = config.get('recursos', {})
                            break
                    if config_recursos:
                        break
                
                if config_recursos and len(config_recursos) > 0:
                    elements.append(Paragraph("Detalle de Recursos Consumidos:", styles['Heading4']))
                    
                    recursos_data = [['Recurso', 'Cantidad', 'Costo/Hora', 'Horas', 'Subtotal']]
                    
                    for recurso_id, cantidad in config_recursos.items():
                        # Buscar info del recurso
                        recurso_info = None
                        for recurso in recursos:
                            if str(recurso['id']) == str(recurso_id):
                                recurso_info = recurso
                                break
                        
                        if recurso_info:
                            nombre_recurso = f"{recurso_info['nombre']} ({recurso_info['abreviatura']})"
                            valor_hora = float(recurso_info['valor_x_hora'])
                            cant = float(cantidad)
                            subtotal = valor_hora * cant * tiempo_total
                            
                            recursos_data.append([
                                nombre_recurso,
                                f"{cant:.2f} {recurso_info['metrica']}",
                                f"Q {valor_hora:.2f}",
                                f"{tiempo_total:.2f}",
                                f"Q {subtotal:.2f}"
                            ])
                    
                    recursos_table = Table(recursos_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1.2*inch])
                    recursos_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#95a5a6')),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
                    ]))
                    elements.append(recursos_table)
                    elements.append(Spacer(1, 0.15*inch))
                    
                    # Gráfico de aporte porcentual (simulado con tabla)
                    elements.append(Paragraph("Aporte Porcentual al Costo de la Instancia:", styles['Heading4']))
                    
                    aporte_data = [['Recurso', 'Porcentaje del Total']]
                    for recurso_id, cantidad in config_recursos.items():
                        recurso_info = None
                        for recurso in recursos:
                            if str(recurso['id']) == str(recurso_id):
                                recurso_info = recurso
                                break
                        
                        if recurso_info:
                            valor_hora = float(recurso_info['valor_x_hora'])
                            cant = float(cantidad)
                            subtotal = valor_hora * cant * tiempo_total
                            porcentaje = (subtotal / monto_instancia * 100) if monto_instancia > 0 else 0
                            
                            aporte_data.append([
                                recurso_info['nombre'],
                                f"{porcentaje:.1f}%"
                            ])
                    
                    aporte_table = Table(aporte_data, colWidths=[3*inch, 2*inch])
                    aporte_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#27ae60')),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8f5e9')])
                    ]))
                    elements.append(aporte_table)
            
            elements.append(Spacer(1, 0.3*inch))
            
            # Línea separadora entre instancias
            line_data = [['', '']]
            line_table = Table(line_data, colWidths=[6.5*inch, 0.1*inch])
            line_table.setStyle(TableStyle([
                ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#bdc3c7'))
            ]))
            elements.append(line_table)
            elements.append(Spacer(1, 0.2*inch))
        
        # ========== RESUMEN FINAL ==========
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("RESUMEN DE FACTURA", heading_style))
        
        resumen_data = [
            ['Total de Instancias Facturadas:', str(len(factura_data['detalles']))],
            ['Monto Total sin IVA:', f"Q {total_general:.2f}"],
            ['IVA (12%):', f"Q {total_general * 0.12:.2f}"],
            ['TOTAL A PAGAR:', f"Q {total_general * 1.12:.2f}"]
        ]
        
        resumen_table = Table(resumen_data, colWidths=[3.5*inch, 2.5*inch])
        resumen_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -2), colors.HexColor('#ecf0f1')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
            ('TEXTCOLOR', (0, 0), (-1, -2), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -2), 11),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 2, colors.HexColor('#95a5a6'))
        ]))
        elements.append(resumen_table)
        
        # Pie de página
        elements.append(Spacer(1, 0.5*inch))
        footer_text = f"Documento generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} | Tecnologías Chapinas, S.A."
        elements.append(Paragraph(footer_text, styles['Normal']))
        
        # Construir PDF
        doc.build(elements)
        
        print(f"✅ Reporte generado exitosamente: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"❌ Error generando reporte de factura: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None


def generar_analisis_ventas(tipo, fecha_inicio, fecha_fin):
    """
    Genera análisis de ventas por categorías/configuraciones o por recursos.
    """
    try:
        print(f"\n=== GENERANDO ANÁLISIS DE VENTAS: {tipo} ===")
        print(f"Período: {fecha_inicio} a {fecha_fin}")
        
        if tipo == 'categorias':
            return generar_analisis_categorias(fecha_inicio, fecha_fin)
        elif tipo == 'recursos':
            return generar_analisis_recursos(fecha_inicio, fecha_fin)
        else:
            print(f"❌ Tipo de análisis no válido: {tipo}")
            return None
            
    except Exception as e:
        print(f"❌ Error en análisis de ventas: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None


def generar_analisis_categorias(fecha_inicio, fecha_fin):
    """
    Analiza categorías y configuraciones que más ingresos generan.
    """
    try:
        # Cargar datos
        facturas = cargar_facturas()
        categorias = cargar_categorias()
        clientes = cargar_clientes()
        
        # Crear archivo PDF
        filename = f"analisis_categorias_{fecha_inicio.replace('/', '-')}_{fecha_fin.replace('/', '-')}.pdf"
        filepath = os.path.join('database', 'data', filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter,
                              rightMargin=40, leftMargin=40,
                              topMargin=40, bottomMargin=40)
        elements = []
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2980b9'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        # Encabezado
        elements.append(Paragraph("Tecnologías Chapinas, S.A.", title_style))
        elements.append(Paragraph("Análisis de Ventas por Categorías y Configuraciones", styles['Heading2']))
        elements.append(Spacer(1, 0.2*inch))
        
        periodo_text = f"Período de Análisis: {fecha_inicio} a {fecha_fin}"
        elements.append(Paragraph(periodo_text, styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Calcular ingresos por categoría y configuración
        ingresos_por_categoria = {}
        ingresos_por_configuracion = {}
        total_ingresos_periodo = 0
        
        for factura in facturas:
            monto_factura = float(factura.get('montoTotal', 0))
            total_ingresos_periodo += monto_factura
            
            # Analizar cada detalle de la factura
            for detalle in factura.get('detalles', []):
                id_instancia = detalle['idInstancia']
                monto = float(detalle['monto'])
                
                # Buscar la configuración de la instancia
                config_id = None
                for cliente in clientes:
                    for instancia in cliente.get('instancias', []):
                        if str(instancia['id']) == str(id_instancia):
                            config_id = instancia['idConfiguracion']
                            break
                    if config_id:
                        break
                
                if config_id:
                    # Buscar la categoría de la configuración
                    for categoria in categorias:
                        for config in categoria.get('configuraciones', []):
                            if str(config['id']) == str(config_id):
                                # Acumular por categoría
                                cat_nombre = categoria['nombre']
                                if cat_nombre not in ingresos_por_categoria:
                                    ingresos_por_categoria[cat_nombre] = {
                                        'monto': 0,
                                        'instancias': 0,
                                        'configuraciones': set()
                                    }
                                ingresos_por_categoria[cat_nombre]['monto'] += monto
                                ingresos_por_categoria[cat_nombre]['instancias'] += 1
                                ingresos_por_categoria[cat_nombre]['configuraciones'].add(config['nombre'])
                                
                                # Acumular por configuración
                                config_nombre = f"{cat_nombre} - {config['nombre']}"
                                if config_nombre not in ingresos_por_configuracion:
                                    ingresos_por_configuracion[config_nombre] = {
                                        'monto': 0,
                                        'instancias': 0
                                    }
                                ingresos_por_configuracion[config_nombre]['monto'] += monto
                                ingresos_por_configuracion[config_nombre]['instancias'] += 1
                                break
        
        # ========== RESUMEN GENERAL ==========
        elements.append(Paragraph("RESUMEN GENERAL", heading_style))
        
        resumen_data = [
            ['Total Ingresos en el Período:', f"Q {total_ingresos_periodo:.2f}"],
            ['Total Facturas Emitidas:', str(len(facturas))],
            ['Categorías Activas:', str(len(ingresos_por_categoria))],
            ['Configuraciones Utilizadas:', str(len(ingresos_por_configuracion))]
        ]
        
        resumen_table = Table(resumen_data, colWidths=[3*inch, 2.5*inch])
        resumen_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
        ]))
        elements.append(resumen_table)
        elements.append(Spacer(1, 0.4*inch))
        
        # ========== INGRESOS POR CATEGORÍA ==========
        elements.append(Paragraph("INGRESOS POR CATEGORÍA", heading_style))
        
        cat_data = [['Categoría', 'Ingresos', '% del Total', 'Instancias', 'Configs Usadas']]
        
        # Ordenar por ingresos descendente
        categorias_ordenadas = sorted(ingresos_por_categoria.items(), 
                                      key=lambda x: x[1]['monto'], 
                                      reverse=True)
        
        for cat_nombre, datos in categorias_ordenadas:
            porcentaje = (datos['monto'] / total_ingresos_periodo * 100) if total_ingresos_periodo > 0 else 0
            cat_data.append([
                cat_nombre,
                f"Q {datos['monto']:.2f}",
                f"{porcentaje:.1f}%",
                str(datos['instancias']),
                str(len(datos['configuraciones']))
            ])
        
        cat_table = Table(cat_data, colWidths=[2*inch, 1.3*inch, 1*inch, 1*inch, 1*inch])
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#95a5a6')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')])
        ]))
        elements.append(cat_table)
        elements.append(Spacer(1, 0.4*inch))
        
        # ========== TOP 10 CONFIGURACIONES ==========
        elements.append(Paragraph("TOP 10 CONFIGURACIONES MÁS RENTABLES", heading_style))
        
        config_data = [['Configuración', 'Ingresos', '% del Total', 'Instancias']]
        
        # Ordenar configuraciones por ingresos
        configs_ordenadas = sorted(ingresos_por_configuracion.items(), 
                                   key=lambda x: x[1]['monto'], 
                                   reverse=True)[:10]
        
        for config_nombre, datos in configs_ordenadas:
            porcentaje = (datos['monto'] / total_ingresos_periodo * 100) if total_ingresos_periodo > 0 else 0
            config_data.append([
                config_nombre,
                f"Q {datos['monto']:.2f}",
                f"{porcentaje:.1f}%",
                str(datos['instancias'])
            ])
        
        config_table = Table(config_data, colWidths=[3*inch, 1.5*inch, 1*inch, 1*inch])
        config_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#27ae60')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8f5e9')])
        ]))
        elements.append(config_table)
        
        # Pie de página
        elements.append(Spacer(1, 0.5*inch))
        footer_text = f"Documento generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} | Tecnologías Chapinas, S.A."
        elements.append(Paragraph(footer_text, styles['Normal']))
        
        # Construir PDF
        doc.build(elements)
        
        print(f"✅ Análisis de categorías generado: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"❌ Error generando análisis de categorías: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None


def generar_analisis_recursos(fecha_inicio, fecha_fin):
    """
    Analiza recursos que más ingresos generan.
    """
    try:
        # Cargar datos
        facturas = cargar_facturas()
        recursos = cargar_recursos()
        categorias = cargar_categorias()
        clientes = cargar_clientes()
        consumos = cargar_consumos()
        
        # Crear archivo PDF
        filename = f"analisis_recursos_{fecha_inicio.replace('/', '-')}_{fecha_fin.replace('/', '-')}.pdf"
        filepath = os.path.join('database', 'data', filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter,
                              rightMargin=40, leftMargin=40,
                              topMargin=40, bottomMargin=40)
        elements = []
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2980b9'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        # Encabezado
        elements.append(Paragraph("Tecnologías Chapinas, S.A.", title_style))
        elements.append(Paragraph("Análisis de Ventas por Recursos", styles['Heading2']))
        elements.append(Spacer(1, 0.2*inch))
        
        periodo_text = f"Período de Análisis: {fecha_inicio} a {fecha_fin}"
        elements.append(Paragraph(periodo_text, styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Calcular ingresos por recurso
        ingresos_por_recurso = {}
        total_ingresos_periodo = 0
        total_horas_consumidas = 0
        
        for factura in facturas:
            monto_factura = float(factura.get('montoTotal', 0))
            total_ingresos_periodo += monto_factura
            
            # Analizar cada detalle de la factura
            for detalle in factura.get('detalles', []):
                id_instancia = detalle['idInstancia']
                tiempo_total = float(detalle['tiempoTotal'])
                monto = float(detalle['monto'])
                total_horas_consumidas += tiempo_total
                
                # Buscar la configuración de la instancia
                config_id = None
                for cliente in clientes:
                    for instancia in cliente.get('instancias', []):
                        if str(instancia['id']) == str(id_instancia):
                            config_id = instancia['idConfiguracion']
                            break
                    if config_id:
                        break
                
                if config_id:
                    # Buscar recursos de la configuración
                    config_recursos = None
                    for categoria in categorias:
                        for config in categoria.get('configuraciones', []):
                            if str(config['id']) == str(config_id):
                                config_recursos = config.get('recursos', {})
                                break
                        if config_recursos:
                            break
                    
                    if config_recursos:
                        # Calcular aporte de cada recurso
                        for recurso_id, cantidad in config_recursos.items():
                            # Buscar info del recurso
                            recurso_info = None
                            for recurso in recursos:
                                if str(recurso['id']) == str(recurso_id):
                                    recurso_info = recurso
                                    break
                            
                            if recurso_info:
                                valor_hora = float(recurso_info['valor_x_hora'])
                                cant = float(cantidad)
                                ingreso_recurso = valor_hora * cant * tiempo_total
                                
                                recurso_nombre = recurso_info['nombre']
                                if recurso_nombre not in ingresos_por_recurso:
                                    ingresos_por_recurso[recurso_nombre] = {
                                        'monto': 0,
                                        'tipo': recurso_info['tipo_recurso'],
                                        'abreviatura': recurso_info['abreviatura'],
                                        'metrica': recurso_info['metrica'],
                                        'valor_hora': valor_hora,
                                        'horas_totales': 0,
                                        'cantidad_total': 0,
                                        'instancias': 0
                                    }
                                
                                ingresos_por_recurso[recurso_nombre]['monto'] += ingreso_recurso
                                ingresos_por_recurso[recurso_nombre]['horas_totales'] += tiempo_total
                                ingresos_por_recurso[recurso_nombre]['cantidad_total'] += cant
                                ingresos_por_recurso[recurso_nombre]['instancias'] += 1
        
        # ========== RESUMEN GENERAL ==========
        elements.append(Paragraph("RESUMEN GENERAL", heading_style))
        
        resumen_data = [
            ['Total Ingresos en el Período:', f"Q {total_ingresos_periodo:.2f}"],
            ['Total Facturas Emitidas:', str(len(facturas))],
            ['Total Horas Consumidas:', f"{total_horas_consumidas:.2f} horas"],
            ['Recursos Diferentes Utilizados:', str(len(ingresos_por_recurso))],
            ['Ingreso Promedio por Hora:', f"Q {total_ingresos_periodo/total_horas_consumidas:.2f}" if total_horas_consumidas > 0 else "Q 0.00"]
        ]
        
        resumen_table = Table(resumen_data, colWidths=[3*inch, 2.5*inch])
        resumen_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
        ]))
        elements.append(resumen_table)
        elements.append(Spacer(1, 0.4*inch))
        
        # ========== INGRESOS POR RECURSO (TODOS) ==========
        elements.append(Paragraph("ANÁLISIS DETALLADO POR RECURSO", heading_style))
        
        recursos_data = [['Recurso', 'Tipo', 'Ingresos', '% Total', 'Horas', 'Instancias']]
        
        # Ordenar por ingresos descendente
        recursos_ordenados = sorted(ingresos_por_recurso.items(), 
                                    key=lambda x: x[1]['monto'], 
                                    reverse=True)
        
        for recurso_nombre, datos in recursos_ordenados:
            porcentaje = (datos['monto'] / total_ingresos_periodo * 100) if total_ingresos_periodo > 0 else 0
            recursos_data.append([
                f"{recurso_nombre}\n({datos['abreviatura']})",
                datos['tipo'],
                f"Q {datos['monto']:.2f}",
                f"{porcentaje:.1f}%",
                f"{datos['horas_totales']:.2f}",
                str(datos['instancias'])
            ])
        
        recursos_table = Table(recursos_data, colWidths=[1.8*inch, 1*inch, 1.2*inch, 0.8*inch, 1*inch, 1*inch])
        recursos_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#8e44ad')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f4ecf7')])
        ]))
        elements.append(recursos_table)
        elements.append(Spacer(1, 0.4*inch))
        
        # ========== ANÁLISIS POR TIPO DE RECURSO ==========
        elements.append(Paragraph("ANÁLISIS POR TIPO DE RECURSO", heading_style))
        
        ingresos_por_tipo = {}
        for recurso_nombre, datos in ingresos_por_recurso.items():
            tipo = datos['tipo']
            if tipo not in ingresos_por_tipo:
                ingresos_por_tipo[tipo] = {
                    'monto': 0,
                    'recursos': 0,
                    'instancias': set()
                }
            ingresos_por_tipo[tipo]['monto'] += datos['monto']
            ingresos_por_tipo[tipo]['recursos'] += 1
            ingresos_por_tipo[tipo]['instancias'].add(datos['instancias'])
        
        tipo_data = [['Tipo', 'Ingresos', '% del Total', 'Recursos', 'Ingresos Promedio/Recurso']]
        
        for tipo, datos in sorted(ingresos_por_tipo.items(), key=lambda x: x[1]['monto'], reverse=True):
            porcentaje = (datos['monto'] / total_ingresos_periodo * 100) if total_ingresos_periodo > 0 else 0
            promedio = datos['monto'] / datos['recursos'] if datos['recursos'] > 0 else 0
            tipo_data.append([
                tipo,
                f"Q {datos['monto']:.2f}",
                f"{porcentaje:.1f}%",
                str(datos['recursos']),
                f"Q {promedio:.2f}"
            ])
        
        tipo_table = Table(tipo_data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 1*inch, 1.5*inch])
        tipo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#c0392b')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fadbd8')])
        ]))
        elements.append(tipo_table)
        elements.append(Spacer(1, 0.4*inch))
        
        # ========== TOP 5 RECURSOS MÁS RENTABLES ==========
        elements.append(Paragraph("TOP 5 RECURSOS MÁS RENTABLES", heading_style))
        
        top_data = [['#', 'Recurso', 'Tipo', 'Ingresos', 'Valor/Hora', 'Rentabilidad']]
        
        top_recursos = recursos_ordenados[:5]
        for idx, (recurso_nombre, datos) in enumerate(top_recursos, 1):
            rentabilidad = datos['monto'] / datos['horas_totales'] if datos['horas_totales'] > 0 else 0
            top_data.append([
                str(idx),
                recurso_nombre,
                datos['tipo'],
                f"Q {datos['monto']:.2f}",
                f"Q {datos['valor_hora']:.2f}",
                f"Q {rentabilidad:.2f}/h"
            ])
        
        top_table = Table(top_data, colWidths=[0.4*inch, 2*inch, 1*inch, 1.2*inch, 1*inch, 1*inch])
        top_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d68910')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fef5e7')])
        ]))
        elements.append(top_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # ========== CONCLUSIONES Y RECOMENDACIONES ==========
        elements.append(Paragraph("CONCLUSIONES Y RECOMENDACIONES", heading_style))
        
        conclusiones_text = f"""
        <b>Recursos más rentables:</b> Los {min(3, len(recursos_ordenados))} recursos que más ingresos generan 
        representan el {sum(d['monto'] for _, d in recursos_ordenados[:3]) / total_ingresos_periodo * 100:.1f}% 
        del total de ingresos.<br/><br/>
        
        <b>Tipo predominante:</b> Los recursos de tipo {max(ingresos_por_tipo.items(), key=lambda x: x[1]['monto'])[0] if ingresos_por_tipo else 'N/A'} 
        generan la mayor parte de los ingresos.<br/><br/>
        
        <b>Recomendación:</b> Se recomienda optimizar la oferta de los recursos más rentables y evaluar 
        la viabilidad de recursos con baja demanda.
        """
        
        elements.append(Paragraph(conclusiones_text, styles['Normal']))
        
        # Pie de página
        elements.append(Spacer(1, 0.5*inch))
        footer_text = f"Documento generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} | Tecnologías Chapinas, S.A."
        elements.append(Paragraph(footer_text, styles['Normal']))
        
        # Construir PDF
        doc.build(elements)
        
        print(f"✅ Análisis de recursos generado: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"❌ Error generando análisis de recursos: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None