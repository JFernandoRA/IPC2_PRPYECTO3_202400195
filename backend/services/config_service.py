from database.xml_storage import guardar_recurso, guardar_categoria, guardar_cliente, cargar_datos
from database.models import Recurso, Configuracion, Categoria, Cliente, Instancia
from utils.xml_parser import parsear_xml_configuracion
from database.xml_storage import guardar_recurso, guardar_categoria, guardar_cliente, cargar_recursos, cargar_categorias, cargar_clientes
from utils.validators import validar_nit, extraer_fecha

def procesar_configuracion(xml_data):
    try:
        # Cargar datos existentes desde los archivos separados
        recursos_existentes = cargar_recursos()
        categorias_existentes = cargar_categorias()
        clientes_existentes = cargar_clientes()
        
        print(f"🔍 EXISTENTES - Recursos: {len(recursos_existentes)}, Categorías: {len(categorias_existentes)}, Clientes: {len(clientes_existentes)}")
        
        # Parsear el nuevo XML
        recursos_nuevos, categorias_nuevas, clientes_nuevos = parsear_xml_configuracion(xml_data)
        
        print(f"🔍 NUEVOS - Recursos: {len(recursos_nuevos)}, Categorías: {len(categorias_nuevas)}, Clientes: {len(clientes_nuevos)}")
        
        # Combinar datos (usar la función combinar_datos que ya tienes)
        recursos_combinados = combinar_datos(recursos_existentes, recursos_nuevos, 'recurso')
        categorias_combinadas = combinar_datos(categorias_existentes, categorias_nuevas, 'categoria')
        clientes_combinados = combinar_datos(clientes_existentes, clientes_nuevos, 'cliente')
        
        # CUARTO: Guardar los datos COMBINADOS
        resultados = {
            'recursos_creados': len(recursos_nuevos),
            'categorias_creadas': len(categorias_nuevas),
            'clientes_creados': len(clientes_nuevos),
            'instancias_creadas': sum(len(cliente.instancias) for cliente in clientes_nuevos),
            'errores': []
        }

        # Guardar todos los recursos combinados
        for recurso in recursos_combinados:
            try:
                guardar_recurso(recurso)
                print(f"✅ Recurso guardado: {recurso.nombre} (ID: {recurso.id_recurso})")
            except Exception as e:
                resultados['errores'].append(f"Error guardando recurso {recurso.id_recurso}: {str(e)}")
        
        # Guardar todas las categorías combinadas
        for categoria in categorias_combinadas:
            try:
                guardar_categoria(categoria)
                print(f"✅ Categoría guardada: {categoria.nombre} (ID: {categoria.id_categoria})")
            except Exception as e:
                resultados['errores'].append(f"Error guardando categoria {categoria.id_categoria}: {str(e)}")
        
        # Guardar todos los clientes combinados
        for cliente in clientes_combinados:
            try:
                if not validar_nit(cliente.nit):
                    resultados['errores'].append(f"NIT inválido: {cliente.nit}")
                    continue
                
                for instancia in cliente.instancias:
                    instancia.fecha_inicio = extraer_fecha(instancia.fecha_inicio)
                    if instancia.fecha_final:
                        instancia.fecha_final = extraer_fecha(instancia.fecha_final)
                
                guardar_cliente(cliente)
                print(f"✅ Cliente guardado: {cliente.nombre} (NIT: {cliente.nit})")
            except Exception as e:
                resultados['errores'].append(f"Error guardando cliente {cliente.nit}: {str(e)}")
        
        print(f"🎯 RESULTADO FINAL - Recursos totales: {len(recursos_combinados)}, Categorías totales: {len(categorias_combinadas)}, Clientes totales: {len(clientes_combinados)}")
        
        return resultados
        
    except Exception as e:
        print(f"ERROR en procesar_configuracion: {str(e)}")
        return {'error': f"Error procesando configuración: {str(e)}"}

