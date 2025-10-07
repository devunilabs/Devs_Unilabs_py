#main.py
import asyncio
import logging.config
from pprint import pprint
import pyodbc
import tomllib
import yaml
import functools
from sqlalchemy.orm import Session

from db_connection import get_engine
from models import load_from_csv_file
from models.operations import insert_records, execute_procedures, OperationalException
from utils.file_manaement import list_csv_files, read_file_content, move_file
from utils.send_email import send_mail, async_send_email

with open("logging_config.yaml", "rb") as f:
    logging_config_file = yaml.safe_load(f.read())
    logging.config.dictConfig(logging_config_file)

with open('config.toml', 'rb') as f:
    config = tomllib.load(f)

logger = logging.getLogger(config['logger'])

pyodbc.pooling = False

send_mail_configured = functools.partial(async_send_email, mail_config=config['email'], logger=logger)


async def main() -> None:
    csv_files = list_csv_files(config['folder']['source'], logger)
    for db_identifier, tables in csv_files.items():
        engine = get_engine(config['db'][db_identifier])
        await process_db(engine, tables, logger)


async def process_db(engine, tables, logger):
    # Define the priority order
    priority_order = ['_TMP_PersonaNatural_', '_TMP_RRHHPersonal_']
    # Sort the tables based on the priority order
    sorted_tables = sorted(tables.items(),
                           key=lambda x: priority_order.index(x[0]) if x[0] in priority_order else float('inf'))

    with Session(engine) as session:
        logger.info(f'Procesando data para la conexión: {engine.url.host}')
        for table, paths in sorted_tables:
            await process_table(session, table, paths, logger)


async def process_table(session, table, paths, logger):
    for path in paths:
        try:
            logger.debug(f"Inicio de carga de data de la ruta: {path}")
            await load_and_insert_records(path, table, session, logger)
            if config['execute_procedures']:
                logger.debug('Ejecutando procedimientos')
                execute_procedures(session, table, logger)
            else:
                logger.debug('Ejecución de procedimientos omitida')
            move_file(path, config['folder']['succeded'], logger)
        except (OperationalException, ValueError) as e:
            logger.error(f"Excepción capturada: {e}")
            move_file(path, config['folder']['observed'], logger)

            body = (f"Archivo: {path} \n"
                    f"Error capturado:\n"
                    f"{str(e)}")

            await send_mail_configured(subject='Archivo observado', body=body)


async def load_and_insert_records(path, table, session, logger):
    models = await load_from_csv_file(rows=read_file_content(path), table=table, logger=logger, path=str(path),
                                      mailer=send_mail_configured)
    if models:
        insert_records(records=models, session=session, table=table, logger=logger)
    return models


if __name__ == '__main__':
    asyncio.run(main())
