from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.filter
def mul(value, arg):
    """
    Multiplie `value` par `arg` en utilisant Decimal pour une précision monétaire.
    """
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError, InvalidOperation):
        return Decimal('0.00')  # Retourne 0.00 en cas d'erreur

@register.filter
def add(value, arg):
    """
    Additionne `value` et `arg` en utilisant Decimal pour une précision monétaire.
    """
    try:
        return Decimal(str(value)) + Decimal(str(arg))
    except (ValueError, TypeError, InvalidOperation):
        return Decimal('0.00')  # Retourne 0.00 en cas d'erreur