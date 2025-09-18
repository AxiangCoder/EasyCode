
import json

def convert_color_to_hex(color_obj):
    """Converts a Sketch color object to a HEX string."""
    if not color_obj:
        return None
    r = int(color_obj.get("red", 0) * 255)
    g = int(color_obj.get("green", 0) * 255)
    b = int(color_obj.get("blue", 0) * 255)
    return f"#{r:02x}{g:02x}{b:02x}".upper()

def parse_semantic_name(name):
    """Parses a semantic name like 'component/button/primary' into a dict."""
    parts = name.split("/")
    if len(parts) < 2:
        return {"type": name, "variant": "default"}
    return {
        "category": parts[0],
        "type": parts[1],
        "variant": parts[2] if len(parts) > 2 else "default",
        "state": parts[3] if len(parts) > 3 else None,
    }
