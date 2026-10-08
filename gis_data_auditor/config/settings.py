"""
Configuración centralizada para GIS Data Auditor.
"""

from pathlib import Path
from typing import Set

# Extensiones de archivos GIS soportadas en la primera versión
SUPPORTED_EXTENSIONS: Set[str] = {".shp"}

# Campos de sistema de Shapefiles / Geodatabases que deben notificarse si aparecen
SYSTEM_FIELDS: Set[str] = {
    "FID", "OBJECTID", "OID", "SHAPE", "GEOMETRY", 
    "SHAPE_LENG", "SHAPE_AREA", "SHAPE_LENGTH", "GEOMETRY_AREA", "GEOMETRY_LEN"
}

# Valores considerados como NA / No especificado en el Excel estándar
NA_VALUES: Set[str] = {"NA", "N/A", "N.A", "NONE", "NULL", "", "NAN"}

# Sensibilidad a mayúsculas en la asociación de nombres (False = insensible)
CASE_SENSITIVE_MATCHING: bool = False

# Configuración por defecto de carpetas
DEFAULT_OUTPUT_DIR = Path("reportes")
DEFAULT_LOG_DIR = Path("logs")
