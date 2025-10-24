import xml.etree.ElementTree as ET
from database.models import Recurso, Configuracion, Categoria, Cliente, Instancia, Consumo

def parsear_xml_configuracion(xml_data):
    print("=== INICIANDO PARSER XML CONFIGURACIÓN ===")
    
    try:
        root = ET.fromstring(xml_data)
    except Exception as e:
        print(f"ERROR parseando XML: {e}")
        return [], [], []

    recursos = []
    categorias = []
    clientes = []

    def get_text(element, tag_name):
        elem = element.find(tag_name)
        return elem.text.strip() if elem is not None and elem.text else ""

    # PARSEAR RECURSOS
    lista_recursos = root.find('listaRecursos')
    if lista_recursos is not None:
        for recurso_elem in lista_recursos.findall('recurso'):
            try:
                recurso = Recurso(
                    id_recurso=int(recurso_elem.get('id')),
                    nombre=get_text(recurso_elem, 'nombre'),
                    abreviatura=get_text(recurso_elem, 'abreviatura'),
                    metrica=get_text(recurso_elem, 'metrica'),
                    tipo=get_text(recurso_elem, 'tipo'),
                    valor_x_hora=float(get_text(recurso_elem, 'valorXhora'))
                )
                recursos.append(recurso)
                print(f"✓ Recurso {recurso.id_recurso}: {recurso.nombre}")
            except Exception as e:
                print(f"✗ Error en recurso {recurso_elem.get('id')}: {e}")

    # PARSEAR CATEGORÍAS Y CONFIGURACIONES
    lista_categorias = root.find('listaCategorias')
    if lista_categorias is not None:
        for categoria_elem in lista_categorias.findall('categoria'):
            try:
                configuraciones = []
                lista_configs = categoria_elem.find('listaConfiguraciones')
                
                if lista_configs is not None:
                    for config_elem in lista_configs.findall('configuracion'):
                        try:
                            # BUSCAR RECURSOS EN TODAS LAS POSIBLES ESTRUCTURAS
                            recursos_config = {}
                            
                            # Intentar diferentes nombres de elementos
                            posibles_elementos = [
                                'recursosConfiguracion', 
                                'recursoConfiguracion', 
                                'recursos',
                                'recursoConfig',
                                'configuracionRecursos'
                            ]
                            
                            recursos_encontrados = False
                            for elem_name in posibles_elementos:
                                recursos_elem = config_elem.find(elem_name)
                                if recursos_elem is not None:
                                    print(f"  Encontrado elemento: {elem_name}")
                                    for recurso_config in recursos_elem.findall('recurso'):
                                        recurso_id = recurso_config.get('id')
                                        cantidad = recurso_config.text
                                        if recurso_id and cantidad and cantidad.strip():
                                            recursos_config[int(recurso_id)] = float(cantidad.strip())
                                            print(f"    Recurso {recurso_id} -> {cantidad}")
                                    recursos_encontrados = True
                                    break
                            
                            # Si no encontró con nombres específicos, buscar cualquier elemento que contenga recursos
                            if not recursos_encontrados:
                                for elem in config_elem:
                                    if 'recurso' in elem.tag.lower():
                                        print(f"  Encontrado elemento alternativo: {elem.tag}")
                                        for recurso_config in elem.findall('recurso'):
                                            recurso_id = recurso_config.get('id')
                                            cantidad = recurso_config.text
                                            if recurso_id and cantidad and cantidad.strip():
                                                recursos_config[int(recurso_id)] = float(cantidad.strip())
                                                print(f"    Recurso {recurso_id} -> {cantidad}")
                                        break
                            
                            print(f"  Recursos encontrados en configuración {config_elem.get('id')}: {recursos_config}")
                            
                            configuracion = Configuracion(
                                id_configuracion=int(config_elem.get('id')),
                                nombre=get_text(config_elem, 'nombre'),
                                descripcion=get_text(config_elem, 'descripcion'),
                                recursos=recursos_config
                            )
                            configuraciones.append(configuracion)
                            print(f"✓ Configuración {config_elem.get('id')} con {len(recursos_config)} recursos")
                            
                        except Exception as e:
                            print(f"✗ Error en configuración {config_elem.get('id')}: {e}")

                categoria = Categoria(
                    id_categoria=int(categoria_elem.get('id')),
                    nombre=get_text(categoria_elem, 'nombre'),
                    descripcion=get_text(categoria_elem, 'descripcion'),
                    carga_trabajo=get_text(categoria_elem, 'cargaTrabajo'),
                    configuraciones=configuraciones
                )
                categorias.append(categoria)
                print(f"✓ Categoría {categoria.id_categoria}: {categoria.nombre}")
                
            except Exception as e:
                print(f"✗ Error en categoría {categoria_elem.get('id')}: {e}")

    # PARSEAR CLIENTES E INSTANCIAS
    lista_clientes = root.find('listaClientes')
    if lista_clientes is not None:
        for cliente_elem in lista_clientes.findall('cliente'):
            try:
                instancias = []
                lista_instancias = cliente_elem.find('listaInstancias')
                
                if lista_instancias is not None:
                    for instancia_elem in lista_instancias.findall('instancia'):
                        try:
                            fecha_final = get_text(instancia_elem, 'fechaFinal')
                            
                            instancia = Instancia(
                                id_instancia=int(instancia_elem.get('id')),
                                id_configuracion=int(get_text(instancia_elem, 'idConfiguracion')),
                                nombre=get_text(instancia_elem, 'nombre'),
                                fecha_inicio=get_text(instancia_elem, 'fechaInicio'),
                                estado=get_text(instancia_elem, 'estado'),
                                fecha_final=fecha_final if fecha_final else None
                            )
                            instancias.append(instancia)
                            print(f"✓ Instancia {instancia.id_instancia} para cliente {cliente_elem.get('nit')}")
                            
                        except Exception as e:
                            print(f"✗ Error en instancia {instancia_elem.get('id')}: {e}")

                cliente = Cliente(
                    nit=cliente_elem.get('nit'),
                    nombre=get_text(cliente_elem, 'nombre'),
                    usuario=get_text(cliente_elem, 'usuario'),
                    clave=get_text(cliente_elem, 'clave'),
                    direccion=get_text(cliente_elem, 'direccion'),
                    correo=get_text(cliente_elem, 'correoElectronico'),
                    instancias=instancias
                )
                clientes.append(cliente)
                print(f"✓ Cliente {cliente.nit}: {cliente.nombre}")
                
            except Exception as e:
                print(f"✗ Error en cliente {cliente_elem.get('nit')}: {e}")

    print(f"=== RESUMEN: {len(recursos)} recursos, {len(categorias)} categorías, {len(clientes)} clientes ===")
    return recursos, categorias, clientes

def parsear_xml_consumo(xml_data):
    print("=== INICIANDO PARSER XML CONSUMO ===")
    try:
        root = ET.fromstring(xml_data)
        consumos = []
        
        for consumo_elem in root.findall('consumo'):
            try:
                consumo = Consumo(
                    nit_cliente=consumo_elem.get('nitCliente'),
                    id_instancia=int(consumo_elem.get('idInstancia')),
                    tiempo=float(consumo_elem.find('tiempo').text),
                    fecha_hora=consumo_elem.find('fechahora').text.strip()
                )
                consumos.append(consumo)
                print(f"✓ Consumo: Cliente {consumo.nit_cliente}, Instancia {consumo.id_instancia}")
            except Exception as e:
                print(f"✗ Error en consumo: {e}")
        
        print(f"=== CONSUMOS PROCESADOS: {len(consumos)} ===")
        return consumos
        
    except Exception as e:
        print(f"ERROR parseando consumo XML: {e}")
        return []