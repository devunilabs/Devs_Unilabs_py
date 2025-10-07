from datetime import datetime

csv_str = """ID_Personal,ID_TipoFileDatoExtra,Fecha,ID_Moneda,Importe,Observaciones,ID_PlanillaConf
12345,1,01/06/2023,1,100.50,,
67890,2,01/07/2023,2,200.75,Dato especial,1234
24680,3,01/08/2023,1,150.25,,5678
13579,4,01/09/2023,2,175.00,,"""

expected_list = [
    {
        'ID_Personal': '12345',
        'ID_TipoFileDatoExtra': 1,
        'Fecha': datetime(2023, 6, 1),
        'ID_Moneda': 1,
        'Importe': 100.50,
        'Observaciones': None,
        'ID_PlanillaConf': None,
    },
    {
        'ID_Personal': '67890',
        'ID_TipoFileDatoExtra': 2,
        'Fecha': datetime(2023, 7, 1),
        'ID_Moneda': 2,
        'Importe': 200.75,
        'Observaciones': 'Dato especial',
        'ID_PlanillaConf': 1234,
    },
    {
        'ID_Personal': '24680',
        'ID_TipoFileDatoExtra': 3,
        'Fecha': datetime(2023, 8, 1),
        'ID_Moneda': 1,
        'Importe': 150.25,
        'Observaciones': None,
        'ID_PlanillaConf': 5678,
    },
    {
        'ID_Personal': '13579',
        'ID_TipoFileDatoExtra': 4,
        'Fecha': datetime(2023, 9, 1),
        'ID_Moneda': 2,
        'Importe': 175.00,
        'Observaciones': None,
        'ID_PlanillaConf': None,
    },
]
