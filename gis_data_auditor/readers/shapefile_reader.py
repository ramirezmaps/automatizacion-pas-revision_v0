"""
Lector central de Shapefiles con selección dinámica del adaptador adecuado (ArcPy o Fiona).
No importa ninguna librería GIS a nivel superior para prevenir errores de importación.
"""

import logging
from pathlib import Path
from gis_data_auditor.adapters.base_adapter import IShapefileAdapter
from gis_data_auditor.models.dataset import DatasetInfo

logger = logging.getLogger(__name__)


class ShapefileReader:
    """Clase principal para leer información de Shapefiles adaptándose al entorno disponible."""

    def __init__(self, force_fiona: bool = False):
        self.adapter: IShapefileAdapter = self._select_adapter(force_fiona)

    def _select_adapter(self, force_fiona: bool) -> IShapefileAdapter:
        # 1. Intentar ArcPy primero si no se forzó explícitamente Fiona
        if not force_fiona:
            try:
                from gis_data_auditor.adapters.arcpy_adapter import ArcPyAdapter
                adapter = ArcPyAdapter()
                logger.info("Utilizando el adaptador nativo ArcPy.")
                return adapter
            except Exception as e:
                logger.info(f"ArcPy no disponible ({e}). Intentando con FionaAdapter...")

        # 2. Intentar FionaAdapter si ArcPy no está o si se forzó Fiona
        try:
            from gis_data_auditor.adapters.fiona_adapter import FionaAdapter
            adapter = FionaAdapter()
            logger.info("Utilizando el adaptador independiente FionaAdapter.")
            return adapter
        except Exception as e_fiona:
            logger.info(f"FionaAdapter no pudo ser cargado: {e_fiona}")

        # 3. Fallback de emergencia a ArcPy si Fiona falló pero no se había intentado
        if force_fiona:
            try:
                from gis_data_auditor.adapters.arcpy_adapter import ArcPyAdapter
                adapter = ArcPyAdapter()
                logger.info("Fallback exitoso a ArcPyAdapter tras fallo de Fiona.")
                return adapter
            except Exception as e_arcpy:
                raise ImportError(
                    f"No se pudo cargar ningún lector GIS. Fiona falló ({e_fiona}) y ArcPy falló ({e_arcpy})."
                ) from e_arcpy

        raise ImportError(f"No se pudo cargar la librería de lectura GIS (ArcPy / Fiona).")

    def read_dataset(self, filepath: Path) -> DatasetInfo:
        """Inspecciona el Shapefile utilizando el adaptador configurado."""
        return self.adapter.inspect_shapefile(filepath)
