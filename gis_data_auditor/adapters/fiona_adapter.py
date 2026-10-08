"""
Adaptador de lectura de Shapefiles utilizando la librería Fiona (para uso independiente sin ArcPy).
"""

import logging
from pathlib import Path
import fiona

from gis_data_auditor.adapters.base_adapter import IShapefileAdapter
from gis_data_auditor.models.dataset import DatasetInfo, FieldInfo

logger = logging.getLogger(__name__)


class FionaAdapter(IShapefileAdapter):
    """Adaptador que lee archivos Shapefile usando fiona."""

    def inspect_shapefile(self, filepath: Path) -> DatasetInfo:
        dataset_info = DatasetInfo(
            name=filepath.stem,
            filepath=filepath
        )

        try:
            with fiona.open(filepath, "r") as src:
                dataset_info.read_status = "SUCCESS"
                dataset_info.geometry_type = src.schema.get("geometry", "UNKNOWN")
                
                # Obtener CRS de forma segura
                crs_info = src.crs
                if crs_info:
                    try:
                        if hasattr(crs_info, "to_string"):
                            dataset_info.crs_name = crs_info.to_string()
                        else:
                            dataset_info.crs_name = str(crs_info)
                    except Exception:
                        dataset_info.crs_name = "DEFINIDO"
                else:
                    dataset_info.crs_name = "SIN_CRS_DEFINIDO"

                # Conteo de registros
                dataset_info.feature_count = len(src)

                # Obtener propiedades / campos
                properties = src.schema.get("properties", {})
                for field_name, type_str in properties.items():
                    type_name, length, scale = self._parse_fiona_type(type_str)
                    
                    field_info = FieldInfo(
                        name=field_name,
                        type_name=type_name,
                        length=length,
                        scale=scale,
                        precision=length
                    )
                    dataset_info.add_field(field_info)

        except Exception as e:
            logger.error(f"Error al inspeccionar Shapefile '{filepath}' con Fiona: {e}")
            dataset_info.read_status = "READ_ERROR"
            dataset_info.error_message = str(e)

        return dataset_info

    @staticmethod
    def _parse_fiona_type(type_str: str):
        """Convierte una cadena de tipo Fiona (ej: 'str:50', 'float:11.2') a (type_name, length, scale)."""
        parts = type_str.split(":")
        base_type = parts[0].strip()
        length = None
        scale = None
        
        if len(parts) > 1:
            nums = parts[1].split(".")
            try:
                length = int(nums[0])
            except ValueError:
                pass
            if len(nums) > 1:
                try:
                    scale = int(nums[1])
                except ValueError:
                    pass
                    
        # Normalizar tipo base
        if base_type.lower() in ("str", "string"):
            norm_type = "String"
        elif base_type.lower() in ("int", "integer"):
            norm_type = "Integer"
        elif base_type.lower() in ("float", "double", "numeric"):
            norm_type = "Double"
        elif base_type.lower() == "date":
            norm_type = "Date"
        else:
            norm_type = base_type.capitalize()
            
        return norm_type, length, scale
