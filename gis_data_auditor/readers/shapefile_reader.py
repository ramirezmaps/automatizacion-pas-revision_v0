"""
Lector central de Shapefiles con selección dinámica y tolerante a fallos del adaptador GIS.
Prioriza ArcPy en ArcGIS Pro, Fiona en entornos compatibles y PurePythonAdapter como fallback infalible.
"""

import logging
from pathlib import Path

from gis_data_auditor.adapters.base_adapter import IShapefileAdapter
from gis_data_auditor.models.dataset import DatasetInfo

logger = logging.getLogger(__name__)


class ShapefileReader:
    """Clase principal para leer información de Shapefiles adaptándose a cualquier entorno."""

    def __init__(self, force_fiona: bool = False):
        self.adapter: IShapefileAdapter = self._select_adapter(force_fiona)

    def _select_adapter(self, force_fiona: bool) -> IShapefileAdapter:
        # 1. Intentar ArcPy primero si se ejecuta dentro de ArcGIS Pro
        if not force_fiona:
            try:
                from gis_data_auditor.adapters.arcpy_adapter import ArcPyAdapter
                adapter = ArcPyAdapter()
                logger.info("Utilizando el adaptador nativo ArcPy.")
                return adapter
            except Exception as e:
                logger.info(f"ArcPy no disponible ({e}). Intentando con FionaAdapter...")

        # 2. Intentar FionaAdapter si ArcPy no está o si se solicitó Fiona
        try:
            from gis_data_auditor.adapters.fiona_adapter import FionaAdapter
            adapter = FionaAdapter()
            logger.info("Utilizando el adaptador FionaAdapter.")
            return adapter
        except Exception as e_fiona:
            logger.info(f"FionaAdapter no pudo ser cargado ({e_fiona}). Usando PurePythonAdapter infalible...")

        # 3. Fallback infalible: PurePythonAdapter (Python puro, cero dependencias C/DLLs)
        from gis_data_auditor.adapters.pure_python_adapter import PurePythonAdapter
        logger.info("Utilizando el adaptador independiente PurePythonAdapter (cero dependencias externas).")
        return PurePythonAdapter()

    def read_dataset(self, filepath: Path) -> DatasetInfo:
        """Inspecciona el Shapefile utilizando el adaptador configurado."""
        return self.adapter.inspect_shapefile(filepath)
