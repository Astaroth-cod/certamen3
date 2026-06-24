import json
import re
from datetime import datetime
from pymongo import MongoClient

def conectar():
    try:
        client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMs=3000)
        client.server_info()
        # Unificamos el nombre de la base de datos a "certamen3"
        db = client["certamen3"]
        return db
    except Exception as e:
        print(f"\n[Error] No se pudo conectar a Mongo :c: {e}")
        exit(1)

# ==========================================
# FUNCIÓN DE CONFIGURACIÓN (Ex setup.py)
# ==========================================
def cargar_datos(db):
    print("\n  Cargando datos en MongoDB...")
    
    # Limpiamos las colecciones antes de cargar
    db.invitados.drop()
    db.eventos.drop()

    try:
        with open("invitados.json", "r", encoding="utf-8") as f:
            invitados = json.load(f)
        db.invitados.insert_many(invitados)
        print(f"  ✔  Invitados insertados: {len(invitados)}")

        with open("eventos.json", "r", encoding="utf-8") as f:
            eventos = json.load(f)
        db.eventos.insert_many(eventos)
        print(f"  ✔  Eventos insertados  : {len(eventos)}")

        # Creación de índices
        db.invitados.create_index("rut", unique=True)
        db.eventos.create_index("codigo", unique=True)
        db.eventos.create_index("invitados.rut")
        print("  ✔  Índices creados")

        print("\n  Base de datos 'certamen3' lista y cargada exitosamente.")
    except FileNotFoundError as e:
        print(f"\n  [Error] No se encontró el archivo JSON: {e}")
    except Exception as e:
        print(f"\n  [Error] Ocurrió un problema al cargar los datos: {e}")
    pausar()


# ==========================================
# UTILIDADES Y MENÚS (Ex gestor_evento.py)
# ==========================================
def separar(titulo=""):
    ancho = 60
    if titulo:
        print(f"\n{'-'*ancho}")
        print(f" {titulo.upper()}")
        print(f"{'-'* ancho}")
    else:
        print(f"{'-'* ancho}")

def cabeza():
    print("\n"+"="*60)
    print(" SISTEMA DE EVENTOS E INVITADOS")
    print(" T13032 ' Base de datos no estructuradas :0")
    print("=" * 60)

def pausar():
    input("\n Presiona Enter para continuar....")

# ACTIVIDAD PARTE 1
def act1_lista(db):
    separar("actividad 1 todos los eventos")
    eventos = db.eventos.find({}, {"codigo":1,"nombre":1,"fecha":1,"lugar":1,"categoria":1,"_id":0}).sort("fecha",1)
    total = 0
    for ev in eventos:
        fecha_str = ev["fecha"].strftime("%d/%m/%Y %H:%M") if isinstance(ev["fecha"], datetime) else str(ev["fecha"])
        print(f"\n  Código   : {ev['codigo']}")
        print(f"  Nombre   : {ev['nombre']}")
        print(f"  Fecha    : {fecha_str}")
        print(f"  Lugar    : {ev['lugar']}")
        print(f"  Categoría: {ev['categoria']}")
        separar()
        total += 1
    print(f"\n  Total de eventos: {total}")
    pausar()

def act1_eventos_por_categoria(db):
    separar("Actividad 2 · Filtrar por categoría")
    categorias = db.eventos.distinct("categoria")
    print(f"\n  Categorías disponibles: {', '.join(categorias)}")
    cat = input("\n  Ingresa categoría a buscar: ").strip().lower()
    eventos = db.eventos.find({"categoria": cat}, {"codigo": 1, "nombre": 1, "fecha": 1, "lugar": 1, "_id": 0})
    total = 0
    for ev in eventos:
        fecha_str = ev["fecha"].strftime("%d/%m/%Y %H:%M") if isinstance(ev["fecha"], datetime) else str(ev["fecha"])
        print(f"\n  [{ev['codigo']}] {ev['nombre']}")
        print(f"  Fecha : {fecha_str}  |  Lugar: {ev['lugar']}")
        total += 1
    if total == 0:
        print(f"\n  No se encontraron eventos con categoría '{cat}'.")
    else:
        print(f"\n  Total encontrados: {total}")
    pausar()

def act1_invitados_por_estado(db):
    separar("Actividad 3 · Invitados por estado")
    estado = input("\n  Estado a filtrar (activo / bloqueado): ").strip().lower()
    invitados = db.invitados.find({"estado": estado}, {"rut": 1, "nombre": 1, "correo": 1, "empresa": 1, "_id": 0}).sort("nombre", 1)
    total = 0
    for inv in invitados:
        print(f"\n  {inv['nombre']}  ({inv['rut']})")
        print(f"  Correo : {inv['correo']}")
        print(f"  Empresa: {inv['empresa']}")
        total += 1
    if total == 0:
        print(f"\n  No se encontraron invitados con estado '{estado}'.")
    else:
        print(f"\n  Total encontrados: {total}")
    pausar()  

