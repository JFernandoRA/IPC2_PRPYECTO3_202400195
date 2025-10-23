from database.xml_storage import guardar_recurso, guardar_categoria, guardar_cliente
from database.models import Recurso, Configuracion, Categoria, Cliente, Instancia
from utils.xml_parser import parsear_xml_configuracion
from utils.validators import validar_nit, extraer_fecha

def procesar_configuracion(xml_data):
    try:
        recursos, categorias, clientes = parsear_xml_configuracion(xml_data)
        
        resultados = {
            'recursos_creados': len(recursos),
            'categorias_creadas': len(categorias),
            'clientes_creados': len(clientes),
            'instancias_creadas': sum(len(cliente.instancias) for cliente in clientes),
            'errores': []
        }

        print(f"RESULTADOS DEL PARSER: {resultados}")
        
        for recurso in recursos:
            try:
                guardar_recurso(recurso)
                print(f"Recurso guardado: {recurso.nombre}")
            except Exception as e:
                resultados['errores'].append(f"Error guardando recurso {recurso.id_recurso}: {str(e)}")
        
        for categoria in categorias:
            try:
                guardar_categoria(categoria)
                print(f"Categoria guardada: {categoria.nombre}")
            except Exception as e:
                resultados['errores'].append(f"Error guardando categoria {categoria.id_categoria}: {str(e)}")
        
        for cliente in clientes:
            try:
                if not validar_nit(cliente.nit):
                    resultados['errores'].append(f"NIT inválido: {cliente.nit}")
                    continue
                
                for instancia in cliente.instancias:
                    instancia.fecha_inicio = extraer_fecha(instancia.fecha_inicio)
                    if instancia.fecha_final:
                        instancia.fecha_final = extraer_fecha(instancia.fecha_final)
                
                guardar_cliente(cliente)
                print(f"Cliente guardado: {cliente.nombre}")
            except Exception as e:
                resultados['errores'].append(f"Error guardando cliente {cliente.nit}: {str(e)}")
        
        return resultados
        
    except Exception as e:
        print(f"ERROR en procesar_configuracion: {str(e)}")
        return {'error': f"Error procesando configuración: {str(e)}"}