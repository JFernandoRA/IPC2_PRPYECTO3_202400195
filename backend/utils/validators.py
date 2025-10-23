import re
from datetime import datetime

def validar_nit(nit):
    patron = r'^\d+-[0-9Kk]$'
    return bool(re.match(patron, nit))

def extraer_fecha(texto):
    patron = r'(\d{2}/\d{2}/\d{4})'
    match = re.search(patron, texto)
    if match:
        return match.group(1)
    return texto

def extraer_fecha_hora(texto):
    patron = r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2})'
    match = re.search(patron, texto)
    if match:
        return match.group(1)
    return texto
