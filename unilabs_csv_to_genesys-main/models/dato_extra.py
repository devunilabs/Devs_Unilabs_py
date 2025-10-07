from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import field_validator, constr
from sqlalchemy import String, DateTime, Integer, Numeric, Float
from sqlalchemy.orm import Mapped, mapped_column

from models.base_models import BaseCSVModel, BaseORM, BaseModelFactory


class DatoExtra(BaseCSVModel):
    ID_Personal: constr(max_length=20)
    ID_TipoFileDatoExtra: int
    Fecha: datetime
    ID_Moneda: int
    Importe: float
    Observaciones: Optional[constr(max_length=50)] = None
    ID_PlanillaConf: Optional[int] = None

    @field_validator('Fecha', mode='before')
    def validate_fecha(cls, value):
        return super().validate_fecha(value)


class DatoExtraEntity(BaseORM):
    __tablename__ = 'TMP_RRHHDatoExtra'

    Op: Mapped[int] = mapped_column(Numeric(18, 0), primary_key=True, autoincrement=True)
    ID_Personal: Mapped[str] = mapped_column(String(20), nullable=False)
    ID_TipoFileDatoExtra: Mapped[int] = mapped_column(Integer, nullable=False)
    Fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ID_Moneda: Mapped[int] = mapped_column(Numeric(18, 0), nullable=False)
    Importe: Mapped[float] = mapped_column(Float, nullable=False)
    Observaciones: Mapped[str] = mapped_column(String(50), nullable=True)
    ID_PlanillaConf: Mapped[int] = mapped_column(Numeric(18, 0), nullable=True)

    def __repr__(self):
        return (
            f"TMP_RRHHDatoExtra(ID_Personal='{self.ID_Personal}', ID_TipoFileDatoExtra={self.ID_TipoFileDatoExtra}, "
            f"Fecha='{self.Fecha}', ID_Moneda={self.ID_Moneda}, Importe={self.Importe}, "
            f"Observaciones='{self.Observaciones}', ID_PlanillaConf={self.ID_PlanillaConf})"
        )


@dataclass
class DatoExtraFactory(BaseModelFactory):
    pydantic_model = DatoExtra
    orm_model = DatoExtraEntity
    procedures = [('EXEC sp_TMPRRHHDatoExtra', None)]
