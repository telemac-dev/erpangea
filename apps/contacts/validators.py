import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def clean_doc_digits(value):
    if not value:
        return ""
    return re.sub(r'\D', '', str(value))

def validate_cpf(cpf):
    """
    Valida dígitos verificadores de CPF (11 dígitos).
    """
    digits = clean_doc_digits(cpf)
    if len(digits) != 11:
        raise ValidationError(_("CPF deve conter exatamente 11 dígitos numéricos."))
    
    # Rejeita CPFs com todos os dígitos iguais (ex: 111.111.111-11)
    if digits == digits[0] * 11:
        raise ValidationError(_("Número de CPF inválido (dígitos repetidos)."))

    # Primeiro dígito verificador
    soma = sum(int(digits[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    d1 = 0 if resto == 10 else resto
    if int(digits[9]) != d1:
        raise ValidationError(_("Dígito verificador do CPF inválido."))

    # Segundo dígito verificador
    soma = sum(int(digits[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    d2 = 0 if resto == 10 else resto
    if int(digits[10]) != d2:
        raise ValidationError(_("Dígito verificador do CPF inválido."))

    return True

def validate_cnpj(cnpj):
    """
    Valida dígitos verificadores de CNPJ (14 dígitos).
    """
    digits = clean_doc_digits(cnpj)
    if len(digits) != 14:
        raise ValidationError(_("CNPJ deve conter exatamente 14 dígitos numéricos."))

    # Rejeita CNPJs com todos os dígitos iguais
    if digits == digits[0] * 14:
        raise ValidationError(_("Número de CNPJ inválido (dígitos repetidos)."))

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(digits[i]) * pesos1[i] for i in range(12))
    resto = soma % 11
    d1 = 0 if resto < 2 else 11 - resto
    if int(digits[12]) != d1:
        raise ValidationError(_("Dígito verificador do CNPJ inválido."))

    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(digits[i]) * pesos2[i] for i in range(13))
    resto = soma % 11
    d2 = 0 if resto < 2 else 11 - resto
    if int(digits[13]) != d2:
        raise ValidationError(_("Dígito verificador do CNPJ inválido."))

    return True

def format_document(doc_number, doc_type='CNPJ'):
    digits = clean_doc_digits(doc_number)
    if doc_type == 'CPF' and len(digits) == 11:
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
    elif doc_type == 'CNPJ' and len(digits) == 14:
        return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"
    return doc_number
