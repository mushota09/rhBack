"""
Constantes pour les calculs de paie.
"""
from decimal import Decimal
from django.conf import settings


# Taux et plafonds INSS
INSS_PENSION_RATE = Decimal(str(getattr(settings, 'PAYROLL_CONSTANTS', {}).get('INSS_PENSION_RATE', 0.06)))
INSS_PENSION_CAP = Decimal(str(getattr(settings, 'PAYROLL_CONSTANTS', {}).get('INSS_PENSION_CAP', 27000)))
INSS_RISK_RATE = Decimal(str(getattr(settings, 'PAYROLL_CONSTANTS', {}).get('INSS_RISK_RATE', 0.06)))
INSS_RISK_CAP = Decimal(str(getattr(settings, 'PAYROLL_CONSTANTS', {}).get('INSS_RISK_CAP', 2400)))
INSS_EMPLOYEE_RATE = Decimal(str(getattr(settings, 'PAYROLL_CONSTANTS', {}).get('INSS_EMPLOYEE_RATE', 0.04)))
INSS_EMPLOYEE_CAP = Decimal(str(getattr(settings, 'PAYROLL_CONSTANTS', {}).get('INSS_EMPLOYEE_CAP', 18000)))

# Barème IRE
IRE_BRACKETS = getattr(settings, 'PAYROLL_CONSTANTS', {}).get('IRE_BRACKETS', [
    {'min': 0, 'max': 150000, 'rate': 0.0},
    {'min': 150000, 'max': 300000, 'rate': 0.2},
    {'min': 300000, 'max': float('inf'), 'rate': 0.3},
])

# Barème allocation familiale
FAMILY_ALLOWANCE_SCALE = getattr(settings, 'PAYROLL_CONSTANTS', {}).get('FAMILY_ALLOWANCE_SCALE', [
    {'children': 0, 'amount': 0},
    {'children': 1, 'amount': 5000},
    {'children': 2, 'amount': 10000},
    {'children': 3, 'amount': 15000},
    {'children_additional': 3000},  # Par enfant au-delà de 3
])


def calculate_ire(base_imposable):
    """
    Calcule l'IRE selon le barème progressif.
    """
    ire = 0
    remaining_amount = base_imposable

    for bracket in IRE_BRACKETS:
        if remaining_amount <= 0:
            break

        bracket_min = bracket['min']
        bracket_max = bracket['max']
        bracket_rate = bracket['rate']

        if base_imposable > bracket_min:
            taxable_in_bracket = min(remaining_amount, bracket_max - bracket_min)
            ire += taxable_in_bracket * bracket_rate
            remaining_amount -= taxable_in_bracket

    return round(ire, 2)


def calculate_family_allowance(nombre_enfants):
    """
    Calcule l'allocation familiale selon le barème progressif.
    """
    if nombre_enfants <= 0:
        return 0

    # Chercher dans le barème
    for scale_item in FAMILY_ALLOWANCE_SCALE:
        if 'children' in scale_item and scale_item['children'] == nombre_enfants:
            return scale_item['amount']

    # Si plus de 3 enfants, calcul progressif
    if nombre_enfants > 3:
        base_amount = 15000  # Pour 3 enfants
        additional_children = nombre_enfants - 3
        additional_amount = additional_children * FAMILY_ALLOWANCE_SCALE[-1]['children_additional']
        return base_amount + additional_amount

    return 0


def calculate_inss_contributions(gross_salary, is_employer=True):
    """
    Calcule les cotisations INSS (pension et risque).
    """
    if is_employer:
        # Cotisations patronales
        pension = min(gross_salary * INSS_PENSION_RATE, INSS_PENSION_CAP)
        risk = min(gross_salary * INSS_RISK_RATE, INSS_RISK_CAP)
    else:
        # Cotisations salariales
        pension = min(gross_salary * INSS_EMPLOYEE_RATE, INSS_EMPLOYEE_CAP)
        risk = 0  # Pas de cotisation risque pour l'employé

    return {
        'pension': round(pension, 2),
        'risk': round(risk, 2),
        'total': round(pension + risk, 2)
    }
