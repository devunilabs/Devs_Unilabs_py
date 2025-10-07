import logging.config
import os

import pytest
import yaml

from utils.file_manaement import list_csv_files, move_file

with open("../logging_config.yaml", "rb") as f:
    logging_config_file = yaml.safe_load(f.read())
    logging.config.dictConfig(logging_config_file)

logger = logging.getLogger('development')


@pytest.fixture
def setup_test_files(tmp_path):
    source_file = tmp_path / "source_file.txt"
    source_file.write_text("Test content")
    dest_dir = tmp_path / "dest_true"
    dest_dir.mkdir()
    return str(source_file), str(dest_dir)


def test_file_not_found_error(tmp_path) -> None:
    non_existent_file = str(tmp_path / "non_existent_file.txt")
    with pytest.raises(FileNotFoundError) as excinfo:
        list_csv_files(path=non_existent_file, logger=logger)
    assert str(excinfo.value) == f"The path '{non_existent_file}' does not exist."


def test_move_file(setup_test_files):
    source_file, dest_dir = setup_test_files
    new_path = move_file(source_file, dest_dir, logger=logger)
    expected_path = os.path.join(dest_dir, "source_file.txt")
    assert new_path == expected_path
    assert os.path.exists(expected_path)


def test_file_not_found(tmp_path):
    non_existent_file = tmp_path / "non_existent_file.txt"
    dest_dir = tmp_path / "dest_true"
    with pytest.raises(FileNotFoundError):
        move_file(str(non_existent_file), str(dest_dir), logger=logger)


def test_invalid_destination_directory(setup_test_files, monkeypatch):
    source_file, _ = setup_test_files
    monkeypatch.setattr(os.path, 'isdir', lambda _: False)
    with pytest.raises(NotADirectoryError):
        move_file(str(source_file), "/invalid/dest/true", logger=logger)
