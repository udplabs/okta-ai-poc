import json
import pprint
import time
from datetime import datetime
from typing import Any
import builtins
from urllib.parse import parse_qs, urlparse
from enum import Enum
import re
import jwt
from IPython.display import HTML, display

def render_button(href: str, url: str | None = None, instruction: str = "", cta: str = "Click Here to Authenticate") -> None:

    display(HTML(f"""
        <div style="margin: 20px 0; color: red; padding: 15px; background-color: #ffcdcd; border-left: 4px solid #ff0000; border-radius: 4px;">
            <strong>Instructions:</strong>
            {instruction if instruction else f"""
            <ol style="margin: 10px 0 0 0;">
                <li>Click the button below to open the authorization URL in a new tab</li>
                <li>Sign in with your Okta credentials</li>
                <li>After authentication, you'll be redirected to: <code>{url}</code></li>
                <li>Copy the <strong>code</strong> parameter from the URL (it will look like: <code>?code=ABC123...</code>)</li>
                <li>Paste the code in the next cell to exchange it for tokens</li>
            </ol>
            """}
        </div>
        <div style="margin: 20px 0;">
            <a href="{href}" target="_blank" style="
                display: inline-block;
                padding: 15px 30px;
                background-color: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 16px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            ">{cta}</a>
        </div>
        """))

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

    def will_exchange_token_for_id_jag(self, flow, subject_token_type):
        debug_print(f"OAuth Request -> Subject Token Type: {subject_token_type}", None)

    def did_exchange_token_for_id_jag(self, flow, subject_token_type, id_token):
        debug_print(f"OAuth Response -> Subject Token Type: {subject_token_type}", id_token)

    def will_exchange_id_jag_for_access_token(self, flow, subject_token_type):
        debug_print(f"OAuth Request -> Subject Token Type: {subject_token_type}", None)

    def did_exchange_id_jag_for_access_token(self, flow, subject_token_type, access_token):
        debug_print(f"OAuth Response -> Subject Token Type: {subject_token_type}", access_token)


REQUIRED_KEYS = [
    "OKTA_DOMAIN",
    "PRINCIPAL_ID",
    "REDIRECT_URI",
    "RESOURCE_ISSUER",
    "RESOURCE_SERVER_AUDIENCE"
]

KNOWN_URL_KEYS = {
    "REDIRECT_URI",
    "RESOURCE_URI"
}

def _is_valid_url(val: Any) -> bool:
    if not isinstance(val, str) or not val.strip():
        return False
    try:
        parsed = urlparse(val.strip())
        return bool(parsed.scheme in ("http", "https") and parsed.netloc)
    except Exception:
        return False


def get_issuer(okta_domain: str, val: str = '', default_val: str = '') -> str:
    auth_server_id_regex = r"^[a-zA-Z0-9-]{20}$";

    if not _is_valid_url(val) and re.match(auth_server_id_regex, val):
        return f"{okta_domain}/oauth2/{val}"
    return val if val else default_val


