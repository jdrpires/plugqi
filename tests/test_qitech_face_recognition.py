import base64
import pytest
from connectors.qitech_face_recognition import QitechFaceRecognitionClient
from qitech_client import QiTechError


def test_analyze_image_invalid_base64_raises():
    client = QitechFaceRecognitionClient(api_key="fake")
    invalid_b64 = "not-a-valid-base64"

    with pytest.raises(QiTechError) as exc:
        client.analyze_image(invalid_b64)

    err = exc.value
    assert err.status == 400
    assert isinstance(err.payload, dict)
    assert err.payload.get("image_status") == "invalid_base64"


def test_analyze_image_valid_png_calls_post(monkeypatch):
    # base64 for a tiny 1x1 png
    png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAAWgmWQ0AAAAASUVORK5CYII="
    client = QitechFaceRecognitionClient(api_key="fake")

    # Replace session.post with a mock that asserts payload and returns a fake response
    class FakeResp:
        def __init__(self):
            self.status_code = 200
        def json(self):
            return {"ok": True}

    def fake_post(url, json=None, headers=None, timeout=None):
        assert json == {"image": png_b64}
        return FakeResp()

    monkeypatch.setattr(client, "session", client.session)
    monkeypatch.setattr(client.session, "post", fake_post)

    resp = client.analyze_image(png_b64)
    assert resp == {"ok": True}
