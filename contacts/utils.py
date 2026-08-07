import re

def validate_cpf(cpf_str: str) -> bool:
    """Valida número de CPF usando o algoritmo oficial de dígitos verificadores."""
    digits = re.sub(r'\D', '', str(cpf_str))
    
    if len(digits) != 11:
        return False
        
    # Rejeita CPFs com todos os dígitos iguais
    if len(set(digits)) == 1:
        return False

    # Primeiro dígito verificador
    s = sum(int(digits[i]) * (10 - i) for i in range(9))
    d1 = (s * 10) % 11
    if d1 == 10:
        d1 = 0
    if d1 != int(digits[9]):
        return False

    # Segundo dígito verificador
    s = sum(int(digits[i]) * (11 - i) for i in range(10))
    d2 = (s * 10) % 11
    if d2 == 10:
        d2 = 0
    if d2 != int(digits[10]):
        return False

    return True


def validate_cnpj(cnpj_str: str) -> bool:
    """Valida número de CNPJ usando o algoritmo oficial de dígitos verificadores."""
    digits = re.sub(r'\D', '', str(cnpj_str))
    
    if len(digits) != 14:
        return False
        
    # Rejeita CNPJs com todos os dígitos iguais
    if len(set(digits)) == 1:
        return False

    # Primeiro dígito verificador
    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    s1 = sum(int(digits[i]) * weights1[i] for i in range(12))
    r1 = s1 % 11
    d1 = 0 if r1 < 2 else 11 - r1
    if d1 != int(digits[12]):
        return False

    # Segundo dígito verificador
    weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    s2 = sum(int(digits[i]) * weights2[i] for i in range(13))
    r2 = s2 % 11
    d2 = 0 if r2 < 2 else 11 - r2
    if d2 != int(digits[13]):
        return False

    return True


def format_cpf(digits_str: str) -> str:
    """Formata 11 dígitos de CPF no padrão 123.456.789-00."""
    d = re.sub(r'\D', '', str(digits_str))
    if len(d) == 11:
        return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"
    return digits_str


def format_cnpj(digits_str: str) -> str:
    """Formata 14 dígitos de CNPJ no padrão 12.345.678/0001-12."""
    d = re.sub(r'\D', '', str(digits_str))
    if len(d) == 14:
        return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"
    return digits_str


def format_cep(digits_str: str) -> str:
    """Formata 8 dígitos de CEP no padrão 01001-000."""
    d = re.sub(r'\D', '', str(digits_str))
    if len(d) == 8:
        return f"{d[:5]}-{d[5:]}"
    return digits_str
