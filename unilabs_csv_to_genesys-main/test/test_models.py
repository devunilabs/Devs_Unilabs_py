import csv
import pytest
from typing import Type

from pydantic import ValidationError

from models import (Falta, Vacacion, Personal, PersonaNatural, BaseCSVModel, AutorizarHE, ConceptoAplicado, DatoExtra,
                    Licencia, SujetoNoDomiciliado)

from test_data import (autorizar_h_e_data, falta_data, vacacion_data, personal_data, persona_natural_data,
                       concepto_aplicado_data, dato_extra_data, licencia_data, sujeto_no_domiciliado_data)


class TestData:
    """Helper class to load test data from files."""

    @staticmethod
    def load_csv_data(file_path):
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            return [row for row in reader]


def csv_load(model: Type[BaseCSVModel], data: str):
    """
    Utility function to load data into model instances from CSV data.

    Args:
        model (Type[BaseCSVModel]): The model class to instantiate.
        data (str): CSV format string with the data.

    Returns:
        list[BaseCSVModel]: The list of instantiated model objects.
    """
    try:
        model_data_list = [model.from_csv_row(line) for line in data.splitlines()[1:]]
    except ValidationError as e:
        pytest.fail(f"Error al parsear los datos CSV: {e}")

    return model_data_list


def assert_model_instances(actual: list[BaseCSVModel], expected: list[dict]):
    """
    Helper function to assert that the actual model instances match the expected data.

    Args:
        actual (list[BaseCSVModel]): The list of actual model instances.
        expected (list[dict]): The list of expected data dictionaries.
    """
    assert len(actual) == len(expected)

    for actual_instance, expected_data in zip(actual, expected):
        for field, expected_value in expected_data.items():
            actual_value = getattr(actual_instance, field)
            assert actual_value == expected_value, (
                f"El campo '{field}' no coincide con el valor esperado: "
                f"{actual_value=} - {expected_value=}"
            )


class TestAutorizarHE:
    """Test cases for the AutorizarHE model."""

    def test_autorizar_h_e_from_csv_data(self):
        actual = csv_load(AutorizarHE, autorizar_h_e_data.csv_str)
        assert_model_instances(actual, autorizar_h_e_data.expected_list)


class TestConceptoAplicado:
    """Test cases for the ConceptoAplicado model."""

    def test_concepto_aplicado_from_csv_data(self):
        actual = csv_load(ConceptoAplicado, concepto_aplicado_data.csv_str)
        assert_model_instances(actual, concepto_aplicado_data.expected_list)


class TestDatoExtra:
    """Test cases for the DatoExtra model."""

    def test_dato_extra_from_csv_data(self):
        actual = csv_load(DatoExtra, dato_extra_data.csv_str)
        assert_model_instances(actual, dato_extra_data.expected_list)


class TestFalta:
    """Test cases for the Falta model."""

    def test_falta_from_csv_data(self):
        actual = csv_load(Falta, falta_data.csv_str)
        assert_model_instances(actual, falta_data.expected_list)


class TestLicencia:
    """Test cases for the Licencia model."""

    def test_licencia_from_csv_data(self):
        actual = csv_load(Licencia, licencia_data.csv_str)
        assert_model_instances(actual, licencia_data.expected_list)


class TestPersonaNatural:
    """Test cases for the PersonaNatural model."""

    def test_persona_natural_from_csv_data(self):
        actual = csv_load(PersonaNatural, persona_natural_data.csv_str)
        assert_model_instances(actual, persona_natural_data.expected_list)


class TestPersonal:
    """Test cases for the Personal model."""

    def test_personal_from_csv_data(self):
        actual = csv_load(Personal, personal_data.csv_str)
        assert_model_instances(actual, personal_data.expected_list)


class TestSujetoNoDomiciliado:
    """Test cases for the SujetoNoDomiciliado model."""
    def test_sujeto_no_domiciliado_from_csv_data(self):
        actual = csv_load(SujetoNoDomiciliado, sujeto_no_domiciliado_data.csv_str)
        assert_model_instances(actual, sujeto_no_domiciliado_data.expected_list)


class TestVacacion:
    """Test cases for the Personal model."""

    def test_vacacion_from_csv_data(self):
        actual = csv_load(Vacacion, vacacion_data.csv_str)
        assert_model_instances(actual, vacacion_data.expected_list)
