import json
from datetime import date

def json_fuller(str_json: str):
    data = json.loads(str_json)
    if data["establecimiento"] == "":
        print("Falta establecimiento")
    if data["importe"] == "":
        print("Falta importe")
    if data["descripcion"] == "":
        print("Falta descripcion")
    if data["categoria"] == "":
        print("Falta categoria")
    data["fecha"] = date.today().isoformat()
    return json.dumps(data)

def json_formatter(str_json: str):
     data = json.loads(str_json)
     salida = f"""
    🧾 **REVISIÓN DE GASTO** 🧾

    👕 **Establecimiento:** {data["establecimiento"]}
    💶 **Importe:** {data["importe"]}
    📝 **Descripción:** {data["descripcion"]}
    📅 **Fecha:** {data["fecha"]}
    🏷️ **Categoría:** {data["categoria"]}
    """
     return salida

def to_list(str_json: str):
    data = json.loads(str_json)
    return [data["establecimiento"], data["importe"], data["descripcion"], data["fecha"], data["categoria"]]