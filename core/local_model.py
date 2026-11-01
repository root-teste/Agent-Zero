"""Inferência privada: endpoint loopback, sem proxies, redirects ou fallback."""
import ipaddress
from urllib.parse import urlsplit
import requests
from .config import settings


class ModelUnavailable(Exception):
    pass


def chat(messages):
    if not settings.LOCAL_MODEL_ENABLED:
        raise ModelUnavailable("Modelo local desativado nas definições do servidor.")
    address = urlsplit(settings.OLLAMA_URL)
    try:
        local = ipaddress.ip_address(address.hostname).is_loopback
    except ValueError:
        local = False
    if address.scheme != "http" or not local or address.username or address.password or address.path not in ("", "/") or address.query or address.fragment:
        raise ModelUnavailable("Configure Ollama num endereço IP de loopback, sem redirecionamentos.")
    if ":cloud" in settings.OLLAMA_MODEL.lower():
        raise ModelUnavailable("Modelos cloud não são permitidos no núcleo privado.")
    try:
        with requests.Session() as session:
            session.trust_env = False
            response = session.post(settings.OLLAMA_URL.rstrip("/") + "/api/chat",
                json={"model": settings.OLLAMA_MODEL, "messages": messages, "stream": False,
                      "options": {"num_ctx": 8192, "num_predict": 1024}},
                timeout=(3, 180), allow_redirects=False)
            if response.status_code != 200:
                raise ModelUnavailable("O modelo local está indisponível. Verifique o serviço e os pesos instalados.")
            data = response.json()
            content = data["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError("empty")
            return content[:24000], data.get("model", settings.OLLAMA_MODEL)
    except (requests.RequestException, ValueError, KeyError, TypeError):
        raise ModelUnavailable("Não foi possível obter uma resposta válida do modelo local.") from None
