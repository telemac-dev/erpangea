from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='currency_br')
def currency_br(value):
    """
    Formata valores numéricos para o padrão brasileiro (R$ 1.234.567,89).
    Exemplo: 1234567.89 -> "1.234.567,89"
    """
    if value is None or value == '':
        return "0,00"
    
    try:
        val = Decimal(str(value))
        formatted = f"{val:,.2f}"
        formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
        return formatted
    except Exception:
        return str(value)
