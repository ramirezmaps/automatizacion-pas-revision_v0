"""
Clase base abstracta para todos los validadores de la arquitectura modular.
"""

from abc import ABC, abstractmethod
from typing import List
from gis_data_auditor.models.dataset import DatasetInfo
from gis_data_auditor.models.standard import StandardDefinition
from gis_data_auditor.models.validation import ValidationIssue


class BaseValidator(ABC):
    """Interfaz abstracta que debe implementar todo validador."""

    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled

    @abstractmethod
    def validate(self, dataset: DatasetInfo, standard: StandardDefinition) -> List[ValidationIssue]:
        """
        Ejecuta las reglas de validación sobre el dataset comparándolo contra el estándar.
        
        Args:
            dataset: Información del Shapefile real.
            standard: Especificación del Estándar Excel.
            
        Returns:
            Lista de incidencias detectadas.
        """
        pass
