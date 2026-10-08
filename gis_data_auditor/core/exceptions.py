"""
Excepciones personalizadas para el aplicativo GIS Data Auditor.
"""

class GISAuditorError(Exception):
    """Excepción base para el auditor GIS."""
    pass


class StandardReadError(GISAuditorError):
    """Lanzada cuando el archivo Excel estándar no puede ser leído o falta estructura."""
    pass


class ShapefileReadError(GISAuditorError):
    """Lanzada cuando un Shapefile está corrupto, inalcanzable o bloqueado."""
    pass


class ConfigurationError(GISAuditorError):
    """Lanzada cuando la configuración o parámetros de entrada son inválidos."""
    pass
