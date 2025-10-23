from database.xml_storage import guardar_factura, cargar_datos
from database.models import Factura
from datetime import datetime
import time

def generar_facturas(fecha_inicio, fecha_fin):
    try:
        print(f"=== INICIANDO FACTURACIÓN: {fecha_inicio} a {fecha_fin} ===")
        print(f"Fecha fin recibida: '{fecha_fin}'")
        facturas_generadas = []
        
        consumos = cargar_datos('consumos')
        configuraciones = cargar_datos('configuraciones')
        
        print(f"Consumos cargados: {len(consumos)}")
        print(f"Configuraciones cargadas: {len(configuraciones)}")
        
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
                costo_instancia = calcular_costo_instancia(id_instancia, tiempo_total, configuraciones)
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

def calcular_costo_instancia(id_instancia, tiempo_total, configuraciones):
    try:
        costo_total = 0
        
        # Buscar la instancia en los clientes
        for config_data in configuraciones:
            if config_data['tipo'] == 'cliente':
                for instancia in config_data.get('instancias', []):
                    if instancia['id'] == str(id_instancia):
                        id_configuracion = instancia['idConfiguracion']
                        print(f"    Configuración encontrada: {id_configuracion}")
                        
                        # Buscar la configuración en las categorías
                        for cat_data in configuraciones:
                            if cat_data['tipo'] == 'categoria':
                                for config in cat_data.get('configuraciones', []):
                                    if config['id'] == id_configuracion:
                                        for recurso_id, cantidad in config.get('recursos', {}).items():
                                            recurso_info = obtener_recurso_info(recurso_id, configuraciones)
                                            if recurso_info:
                                                costo_recurso = float(recurso_info['valor_x_hora']) * float(cantidad) * tiempo_total
                                                costo_total += costo_recurso
                                                print(f"      Recurso {recurso_id}: Q{costo_recurso:.2f}")
        return round(costo_total, 2)
    except Exception as e:
        print(f"Error calculando costo: {e}")
        return 0

def obtener_recurso_info(id_recurso, configuraciones):
    for data in configuraciones:
        if data['tipo'] == 'recurso' and data['id'] == id_recurso:
            return data
    return None