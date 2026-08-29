from pathlib import Path

from sio_asyncapi.cli import main


def test_cli_export_yaml_to_file(tmp_path: Path):
    out = tmp_path / "spec.yml"
    assert main(["export", "tests.fixtures:socketio", "--out", str(out)]) == 0
    text = out.read_text()
    assert text.startswith("asyncapi: 3.1.0")
    assert "receive_download_file" in text
    assert "reply:" in text


def test_cli_export_agent_schema(tmp_path: Path, capsys):
    assert main(["export", "tests.fixtures:socketio", "--agent-schema"]) == 0
    captured = capsys.readouterr()
    assert "sio-asyncapi-agent-schema" in captured.out
