"""
Escáner recursivo de carpetas para identificar archivos Shapefile (.shp).
"""

import logging
from pathlib import Path
from typing import List, Union

from gis_data_auditor.config.settings import SUPPORTED_EXTENSIONS

logger = logging.getLogger(__name__)


class FolderScanner:
    """Explora carpetas y subcarpetas localizando archivos Shapefile."""

    def scan_directory(self, root_dir: Union[str, Path]) -> List[Path]:
        """
        Recorre recursivamente root_dir y devuelve la lista de rutas a archivos .shp únicos.
        """
        root_path = Path(root_dir)
        if not root_path.exists() or not root_path.is_dir():
            logger.error(f"La carpeta raíz especificada no existe o no es válida: '{root_dir}'")
            return []

        shp_files: List[Path] = []
        
        for item in root_path.rglob("*"):
            if item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS:
                # Evitar contar archivos auxiliares como .shp.xml
                if not item.name.lower().endswith(".shp.xml"):
                    shp_files.append(item.resolve())

        logger.info(f"Escaneo finalizado en '{root_dir}'. Se encontraron {len(shp_files)} archivos Shapefile.")
        return shp_files
