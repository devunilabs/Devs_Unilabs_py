# Prompts to generate some code

## Generate Pydantic models

I'm going to provide a CSV data that represents a table in a database.
The table name is: PersonaNatural.

The first column (COLUMN_NAME) indicates the name of the column.
The second column (IS_NULLABLE) indicates if the column is required.
The third column (DATA_TYPE) indicates the type of the column.

With that information create a Python class that inherits from the Pydantic
BaseModel class, that represents the entity based on the table.

Consider the use of the snake case convention for the attributes.
For instance, "DomicilioTipoVia" must be converted to "domicilio_tipo_via".

Provide a Python function that:

- Generate a CSV data with 4 records that correspond with the entity, keeping the names from the original table.
- Generate a python list of objects, with 4 records, as expected data from the pydantic entity.
- Calls the function csv_load, passing the model, the csv data and the expected data:

```python
def test_persona_natural_from_csv():
    # The CSV data should follow, for instance, this format:
    csv_data_persona_natural = """Nombre1,Nombre2,ApellidoPaterno,ApellidoMaterno,DNI,RUC
Alejandro,,Benavides,Samame,0123456789,"""

    # The Python list should follow this example format:
    expected_persona_natural_data = [
        {
            'nombre1': 'Alenajdro',
            'nombre2': None,
            'apellido_paterno': 'Benavides',    
            'apellido_materno': 'Samame',    
            'dni': '0123456789',
            'ruc': None,
        },
        ...
    ]

    # Calls the csv_load function
    csv_load(PersonaNatural, csv_data=csv_data_persona_natural, expected_data=expected_persona_natural_data)
```
This is the input CSV data:
```csv
COLUMN_NAME,IS_NULLABLE,DATA_TYPE
Nombre1,NO,varchar
Nombre2,YES,varchar
ApellidoPaterno,NO,varchar
ApellidoMaterno,NO,varchar
DNI,NO,varchar
RUC,YES,varchar
```

