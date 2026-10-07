from decimal import Decimal, InvalidOperation
from django import template

register = template.Library()

def parse_decimal_br(value):
    """
    Converte qualquer representação numérica ou string em Decimal padrão brasileiro.
    Suporta:
      - '1.234,56' -> Decimal('1234.56')
      - '1234,56' -> Decimal('1234.56')
      - '1234.56' -> Decimal('1234.56')
      - 'R$ 42.000,00' -> Decimal('42000.00')
      - 42000 -> Decimal('42000.00')
    """
    if value is None or value == "":
        return Decimal("0.00")
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    
    val_str = str(value).strip().replace("R$", "").replace("r$", "").strip()
    if not val_str:
        return Decimal("0.00")
    
    # Se contém ponto e vírgula (ex: 1.234,56), remove pontos de milhar e troca vírgula decimal por ponto
    if "." in val_str and "," in val_str:
        val_str = val_str.replace(".", "").replace(",", ".")
    # Se contém apenas vírgula (ex: 1234,56), troca vírgula decimal por ponto
    elif "," in val_str:
        val_str = val_str.replace(",", ".")
    
    try:
        return Decimal(val_str)
    except (InvalidOperation, ValueError):
        return Decimal("0.00")


@register.filter(name="currency_br")
def currency_br(value):
    """
    Formata valores monetários no padrão brasileiro oficial:
    Exemplo: 42000.00 -> 'R$ 42.000,00'
             1234.56  -> 'R$ 1.234,56'
    """
    if value is None or value == "":
        return "R$ 0,00"
    try:
        dec = parse_decimal_br(value)
        # Formata com separador de milhar americano e depois inverte
        # 1234567.89 -> 1,234,567.89 -> 1.234.567,89
        parts = f"{dec:,.2f}".split(".")
        integer_part = parts[0].replace(",", ".")
        decimal_part = parts[1]
        return f"R$ {integer_part},{decimal_part}"
    except Exception:
        return f"R$ {value}"


@register.filter(name="number_br")
def number_br(value):
    """
    Formata números no padrão brasileiro sem o prefixo R$:
    Exemplo: 42000.00 -> '42.000,00'
    """
    if value is None or value == "":
        return "0,00"
    try:
        dec = parse_decimal_br(value)
        parts = f"{dec:,.2f}".split(".")
        integer_part = parts[0].replace(",", ".")
        decimal_part = parts[1]
        return f"{integer_part},{decimal_part}"
    except Exception:
        return str(value)
