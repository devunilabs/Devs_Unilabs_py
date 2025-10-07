from datetime import datetime

csv_str = """ID_Personal,Fecha,ID_TipoFalta,Descripcion,Estado,Condicion,Cantidad_Horas,Observaciones
09330594,09/02/2024,4,,1,0,.5
43090510,30/01/2024,1,,1,1,1
43090510,02/01/2024,1,,1,1,1
09993871,16/01/2024,1,,1,1,1
09993871,31/01/2024,1,,1,1,1
42860009,23/01/2024,1,,1,1,1
47428300,18/01/2024,1,,1,1,1
47428300,05/02/2024,1,,1,1,1,Ejemplo de observaciones
"""

expected_list = [
    {
        "ID_Personal": '09330594',
        "Fecha": datetime(2024, 2, 9),
        "ID_TipoFalta": 4,
        "Descripcion": None,
        "Estado": 1,
        "Condicion": 0,
        "Cantidad_Horas": .5,
        "Observaciones": None
    },
    {
        "ID_Personal": '43090510',
        "Fecha": datetime(2024, 1, 30),
        "ID_TipoFalta": 1,
        "Descripcion": None,
        "Estado": 1,
        "Condicion": 1,
        "Cantidad_Horas": 1,
        "Observaciones": None
    },
    {
        "ID_Personal": '43090510',
        "Fecha": datetime(2024, 1, 2),
        "ID_TipoFalta": 1,
        "Descripcion": None,
        "Estado": 1,
        "Condicion": 1,
        "Cantidad_Horas": 1,
        "Observaciones": None
    },
    {
        "ID_Personal": '09993871',
        "Fecha": datetime(2024, 1, 16),
        "ID_TipoFalta": 1,
        "Descripcion": None,
        "Estado": 1,
        "Condicion": 1,
        "Cantidad_Horas": 1,
        "Observaciones": None
    },
    {
        "ID_Personal": '09993871',
        "Fecha": datetime(2024, 1, 31),
        "ID_TipoFalta": 1,
        "Descripcion": None,
        "Estado": 1,
        "Condicion": 1,
        "Cantidad_Horas": 1,
        "Observaciones": None
    },
    {
        "ID_Personal": '42860009',
        "Fecha": datetime(2024, 1, 23),
        "ID_TipoFalta": 1,
        "Descripcion": None,
        "Estado": 1,
        "Condicion": 1,
        "Cantidad_Horas": 1,
        "Observaciones": None
    },
    {
        "ID_Personal": '47428300',
        "Fecha": datetime(2024, 1, 18),
        "ID_TipoFalta": 1,
        "Descripcion": None,
        "Estado": 1,
        "Condicion": 1,
        "Cantidad_Horas": 1,
        "Observaciones": None
    },
    {
        "ID_Personal": '47428300',
        "Fecha": datetime(2024, 2, 5),
        "ID_TipoFalta": 1,
        "Descripcion": None,
        "Estado": 1,
        "Condicion": 1,
        "Cantidad_Horas": 1,
        "Observaciones": 'Ejemplo de observaciones'
    },
]
