"""
Asociador de archivos Shapefile con sus esquemas del Estándar Excel.
"""

import logging
from typing import Dict, List, Optional
from gis_data_auditor.models.dataset import DatasetInfo
from gis_data_auditor.models.standard import StandardDefinition

logger = logging.getLogger(__name__)


class DatasetMatcher:
    """Asocia cada DatasetInfo con la definición correspondiente de la columna 'shp' del Excel."""

    def match_dataset(
        self, dataset: DatasetInfo, standards: Dict[str, StandardDefinition]
    ) -> Optional[StandardDefinition]:
        """
        Busca coincidencia entre el nombre del SHP y las claves de esquemas del Estándar.
        Actualiza match_status y associated_schema en el objeto dataset.
        """
        shp_basename = dataset.name.strip().upper()
        
        # Buscar coincidencias exactas (case-insensitive)
        matched_standards: List[StandardDefinition] = []
        
        for std_key, std_def in standards.items():
            if shp_basename == std_key.strip().upper():
                matched_standards.append(std_def)

        if len(matched_standards) == 1:
            std = matched_standards[0]
            dataset.match_status = "MATCH"
            dataset.associated_schema = std.schema_id
            logger.info(f"Asociación exitosa: SHP '{dataset.name}' -> Esquema '{std.schema_id}'")
            return std
            
        elif len(matched_standards) > 1:
            dataset.match_status = "AMBIGUOUS_MATCH"
            dataset.associated_schema = None
            logger.warning(f"Asociación ambigua para SHP '{dataset.name}': {len(matched_standards)} coincidencias.")
            return None
            
        else:
            dataset.match_status = "NO_MATCH"
            dataset.associated_schema = None
            logger.warning(f"Sin esquema asociado para SHP '{dataset.name}'.")
            return None
