from database.xml_storage import guardar_factura, cargar_recursos, cargar_categorias, cargar_clientes, cargar_consumos
from database.models import Factura
from datetime import datetime

def generar_facturas(fecha_inicio, fecha_fin):
    try:
        print(f"=== INICIANDO FACTURACIÓN: {fecha_inicio} a {fecha_fin} ===")
        
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
        
        # Cargar datos
        consumos = cargar_consumos()
        clientes = cargar_clientes()
        categorias = cargar_categorias()
        recursos = cargar_recursos()
        
        print(f"Consumos cargados: {len(consumos)}")
        print(f"Clientes cargados: {len(clientes)}")
        print(f"Categorías cargadas: {len(categorias)}")
        print(f"Recursos cargados: {len(recursos)}")
        
        # DEBUG: Mostrar estructura completa
        print("\n=== DEBUG ESTRUCTURA COMPLETA ===")
        print("CLIENTES:")
        for cliente in clientes:
            print(f"  NIT: {cliente['nit']}, Nombre: {cliente.get('nombre', 'N/A')}")
            for instancia in cliente.get('instancias', []):
                print(f"    Instancia ID: {instancia['id']}, Config: {instancia['idConfiguracion']}")
        
        print("\nCATEGORÍAS Y CONFIGURACIONES:")
        for categoria in categorias:
            print(f"  Categoría: {categoria['nombre']} (ID: {categoria['id']})")
            for config in categoria.get('configuraciones', []):
                print(f"    Configuración ID: {config['id']}, Nombre: {config.get('nombre', 'N/A')}")
                recursos_config = config.get('recursos', {})
                print(f"      Recursos: {recursos_config}")
                if recursos_config:
                    for recurso_id, cantidad in recursos_config.items():
                        print(f"        Recurso ID: {recurso_id}, Cantidad: {cantidad}")
                else:
                    print(f"        ⚠️ NO HAY RECURSOS EN ESTA CONFIGURACIÓN")
        
        print("\nRECURSOS DISPONIBLES:")
        for recurso in recursos:
            print(f"  ID: {recurso['id']}, Nombre: {recurso['nombre']}, Valor/hora: Q{recurso['valor_x_hora']}")
        
        print("\nCONSUMOS:")
        for consumo in consumos:
            print(f"  NIT: {consumo['nitCliente']}, Instancia: {consumo['idInstancia']}, Tiempo: {consumo['tiempo']} horas")
        
        # Si no hay consumos, retornar vacío
        if not consumos:
            print("⚠️ No hay consumos para facturar")
            return {
                'facturas_generadas': 0,
                'detalles': []
            }
        
        # Agrupar consumos por cliente
        consumos_por_cliente = {}
        for consumo in consumos:
            nit_cliente = consumo['nitCliente']
            if nit_cliente not in consumos_por_cliente:
                consumos_por_cliente[nit_cliente] = []
            consumos_por_cliente[nit_cliente].append(consumo)
        
        print(f"Clientes con consumos: {list(consumos_por_cliente.keys())}")
        
        for nit_cliente, consumos_cliente in consumos_por_cliente.items():
            print(f"\nProcesando cliente: {nit_cliente}")
            
            # Verificar si el cliente existe en el sistema
            cliente_existe = any(cliente['nit'] == nit_cliente for cliente in clientes)
            if not cliente_existe:
                print(f"⚠️ Cliente {nit_cliente} no existe en el sistema, saltando...")
                continue
            
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
                print(f"  Procesando instancia {id_instancia} - Tiempo total: {tiempo_total} horas")
                
                costo_instancia = calcular_costo_instancia(id_instancia, tiempo_total, clientes, categorias, recursos)
                
                if costo_instancia > 0:
                    total_factura += costo_instancia
                    detalles_factura.append({
                        'id_instancia': id_instancia,
                        'tiempo_total': tiempo_total,
                        'monto': costo_instancia
                    })
                    print(f"  ✓ Instancia {id_instancia}: {tiempo_total} horas = Q{costo_instancia:.2f}")
                else:
                    print(f"  ⚠️ Instancia {id_instancia}: {tiempo_total} horas = Q0.00 (no facturable)")
            
            if total_factura > 0:
                # NÚMERO DE FACTURA ÚNICO
                numero_factura = generar_numero_factura(nit_cliente)
                
                factura = Factura(
                    numero_factura=numero_factura,
                    nit_cliente=nit_cliente,
                    fecha_factura=fecha_fin,
                    monto_total=round(total_factura, 2),
                    detalles=detalles_factura
                )
                
                # GUARDAR LA FACTURA
                guardar_factura(factura)
                facturas_generadas.append({
                    'numero_factura': numero_factura,
                    'nit_cliente': nit_cliente,
                    'monto_total': round(total_factura, 2)
                })
                
                print(f"✓ Factura {numero_factura} generada: Q{total_factura:.2f}")
            else:
                print(f"⚠️ Cliente {nit_cliente} no tiene consumos facturables (total: Q{total_factura:.2f})")
        
        resultado = {
            'facturas_generadas': len(facturas_generadas),
            'detalles': facturas_generadas
        }
        
        print(f"\n=== FACTURACIÓN COMPLETADA: {resultado} ===")
        return resultado
        
    except Exception as e:
        print(f"ERROR en facturación: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {'error': f"Error en facturación: {str(e)}"}

def generar_numero_factura(nit_cliente):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    # Incluir parte del NIT para hacer único por cliente
    nit_short = nit_cliente.replace('-', '')[:4]
    return f"FACT-{timestamp}-{nit_short}"

def calcular_costo_instancia(id_instancia, tiempo_total, clientes, categorias, recursos):
    try:
        costo_total = 0
        
        print(f"    Buscando instancia {id_instancia}...")
        
        # Buscar la instancia en los clientes
        instancia_encontrada = False
        configuracion_encontrada = False
        id_configuracion = None
        
        for cliente in clientes:
            for instancia in cliente.get('instancias', []):
                # Comparar como strings para evitar problemas de tipo
                instancia_id_str = str(instancia['id']).strip()
                id_instancia_str = str(id_instancia).strip()
                
                if instancia_id_str == id_instancia_str:
                    id_configuracion = instancia['idConfiguracion']
                    print(f"    ✓ Instancia encontrada: ID {id_instancia}, Configuración: {id_configuracion}")
                    instancia_encontrada = True
                    break
            if instancia_encontrada:
                break
        
        if not instancia_encontrada:
            print(f"    ⚠️ Instancia {id_instancia} no encontrada en ningún cliente")
            return 0
        
        # Buscar la configuración en las categorías
        print(f"    Buscando configuración {id_configuracion}...")
        
        for categoria in categorias:
            for config in categoria.get('configuraciones', []):
                # Comparar como strings
                config_id_str = str(config['id']).strip()
                id_configuracion_str = str(id_configuracion).strip()
                
                if config_id_str == id_configuracion_str:
                    print(f"    ✓ Configuración {id_configuracion} encontrada en categoría {categoria['nombre']}")
                    configuracion_encontrada = True
                    
                    # Verificar si la configuración tiene recursos
                    recursos_config = config.get('recursos', {})
                    if not recursos_config:
                        print(f"    ⚠️ CRÍTICO: La configuración {id_configuracion} NO TIENE RECURSOS ASIGNADOS")
                        print(f"    ℹ️  Revisa el archivo XML de categorías en backend/data/categorias.xml")
                        print(f"    ℹ️  La configuración debe tener recursos dentro de <recursos>")
                        return 0
                    
                    print(f"    Recursos en configuración: {recursos_config}")
                    
                    # Calcular costo por cada recurso en la configuración
                    for recurso_id, cantidad in recursos_config.items():
                        recurso_id_str = str(recurso_id).strip()
                        print(f"      Procesando recurso {recurso_id_str}, cantidad: {cantidad}")
                        
                        recurso_info = obtener_recurso_info(recurso_id_str, recursos)
                        if recurso_info:
                            try:
                                valor_hora = float(recurso_info['valor_x_hora'])
                                cant = float(cantidad)
                                costo_recurso = valor_hora * cant * tiempo_total
                                costo_total += costo_recurso
                                print(f"      ✓ Recurso {recurso_id_str}: {cant} unidades x {tiempo_total} horas x Q{valor_hora}/hora = Q{costo_recurso:.2f}")
                            except (ValueError, TypeError) as e:
                                print(f"      ✗ Error calculando costo recurso {recurso_id_str}: {e}")
                        else:
                            print(f"      ⚠️ Recurso {recurso_id_str} no encontrado en recursos disponibles")
                    
                    break
            if configuracion_encontrada:
                break
        
        if not configuracion_encontrada:
            print(f"    ⚠️ Configuración {id_configuracion} no encontrada en categorías")
            return 0
        
        print(f"    Costo total para instancia {id_instancia}: Q{costo_total:.2f}")
        return round(costo_total, 2)
        
    except Exception as e:
        print(f"Error calculando costo para instancia {id_instancia}: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return 0

def obtener_recurso_info(id_recurso, recursos):
    for recurso in recursos:
        recurso_id_str = str(recurso['id']).strip()
        id_recurso_str = str(id_recurso).strip()
        
        if recurso_id_str == id_recurso_str:
            return recurso
    
    return None