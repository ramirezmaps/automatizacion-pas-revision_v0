"""
Modelos de datos para representar la información inspeccionada de cada Shapefile.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional


@dataclass
class FieldInfo:
    """Información real extraída de un campo del Shapefile."""
    name: str
    type_name: str
    length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None


@dataclass
class DatasetInfo:
    """Información general y estructural del Shapefile auditado."""
    name: str
    filepath: Path
    associated_schema: Optional[str] = None
    match_status: str = "NO_MATCH"  # MATCH, NO_MATCH, AMBIGUOUS_MATCH
    read_status: str = "UNREAD"     # SUCCESS, READ_ERROR, UNREAD
    geometry_type: str = "UNKNOWN"
    crs_name: str = "UNKNOWN"
    feature_count: int = 0
    fields: Dict[str, FieldInfo] = field(default_factory=dict)
    error_message: Optional[str] = None

    def add_field(self, field_info: FieldInfo) -> None:
        """Agrega la especificación de un campo encontrado."""
        self.fields[field_info.name.upper()] = field_info

    def get_field(self, name: str) -> Optional[FieldInfo]:
        """Obtiene un campo real ignorando mayúsculas/minúsculas."""
        return self.fields.get(name.upper())
