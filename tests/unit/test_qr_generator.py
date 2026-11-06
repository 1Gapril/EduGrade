import base64
from pathlib import Path

from PIL import Image

from backend.app.integrations.qr.generator import QRCodeGenerator


def test_generate_qr_png_and_write_file(tmp_path):
    output = tmp_path / "exam.png"

    image = QRCodeGenerator().generate(
        {"exam_id": "exam-1", "student": "á"},
        output_path=str(output),
    )

    assert image.startswith(b"\x89PNG\r\n\x1a\n")
    assert output.read_bytes() == image
    with Image.open(output) as decoded:
        assert decoded.format == "PNG"


def test_styled_qr_and_data_uri_round_trip():
    generator = QRCodeGenerator()
    encoded = generator.generate_base64({"type": "exam"}, styled=True)
    uri = generator.generate_data_uri({"type": "exam"})

    assert base64.b64decode(encoded).startswith(b"\x89PNG")
    assert uri.startswith("data:image/png;base64,")


def test_batch_generates_sequential_files(tmp_path):
    paths = QRCodeGenerator().generate_batch(
        [{"copy": "a"}, {"copy": "b"}],
        str(tmp_path),
        prefix="copy_",
    )

    assert [Path(path).name for path in paths] == [
        "copy_0001.png",
        "copy_0002.png",
    ]
    assert all(path for path in paths)
    assert all((tmp_path / f"copy_{index:04d}.png").is_file() for index in (1, 2))


def test_parse_qr_json_and_plain_text():
    assert QRCodeGenerator.parse_qr_data('{"exam_id":"exam-1"}') == {"exam_id": "exam-1"}
    assert QRCodeGenerator.parse_qr_data("legacy-id") == {"raw": "legacy-id"}


def test_build_exam_qr_data_includes_student_only_when_provided():
    base = QRCodeGenerator.build_exam_qr_data("exam", "version", "copy")
    assigned = QRCodeGenerator.build_exam_qr_data("exam", "version", "copy", "student")

    assert base == {
        "exam_id": "exam",
        "version_id": "version",
        "copy_identifier": "copy",
        "type": "exam_copy",
    }
    assert assigned["student_id"] == "student"
