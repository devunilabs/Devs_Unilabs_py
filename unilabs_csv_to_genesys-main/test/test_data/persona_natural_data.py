csv_str = """Nombre1,Nombre2,ApellidoPaterno,ApellidoMaterno,DNI,RUC
Alejandro,,Benavides,Samame,10109403,
María,Elizabeth,Rodríguez,López,87654321,20123456789
Pedro,,García,Martínez,98765432,
Juan,Carlos,Pérez,González,12345678,"""

expected_list = [
    {
        'Nombre1': 'Alejandro',
        'Nombre2': None,
        'ApellidoPaterno': 'Benavides',
        'ApellidoMaterno': 'Samame',
        'DNI': '10109403',
        'RUC': None,
    },
    {
        'Nombre1': 'María',
        'Nombre2': 'Elizabeth',
        'ApellidoPaterno': 'Rodríguez',
        'ApellidoMaterno': 'López',
        'DNI': '87654321',
        'RUC': '20123456789',
    },
    {
        'Nombre1': 'Pedro',
        'Nombre2': None,
        'ApellidoPaterno': 'García',
        'ApellidoMaterno': 'Martínez',
        'DNI': '98765432',
        'RUC': None,
    },
    {
        'Nombre1': 'Juan',
        'Nombre2': 'Carlos',
        'ApellidoPaterno': 'Pérez',
        'ApellidoMaterno': 'González',
        'DNI': '12345678',
        'RUC': None,
    },
]