# ACTIVIDAD PARTE 2
def act2_buscar_por_nombre(db):
    separar("Actividad 2.1 · Buscar invitado por nombre")
    termino = input("\n  Ingresa parte del nombre a buscar: ").strip()
    patron = re.compile(termino, re.IGNORECASE)
    invitados = db.invitados.find({"nombre": {"$regex": patron}}, {"rut": 1, "nombre": 1, "correo": 1, "empresa": 1, "estado": 1, "_id": 0})
    total = 0
    for inv in invitados:
        print(f"\n  {inv['nombre']}  ({inv['rut']})  [{inv['estado'].upper()}]")
        print(f"  Correo : {inv['correo']}")
        print(f"  Empresa: {inv['empresa']}")
        total += 1
    if total == 0:
        print(f"\n  No se encontraron resultados para '{termino}'.")
    else:
        print(f"\n  Total encontrados: {total}")
    pausar()
 
def act2_buscar_por_dominio_correo(db):
    separar("Actividad 2.2 · Buscar por dominio de correo")
    dominio = input("\n  Ingresa el dominio (ej: inacap.cl, empresa.cl): ").strip()
    patron = re.compile(f"@{re.escape(dominio)}$", re.IGNORECASE)
    invitados = db.invitados.find({"correo": {"$regex": patron}}, {"rut": 1, "nombre": 1, "correo": 1, "empresa": 1, "_id": 0})
    total = 0
    for inv in invitados:
        print(f"\n  {inv['nombre']}  ({inv['rut']})")
        print(f"  Correo : {inv['correo']}")
        print(f"  Empresa: {inv['empresa']}")
        total += 1
    if total == 0:
        print(f"\n  No se encontraron invitados con dominio '@{dominio}'.")
    else:
        print(f"\n  Total encontrados: {total}")
    pausar()
 
def act2_buscar_evento_por_nombre(db):
    separar("Actividad 2.3 · Buscar evento por nombre parcial")
    termino = input("\n  Ingresa parte del nombre del evento: ").strip()
    patron = re.compile(termino, re.IGNORECASE)
    eventos = db.eventos.find({"nombre": {"$regex": patron}}, {"codigo": 1, "nombre": 1, "fecha": 1, "lugar": 1, "categoria": 1, "_id": 0})
    total = 0
    for ev in eventos:
        fecha_str = ev["fecha"].strftime("%d/%m/%Y %H:%M") if isinstance(ev["fecha"], datetime) else str(ev["fecha"])
        print(f"\n  [{ev['codigo']}] {ev['nombre']}")
        print(f"  Fecha : {fecha_str}  |  Lugar: {ev['lugar']}  |  Categoría: {ev['categoria']}")
        total += 1
    if total == 0:
        print(f"\n  No se encontraron eventos con '{termino}' en el nombre.")
    else:
        print(f"\n  Total encontrados: {total}")
    pausar()
 
# ACTIVIDAD PARTE 3
def act3_verificar_acceso(db):
    separar("Actividad 3.1 · Validar acceso de invitado a evento")
    rut = input("\n  RUT del invitado (ej: 11.118.512-6): ").strip()
    cod = input("  Código del evento  (ej: EVT-2025-001): ").strip().upper()
    evento = db.eventos.find_one({"codigo": cod, "invitados": {"$elemMatch": {"rut": rut, "estado": "confirmado"}}}, {"codigo": 1, "nombre": 1, "_id": 0})
    invitado = db.invitados.find_one({"rut": rut, "estado": "activo"}, {"nombre": 1, "empresa": 1, "_id": 0})
    print()
    if evento and invitado:
        print(f"  ✔  ACCESO PERMITIDO")
        print(f"     Invitado : {invitado['nombre']} ({invitado['empresa']})")
        print(f"     Evento   : {evento['nombre']} ({evento['codigo']})")
        print(f"     Estado   : Confirmado y cuenta activa")
    elif not evento:
        print(f"  ✘  ACCESO DENEGADO: invitado no confirmado en este evento")
        inv_existe = db.invitados.find_one({"rut": rut}, {"nombre": 1, "_id": 0})
        if inv_existe:
            print(f"     Invitado encontrado: {inv_existe['nombre']}")
        else:
            print(f"     El RUT ingresado no existe en el sistema.")
    elif not invitado:
        print(f"  ✘  ACCESO DENEGADO: cuenta del invitado bloqueada o no existe")
        ev_existe = db.eventos.find_one({"codigo": cod}, {"nombre": 1, "_id": 0})
        if ev_existe:
            print(f"     Evento: {ev_existe['nombre']}")
    pausar()
 
