from database.xml_storage import guardar_factura, cargar_recursos, cargar_categorias, cargar_clientes, cargar_consumos
from database.models import Factura
from datetime import datetime

def generar_facturas(fecha_inicio, fecha_fin):
    try:
        print(f"=== INICIANDO FACTURACIÓN: {fecha_inicio} a {fecha_fin} ===")
        print(f"Tipo fecha_inicio: {type(fecha_inicio)}, Tipo fecha_fin: {type(fecha_fin)}")
        
        # Convertir formato YYYY-MM-DD a DD/MM/YYYY si es necesario
        if fecha_inicio and '-' in str(fecha_inicio):
            try:
                fecha_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d')
                fecha_inicio = fecha_obj.strftime('%d/%m/%Y')
                print(f"Fecha inicio convertida: {fecha_inicio}")
            except Exception as e:
                print(f"Error convirtiendo fecha inicio: {e}")
        
        if fecha_fin and '-' in str(fecha_fin):
            try:
                fecha_obj = datetime.strptime(fecha_fin, '%Y-%m-%d')
                fecha_fin = fecha_obj.strftime('%d/%m/%Y')
                print(f"Fecha fin convertida: {fecha_fin}")
            except Exception as e:
                print(f"Error convirtiendo fecha fin: {e}")
        
        # Si aún son None, usar fechas por defecto
        if not fecha_inicio:
            fecha_inicio = "01/10/2025"
        if not fecha_fin:
            fecha_fin = "31/10/2025"
        
        print(f"Fechas finales: {fecha_inicio} a {fecha_fin}")
        
        facturas_generadas = []
        
        # Usar las nuevas funciones de carga
        consumos = cargar_consumos()
        clientes = cargar_clientes()
        categorias = cargar_categorias()
        recursos = cargar_recursos()
        
        print(f"Consumos cargados: {len(consumos)}")
        print(f"Clientes cargados: {len(clientes)}")
        print(f"Categorías cargadas: {len(categorias)}")
        print(f"Recursos cargados: {len(recursos)}")
        
        # Agrupar consumos por cliente
        consumos_por_cliente = {}
        for consumo in consumos:
            nit_cliente = consumo['nitCliente']
            if nit_cliente not in consumos_por_cliente:
                consumos_por_cliente[nit_cliente] = []
            consumos_por_cliente[nit_cliente].append(consumo)
        
        print(f"Clientes con consumos: {list(consumos_por_cliente.keys())}")
        
        for nit_cliente, consumos_cliente in consumos_por_cliente.items():
            print(f"Procesando cliente: {nit_cliente}")
            
            total_factura = 0
            detalles_factura = []
            
            # Agrupar consumos por instancia
            consumos_por_instancia = {}
            for consumo in consumos_cliente:
                id_instancia = consumo['idInstancia']
                if id_instancia not in consumos_por_instancia:
                    consumos_por_instancia[id_instancia] = []
                consumos_por_instancia[id_instancia].append(consumo)
            
            # Calcular costos por instancia
            for id_instancia, consumos_instancia in consumos_por_instancia.items():
                tiempo_total = sum(float(consumo['tiempo']) for consumo in consumos_instancia)
                costo_instancia = calcular_costo_instancia(id_instancia, tiempo_total, clientes, categorias, recursos)
                total_factura += costo_instancia
                
                detalles_factura.append({
                    'id_instancia': id_instancia,
                    'tiempo_total': tiempo_total,
                    'monto': costo_instancia
                })
                
                print(f"  Instancia {id_instancia}: {tiempo_total} horas = Q{costo_instancia:.2f}")
            
            if total_factura > 0:
                # NÚMERO DE FACTURA ÚNICO POR CLIENTE
                numero_factura = generar_numero_factura(nit_cliente)
                
                factura = Factura(
                    numero_factura=numero_factura,
                    nit_cliente=nit_cliente,
                    fecha_factura=fecha_fin,  # Usar la fecha de fin del período
                    monto_total=total_factura,
                    detalles=detalles_factura
                )
                
                guardar_factura(factura)
                facturas_generadas.append({
                    'numero_factura': numero_factura,
                    'nit_cliente': nit_cliente,
                    'monto_total': total_factura
                })
                
                print(f"✓ Factura {numero_factura} generada: Q{total_factura:.2f}")
        
        resultado = {
            'facturas_generadas': len(facturas_generadas),
            'detalles': facturas_generadas
        }
        
        print(f"=== FACTURACIÓN COMPLETADA: {resultado} ===")
        return resultado
        
    except Exception as e:
        print(f"ERROR en facturación: {str(e)}")
        return {'error': f"Error en facturación: {str(e)}"}

# NÚMERO DE FACTURA ÚNICO POR CLIENTE
def generar_numero_factura(nit_cliente):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    # Incluir parte del NIT para hacer único por cliente
    nit_short = nit_cliente.replace('-', '')[:4]
    return f"FACT-{timestamp}-{nit_short}"

def calcular_costo_instancia(id_instancia, tiempo_total, clientes, categorias, recursos):
    try:
        costo_total = 0
        
        print(f"    Calculando costo para instancia {id_instancia}")
        
        # Buscar la instancia en los clientes
        for cliente in clientes:
            for instancia in cliente.get('instancias', []):
                if instancia['id'] == str(id_instancia):
                    id_configuracion = instancia['idConfiguracion']
                    print(f"    Configuración encontrada: {id_configuracion}")
                    
                    # Buscar la configuración en las categorías
                    for categoria in categorias:
                        for config in categoria.get('configuraciones', []):
                            if config['id'] == id_configuracion:
                                print(f"    Configuración {id_configuracion} encontrada en categoría {categoria['nombre']}")
                                
                                # Calcular costo por cada recurso en la configuración
                                for recurso_id, cantidad in config.get('recursos', {}).items():
                                    recurso_info = obtener_recurso_info(recurso_id, recursos)
                                    if recurso_info:
                                        costo_recurso = float(recurso_info['valor_x_hora']) * float(cantidad) * tiempo_total
                                        costo_total += costo_recurso
                                        print(f"      Recurso {recurso_id}: {cantidad} unidades x {tiempo_total} horas x Q{recurso_info['valor_x_hora']}/hora = Q{costo_recurso:.2f}")
                                    else:
                                        print(f"      ⚠️ Recurso {recurso_id} no encontrado")
        
        return round(costo_total, 2)
    except Exception as e:
        print(f"Error calculando costo: {e}")
        return 0

def obtener_recurso_info(id_recurso, recursos):
    for recurso in recursos:
        if recurso['id'] == id_recurso:
            return recurso
    return None