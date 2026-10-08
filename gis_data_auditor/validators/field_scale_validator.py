"""
Validador de escala/decimales esperados. Respeta estrictamente la Regla NA.
"""

from typing import List
from gis_data_auditor.models.dataset import DatasetInfo
from gis_data_auditor.models.standard import StandardDefinition
from gis_data_auditor.models.validation import IssueCategory, Severity, ValidationIssue
from gis_data_auditor.validators.base_validator import BaseValidator


class FieldScaleValidator(BaseValidator):
    """Compara la cantidad esperada de decimales/escala contra la del SHP real."""

    def __init__(self):
        super().__init__(name="FieldScaleValidator")

    def validate(self, dataset: DatasetInfo, standard: StandardDefinition) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []

        for field_key, field_def in standard.fields.items():
            # REGLA CRÍTICA NA: Si decimales es NA o vacío, no validar decimales.
            if not field_def.has_decimals_spec:
                continue

            real_field = dataset.get_field(field_key)
            if not real_field:
                continue

            exp_scale = field_def.expected_decimals
            real_scale = real_field.scale

            if real_scale is None:
                # Si la información de decimales no se puede extraer del formato
                issue = ValidationIssue(
                    issue_id=f"SCALE_UNVERIFIABLE_{dataset.name}_{field_def.name}",
                    dataset_name=dataset.name,
                    filepath=str(dataset.filepath),
                    schema_id=standard.schema_id,
                    field_name=field_def.name,
                    rule_name=self.name,
                    expected_value=exp_scale,
                    found_value="NO_VERIFICABLE",
                    severity=Severity.INFO,
                    category=IssueCategory.ESCALA_INCORRECTA,
                    message=f"La escala del campo '{field_def.name}' no es directamente verificable en este formato.",
                    recommendation="Revisar manualmente los decimales almacenados en la tabla de atributos."
                )
                issues.append(issue)
            elif real_scale != exp_scale:
                issue = ValidationIssue(
                    issue_id=f"SCALE_MISMATCH_{dataset.name}_{field_def.name}",
                    dataset_name=dataset.name,
                    filepath=str(dataset.filepath),
                    schema_id=standard.schema_id,
                    field_name=field_def.name,
                    rule_name=self.name,
                    expected_value=exp_scale,
                    found_value=real_scale,
                    severity=Severity.WARNING,
                    category=IssueCategory.ESCALA_INCORRECTA,
                    message=(
                        f"El campo '{field_def.name}' tiene escala {real_scale}, "
                        f"pero el estándar requiere {exp_scale} decimales."
                    ),
                    recommendation=f"Ajustar la escala del campo '{field_def.name}' a {exp_scale}."
                )
                issues.append(issue)

        return issues
