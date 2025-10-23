import os
import xml.etree.ElementTree as ET
from datetime import datetime
from .models import Recurso, Configuracion, Categoria, Cliente, Instancia, Consumo, Factura

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def reset_database():
    ensure_data_dir()
    archivos = ['configuraciones.xml', 'consumos.xml', 'facturas.xml']
    for archivo in archivos:
        file_path = os.path.join(DATA_DIR, archivo)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            if archivo == 'configuraciones.xml':
                f.write('<configuraciones>\n</configuraciones>')
            elif archivo == 'consumos.xml':
                f.write('<consumos>\n</consumos>')
            elif archivo == 'facturas.xml':
                f.write('<facturas>\n</facturas>')

def guardar_recurso(recurso):
    ensure_data_dir()
    file_path = os.path.join(DATA_DIR, 'configuraciones.xml')
    
    try:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for elem in root.findall('recurso'):
                if elem.get('id') == str(recurso.id_recurso):
                    root.remove(elem)
        else:
            root = ET.Element('configuraciones')
            tree = ET.ElementTree(root)
    except:
        root = ET.Element('configuraciones')
        tree = ET.ElementTree(root)
    
    recurso_elem = ET.SubElement(root, 'recurso')
    recurso_elem.set('id', str(recurso.id_recurso))
    
    ET.SubElement(recurso_elem, 'nombre').text = recurso.nombre
    ET.SubElement(recurso_elem, 'abreviatura').text = recurso.abreviatura
    ET.SubElement(recurso_elem, 'metrica').text = recurso.metrica
    ET.SubElement(recurso_elem, 'tipo').text = recurso.tipo
    ET.SubElement(recurso_elem, 'valorXhora').text = str(recurso.valor_x_hora)
    
    indent(root)
    tree.write(file_path, encoding='utf-8', xml_declaration=True)

def guardar_categoria(categoria):
    ensure_data_dir()
    file_path = os.path.join(DATA_DIR, 'configuraciones.xml')
    
    try:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for elem in root.findall('categoria'):
                if elem.get('id') == str(categoria.id_categoria):
                    root.remove(elem)
        else:
            root = ET.Element('configuraciones')
            tree = ET.ElementTree(root)
    except:
        root = ET.Element('configuraciones')
        tree = ET.ElementTree(root)
    
    categoria_elem = ET.SubElement(root, 'categoria')
    categoria_elem.set('id', str(categoria.id_categoria))
    
    ET.SubElement(categoria_elem, 'nombre').text = categoria.nombre
    ET.SubElement(categoria_elem, 'descripcion').text = categoria.descripcion
    ET.SubElement(categoria_elem, 'cargaTrabajo').text = categoria.carga_trabajo
    
    configs_elem = ET.SubElement(categoria_elem, 'configuraciones')
    for config in categoria.configuraciones:
        config_elem = ET.SubElement(configs_elem, 'configuracion')
        config_elem.set('id', str(config.id_configuracion))
        ET.SubElement(config_elem, 'nombre').text = config.nombre
        ET.SubElement(config_elem, 'descripcion').text = config.descripcion
        
        recursos_elem = ET.SubElement(config_elem, 'recursos')
        for recurso_id, cantidad in config.recursos.items():
            recurso_elem = ET.SubElement(recursos_elem, 'recurso')
            recurso_elem.set('id', str(recurso_id))
            recurso_elem.text = str(cantidad)
    
    indent(root)
    tree.write(file_path, encoding='utf-8', xml_declaration=True)

