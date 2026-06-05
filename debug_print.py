import json
import pprint
from typing import Any

def debug_print(label: str, data: Any) -> None:
    """
    Safely inspects and pretty-prints any Python object, 
    JSON string, or raw byte body.
    """
    indent = "    "
    print(f"\n=== DEBUG: {label} ===")
    
    # 1. Handle Empty or None values
    if data is None or data == "":
        print(f"{indent}[Empty or None]")
        return

    # 2. Handle Bytes (convert to string if possible)
    if isinstance(data, bytes):
        try:
            data = data.decode('utf-8')
        except UnicodeDecodeError:
            print(f"{indent}[Raw Binary/Bytes data: {len(data)} bytes]")
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
                print("\n".join(f"{indent}{line}" for line in pretty_json.splitlines()))
                return
            except (ValueError, TypeError):
                pass # Not valid JSON after all, move to fallback
        
        # Regular string fallback
        print("\n".join(f"{indent}{line}" for line in data.splitlines()))
        return

    # 4. Handle Python Objects (Dictionaries, Lists, Objects, Dataclasses)
    try:
        # Use standard library pretty printer for native python structures
        pretty_obj = pprint.pformat(data, indent=4, width=80)
        print("\n".join(f"{indent}{line}" for line in pretty_obj.splitlines()))
    except Exception as e:
        # Absolute safety net fallback
        print(f"{indent}[Fallback to __str__]: {str(data)}")