def act3_invitados_confirmados_en_evento(db):
    separar("Actividad 3.2 · Invitados confirmados en un evento")
    cod = input("\n  Código del evento (ej: EVT-2025-001): ").strip().upper()
    evento = db.eventos.find_one({"codigo": cod}, {"nombre": 1, "invitados": 1, "_id": 0})
    if not evento:
        print(f"\n  Evento '{cod}' no encontrado.")
        pausar()
        return
    print(f"\n  Evento: {evento['nombre']}")
    confirmados = [i for i in evento.get("invitados", []) if i["estado"] == "confirmado"]
    if not confirmados:
        print("  No hay invitados confirmados en este evento.")
        pausar()
        return
    print(f"  Invitados confirmados ({len(confirmados)}):\n")
    for conf in confirmados:
        inv = db.invitados.find_one({"rut": conf["rut"]}, {"nombre": 1, "empresa": 1, "_id": 0})
        if inv:
            print(f"  • {inv['nombre']} ({conf['rut']})  –  {inv['empresa']}")
        else:
            print(f"  • {conf['rut']}  (sin datos adicionales)")
    pausar()
 
# ACTIVIDAD 4 – $LOOKUP Y AGREGACIONES
def act4_top3_eventos_confirmados(db):
    separar("Actividad 4.1 · Top 3 eventos con más confirmados")
    pipeline = [
        {"$unwind": "$invitados"},
        {"$match": {"invitados.estado": "confirmado"}},
        {"$group": {
            "_id": "$codigo",
            "nombre": {"$first": "$nombre"},
            "lugar": {"$first": "$lugar"},
            "categoria": {"$first": "$categoria"},
            "total_confirmados": {"$sum": 1}
        }},
        {"$sort": {"total_confirmados": -1}},
        {"$limit": 3}
    ]
    resultados = list(db.eventos.aggregate(pipeline))
    if not resultados:
        print("\n  No hay datos disponibles.")
        pausar()
        return
    print()
    for i, ev in enumerate(resultados, 1):
        print(f"  #{i}  {ev['nombre']}  ({ev['_id']})")
        print(f"       Lugar    : {ev['lugar']}")
        print(f"       Categoría: {ev['categoria']}")
        print(f"       Confirmados: {ev['total_confirmados']}\n")
    pausar()
 
def act4_lookup_evento_con_invitados(db):
    separar("Actividad 4 · $lookup – Evento con detalle de invitados")
    cod = input("\n  Código del evento (ej: EVT-2025-001): ").strip().upper()
    pipeline = [
        {"$match": {"codigo": cod}},
        {"$unwind": "$invitados"},
        {"$lookup": {
            "from": "invitados",
            "localField": "invitados.rut",
            "foreignField": "rut",
            "as": "detalle_invitado"
        }},
        {"$unwind": "$detalle_invitado"},
        {"$project": {
            "_id": 0,
            "evento_codigo": "$codigo",
            "evento_nombre": "$nombre",
            "lugar": "$lugar",
            "estado_evento": "$invitados.estado",
            "checkin": "$invitados.checkin",
            "rut": "$invitados.rut",
            "nombre_invitado": "$detalle_invitado.nombre",
            "empresa": "$detalle_invitado.empresa",
            "correo": "$detalle_invitado.correo",
            "estado_cuenta": "$detalle_invitado.estado"
        }},
        {"$sort": {"estado_evento": 1, "nombre_invitado": 1}}
    ]
    resultados = list(db.eventos.aggregate(pipeline))
    if not resultados:
        print(f"\n  No se encontró el evento '{cod}'.")
        pausar()
        return
    primer = resultados[0]
    print(f"\n  Evento : {primer['evento_nombre']} ({primer['evento_codigo']})")
    print(f"  Lugar  : {primer['lugar']}")
    print(f"  Total invitados: {len(resultados)}\n")
    estado_actual = None
    for reg in resultados:
        if reg["estado_evento"] != estado_actual:
            estado_actual = reg["estado_evento"]
            print(f"\n  ── Estado: {estado_actual.upper()} ──")
        cuenta_icon = "✔" if reg["estado_cuenta"] == "activo" else "✘"
        checkin_icon = "★" if reg["checkin"] else "·"
        print(f"  {checkin_icon} {cuenta_icon}  {reg['nombre_invitado']:<25} {reg['empresa']:<15}  {reg['correo']}")
    print(f"\n  Leyenda: ★ Check-in realizado  |  ✔ Cuenta activa  |  ✘ Bloqueado")
    pausar()
 
