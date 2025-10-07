csv_str = """Codigo,RazonSocial,NombreComercial,TipoDocumento,NroDocumento
001372731,Nombre,Apellido Prueba,4,001372731"""

expected_list = [
    {
        'Codigo': '001372731',
        'RazonSocial': 'Nombre',
        'NombreComercial': 'Apellido Prueba',
        'TipoDocumento': 4,
        'NroDocumento': '001372731'
    }
]