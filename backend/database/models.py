class Recurso:
    def __init__(self, id_recurso, nombre, abreviatura, metrica, tipo, valor_x_hora):
        self.id_recurso = id_recurso
        self.nombre = nombre
        self.abreviatura = abreviatura
        self.metrica = metrica
        self.tipo = tipo
        self.valor_x_hora = float(valor_x_hora)

class Configuracion:
    def __init__(self, id_configuracion, nombre, descripcion, recursos):
        self.id_configuracion = id_configuracion
        self.nombre = nombre
        self.descripcion = descripcion
        self.recursos = recursos

class Categoria:
    def __init__(self, id_categoria, nombre, descripcion, carga_trabajo, configuraciones):
        self.id_categoria = id_categoria
        self.nombre = nombre
        self.descripcion = descripcion
        self.carga_trabajo = carga_trabajo
        self.configuraciones = configuraciones

class Cliente:
    def __init__(self, nit, nombre, usuario, clave, direccion, correo, instancias=None):
        self.nit = nit
        self.nombre = nombre
        self.usuario = usuario
        self.clave = clave
        self.direccion = direccion
        self.correo = correo
        self.instancias = instancias if instancias is not None else []

class Instancia:
    def __init__(self, id_instancia, id_configuracion, nombre, fecha_inicio, estado, fecha_final=None):
        self.id_instancia = id_instancia
        self.id_configuracion = id_configuracion
        self.nombre = nombre
        self.fecha_inicio = fecha_inicio
        self.estado = estado
        self.fecha_final = fecha_final
        self.consumos = []

class Consumo:
    def __init__(self, nit_cliente, id_instancia, tiempo, fecha_hora):
        self.nit_cliente = nit_cliente
        self.id_instancia = id_instancia
        self.tiempo = float(tiempo)
        self.fecha_hora = fecha_hora

class Factura:
    def __init__(self, numero_factura, nit_cliente, fecha_factura, monto_total, detalles):
        self.numero_factura = numero_factura
        self.nit_cliente = nit_cliente
        self.fecha_factura = fecha_factura
        self.monto_total = monto_total
        self.detalles = detalles 
