import json
import pprint
from typing import Any
import builtins
from urllib.parse import parse_qs
from enum import Enum
import re

class NotebookType(Enum):
    XAA = "cross_app_access"
    AGENT_REGISTRATION = "agent_registration"
    STS = "sts"
    AUTHZ = "authz"
    A2A = "a2a"

if getattr(builtins, "_original_print", None) is None:
    setattr(builtins, "_original_print", builtins.print)

_builtin_print = getattr(builtins, "_original_print")

_PRIMITIVES = (str, int, float, bool, type(None))

def _is_url_encoded(s: str) -> bool:
    if "=" not in s or "\n" in s:
        return False
    try:
        return len(parse_qs(s, strict_parsing=True)) > 0
    except Exception:
        return False

def _smart_print(*args, sep=" ", end="\n", **kwargs):
    plain, complex_args = [], []

    for arg in args:
        if isinstance(arg, _PRIMITIVES):
            plain.append(str(arg))
        else:
            complex_args.append(arg)

    if plain:
        _builtin_print(sep.join(plain), end=end if not complex_args else "\n", **kwargs)
    for arg in complex_args:
        debug_print(type(arg).__name__, arg)

if builtins.print is not _smart_print:
    builtins.print = _smart_print

def debug_print(label: str, data: Any) -> None:
    """
    Safely inspects and pretty-prints any Python object,
    JSON string, or raw byte body.
    """

    indent = "    "
    _builtin_print(f"\n=== DEBUG: {label} ===")

    # 1. Handle Empty or None values
    if data is None or data == "":
        _builtin_print(f"{indent}[Empty or None]")
        return

    # 2. Handle Bytes (convert to string if possible)
    if isinstance(data, bytes):
        try:
            data = data.decode('utf-8')
        except UnicodeDecodeError:
            _builtin_print(f"{indent}[Raw Binary/Bytes data: {len(data)} bytes]")
            return

    # 3. Handle Strings (Check if it's a JSON string)
    if isinstance(data, str):
        # Strip whitespace to check if it looks like JSON
        stripped = data.strip()
        if (stripped.startswith('{') and stripped.endswith('}')) or \
           (stripped.startswith('[') and stripped.endswith(']')):
            try:
                json_data = json.loads(stripped)
                # Success! Print parsed JSON beautifully
                pretty_json = json.dumps(json_data, indent=4)
                # Indent every line for cleaner look
                _builtin_print("\n".join(f"{indent}{line}" for line in pretty_json.splitlines()))
                return
            except (ValueError, TypeError):
                pass # Not valid JSON after all, move to fallback

        # URL-form-encoded string
        if _is_url_encoded(stripped):
            parsed = parse_qs(stripped)
            flat = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
            _builtin_print("\n".join(f"{indent}{line}" for line in json.dumps(flat, indent=4).splitlines()))
            return

        # Regular string fallback
        _builtin_print("\n".join(f"{indent}{line}" for line in data.splitlines()))
        return

    # 4. Handle Python Objects (Dictionaries, Lists, Objects, Dataclasses)
    try:
        # Use standard library pretty printer for native python structures
        pretty_obj = pprint.pformat(data, indent=4, width=80)
        _builtin_print("\n".join(f"{indent}{line}" for line in pretty_obj.splitlines()))
    except Exception as e:
        # Absolute safety net fallback
        _builtin_print(f"{indent}[Fallback to __str__]: {str(data)}")

from okta_client.authfoundation.oauth2.client import OAuth2ClientListener

class Debugger(OAuth2ClientListener):
    _builtin_print("\n" + "=" * 80)
    _builtin_print("DEBUG ENABLED")
    _builtin_print("\n" + "=" * 80)
    def will_send(self, client, request):
        debug_print(f"OAuth Request -> {request.method} {request.url}", request.body)

    def did_send(self, client, request, response):
        debug_print(f"OAuth Response Status", response.status_code)
        debug_print(f"OAuth Response Body", response.result)

    def did_send_error(self, client, request, error):
        debug_print(f"OAuth Error", error)

REQUIRED_KEYS = [
    "OKTA_DOMAIN",
    "REDIRECT_URI",
    "RESOURCE_AUTHZ_SERVER_ID"
]

def validate_config(config: dict, notebook_type: str = "xaa"):
    _notebook_type = NotebookType(notebook_type)
    required_keys = list(REQUIRED_KEYS)

    if _notebook_type == NotebookType.XAA:
        pass
    elif _notebook_type == NotebookType.AGENT_REGISTRATION:
        pass
    elif _notebook_type == NotebookType.STS:
        pass
    elif _notebook_type == NotebookType.AUTHZ:
        required_keys.extend([
            "CLIENT_AUTHZ_SERVER_ID",
            "RESOURCE_URI",
            "PRINCIPAL_ID",
            "CLIENT_ID",
            "RESOURCE_SERVER_AUDIENCE"
        ]);

        if 'CLIENT_SECRET' not in config or not config.get('CLIENT_SECRET'):
            required_keys.append("CLIENT_PRIVATE_JWK");
        else:
            required_keys.append("CLIENT_SECRET");

        if 'PRINCIPAL_SECRET' not in config or not config.get('PRINCIPAL_SECRET'):
            required_keys.append("PRINCIPAL_PRIVATE_JWK");

    elif _notebook_type == NotebookType.A2A:
        pass


    for key in required_keys:
        value = config.get(key);

        if key not in config or not value:
            raise ValueError(f"Missing required configuration key: {key}")

        # Validate OKTA_DOMAIN format
        okta_domain_regex = r"^https:\/\/[a-zA-Z0-9-]+\.(okta|oktapreview|okta-emea)\.com$"

        if key == "OKTA_DOMAIN" and not re.match(okta_domain_regex, value):
            raise ValueError(
                f"Invalid OKTA_DOMAIN: '{value}'. "
                "Expected format: 'https://<your-domain>.<okta|oktapreview|okta-emea>.com'"
            )

        # Validate JWK structure if present
        if 'JWK' in key and (not isinstance(value, dict) or not value.get('kid')):
            raise ValueError(f"{key} must be a dictionary containing at least a 'kid'")