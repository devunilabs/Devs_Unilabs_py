from datetime import datetime

csv_str = """ID_Personal,Fecha,Cantidad_Horas,PeriodoAño,Observaciones
40770860,04/03/2024,0,2024,"""

expected_list = [
    {
        'ID_Personal': '40770860',
        'Fecha': datetime(2024, 3, 4),
        'Cantidad_Horas': 0,
        'PeriodoAño': 2024,
        'Observaciones': None
    }
]
