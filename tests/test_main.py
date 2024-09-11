import pytest
import json
from unittest import mock
from unittest.mock import patch, MagicMock
from main import FILE_PATH, load_json, write_json

### TESTS ###

### TEST FOR JSON FUNCTIONS ###

def test_load_json_file_exists(monkeypatch):
    mock_open = mock.mock_open(read_data='{"1": {"stars": 5, "comment": "Great job!", "user": 12345}}')
    monkeypatch.setattr("builtins.open", mock_open)
    monkeypatch.setattr("os.path.exists", lambda x: True)

    data, error = load_json()

    assert error == None
    assert data == {"1": {"stars": 5, "comment": "Great job!", "user": 12345}}


def test_load_json_file_does_not_exist(monkeypatch):
    monkeypatch.setattr("os.path.exists", lambda x: False)

    data, error = load_json()

    assert error == None
    assert data == {}


def test_load_json_file_corrupted(monkeypatch):
    mock_open = mock.mock_open(read_data='{invalid_json}')
    monkeypatch.setattr("builtins.open", mock_open)
    monkeypatch.setattr("os.path.exists", lambda x: True)

    data, error = load_json()

    assert error != None
    assert data == {}


def test_write_json_success(monkeypatch):
    mock_open = mock.mock_open()
    monkeypatch.setattr("builtins.open", mock_open)

    data = {"1": {"stars": 5, "comment": "Great job!", "user": 12345}}
    error = write_json(data)

    assert error == None
    mock_open.assert_called_once_with(FILE_PATH, "w", encoding="utf8")
    mock_open().write.assert_called_once_with(json.dumps(data, indent=4))


def test_write_json_failure(monkeypatch):
    monkeypatch.setattr("builtins.open", mock.mock_open(side_effect=OSError("Permission denied")))

    data = {"1": {"stars": 5, "comment": "Great job!", "user": 12345}}
    error = write_json(data)

    assert "Permission denied" in error

# ### TEST FOR SLASH COMMANDS ###

# @pytest.mark.asyncio
# @patch("main.load_json")
# @patch("main.write_json")
# async def test_vouch_command(mock_write_json, mock_load_json, monkeypatch):

#     # Prepare mock data for load_json and write_json
#     mock_load_json.return_value = ({}, "")
#     mock_write_json.return_value = ""

#     # Create a mock Interaction
#     mock_interaction = MagicMock()
#     mock_interaction.user.mention = "MockUser"
#     mock_interaction.user.id = 123456
#     mock_interaction.response.defer = MagicMock()
#     mock_interaction.followup.send = MagicMock()
#     mock_interaction.channel.edit = MagicMock()
    
#     # Mock an attachment (image)
#     mock_attachment = MagicMock()
#     mock_attachment.content_type = "image/png"
#     mock_attachment.url = "http://example.com/image.png"

#     # Call the command
#     await main.vouch(mock_interaction, stars=MagicMock(value=5), comment="Great vouch!", image=mock_attachment)

#     # Verify that the defer method was called
#     mock_interaction.response.defer.assert_called_once_with(thinking=True)

#     # Check that write_json was called to save the vouch
#     mock_write_json.assert_called_once()

#     # Check that followup.send was called to send the result
#     mock_interaction.followup.send.assert_called_once()
    
# channel_id = 12345
# style = mock.Mock()
# style.wrong_channel_error_text = "You cannot use this command in this channel."

# @pytest.mark.asyncio
# async def test_command_in_correct_channel():
#     mock_ctx = mock.Mock()
#     mock_ctx.channel_id = channel_id
#     mock_ctx.followup = mock.AsyncMock()

#     if mock_ctx.channel_id != channel_id:
#         await mock_ctx.followup.send(style.wrong_channel_error_text)
#         return

#     mock_ctx.followup.send.assert_not_called()
    
# @pytest.mark.asyncio
# async def test_command_in_wrong_channel():
#     mock_ctx = mock.Mock()
#     mock_ctx.channel_id = 54321
#     mock_ctx.followup = mock.AsyncMock()

#     if mock_ctx.channel_id != channel_id:
#         await mock_ctx.followup.send(style.wrong_channel_error_text)
#         return

#     mock_ctx.followup.send.assert_called_once_with(style.wrong_channel_error_text)
