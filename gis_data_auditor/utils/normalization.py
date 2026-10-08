"""
Utilidades para la normalización de textos, valores NA y conversión de tipos.
"""

from typing import Any, Optional
from gis_data_auditor.config.settings import NA_VALUES


def normalize_string(val: Any) -> str:
    """Normaliza un texto eliminando espacios sobrantes."""
    if val is None:
        return ""
    return str(val).strip()


def is_na_value(val: Any) -> bool:
    """
    Evalúa si un valor representa un estado 'NA' / No Especificado en el Excel.
    Reconoce variantes como 'NA', 'na', 'Na', valores nulos o celdas vacías.
    """
    if val is None:
        return True
    cleaned = str(val).strip().upper()
    return cleaned in NA_VALUES


def parse_optional_int(val: Any) -> Optional[int]:
    """
    Convierte un valor a un entero opcional.
    Si es un valor NA o vacío, retorna None.
    NO convierte NA a cero.
    """
    if is_na_value(val):
        return None
    
    try:
        # En caso de que venga como float desde pandas/openpyxl (ej: 5.0)
        float_val = float(str(val).strip())
        return int(float_val)
    except (ValueError, TypeError):
        return None
