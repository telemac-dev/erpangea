import re
from django import template

register = template.Library()

@register.filter(name='format_phone_br')
def format_phone_br(value):
    """
    Formata numero de telefone para o padrao brasileiro:
    - Celular (11 digitos): (99) 9 9999-9999
    - Fixo (10 digitos): (99) 9999-9999
    Retorna o valor original caso nao coincida com a quantidade de digitos esperada.
    """
    if not value:
        return ""
    
    # Extrai apenas os digitos numericos
    digits = re.sub(r'\D', '', str(value))
    
    # 11 digitos (Celular com 9 digitos: DDD + 9 + 8 digitos)
    if len(digits) == 11:
        return f"({digits[:2]}) {digits[2]} {digits[3:7]}-{digits[7:]}"
    
    # 10 digitos (Telefone fixo: DDD + 8 digitos)
    elif len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    
    # Retorna o valor original caso seja outro formato (ex: ramal ou internacional)
    return value
