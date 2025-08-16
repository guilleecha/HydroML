import json
import pprint
from django import template

register = template.Library()

@register.filter
def pprint(value):
    """
    Format a value with pretty print for better readability in templates.
    """
    if value is None:
        return ""
    
    try:
        # If it's a string that looks like JSON, try to parse and format it
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                return json.dumps(parsed, indent=2, ensure_ascii=False)
            except (json.JSONDecodeError, ValueError):
                return str(value)
        
        # For dictionaries and lists, use pretty print
        if isinstance(value, (dict, list)):
            return pprint.pformat(value, indent=2, width=80)
        
        # For other types, convert to string
        return str(value)
    except Exception:
        return str(value)


@register.filter
def abs(value):
    """
    Return the absolute value of a number.
    """
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return value


@register.filter
def sub(value, arg):
    """
    Subtract arg from value.
    """
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value


@register.filter
def mul(value, arg):
    """
    Multiply value by arg.
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value


@register.filter
def lookup(d, key):
    """Template filter to look up a dictionary value by key"""
    if hasattr(d, 'get'):
        return d.get(key, '')
    return ''
