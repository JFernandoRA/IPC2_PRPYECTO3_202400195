from flask import Flask, request, jsonify
from services.config_service import procesar_configuracion
from services.consumo_service import procesar_consumo
from services.facturacion_service import generar_facturas
from services.report_service import generar_reporte_factura, generar_analisis_ventas
from database.xml_storage import reset_database, guardar_recurso, guardar_categoria, cargar_datos
from database.models import Recurso, Categoria

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
    from database.xml_storage import cargar_datos
    if tipo in ['recursos', 'categorias', 'clientes']:
        datos = cargar_datos('configuraciones', tipo)
    else:
        datos = cargar_datos(tipo)
    
    return jsonify(datos)

@app.route('/crear/recurso', methods=['POST'])
def crear_recurso():
    data = request.json
    nuevo_recurso = Recurso(
        id_recurso=generar_id_recurso(),
        nombre=data.get('nombre'),
        abreviatura=data.get('abreviatura'),
        metrica=data.get('metrica'),
        tipo=data.get('tipo'),
        valor_x_hora=data.get('valor')
    )
    guardar_recurso(nuevo_recurso)
    return jsonify({"mensaje": "Recurso creado exitosamente"})

@app.route('/crear/categoria', methods=['POST'])
def crear_categoria():
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

def generar_id_recurso():
    datos = cargar_datos('configuraciones')
    recursos = [d for d in datos if d['tipo'] == 'recurso']
    if recursos:
        return max([int(r['id']) for r in recursos]) + 1
    return 1

def generar_id_categoria():
    datos = cargar_datos('configuraciones')
    categorias = [d for d in datos if d['tipo'] == 'categoria']
    if categorias:
        return max([int(c['id']) for c in categorias]) + 1
    return 1

if __name__ == '__main__':
    app.run(debug=True, port=5000)