def act4_resumen_estadistico(db):
    separar("Actividad 4.3 · Resumen estadístico por evento")
    pipeline = [
        {"$unwind": "$invitados"},
        {"$group": {
            "_id": {
                "codigo": "$codigo",
                "nombre": "$nombre",
                "estado": "$invitados.estado"
            },
            "cantidad": {"$sum": 1}
        }},
        {"$group": {
            "_id": {
                "codigo": "$_id.codigo",
                "nombre": "$_id.nombre"
            },
            "estados": {
                "$push": {
                    "estado": "$_id.estado",
                    "cantidad": "$cantidad"
                }
            },
            "total": {"$sum": "$cantidad"}
        }},
        {"$sort": {"_id.codigo": 1}}
    ]
    resultados = list(db.eventos.aggregate(pipeline))
    print()
    for ev in resultados:
        cod = ev["_id"]["codigo"]
        nom = ev["_id"]["nombre"]
        estados = {e["estado"]: e["cantidad"] for e in ev["estados"]}
        conf = estados.get("confirmado", 0)
        pend = estados.get("pendiente", 0)
        rech = estados.get("rechazado", 0)
        print(f"  {cod}  |  {nom}")
        print(f"    Confirmados: {conf:>2}  |  Pendientes: {pend:>2}  |  Rechazados: {rech:>2}  |  Total: {ev['total']}\n")
    pausar()
 
# SUBMENÚS
def menu1(db):
    while True:
        cabeza()
        print("\n  ACTIVIDAD 1 · Filtros y Condiciones\n")
        print("  [1] Listar todos los eventos")
        print("  [2] Filtrar eventos por categoría")
        print("  [3] Filtrar invitados por estado (activo/bloqueado)")
        print("  [0] Volver")
        op = input("\n  Selecciona: ").strip()
        if op == "1": act1_lista(db)
        elif op == "2": act1_eventos_por_categoria(db)
        elif op == "3": act1_invitados_por_estado(db)
        elif op == "0": break
        else: print("  Opción inválida.")
 
def menu2(db):
    while True:
        cabeza()
        print("\n  ACTIVIDAD 2 · Expresiones Regulares (Regex)\n")
        print("  [1] Buscar invitado por nombre parcial")
        print("  [2] Buscar invitados por dominio de correo")
        print("  [3] Buscar evento por nombre parcial")
        print("  [0] Volver")
        op = input("\n  Selecciona: ").strip()
        if op == "1": act2_buscar_por_nombre(db)
        elif op == "2": act2_buscar_por_dominio_correo(db)
        elif op == "3": act2_buscar_evento_por_nombre(db)
        elif op == "0": break
        else: print("  Opción inválida.")
 
def menu3(db):
    while True:
        cabeza()
        print("\n  ACTIVIDAD 3 · Búsquedas en Subdocumentos\n")
        print("  [1] Validar acceso de un invitado a un evento")
        print("  [2] Listar invitados confirmados en un evento")
        print("  [0] Volver")
        op = input("\n  Selecciona: ").strip()
        if op == "1": act3_verificar_acceso(db)
        elif op == "2": act3_invitados_confirmados_en_evento(db)
        elif op == "0": break
        else: print("  Opción inválida.")
 
def menu4(db):
    while True:
        cabeza()
        print("\n  ACTIVIDAD 4 · $lookup y Agregaciones\n")
        print("  [1] Top 3 eventos con más invitados confirmados")
        print("  [2] Detalle de evento cruzado con invitados ($lookup)")
        print("  [3] Resumen estadístico por evento")
        print("  [0] Volver")
        op = input("\n  Selecciona: ").strip()
        if op == "1": act4_top3_eventos_confirmados(db)
        elif op == "2": act4_lookup_evento_con_invitados(db)
        elif op == "3": act4_resumen_estadistico(db)
        elif op == "0": break
        else: print("  Opción inválida.")
 
# MENÚ PRINCIPAL
def menu_principal(db):
    while True:
        cabeza()
        print("\n  MENÚ PRINCIPAL\n")
        print("  [1] Filtros y Condiciones")
        print("  [2] Expresiones Regulares")
        print("  [3] Búsquedas en Subdocumentos")
        print("  [4] lookup y Agregaciones")
        print("  [5] Cargar/Resetear datos de prueba")
        print("  [0] Salir")
        op = input("\n  Selecciona: ").strip()
        if op == "1": menu1(db)
        elif op == "2": menu2(db)
        elif op == "3": menu3(db)
        elif op == "4": menu4(db)
        elif op == "5": cargar_datos(db)
        elif op == "0":
            print("\n  Adiós \n")
            break
        else:
            print("  Opción inválida.")
 
if __name__ == "__main__":
    db = conectar()
    print("\n  Conexión a MongoDB establecida correctamente.")
    menu_principal(db)