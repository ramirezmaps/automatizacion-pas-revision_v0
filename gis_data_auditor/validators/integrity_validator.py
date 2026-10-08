"""
Validador de legibilidad e integridad de archivos Shapefile.
"""

from typing import List
from gis_data_auditor.models.dataset import DatasetInfo
from gis_data_auditor.models.standard import StandardDefinition
from gis_data_auditor.models.validation import IssueCategory, Severity, ValidationIssue
from gis_data_auditor.validators.base_validator import BaseValidator


class IntegrityValidator(BaseValidator):
    """Valida la lectura correcta del archivo Shapefile."""

    def __init__(self):
        super().__init__(name="IntegrityValidator")

    def validate(self, dataset: DatasetInfo, standard: StandardDefinition) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []

        if dataset.read_status == "READ_ERROR":
            issue = ValidationIssue(
                issue_id=f"READ_ERROR_{dataset.name}",
                dataset_name=dataset.name,
                filepath=str(dataset.filepath),
                schema_id=standard.schema_id if standard else "DESCONOCIDO",
                field_name="N/A",
                rule_name=self.name,
                expected_value="LECTURA_EXITOSA",
                found_value="ERROR_DE_LECTURA",
                severity=Severity.ERROR,
                category=IssueCategory.ERROR_LECTURA,
                message=f"No se pudo acceder o leer la estructura del Shapefile '{dataset.name}'.",
                technical_details=dataset.error_message or "",
                recommendation="Verificar que el archivo no esté dañado o bloqueado por otro software GIS."
            )
            issues.append(issue)

        return issues
