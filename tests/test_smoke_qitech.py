import os
import pytest
import requests

@pytest.mark.skipif(os.getenv("RUN_INTEGRATION") != "1", reason="set RUN_INTEGRATION=1 to enable")
def test_smoke_post_and_get():
    base = os.environ["QITECH_BASE_URL"]
    api_key = os.environ["QITECH_API_KEY"]
    headers = {
        "Authorization": f"Bearer {os.environ['QITECH_JWT']}",
        "API-CLIENT-KEY": os.environ["QITECH_API_CLIENT_KEY"],
        "Content-Type": "application/json",
        "payload_md5": os.environ.get("QITECH_PAYLOAD_MD5", "d41d8cd98f00b204e9800998ecf8427e"),
    }

    r1 = requests.post(f"{base}/test", headers=headers, json={})
    assert r1.status_code in (200, 202)
    assert "Congrats" in r1.text

    r2 = requests.get(f"{base}/test/{api_key}", headers=headers)
    assert r2.status_code in (200, 202)
    assert "Congrats" in r2.text
