"""Cliente do núcleo: credencial e timeout consistentes, sem logging de payloads."""
import requests as _requests
from urllib.parse import urlsplit

from .config import settings

exceptions = _requests.exceptions


def request(method, url, **kwargs):
    if (urlsplit(url).scheme, urlsplit(url).netloc) != (urlsplit(settings.API_URL).scheme, urlsplit(settings.API_URL).netloc):
        raise ValueError("O cliente do núcleo só pode contactar a origem configurada")
    kwargs.setdefault("timeout", 15)
    headers = dict(kwargs.pop("headers", {}) or {})
    headers.setdefault("x-api-key", settings.API_KEY)
    # Não seguir redirects: uma credencial do núcleo não deve mudar de destino.
    kwargs["allow_redirects"] = False
    return _requests.request(method, url, headers=headers, **kwargs)


def get(url, **kwargs):
    return request("GET", url, **kwargs)


def post(url, **kwargs):
    return request("POST", url, **kwargs)


def patch(url, **kwargs):
    return request("PATCH", url, **kwargs)
