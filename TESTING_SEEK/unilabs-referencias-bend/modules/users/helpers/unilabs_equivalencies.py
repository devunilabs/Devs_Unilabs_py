def _select_document_type(value):
    response = ''
    if value == 'Dni':
        response = 1
    elif value == 'Carnet extranjeria':
        response = 2
    elif value == 'Pasaporte':
        response = 3
    return response

def _type_user(value):
    response = 1
    if value == 'Referencia':
        response = 1
    elif value == 'Unilabs':
        response = 2
    return response

def _set_gender(value):
    response = 'M'
    if value == 'Masculino':
        response = 'H'
    return response


