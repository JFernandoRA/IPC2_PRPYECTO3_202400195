import xml.etree.ElementTree as ET
from database.models import Recurso, Configuracion, Categoria, Cliente, Instancia, Consumo

def parsear_xml_configuracion(xml_data):
    print("=== INICIANDO PARSER XML ===")
    
    try:
        root = ET.fromstring(xml_data)
    except Exception as e:
        print(f"ERROR parseando XML: {e}")
        return [], [], []

    print(f"TAG RAIZ: {root.tag}")

    recursos = []
    categorias = []
    clientes = []

    def get_text(element, tag_name):
        elem = element.find(tag_name)
        if elem is not None and elem.text is not None:
            return elem.text.strip()
        return None

    lista_recursos = root.find('listaRecursos')
    if lista_recursos is not None:
        for recurso_elem in lista_recursos.findall('recurso'):
            recurso_id = recurso_elem.get('id')
            nombre = get_text(recurso_elem, 'nombre')
            abreviatura = get_text(recurso_elem, 'abreviatura')
            metrica = get_text(recurso_elem, 'metrica')
            tipo = get_text(recurso_elem, 'tipo')
            valor_x_hora = get_text(recurso_elem, 'valorXhora')

            print(f"Recurso {recurso_id}: nombre='{nombre}'")

            if nombre and abreviatura and metrica and tipo and valor_x_hora:
                try:
                    recurso = Recurso(
                        id_recurso=int(recurso_id),
                        nombre=nombre,
                        abreviatura=abreviatura,
                        metrica=metrica,
                        tipo=tipo,
                        valor_x_hora=float(valor_x_hora)
                    )
                    recursos.append(recurso)
                    print(f"  ✓ Recurso {recurso_id} agregado")
                except ValueError as e:
                    print(f"  ✗ Error en recurso {recurso_id}: {e}")

    lista_categorias = root.find('listaCategorias')
    if lista_categorias is not None:
        for categoria_elem in lista_categorias.findall('categoria'):
            categoria_id = categoria_elem.get('id')
            nombre = get_text(categoria_elem, 'nombre')
            descripcion = get_text(categoria_elem, 'descripcion')
            carga_trabajo = get_text(categoria_elem, 'cargaTrabajo')

            print(f"Categoria {categoria_id}: nombre='{nombre}'")

            configuraciones = []
            lista_configs = categoria_elem.find('listaConfiguraciones')
            if lista_configs is not None:
                for config_elem in lista_configs.findall('configuracion'):
                    config_id = config_elem.get('id')
                    config_nombre = get_text(config_elem, 'nombre')
                    config_descripcion = get_text(config_elem, 'descripcion')

                    recursos_config = {}
                    recursos_elem = config_elem.find('recursoConfiguracion')
                    if recursos_elem is not None:
                        for recurso_config in recursos_elem.findall('recurso'):
                            recurso_id = recurso_config.get('id')
                            cantidad = recurso_config.text
                            if cantidad and recurso_id:
                                try:
                                    recursos_config[int(recurso_id)] = float(cantidad.strip())
                                    print(f"    Recurso config: {recurso_id} -> {cantidad}")
                                except ValueError:
                                    print(f"    Error en cantidad: {cantidad}")

                    if config_nombre and config_descripcion:
                        try:
                            configuracion = Configuracion(
                                id_configuracion=int(config_id),
                                nombre=config_nombre,
                                descripcion=config_descripcion,
                                recursos=recursos_config
                            )
                            configuraciones.append(configuracion)
                            print(f"    ✓ Configuración {config_id} agregada")
                        except ValueError as e:
                            print(f"    ✗ Error en configuración {config_id}: {e}")

            if nombre and descripcion and carga_trabajo:
                try:
                    categoria = Categoria(
                        id_categoria=int(categoria_id),
                        nombre=nombre,
                        descripcion=descripcion,
                        carga_trabajo=carga_trabajo,
                        configuraciones=configuraciones
                    )
                    categorias.append(categoria)
                    print(f"  ✓ Categoria {categoria_id} agregada")
                except ValueError as e:
                    print(f"  ✗ Error en categoria {categoria_id}: {e}")

    lista_clientes = root.find('listaClientes')
    if lista_clientes is not None:
        for cliente_elem in lista_clientes.findall('cliente'):
            nit = cliente_elem.get('nit')
            nombre = get_text(cliente_elem, 'nombre')
            usuario = get_text(cliente_elem, 'usuario')
            clave = get_text(cliente_elem, 'clave')
            direccion = get_text(cliente_elem, 'direccion')
            correo = get_text(cliente_elem, 'correoElectronico')

            print(f"Cliente {nit}: nombre='{nombre}'")

            instancias = []
            lista_instancias = cliente_elem.find('listaInstancias')
            if lista_instancias is not None:
                for instancia_elem in lista_instancias.findall('instancia'):
                    instancia_id = instancia_elem.get('id')
                    id_configuracion = get_text(instancia_elem, 'idConfiguracion')
                    instancia_nombre = get_text(instancia_elem, 'nombre')
                    fecha_inicio = get_text(instancia_elem, 'fechaInicio')
                    estado = get_text(instancia_elem, 'estado')
                    fecha_final = get_text(instancia_elem, 'fechaFinal')

                    print(f"  Instancia {instancia_id}: config='{id_configuracion}', nombre='{instancia_nombre}'")

                    if id_configuracion and instancia_nombre and fecha_inicio and estado:
                        try:
                            instancia = Instancia(
                                id_instancia=int(instancia_id),
                                id_configuracion=int(id_configuracion),
                                nombre=instancia_nombre,
                                fecha_inicio=fecha_inicio,
                                estado=estado,
                                fecha_final=fecha_final
                            )
                            instancias.append(instancia)
                            print(f"    ✓ Instancia {instancia_id} agregada")
                        except ValueError as e:
                            print(f"    ✗ Error en instancia {instancia_id}: {e}")

            if nombre and usuario and clave and direccion and correo:
                try:
                    cliente = Cliente(
                        nit=nit,
                        nombre=nombre,
                        usuario=usuario,
                        clave=clave,
                        direccion=direccion,
                        correo=correo,
                        instancias=instancias
                    )
                    clientes.append(cliente)
                    print(f"  ✓ Cliente {nit} agregado")
                except Exception as e:
                    print(f"  ✗ Error en cliente {nit}: {e}")

    print(f"=== RESUMEN FINAL ===")
    print(f"Recursos procesados: {len(recursos)}")
    print(f"Categorias procesadas: {len(categorias)}")
    print(f"Clientes procesados: {len(clientes)}")
    print("=== FIN PARSER XML ===")

    return recursos, categorias, clientes