def combinar_datos(datos_existentes, datos_nuevos, tipo_dato):
    """Combina datos existentes con nuevos datos, evitando duplicados"""
    combinados = []
    
    # Convertir datos existentes a objetos del tipo correcto
    if tipo_dato == 'recurso':
        # Agregar recursos existentes
        for dato in datos_existentes:
            if dato.get('tipo') == 'recurso':
                recurso = Recurso(
                    id_recurso=int(dato['id']),
                    nombre=dato['nombre'],
                    abreviatura=dato['abreviatura'],
                    metrica=dato['metrica'],
                    tipo=dato['tipo_recurso'],
                    valor_x_hora=float(dato['valor_x_hora'])
                )
                combinados.append(recurso)
        
        # Agregar recursos nuevos (sobrescribiendo si hay mismo ID)
        for nuevo in datos_nuevos:
            # Buscar si ya existe un recurso con el mismo ID
            existe = False
            for i, existente in enumerate(combinados):
                if existente.id_recurso == nuevo.id_recurso:
                    combinados[i] = nuevo  # Reemplazar el existente
                    existe = True
                    print(f"🔄 Actualizando recurso existente ID: {nuevo.id_recurso}")
                    break
            
            if not existe:
                combinados.append(nuevo)
                print(f"✅ Agregando nuevo recurso ID: {nuevo.id_recurso}")
    
    elif tipo_dato == 'categoria':
        # Lógica similar para categorías
        for dato in datos_existentes:
            if dato.get('tipo') == 'categoria':
                # Convertir datos de categoría existente a objeto Categoria
                configuraciones = []
                for config_data in dato.get('configuraciones', []):
                    recursos_config = {}
                    for recurso_id, cantidad in config_data.get('recursos', {}).items():
                        recursos_config[int(recurso_id)] = float(cantidad)
                    
                    config = Configuracion(
                        id_configuracion=int(config_data['id']),
                        nombre=config_data['nombre'],
                        descripcion=config_data['descripcion'],
                        recursos=recursos_config
                    )
                    configuraciones.append(config)
                
                categoria = Categoria(
                    id_categoria=int(dato['id']),
                    nombre=dato['nombre'],
                    descripcion=dato['descripcion'],
                    carga_trabajo=dato['carga_trabajo'],
                    configuraciones=configuraciones
                )
                combinados.append(categoria)
        
        # Agregar categorías nuevas
        for nuevo in datos_nuevos:
            existe = False
            for i, existente in enumerate(combinados):
                if existente.id_categoria == nuevo.id_categoria:
                    combinados[i] = nuevo
                    existe = True
                    print(f"🔄 Actualizando categoría existente ID: {nuevo.id_categoria}")
                    break
            
            if not existe:
                combinados.append(nuevo)
                print(f"✅ Agregando nueva categoría ID: {nuevo.id_categoria}")
    
    elif tipo_dato == 'cliente':
        # Lógica similar para clientes
        for dato in datos_existentes:
            if dato.get('tipo') == 'cliente':
                # Convertir datos de cliente existente a objeto Cliente
                instancias = []
                for inst_data in dato.get('instancias', []):
                    instancia = Instancia(
                        id_instancia=int(inst_data['id']),
                        id_configuracion=int(inst_data['idConfiguracion']),
                        nombre=inst_data['nombre'],
                        fecha_inicio=inst_data['fechaInicio'],
                        estado=inst_data['estado'],
                        fecha_final=inst_data.get('fechaFinal')
                    )
                    instancias.append(instancia)
                
                cliente = Cliente(
                    nit=dato['nit'],
                    nombre=dato['nombre'],
                    usuario=dato['usuario'],
                    clave=dato.get('clave', ''),
                    direccion=dato.get('direccion', ''),
                    correo=dato.get('correo', ''),
                    instancias=instancias
                )
                combinados.append(cliente)
        
        # Agregar clientes nuevos
        for nuevo in datos_nuevos:
            existe = False
            for i, existente in enumerate(combinados):
                if existente.nit == nuevo.nit:
                    combinados[i] = nuevo
                    existe = True
                    print(f"🔄 Actualizando cliente existente NIT: {nuevo.nit}")
                    break
            
            if not existe:
                combinados.append(nuevo)
                print(f"✅ Agregando nuevo cliente NIT: {nuevo.nit}")
    
    return combinados