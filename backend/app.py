from flask import Flask, request, jsonify
from services.config_service import procesar_configuracion
from services.consumo_service import procesar_consumo
from services.facturacion_service import generar_facturas
from services.report_service import generar_reporte_factura, generar_analisis_ventas
from database.xml_storage import (
    reset_database, guardar_recurso, guardar_categoria, guardar_cliente, 
    guardar_consumo, guardar_factura, cargar_recursos, cargar_categorias, 
    cargar_clientes, cargar_consumos, cargar_facturas
)
from database.models import Recurso, Configuracion, Categoria, Cliente
from utils.validators import validar_nit

app = Flask(__name__)

@app.route('/reset', methods=['POST'])
def reset_sistema():
    try:
        reset_database()
        return jsonify({"mensaje": "Sistema reiniciado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/configuracion', methods=['POST'])
def recibir_configuracion():
    xml_data = request.data.decode('utf-8')
    resultado = procesar_configuracion(xml_data)
    return jsonify(resultado)

@app.route('/consumo', methods=['POST'])
def recibir_consumo():
    xml_data = request.data.decode('utf-8')
    resultado = procesar_consumo(xml_data)
    return jsonify(resultado)

@app.route('/facturacion', methods=['POST'])
def facturar():
    data = request.json
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    resultado = generar_facturas(fecha_inicio, fecha_fin)
    return jsonify(resultado)

@app.route('/reporte/factura', methods=['POST'])
def reporte_factura():
    data = request.json
    numero_factura = data.get('numero_factura')
    pdf_path = generar_reporte_factura(numero_factura)
    return jsonify({"pdf_path": pdf_path})

@app.route('/reporte/ventas', methods=['POST'])
def reporte_ventas():
    data = request.json
    tipo = data.get('tipo')
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    pdf_path = generar_analisis_ventas(tipo, fecha_inicio, fecha_fin)
    return jsonify({"pdf_path": pdf_path})

@app.route('/consultar/<tipo>', methods=['GET'])
def consultar_datos(tipo):
    """Consulta datos desde los archivos separados"""
    if tipo == 'recursos':
        datos = cargar_recursos()
    elif tipo == 'categorias':
        datos = cargar_categorias()
    elif tipo == 'clientes':
        datos = cargar_clientes()
    elif tipo == 'consumos':
        datos = cargar_consumos()
    elif tipo == 'facturas':
        datos = cargar_facturas()
    else:
        datos = []
    
    print(f"🔍 CONSULTA - Tipo: {tipo}, Elementos encontrados: {len(datos)}")
    return jsonify(datos)

# NUEVAS RUTAS PARA CREAR DATOS
@app.route('/crear/recurso', methods=['POST'])
def crear_recurso():
    try:
        print("🔧 BACKEND - Creando recurso...")
        data = request.json
        print(f"🔧 BACKEND - Datos recibidos: {data}")
        
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400
        
        # Generar ID único para el recurso
        nuevo_id = generar_id_recurso()
        
        nuevo_recurso = Recurso(
            id_recurso=nuevo_id,
            nombre=data.get('nombre'),
            abreviatura=data.get('abreviatura'),
            metrica=data.get('metrica'),
            tipo=data.get('tipo'),
            valor_x_hora=float(data.get('valor'))
        )
        
        print(f"🔧 BACKEND - Guardando recurso: {nuevo_recurso.nombre}")
        guardar_recurso(nuevo_recurso)
        
        return jsonify({
            "mensaje": "Recurso creado exitosamente",
            "id": nuevo_id
        })
        
    except Exception as e:
        print(f"🔧 BACKEND - Error: {str(e)}")
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@app.route('/crear/categoria', methods=['POST'])
def crear_categoria():
    try:
        print("🔧 BACKEND - Creando categoría...")
        data = request.json
        
        nueva_categoria = Categoria(
            id_categoria=generar_id_categoria(),
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion'),
            carga_trabajo=data.get('carga_trabajo'),
            configuraciones=[]
        )
        
        guardar_categoria(nueva_categoria)
        return jsonify({"mensaje": "Categoría creada exitosamente"})
        
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@app.route('/crear/cliente', methods=['POST'])
def crear_cliente():
    try:
        print("🔧 BACKEND - Creando cliente...")
        data = request.json
        
        # Validar NIT
        if not validar_nit(data.get('nit')):
            return jsonify({"error": "NIT inválido"}), 400
        
        nuevo_cliente = Cliente(
            nit=data.get('nit'),
            nombre=data.get('nombre'),
            usuario=data.get('usuario'),
            clave=data.get('clave'),
            direccion=data.get('direccion'),
            correo=data.get('correo'),
            instancias=[]
        )
        
        guardar_cliente(nuevo_cliente)
        return jsonify({"mensaje": "Cliente creado exitosamente"})
        
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@app.route('/crear/configuracion', methods=['POST'])
def crear_configuracion():
    try:
        data = request.json
        print(f"🔧 BACKEND - Creando configuración: {data}")
        
        # Cargar categorías existentes
        categorias = cargar_categorias()
        
        print(f"🔧 BACKEND - Categorías disponibles:")
        for cat in categorias:
            print(f"  - ID: '{cat['id']}' (tipo: {type(cat['id']).__name__}), Nombre: '{cat.get('nombre', 'N/A')}'")
        
        # Buscar la categoría donde agregar la configuración
        categoria_id = data.get('categoria_id')
        categoria_encontrada = None
        
        for categoria in categorias:
            # Comparar como strings para evitar problemas de tipo
            print(f"🔧 BACKEND - Comparando: '{categoria['id']}' con '{categoria_id}'")
            if str(categoria['id']) == str(categoria_id):
                categoria_encontrada = categoria
                print(f"🔧 BACKEND - ✅ Categoría encontrada: {categoria_encontrada['nombre']}")
                break
        
        if not categoria_encontrada:
            print(f"🔧 BACKEND - ❌ ERROR: No se encontró categoría con ID {categoria_id}")
            print(f"🔧 BACKEND - IDs disponibles: {[cat['id'] for cat in categorias]}")
            return jsonify({"error": f"Categoría con ID {categoria_id} no encontrada. IDs disponibles: {[cat['id'] for cat in categorias]}"}), 400
        
        # Generar ID único para la configuración
        nuevo_id = generar_id_configuracion(categoria_encontrada)
        
        # Crear recursos de la configuración
        recursos_config = {}
        for recurso in data.get('recursos', []):
            recursos_config[int(recurso['id'])] = float(recurso['cantidad'])
            print(f"🔧 BACKEND - Recurso agregado: ID {recurso['id']}, Cantidad: {recurso['cantidad']}")
        
        # Crear objeto Configuracion
        nueva_configuracion = Configuracion(
            id_configuracion=nuevo_id,
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion'),
            recursos=recursos_config
        )
        
        # Agregar a la categoría
        if 'configuraciones' not in categoria_encontrada:
            categoria_encontrada['configuraciones'] = []
        
        # Convertir a dict para guardar
        config_dict = {
            'id': str(nuevo_id),
            'nombre': nueva_configuracion.nombre,
            'descripcion': nueva_configuracion.descripcion,
            'recursos': recursos_config
        }
        
        categoria_encontrada['configuraciones'].append(config_dict)
        
        # Convertir de vuelta a objeto Categoria y guardar
        configuraciones_obj = []
        for config in categoria_encontrada.get('configuraciones', []):
            recursos_obj = {}
            for recurso_id, cantidad in config.get('recursos', {}).items():
                recursos_obj[int(recurso_id)] = float(cantidad)
            
            config_obj = Configuracion(
                id_configuracion=int(config['id']),
                nombre=config['nombre'],
                descripcion=config['descripcion'],
                recursos=recursos_obj
            )
            configuraciones_obj.append(config_obj)
        
        categoria_obj = Categoria(
            id_categoria=int(categoria_encontrada['id']),
            nombre=categoria_encontrada['nombre'],
            descripcion=categoria_encontrada['descripcion'],
            carga_trabajo=categoria_encontrada['carga_trabajo'],
            configuraciones=configuraciones_obj
        )
        
        guardar_categoria(categoria_obj)
        
        print(f"🔧 BACKEND - ✅ Configuración creada exitosamente: {config_dict}")
        
        return jsonify({
            "mensaje": "Configuración creada exitosamente",
            "id": nuevo_id,
            "configuracion": config_dict
        })
        
    except Exception as e:
        print(f"🔧 BACKEND - ❌ Error: {str(e)}")
        import traceback
        print(f"🔧 BACKEND - Traceback: {traceback.format_exc()}")
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

# FUNCIONES AUXILIARES PARA GENERAR IDs
def generar_id_recurso():
    try:
        # Usar la nueva función de carga de recursos
        recursos = cargar_recursos()
        print(f"🔍 GENERAR_ID_RECURSO - Recursos encontrados: {len(recursos)}")
        
        if recursos:
            ids = []
            for r in recursos:
                try:
                    ids.append(int(r['id']))
                    print(f"🔍 Recurso encontrado: ID {r['id']} - {r['nombre']}")
                except (ValueError, KeyError) as e:
                    print(f"⚠️  Error con ID del recurso: {r.get('id')} - {e}")
            
            if ids:
                max_id = max(ids)
                print(f"🔍 ID máximo encontrado: {max_id}")
                nuevo_id = max_id + 1
                print(f"🔍 Nuevo ID generado: {nuevo_id}")
                return nuevo_id
        
        print("🔍 No hay recursos, usando ID: 1")
        return 1
        
    except Exception as e:
        print(f"🔴 ERROR en generar_id_recurso: {e}")
        return 1

def generar_id_categoria():
    try:
        # Usar la nueva función de carga de categorías
        categorias = cargar_categorias()
        print(f"🔍 GENERAR_ID_CATEGORIA - Categorías encontradas: {len(categorias)}")
        
        if categorias:
            ids = []
            for c in categorias:
                try:
                    ids.append(int(c['id']))
                    print(f"🔍 Categoría encontrada: ID {c['id']} - {c['nombre']}")
                except (ValueError, KeyError) as e:
                    print(f"⚠️  Error con ID de categoría: {c.get('id')} - {e}")
            
            if ids:
                max_id = max(ids)
                print(f"🔍 ID máximo encontrado: {max_id}")
                nuevo_id = max_id + 1
                print(f"🔍 Nuevo ID generado: {nuevo_id}")
                return nuevo_id
        
        print("🔍 No hay categorías, usando ID: 1")
        return 1
        
    except Exception as e:
        print(f"🔴 ERROR en generar_id_categoria: {e}")
        return 1

def generar_id_configuracion(categoria):
    """Genera un ID único para una configuración dentro de una categoría"""
    if not categoria.get('configuraciones'):
        return 1
    
    ids = []
    for config in categoria['configuraciones']:
        try:
            ids.append(int(config['id']))
        except (ValueError, KeyError):
            continue
    
    return max(ids) + 1 if ids else 1

if __name__ == '__main__':
    app.run(debug=True, port=5000)