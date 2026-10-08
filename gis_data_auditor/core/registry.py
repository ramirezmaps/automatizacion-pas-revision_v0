"""
Registro central de validadores habilitados en el sistema.
"""

from typing import List
from gis_data_auditor.validators.base_validator import BaseValidator
from gis_data_auditor.validators.field_length_validator import FieldLengthValidator
from gis_data_auditor.validators.field_scale_validator import FieldScaleValidator
from gis_data_auditor.validators.field_type_validator import FieldTypeValidator
from gis_data_auditor.validators.integrity_validator import IntegrityValidator
from gis_data_auditor.validators.schema_validator import SchemaValidator


class ValidatorRegistry:
    """Maneja los validadores registrados para la ejecución de la auditoría."""

    def __init__(self):
        self._validators: List[BaseValidator] = []
        self._load_default_validators()

    def _load_default_validators(self) -> None:
        """Carga los validadores por defecto de la versión 1.0."""
        self._validators = [
            IntegrityValidator(),
            SchemaValidator(),
            FieldTypeValidator(),
            FieldLengthValidator(),
            FieldScaleValidator()
        ]

    def register_validator(self, validator: BaseValidator) -> None:
        """Permite agregar un nuevo validador personalizado dinámicamente."""
        self._validators.append(validator)

    def get_active_validators(self) -> List[BaseValidator]:
        """Retorna la lista de validadores que se encuentran habilitados."""
        return [v for v in self._validators if v.enabled]
