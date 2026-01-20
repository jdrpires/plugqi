from typing import Optional

_store: dict[str, str] = {}

def set_redirect(token: str, url: str) -> None:
    _store[token] = url

def get_redirect(token: str) -> Optional[str]:
    return _store.get(token)
