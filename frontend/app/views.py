import requests
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings

def home(request):
    return render(request, 'home.html')

def configuracion(request):
    if request.method == 'POST' and request.FILES.get('archivo_xml'):
        archivo = request.FILES['archivo_xml']
        xml_data = archivo.read().decode('utf-8')
        
        try:
            response = requests.post(
                f'{settings.BACKEND_URL}/configuracion',
                data=xml_data,
                headers={'Content-Type': 'application/xml'}
            )
            resultado = response.json()
            return JsonResponse(resultado)
        except Exception as e:
            return JsonResponse({'error': str(e)})
    
    return render(request, 'configuracion.html')

# Agregar estas funciones al views.py del frontend

def crear_recurso(request):
    if request.method == 'POST':
        import json
        try:
            # Parsear el JSON del request body
            data = json.loads(request.body)
            
            print(f"🎯 CREAR RECURSO - Datos recibidos: {data}")
            
            # Enviar al backend Flask
            response = requests.post(
                f'{settings.BACKEND_URL}/crear/recurso',
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"🎯 CREAR RECURSO - Respuesta backend: {response.status_code}")
            
            return JsonResponse(response.json())
            
        except Exception as e:
            print(f"🎯 CREAR RECURSO - Error: {e}")
            return JsonResponse({'error': str(e)})
    
    return JsonResponse({'error': 'Método no permitido'})

def crear_categoria(request):
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            
            print(f"🎯 CREAR CATEGORIA - Datos recibidos: {data}")
            
            response = requests.post(
                f'{settings.BACKEND_URL}/crear/categoria',
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"🎯 CREAR CATEGORIA - Respuesta backend: {response.status_code}")
            
            return JsonResponse(response.json())
            
        except Exception as e:
            print(f"🎯 CREAR CATEGORIA - Error: {e}")
            return JsonResponse({'error': str(e)})
    
    return JsonResponse({'error': 'Método no permitido'})

def crear_cliente(request):
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            
            print(f"🎯 CREAR CLIENTE - Datos recibidos: {data}")
            
            response = requests.post(
                f'{settings.BACKEND_URL}/crear/cliente',
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"🎯 CREAR CLIENTE - Respuesta backend: {response.status_code}")
            
            return JsonResponse(response.json())
            
        except Exception as e:
            print(f"🎯 CREAR CLIENTE - Error: {e}")
            return JsonResponse({'error': str(e)})
    
    return JsonResponse({'error': 'Método no permitido'})

def consumo(request):
    if request.method == 'POST' and request.FILES.get('archivo_xml'):
        archivo = request.FILES['archivo_xml']
        xml_data = archivo.read().decode('utf-8')
        
        try:
            response = requests.post(
                f'{settings.BACKEND_URL}/consumo',
                data=xml_data,
                headers={'Content-Type': 'application/xml'}
            )
            resultado = response.json()
            return JsonResponse(resultado)
        except Exception as e:
            return JsonResponse({'error': str(e)})
    
    return render(request, 'consumo.html')

def consultar_datos(request):
    tipo = request.GET.get('tipo', 'configuraciones')
    
    try:
        response = requests.get(f'{settings.BACKEND_URL}/consultar/{tipo}')
        print(f"🔍 CONSULTA - Tipo: {tipo}, Status: {response.status_code}")
        print(f"🔍 CONSULTA - Datos: {response.text[:500]}...")  # Primeros 500 chars
        datos = response.json()
        return JsonResponse({'datos': datos})
    except Exception as e:
        print(f"🔍 CONSULTA - Error: {e}")
        return JsonResponse({'error': str(e)})
    
    
def reset_sistema(request):
    if request.method == 'POST':
        try:
            response = requests.post(f'{settings.BACKEND_URL}/reset')
            return JsonResponse(response.json())
        except Exception as e:
            return JsonResponse({'error': str(e)})
    return JsonResponse({'error': 'Método no permitido'})

def facturacion(request):
    if request.method == 'POST':
        # Obtener datos del formulario
        data = json.loads(request.body)
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        print(f"🎯 FRONTEND - Fecha inicio: '{fecha_inicio}', Fecha fin: '{fecha_fin}'")
        
        try:
            response = requests.post(
                f'{settings.BACKEND_URL}/facturacion',
                json={'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin},
                headers={'Content-Type': 'application/json'}
            )
            print(f"🎯 FRONTEND - Respuesta backend: {response.status_code}")
            return JsonResponse(response.json())
        except Exception as e:
            print(f"🎯 FRONTEND - Error: {e}")
            return JsonResponse({'error': str(e)})
    
    return render(request, 'facturacion.html')

def operaciones(request):
    return render(request, 'operaciones.html')

def ayuda(request):
    return render(request, 'ayuda.html')

def reportes(request):
    if request.method == 'POST':
        tipo_reporte = request.POST.get('tipo_reporte')
        
        if tipo_reporte == 'factura':
            numero_factura = request.POST.get('numero_factura')
            response = requests.post(
                f'{settings.BACKEND_URL}/reporte/factura',
                json={'numero_factura': numero_factura}
            )
        elif tipo_reporte == 'ventas':
            tipo_analisis = request.POST.get('tipo_analisis')
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_fin = request.POST.get('fecha_fin')
            response = requests.post(
                f'{settings.BACKEND_URL}/reporte/ventas',
                json={
                    'tipo': tipo_analisis,
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin
                }
            )
        
        return JsonResponse(response.json())
    
    return render(request, 'reportes.html')