# -*- coding: utf-8 -*-
import arcpy


class GISDataAuditorTool(object):
    def __init__(self):
        """Define la herramienta de auditoría de datos GIS."""
        self.label = "Auditar Estructura de Shapefiles"
        self.description = (
            "Audita recursivamente la estructura de archivos Shapefile "
            "comparándolos contra un estándar definido en Excel."
        )
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define los parámetros de entrada y salida de la herramienta."""
        param_excel = arcpy.Parameter(
            displayName="Archivo Excel con el Estándar (.xlsx)",
            name="excel_file",
            datatype="DEFile",
            parameterType="Required",
            direction="Input"
        )

        param_folder = arcpy.Parameter(
            displayName="Carpeta Raíz a Auditar",
            name="target_folder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )

        param_output = arcpy.Parameter(
            displayName="Reporte Excel de Salida (.xlsx)",
            name="output_report",
            datatype="DEFile",
            parameterType="Required",
            direction="Output"
        )

        return [param_excel, param_folder, param_output]

    def isLicensed(self):
        """Indica si la herramienta está licendida para ejecutarse."""
        return True

    def updateParameters(self, parameters):
        """Modifica los valores de parámetros antes de la validación interna."""
        return

    def updateMessages(self, parameters):
        """Modifica los mensajes generados por la validación interna."""
        return

    def execute(self, parameters, messages):
        """Código fuente principal de la herramienta."""
        import os
        import sys

        toolbox_dir = os.path.dirname(os.path.abspath(__file__))
        if toolbox_dir not in sys.path:
            sys.path.insert(0, toolbox_dir)

        from gis_data_auditor.core.audit_engine import AuditEngine
        from gis_data_auditor.reports.excel_report_generator import ExcelReportGenerator

        excel_path = parameters[0].valueAsText
        target_folder = parameters[1].valueAsText
        output_report_path = parameters[2].valueAsText

        arcpy.AddMessage("Iniciando auditoría GIS Data Auditor...")
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


class Toolbox(object):
    def __init__(self):
        """Define la caja de herramientas."""
        self.label = "GIS Data Auditor Toolbox"
        self.alias = "gis_auditor"
        self.tools = [GISDataAuditorTool]