def parsear_xml_consumo(xml_data):
    print("=== INICIANDO PARSER CONSUMO ===")
    try:
        root = ET.fromstring(xml_data)
        consumos = []
        
        print(f"Elementos en raíz: {[elem.tag for elem in root]}")
        
        # FUNCIÓN AUXILIAR (la misma que en config)
        def get_text(element, tag_name):
            elem = element.find(tag_name)
            if elem is not None and elem.text is not None:
                return elem.text.strip()
            return None
        
        for consumo_elem in root.findall('consumo'):
            nit_cliente = consumo_elem.get('nitCliente')
            id_instancia = consumo_elem.get('idInstancia')
            tiempo = get_text(consumo_elem, 'tiempo')
            fecha_hora = get_text(consumo_elem, 'fechahora')
            
            print(f"Consumo encontrado: nit={nit_cliente}, instancia={id_instancia}")
            print(f"  tiempo: '{tiempo}'")
            print(f"  fechahora: '{fecha_hora}'")
            
            if all([nit_cliente, id_instancia, tiempo, fecha_hora]):
                try:
                    consumo = Consumo(
                        nit_cliente=nit_cliente,
                        id_instancia=int(id_instancia),
                        tiempo=float(tiempo),
                        fecha_hora=fecha_hora
                    )
                    consumos.append(consumo)
                    print(f"  ✓ Consumo agregado")
                except ValueError as e:
                    print(f"  ✗ Error en consumo: {e}")
            else:
                print(f"  ✗ Consumo incompleto")
        
        print(f"=== CONSUMOS PARSER: {len(consumos)} consumos procesados ===")
        return consumos
    except Exception as e:
        print(f"Error parseando consumo XML: {e}")
        return []