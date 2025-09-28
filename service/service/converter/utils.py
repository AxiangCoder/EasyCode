

def generate_html_from_dsl(dsl: dict) -> str:
    """
    Generates a simple HTML preview from a DSL dictionary.
    This is a placeholder and should be implemented with a proper renderer.
    """
    # Basic implementation for now
    import json
    pretty_dsl = json.dumps(dsl, indent=2, ensure_ascii=False)
    return f"<pre><code>{pretty_dsl}</code></pre>"
