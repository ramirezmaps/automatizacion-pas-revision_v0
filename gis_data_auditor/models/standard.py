"""
Modelos de datos para el Estándar definido en Excel.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class FieldDefinition:
    """Representa la especificación esperada para un campo según el estándar Excel."""
    name: str
    expected_type: str
    expected_length: Optional[int] = None
    expected_decimals: Optional[int] = None
    row_number: int = 0

    @property
    def has_length_spec(self) -> bool:
        """Indica si el estándar definió explícitamente una longitud (distinto de NA)."""
        return self.expected_length is not None

    @property
    def has_decimals_spec(self) -> bool:
        """Indica si el estándar definió explícitamente decimales (distinto de NA)."""
        return self.expected_decimals is not None


@dataclass
class StandardDefinition:
    """Representa el esquema completo de una capa/SHP en el estándar."""
    schema_id: str
    fields: Dict[str, FieldDefinition] = field(default_factory=dict)
    source_file: str = ""

    def add_field(self, field_def: FieldDefinition) -> None:
        """Agrega una definición de campo al esquema (clave en mayúsculas para búsquedas case-insensitive)."""
        self.fields[field_def.name.upper()] = field_def

    def get_field(self, name: str) -> Optional[FieldDefinition]:
        """Obtiene una definición de campo ignorando mayúsculas/minúsculas."""
        return self.fields.get(name.upper())
