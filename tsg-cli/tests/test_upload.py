import pytest
import os
import shutil
import tempfile
from typer.testing import CliRunner
from cli.commands import app

runner = CliRunner()

from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_upload_file(monkeypatch):
    mock = AsyncMock(return_value={"id": 1, "name": "test.txt", "size": "1B"})
    monkeypatch.setattr("cli.commands.upload_file", mock)
    return mock

@pytest.fixture
def mock_auth(monkeypatch):
    mock_client = MagicMock()
    mock_client.is_connected = True
    mock = AsyncMock(return_value=mock_client)
    monkeypatch.setattr("cli.commands.get_authenticated_client", mock)
    return mock

@pytest.fixture
def test_dir():
    dir_path = tempfile.mkdtemp()

    # Create some files
    with open(os.path.join(dir_path, "file1.txt"), "w") as f:
        f.write("1")
    with open(os.path.join(dir_path, "file2.txt"), "w") as f:
        f.write("2")

    # Create a nested dir
    nested = os.path.join(dir_path, "nested")
    os.makedirs(nested)
    with open(os.path.join(nested, "file3.txt"), "w") as f:
        f.write("3")

    yield dir_path

    shutil.rmtree(dir_path)

def test_upload_single_file(mock_upload_file, mock_auth, test_dir):
    file_path = os.path.join(test_dir, "file1.txt")
    result = runner.invoke(app, ["upload", file_path])
    assert result.exit_code == 0
    assert "Uploading:" in result.stdout
    assert "Success: 1" in result.stdout

def test_upload_folder(mock_upload_file, mock_auth, test_dir):
    result = runner.invoke(app, ["upload", test_dir], input="y\n") # Confirm prompt for >3 files (3 files in test_dir)
    assert result.exit_code == 0
    assert "Total files to upload: 3" in result.stdout
    assert "Success: 3" in result.stdout

def test_upload_mixed(mock_upload_file, mock_auth, test_dir):
    file_path = os.path.join(test_dir, "file1.txt")
    nested = os.path.join(test_dir, "nested")
    # Will result in 2 unique files: file1.txt (from direct and folder) and file3.txt (from nested folder)
    result = runner.invoke(app, ["upload", file_path, nested])
    assert result.exit_code == 0
    assert "Total files to upload: 2" in result.stdout
    assert "Success: 2" in result.stdout

def test_upload_missing_file(mock_upload_file, mock_auth):
    result = runner.invoke(app, ["upload", "does_not_exist.txt"])
    assert result.exit_code == 0 # Caught by the inner loop
    assert "File not found" in result.stdout
    assert "Failed: 1" in result.stdout
