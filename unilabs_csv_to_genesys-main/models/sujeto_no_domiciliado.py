from dataclasses import dataclass
from typing import Optional

from pydantic import constr
from sqlalchemy import String, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from models.base_models import BaseCSVModel, BaseORM, BaseModelFactory


class SujetoNoDomiciliado(BaseCSVModel):
    Codigo: constr(max_length=20)
    RazonSocial: constr(max_length=200)
    NombreComercial: Optional[constr(max_length=100)] = None
    TipoDocumento: int
    NroDocumento: constr(max_length=20)


class SujetoNoDomiciliadoEntity(BaseORM):
    __tablename__ = 'TMP_SujetoNoDomiciliado'

    Codigo: Mapped[str] = mapped_column(String(20), nullable=False)
    RazonSocial: Mapped[str] = mapped_column(String(200), nullable=False)
    NombreComercial: Mapped[str] = mapped_column(String(100), nullable=True)
    TipoDocumento: Mapped[int] = mapped_column(Integer, nullable=False)
    NroDocumento: Mapped[str] = mapped_column(String(20), nullable=False)
    Op: Mapped[int] = mapped_column(Numeric(18, 0), primary_key=True, autoincrement=True)

    def __repr__(self):
        return (
            f"SujetoNoDomiciliadoEntity(Codigo='{self.Codigo}', RazonSocial='{self.RazonSocial}', "
            f"NombreComercial='{self.NombreComercial}', TipoDocumento={self.TipoDocumento}, "
            f"NroDocumento='{self.NroDocumento}', Op={self.Op}, OpTransferido={self.OpTransferido}, "
            f"OpTransferidoIntento={self.OpTransferidoIntento}, OpTransferidoFechaHora='{self.OpTransferidoFechaHora}', "
            f"OpTransferidoUsuario={self.OpTransferidoUsuario})"
        )


@dataclass
class SujetoNoDomiciliadoFactory(BaseModelFactory):
    pydantic_model = SujetoNoDomiciliado
    orm_model = SujetoNoDomiciliadoEntity
    procedures = [('EXEC sp_TMPSujetoNoDomiciliado', None)]
