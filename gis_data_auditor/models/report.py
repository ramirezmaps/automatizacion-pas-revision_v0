"""
Modelo de datos para el Reporte Consolidado de Auditoría.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List
from gis_data_auditor.models.dataset import DatasetInfo
from gis_data_auditor.models.standard import StandardDefinition
from gis_data_auditor.models.validation import ValidationIssue


@dataclass
class AuditReport:
    """Contiene todos los resultados y métricas consolidadas de la auditoría."""
    timestamp: datetime = field(default_factory=datetime.now)
    root_folder: str = ""
    standard_file: str = ""
    total_shps_found: int = 0
    total_shps_read: int = 0
    total_shps_audited: int = 0
    total_no_match: int = 0
    total_ambiguous_match: int = 0
    total_clean_files: int = 0
    total_files_with_errors: int = 0
    total_files_with_warnings: int = 0
    
    datasets: List[DatasetInfo] = field(default_factory=list)
    issues: List[ValidationIssue] = field(default_factory=list)
    standards_used: Dict[str, StandardDefinition] = field(default_factory=dict)
