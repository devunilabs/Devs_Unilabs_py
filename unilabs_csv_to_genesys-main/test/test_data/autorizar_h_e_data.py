from datetime import datetime

csv_str = """ID_Personal,Fecha,HoraInicio,HoraTermino,HorasExtras_Autorizadas
12345,01/05/2023,8.5,17.5,9
67890,02/05/2023,9.0,18.0,9
24680,03/05/2023,7.5,16.5,9
13579,04/05/2023,10.0,19.0,9"""

expected_list = [
    {
        'ID_Personal': '12345',
        'Fecha': datetime(2023, 5, 1),
        'HoraInicio': 8.5,
        'HoraTermino': 17.5,
        'HorasExtras_Autorizadas': 9.0,
    },
    {
        'ID_Personal': '67890',
        'Fecha': datetime(2023, 5, 2),
        'HoraInicio': 9.0,
        'HoraTermino': 18.0,
        'HorasExtras_Autorizadas': 9.0,
    },
    {
        'ID_Personal': '24680',
        'Fecha': datetime(2023, 5, 3),
        'HoraInicio': 7.5,
        'HoraTermino': 16.5,
        'HorasExtras_Autorizadas': 9.0,
    },
    {
        'ID_Personal': '13579',
        'Fecha': datetime(2023, 5, 4),
        'HoraInicio': 10.0,
        'HoraTermino': 19.0,
        'HorasExtras_Autorizadas': 9.0,
    },
]
