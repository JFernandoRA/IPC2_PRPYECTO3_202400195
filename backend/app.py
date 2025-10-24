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
from database.models import Recurso, Categoria, Cliente

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
        from utils.validators import validar_nit
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
    

if __name__ == '__main__':
    app.run(debug=True, port=5000)