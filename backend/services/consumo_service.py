from database.xml_storage import guardar_consumo
from utils.xml_parser import parsear_xml_consumo
from utils.validators import extraer_fecha_hora

def procesar_consumo(xml_data):
    try:
        consumos = parsear_xml_consumo(xml_data)
        
        resultados = {
            'consumos_procesados': len(consumos),
            'errores': []
        }

        print(f"RESULTADOS CONSUMO: {resultados}")
        
        for consumo in consumos:
            try:
                consumo.fecha_hora = extraer_fecha_hora(consumo.fecha_hora)
                guardar_consumo(consumo)
                print(f"Consumo guardado: {consumo.nit_cliente} - Instancia {consumo.id_instancia}")
            except Exception as e:
                resultados['errores'].append(f"Error procesando consumo: {str(e)}")
        
        return resultados
        
    except Exception as e:
        print(f"ERROR en procesar_consumo: {str(e)}")
        return {'error': f"Error procesando consumo: {str(e)}"}