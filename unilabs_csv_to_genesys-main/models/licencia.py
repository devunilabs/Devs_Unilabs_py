from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import field_validator, constr
from sqlalchemy import String, DateTime, Integer, Numeric, Float
from sqlalchemy.orm import Mapped, mapped_column

from models.base_models import BaseCSVModel, BaseORM, BaseModelFactory


class Licencia(BaseCSVModel):
    ID_Personal: constr(max_length=20)
    Fecha: datetime
    ID_TipoLicencia: int
    Descripcion: constr(max_length=250)
    Estado: int
    Condicion: int
    Solicitado_Horas: float
    Observaciones: Optional[constr(max_length=250)] = None
    ID_TipoEnfermedad: Optional[int] = None
    ID_TipoAccidenteTrabajo: Optional[int] = None
    ID_TipoParteLesionada: Optional[int] = None
    ID_TipoNaturalezaLesion: Optional[int] = None
    ID_TipoMaternidad: Optional[int] = None
    ID_TipoAplicacionLicencia: Optional[int] = None

    @field_validator('Fecha', mode='before')
    def validate_fecha(cls, value):
        return super().validate_fecha(value)


class LicenciaEntity(BaseORM):
    __tablename__ = 'TMP_RRHHLicencia'

    Op: Mapped[int] = mapped_column(Numeric(18, 0), primary_key=True, autoincrement=True)
    ID_Personal: Mapped[str] = mapped_column(String(20), nullable=False)
    Fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ID_TipoLicencia: Mapped[int] = mapped_column(Integer, nullable=False)
    Descripcion: Mapped[str] = mapped_column(String(250), nullable=False)
    Estado: Mapped[int] = mapped_column(Integer, nullable=False)
    Condicion: Mapped[int] = mapped_column(Integer, nullable=False)
    Solicitado_Horas: Mapped[float] = mapped_column(Float, nullable=False)
    Observaciones: Mapped[str] = mapped_column(String(250), nullable=True)
    ID_TipoEnfermedad: Mapped[int] = mapped_column(Integer, nullable=True)
    ID_TipoAccidenteTrabajo: Mapped[int] = mapped_column(Integer, nullable=True)
    ID_TipoParteLesionada: Mapped[int] = mapped_column(Integer, nullable=True)
    ID_TipoNaturalezaLesion: Mapped[int] = mapped_column(Integer, nullable=True)
    ID_TipoMaternidad: Mapped[int] = mapped_column(Integer, nullable=True)
    ID_TipoAplicacionLicencia: Mapped[int] = mapped_column(Integer, nullable=True)

    def __repr__(self):
        return (
            f"TMP_RRHHLicencia(ID_Personal='{self.ID_Personal}', Fecha='{self.Fecha}', "
            f"ID_TipoLicencia={self.ID_TipoLicencia}, "
            f"Descripcion='{self.Descripcion}', Estado={self.Estado}, Condicion={self.Condicion}, "
            f"Solicitado_Horas={self.Solicitado_Horas}, Observaciones='{self.Observaciones}', "
            f"ID_TipoEnfermedad={self.ID_TipoEnfermedad}, "
            f"ID_TipoAccidenteTrabajo={self.ID_TipoAccidenteTrabajo}, "
            f"ID_TipoParteLesionada={self.ID_TipoParteLesionada}, "
            f"ID_TipoNaturalezaLesion={self.ID_TipoNaturalezaLesion}, ID_TipoMaternidad={self.ID_TipoMaternidad}, "
            f"ID_TipoAplicacionLicencia={self.ID_TipoAplicacionLicencia})"
        )


@dataclass
class LicenciaFactory(BaseModelFactory):
    pydantic_model = Licencia
    orm_model = LicenciaEntity
    procedures = [('EXEC sp_TMPRRHHLicencia', None)]