def guardar_cliente(cliente):
    ensure_data_dir()
    file_path = os.path.join(DATA_DIR, 'configuraciones.xml')
    
    try:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for elem in root.findall('cliente'):
                if elem.get('nit') == cliente.nit:
                    root.remove(elem)
        else:
            root = ET.Element('configuraciones')
            tree = ET.ElementTree(root)
    except:
        root = ET.Element('configuraciones')
        tree = ET.ElementTree(root)
    
    cliente_elem = ET.SubElement(root, 'cliente')
    cliente_elem.set('nit', cliente.nit)
    
    ET.SubElement(cliente_elem, 'nombre').text = cliente.nombre
    ET.SubElement(cliente_elem, 'usuario').text = cliente.usuario
    ET.SubElement(cliente_elem, 'clave').text = cliente.clave
    ET.SubElement(cliente_elem, 'direccion').text = cliente.direccion
    ET.SubElement(cliente_elem, 'correoElectronico').text = cliente.correo
    
    instancias_elem = ET.SubElement(cliente_elem, 'instancias')
    for instancia in cliente.instancias:
        instancia_elem = ET.SubElement(instancias_elem, 'instancia')
        instancia_elem.set('id', str(instancia.id_instancia))
        
        ET.SubElement(instancia_elem, 'idConfiguracion').text = str(instancia.id_configuracion)
        ET.SubElement(instancia_elem, 'nombre').text = instancia.nombre
        ET.SubElement(instancia_elem, 'fechaInicio').text = instancia.fecha_inicio
        ET.SubElement(instancia_elem, 'estado').text = instancia.estado
        if instancia.fecha_final:
            ET.SubElement(instancia_elem, 'fechaFinal').text = instancia.fecha_final
    
    indent(root)
    tree.write(file_path, encoding='utf-8', xml_declaration=True)

def guardar_consumo(consumo):
    ensure_data_dir()
    file_path = os.path.join(DATA_DIR, 'consumos.xml')
    
    try:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            tree = ET.parse(file_path)
            root = tree.getroot()
        else:
            root = ET.Element('consumos')
            tree = ET.ElementTree(root)
    except:
        root = ET.Element('consumos')
        tree = ET.ElementTree(root)
    
    consumo_elem = ET.SubElement(root, 'consumo')
    consumo_elem.set('nitCliente', consumo.nit_cliente)
    consumo_elem.set('idInstancia', str(consumo.id_instancia))
    
    ET.SubElement(consumo_elem, 'tiempo').text = str(consumo.tiempo)
    ET.SubElement(consumo_elem, 'fechahora').text = consumo.fecha_hora
    
    indent(root)
    tree.write(file_path, encoding='utf-8', xml_declaration=True)

def guardar_factura(factura):
    ensure_data_dir()
    file_path = os.path.join(DATA_DIR, 'facturas.xml')
    
    try:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            tree = ET.parse(file_path)
            root = tree.getroot()
        else:
            root = ET.Element('facturas')
            tree = ET.ElementTree(root)
    except:
        root = ET.Element('facturas')
        tree = ET.ElementTree(root)
    
    factura_elem = ET.SubElement(root, 'factura')
    factura_elem.set('numero', str(factura.numero_factura))
    
    ET.SubElement(factura_elem, 'nitCliente').text = factura.nit_cliente
    ET.SubElement(factura_elem, 'fechaFactura').text = factura.fecha_factura
    ET.SubElement(factura_elem, 'montoTotal').text = str(factura.monto_total)
    
    detalles_elem = ET.SubElement(factura_elem, 'detalles')
    for detalle in factura.detalles:
        detalle_elem = ET.SubElement(detalles_elem, 'detalle')
        ET.SubElement(detalle_elem, 'idInstancia').text = str(detalle['id_instancia'])
        ET.SubElement(detalle_elem, 'tiempoTotal').text = str(detalle['tiempo_total'])
        ET.SubElement(detalle_elem, 'monto').text = str(detalle['monto'])
    
    indent(root)
    tree.write(file_path, encoding='utf-8', xml_declaration=True)

