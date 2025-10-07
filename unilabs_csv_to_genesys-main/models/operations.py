from logging import Logger

import pyodbc
from sqlalchemy import sql
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models import BaseCSVModel, model_mapper


class OperationalException(Exception):
    pass


def insert_records(records: list[BaseCSVModel], session: Session, table: str, logger: Logger) -> None:
    """
    Perform a insert operation of a list of models into a given table
    :param records: List of models to insert
    :param session: DB session object
    :param table: Table to perform the insertion
    :param logger: Logger object
    """
    orm_entity_class = model_mapper[table].orm_model

    logger.debug(f"A punto de insertar {len(records)} registros en el modelo: {orm_entity_class.__name__}")

    try:
        for record in records:
            entity_object = orm_entity_class(**record.model_dump())
            session.add(entity_object)

        session.commit()
        logger.info(f"{len(records)} registros insertados en tabla: {orm_entity_class.__table__}")
    except (SQLAlchemyError, pyodbc.Error) as e:
        detailed_error = f"Error durante la inserción en la entidad: {orm_entity_class.__name__}: \n{e}"
        logger.error(detailed_error)
        raise OperationalException(f"Error durante inserción de registros.\n{detailed_error}")


def execute_procedures(session: Session, table: str, logger: Logger) -> None:
    """
    Execute stored procedures
    :param session: DB session object
    :param table: Table to get the related stored procedures
    :param logger: Logger object
    """
    for procedure in model_mapper[table].procedures:
        query = params = None
        try:
            query, params = procedure
            statement = sql.text(query)
            session.execute(statement=statement, params=params)
            session.commit()
            logger.info(f"Procedimiento {query} ejecutado exitosamente.")
        except SQLAlchemyError as e:
            detailed_error = f"Error ejecutando {query=}; {params=}: {e}"
            logger.error(detailed_error)
            raise OperationalException(f"Error durante inserción de registros.\n{detailed_error}")
