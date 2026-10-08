"""
Validador de longitud de campos. Respeta estrictamente la Regla NA.
"""

from typing import List
from gis_data_auditor.models.dataset import DatasetInfo
from gis_data_auditor.models.standard import StandardDefinition
from gis_data_auditor.models.validation import IssueCategory, Severity, ValidationIssue
from gis_data_auditor.validators.base_validator import BaseValidator


class FieldLengthValidator(BaseValidator):
    """Compara la longitud definida en el estándar con la longitud real del campo en el SHP."""

    def __init__(self):
        super().__init__(name="FieldLengthValidator")

    def validate(self, dataset: DatasetInfo, standard: StandardDefinition) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []

        for field_key, field_def in standard.fields.items():
            # REGLA CRÍTICA NA: Si no se especificó longitud en el estándar, se omite.
            if not field_def.has_length_spec:
                continue

            real_field = dataset.get_field(field_key)
            if not real_field or real_field.length is None:
                continue

            exp_len = field_def.expected_length
            real_len = real_field.length

            if real_len != exp_len:
                severity = Severity.WARNING if real_len > exp_len else Severity.ERROR
                msg = (
                    f"El campo '{field_def.name}' tiene longitud {real_len}, "
                    f"pero el estándar requiere longitud {exp_len}."
                )

                issue = ValidationIssue(
                    issue_id=f"LENGTH_MISMATCH_{dataset.name}_{field_def.name}",
                    dataset_name=dataset.name,
                    filepath=str(dataset.filepath),
                    schema_id=standard.schema_id,
                    field_name=field_def.name,
                    rule_name=self.name,
                    expected_value=exp_len,
                    found_value=real_len,
                    severity=severity,
                    category=IssueCategory.LONGITUD_INCORRECTA,
                    message=msg,
                    recommendation=f"Ajustar la longitud del campo '{field_def.name}' a {exp_len}."
                )
                issues.append(issue)

        return issues
