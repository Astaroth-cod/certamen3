"""
setup_db.py – Poblar la base de datos prueba3 con los JSON de la evaluación.
Ejecutar UNA vez antes de usar gestor_eventos.py
"""

import json
from pymongo import MongoClient

def cargar_datos():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["certamen3"]


    db.invitados.drop()
    db.eventos.drop()


    with open("invitados.json", "r", encoding="utf-8") as f:
        invitados = json.load(f)
    db.invitados.insert_many(invitados)
    print(f"  ✔  Invitados insertados: {len(invitados)}")

    with open("eventos.json", "r", encoding="utf-8") as f:
        eventos = json.load(f)
    db.eventos.insert_many(eventos)
    print(f"  ✔  Eventos insertados  : {len(eventos)}")


    db.invitados.create_index("rut", unique=True)
    db.eventos.create_index("codigo", unique=True)
    db.eventos.create_index("invitados.rut")
    print("  ✔  Índices creados")

    print("\n  Base de datos 'prueba3' lista.")
    client.close()

if __name__ == "__main__":
    print("\n  Cargando datos en MongoDB...\n")
    cargar_datos()