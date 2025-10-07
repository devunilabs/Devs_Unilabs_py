from dataclasses import dataclass
from datetime import datetime

from pydantic import field_validator, constr
from sqlalchemy import DateTime, Float, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base_models import BaseCSVModel, BaseORM, BaseModelFactory


class AutorizarHE(BaseCSVModel):
    ID_Personal: constr(max_length=20)
    Fecha: datetime
    HoraInicio: float
    HoraTermino: float
    HorasExtras_Autorizadas: float

    @field_validator('Fecha', mode='before')
    def validate_fecha(cls, value):
        return super().validate_fecha(value)


class AutorizarHEEntity(BaseORM):
    __tablename__ = 'TMP_RRHHAutorizarHE'

    Op: Mapped[int] = mapped_column(Numeric(18, 0), primary_key=True, autoincrement=True)
    ID_Personal: Mapped[str] = mapped_column(String(20), nullable=False)
    Fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    HoraInicio: Mapped[float] = mapped_column(Float, nullable=False)
    HoraTermino: Mapped[float] = mapped_column(Float, nullable=False)
    HorasExtras_Autorizadas: Mapped[float] = mapped_column(Float, nullable=False)

    def __repr__(self):
        return (
            f"TMP_RRHHAutorizarHE(ID_Personal='{self.ID_Personal}', Fecha='{self.Fecha}', "
            f"HoraInicio={self.HoraInicio}, HoraTermino={self.HoraTermino}, "
            f"HorasExtras_Autorizadas={self.HorasExtras_Autorizadas})"
        )


@dataclass
class AutorizarHEFactory(BaseModelFactory):
    pydantic_model = AutorizarHE
    orm_model = AutorizarHEEntity
    procedures = [('EXEC sp_TMPRRHHAutorizarHE', None)]
