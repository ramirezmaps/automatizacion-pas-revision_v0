# -*- coding: utf-8 -*-
"""
Caja de Herramientas de Python (Python Toolbox) para ArcGIS Pro.
Permite ejecutar GIS Data Auditor nativamente en ArcGIS Pro.
"""

import os
import sys

# Requerido por ArcGIS Pro para reconocer la toolbox .pyt
try:
    import arcpy
except ImportError:
    pass

# Agregar carpeta del proyecto al PYTHONPATH
toolbox_dir = os.path.dirname(os.path.abspath(__file__))
if toolbox_dir not in sys.path:
    sys.path.insert(0, toolbox_dir)


class Toolbox(object):
    def __init__(self):
        self.label = "GIS Data Auditor Toolbox"
        self.alias = "gis_auditor"
        self.tools = [GISDataAuditorTool]


class GISDataAuditorTool(object):
    def __init__(self):
        self.label = "Auditar Estructura de Shapefiles"
        self.description = (
            "Audita la estructura de archivos Shapefile comparándolos con un estándar Excel."
        )
        self.canRunInBackground = False

    def getParameterInfo(self):
        # Param 0: Estándar Excel
        param_excel = arcpy.Parameter(
            displayName="Archivo Excel con el Estándar",
            name="excel_file",
            datatype="DEFile",
            parameterType="Required",
            direction="Input"
        )

        # Param 1: Carpeta Raíz de SHPs
        param_folder = arcpy.Parameter(
            displayName="Carpeta Raíz a Auditar",
            name="target_folder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )

        # Param 2: Archivo de Salida Excel
        param_output = arcpy.Parameter(
            displayName="Reporte Excel de Salida (.xlsx)",
            name="output_report",
            datatype="DEFile",
            parameterType="Required",
            direction="Output"
        )

        return [param_excel, param_folder, param_output]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        from gis_data_auditor.core.audit_engine import AuditEngine
        from gis_data_auditor.reports.excel_report_generator import ExcelReportGenerator

        excel_path = parameters[0].valueAsText
        target_folder = parameters[1].valueAsText
        output_report_path = parameters[2].valueAsText

        arcpy.AddMessage(f"Iniciando auditoría GIS Data Auditor...")
        arcpy.AddMessage(f"Estándar: {excel_path}")
        arcpy.AddMessage(f"Carpeta: {target_folder}")

        def progress_callback(current, total, msg):
            arcpy.AddMessage(f"[{current}/{total}] {msg}")

        engine = AuditEngine(force_fiona=False)
        report = engine.run_audit(
            excel_path=excel_path,
            target_dir=target_folder,
            progress_callback=progress_callback
        )

        generator = ExcelReportGenerator()
        final_file = generator.generate_report(report, output_report_path)

        arcpy.AddMessage("Auditoría completada exitosamente.")
        arcpy.AddMessage(f"Total SHPs auditados: {report.total_shps_audited}")
        arcpy.AddMessage(f"Archivos Conformes: {report.total_clean_files}")
        arcpy.AddMessage(f"Archivos con Errores: {report.total_files_with_errors}")
        arcpy.AddMessage(f"Archivos con Advertencias: {report.total_files_with_warnings}")
        arcpy.AddMessage(f"Reporte generado en: {final_file}")

        return
