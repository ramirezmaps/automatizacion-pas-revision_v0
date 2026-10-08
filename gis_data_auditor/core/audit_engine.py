"""
Motor principal de auditoría (AuditEngine). Totalmente desacoplado de la interfaz de usuario.
"""

import logging
from pathlib import Path
from typing import Callable, Optional, Union

from gis_data_auditor.core.registry import ValidatorRegistry
from gis_data_auditor.matchers.dataset_matcher import DatasetMatcher
from gis_data_auditor.models.report import AuditReport
from gis_data_auditor.models.validation import IssueCategory, Severity, ValidationIssue
from gis_data_auditor.readers.excel_standard_reader import ExcelStandardReader
from gis_data_auditor.readers.shapefile_reader import ShapefileReader
from gis_data_auditor.scanners.folder_scanner import FolderScanner

logger = logging.getLogger(__name__)


class AuditEngine:
    """Coordinador central del proceso de auditoría de datos geoespaciales."""

    def __init__(self, force_fiona: bool = False):
        self.standard_reader = ExcelStandardReader()
        self.folder_scanner = FolderScanner()
        self.shapefile_reader = ShapefileReader(force_fiona=force_fiona)
        self.dataset_matcher = DatasetMatcher()
        self.registry = ValidatorRegistry()

    def run_audit(
        self,
        excel_path: Union[str, Path],
        target_dir: Union[str, Path],
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> AuditReport:
        """
        Ejecuta el flujo completo de auditoría.
        
        Args:
            excel_path: Ruta al Excel con el estándar
            target_dir: Carpeta raíz a analizar
            progress_callback: Función opcional para reportar progreso (actual, total, mensaje)
            
        Returns:
            Objeto AuditReport completo con resultados e incidencias.
        """
        logger.info(f"Iniciando auditoría. Estándar: '{excel_path}', Carpeta: '{target_dir}'")
        
        report = AuditReport(
            root_folder=str(target_dir),
            standard_file=str(excel_path)
        )

        # 1. Leer el Estándar
        standards = self.standard_reader.read_standard(excel_path)
        report.standards_used = standards

        # 2. Escanear carpeta en busca de Shapefiles
        shp_paths = self.folder_scanner.scan_directory(target_dir)
        report.total_shps_found = len(shp_paths)

        if not shp_paths:
            logger.warning("No se encontraron archivos Shapefile en la carpeta especificada.")
            return report

        # 3. Procesar cada Shapefile
        active_validators = self.registry.get_active_validators()
        
        for idx, shp_path in enumerate(shp_paths, start=1):
            if progress_callback:
                progress_callback(idx, len(shp_paths), f"Auditando: {shp_path.name}")

            # Inspeccionar datos reales del SHP
            dataset_info = self.shapefile_reader.read_dataset(shp_path)
            report.datasets.append(dataset_info)

            if dataset_info.read_status == "SUCCESS":
                report.total_shps_read += 1

            # Buscar asociación con el estándar
            matched_standard = self.dataset_matcher.match_dataset(dataset_info, standards)

            if dataset_info.match_status == "NO_MATCH":
                report.total_no_match += 1
                issue = ValidationIssue(
                    issue_id=f"NO_MATCH_{dataset_info.name}",
                    dataset_name=dataset_info.name,
                    filepath=str(dataset_info.filepath),
                    schema_id="SIN_ASOCIAR",
                    field_name="N/A",
                    rule_name="DatasetMatcher",
                    expected_value="ESQUEMA_EN_EXCEL",
                    found_value="SIN_ESQUEMA_COINCIDENTE",
                    severity=Severity.WARNING,
                    category=IssueCategory.SIN_ESQUEMA,
                    message=f"No se encontró un esquema definido en el Excel para el SHP '{dataset_info.name}'.",
                    recommendation="Verificar el nombre de la capa en la columna 'shp' del estándar Excel."
                )
                report.issues.append(issue)
                continue

            elif dataset_info.match_status == "AMBIGUOUS_MATCH":
                report.total_ambiguous_match += 1
                issue = ValidationIssue(
                    issue_id=f"AMBIGUOUS_{dataset_info.name}",
                    dataset_name=dataset_info.name,
                    filepath=str(dataset_info.filepath),
                    schema_id="AMBIGUO",
                    field_name="N/A",
                    rule_name="DatasetMatcher",
                    expected_value="COINCIDENCIA_UNICA",
                    found_value="MULTIPLES_COINCIDENCIAS",
                    severity=Severity.ERROR,
                    category=IssueCategory.ASOCIACION_AMBIGUA,
                    message=f"El SHP '{dataset_info.name}' coincide con múltiples esquemas del Excel.",
                    recommendation="Revisar que no existan nombres repetidos en la columna 'shp' del estándar."
                )
                report.issues.append(issue)
                continue

            # Ejecutar validadores si hay coincidencia única
            report.total_shps_audited += 1
            for validator in active_validators:
                new_issues = validator.validate(dataset_info, matched_standard)
                report.issues.extend(new_issues)

        # 4. Calcular estadísticas finales de archivos
        self._calculate_summary_statistics(report)

        logger.info(
            f"Auditoría completada. Total SHP: {report.total_shps_found}, "
            f"Sin errores: {report.total_clean_files}, Con errores: {report.total_files_with_errors}, "
            f"Con advertencias: {report.total_files_with_warnings}"
        )
        return report

    def _calculate_summary_statistics(self, report: AuditReport) -> None:
        """Calcula los contadores de archivos limpios, con error y con advertencia de forma consistente."""
        datasets_with_errors = set()
        datasets_with_warnings = set()

        for issue in report.issues:
            if issue.severity == Severity.ERROR:
                datasets_with_errors.add(issue.dataset_name)
            elif issue.severity == Severity.WARNING:
                datasets_with_warnings.add(issue.dataset_name)

        report.total_files_with_errors = len(datasets_with_errors)
        
        # Archivos que tienen advertencias pero NO tienen errores
        warnings_only = datasets_with_warnings - datasets_with_errors
        report.total_files_with_warnings = len(warnings_only)

        # Archivos auditados sin errores ni advertencias
        audited_names = {ds.name for ds in report.datasets if ds.match_status == "MATCH" and ds.read_status == "SUCCESS"}
        clean = audited_names - datasets_with_errors - datasets_with_warnings
        report.total_clean_files = len(clean)
