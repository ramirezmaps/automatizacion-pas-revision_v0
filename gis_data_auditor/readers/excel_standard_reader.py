"""
Lector y normalizador del Estándar definido en Excel.
"""

import logging
from pathlib import Path
from typing import Dict, Union
import pandas as pd

from gis_data_auditor.core.exceptions import StandardReadError
from gis_data_auditor.models.standard import FieldDefinition, StandardDefinition
from gis_data_auditor.utils.normalization import normalize_string, parse_optional_int

logger = logging.getLogger(__name__)


class ExcelStandardReader:
    """Clase encargada de cargar y normalizar la estructura esperada desde un Excel."""

    REQUIRED_COLUMNS = {"shp", "nombre", "tipo", "longitud", "decimales"}

    def read_standard(self, excel_path: Union[str, Path]) -> Dict[str, StandardDefinition]:
        """
        Lee el archivo Excel y retorna un diccionario mapeando schema_id -> StandardDefinition.
        Aplica estrictamente la regla NA (longitud y decimales opcionales).
        """
        excel_path = Path(excel_path)
        if not excel_path.exists():
            raise StandardReadError(f"El archivo estándar no existe: {excel_path}")

        try:
            # Leer la primera hoja por defecto o buscar la que tenga las columnas
            xl = pd.ExcelFile(excel_path)
            target_sheet = xl.sheet_names[0]
            
            # Buscar si alguna hoja contiene explícitamente las columnas requeridas
            for sheet in xl.sheet_names:
                df_temp = pd.read_excel(excel_path, sheet_name=sheet, nrows=2)
                cols_lower = {str(c).strip().lower() for c in df_temp.columns}
                if self.REQUIRED_COLUMNS.issubset(cols_lower):
                    target_sheet = sheet
                    break
                    
            df = pd.read_excel(excel_path, sheet_name=target_sheet)
        except Exception as e:
            raise StandardReadError(f"Error al abrir el archivo Excel '{excel_path}': {e}") from e

        # Mapear nombres de columnas a minúsculas para robustez
        col_mapping = {str(col).strip().lower(): col for col in df.columns}
        missing_cols = self.REQUIRED_COLUMNS - set(col_mapping.keys())
        if missing_cols:
            raise StandardReadError(
                f"El archivo Excel falta de las siguientes columnas requeridas: {missing_cols}"
            )

        col_shp = col_mapping["shp"]
        col_nombre = col_mapping["nombre"]
        col_tipo = col_mapping["tipo"]
        col_longitud = col_mapping["longitud"]
        col_decimales = col_mapping["decimales"]

        standards: Dict[str, StandardDefinition] = {}

        for index, row in df.iterrows():
            row_num = index + 2  # Considerar encabezado en fila 1
            shp_name = normalize_string(row[col_shp])
            field_name = normalize_string(row[col_nombre])
            field_type = normalize_string(row[col_tipo])

            if not shp_name or not field_name:
                logger.warning(
                    f"Fila {row_num}: Se omitió una fila vacía o sin identificador de shp/nombre."
                )
                continue

            schema_key = shp_name.upper()
            if schema_key not in standards:
                standards[schema_key] = StandardDefinition(
                    schema_id=shp_name,
                    source_file=str(excel_path)
                )

            # Aplicar Regla NA para longitud y decimales
            exp_length = parse_optional_int(row[col_longitud])
            exp_decimals = parse_optional_int(row[col_decimales])

            field_def = FieldDefinition(
                name=field_name,
                expected_type=field_type,
                expected_length=exp_length,
                expected_decimals=exp_decimals,
                row_number=row_num
            )

            standards[schema_key].add_field(field_def)

        logger.info(
            f"Estándar cargado exitosamente desde '{excel_path}'. "
            f"Se identificaron {len(standards)} esquemas de capas."
        )
        return standards
