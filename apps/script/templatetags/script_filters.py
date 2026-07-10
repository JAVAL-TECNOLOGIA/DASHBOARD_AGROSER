from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """
    Permite hacer lookup dinámico en diccionarios desde templates
    Uso: {{ perms|lookup:modulo.permiso }}
    """
    if hasattr(dictionary, key):
        return getattr(dictionary, key)
    
    # Para permisos anidados como 'script.MODULO_APROBACIONES_DONLUIS_FITOSANIDAD'
    keys = key.split('.')
    value = dictionary
    
    try:
        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            else:
                return False
        return value
    except (AttributeError, KeyError):
        return False