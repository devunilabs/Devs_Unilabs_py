import csv
import os
import shutil

from logging import Logger


def list_csv_files(path: str, logger: Logger) -> dict[str, dict[str, list]]:
    """
    Returns a dictionary of all CSV files in the given path.

    Args:
        path (str): The path to search for CSV files.
        logger: Logger object

    Returns:
        files_to_process (dict): A dictionary of file paths for all CSV files found in the given path.

    Raises:
        FileNotFoundError: If the provided path does not exist.
    """

    # Check if the path exists
    if not os.path.exists(path):
        logger.error(f"El archivo '{path}' no existe.")
        raise FileNotFoundError(f"El archivo '{path}' no existe.")

    files_to_process = {}

    # Walk through the directory tree starting from the given path
    for root, dirs, files in os.walk(path):
        for file in files:
            # Check if the file has a .csv extension
            if file.endswith('.csv'):
                try:
                    # Construct the full file path and append it to the list
                    db_id, table, _ = parse_filename(file)
                    files_to_process[db_id] = files_to_process.get(db_id, {})
                    files_to_process[db_id][table] = files_to_process[db_id].get(table, [])
                    files_to_process[db_id][table].append(os.path.join(root, file))
                except ValueError as error:
                    logger.error(f"Error obteniendo partes del nombre. '{file=}' \n{error=}")

    logger.info(f"{files_to_process=}")
    return files_to_process


def read_file_content(path: str) -> list[list[str]]:
    """
    Returns the content of the CSV file
    :param path: The CSV path
    :return: List of rows from the CSV file
    """
    with open(path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        return [row for row in reader]


def parse_filename(file_path: str) -> tuple[str, ...]:
    """
    Returns the parts from the filename
    :param file_path: complete file path
    :return: list with DB name, Table name and date
    """
    file_name = os.path.basename(file_path)
    name = os.path.splitext(file_name)[0]  # removes file's extension
    return tuple(name.strip('%').split('%'))


def move_file(file_path: str, destination_path: str, logger: Logger) -> str:
    """
    Moves a file to a destination directory
    :param file_path: Current file path
    :param destination_path: Destination directory
    :param logger: Logger object
    :return: New file path after the move operation
    Raises:
        FileNotFoundError: If the file to be moved is not found.
        NotADirectoryError: If either of the destination directories is not a valid directory.
    """
    # Check if the file exists
    if not os.path.isfile(file_path):
        logger.error(f"Archivo no encontrado: {file_path}")
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

    # Check if the destination directories are valid
    if not os.path.isdir(destination_path):
        logger.error(f"Directorio inválido: {destination_path}")
        raise NotADirectoryError(f"Directorio inválido: {destination_path}")

    # Get the filename from the file path
    filename = os.path.basename(file_path)

    # Construct the new file path
    new_file_path = os.path.join(destination_path, filename)

    try:
        # Move the file
        shutil.move(file_path, new_file_path)
        logger.info(f"Archivo movido a: {new_file_path}")
        return new_file_path
    except Exception as e:
        logger.error(f"Error moviendo archivo de: '{filename}' a: '{destination_path}':\n{e}")
