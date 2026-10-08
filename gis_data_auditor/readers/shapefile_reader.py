"""
Lector central de Shapefiles con selección dinámica del adaptador adecuado (ArcPy o Fiona).
"""

import logging
from pathlib import Path

from gis_data_auditor.adapters.base_adapter import IShapefileAdapter
from gis_data_auditor.adapters.fiona_adapter import FionaAdapter
from gis_data_auditor.models.dataset import DatasetInfo

logger = logging.getLogger(__name__)


class ShapefileReader:
    """Clase principal para leer información de Shapefiles adaptándose al entorno disponible."""

    def __init__(self, force_fiona: bool = False):
        self.adapter: IShapefileAdapter = self._select_adapter(force_fiona)

    def _select_adapter(self, force_fiona: bool) -> IShapefileAdapter:
        if not force_fiona:
            try:
                from gis_data_auditor.adapters.arcpy_adapter import ArcPyAdapter
                adapter = ArcPyAdapter()
                logger.info("Utilizando el adaptador nativo ArcPy.")
                return adapter
            except Exception:
                logger.info("ArcPy no disponible. Seleccionando adaptador independiente FionaAdapter.")
        
        return FionaAdapter()

    def read_dataset(self, filepath: Path) -> DatasetInfo:
        """Inspecciona el Shapefile utilizando el adaptador configurado."""
        return self.adapter.inspect_shapefile(filepath)