def validate_config(config: dict, notebook_type: str = "xaa"):
    _notebook_type = NotebookType(notebook_type);
    required_keys = list(REQUIRED_KEYS);

    print("⏳ Validating configuration...");

    if _notebook_type == NotebookType.XAA or _notebook_type == NotebookType.AUTHZ:

        if 'PRINCIPAL_SECRET' not in config or not config.get('PRINCIPAL_SECRET'):

            required_keys.append("PRINCIPAL_PRIVATE_JWK");
        else:
            print("  ⚠️ PRINCIPAL configured for client secret. This is not a recommended method of authentication!");

            required_keys.append("PRINCIPAL_SECRET");

    elif _notebook_type == NotebookType.AGENT_REGISTRATION:
        pass
    elif _notebook_type == NotebookType.A2A:

        required_keys.remove("PRINCIPAL_ID");
        required_keys.extend([
            "PRINCIPAL_A_ID",
            "DOMAIN_A_ISSUER",
            "PRINCIPAL_A_SCOPES",
            "PRINCIPAL_B_ID",
            "DOMAIN_B_ISSUER",
            "PRINCIPAL_B_SCOPES",
        ]);

        if 'PRINCIPAL_A_SECRET' not in config or not config.get('PRINCIPAL_A_SECRET'):

            required_keys.append("PRINCIPAL_A_PRIVATE_JWK");
        else:
            print("  ⚠️ PRINCIPAL configured for client secret. This is not a recommended method of authentication!");

            required_keys.append("PRINCIPAL_A_SECRET");

        if 'PRINCIPAL_B_SECRET' not in config or not config.get('PRINCIPAL_B_SECRET'):

            required_keys.append("PRINCIPAL_B_PRIVATE_JWK");
        else:
            print("  ⚠️ PRINCIPAL configured for client secret. This is not a recommended method of authentication!");

            required_keys.append("PRINCIPAL_B_SECRET");

    elif _notebook_type == NotebookType.STS:
        required_keys.append("RESOURCE_INDICATOR");

        if 'RESOURCE_ISSUER' in required_keys:
            required_keys.remove("RESOURCE_ISSUER");

        if 'RESOURCE_SERVER_AUDIENCE' in required_keys:
            required_keys.remove("RESOURCE_SERVER_AUDIENCE");

    elif _notebook_type == NotebookType.AUTHZ:
        required_keys.extend([
            "CLIENT_AUTHZ_SERVER_ID",
            "RESOURCE_URI",
            "CLIENT_ID"
        ]);

        if 'CLIENT_SECRET' not in config or not config.get('CLIENT_SECRET'):

            required_keys.append("CLIENT_PRIVATE_JWK");
        else:
            print("  ⚠️ CLIENT configured for client secret. This is not a recommended method of authentication!");

            required_keys.append("CLIENT_SECRET");

    elif _notebook_type == NotebookType.A2A:
        pass


    for key in required_keys:
        value = config.get(key);

        # Validate JWK structure if present
        if 'JWK' in key and (not isinstance(value, dict) or not value.get('kid')):
            raise ValueError(f"{key} must be a dictionary containing at least a 'kid'");

        # Validate OKTA_DOMAIN format
        okta_domain_regex = r"^https:\/\/[a-zA-Z0-9-]+\.(okta|oktapreview|okta-emea)\.com$";

        if key == "OKTA_DOMAIN":
            if not isinstance(value, str) or not re.match(okta_domain_regex, value):
                raise ValueError(
                    f"Invalid OKTA_DOMAIN: '{value}'. "
                    "Expected format: 'https://<your-domain>.<okta|oktapreview|okta-emea>.com'"
                )

        elif (key in KNOWN_URL_KEYS or key.endswith(("_URI", "_URL"))) and not _is_valid_url(value):
            raise ValueError(
                f"Invalid URL for configuration key '{key}': '{value}'. "
                "Expected a valid HTTP/HTTPS URL (e.g., 'https://...')"
            );

        if key not in config or not value:
            raise ValueError(f"Missing required configuration key: {key}");

        print(f"  ☑️ {key}");

def _auth_method(private_jwk: dict | None, client_secret: str | None) -> str:
    if private_jwk and isinstance(private_jwk, dict) and private_jwk.get("kid"):
        return f"Private Key KID: {private_jwk.get('kid')}"
    elif client_secret:
        return f"Client Secret: {'*' * 9}..."
    else:
        return "⚠️ NONE — configure a JWK or secret"

def a2a_config_out(config: dict, header: str = "✅ All configuration variables validated successfully!") -> None:
    """
    Outputs the A2A configuration in a structured format to remove unnecessary code from the learning notebook.
    """
    print(f"\n{header}")

    print("Delegation chain:")
    print(f"   User → {config.get('CLIENT_ID') or '❓'} (Client App) → {config.get('PRINCIPAL_A_ID') or '❓'} (Agent A) → {config.get('PRINCIPAL_B_ID') or '❓'} (Agent B) → {config.get('RESOURCE_SERVER_AUDIENCE') or '❓'}\n")

    print(f"Okta Domain: {config.get('OKTA_DOMAIN')}")

    print("Client (App)")
    print(f"   Client ID:  {config.get('CLIENT_ID')}")
    print(f"   Issuer:     {config.get('DOMAIN_A_ISSUER')}")
    print(f"   Scopes:     {config.get('CLIENT_SCOPES')}")
    print(f"   Auth:       {_auth_method(config.get('CLIENT_PRIVATE_JWK'), config.get('CLIENT_SECRET'))}\n")

    print("Agent A  (acting on behalf of the user)")
    print(f"   Principal:  {config.get('PRINCIPAL_A_ID')}")
    print(f"   Issuer:     {config.get('DOMAIN_A_ISSUER')}")
    print(f"   Audience:   {config.get('PRINCIPAL_A_RESOURCE_URI')}")
    print(f"   Scopes:     {config.get('PRINCIPAL_A_SCOPES')}")
    print(f"   Auth:       {_auth_method(config.get('PRINCIPAL_A_PRIVATE_JWK'), config.get('PRINCIPAL_A_SECRET'))}\n")

    print("Agent B  (acting on behalf of Agent A)")
    print(f"   Principal:  {config.get('PRINCIPAL_B_ID')}")
    print(f"   Issuer:     {config.get('DOMAIN_B_ISSUER')}")
    print(f"   Audience:   {config.get('PRINCIPAL_B_RESOURCE_URI')}")
    print(f"   Scopes:     {config.get('PRINCIPAL_B_SCOPES')}")
    print(f"   Auth:       {_auth_method(config.get('PRINCIPAL_B_PRIVATE_JWK'), config.get('PRINCIPAL_B_SECRET'))}\n")

    print("Resource")
    print(f"   Issuer:     {config.get('RESOURCE_ISSUER')}")
    print(f"   Audience:   {config.get('RESOURCE_SERVER_AUDIENCE')}")

