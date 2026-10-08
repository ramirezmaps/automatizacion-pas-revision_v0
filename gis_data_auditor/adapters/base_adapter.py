"""
Interfaz base (clase abstracta) para adaptadores de lectura de Shapefiles.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from gis_data_auditor.models.dataset import DatasetInfo


class IShapefileAdapter(ABC):
    """Interfaz abstracta para los adaptadores de lectura GIS."""

    @abstractmethod
    def inspect_shapefile(self, filepath: Path) -> DatasetInfo:
        """
        Inspecciona la estructura de un archivo Shapefile y retorna su DatasetInfo.
        
        Args:
            filepath: Ruta al archivo .shp
            
        Returns:
            DatasetInfo con los metadatos, tipo de geometría, CRS y campos encontrados.
        """
        pass
