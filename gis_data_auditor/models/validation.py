"""
Modelos de datos para representar incidencias, errores y advertencias.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class Severity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class IssueCategory(str, Enum):
    CAMPO_FALTANTE = "CAMPO_FALTANTE"
    CAMPO_ADICIONAL = "CAMPO_ADICIONAL"
    CAMPO_ADICIONAL_SISTEMA = "CAMPO_ADICIONAL_SISTEMA"
    TIPO_INCORRECTO = "TIPO_INCORRECTO"
    LONGITUD_INCORRECTA = "LONGITUD_INCORRECTA"
    ESCALA_INCORRECTA = "ESCALA_INCORRECTA"
    ERROR_LECTURA = "ERROR_LECTURA"
    ASOCIACION_AMBIGUA = "ASOCIACION_AMBIGUA"
    SIN_ESQUEMA = "SIN_ESQUEMA"
    CONFIGURACION_ESTANDAR = "CONFIGURACION_ESTANDAR"


@dataclass
class ValidationIssue:
    """Representa una incidencia detectada durante la auditoría."""
    issue_id: str
    dataset_name: str
    filepath: str
    schema_id: str
    field_name: str
    rule_name: str
    expected_value: Any
    found_value: Any
    severity: Severity
    category: IssueCategory
    message: str
    technical_details: Optional[str] = ""
    recommendation: Optional[str] = ""
