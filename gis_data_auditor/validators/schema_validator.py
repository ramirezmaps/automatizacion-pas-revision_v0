"""
Validador de presencia de campos (Campos faltantes y campos adicionales).
"""

from typing import List
from gis_data_auditor.config.settings import SYSTEM_FIELDS
from gis_data_auditor.models.dataset import DatasetInfo
from gis_data_auditor.models.standard import StandardDefinition
from gis_data_auditor.models.validation import IssueCategory, Severity, ValidationIssue
from gis_data_auditor.validators.base_validator import BaseValidator


class SchemaValidator(BaseValidator):
    """Inspecciona la presencia de campos faltantes o campos adicionales."""

    def __init__(self):
        super().__init__(name="SchemaValidator")

    def validate(self, dataset: DatasetInfo, standard: StandardDefinition) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []

        std_fields_upper = {k.upper(): v for k, v in standard.fields.items()}
        shp_fields_upper = {k.upper(): v for k, v in dataset.fields.items()}

        # 1. Campos Faltantes (Definidos en Excel pero ausentes en el SHP)
        for field_key, field_def in std_fields_upper.items():
            if field_key not in shp_fields_upper:
                issue = ValidationIssue(
                    issue_id=f"MISSING_{dataset.name}_{field_def.name}",
                    dataset_name=dataset.name,
                    filepath=str(dataset.filepath),
                    schema_id=standard.schema_id,
                    field_name=field_def.name,
                    rule_name=self.name,
                    expected_value="EXISTENTE",
                    found_value="AUSENTE",
                    severity=Severity.ERROR,
                    category=IssueCategory.CAMPO_FALTANTE,
                    message=f"El campo esperado '{field_def.name}' no existe en el Shapefile.",
                    recommendation=f"Agregar el campo '{field_def.name}' ({field_def.expected_type}) al Shapefile."
                )
                issues.append(issue)

        # 2. Campos Adicionales (Existen en el SHP pero no están en el Excel)
        for field_key, field_info in shp_fields_upper.items():
            if field_key not in std_fields_upper:
                is_system = field_key in SYSTEM_FIELDS or field_info.name.upper() in SYSTEM_FIELDS
                category = IssueCategory.CAMPO_ADICIONAL_SISTEMA if is_system else IssueCategory.CAMPO_ADICIONAL
                
                msg = (
                    f"El campo de sistema '{field_info.name}' existe en el Shapefile pero no está en el estándar."
                    if is_system else
                    f"El campo adicional '{field_info.name}' existe en el Shapefile pero no está definido en el estándar."
                )

                issue = ValidationIssue(
                    issue_id=f"EXTRA_{dataset.name}_{field_info.name}",
                    dataset_name=dataset.name,
                    filepath=str(dataset.filepath),
                    schema_id=standard.schema_id,
                    field_name=field_info.name,
                    rule_name=self.name,
                    expected_value="NO_DEFINIDO",
                    found_value=f"EXISTENTE ({field_info.type_name})",
                    severity=Severity.WARNING,
                    category=category,
                    message=msg,
                    recommendation="Verificar si el campo debe ser documentado en el estándar o eliminado del SHP."
                )
                issues.append(issue)

        return issues
