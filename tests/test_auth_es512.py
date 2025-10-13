import re
import jwt
import responses

def test_jwt_es512_and_headers_in_get(client_sandbox):
    pattern = re.compile(r".*/test/[^/]+$")

    captured = {}
    @responses.activate
    def run():
        def cb(req):
            # headers case-insensitive + normalizados
            h = {k.lower().replace("_","-"): v for k,v in req.headers.items()}
            captured["auth"] = h.get("authorization")
            captured["api_client_key"] = h.get("api-client-key")
            captured["payload_md5"] = h.get("payload-md5") or h.get("payload_md5")
            return (200, {"Content-Type":"application/json"}, '{"success":"Congrats!"}')
        responses.add_callback(responses.GET, pattern, callback=cb)

        api_key = getattr(client_sandbox, "api_key", "sandbox-api-key")
        client_sandbox.get(f"/test/{api_key}")

    run()

    # 1) Authorization presente (com ou sem 'Bearer ')
    assert captured["auth"], "Header Authorization ausente"
    auth = captured["auth"]
    token = auth.split(" ", 1)[1] if auth.lower().startswith("bearer ") else auth

    # 2) Prova do algoritmo ES512
    header = jwt.get_unverified_header(token)
    assert header.get("alg") == "ES512"

    # 3) API-CLIENT-KEY presente (nome do header pode variar na sua lib; aqui aceitamos o padrão)
    assert captured["api_client_key"] is not None

    # 4) payload_md5: aceitar header OU claim no JWT (fallback)
    md5_header = captured["payload_md5"]
    if not md5_header:
        payload = jwt.decode(token, options={"verify_signature": False})
        assert "payload_md5" in payload, "Nem header payload_md5 nem claim payload_md5 no JWT encontrados"
