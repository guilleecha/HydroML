from django import template
import json

register = template.Library()


@register.filter
def get_type(value):
    """Get the type name of a value"""
    if isinstance(value, bool):
        return 'boolean'
    elif isinstance(value, int):
        return 'integer'
    elif isinstance(value, float):
        return 'float'
    elif isinstance(value, str):
        return 'string'
    elif isinstance(value, list):
        return 'list'
    elif isinstance(value, dict):
        return 'object'
    else:
        return 'unknown'


@register.filter
def pprint(value):
    """Pretty print JSON with proper formatting"""
    try:
        if isinstance(value, (dict, list)):
            return json.dumps(value, indent=2, ensure_ascii=False)
        elif isinstance(value, str):
            # Try to parse as JSON first
            try:
                parsed = json.loads(value)
                return json.dumps(parsed, indent=2, ensure_ascii=False)
            except (json.JSONDecodeError, TypeError):
                return value
        else:
            return str(value)
    except Exception:
        return str(value)
