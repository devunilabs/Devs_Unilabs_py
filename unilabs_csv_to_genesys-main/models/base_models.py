from abc import ABC
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Integer, Numeric, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseCSVModel(BaseModel):
    @classmethod
    def from_csv_row(cls, row: str | list[str]):
        """Create an instance of the model from a CSV row."""
        values = row.split(',') if type(row) is str else row
        field_values = {}
        for i, field in enumerate(cls.model_fields.keys()):
            if i < len(values) and values[i]:
                field_values[field] = values[i].strip('"')
        return cls(**field_values)

    @staticmethod
    def validate_fecha(value):
        """Validates a string date formats and converts it into a date format"""
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%d/%m/%Y")
            except ValueError:
                raise ValueError(f'Invalid date format: {value}')
        return value


class BaseORM(DeclarativeBase):
    OpTransferido: Mapped[int] = mapped_column(Integer, nullable=True)
    OpTransferidoIntento: Mapped[int] = mapped_column(Numeric(18, 0), nullable=True)
    OpTransferidoFechaHora: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    OpTransferidoUsuario: Mapped[int] = mapped_column(Integer, nullable=True)


class BaseModelFactory(ABC):
    pydantic_model: BaseCSVModel
    orm_model: BaseORM
    procedures: list[tuple]
