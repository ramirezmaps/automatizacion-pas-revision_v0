"""
Adaptador de lectura de Shapefiles utilizando ArcPy (para entornos con ArcGIS Pro).
"""

import logging
from pathlib import Path
from gis_data_auditor.adapters.base_adapter import IShapefileAdapter
from gis_data_auditor.models.dataset import DatasetInfo, FieldInfo

logger = logging.getLogger(__name__)


class ArcPyAdapter(IShapefileAdapter):
    """Adaptador que lee archivos Shapefile usando ArcPy."""

    def __init__(self):
        try:
            import arcpy
            self.arcpy = arcpy
        except ImportError as e:
            raise ImportError(
                "ArcPy no está disponible en este entorno de Python. "
                "Para la versión independiente, se debe utilizar FionaAdapter."
            ) from e

    def inspect_shapefile(self, filepath: Path) -> DatasetInfo:
        dataset_info = DatasetInfo(
            name=filepath.stem,
            filepath=filepath
        )

        try:
            desc = self.arcpy.Describe(str(filepath))
            dataset_info.read_status = "SUCCESS"
            dataset_info.geometry_type = getattr(desc, "shapeType", "UNKNOWN")
            
            if hasattr(desc, "spatialReference") and desc.spatialReference:
                dataset_info.crs_name = desc.spatialReference.name
            else:
                dataset_info.crs_name = "SIN_CRS_DEFINIDO"

            # Recuento de entidades
            res = self.arcpy.management.GetCount(str(filepath))
            dataset_info.feature_count = int(res.getOutput(0))

            # Lista de campos
            fields = self.arcpy.ListFields(str(filepath))
            for f in fields:
                field_info = FieldInfo(
                    name=f.name,
                    type_name=f.type,
                    length=f.length if hasattr(f, "length") else None,
                    precision=f.precision if hasattr(f, "precision") else None,
                    scale=f.scale if hasattr(f, "scale") else None
                )
                dataset_info.add_field(field_info)

        except Exception as e:
            logger.error(f"Error al inspeccionar Shapefile '{filepath}' con ArcPy: {e}")
            dataset_info.read_status = "READ_ERROR"
            dataset_info.error_message = str(e)

        return dataset_info
