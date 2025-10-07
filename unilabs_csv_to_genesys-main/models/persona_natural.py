from dataclasses import dataclass
from typing import Optional

from pydantic import constr
from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from models.base_models import BaseCSVModel, BaseORM, BaseModelFactory


class PersonaNatural(BaseCSVModel):
    Nombre1: constr(max_length=50)
    Nombre2: Optional[constr(max_length=50)] = None
    ApellidoPaterno: constr(max_length=50)
    ApellidoMaterno: constr(max_length=50)
    DNI: constr(max_length=8)
    RUC: Optional[constr(max_length=11)] = None


class PersonaNaturalEntity(BaseORM):
    __tablename__ = 'TMP_PersonaNatural'

    Op: Mapped[int] = mapped_column(Numeric(18, 0), primary_key=True, autoincrement=True)
    Nombre1: Mapped[str] = mapped_column(String(50), nullable=False)
    Nombre2: Mapped[str] = mapped_column(String(50), nullable=True)
    ApellidoPaterno: Mapped[str] = mapped_column(String(50), nullable=False)
    ApellidoMaterno: Mapped[str] = mapped_column(String(50), nullable=False)
    DNI: Mapped[str] = mapped_column(String(8), nullable=False)
    RUC: Mapped[str] = mapped_column(String(11), nullable=True)

    def __repr__(self):
        return (
            f"TMP_PersonaNatural(Nombre1='{self.Nombre1}', Nombre2='{self.Nombre2}', "
            f"ApellidoPaterno='{self.ApellidoPaterno}', ApellidoMaterno='{self.ApellidoMaterno}', "
            f"DNI='{self.DNI}', RUC='{self.RUC}')"
        )


@dataclass
class PersonaNaturalFactory(BaseModelFactory):
    pydantic_model = PersonaNatural
    orm_model = PersonaNaturalEntity
    procedures = [('EXEC sp_TMPPersonaNatural', None)]