_TOKEN_LABELS = {
    "id_token": "ID Token",
    "access_token": "Access Token",
    "refresh_token": "Refresh Token",
    "id_jag": "ID-JAG Token"
}

_DEFAULT_CLAIMS = {
    "id_token": ["iss", "aud", "sub", "email", "name", "exp"],
    "access_token": ["iss", "aud", "resource", "sub", "cid", "scp", "exp"],
    "id_jag": ["iss", "aud", "resource", "sub", "sub_id", "sub_profile", "client_id", "scope", "actor", "aud_sub", "exp"],
}

_HELPER_TEXT = {
    "delimiter": "      ⬅️ ",
    "id_jag": {
        "iss": "The IDP that issued the original token(s).",
        "aud": "The authorization server URL for the resource being accessed. This represents WHO will validate the ID-JAG.",
        "sub": "The IDPs user identifier and subject of the token.",
        "sub_id": "The RESOURCE SERVER's identifier for the user if a different name-space than `sub` is used. Typically only applicable w/ SAML SSO.",
        "client_id": "The RESOURCE SERVER's identifier for the client that is making the request. Typically this would be the currently acting agent's client ID.",
        "resource": "The canonical URL of the resource server that the ID-JAG is intended for. This represents WHAT the token is meant to access.",
        "scope": "The scopes requested by the client for the resource server. This represents what the token should be allowed to do.",
        "aud_sub": "The RESOURCE SERVER's unique identifier for the user if different from `sub`.",
    },
}

def _format_claim(claim: str, value: Any) -> str:
    if claim in ("exp", "iat") and isinstance(value, (int, float)):
        stamp = datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S")
        remaining = int(value - time.time())

        if claim == "iat":
            return stamp

        return f"{stamp}  ·  {remaining // 60}m {remaining % 60}s remaining" if remaining > 0 else f"{stamp}  ·  EXPIRED"

    if isinstance(value, (list, tuple)):
        return " ".join(str(v) for v in value)

    return str(value)

def print_claims(claims: dict, title: str = "Token Claims", output_claims: list = [], helper_text: dict | None = None) -> None:
    """
    Prints selected JWT claims with their human-readable names. Claims absent from the token are skipped.
    """

    present = [claim for claim in output_claims if claim in claims]

    print(f"\n{title}")

    if not present:
        print("   (none of the requested claims are present)")
        return

    labels = {claim: claim for claim in present}
    width = max(len(label) for label in labels.values())

    for claim in present:
        output = f"   {labels[claim].ljust(width)}   {_format_claim(claim, claims.get(claim))}"
        if helper_text and claim in helper_text:
            print(f"{output}{_HELPER_TEXT.get('delimiter', '      ⬅️ ')}{helper_text[claim]}")
        else:
            print(output)

def token_exchange_out(
    token: Any,
    focus: str = "id_token",
    expected_issuer: str | None = None,
    output_claims: list | None = None,
) -> None:
    """
    Summarizes an authorization code exchange for a training notebook.

    `focus` names the user token type the notebook utilizes ('id_token' or 'access_token');
    """
    if focus not in _TOKEN_LABELS:
        raise ValueError(f"focus must be one of {list(_TOKEN_LABELS)}, got '{focus}'")

    returned = {
        "id_token": getattr(token.id_token, "raw", None),
        "access_token": token.access_token,
        "refresh_token": token.refresh_token,
    }

    print("✅ Token exchange successful!\n")

    print("\nTokens Returned:")
    width = max(len(label) for label in _TOKEN_LABELS.values())

    if focus == "id_jag":
        returned = {
            "id_jag": token.access_token
        }

    for name, value in returned.items():
        label = _TOKEN_LABELS[name].ljust(width)

        if not value:
            hint = "   (request the 'offline_access' scope to receive one)" if name == "refresh_token" else ""
            print(f"   ❌ {label}   not returned{hint}")
        elif name == "refresh_token":
            print(f"   ✅ {label}   {value[:24]}…")
        else:
            print(f"   ✅ {label}   https://jwt.io#token={value}")

    focus_label = _TOKEN_LABELS[focus]
    focus_token = returned[focus]

    if not focus_token:
        print(f"\n⚠️ No {focus_label.lower()} was returned, so the next step has nothing to exchange.")
        return

    decoded = jwt.decode(focus_token, options={"verify_signature": False})

    print_claims(
        decoded,
        title=f"{focus_label} Claims  (decoded for display — signature NOT verified)",
        output_claims=output_claims or _DEFAULT_CLAIMS.get(focus),
        helper_text=_HELPER_TEXT.get(focus, {})
    )

    if expected_issuer:
        if decoded.get("iss") == expected_issuer:
            print(f"\n✅ Issued by the expected authorization server: {expected_issuer}")
        else:
            print(f"\n⚠️ Unexpected issuer: {decoded.get('iss')}")
            print(f"   Expected: {expected_issuer}")
