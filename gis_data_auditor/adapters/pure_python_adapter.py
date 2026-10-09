"""
Adaptador de lectura de Shapefiles en 100% Python puro (sin dependencias externas C/DLLs).
Lee directamente los encabezados de archivos .dbf, .shp y .prj utilizando el módulo estándar struct.
"""

import logging
import struct
from pathlib import Path
from gis_data_auditor.adapters.base_adapter import IShapefileAdapter
from gis_data_auditor.models.dataset import DatasetInfo, FieldInfo

logger = logging.getLogger(__name__)


class PurePythonAdapter(IShapefileAdapter):
    """Adaptador de lectura de Shapefiles en Python puro (cero dependencias externas)."""

    SHAPE_TYPES = {
        0: "Null",
        1: "Point",
        3: "Polyline",
        5: "Polygon",
        8: "MultiPoint",
        11: "PointZ",
        13: "PolylineZ",
        15: "PolygonZ",
        21: "PointM",
        23: "PolylineM",
        25: "PolygonM",
        31: "MultiPatch"
    }

    TYPE_MAPPING = {
        'C': 'String',
        'N': 'Double',
        'F': 'Double',
        'I': 'Integer',
        'D': 'Date',
        'L': 'Logical'
    }

    def inspect_shapefile(self, filepath: Path) -> DatasetInfo:
        dataset_info = DatasetInfo(
            name=filepath.stem,
            filepath=filepath
        )

        dbf_path = filepath.with_suffix('.dbf')

        if not dbf_path.exists():
            dataset_info.read_status = "READ_ERROR"
            dataset_info.error_message = f"Archivo de tabla de atributos (.dbf) no encontrado: '{dbf_path}'"
            return dataset_info

        try:
            # 1. Leer .dbf para obtener campos, tipos, longitudes, escala y recuento
            self._read_dbf_header(dbf_path, dataset_info)

            # 2. Leer .shp para obtener tipo de geometría
            self._read_shp_header(filepath, dataset_info)

            # 3. Leer .prj para obtener nombre del CRS
            self._read_prj_file(filepath.with_suffix('.prj'), dataset_info)

            dataset_info.read_status = "SUCCESS"

        except Exception as e:
            logger.error(f"Error al inspeccionar Shapefile en Python puro '{filepath}': {e}")
            dataset_info.read_status = "READ_ERROR"
            dataset_info.error_message = str(e)

        return dataset_info

    def _read_dbf_header(self, dbf_path: Path, dataset_info: DatasetInfo) -> None:
        """Lee el encabezado dBase III/IV de un archivo .dbf para extraer campos y recuento."""
        with open(dbf_path, "rb") as f:
            header_bytes = f.read(32)
            if len(header_bytes) < 32:
                raise ValueError("Archivo .dbf corrupto o demasiado corto.")

            # Unpack registros (int 32 bit), longitud encabezado (int 16 bit), longitud registro (int 16 bit)
            num_records, header_len, record_len = struct.unpack("<IHH", header_bytes[4:12])
            dataset_info.feature_count = num_records

            # Cada descriptor de campo ocupa 32 bytes
            num_fields = (header_len - 33) // 32
            for _ in range(num_fields):
                field_bytes = f.read(32)
                if not field_bytes or field_bytes[0] == 0x0D:
                    break

                raw_name = field_bytes[:11].replace(b"\x00", b"")
                try:
                    field_name = raw_name.decode("utf-8").strip()
                except UnicodeDecodeError:
                    field_name = raw_name.decode("latin1", errors="ignore").strip()

                type_code = chr(field_bytes[11]).upper()
                length = field_bytes[16]
                scale = field_bytes[17]

                # Para enteros puros, ajustar tipo si decimales es 0
                norm_type = self.TYPE_MAPPING.get(type_code, "String")
                if type_code == 'N' and scale == 0 and length <= 9:
                    norm_type = "Integer"

                field_info = FieldInfo(
                    name=field_name,
                    type_name=norm_type,
                    length=length,
                    precision=length,
                    scale=scale if scale > 0 else None
                )
                dataset_info.add_field(field_info)

    def _read_shp_header(self, shp_path: Path, dataset_info: DatasetInfo) -> None:
        """Lee el encabezado principal del archivo .shp para obtener el tipo de geometría."""
        if not shp_path.exists():
            return

        with open(shp_path, "rb") as f:
            header = f.read(100)
            if len(header) >= 36:
                shape_type_id = struct.unpack("<i", header[32:36])[0]
                dataset_info.geometry_type = self.SHAPE_TYPES.get(shape_type_id, f"Desconocido ({shape_type_id})")

    def _read_prj_file(self, prj_path: Path, dataset_info: DatasetInfo) -> None:
        """Lee el archivo .prj para extraer el nombre del sistema de referencia espacial (CRS)."""
        if not prj_path.exists():
            dataset_info.crs_name = "SIN_CRS_DEFINIDO"
            return

        try:
            with open(prj_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().strip()
                if "GEOGCS[" in content:
                    parts = content.split("GEOGCS[")
                    if len(parts) > 1:
                        name = parts[1].split('"')[1] if '"' in parts[1] else parts[1].split(',')[0]
                        dataset_info.crs_name = f"GCS_{name}"
                        return
                elif "PROJCS[" in content:
                    parts = content.split("PROJCS[")
                    if len(parts) > 1:
                        name = parts[1].split('"')[1] if '"' in parts[1] else parts[1].split(',')[0]
                        dataset_info.crs_name = name
                        return
                
                dataset_info.crs_name = content[:40] if content else "DEFINIDO"
        except Exception:
            dataset_info.crs_name = "PROJECTION_FILE_PRESENT"
