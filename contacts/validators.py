import re
from django.core.exceptions import ValidationError

def validate_cpf_digits(cpf_str: str) -> str:
    """Valida número de CPF usando o algoritmo oficial de dígitos verificadores."""
    if not cpf_str:
        return cpf_str

    digits = re.sub(r'\D', '', str(cpf_str))
    
    if len(digits) != 11:
        raise ValidationError('CPF inválido. Informe um número de CPF válido com 11 dígitos.')
        
    if len(set(digits)) == 1:
        raise ValidationError('CPF inválido. Dígitos não podem ser todos iguais.')

    # Primeiro dígito verificador
    s = sum(int(digits[i]) * (10 - i) for i in range(9))
    d1 = (s * 10) % 11
    if d1 == 10:
        d1 = 0
    if d1 != int(digits[9]):
        raise ValidationError('CPF inválido. Dígitos verificadores não conferem.')

    # Segundo dígito verificador
    s = sum(int(digits[i]) * (11 - i) for i in range(10))
    d2 = (s * 10) % 11
    if d2 == 10:
        d2 = 0
    if d2 != int(digits[10]):
        raise ValidationError('CPF inválido. Dígitos verificadores não conferem.')

    return digits


def validate_cnpj_digits(cnpj_str: str) -> str:
    """Valida número de CNPJ usando o algoritmo oficial de dígitos verificadores."""
    if not cnpj_str:
        return cnpj_str

    digits = re.sub(r'\D', '', str(cnpj_str))
    
    if len(digits) != 14:
        raise ValidationError('CNPJ inválido. Informe um número de CNPJ válido com 14 dígitos.')
        
    if len(set(digits)) == 1:
        raise ValidationError('CNPJ inválido. Dígitos não podem ser todos iguais.')

    # Primeiro dígito verificador
    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    s1 = sum(int(digits[i]) * weights1[i] for i in range(12))
    r1 = s1 % 11
    d1 = 0 if r1 < 2 else 11 - r1
    if d1 != int(digits[12]):
        raise ValidationError('CNPJ inválido. Dígitos verificadores não conferem.')

    # Segundo dígito verificador
    weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    s2 = sum(int(digits[i]) * weights2[i] for i in range(13))
    r2 = s2 % 11
    d2 = 0 if r2 < 2 else 11 - r2
    if d2 != int(digits[13]):
        raise ValidationError('CNPJ inválido. Dígitos verificadores não conferem.')

    return digits


def validate_cep_digits(cep_str: str) -> str:
    """Valida formato de CEP."""
    if not cep_str:
        return cep_str
        
    digits = re.sub(r'\D', '', str(cep_str))
    if len(digits) != 8:
        raise ValidationError('CEP inválido. Informe um CEP com 8 dígitos.')
    return digits
