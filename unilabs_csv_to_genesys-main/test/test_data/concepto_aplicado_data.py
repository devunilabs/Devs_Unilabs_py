from datetime import datetime

csv_str = """ID_Personal,ID_TipoConcepto,Vigencia,ID_Moneda,Monto,Observaciones
12345,1,01/06/2023,1,100.50,
67890,2,01/07/2023,2,200.75,Concepto especial
24680,3,01/08/2023,1,150.25,
13579,4,01/09/2023,2,175.00,"""

expected_list = [
    {
        'ID_Personal': '12345',
        'ID_TipoConcepto': 1,
        'Vigencia': datetime(2023, 6, 1),
        'ID_Moneda': 1,
        'Monto': 100.50,
        'Observaciones': None,
    },
    {
        'ID_Personal': '67890',
        'ID_TipoConcepto': 2,
        'Vigencia': datetime(2023, 7, 1),
        'ID_Moneda': 2,
        'Monto': 200.75,
        'Observaciones': 'Concepto especial',
    },
    {
        'ID_Personal': '24680',
        'ID_TipoConcepto': 3,
        'Vigencia': datetime(2023, 8, 1),
        'ID_Moneda': 1,
        'Monto': 150.25,
        'Observaciones': None,
    },
    {
        'ID_Personal': '13579',
        'ID_TipoConcepto': 4,
        'Vigencia': datetime(2023, 9, 1),
        'ID_Moneda': 2,
        'Monto': 175.00,
        'Observaciones': None,
    },
]
