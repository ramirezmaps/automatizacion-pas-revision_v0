"""
Validador de compatibilidad de tipos de datos entre el Estándar y el Shapefile real.
"""

from typing import List, Set
from gis_data_auditor.models.dataset import DatasetInfo
from gis_data_auditor.models.standard import StandardDefinition
from gis_data_auditor.models.validation import IssueCategory, Severity, ValidationIssue
from gis_data_auditor.validators.base_validator import BaseValidator


class FieldTypeValidator(BaseValidator):
    """Compara el tipo de dato especificado en el estándar con el tipo real reportado por el GIS."""

    TYPE_MAPPING = {
        "CHARACTER": {"STRING", "TEXT", "STR", "CHARACTER"},
        "NUMERIC": {"DOUBLE", "SINGLE", "FLOAT", "NUMERIC", "DECIMAL", "INTEGER", "SMALLINTEGER", "LONG"}, # numeric admite flotante y entero
        "INTEGER": {"INTEGER", "SMALLINTEGER", "INT", "LONG"},
        "DATE": {"DATE", "DATETIME"}
    }

    def __init__(self):
        super().__init__(name="FieldTypeValidator")

    def validate(self, dataset: DatasetInfo, standard: StandardDefinition) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []

        for field_key, field_def in standard.fields.items():
            real_field = dataset.get_field(field_key)
            if not real_field:
                continue  # SchemaValidator ya reporta campos faltantes

            exp_type_norm = field_def.expected_type.strip().upper()
            real_type_norm = real_field.type_name.strip().upper()

            allowed_types: Set[str] = self.TYPE_MAPPING.get(exp_type_norm, {exp_type_norm})

            if real_type_norm not in allowed_types:
                issue = ValidationIssue(
                    issue_id=f"TYPE_MISMATCH_{dataset.name}_{field_def.name}",
                    dataset_name=dataset.name,
                    filepath=str(dataset.filepath),
                    schema_id=standard.schema_id,
                    field_name=field_def.name,
                    rule_name=self.name,
                    expected_value=field_def.expected_type,
                    found_value=real_field.type_name,
                    severity=Severity.ERROR,
                    category=IssueCategory.TIPO_INCORRECTO,
                    message=(
                        f"El campo '{field_def.name}' tiene tipo '{real_field.type_name}', "
                        f"pero se esperaba tipo '{field_def.expected_type}'."
                    ),
                    recommendation=f"Modificar el tipo del campo '{field_def.name}' a '{field_def.expected_type}'."
                )
                issues.append(issue)

        return issues
