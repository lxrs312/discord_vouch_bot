import pytest
import json
from unittest import mock
from unittest.mock import patch, MagicMock
import main

### TESTS ###

### TEST FOR JSON FUNCTIONS ###

def test_load_json_file_exists(monkeypatch):
    mock_open = mock.mock_open(read_data='{"1": {"stars": 5, "message": "Great job!", "product": "r6", "user": 12345}}')
    monkeypatch.setattr("builtins.open", mock_open)
    monkeypatch.setattr("os.path.exists", lambda x: True)

    data, error = main.load_json()

    assert error == None
    assert data == {"1": {"stars": 5, "message": "Great job!", "product": "r6", "user": 12345}}


def test_load_json_file_does_not_exist(monkeypatch):
    monkeypatch.setattr("os.path.exists", lambda x: False)

    data, error = main.load_json()

    assert error == None
    assert data == {}


def test_load_json_file_corrupted(monkeypatch):
    mock_open = mock.mock_open(read_data='{invalid_json}')
    monkeypatch.setattr("builtins.open", mock_open)
    monkeypatch.setattr("os.path.exists", lambda x: True)

    data, error = main.load_json()

    assert error != None
    assert data == {}


def test_write_json_success(monkeypatch):
    mock_open = mock.mock_open()
    monkeypatch.setattr("builtins.open", mock_open)

    data = {"1": {"stars": 5, "message": "Great job!", "product": "r6", "user": 12345}}
    error = main.write_json(data)

    assert error is None
    mock_open.assert_called_once_with(main.FILE_PATH, "w", encoding="utf8")

    # Collect all the data written and compare it with the expected JSON
    written_data = "".join(call.args[0] for call in mock_open().write.call_args_list)
    assert written_data == json.dumps(data, indent=4)


def test_write_json_failure(monkeypatch):
    def raise_oserror(*args, **kwargs):
        raise OSError("Permission denied")

    monkeypatch.setattr("builtins.open", raise_oserror)

    data = {"1": {"stars": 5, "message": "Great job!", "product": "r6", "user": 12345}}
    error = main.write_json(data)

    assert "Permission denied" in str(error)