def cargar_datos(tipo, subtipo=None):
    ensure_data_dir()
    
    # Determinar qué archivo usar
    if tipo in ['recursos', 'categorias', 'clientes'] or subtipo:
        file_path = os.path.join(DATA_DIR, 'configuraciones.xml')
    else:
        file_path = os.path.join(DATA_DIR, f'{tipo}.xml')
    
    print(f"🔍 CARGAR_DATOS - Tipo: {tipo}, Subtipo: {subtipo}, Archivo: {file_path}")
    
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        print(f"🔍 CARGAR_DATOS - Archivo no existe o está vacío")
        return []
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        print(f"🔍 CARGAR_DATOS - Root tag: {root.tag}")
    except Exception as e:
        print(f"🔍 CARGAR_DATOS - Error parseando: {e}")
        return []
    
    datos = []
    
    # Si se especificó subtipo, usar ese
    tipo_consulta = subtipo if subtipo else tipo
    
    if tipo_consulta == 'recursos':
        for elem in root.findall('recurso'):
            datos.append({
                'tipo': 'recurso',
                'id': elem.get('id'),
                'nombre': elem.find('nombre').text if elem.find('nombre') is not None else '',
                'abreviatura': elem.find('abreviatura').text if elem.find('abreviatura') is not None else '',
                'metrica': elem.find('metrica').text if elem.find('metrica') is not None else '',
                'tipo_recurso': elem.find('tipo').text if elem.find('tipo') is not None else '',
                'valor_x_hora': elem.find('valorXhora').text if elem.find('valorXhora') is not None else '0'
            })
    
    elif tipo_consulta == 'categorias':
        for elem in root.findall('categoria'):
            configuraciones = []
            configs_elem = elem.find('configuraciones')
            if configs_elem is not None:
                for config in configs_elem.findall('configuracion'):
                    recursos_config = {}
                    recursos_elem = config.find('recursos')
                    if recursos_elem is not None:
                        for recurso in recursos_elem.findall('recurso'):
                            recursos_config[recurso.get('id')] = recurso.text
                    
                    configuraciones.append({
                        'id': config.get('id'),
                        'nombre': config.find('nombre').text if config.find('nombre') is not None else '',
                        'descripcion': config.find('descripcion').text if config.find('descripcion') is not None else '',
                        'recursos': recursos_config
                    })
            
            datos.append({
                'tipo': 'categoria',
                'id': elem.get('id'),
                'nombre': elem.find('nombre').text if elem.find('nombre') is not None else '',
                'descripcion': elem.find('descripcion').text if elem.find('descripcion') is not None else '',
                'carga_trabajo': elem.find('cargaTrabajo').text if elem.find('cargaTrabajo') is not None else '',
                'configuraciones': configuraciones
            })
    
    elif tipo_consulta == 'clientes':
        for elem in root.findall('cliente'):
            instancias = []
            instancias_elem = elem.find('instancias')
            if instancias_elem is not None:
                for instancia in instancias_elem.findall('instancia'):
                    instancias.append({
                        'id': instancia.get('id'),
                        'idConfiguracion': instancia.find('idConfiguracion').text if instancia.find('idConfiguracion') is not None else '',
                        'nombre': instancia.find('nombre').text if instancia.find('nombre') is not None else '',
                        'fechaInicio': instancia.find('fechaInicio').text if instancia.find('fechaInicio') is not None else '',
                        'estado': instancia.find('estado').text if instancia.find('estado') is not None else '',
                        'fechaFinal': instancia.find('fechaFinal').text if instancia.find('fechaFinal') is not None else None
                    })
            
            datos.append({
                'tipo': 'cliente',
                'nit': elem.get('nit'),
                'nombre': elem.find('nombre').text if elem.find('nombre') is not None else '',
                'usuario': elem.find('usuario').text if elem.find('usuario') is not None else '',
                'correo': elem.find('correoElectronico').text if elem.find('correoElectronico') is not None else '',
                'instancias': instancias
            })
    
    elif tipo == 'consumos':
        for elem in root.findall('consumo'):
            datos.append({
                'nitCliente': elem.get('nitCliente'),
                'idInstancia': elem.get('idInstancia'),
                'tiempo': elem.find('tiempo').text if elem.find('tiempo') is not None else '0',
                'fechahora': elem.find('fechahora').text if elem.find('fechahora') is not None else ''
            })
    
    elif tipo == 'facturas':
        for elem in root.findall('factura'):
            detalles = []
            detalles_elem = elem.find('detalles')
            if detalles_elem is not None:
                for detalle in detalles_elem.findall('detalle'):
                    detalles.append({
                        'idInstancia': detalle.find('idInstancia').text if detalle.find('idInstancia') is not None else '',
                        'tiempoTotal': detalle.find('tiempoTotal').text if detalle.find('tiempoTotal') is not None else '0',
                        'monto': detalle.find('monto').text if detalle.find('monto') is not None else '0'
                    })
            
            datos.append({
                'numero': elem.get('numero'),
                'nitCliente': elem.find('nitCliente').text if elem.find('nitCliente') is not None else '',
                'fechaFactura': elem.find('fechaFactura').text if elem.find('fechaFactura') is not None else '',
                'montoTotal': elem.find('montoTotal').text if elem.find('montoTotal') is not None else '0',
                'detalles': detalles
            })
    
    print(f"🔍 CARGAR_DATOS - {len(datos)} elementos encontrados para {tipo_consulta}")
    return datos


# FUNCIÓN PARA MEJORAR FORMATO XML
def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i