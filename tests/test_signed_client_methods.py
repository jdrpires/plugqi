import re
import inspect
import jwt
import responses

ALLOWED_EMPTY_MD5 = {
    "",  # algumas libs mandam string vazia
    "d41d8cd98f00b204e9800998ecf8427e",  # md5("")
    "99914b932bd37a50b983c5e7c90ae93b",  # md5("{}")
}


def _call_post_dynamic(client, path, body):
    sig = inspect.signature(client.post)
    if "json" in sig.parameters:
        return client.post(path, json=body)
    elif "data" in sig.parameters:
        return client.post(path, data=body)
    elif "payload" in sig.parameters:
        return client.post(path, payload=body)
    else:
        # assume assinatura posicional: (path, body)
        return client.post(path, body)

def test_post_sends_md5_of_body(client_sandbox, md5_of):
    pattern = re.compile(r".*/test$")
    body = {"ping":"pong"}

    captured = {}
    @responses.activate
    def run():
        def cb(req):
            h = {k.lower().replace("_","-"): v for k,v in req.headers.items()}
            captured["payload_md5"] = h.get("payload-md5") or h.get("payload_md5")
            captured["auth"] = h.get("authorization")
            return (200, {"Content-Type":"application/json"}, '{"success":"Congrats!"}')
        responses.add_callback(responses.POST, pattern, callback=cb)

        _call_post_dynamic(client_sandbox, "/test", body)

    run()

    want = md5_of(body)

    # Preferimos header; se não vier, validamos o claim no JWT
    if captured["payload_md5"]:
        assert captured["payload_md5"] == want
    else:
        assert captured["auth"], "Sem Authorization para checar claim payload_md5"
        token = captured["auth"].split(" ", 1)[1] if captured["auth"].lower().startswith("bearer ") else captured["auth"]
        payload = jwt.decode(token, options={"verify_signature": False})
        assert payload.get("payload_md5") == want

def test_delete_is_also_signed_with_md5(client_sandbox):
    pattern = re.compile(r".*/resource/123$")

    captured = {}
    @responses.activate
    def run():
        def cb(req):
            h = {k.lower().replace("_","-"): v for k,v in req.headers.items()}
            captured["payload_md5"] = h.get("payload-md5") or h.get("payload_md5")
            captured["auth"] = h.get("authorization")
            return (204, {}, "")
        responses.add_callback(responses.DELETE, pattern, callback=cb)
        client_sandbox.delete("/resource/123")
    run()

    if captured["payload_md5"] is not None:
        assert captured["payload_md5"] in ALLOWED_EMPTY_MD5
    else:
        assert captured["auth"], "Sem Authorization e sem header payload_md5"
        token = captured["auth"].split(" ", 1)[1] if captured["auth"].lower().startswith("bearer ") else captured[
            "auth"]
        payload = jwt.decode(token, options={"verify_signature": False})
        assert payload.get("payload_md5") in ALLOWED_EMPTY_MD5

