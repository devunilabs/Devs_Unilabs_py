def valid(obj):
    complete = False
    row = [obj['name'], obj['first_surname'], obj['last_surname'], obj['gender'], obj['date_birth'],  obj['document']]
    count_fields = 6
    if (obj['document_type'] == 'ce') or (obj['document_type'] == 'passport') or (obj['document_type'] == 'rn'):
        row = [obj['name'], obj['first_surname'], obj['gender'], obj['date_birth'], obj['document']]
        count_fields = 5

    if (obj['document_type'] == 'ot'):
        row = [obj['name'], obj['first_surname'], obj['gender'], obj['date_birth'], obj['document']]
        count_fields = 5

    if len([x for x in row if x]) == count_fields:
        complete = True
    return complete

